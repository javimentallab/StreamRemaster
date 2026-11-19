// Smooth video on the page: finds the video being watched, lays a canvas over it, feeds the frames
// to the graphics card and paints the canvas on every refresh of the screen. It answers the popup
// and the watcher that starts it by itself. Nothing touches the graphics card until it is turned on.
//
// One way of working, on the page's own thread, in every browser. What differs is how frames come in:
//   - Chromium calls requestVideoFrameCallback for every frame, right when the video shows it and
//     while the <video> holds that very frame: each frame is taken there, once, with its timestamp.
//   - Gecko calls it for about 25 frames a second of a 60 fps video. There the frames are taken on
//     the screen's refresh, when the video's clock says a new one is up (Schedule.due), and those
//     calls only tell where the frames sit in time.
"use strict";

(function () {
  if (globalThis.STFramegenPage) return;

  const FG = globalThis.STFramegen;
  const GECKO = /firefox/i.test(navigator.userAgent);
  // With nothing painted for this long (paused, seeking, buffering) the video itself shows through.
  const HIDE_AFTER_MS = 200;
  const HOUSEKEEPING_MS = 250;
  // A new size of the player counts once it has held this long (a window being dragged).
  const RESIZE_SETTLE_MS = 500;
  // The rate at which paintings are spread when the target is under the screen's: a refresh that
  // comes this much early still counts (browser clocks round to the millisecond).
  const TARGET_TOLERANCE_MS = 1.5;
  const SHARPEN = { off: 0, soft: 0.35, medium: 0.6, strong: 0.9 };
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

  // In Chromium the video under a shown canvas is hidden. Left in view, the browser keeps handing
  // it to the screen as a layer of its own beneath ours and, with a large player, stalls when it
  // presents the two (measured on YouTube: stalls of up to 48 ms several times a second). Its
  // frames keep coming all the same. Gecko is left alone: it may stop decoding a video nobody sees.
  const HIDE_VIDEO_BENEATH = !GECKO;
  // Parts of a page that cost the browser dearly under a picture repainted on every refresh, put
  // away while the canvas shows. YouTube's ambient mode (the blurred glow around the player).
  const COSTLY = [{ host: /(^|\.)youtube\.com$/, selector: "#cinematics" }];
  const costly = COSTLY.find((rule) => rule.host.test(location.hostname)) || null;

  let device = null;
  let session = null;
  let target = 0;
  let lastError = null;
  let lastDetail = null;

  // ---- the video and what to do with it -----------------------------------------------------------

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
    const created = await adapter.requestDevice({
      requiredLimits: {
        maxStorageBufferBindingSize: adapter.limits.maxStorageBufferBindingSize,
        maxBufferSize: adapter.limits.maxBufferSize,
      },
    });
    device = created;
    created.lost.then(() => {
      if (device === created) device = null;
      if (session && session.device === created) stop("no_webgpu");
    });
    return device;
  }

  async function readOptions() {
    const settings = await ST.getSettings();
    const { fgModels } = await ext.storage.local.get("fgModels");
    const entry = fgModels && fgModels[settings.fgModel];
    let model = null;
    if (entry) {
      try {
        model = globalThis.STFramegenModel.parse(ST.base64ToBuffer(entry.data));
      } catch (error) {
        console.warn("[streamremaster] the selected model cannot be read:", error);
      }
    }
    return {
      resolution: settings.fgResolution,
      sharpen: SHARPEN[settings.fgSharpen] ?? SHARPEN.medium,
      meter: settings.fgMeter !== false,
      model: model && model.sr,
      interpolator: model && model.fi,
    };
  }

  // The height the player takes on screen, in device pixels and in steps (see FG.shownStep): the
  // picture inside the video's box, without the bars around it.
  function shownHeight(video) {
    const ratio = devicePixelRatio || 1;
    let height = video.offsetHeight;
    if (video.videoWidth && video.videoHeight && video.offsetWidth) {
      height = Math.min(height, (video.offsetWidth * video.videoHeight) / video.videoWidth);
    }
    return FG.shownStep(Math.round(height * ratio), Math.round(screen.height * ratio));
  }

  function makePlan(video, options) {
    const shown = shownHeight(video);
    const plan = FG.planSizes(video.videoWidth, video.videoHeight, options, shown);
    plan.sharpen = options.sharpen;
    plan.shown = shown;
    plan.source = [video.videoWidth, video.videoHeight];
    return plan;
  }

  const WORK_KEYS = ["width", "height", "contentWidth", "contentHeight", "outputWidth", "outputHeight", "sharpen", "model", "interpolator"];
  const sameWork = (a, b) => WORK_KEYS.every((key) => a[key] === b[key]);

  // New buffers and networks for the sizes of this moment. The timing carries on: only the frames
  // in hand are lost, and the canvas, emptied by its new size, stays hidden until it is painted
  // again (the video itself shows meanwhile), which is a few frames.
  function build(s) {
    const plan = makePlan(s.video, s.options);
    if (s.renderer && sameWork(plan, s.plan)) {
      s.plan = plan;
      return;
    }
    if (s.renderer) s.renderer.destroy();
    s.plan = plan;
    s.schedule.forget();
    showCanvas(s, false);
    s.renderer = new FG.Renderer({ device: s.device, canvas: s.canvas, plan });
  }

  // ---- frames in ----------------------------------------------------------------------------------

  const playing = (video) => !video.paused && !video.seeking && video.readyState >= 2 && !!video.videoWidth;

  // The frame the video shows right now, stamped with the media time it is shown from.
  function take(s, media, wall) {
    s.schedule.seen(media);
    if (s.renderer.busy()) return;
    const { frame, previous, bridge } = s.schedule.take(media, wall);
    s.renderer.take(s.video, frame, previous, bridge);
    if (api.onFrame) api.onFrame(s.renderer.frames[frame.slot].texture, media, s);
  }

  // The video's frame callback: the exact media time of a frame and the moment it reaches the screen
  // (expectedDisplayTime), which is what the clock is set by in every browser. Gecko's currentTime
  // is no use for it: it moves in steps of 40 ms and runs 10-25 ms behind the picture on screen
  // (measured in Firefox 160). Chromium calls it for every frame, and the frame is taken here;
  // Gecko for about 25 a second, and there the frames are taken on the refresh (takeOnTick).
  function onVideoFrame(s, wall, metadata) {
    if (session !== s) return;
    s.frameCall = s.video.requestVideoFrameCallback((w, m) => onVideoFrame(s, w, m));
    if (!metadata || typeof metadata.mediaTime !== "number") return;
    const video = s.video;
    if (!playing(video) || !s.renderer) return;
    s.frameCalls++;
    const shownAt = metadata.expectedDisplayTime > 0 ? metadata.expectedDisplayTime : wall;
    try {
      s.schedule.clock(metadata.mediaTime, shownAt, video.playbackRate || 1);
      if (GECKO) {
        s.schedule.grid.sample(metadata.mediaTime, s.counter.hz);
        return;
      }
      if (Number.isFinite(s.schedule.lastSeen) && metadata.mediaTime <= s.schedule.lastSeen) return;
      take(s, metadata.mediaTime, wall);
    } catch (error) {
      console.warn("[streamremaster] smooth video stopped:", error);
      stop(errorCode(error));
    }
  }

  // Gecko: on the screen's refresh, by the clock the frame callbacks set (currentTime only where
  // there are no frame callbacks, before Firefox 132).
  function takeOnTick(s, wall) {
    const video = s.video;
    const rate = video.playbackRate || 1;
    const reading = video.currentTime;
    if (!s.frameCalls && reading !== s.lastReading) {
      s.lastReading = reading;
      s.schedule.clock(reading, wall, rate);
    }
    const rough = video.getVideoPlaybackQuality ? s.counter.add(video.getVideoPlaybackQuality().totalVideoFrames, wall, rate) : 0;
    const media = s.schedule.due(wall, rough);
    if (media !== null) take(s, media, wall);
  }

  // ---- the canvas ---------------------------------------------------------------------------------

  function makeCanvas(video) {
    const canvas = document.createElement("canvas");
    canvas.style.cssText = "position:absolute;pointer-events:none;margin:0;padding:0;border:0;visibility:hidden;";
    video.insertAdjacentElement("afterend", canvas);
    return canvas;
  }

  // The same box as the video, in the same parent, so the page's own layout moves both.
  function layout(s) {
    const { video, canvas } = s;
    const key = [video.offsetLeft, video.offsetTop, video.offsetWidth, video.offsetHeight].join();
    if (key === s.layoutKey) return;
    s.layoutKey = key;
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

  // Sets a style on an element, remembering what it had, or puts back what it had.
  function override(s, element, property, value) {
    const style = element.style;
    const kept = s.overrides.find((entry) => entry[0] === element && entry[1] === property);
    if (value !== null) {
      if (kept) return;
      s.overrides.push([element, property, style.getPropertyValue(property), style.getPropertyPriority(property)]);
      style.setProperty(property, value, "important");
    } else if (kept) {
      s.overrides.splice(s.overrides.indexOf(kept), 1);
      style.removeProperty(property);
      if (kept[2]) style.setProperty(property, kept[2], kept[3]);
    }
  }

  function putAwayCostly(s) {
    if (!costly) return;
    for (const element of document.querySelectorAll(costly.selector)) override(s, element, "display", "none");
  }

  // Shows the canvas, or takes it away so the video itself shows.
  function showCanvas(s, visible) {
    const wanted = visible ? "visible" : "hidden";
    if (s.canvas.style.visibility !== wanted) s.canvas.style.visibility = wanted;
    if (s.shown === visible) return;
    s.shown = visible;
    if (visible) {
      if (HIDE_VIDEO_BENEATH) override(s, s.video, "visibility", "hidden");
      putAwayCostly(s);
    } else {
      for (const [element, property] of s.overrides.slice()) override(s, element, property, null);
    }
  }

  // ---- the frame rate label -----------------------------------------------------------------------

  function createMeter() {
    const host = document.createElement("stream-remaster-fps");
    const shadow = host.attachShadow({ mode: "open" });
    const style = document.createElement("style");
    style.textContent = METER_CSS;
    const label = document.createElement("div");
    label.className = "fps";
    label.textContent = "… fps";
    shadow.append(style, label);
    return { host, label };
  }

  // In full screen the browser only paints the full-screen element and what is inside it.
  // The label is a choice of the user's: without it, it is not on the page at all.
  function placeMeter(s) {
    if (!s.options.meter) {
      s.meter.host.remove();
      return;
    }
    let parent = document.fullscreenElement || document.webkitFullscreenElement || null;
    if (parent && /^(VIDEO|AUDIO|IMG|CANVAS)$/.test(parent.tagName)) parent = parent.parentElement;
    parent = parent || document.documentElement;
    if (s.meter.host.parentNode !== parent) parent.appendChild(s.meter.host);
  }

  const USUAL_RATES = [23.976, 24, 25, 29.97, 30, 48, 50, 59.94, 60, 120];
  const sourceHz = (s) => (s.schedule.period ? 1 / s.schedule.period : 0);

  function updateMeter(s) {
    // The usual rate it is nearest to, when it is within the error of the timestamps; two decimals
    // when it is not a whole number (59.94, 29.97, 23.98), to tell them apart.
    let hz = sourceHz(s);
    const usual = USUAL_RATES.reduce((a, b) => (Math.abs(b - hz) < Math.abs(a - hz) ? b : a));
    if (Math.abs(usual - hz) < usual * 0.004) hz = usual;
    const source = Math.abs(hz - Math.round(hz)) < 0.005 ? String(Math.round(hz)) : hz.toFixed(2);
    const renderer = s.renderer;
    s.meter.label.textContent = hz
      ? `${source} → ${s.paints.length} fps${renderer.upscalerReady ? " · SR" : ""}${renderer.motionReady ? " · FI" : ""}`
      : "… fps";
  }

  // ---- the loop -----------------------------------------------------------------------------------

  // The paintings are spread evenly at the target rate; with no target, or one above the screen's,
  // every refresh paints.
  function dueToPaint(s, now) {
    if (!target) return true;
    if (now + TARGET_TOLERANCE_MS < s.nextPaint) return false;
    s.nextPaint = Math.max(s.nextPaint + 1000 / target, now);
    return true;
  }

  function housekeeping(s, now) {
    const video = s.video;
    layout(s);
    if (s.shown) putAwayCostly(s);
    // The player changed size (the window, full screen): new sizes once it holds.
    if (shownHeight(video) === s.plan.shown) {
      s.resizedAt = 0;
    } else if (!s.resizedAt) {
      s.resizedAt = now;
    } else if (now - s.resizedAt >= RESIZE_SETTLE_MS) {
      s.resizedAt = 0;
      build(s);
    }
    updateMeter(s);
    // For measuring on a real page: with localStorage["st-fg-debug"] = "1" on that site, the status
    // is written to <html data-st-fg-status> where the page's own console can read it.
    let debug = false;
    try { debug = localStorage.getItem("st-fg-debug") === "1"; } catch { /* storage blocked */ }
    if (debug) document.documentElement.setAttribute("data-st-fg-status", JSON.stringify(status()));
  }

  function tick(s, now) {
    const video = s.video;
    if (!video.isConnected) { stop("no_video"); return; }
    // The extension was reloaded or removed: the popup can no longer reach this copy, so it takes
    // its canvas away instead of staying over the video for good.
    if (!ext.runtime || !ext.runtime.id) { stop(); return; }
    if (video.videoWidth && (video.videoWidth !== s.plan.source[0] || video.videoHeight !== s.plan.source[1])) build(s);
    if (now - s.housekeptAt >= HOUSEKEEPING_MS) {
      s.housekeptAt = now;
      housekeeping(s, now);
    }
    if (s.lastTick) {
      const gap = now - s.lastTick;
      if (gap > 20) s.gaps20++;
      if (gap > 50) s.gaps50++;
    }
    s.lastTick = now;

    let painted = false;
    if (playing(video)) {
      // Gecko stamps the refresh with when it was due, which under load can be tens of
      // milliseconds before this code runs: the frame the video holds is the one of this moment.
      if (GECKO) takeOnTick(s, performance.now());
      const view = dueToPaint(s, now) ? s.schedule.view(now) : null;
      if (view) {
        s.renderer.paint(view.a, view.b, view.t, view.moving);
        painted = true;
      }
    } else {
      s.counter.reset();
    }
    if (painted) {
      s.lastPaint = now;
      s.paints.push(now);
      showCanvas(s, true);
    } else if (now - s.lastPaint > HIDE_AFTER_MS) {
      showCanvas(s, false);
    }
    while (s.paints.length && s.paints[0] <= now - 1000) s.paints.shift();
  }

  // ---- on and off ---------------------------------------------------------------------------------

  function errorCode(error) {
    lastDetail = String((error && error.message) || error).slice(0, 300);
    if (error && typeof error.code === "string") return error.code; // a DOMException's code is a number
    return error && error.name === "NotSupportedError" ? "no_webgpu" : "cannot_read";
  }

  function fail(code) {
    lastError = code;
    return status();
  }

  async function start(targetFps) {
    stop();
    lastError = null;
    lastDetail = null;
    target = Number(targetFps) || 0;
    if (!navigator.gpu) return fail("no_webgpu");
    const video = mainVideo();
    if (!video) return fail("no_video");
    if (video.mediaKeys) return fail("cannot_read"); // protected video decodes to black here

    const starting = {};
    start.latest = starting;
    let options;
    let gpu;
    try {
      options = await readOptions();
      gpu = await getDevice();
    } catch (error) {
      return fail(errorCode(error));
    }
    if (start.latest !== starting || session) return status(); // started again meanwhile

    const s = {
      video, device: gpu, options, canvas: makeCanvas(video), meter: createMeter(),
      schedule: new FG.Schedule(), counter: new FG.Counter(), renderer: null, plan: null,
      shown: false, overrides: [], layoutKey: "", paints: [],
      lastPaint: 0, lastTick: 0, nextPaint: 0, housekeptAt: 0, resizedAt: 0, lastReading: NaN,
      gaps20: 0, gaps50: 0, jumps: 0, frame: 0, frameCall: 0, frameCalls: 0,
    };
    try {
      build(s);
    } catch (error) {
      s.canvas.remove();
      return fail(errorCode(error));
    }
    // The element plays something else, or another part of the same: start the timing afresh.
    s.onJump = () => {
      s.jumps++;
      s.schedule.reset();
      s.counter.reset();
      s.lastReading = NaN;
      s.frameCalls = 0;
      s.renderer.forget();
    };
    s.onFullscreen = () => placeMeter(s);
    for (const event of ["emptied", "loadedmetadata", "seeking"]) video.addEventListener(event, s.onJump);
    document.addEventListener("fullscreenchange", s.onFullscreen);
    document.addEventListener("webkitfullscreenchange", s.onFullscreen);
    placeMeter(s);
    session = s;
    if (typeof video.requestVideoFrameCallback === "function") {
      s.frameCall = video.requestVideoFrameCallback((w, m) => onVideoFrame(s, w, m));
    }
    const loop = (now) => {
      if (session !== s) return;
      s.frame = requestAnimationFrame(loop);
      try {
        tick(s, now);
      } catch (error) {
        console.warn("[streamremaster] smooth video stopped:", error);
        stop(errorCode(error));
      }
    };
    s.frame = requestAnimationFrame(loop);
    return status();
  }

  function stop(error, detail) {
    if (error) lastError = error;
    if (detail) lastDetail = String(detail).slice(0, 300);
    const s = session;
    if (!s) return status();
    session = null;
    cancelAnimationFrame(s.frame);
    if (s.frameCall && typeof s.video.cancelVideoFrameCallback === "function") s.video.cancelVideoFrameCallback(s.frameCall);
    for (const event of ["emptied", "loadedmetadata", "seeking"]) s.video.removeEventListener(event, s.onJump);
    document.removeEventListener("fullscreenchange", s.onFullscreen);
    document.removeEventListener("webkitfullscreenchange", s.onFullscreen);
    s.meter.host.remove();
    showCanvas(s, false);
    s.canvas.remove();
    if (s.renderer) s.renderer.destroy();
    return status();
  }

  function setTarget(targetFps) {
    target = Number(targetFps) || 0;
    if (session) session.nextPaint = 0;
    return status();
  }

  // The resolution, the sharpening or the model changed in the popup.
  async function reconfigure() {
    const s = session;
    if (!s) return status();
    const options = await readOptions();
    if (session !== s) return status();
    s.options = options;
    placeMeter(s);
    build(s);
    s.layoutKey = "";
    return status();
  }

  function status() {
    const s = session;
    if (!s) return { running: false, state: "off", error: lastError, detail: lastDetail, target };
    const hz = sourceHz(s);
    const { plan, renderer } = s;
    return {
      running: true,
      state: hz ? "on" : "measuring",
      fps: s.paints.length,
      sourceHz: hz,
      target,
      error: null,
      delayMs: Math.round(s.schedule.delayMs * 10) / 10,
      gaps20: s.gaps20,
      gaps50: s.gaps50,
      jumps: s.jumps,
      stats: { ...renderer.stats },
      size: [plan.outputWidth, plan.outputHeight],
      input: [plan.width, plan.height],
      memory: FG.memoryBytes(plan),
      model: plan.model ? plan.model.name : null,
      modelReady: renderer.upscalerReady,
      interpolator: plan.interpolator ? plan.interpolator.name : null,
      interpolatorReady: renderer.motionReady,
    };
  }

  // onFrame(texture, media, session): called for every frame taken, for the test benches.
  const api = { start, stop, setTarget, reconfigure, status, onFrame: null, device: () => device };
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
