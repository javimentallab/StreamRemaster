// The timing of the smooth video, with no graphics: frames come in as a browser hands them over
// and the schedule says what to paint on each refresh of the screen. What must hold is that the
// picture moves forward evenly, that every frame is taken once, and that it recovers by itself
// from pauses, jumps and frames that never came.
import assert from 'node:assert/strict';
import { test } from 'node:test';

globalThis.navigator ??= { userAgent: 'node' };
await import('../extension/shared/framegen.js');
const { Schedule, Timebase, Counter, Grid, Pacer, RING } = globalThis.STFramegen;

// A repeatable source of small random numbers.
function noise(seed) {
  let state = seed;
  return () => {
    state = (state * 1664525 + 1013904223) % 4294967296;
    return state / 4294967296;
  };
}

// Chromium: a refresh of the screen every 1000 / display ms; on each one the frame the video has
// come to is handed over once, with its timestamp, and then the canvas is painted.
// options.stall(ms) → true while the page is stuck (no refresh runs); options.leave(n) → true for
// a frame the card had no time for.
function playChromium({ fps, display = 144, seconds = 6, startMs = 5000, stall = () => false, leave = () => false, jitter = 0 }) {
  const schedule = new Schedule();
  const random = noise(7);
  const refresh = 1000 / display;
  const shown = [];   // media time painted on each refresh, or null
  const views = [];
  let handed = -1;
  let taken = 0;
  for (let tick = 0; tick * refresh < seconds * 1000; tick++) {
    const wall = startMs + tick * refresh;
    if (stall(wall - startMs)) continue;
    // the frame on screen by this refresh; with jitter the hand-over sometimes comes a refresh late
    const late = jitter && random() < jitter ? refresh : 0;
    const frame = Math.floor(((wall - startMs - late) / 1000) * fps);
    if (frame > handed) {
      handed = frame;
      const media = frame / fps;
      schedule.clock(media, wall);
      schedule.seen(media);
      if (!leave(frame)) {
        const { frame: record, previous, bridge } = schedule.take(media, wall);
        if (bridge) record.from = previous.media;
        taken++;
      }
    }
    const view = schedule.view(wall);
    views.push(view);
    shown.push(view ? view.a.media + view.t * (view.b.media - view.a.media) : null);
  }
  return { schedule, shown, views, taken, refresh };
}

// How much the painted media time advances from one refresh to the next, once it has started.
function steps(shown) {
  const first = shown.findIndex((value) => value !== null);
  const out = [];
  for (let i = first + 1; i < shown.length; i++) {
    if (shown[i] !== null && shown[i - 1] !== null) out.push(shown[i] - shown[i - 1]);
  }
  return out;
}

for (const fps of [60, 59.94, 30, 24, 50]) {
  test(`a ${fps} fps video on a 144 Hz screen moves forward evenly`, () => {
    const { shown, views, refresh, schedule } = playChromium({ fps });
    const settled = steps(shown.slice(288)); // the first two seconds settle the clock and the delay
    assert.ok(settled.length > 500);
    const expected = refresh / 1000;
    for (const step of settled) {
      assert.ok(Math.abs(step - expected) < expected * 0.25, `a refresh moved the picture ${step * 1000} ms, not ${refresh}`);
    }
    // never a frame held for want of the next one, and always with motion between the two
    for (const view of views.slice(288)) {
      assert.ok(view && view.a !== view.b, 'a frame was held');
      assert.ok(view.moving);
      assert.ok(view.t >= 0 && view.t < 1);
    }
    // it runs about one frame's time behind the video, not more than two
    assert.ok(schedule.delayMs > 1000 / fps * 0.9 && schedule.delayMs < 2000 / fps, `${schedule.delayMs} ms`);
  });
}

test('frames handed over a refresh late now and then do not hold the picture', () => {
  const { views } = playChromium({ fps: 60, jitter: 0.15, seconds: 12 });
  const held = views.slice(432).filter((view) => !view || view.a === view.b).length;
  assert.equal(held, 0);
});

