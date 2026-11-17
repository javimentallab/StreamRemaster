// The smooth video on its own thread (Chromium). framegen-page.js builds a dedicated worker from the
// installers of framegen.js, framegen-sr.js and framegen-fi.js plus this function, hands it the
// canvas (as an OffscreenCanvas) and the video's frames (a MediaStreamTrackProcessor on
// video.captureStream()), and from then on the page's main thread only keeps the canvas over the
// video. Painting runs on the worker's own animation frames, so a page busy with its own scripts
// (Twitch stalls for 50-100 ms at a time) no longer holds the picture back; see StreamTimer in
// framegen.js for how frames that reach the worker late are still shown on time.
//
// Nothing here runs in the page: this file only defines the function the worker calls.
"use strict";

globalThis.STFramegenWorkerMain = function (self) {
  const { FrameGenerator, StreamTimer } = self.STFramegen;
  // With no frame for this long (paused, seeking, buffering) the real video shows through.
  const IDLE_MS = 250;
  const STATUS_EVERY_MS = 250;
  // Frames come in bursts after a stall: let the networks queue a little more work than on the main
  // thread before a frame goes without them.
  const MAX_IN_FLIGHT = 4;

  let device = null;
  let canvas = null;
  let gen = null;
  let target = 0;
  let reader = null;
  let stopped = false;
  let visible = false;
  let lastFrameAt = 0;
  let raf = 0;
  let statusTimer = 0;
  const paints = [];
  const timer = new StreamTimer();
  // for the status: the worker's own frames late by more than 20 ms, and source frames never captured
  let lastLoop = 0;
  let gaps20 = 0;
  let skipped = 0;
  let lastIndex = null;

  const post = (message) => self.postMessage(message);

  function errorCode(error) {
    if (error && typeof error.code === "string") return error.code;
    return error && error.name === "NotSupportedError" ? "no_webgpu" : "cannot_read";
  }

  function report(error) {
    if (stopped) return;
    console.warn("[streamremaster] smooth video worker:", error);
    post({ type: "error", code: errorCode(error), detail: String((error && error.message) || error).slice(0, 300) });
  }

  async function init(message) {
    canvas = message.canvas;
    target = Number(message.target) || 0;
    // The same graphics card as the page and the video decoder: a frame shared between two cards
    // can arrive with its colour corrupted (green).
    const adapter = self.navigator.gpu ? await self.navigator.gpu.requestAdapter({ powerPreference: "high-performance" }) : null;
    if (!adapter) throw Object.assign(new Error("no adapter"), { code: "no_webgpu" });
    device = await adapter.requestDevice({
      requiredLimits: {
        maxStorageBufferBindingSize: adapter.limits.maxStorageBufferBindingSize,
        maxBufferSize: adapter.limits.maxBufferSize,
      },
    });
    device.lost.then((info) => {
      if (!stopped) post({ type: "error", code: "no_webgpu", detail: `device lost: ${info.message}` });
    });
    build(message.plan);
    post({ type: "ready" });
    reader = message.readable.getReader();
    read(reader);
    raf = self.requestAnimationFrame(loop);
    statusTimer = self.setInterval(sendStatus, STATUS_EVERY_MS);
  }

  function build(plan) {
    if (gen) gen.destroy();
    gen = null;
    gen = new FrameGenerator({ device, canvas, ...plan, maxInFlight: MAX_IN_FLIGHT });
    gen.targetFps = target;
  }

  // Reads one track's frames until it ends. A track that was swapped for a new one (see "source")
  // just stops here without a word.
  async function read(own) {
    while (!stopped && own === reader) {
      let result;
      try {
        result = await own.read();
      } catch (error) {
        if (own === reader) report(error);
        return;
      }
      if (result.done) {
        if (!stopped && own === reader) post({ type: "ended" });
        return;
      }
      if (own !== reader) {
        result.value.close();
        return;
      }
      const frame = result.value;
      try {
        onFrame(frame);
      } catch (error) {
        report(error);
      } finally {
        // Closed right away: the copy into the ring is already submitted. Holding frames until the
        // graphics card was done (tried on 17-nov) starved the decoder and froze Twitch.
        frame.close();
      }
    }
  }

  function onFrame(frame) {
    const now = performance.now();
    lastFrameAt = now;
    const { index, reset } = timer.frame(frame.timestamp / 1e6, now / 1000);
    if (reset) {
      lastIndex = null;
      if (gen) gen.reset();
    }
    if (index === null || !gen) return;
    if (lastIndex !== null && index > lastIndex + 1) skipped += index - lastIndex - 1;
    lastIndex = index;
    gen.capture(index, frame);
  }

  function setVisible(value) {
    if (value === visible) return;
    visible = value;
    post({ type: "visible", visible });
  }

  function loop(now) {
    if (stopped) return;
    raf = self.requestAnimationFrame(loop);
    if (lastLoop && now - lastLoop > 20) gaps20++;
    lastLoop = now;
    while (paints.length && paints[0] <= now - 1000) paints.shift();
    if (!gen) return;
    if (now - lastFrameAt > IDLE_MS) {
      setVisible(false);
      return;
    }
    const position = timer.position(now / 1000);
    if (!Number.isFinite(position)) return;
    try {
      if (gen.present(position, now)) {
        paints.push(now);
        setVisible(true);
      }
    } catch (error) {
      report(error);
    }
  }

  function sendStatus() {
    if (stopped) return;
    post({
      type: "status",
      fps: paints.length,
      sourceHz: timer.hz,
      delayMs: Math.round(timer.delay * 1000),
      gaps20,
      skipped,
      stats: gen ? { ...gen.stats } : null,
      modelReady: !!(gen && gen.upscaler && gen.upscaler.ready),
      interpolatorReady: !!(gen && gen.interpolator && gen.interpolator.ready),
    });
  }

  function stop() {
    stopped = true;
    self.cancelAnimationFrame(raf);
    self.clearInterval(statusTimer);
    if (reader) reader.cancel().catch(() => {});
    if (gen) gen.destroy();
    gen = null;
    if (device) device.destroy();
    device = null;
  }

  self.onmessage = (event) => {
    const message = event.data || {};
    if (message.type === "init") {
      init(message).catch(report);
    } else if (message.type === "source") {
      // The video plays something else (an ad, another quality, a new stream): a new track's frames,
      // with the same device and the same compiled shaders. Only the numbering starts over.
      const old = reader;
      reader = message.readable.getReader();
      if (old) old.cancel().catch(() => {});
      timer.reset();
      lastIndex = null;
      if (gen) gen.reset();
      read(reader);
    } else if (message.type === "plan") {
      try {
        build(message.plan);
      } catch (error) {
        report(error);
      }
    } else if (message.type === "target") {
      target = Number(message.target) || 0;
      if (gen) {
        gen.targetFps = target;
        gen.nextPresentAt = 0;
      }
    } else if (message.type === "stop") {
      stop();
    }
  };
};
