// The worker path's clock, fed the way Chromium feeds it (measured on Twitch, 17-nov): frames are
// captured on the page's main thread and stamped with the moment of capture, a few milliseconds
// either side of their turn; while the page stalls the frames that come due are never captured, and
// the one on screen when it frees up arrives then, stamped then. The output must keep a pair of
// captured frames around every instant it paints, never go back, and not fall far behind.
import test from 'node:test';
import assert from 'node:assert/strict';

await import(new URL('../extension/shared/framegen.js', import.meta.url).href);
const { StreamTimer } = globalThis.STFramegen;

const START = 3456.25;  // seconds; capture clocks do not start at zero
const TRANSIT = 0.0003; // capture to worker, measured

function simulate({ hz = 60, seconds = 12, stall = 0.06, every = 0.45, jitter = 0.003 } = {}) {
  let seed = 7;
  const random = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const timer = new StreamTimer();
  const frames = [];
  let lastCapture = -Infinity;
  for (let n = 0; n < hz * seconds; n++) {
    const due = START + n / hz;
    let capture = due + (random() - 0.5) * 2 * jitter;
    if (stall) {
      const since = (due - START) % every;
      if (since < stall) {
        const next = START + (n + 1) / hz;
        const freed = due - since + stall;
        if (next < freed) continue; // replaced on screen before the page freed up: never captured
        capture = freed + random() * 0.001;
      }
    }
    if (capture <= lastCapture) capture = lastCapture + 0.0003;
    lastCapture = capture;
    frames.push({ n, ts: capture, arrival: capture + TRANSIT });
  }
  const captured = new Map(); // index -> source frame
  let lost = 0, misses = 0, ticks = 0, lastPos = -Infinity, backwards = 0, maxDelay = 0, misnumbered = 0;
  let next = 0, first = null;
  for (let k = 0; k < 144 * seconds; k++) {
    const now = START + k / 144;
    while (next < frames.length && frames[next].arrival <= now) {
      const f = frames[next++];
      const { index } = timer.frame(f.ts, f.arrival);
      if (index === null) continue;
      // a frame captured late may be numbered as the next one (it was on screen by then), never further
      if (first === null) first = index - f.n;
      if (Math.abs(index - f.n - first) > 1) misnumbered++;
      captured.set(index, f.n);
    }
    if (now < START + 3) continue; // warming up: rate, fit and the first stalls
    const p = timer.position(now);
    if (!Number.isFinite(p)) continue;
    ticks++;
    if (p < lastPos - 1e-9) backwards++;
    lastPos = p;
    let before = false, after = false;
    for (const i of captured.keys()) { if (i <= p) before = true; if (i > p && i <= p + 6) after = true; }
    if (!before || !after) misses++;
    maxDelay = Math.max(maxDelay, timer.delay);
  }
  lost = hz * seconds - frames.length;
  return { lost, misses, misnumbered, ticks, backwards, maxDelay, hz: timer.hz };
}

test('a quiet page: frames numbered as they come, every instant between two of them, little delay', () => {
  const r = simulate({ stall: 0 });
  assert.equal(r.lost, 0);
  assert.equal(r.misnumbered, 0);
  assert.equal(r.misses, 0, `${r.misses} of ${r.ticks}`);
  assert.equal(r.backwards, 0);
  assert.ok(r.maxDelay < 0.02, `delay ${r.maxDelay}`);
  assert.ok(Math.abs(r.hz - 60) < 0.05, `hz ${r.hz}`);
});

for (const hz of [60, 60000 / 1001, 30]) {
  test(`a page that stalls 60 ms every 0.45 s at ${hz.toFixed(2)} fps: painting goes on across the gaps`, () => {
    const r = simulate({ hz });
    assert.ok(r.lost > 0, 'the simulation should lose frames');
    assert.equal(r.misnumbered, 0, `${r.misnumbered} frames numbered wrong`);
    assert.equal(r.misses, 0, `${r.misses} of ${r.ticks} ticks without a frame on either side`);
    assert.equal(r.backwards, 0);
    assert.ok(r.maxDelay > 0.03 && r.maxDelay < 0.12, `delay ${r.maxDelay}`);
  });
}

test('a seek starts the numbering over and keeps the delay learnt', () => {
  const timer = new StreamTimer();
  for (let n = 0; n < 120; n++) timer.frame(START + n / 60 + (n % 27 === 0 ? 0.05 : 0), START + n / 60 + TRANSIT + (n % 27 === 0 ? 0.05 : 0));
  const delay = timer.delay;
  assert.ok(delay > 0.03, `delay ${delay}`);
  const { reset } = timer.frame(START + 500, START + 2.1);
  assert.equal(reset, true);
  assert.equal(timer.delay, delay);
});