test('a page stuck for 60 ms loses those frames and goes on through the gap with motion', () => {
  const { views, shown } = playChromium({ fps: 60, stall: (ms) => ms > 3000 && ms < 3060 });
  const after = views.slice(-200);
  for (const view of after) assert.ok(view && view.a !== view.b && view.moving);
  // some pair spans the frames that were never taken
  const widest = Math.max(...views.filter(Boolean).map((view) => view.b.media - view.a.media));
  assert.ok(widest > 2.5 / 60 && widest < 4.6 / 60, `${widest}`);
  // and the picture never goes back
  for (const step of steps(shown)) assert.ok(step >= -1e-9);
});

test('frames the card has no time for are bridged: the motion spans the gap', () => {
  const { views } = playChromium({ fps: 60, leave: (n) => n > 120 && n % 6 === 0 });
  const late = views.slice(-300);
  assert.ok(late.every((view) => view && view.moving && view.a !== view.b));
  assert.ok(late.some((view) => Math.abs(view.b.media - view.a.media - 2 / 60) < 1e-6));
});

test('two frames too far apart are not joined: the earlier one stays', () => {
  const schedule = new Schedule();
  let wall = 1000;
  const feed = (media) => {
    schedule.clock(media, wall);
    schedule.seen(media);
    const taken = schedule.take(media, wall);
    if (taken.bridge) taken.frame.from = taken.previous.media;
    return taken;
  };
  for (let n = 0; n < 30; n++) { feed(n / 60); wall += 1000 / 60; }
  // twelve frames never come, without the clock jumping (the card was behind)
  const media = 41 / 60;
  wall += 11000 / 60;
  schedule.seen(media);
  const { bridge } = schedule.take(media, wall);
  assert.equal(bridge, false);
  const view = schedule.view(wall);
  assert.ok(view === null || view.a === view.b);
});

test('a seek or a pause drops the frames in hand and starts again', () => {
  const schedule = new Schedule();
  let wall = 0;
  for (let n = 0; n < 60; n++) {
    schedule.clock(n / 60, wall);
    schedule.seen(n / 60);
    schedule.take(n / 60, wall);
    wall += 1000 / 60;
  }
  assert.equal(schedule.frames.length, RING);
  assert.equal(schedule.clock(100, wall), true);     // a seek far ahead
  assert.equal(schedule.frames.length, 0);
  assert.equal(schedule.view(wall), null);
  wall += 3000;                                       // paused for three seconds: same media time
  assert.equal(schedule.clock(100, wall), true);
  assert.equal(schedule.clock(100 + 1 / 60, wall + 1000 / 60), false);
});

test('a change of playback speed is a jump too, and the delay follows the speed', () => {
  const timebase = new Timebase();
  assert.equal(timebase.sample(10, 1000, 1), false);
  assert.equal(timebase.sample(10.5, 1500, 1), false);
  assert.equal(timebase.sample(10.6, 1550, 2), true);
  assert.ok(Math.abs(timebase.mediaAt(1650) - 10.8) < 1e-9);
});

test('the slots of the frames in hand are never given out twice', () => {
  const schedule = new Schedule();
  for (let n = 0; n < 50; n++) {
    schedule.seen(n / 60);
    schedule.take(n / 60, n * 16.7);
    const slots = schedule.frames.map((frame) => frame.slot);
    assert.equal(new Set(slots).size, slots.length);
    assert.ok(slots.every((slot) => slot >= 0 && slot < RING));
    assert.ok(schedule.frames.length <= RING);
  }
});

