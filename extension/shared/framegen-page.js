// Runs frame generation on the page's main video: finds the video, lays a canvas over it and
// answers the popup. Nothing touches the GPU until the user turns it on.
"use strict";

(function () {
  if (globalThis.STFramegenPage) return;

  const MAX_OUTPUT_HEIGHT = 2160;
  // Above this the network costs more than a frame on mid-range cards.
  const MAX_MODEL_INPUT_HEIGHT = 1080;
  const LAYOUT_EVERY_TICKS = 8;
  // With nothing painted for this long (paused, seeking, buffering) the real video shows through.
  const HIDE_AFTER_MS = 200;
  const METER_EVERY_MS = 250;
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

  const even = (n) => Math.max(2, Math.round(n / 2) * 2);
  // The sharpening choices of the popup, as the strength PRESENT_SHADER takes.
  const SHARPEN = { off: 0, soft: 0.35, medium: 0.6, strong: 0.9 };

  // What to capture and what to paint for the chosen resolution. The network only runs when the
  // output is larger than the video.
  function planSizes(video, options) {
    const width = video.videoWidth;
    const height = video.videoHeight;
    let wanted = height;
    if (options.resolution === "display") wanted = Math.round(screen.height * devicePixelRatio);
    else if (options.resolution !== "original") wanted = Number(options.resolution) || height;
    const outputHeight = even(Math.min(MAX_OUTPUT_HEIGHT, wanted));
    const useModel = !!options.model && outputHeight > height;
    // The interpolator needs captured frames in multiples of 16; the canvas is stretched to the
    // video's box anyway, so a few pixels more or less do not show.
    const round = options.interpolator ? (n) => Math.max(16, Math.round(n / 16) * 16) : even;
    const inputHeight = round(Math.min(height, outputHeight, useModel ? MAX_MODEL_INPUT_HEIGHT : Infinity));
    return {
      width: round((width * inputHeight) / height), height: inputHeight,
      outputWidth: even((width * outputHeight) / height), outputHeight,
      model: useModel ? options.model : null,
      interpolator: options.interpolator || null,
      sharpen: SHARPEN[options.sharpen] ?? SHARPEN.medium,
    };
  }

  function build(state) {
    if (state.gen) state.gen.destroy();
    const video = state.video;
    state.plan = planSizes(video, state.options);
    state.sourceWidth = video.videoWidth;
    state.sourceHeight = video.videoHeight;
    state.gen = new globalThis.STFramegen.FrameGenerator({
      device: state.device, video, canvas: state.canvas, ...state.plan,
      onCapture: (texture, index) => { if (api.onCapture) api.onCapture(texture, index); },
    });
    state.gen.targetFps = target;
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

  function updateMeter(state, now) {
    if (now - state.meterAt < METER_EVERY_MS) return;
    state.meterAt = now;
    const hz = state.gen.sourceHz();
    const upscaling = state.gen.upscaler && state.gen.upscaler.ready ? " · SR" : "";
    const interpolating = state.gen.interpolator && state.gen.interpolator.ready ? " · FI" : "";
    // two decimals when the rate is not a whole number (59.94, 29.97, 23.98), so it can be told apart
    const source = Math.abs(hz - Math.round(hz)) < 0.005 ? String(Math.round(hz)) : hz.toFixed(2);
    state.meter.label.textContent = hz ? `${source} → ${state.paints.length} fps${upscaling}${interpolating}` : "… fps";
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
      build(state);
      state.layoutKey = "";
    }
    if (state.ticks++ % LAYOUT_EVERY_TICKS === 0) layout(state);

    if (state.lastTick) {
      const gap = now - state.lastTick;
      if (gap > 20) state.gaps20++;
      if (gap > 50) state.gaps50++;
    }
    state.lastTick = now;

    if (state.gen.tick(now)) {
      state.lastPaint = now;
      state.canvas.style.visibility = "visible";
      state.paints.push(now);
    } else if (now - state.lastPaint > HIDE_AFTER_MS) {
      state.canvas.style.visibility = "hidden";
    }
    while (state.paints.length && state.paints[0] <= now - 1000) state.paints.shift();
    updateMeter(state, now);
  }

  async function start(targetFps) {
    stop();
    lastError = null;
    target = Number(targetFps) || 0;
    if (!navigator.gpu) return fail("no_webgpu");
    const video = mainVideo();
    if (!video) return fail("no_video");
    if (video.mediaKeys) return fail("cannot_read"); // protected video decodes to black here

    let gpu;
    let options;
    try {
      gpu = await getDevice();
      options = await readOptions();
    } catch (error) {
      return fail(error.code || "no_webgpu");
    }

    const canvas = document.createElement("canvas");
    canvas.style.cssText = "position:absolute;pointer-events:none;margin:0;padding:0;border:0;visibility:hidden;";
    video.insertAdjacentElement("afterend", canvas);

    const state = {
      device: gpu, video, canvas, options, plan: null, gen: null, ticks: 0, lastPaint: 0, lastTick: 0, paints: [],
      gaps20: 0, gaps50: 0, raf: 0, layoutKey: "", sourceWidth: 0, sourceHeight: 0,
      sourceResets: 0,
      onSource: () => { state.sourceResets++; if (state.gen) state.gen.resetSource(); },
      meter: createMeter(),
      meterAt: 0,
      onFullscreen: () => placeMeter(state),
    };
    try {
      build(state);
    } catch (error) {
      canvas.remove();
      return fail(errorCode(error));
    }
    video.addEventListener("emptied", state.onSource);
    video.addEventListener("loadedmetadata", state.onSource);
    document.addEventListener("fullscreenchange", state.onFullscreen);
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

  function stop(error) {
    if (error) lastError = error;
    const state = run;
    if (!state) return status();
    run = null;
    cancelAnimationFrame(state.raf);
    state.video.removeEventListener("emptied", state.onSource);
    state.video.removeEventListener("loadedmetadata", state.onSource);
    document.removeEventListener("fullscreenchange", state.onFullscreen);
    document.removeEventListener("webkitfullscreenchange", state.onFullscreen);
    state.meter.host.remove();
    if (state.gen) state.gen.destroy();
    state.canvas.remove();
    return status();
  }

  function setTarget(targetFps) {
    target = Number(targetFps) || 0;
    if (run && run.gen) {
      run.gen.targetFps = target;
      run.gen.nextPresentAt = 0;
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
    build(state);
    state.layoutKey = "";
    return status();
  }

  function status() {
    if (!run) return { running: false, state: "off", error: lastError, detail: lastDetail, target };
    const hz = run.gen ? run.gen.sourceHz() : 0;
    return {
      running: true,
      state: hz ? "on" : "measuring",
      fps: run.paints.length,
      sourceHz: hz,
      target,
      error: null,
      gaps20: run.gaps20,
      gaps50: run.gaps50,
      ticks: run.ticks,
      sourceResets: run.sourceResets,
      stats: run.gen ? { ...run.gen.stats } : null,
      size: run.gen ? [run.canvas.width, run.canvas.height] : null,
      input: run.plan ? [run.plan.width, run.plan.height] : null,
      model: run.plan && run.plan.model ? run.plan.model.name : null,
      modelReady: !!(run.gen && run.gen.upscaler && run.gen.upscaler.ready),
      interpolator: run.plan && run.plan.interpolator ? run.plan.interpolator.name : null,
      interpolatorReady: !!(run.gen && run.gen.interpolator && run.gen.interpolator.ready),
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
