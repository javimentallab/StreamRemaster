// Runs frame generation on the page's main video: finds the video, lays a canvas over it and
// answers the popup. Nothing touches the GPU until the user turns it on.
//
// Two ways to run it. By default it runs here, on the page's main thread, in every browser. In
// Chromium the work can also go to a dedicated worker (framegen-worker.js, only when asked with
// options.worker): the canvas is handed over as an OffscreenCanvas and the frames as a stream, so the
// page's own scripts can no longer hold the picture back. It is off because on Twitch it froze at
// 0 fps when the window lost the focus or was resized (a quality change rebuilds the whole worker).
"use strict";

(function () {
  if (globalThis.STFramegenPage) return;

  const LAYOUT_EVERY_TICKS = 8;
  // With nothing painted for this long (paused, seeking, buffering) the real video shows through.
  const HIDE_AFTER_MS = 200;
  const METER_EVERY_MS = 250;
  // How long the worker may take to set up its GPU before the main thread takes over.
  const WORKER_START_TIMEOUT_MS = 8000;
  // A worker that has not painted for this long has its canvas hidden (see onWorkerMessage).
  const STALE_PAINT_MS = 400;
  // Frames waiting for the worker while the page is busy: about half a second at 60 fps.
  const FRAME_QUEUE = 30;
  // Same level as the subtitles: a fixed element in its own shadow root, above everything on the
  // page. It never takes the mouse.
  const METER_CSS = `
    :host { all: initial; }
    .fps {
      position: fixed; left: 12px; top: 12px; z-index: 2147483647; pointer-events: none;
      font: 600 16px/1.3 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
      font-variant-numeric: tabular-nums; color: #fff; white-space: nowrap;
      background: rgba(0, 0, 0, .74); padding: 3px 10px; border-radius: 6px;
      text-shadow: 0 1px 2px rgba(0, 0, 0, .9);
    }
  `;

  let device = null;
  let run = null;
  let target = 0;
  let lastError = null;
  let lastDetail = null;

  function mainVideo() {
    let best = null;
    let bestScore = 0;
    for (const video of document.querySelectorAll("video")) {
      if (video.readyState < 2 || !video.videoWidth) continue;
      const box = video.getBoundingClientRect();
      const score = box.width * box.height * (video.paused ? 0.5 : 1);
      if (score > bestScore) { best = video; bestScore = score; }
    }
    return best;
  }

  async function getDevice() {
    if (device) return device;
    const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
    if (!adapter) throw Object.assign(new Error("no adapter"), { code: "no_webgpu" });
    device = await adapter.requestDevice({
      requiredLimits: {
        maxStorageBufferBindingSize: adapter.limits.maxStorageBufferBindingSize,
        maxBufferSize: adapter.limits.maxBufferSize,
      },
    });
    const created = device;
    created.lost.then(() => {
      if (device === created) device = null;
      if (run && run.device === created) stop("no_webgpu");
    });
    return device;
  }

  // The sharpening choices of the popup, as the strength PRESENT_SHADER takes.
  const SHARPEN = { off: 0, soft: 0.35, medium: 0.6, strong: 0.9 };

  // The work never goes past what the player shows. YouTube serves a 4K video to a big player on a
  // 4K screen even when it takes half the screen; at "Original" everything then ran at 4K (capture,
  // motion and 144 paintings a second) and the graphics card fell behind: stutter and green bars.
  // The height on screen, in device pixels, is taken to the nearest of these steps not far below it,
  // so dragging a window does not rebuild at every pixel, and the output follows when it changes.
  const DISPLAY_STEPS = [720, 1080, 1440, 2160];
  const DISPLAY_STEP_SLACK = 0.85;
  const RESIZE_SETTLE_MS = 500;
  // The card's load is looked at this often. Each frame's work may take as long as the video takes
  // to bring the next frame, within these limits: past that the card is falling behind the video.
  // (Tried with one and a half display ticks, 10 ms at 144 Hz: on a card that other programs keep
  // at 80 % the work takes 5-11 ms even at 720p, and everything went to the lowest step for good.)
  const LOAD_EVERY_MS = 250;
  const LOAD_BUDGET_MIN_MS = 12;
  const LOAD_BUDGET_MAX_MS = 25;
  const TICK_GAPS_KEPT = 300;

  function shownHeight(video) {
    const dpr = devicePixelRatio || 1;
    const screenHeight = Math.round(screen.height * dpr);
    let shown = video.offsetHeight;
    if (video.videoWidth && video.videoHeight && video.offsetWidth) {
      shown = Math.min(shown, (video.offsetWidth * video.videoHeight) / video.videoWidth); // bars around it
    }
    const needed = Math.round(shown * dpr);
    if (!(needed > 0)) return screenHeight;
    const step = DISPLAY_STEPS.find((h) => h >= needed * DISPLAY_STEP_SLACK) || DISPLAY_STEPS[DISPLAY_STEPS.length - 1];
    return Math.min(step, screenHeight);
  }

  // cap: the tallest picture the graphics card can take right now (see LoadGovernor in framegen.js).
  function planSizes(video, options, cap = Infinity) {
    const shown = shownHeight(video);
    // "Original" is the video's own height, "Match the screen" the player's, a number the one chosen:
    // all three capped at the player's.
    const chosen = options.resolution === "display" ? shown
      : options.resolution === "original" ? video.videoHeight || shown
      : Number(options.resolution) || video.videoHeight || shown;
    const wanted = Math.min(chosen, shown);
    const sized = Object.assign({}, options, { resolution: Math.min(wanted, cap) });
    const plan = globalThis.STFramegen.planSizes(video.videoWidth, video.videoHeight, sized, shown);
    plan.sharpen = SHARPEN[options.sharpen] ?? SHARPEN.medium;
    plan.shownHeight = shown;
    plan.wantedHeight = wanted;
    plan.lowered = cap < wanted;
    return plan;
  }

  // The same buffers and the same networks: nothing to build again.
  function samePlan(a, b) {
    return a.width === b.width && a.height === b.height && a.contentWidth === b.contentWidth && a.contentHeight === b.contentHeight
      && a.outputWidth === b.outputWidth && a.outputHeight === b.outputHeight && a.sharpen === b.sharpen
      && a.model === b.model && a.interpolator === b.interpolator;
  }

  // The player changed size (window resized, full screen on or off): new sizes once it holds.
  function checkShownSize(state, now) {
    if (!state.plan || shownHeight(state.video) === state.plan.shownHeight) {
      state.resizeSince = 0;
      return;
    }
    if (!state.resizeSince) { state.resizeSince = now; return; }
    if (now - state.resizeSince < RESIZE_SETTLE_MS) return;
    state.resizeSince = 0;
    if (state.worker) {
      state.plan = planSizes(state.video, state.options);
      state.worker.postMessage({ type: "plan", plan: state.plan });
    } else {
      // With the work lowered for the card's sake the sizes can stay as they were.
      const plan = planSizes(state.video, state.options, state.governor.cap);
      if (samePlan(plan, state.plan)) state.plan = plan;
      else build(state);
    }
    state.layoutKey = "";
  }

  // A new generator for the sizes of this moment. It goes on from the timing of the one before, so
  // a change of size costs a couple of frames and not two seconds; the canvas, emptied by its new
  // size, stays hidden until the first frame is painted on it (the video itself shows meanwhile).
  function build(state) {
    let carry = null;
    if (state.gen) {
      carry = state.gen.handover();
      state.gen.destroy();
    }
    const video = state.video;
    state.plan = planSizes(video, state.options, state.governor.cap);
    state.sourceWidth = video.videoWidth;
    state.sourceHeight = video.videoHeight;
    state.canvas.style.visibility = "hidden";
    state.gen = new globalThis.STFramegen.FrameGenerator({
      device: state.device, video, canvas: state.canvas, ...state.plan, carry,
      onCapture: (texture, index) => { if (api.onCapture) api.onCapture(texture, index); },
      onWork: (ms) => state.governor.sample(ms, performance.now()),
    });
    applyTarget(state);
  }

  // The rate asked for in the popup, or half the display's when the card cannot take more.
  function applyTarget(state) {
    if (!state.gen) return;
    let fps = target;
    if (state.governor.slow && state.displayMs) {
      const half = Math.round(500 / state.displayMs);
      fps = fps ? Math.min(fps, half) : half;
    }
    if (state.gen.targetFps === fps) return;
    state.gen.targetFps = fps;
    state.gen.nextPresentAt = 0;
  }

  // The display's interval, from the page's own ticks: the short end of the last few seconds, so
  // ticks that came late with the card or the page busy do not count.
  function displayInterval(state) {
    if (state.tickGaps.length < 60) return 0;
    const sorted = state.tickGaps.slice().sort((a, b) => a - b);
    return sorted[Math.floor(sorted.length * 0.1)];
  }

  // Four times a second: is the card keeping up? (LoadGovernor, in framegen.js.)
  function checkLoad(state, now) {
    if (now - state.loadAt < LOAD_EVERY_MS) return;
    state.loadAt = now;
    if (!state.gen || !state.plan) return;
    state.displayMs = displayInterval(state) || state.displayMs;
    const hz = state.gen.sourceHz();
    if (!state.displayMs || !hz) return;
    const budget = Math.min(LOAD_BUDGET_MAX_MS, Math.max(LOAD_BUDGET_MIN_MS, 1000 / hz));
    state.loadBudget = budget;
    if (!state.governor.update(now, budget, state.plan.wantedHeight)) return;
    const plan = planSizes(state.video, state.options, state.governor.cap);
    if (samePlan(plan, state.plan)) {
      state.plan = plan;
    } else {
      build(state);
      state.layoutKey = "";
    }
    applyTarget(state);
  }

  async function readOptions() {
    const settings = await ST.getSettings();
    const { fgModels } = await ext.storage.local.get("fgModels");
    let parsed = null;
    const entry = fgModels && fgModels[settings.fgModel];
    if (entry) {
      try {
        parsed = globalThis.STFramegenModel.parse(ST.base64ToBuffer(entry.data));
      } catch (e) {
        console.warn("[streamremaster] the selected model cannot be read:", e);
      }
    }
    return {
      resolution: settings.fgResolution,
      sharpen: settings.fgSharpen,
      model: parsed && parsed.sr,
      interpolator: parsed && parsed.fi,
    };
  }

  // ---- the worker path -------------------------------------------------------------------------

  // The worker's script: the installers of the frame generation files, which leave their code in
  // globals when they run here, and the worker's main function, written out as source.
  function workerSource() {
    const parts = [globalThis.STFramegenInstall, globalThis.STFramegenSRInstall, globalThis.STFramegenFIInstall];
    const main = globalThis.STFramegenWorkerMain;
    if (parts.some((part) => typeof part !== "function") || typeof main !== "function") return null;
    return `"use strict";\n${parts.map((part) => `(${part})(self);`).join("\n")}\n(${main})(self);\n`;
  }

  function workerPossible(video) {
    return typeof Worker === "function" && typeof MediaStreamTrackProcessor === "function"
      && typeof HTMLCanvasElement.prototype.transferControlToOffscreen === "function"
      && typeof video.captureStream === "function" && !!workerSource();
  }

  // Sets the worker up and waits until it has a GPU device; throws if anything on the way fails,
  // and then leaves nothing running (the canvas, once handed over, cannot be used here any more).
  async function startWorker(state) {
    const { video } = state;
    const stream = video.captureStream();
    for (const track of stream.getAudioTracks()) track.stop();
    const track = stream.getVideoTracks()[0];
    if (!track) throw new Error("the video gives no track to capture");
    state.track = track;
    const processor = new MediaStreamTrackProcessor({ track, maxBufferSize: FRAME_QUEUE });
    const url = URL.createObjectURL(new Blob([workerSource()], { type: "text/javascript" }));
    try {
      state.worker = new Worker(url);
      state.plan = planSizes(video, state.options);
      state.sourceWidth = video.videoWidth;
      state.sourceHeight = video.videoHeight;
      const offscreen = state.canvas.transferControlToOffscreen();
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error("the worker did not start")), WORKER_START_TIMEOUT_MS);
        state.worker.onerror = (event) => { clearTimeout(timeout); reject(new Error(event.message || "worker error")); };
        state.worker.onmessage = (event) => {
          const message = event.data || {};
          if (message.type === "ready") { clearTimeout(timeout); resolve(); }
          else if (message.type === "error") { clearTimeout(timeout); reject(Object.assign(new Error(message.detail), { code: message.code })); }
        };
        state.worker.postMessage({ type: "init", canvas: offscreen, readable: processor.readable, plan: state.plan, target },
          [offscreen, processor.readable]);
      });
    } catch (error) {
      endWorker(state);
      throw error;
    } finally {
      URL.revokeObjectURL(url);
    }
    state.worker.onerror = (event) => { if (run === state) stop("cannot_read", event.message); };
    state.worker.onmessage = (event) => onWorkerMessage(state, event.data || {});
  }

  function onWorkerMessage(state, message) {
    if (run !== state) return;
    if (message.type === "status") {
      state.remote = message;
      // The worker shows its canvas but has painted nothing for a while: take the canvas away so the
      // video itself shows, never a frozen picture over it. The worker shows it again when it paints.
      if (message.sincePaintMs > STALE_PAINT_MS && state.canvas.style.visibility !== "hidden") {
        state.canvas.style.visibility = "hidden";
      }
    }
    else if (message.type === "visible") state.canvas.style.visibility = message.visible ? "visible" : "hidden";
    else if (message.type === "ended") restart(state); // the video changed source: a new track
    else if (message.type === "error") stop(message.code || "cannot_read", message.detail);
  }

  function endWorker(state) {
    if (state.worker) {
      try { state.worker.postMessage({ type: "stop" }); } catch { /* already gone */ }
      state.worker.terminate();
      state.worker = null;
    }
    if (state.track) {
      state.track.stop();
      state.track = null;
    }
  }

  // The video started playing something else: on the worker path the captured track goes with the
  // old source, so it all starts again on the new one.
  function restart(state) {
    if (state.restarting) return;
    state.restarting = true;
    setTimeout(() => { if (run === state) start(target); }, 300);
  }

  // ---- what both paths share --------------------------------------------------------------------

  function createMeter() {
    const host = document.createElement("stream-remaster-fps");
    const root = host.attachShadow({ mode: "open" });
    const style = document.createElement("style");
    style.textContent = METER_CSS;
    const label = document.createElement("div");
    label.className = "fps";
    label.textContent = "… fps";
    root.append(style, label);
    return { host, label };
  }

  // In fullscreen the browser only paints the fullscreen element and its descendants.
  function placeMeter(state) {
    let parent = document.fullscreenElement || document.webkitFullscreenElement || null;
    if (parent && /^(VIDEO|AUDIO|IMG|CANVAS)$/.test(parent.tagName)) parent = parent.parentElement;
    parent = parent || document.documentElement;
    if (state.meter.host.parentNode !== parent) parent.appendChild(state.meter.host);
  }

  // Source rate, frames painted in the last second, and whether each network is running.
  function liveInfo(state) {
    if (state.worker) {
      const r = state.remote || {};
      return { hz: r.sourceHz || 0, fps: r.fps || 0, sr: !!r.modelReady, fi: !!r.interpolatorReady };
    }
    const gen = state.gen;
    return {
      hz: gen ? gen.sourceHz() : 0,
      fps: state.paints.length,
      sr: !!(gen && gen.upscaler && gen.upscaler.ready),
      fi: !!(gen && gen.interpolator && gen.interpolator.ready),
    };
  }

  function updateMeter(state, now) {
    if (now - state.meterAt < METER_EVERY_MS) return;
    state.meterAt = now;
    const { hz, fps, sr, fi } = liveInfo(state);
    // two decimals when the rate is not a whole number (59.94, 29.97, 23.98), so it can be told apart
    const source = Math.abs(hz - Math.round(hz)) < 0.005 ? String(Math.round(hz)) : hz.toFixed(2);
    // "↓1080p": the work was lowered to that height because the graphics card was not keeping up
    const lowered = !state.worker && state.plan && state.plan.lowered ? ` · ↓${state.plan.outputHeight}p` : "";
    state.meter.label.textContent = hz ? `${source} → ${fps} fps${sr ? " · SR" : ""}${fi ? " · FI" : ""}${lowered}` : "… fps";
  }

  // Same box as the video, inside the same positioned parent, so the page's own layout moves both.
  function layout(state) {
    const { video, canvas } = state;
    const key = [video.offsetLeft, video.offsetTop, video.offsetWidth, video.offsetHeight].join();
    if (key === state.layoutKey) return;
    state.layoutKey = key;
    const computed = getComputedStyle(video);
    Object.assign(canvas.style, {
      left: video.offsetLeft + "px",
      top: video.offsetTop + "px",
      width: video.offsetWidth + "px",
      height: video.offsetHeight + "px",
      objectFit: computed.objectFit,
      objectPosition: computed.objectPosition,
    });
  }

  function errorCode(error) {
    lastDetail = String((error && error.message) || error).slice(0, 300);
    if (error && typeof error.code === "string") return error.code; // a DOMException's code is a number
    return error && error.name === "NotSupportedError" ? "no_webgpu" : "cannot_read";
  }

  function step(state, now) {
    const video = state.video;
    if (!video.isConnected) { stop("no_video"); return; }
    // The extension was reloaded or removed: this copy can no longer be reached from the popup,
    // so it takes its canvas away instead of staying over the video for good.
    if (!ext.runtime || !ext.runtime.id) { stop(); return; }
    if (video.videoWidth && (video.videoWidth !== state.sourceWidth || video.videoHeight !== state.sourceHeight)) {
      if (state.worker) {
        state.plan = planSizes(video, state.options);
        state.sourceWidth = video.videoWidth;
        state.sourceHeight = video.videoHeight;
        state.worker.postMessage({ type: "plan", plan: state.plan });
      } else {
        build(state);
      }
      state.layoutKey = "";
    }
    if (state.ticks % LAYOUT_EVERY_TICKS === 1) checkShownSize(state, now);
    if (state.ticks++ % LAYOUT_EVERY_TICKS === 0) layout(state);

    if (state.lastTick) {
      const gap = now - state.lastTick;
      if (gap > 20) state.gaps20++;
      if (gap > 50) state.gaps50++;
      state.tickGaps.push(gap);
      if (state.tickGaps.length > TICK_GAPS_KEPT) state.tickGaps.shift();
    }
    state.lastTick = now;
    if (!state.worker) checkLoad(state, now);

    // On the worker path the worker paints and says when to show or hide the canvas.
    if (!state.worker) {
      if (state.gen.tick(now)) {
        state.lastPaint = now;
        state.canvas.style.visibility = "visible";
        state.paints.push(now);
      } else if (now - state.lastPaint > HIDE_AFTER_MS) {
        state.canvas.style.visibility = "hidden";
      }
      while (state.paints.length && state.paints[0] <= now - 1000) state.paints.shift();
    }
    updateMeter(state, now);
    debugStatus(state, now);
  }

  // A hidden switch for measuring on a real page: with localStorage["st-fg-debug"] = "1" on that
  // site the status is written to <html data-st-fg-status> once a second, where the page's own
  // console can read it (the extension's context is hard to pick out among many in DevTools).
  function debugStatus(state, now) {
    if (now - (state.debugAt || 0) < 1000) return;
    state.debugAt = now;
    let on = false;
    try { on = localStorage.getItem("st-fg-debug") === "1"; } catch { /* storage blocked */ }
    if (on) document.documentElement.setAttribute("data-st-fg-status", JSON.stringify(status()));
  }

  function makeCanvas(video) {
    const canvas = document.createElement("canvas");
    canvas.style.cssText = "position:absolute;pointer-events:none;margin:0;padding:0;border:0;visibility:hidden;";
    video.insertAdjacentElement("afterend", canvas);
    return canvas;
  }

  // options.worker: use the worker where possible (off by default, see the top of this file).
  async function start(targetFps, options = {}) {
    stop();
    lastError = null;
    lastDetail = null;
    target = Number(targetFps) || 0;
    if (!navigator.gpu) return fail("no_webgpu");
    const video = mainVideo();
    if (!video) return fail("no_video");
    if (video.mediaKeys) return fail("cannot_read"); // protected video decodes to black here

    let settings;
    try {
      settings = await readOptions();
    } catch (error) {
      return fail(error.code || "no_webgpu");
    }

    const state = {
      device: null, video, canvas: makeCanvas(video), options: settings, plan: null, gen: null,
      worker: null, track: null, remote: null, restarting: false,
      ticks: 0, lastPaint: 0, lastTick: 0, paints: [],
      gaps20: 0, gaps50: 0, raf: 0, layoutKey: "", sourceWidth: 0, sourceHeight: 0,
      sourceResets: 0,
      governor: new globalThis.STFramegen.LoadGovernor(), tickGaps: [], displayMs: 0, loadAt: 0, loadBudget: 0,
      onSource: () => {
        state.sourceResets++;
        if (state.worker) restart(state);
        else if (state.gen) state.gen.resetSource();
      },
      meter: createMeter(),
      meterAt: 0,
      onFullscreen: () => placeMeter(state),
      // Back from the background: the worker starts its timing afresh (see forgetLateness).
      onVisibility: () => {
        if (!state.worker) return;
        state.worker.postMessage({ type: document.visibilityState === "visible" ? "resume" : "hidden" });
      },
    };

    if (options.worker && workerPossible(video)) {
      try {
        await startWorker(state);
      } catch (error) {
        console.warn("[streamremaster] smooth video on its own thread unavailable, using the page's:", error);
        state.canvas.remove(); // handed over to the worker: it cannot be drawn on from here
        state.canvas = makeCanvas(video);
      }
    }
    if (!state.worker) {
      try {
        state.device = await getDevice();
        build(state);
      } catch (error) {
        state.canvas.remove();
        return fail(errorCode(error));
      }
    }
    if (run) { // started again meanwhile
      endWorker(state);
      if (state.gen) state.gen.destroy();
      state.canvas.remove();
      return status();
    }
    video.addEventListener("emptied", state.onSource);
    video.addEventListener("loadedmetadata", state.onSource);
    document.addEventListener("fullscreenchange", state.onFullscreen);
    document.addEventListener("visibilitychange", state.onVisibility);
    document.addEventListener("webkitfullscreenchange", state.onFullscreen);
    placeMeter(state);
    run = state;
    const loop = (now) => {
      if (run !== state) return;
      state.raf = requestAnimationFrame(loop);
      try {
        step(state, now);
      } catch (error) {
        console.warn("[streamremaster] frame generation stopped:", error);
        stop(errorCode(error));
      }
    };
    state.raf = requestAnimationFrame(loop);
    return status();
  }

  function fail(code) {
    lastError = code;
    return status();
  }

  function stop(error, detail) {
    if (error) lastError = error;
    if (detail) lastDetail = String(detail).slice(0, 300);
    const state = run;
    if (!state) return status();
    run = null;
    cancelAnimationFrame(state.raf);
    state.video.removeEventListener("emptied", state.onSource);
    state.video.removeEventListener("loadedmetadata", state.onSource);
    document.removeEventListener("fullscreenchange", state.onFullscreen);
    document.removeEventListener("visibilitychange", state.onVisibility);
    document.removeEventListener("webkitfullscreenchange", state.onFullscreen);
    state.meter.host.remove();
    endWorker(state);
    if (state.gen) state.gen.destroy();
    state.canvas.remove();
    return status();
  }

  function setTarget(targetFps) {
    target = Number(targetFps) || 0;
    if (run && run.worker) run.worker.postMessage({ type: "target", target });
    if (run && run.gen) {
      run.gen.nextPresentAt = 0;
      applyTarget(run);
    }
    return status();
  }

  // The resolution or the model changed in the popup.
  async function reconfigure() {
    if (!run) return status();
    const state = run;
    const options = await readOptions();
    if (run !== state) return status();
    state.options = options;
    if (state.worker) {
      state.plan = planSizes(state.video, options);
      state.worker.postMessage({ type: "plan", plan: state.plan });
    } else {
      build(state);
    }
    state.layoutKey = "";
    return status();
  }

  function status() {
    if (!run) return { running: false, state: "off", error: lastError, detail: lastDetail, target };
    const info = liveInfo(run);
    const remote = run.remote || {};
    return {
      running: true,
      state: info.hz ? "on" : "measuring",
      thread: run.worker ? "worker" : "page",
      fps: info.fps,
      sourceHz: info.hz,
      delayMs: run.worker ? remote.delayMs || 0 : null,
      workerGaps20: run.worker ? remote.gaps20 || 0 : null,
      workerSkipped: run.worker ? remote.skipped || 0 : null,
      target,
      error: null,
      gaps20: run.gaps20,
      gaps50: run.gaps50,
      ticks: run.ticks,
      sourceResets: run.sourceResets,
      stats: run.worker ? remote.stats || null : run.gen ? { ...run.gen.stats } : null,
      size: run.plan ? [run.plan.outputWidth, run.plan.outputHeight] : null,
      input: run.plan ? [run.plan.width, run.plan.height] : null,
      memory: run.plan ? globalThis.STFramegen.memoryBytes(run.plan) : null,
      load: run.worker ? null : {
        cap: Number.isFinite(run.governor.cap) ? run.governor.cap : null, slow: run.governor.slow,
        workMs: Number.isFinite(run.governor.median) ? +run.governor.median.toFixed(1) : null,
        budgetMs: +run.loadBudget.toFixed(1), displayMs: +run.displayMs.toFixed(2),
        gen: run.gen ? run.gen.targetFps : null,
      },
      model: run.plan && run.plan.model ? run.plan.model.name : null,
      modelReady: info.sr,
      interpolator: run.plan && run.plan.interpolator ? run.plan.interpolator.name : null,
      interpolatorReady: info.fi,
    };
  }

  const api = { start, stop, setTarget, reconfigure, status, onCapture: null, device: () => device };
  globalThis.STFramegenPage = api;

  // sendResponse rather than a returned promise: Chromium's content scripts do not take promises.
  ext.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (!msg || msg.st !== "framegen") return undefined;
    if (msg.cmd === "start") {
      start(msg.target).then(sendResponse);
      return true;
    }
    if (msg.cmd === "reconfigure") {
      reconfigure().then(sendResponse);
      return true;
    }
    if (msg.cmd === "stop") sendResponse(stop());
    else if (msg.cmd === "target") sendResponse(setTarget(msg.target));
    else if (msg.cmd === "status") sendResponse(status());
    return undefined;
  });
})();