test('the delay grows at once when frames come late and is given back slowly', () => {
  const pacer = new Pacer();
  const period = 1 / 60;
  pacer.arrival(period, 0);
  const calm = pacer.update(period, 0);
  assert.ok(Math.abs(calm - (period + 0.004)) < 1e-9);
  pacer.arrival(period + 0.007, 100); // a frame 7 ms late
  let delay = pacer.update(period, 0.007);
  assert.ok(delay > calm && delay <= calm + 0.007);
  for (let i = 0; i < 20; i++) delay = pacer.update(period, 0.007);
  assert.ok(Math.abs(delay - (period + 0.011)) < 1e-6);
  pacer.arrival(period, 6000);     // the late one is forgotten after five seconds
  const back = pacer.update(period, 0.007);
  assert.ok(back < delay && delay - back < 0.001);
  // never more than two and a half frames
  pacer.arrival(1, 6100);
  for (let i = 0; i < 200; i++) delay = pacer.update(period, 0.007);
  assert.ok(Math.abs(delay - 2.5 * period) < 1e-9);
});

test('frames a second from the count of decoded frames', () => {
  const counter = new Counter();
  let hz = 0;
  for (let ms = 0; ms <= 3000; ms += 7) hz = counter.add(Math.floor((ms / 1000) * 59.94), ms);
  assert.ok(Math.abs(hz - 59.94) < 1.5, `${hz}`);
  // at double speed the browser decodes twice as many: still the video's own rate
  const fast = new Counter();
  for (let ms = 0; ms <= 3000; ms += 7) hz = fast.add(Math.floor((ms / 1000) * 120), ms, 2);
  assert.ok(Math.abs(hz - 60) < 1.5, `${hz}`);
  // a long silence (paused) starts the count again instead of reading low
  assert.equal(counter.add(1000, 60000), counter.hz);
  assert.equal(counter.readings.length, 1);
});

test('the grid of frames from a few timestamps and a rough rate', () => {
  const grid = new Grid();
  const period = 1001 / 60000; // 59.94
  // Gecko: a report every two or three frames, and the rough rate is a little off
  let n = 0;
  for (let i = 0; i < 60; i++) {
    grid.sample(n * period, 57.5);
    n += i % 2 ? 3 : 2;
  }
  assert.ok(Math.abs(grid.period - period) < 1e-9);
  const cell = grid.frameAt((n + 4.4) * period, 57.5);
  assert.ok(Math.abs(cell.start - (n - 3 + 4 + 3) * period) < 1e-6 || Math.abs(cell.start - (n + 4) * period) < 1e-6);
  // nothing reported yet: the rough rate alone
  assert.equal(new Grid().frameAt(1, 0), null);
  assert.ok(Math.abs(new Grid().frameAt(1.01, 50).period - 0.02) < 1e-12);
});

// Gecko: frames are taken on the refresh, by the clock the frame callbacks set (about 25 a second,
// each with the exact media time of a frame and the moment it is shown); the video itself swaps
// frames on its own, ahead of what that clock says by up to `lead` ms (as Firefox 160 does), never
// after it.
function playGeckoCallbacks({ fps, display = 144, seconds = 8, lead = 0 }) {
  const schedule = new Schedule();
  const counter = new Counter();
  const refresh = 1000 / display;
  const random = noise(3);
  const swaps = [];   // the moment frame n really shows, against the clock
  for (let n = 0; n < seconds * fps + 10; n++) swaps.push(2000 + (n / fps) * 1000 - 0.5 - random() * lead);
  const holding = (wall) => { let n = 0; while (n + 1 < swaps.length && swaps[n + 1] <= wall) n++; return n; };
  const taken = [];
  const views = [];
  let calledAt = -1;
  for (let tick = 0; tick * refresh < seconds * 1000; tick++) {
    const wall = 2000 + tick * refresh;
    const elapsed = (wall - 2000) / 1000;
    if (Math.floor(elapsed * 25) !== calledAt) {   // a frame callback
      calledAt = Math.floor(elapsed * 25);
      const n = Math.floor(elapsed * fps) + 1;      // it reports the frame about to be shown
      schedule.clock(n / fps, 2000 + (n / fps) * 1000);
      schedule.grid.sample(n / fps, counter.hz);
    }
    const rough = counter.add(holding(wall), wall);
    const media = schedule.due(wall, rough);
    if (media !== null) {
      schedule.seen(media);
      const { frame, previous, bridge } = schedule.take(media, wall);
      if (bridge) frame.from = previous.media;
      taken.push({ stamp: Math.round(media * fps), real: holding(wall) });
    }
    views.push(schedule.view(wall));
  }
  return { taken, views };
}

