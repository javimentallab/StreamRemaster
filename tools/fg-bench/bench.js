// Measures the capture and the pacing of framegen.js in a real browser, with no model involved.
//
// The clip carries its frame number as a grey level in the top-left corner (see run.ps1), so what
// is checked is which frames really reached the GPU, not what the time readings claim.
"use strict";

(async function () {
  const WIDTH = 1280;
  const HEIGHT = 720;
  const LEVELS = 26;
  const SETTLE_MS = 6000;
  const WARMUP_MS = 2500;
  const MEASURE_MS = 12000;
  const READBACKS = 32;
  const RUNS = [{ targetFps: 0 }, { targetFps: 144 }, { targetFps: 120 }, { targetFps: 90 }, { targetFps: 60 }];

  const logEl = document.getElementById("log");
  const log = (text) => { logEl.textContent = text; };
  const post = (body) => fetch("/result", { method: "POST", body: JSON.stringify(body) });
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const percentile = (sorted, p) => (sorted.length ? sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * p))] : 0);

  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");

  function sizeToDevicePixels() {
    const css = `${WIDTH / devicePixelRatio}px`;
    const cssH = `${HEIGHT / devicePixelRatio}px`;
    for (const el of [video, canvas]) { el.style.width = css; el.style.height = cssH; }
  }

  // Reads the corner of captured frames back, in capture order.
  class FrameProbe {
    constructor(device) {
      this.device = device;
      this.free = [];
      for (let i = 0; i < READBACKS; i++) {
        this.free.push(device.createBuffer({ size: 256, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ }));
      }
      this.pending = 0;
      this.seq = 0;
      this.results = [];
      this.missed = 0;
    }

    clear() { this.seq = 0; this.results = []; this.missed = 0; }

    read(texture, index) {
      const seq = this.seq++;
      const buffer = this.free.pop();
      if (!buffer) { this.missed++; return; }
      const encoder = this.device.createCommandEncoder();
      encoder.copyTextureToBuffer({ texture, origin: [16, 16] }, { buffer, bytesPerRow: 256 }, [1, 1]);
      this.device.queue.submit([encoder.finish()]);
      this.pending++;
      this.nudge();
      buffer.mapAsync(GPUMapMode.READ).then(() => {
        const red = new Uint8Array(buffer.getMappedRange())[0];
        buffer.unmap();
        const luma = red / 1.164 + 16;
        this.results.push({ seq, index, level: ((Math.round((luma - 24) / 8) % LEVELS) + LEVELS) % LEVELS });
      }).catch(() => {}).finally(() => { this.pending--; this.free.push(buffer); });
    }

    // Firefox only resolves a mapping on its own slow GPU polls unless work keeps being submitted.
    nudge() {
      if (this.nudging) return;
      this.nudging = true;
      const again = () => {
        if (this.pending <= 0) { this.nudging = false; return; }
        this.device.queue.submit([]);
        setTimeout(again, 1);
      };
      setTimeout(again, 0);
    }

    summary(seconds) {
      const ordered = this.results.slice().sort((a, b) => a.seq - b.seq);
      let unique = 0;
      let duplicates = 0;
      let skipped = 0;
      const events = [];
      for (let i = 1; i < ordered.length; i++) {
        const before = ordered[i - 1];
        const current = ordered[i];
        if (current.seq !== before.seq + 1) continue; // a frame the probe could not read
        const gap = (current.level - before.level + LEVELS) % LEVELS;
        if (gap === 0) duplicates++;
        else { unique++; skipped += gap - 1; }
        if (gap !== 1 && events.length < 12) {
          events.push({ seq: current.seq, levels: [before.level, current.level], index: [before.index, current.index] });
        }
      }
      return { read: ordered.length, missedReads: this.missed, uniquePerS: +(unique / seconds).toFixed(2), duplicates, skipped, events };
    }
  }

  async function run(gen, probe, config, runNumber) {
    gen.targetFps = config.targetFps;
    gen.reset();
    const stats = gen.stats;
    const start = performance.now();
    let measuring = false;
    let measureStart = 0;
    let before = null;
    let last = 0;
    const intervals = [];
    const tickCosts = [];

    await new Promise((resolve) => {
      const loop = (now) => {
        const t0 = performance.now();
        gen.tick(now);
        const cost = performance.now() - t0;
        if (!measuring && now - start >= WARMUP_MS) {
          measuring = true;
          measureStart = now;
          before = { ...stats };
          probe.clear();
          last = 0;
        }
        if (measuring) {
          if (last) intervals.push(now - last);
          last = now;
          tickCosts.push(cost);
          if (now - measureStart >= MEASURE_MS) { resolve(); return; }
        }
        requestAnimationFrame(loop);
      };
      requestAnimationFrame(loop);
    });

    await sleep(300); // the last readbacks
    const seconds = MEASURE_MS / 1000;
    const sorted = intervals.slice().sort((a, b) => a - b);
    const costs = tickCosts.slice().sort((a, b) => a - b);
    const result = {
      run: runNumber,
      targetFps: config.targetFps,
      sourceHz: gen.rate.hz,
      rafPerS: +(intervals.length / seconds).toFixed(1),
      rafMs: { p50: +percentile(sorted, 0.5).toFixed(2), p95: +percentile(sorted, 0.95).toFixed(2), p99: +percentile(sorted, 0.99).toFixed(2), max: +(sorted[sorted.length - 1] || 0).toFixed(1) },
      gapsOver20ms: intervals.filter((x) => x > 20).length,
      gapsOver50ms: intervals.filter((x) => x > 50).length,
      presentsPerS: +((stats.presents - before.presents) / seconds).toFixed(1),
      capturesPerS: +((stats.captures - before.captures) / seconds).toFixed(1),
      holdsPerS: +((stats.holds - before.holds) / seconds).toFixed(1),
      tickCostMs: { p50: +percentile(costs, 0.5).toFixed(2), p99: +percentile(costs, 0.99).toFixed(2) },
      frames: probe.summary(seconds),
    };
    log(JSON.stringify(result, null, 1));
    await post(result);
  }

  try {
    sizeToDevicePixels();
    window.addEventListener("resize", sizeToDevicePixels);
    await video.play();
    log("waiting for the window to be placed");
    await sleep(SETTLE_MS);
    sizeToDevicePixels();

    const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
    const device = await adapter.requestDevice();
    const probe = new FrameProbe(device);
    const gen = new STFramegen.FrameGenerator({
      device, video, canvas, width: WIDTH, height: HEIGHT,
      onCapture: (texture, index) => probe.read(texture, index),
    });
    await post({
      info: true,
      userAgent: navigator.userAgent,
      adapter: adapter.info && (adapter.info.description || adapter.info.vendor),
      screen: { x: window.screenX, y: window.screenY, w: screen.width, h: screen.height },
      devicePixelRatio,
    });

    for (let i = 0; i < RUNS.length; i++) {
      log(`run ${i + 1}/${RUNS.length}`);
      await run(gen, probe, RUNS[i], i + 1);
    }
    await post({ done: true });
    log("done");
  } catch (error) {
    await post({ error: String((error && error.stack) || error) });
    await post({ done: true });
    log(String(error));
  }
})();
