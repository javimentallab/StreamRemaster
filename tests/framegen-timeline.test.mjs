// The frame timeline: the fit of where source frames sit in media time, and what it does to the
// capture against the clock-only numbering it replaces.
import test from 'node:test';
import assert from 'node:assert/strict';

await import(new URL('../extension/shared/framegen.js', import.meta.url).href);
const { FrameTimeline } = globalThis.STFramegen;

const HZ = 60000 / 1001; // 59.94
const PHASE = 0.7;       // frames sit 0.7 of a frame past the whole-number grid
const START = 1234.5;    // a live stream's media time does not start at zero
const frameTime = (n) => (n + PHASE) / HZ;
const shownAt = (media) => Math.floor(media * HZ - PHASE); // the frame the video shows at a media time

function feed(timeline, from, to, every) {
  // every = null: every frame is reported (Chromium); else the frame shown every `every` seconds (Gecko)
  if (every === null) {
    for (let n = Math.ceil(from * HZ); frameTime(n) < to; n++) timeline.add(frameTime(n), 60);
  } else {
    for (let t = from; t < to; t += every) timeline.add(frameTime(shownAt(t)), 60);
  }
}

for (const [name, every] of [['every frame', null], ['about 25 a second', 0.04]]) {
  test(`fits rate and phase of a 59.94 stream from ${name}`, () => {
    const timeline = new FrameTimeline();
    feed(timeline, START, START + 3, every);
    assert.ok(Math.abs(timeline.hz - HZ) < 1e-4, `hz ${timeline.hz}`);
    // a frame's presentation time maps to a whole frame number
    const p = timeline.position(frameTime(shownAt(START + 2.5)), 60);
    assert.ok(Math.abs(p - Math.round(p)) < 0.01, `position ${p}`);
  });
}

test('falls back to the clock until there is a fit, and restarts on a seek', () => {
  const timeline = new FrameTimeline();
  assert.equal(timeline.position(10, 60), 600);
  feed(timeline, START, START + 2, null);
  assert.ok(timeline.hz > 0);
  timeline.add(frameTime(10), 60); // back to the start
  assert.equal(timeline.hz, 0);
  assert.equal(timeline.position(10, 60), 600);
});

// 60 seconds at 144 Hz with a little tick jitter: the source frame taken for each new index. A
// frame taken twice in a row, or one never taken, is a visible jerk.
function jerks(useTimeline) {
  const timeline = new FrameTimeline();
  let lastIndex = -Infinity, lastFrame = null, count = 0, seed = 1;
  const random = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let k = 0; k < 144 * 60; k++) {
    const media = START + k / 144 + (random() - 0.5) * 0.002;
    // the video reports a frame now and then (Gecko-like), the clock is exact
    if (useTimeline && k % 6 === 0) timeline.add(frameTime(shownAt(media)), 60);
    const index = useTimeline ? Math.floor(timeline.position(media, 60) - 0.25) : Math.floor(media * 60 + 0.002);
    if (index > lastIndex) {
      const frame = shownAt(media);
      if (lastFrame !== null && k > 144 * 2 && frame - lastFrame !== index - lastIndex) count++;
      lastIndex = index;
      lastFrame = frame;
    }
  }
  return count;
}

test('the clock-only numbering jerks on a 59.94 stream; the timeline does not', () => {
  assert.ok(jerks(false) > 0, 'expected the old numbering to jerk');
  assert.equal(jerks(true), 0);
});

// Seen on Twitch (17-nov): the rate meter read 57.75 for a 60 fps stream (the page was busy while
// it measured) and the fit, 3 % away from that, was thrown out for good: the capture then numbered
// frames at 57.75 a second and dropped one every ~0.4 s.
test('a fit on a common rate wins over a rate meter that read low', () => {
  for (const every of [null, 0.04]) {
    const timeline = new FrameTimeline();
    const at = (n) => (n + 0.3) / 60;
    if (every === null) {
      for (let n = Math.ceil(START * 60); at(n) < START + 3; n++) timeline.add(at(n), 57.75);
    } else {
      for (let t = START; t < START + 3; t += every) timeline.add(at(Math.floor(t * 60 - 0.3)), 57.75);
    }
    assert.ok(Math.abs(timeline.hz - 60) < 1e-3, `hz ${timeline.hz} (${every === null ? 'every frame' : 'Gecko-like'})`);
  }
});

test('a fit far from the measured rate and from any common rate is still refused', () => {
  const timeline = new FrameTimeline();
  const at = (n) => n / 27.3; // not a common rate
  for (let n = Math.ceil(START * 27.3); at(n) < START + 3; n++) timeline.add(at(n), 30);
  assert.equal(timeline.hz, 0);
});
