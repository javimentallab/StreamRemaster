// What the smooth video takes and paints for each resolution choice, and the graphics memory
// that takes, which Settings and the popup show.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

globalThis.navigator ??= { userAgent: 'node' };
await import('../extension/shared/framegen.js');
await import('../extension/shared/framegen-sr.js');
await import('../extension/shared/framegen-fi.js');
await import('../extension/shared/framegen-model.js');
const { planSizes, shownStep, memoryBytes } = globalThis.STFramegen;

const file = readFileSync(new URL('../extension/shared/models/streamremaster.stmodel', import.meta.url));
const model = globalThis.STFramegenModel.parse(file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength));
const both = (resolution) => ({ resolution, model: model.sr, interpolator: model.fi });
const MB = 1024 * 1024;

test('the upscaling network only runs when the output is taller than the video', () => {
  const same = planSizes(1920, 1080, both('original'), 2160);
  assert.equal(same.model, null);
  assert.equal(same.interpolator, model.fi);
  assert.deepEqual([same.width % 16, same.height % 16], [0, 0]);
  assert.deepEqual([same.outputWidth, same.outputHeight], [1920, 1080]);
  // the picture itself is not stretched: only an edge band is added up to the multiple of 16
  assert.deepEqual([same.contentWidth, same.contentHeight], [1920, 1080]);
  const up = planSizes(1280, 720, both('2160'), 2160);
  assert.equal(up.model, model.sr);
  assert.deepEqual([up.outputWidth, up.outputHeight], [3840, 2160]);
  assert.equal(planSizes(1280, 720, both('display'), 1440).outputHeight, 1440);
});

test('no choice goes past what the player can show', () => {
  // 4K chosen, the player takes 1080 pixels of the screen: a 1080p video is shown as it is
  const half = planSizes(1920, 1080, both('2160'), 1080);
  assert.deepEqual([half.outputWidth, half.outputHeight], [1920, 1080]);
  assert.equal(half.model, null);
  // a 4K video in that same player is taken at 1080p: the rest could not be seen
  const big = planSizes(3840, 2160, both('original'), 1080);
  assert.deepEqual([big.contentWidth, big.contentHeight], [1920, 1080]);
  assert.equal(big.outputHeight, 1080);
  // full screen on a 4K display: the 1080p video goes up to 4K
  const full = planSizes(1920, 1080, both('2160'), 2160);
  assert.equal(full.model, model.sr);
  assert.equal(full.outputHeight, 2160);
});

test('the frames stop at 1080p when the network upscales', () => {
  assert.equal(planSizes(3840, 2160, both('2160'), 2160).model, null); // already 4K: nothing to upscale
  const big = planSizes(2560, 1440, both('2160'), 2160);
  assert.equal(big.height, 1088);
  assert.equal(big.contentHeight, 1080);
  assert.equal(big.model, model.sr);
});

test('the height on screen goes in steps, not pixel by pixel', () => {
  assert.equal(shownStep(1248, 2160), 1080); // half a 4K screen
  assert.equal(shownStep(1300, 2160), 1440);
  assert.equal(shownStep(2160, 2160), 2160);
  assert.equal(shownStep(2100, 2160), 2160);
  assert.equal(shownStep(600, 2160), 720);
  assert.equal(shownStep(3000, 2160), 2160);
  assert.equal(shownStep(1000, 1080), 1080);
  assert.equal(shownStep(0, 1440), 1440);    // not laid out yet: the screen's
});

test('graphics memory: StreamRemaster with a 1080p video, and upscaling it to 4K', () => {
  const hd = memoryBytes(planSizes(1920, 1080, both('original'), 2160));
  const uhd = memoryBytes(planSizes(1920, 1080, both('2160'), 2160));
  const plain = memoryBytes(planSizes(1920, 1080, { resolution: 'original' }, 2160));
  assert.ok(hd > 150 * MB && hd < 300 * MB, `${hd / MB} MB`);
  assert.ok(uhd > 600 * MB && uhd < 1100 * MB, `${uhd / MB} MB`);
  assert.ok(plain < hd, 'without a model it takes less');
});
