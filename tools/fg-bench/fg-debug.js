// Test-only content script, added by youtube.py to its own copy of the build and never packaged.
// The page asks through data-st-fg-cmd and reads data-st-fg-status. It also compares each captured
// frame with the one before: a capture identical to its predecessor is a frame taken twice.
"use strict";

(function () {
  const root = document.documentElement;
  const page = globalThis.STFramegenPage;
  const REGION = { w: 128, h: 72 };
  const BYTES_PER_ROW = 512;
  const free = [];
  const results = new Map();
  let seq = 0;
  let nextToCompare = 0;
  let previous = null;
  let pending = 0;
  let nudging = false;
  const probe = { captures: 0, identical: 0, unread: 0 };

  // Where the stutter comes from: frames the capture stepped over, the video stalling or changing
  // speed or size, frames the browser itself dropped, and how well the frame timeline fits.
  const diag = { skipped: 0, skipEvents: 0, backwards: 0, waiting: 0, stalled: 0, rateChanges: 0, resizes: 0, rebuilds: 0 };
  const events = [];
  const note = (type, detail) => {
    events.push({ t: Math.round(performance.now()), type, detail });
    if (events.length > 300) events.shift();
  };
  let currentGen = null;
  const proto = globalThis.STFramegen.FrameGenerator.prototype;
  const tick = proto.tick;
  proto.tick = function (now) {
    if (currentGen !== this) { if (currentGen) { diag.rebuilds++; note("rebuild"); } currentGen = this; this.diagLast = -1; }
    return tick.call(this, now);
  };
  const capture = proto.capture;
  proto.capture = function (index) {
    if (this.diagLast >= 0) {
      if (index > this.diagLast + 1) {
        diag.skipped += index - this.diagLast - 1;
        diag.skipEvents++;
        note("skip", index - this.diagLast - 1);
      } else if (index <= this.diagLast) {
        diag.backwards++;
        note("backwards", this.diagLast - index);
      }
    }
    this.diagLast = index;
    return capture.call(this, index);
  };
  let watched = null;
  function watch() {
    const video = currentGen && currentGen.video;
    if (!video || video === watched) return;
    watched = video;
    video.addEventListener("waiting", () => { diag.waiting++; note("waiting"); });
    video.addEventListener("stalled", () => { diag.stalled++; note("stalled"); });
    video.addEventListener("ratechange", () => { diag.rateChanges++; note("rate", video.playbackRate); });
    video.addEventListener("resize", () => { diag.resizes++; note("resize", [video.videoWidth, video.videoHeight]); });
  }
  function timelineInfo() {
    const gen = currentGen;
    if (!gen) return null;
    const tl = gen.timeline;
    let rms = null;
    let worst = null;
    if (tl.hz && tl.samples.length) {
      let sum = 0;
      worst = 0;
      for (const [n, t] of tl.samples) {
        const off = (t - (tl.a + n / tl.hz)) * tl.hz; // in frames
        sum += off * off;
        worst = Math.max(worst, Math.abs(off));
      }
      rms = +Math.sqrt(sum / tl.samples.length).toFixed(3);
      worst = +worst.toFixed(3);
    }
    const video = gen.video;
    const quality = video.getVideoPlaybackQuality ? video.getVideoPlaybackQuality() : {};
    return {
      fitHz: tl.hz ? +tl.hz.toFixed(3) : 0, rateHz: gen.rate.hz, samples: tl.samples.length, residualRms: rms, residualMax: worst,
      playbackRate: video.playbackRate, size: [video.videoWidth, video.videoHeight],
      dropped: quality.droppedVideoFrames, decoded: quality.totalVideoFrames,
      buffered: video.buffered.length ? +(video.buffered.end(video.buffered.length - 1) - video.currentTime).toFixed(2) : 0,
    };
  }

  function compareInOrder() {
    while (results.has(nextToCompare)) {
      const data = results.get(nextToCompare);
      results.delete(nextToCompare);
      nextToCompare++;
      if (data === null) { previous = null; continue; }
      if (previous) {
        probe.captures++;
        let same = true;
        for (let i = 0; i < data.length; i += 4) {
          if (data[i] !== previous[i] || data[i + 1] !== previous[i + 1]) { same = false; break; }
        }
        if (same) probe.identical++;
      }
      previous = data;
    }
  }

  function nudge(device) {
    if (nudging) return;
    nudging = true;
    const again = () => {
      if (pending <= 0) { nudging = false; return; }
      device.queue.submit([]);
      setTimeout(again, 1);
    };
    setTimeout(again, 0);
  }

  page.onCapture = (texture) => {
    const device = page.device();
    const id = seq++;
    if (!free.length && pending < 24) {
      free.push(device.createBuffer({ size: BYTES_PER_ROW * REGION.h, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ }));
    }
    const buffer = free.pop();
    if (!buffer) { probe.unread++; results.set(id, null); compareInOrder(); return; }
    const origin = [Math.floor((texture.width - REGION.w) / 2), Math.floor((texture.height - REGION.h) / 2)];
    const encoder = device.createCommandEncoder();
    encoder.copyTextureToBuffer({ texture, origin }, { buffer, bytesPerRow: BYTES_PER_ROW }, [REGION.w, REGION.h]);
    device.queue.submit([encoder.finish()]);
    pending++;
    nudge(device);
    buffer.mapAsync(GPUMapMode.READ).then(() => {
      const copy = new Uint8Array(buffer.getMappedRange()).slice();
      buffer.unmap();
      free.push(buffer);
      results.set(id, copy);
    }).catch(() => { results.set(id, null); }).finally(() => { pending--; compareInOrder(); });
  };

  new MutationObserver(() => {
    const raw = root.getAttribute("data-st-fg-cmd");
    if (!raw) return;
    root.removeAttribute("data-st-fg-cmd");
    const command = JSON.parse(raw);
    if (command.cmd === "setup") {
      const models = {};
      if (command.model) models.test = { id: "test", kind: "sr", name: "test", size: 1, data: command.model };
      if (command.interp) models.testfi = { id: "testfi", kind: "fi", name: "test-fi", size: 1, data: command.interp };
      ext.storage.local.set({ fgModels: models })
        .then(() => ST.setSettings({
          fgResolution: command.resolution, fgModel: command.model ? "test" : "", fgInterpModel: command.interp ? "testfi" : "",
        }))
        .then(() => root.setAttribute("data-st-fg-setup", "done"));
    }
    if (command.cmd === "model") {
      ST.setSettings({ fgModel: command.id }).then(() => root.setAttribute("data-st-fg-setup", "model:" + command.id));
    }
    if (command.cmd === "start") page.start(command.target);
    if (command.cmd === "target") page.setTarget(command.target);
    if (command.cmd === "stop") page.stop();
  }).observe(root, { attributes: true, attributeFilter: ["data-st-fg-cmd"] });

  setInterval(() => {
    watch();
    root.setAttribute("data-st-fg-status", JSON.stringify(Object.assign(page.status(), { probe, diag, timeline: timelineInfo() })));
    root.setAttribute("data-st-fg-events", JSON.stringify(events));
  }, 250);
})();
