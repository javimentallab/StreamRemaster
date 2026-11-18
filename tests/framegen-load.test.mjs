// The load governor: lowers the smooth video's work when the graphics card takes too long over
// each frame, and raises it again, carefully, when the card has room.
import test from 'node:test';
import assert from 'node:assert/strict';

await import(new URL('../extension/shared/framegen.js', import.meta.url).href);
const { LoadGovernor } = globalThis.STFramegen;

const BUDGET = 10;

// Feeds one sample every 1/60 s for `seconds`, asking the governor four times a second.
// Returns the times (ms) at which it changed something.
function run(governor, from, seconds, ms, height = 2160) {
  const changes = [];
  let nextUpdate = from;
  for (let t = from; t < from + seconds * 1000; t += 1000 / 60) {
    governor.sample(typeof ms === 'function' ? ms(governor) : ms, t);
    if (t >= nextUpdate) {
      nextUpdate += 250;
      if (governor.update(t, BUDGET, height)) changes.push(Math.round(t));
    }
  }
  return changes;
}

test('a card that keeps up is left alone', () => {
  const governor = new LoadGovernor();
  assert.deepEqual(run(governor, 0, 60, 3), []);
  assert.equal(governor.cap, Infinity);
  assert.equal(governor.slow, false);
});

test('a card that is behind gets a smaller picture, step by step, then half the frames', () => {
  const governor = new LoadGovernor();
  const changes = run(governor, 0, 20, 15);
  assert.equal(governor.cap, 720);
  assert.equal(governor.slow, true);
  assert.equal(changes.length, 4); // 1440, 1080, 720, half the frames
  assert.ok(changes[0] < 1000, `first change at ${changes[0]} ms`);
  for (let i = 1; i < changes.length; i++) assert.ok(changes[i] - changes[i - 1] >= 1000, 'it waits for each change to settle');
});

test('all the frames come back sooner than a bigger picture', () => {
  const governor = new LoadGovernor();
  run(governor, 0, 8, 15, 1080); // 720 and half the frames
  assert.equal(governor.slow, true);
  run(governor, 8000, 30, 7, 1080); // under the budget, not far under
  assert.equal(governor.slow, false);
  assert.equal(governor.cap, 720);
});

test('skipped work counts as being behind', () => {
  const governor = new LoadGovernor();
  run(governor, 0, 0.6, Infinity);
  assert.ok(governor.cap < Infinity);
});

test('the steps start below the height the picture already has', () => {
  const governor = new LoadGovernor();
  run(governor, 0, 0.6, 15, 1080);
  assert.equal(governor.cap, 720);
  const small = new LoadGovernor();
  run(small, 0, 0.6, 15, 720);
  assert.equal(small.cap, Infinity);
  assert.equal(small.slow, true);
});

test('nothing changes without enough work to judge by (a paused video)', () => {
  const governor = new LoadGovernor();
  for (let t = 0; t < 5000; t += 250) {
    governor.sample(50, t);
    assert.equal(governor.update(t, BUDGET, 2160), false);
  }
});

test('with room again the work is raised a step at a time, after a calm while', () => {
  const governor = new LoadGovernor();
  run(governor, 0, 6, 15, 1440); // down to 720 and half the frames
  assert.equal(governor.cap, 720);
  assert.equal(governor.slow, true);
  const changes = run(governor, 6000, 120, 2, 1440);
  assert.equal(governor.slow, false);
  assert.equal(governor.cap, Infinity);
  assert.equal(changes.length, 3); // the frames, 1080, and the cap off (1440 is the picture's own)
  assert.ok(changes[0] - 6000 >= 20000, `first raise after ${changes[0] - 6000} ms`);
});

test('between busy and calm it stays where it is', () => {
  const governor = new LoadGovernor();
  run(governor, 0, 1, 15);
  const cap = governor.cap;
  assert.deepEqual(run(governor, 1000, 120, 6), []); // under the budget, not under 40 % of it
  assert.equal(governor.cap, cap);
});

test('a raise that had to be undone makes the next one wait twice as long', () => {
  const governor = new LoadGovernor();
  // the card only keeps up at 1080 or below
  const load = (g) => (g.cap <= 1080 ? 2 : 15);
  const changes = run(governor, 0, 400, load, 2160);
  assert.equal(governor.cap, 1080);
  const raises = [];
  for (let i = 1; i < changes.length; i++) if (changes[i] - changes[i - 1] > 5000) raises.push(changes[i] - changes[i - 1]);
  assert.ok(raises.length >= 3, `raises: ${raises}`);
  for (let i = 1; i < raises.length; i++) assert.ok(raises[i] > raises[i - 1] * 1.7, `waits: ${raises}`);
});