for (const [fps, display, lead] of [[60, 144, 6], [59.94, 144, 6], [30, 144, 16], [24, 144, 16], [60, 120, 5], [50, 144, 6], [30, 60, 16], [30, 45, 16]]) {
  test(`Gecko, ${fps} fps on ${display} Hz, frames swapped up to ${lead} ms early: each frame known for what it is`, () => {
    const { taken, views } = playGeckoCallbacks({ fps, display, lead });
    const settled = taken.slice(Math.round(fps * 2.5));
    for (const { stamp, real } of settled) assert.equal(real, stamp, `frame ${real} was taken as ${stamp}`);
    // with the screen at least twice as fast as the video, every frame is taken; slower, never two
    // in a row are left out
    const most = display >= 2 * fps ? 1 : 2;
    for (let i = 1; i < settled.length; i++) {
      const step = settled[i].real - settled[i - 1].real;
      assert.ok(step >= 1 && step <= most, `from ${settled[i - 1].real} to ${settled[i].real}`);
    }
    assert.ok(settled.length >= (fps * 4.4) / most, `${settled.length} frames taken`);
    assert.ok(views.slice(-300).every((view) => view && view.a !== view.b && view.moving), 'a frame was held');
  });
}

// Gecko before frame callbacks: the clock from currentTime readings.
function playGecko({ fps, display = 144, seconds = 8 }) {
  const schedule = new Schedule();
  const counter = new Counter();
  const refresh = 1000 / display;
  const taken = [];
  let lastReading = NaN;
  let lastReport = -1;
  const views = [];
  for (let tick = 0; tick * refresh < seconds * 1000; tick++) {
    const wall = 2000 + tick * refresh;
    const elapsed = (wall - 2000) / 1000;
    const onScreen = Math.floor(elapsed * fps);            // the frame the <video> holds right now
    // the clock moves in steps of 40 ms; a frame is reported about every 40 ms as well
    const reading = Math.floor(elapsed / 0.04) * 0.04;
    if (reading !== lastReading) {
      lastReading = reading;
      schedule.clock(reading, wall - (elapsed - reading) * 1000 + refresh * 0.5);
    }
    const report = Math.floor(elapsed / 0.04);
    if (report !== lastReport) {
      lastReport = report;
      schedule.grid.sample(onScreen / fps, counter.hz);
    }
    const rough = counter.add(onScreen, wall);
    const media = schedule.due(wall, rough);
    if (media !== null) {
      schedule.seen(media);
      const { frame, previous, bridge } = schedule.take(media, wall);
      if (bridge) frame.from = previous.media;
      taken.push({ stamp: media, real: onScreen });
    }
    views.push(schedule.view(wall));
  }
  return { taken, views, schedule };
}

for (const fps of [60, 59.94, 30]) {
  test(`Gecko, ${fps} fps: once the rate is known every frame is taken once`, () => {
    const { taken, views } = playGecko({ fps });
    const settled = taken.slice(Math.round(fps * 2.5));
    assert.ok(settled.length > fps * 3);
    for (let i = 1; i < settled.length; i++) {
      assert.equal(settled[i].real - settled[i - 1].real, 1, `frame ${settled[i - 1].real} was followed by ${settled[i].real}`);
    }
    const late = views.slice(-400);
    assert.ok(late.every((view) => view && view.a !== view.b && view.moving), 'a frame was held');
  });
}
