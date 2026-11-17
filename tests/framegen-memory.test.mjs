// What the smooth video captures and paints for each resolution choice, and the graphics memory
// that takes, which Settings and the popup show.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

globalThis.navigator ??= { userAgent: 'node' };
await import('../extension/shared/framegen.js');
await import('../extension/shared/framegen-sr.js');
await import('../extension/shared/framegen-fi.js');
await import('../extension/shared/framegen-model.js');
const { planSizes, memoryBytes } = globalThis.STFramegen;

const file = readFileSync(new URL('../extension/shared/models/streamremaster.stmodel', import.meta.url));
const model = globalThis.STFramegenModel.parse(file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength));
const both = (resolution) => ({ resolution, model: model.sr, interpolator: model.fi });
const MB = 1024 * 1024;

test('the network only runs when the output is larger than the video', () => {
  const same = planSizes(1920, 1080, both('original'), 2160);
  assert.equal(same.model, null);
  assert.equal(same.interpolator, model.fi);
  assert.deepEqual([same.width % 16, same.height % 16], [0, 0]);
  assert.deepEqual([same.outputWidth, same.outputHeight], [1920, 1080]);
  // the picture itself is not stretched: only an edge band is added up to the multiple of 16
  assert.deepEqual([same.contentWidth, same.contentHeight], [1920, 1080]);
  const up = planSizes(1280, 720, both('2160'), 1440);
  assert.equal(up.model, model.sr);
  assert.deepEqual([up.outputWidth, up.outputHeight], [3840, 2160]);
  assert.equal(planSizes(1280, 720, both('display'), 1440).outputHeight, 1440);
});

test('the captured frames stop at 1080p when the network upscales', () => {
  const plan = planSizes(3840, 2160, both('2160'), 2160);
  assert.equal(plan.model, null); // the video is already 4K: nothing to upscale
  const big = planSizes(2560, 1440, both('2160'), 2160);
  assert.equal(big.height, 1088);
  assert.equal(big.model, model.sr);
});

test('graphics memory: StreamRemaster with a 1080p video, and upscaling it to 4K', () => {
  const hd = memoryBytes(planSizes(1920, 1080, both('original'), 2160));
  const uhd = memoryBytes(planSizes(1920, 1080, both('2160'), 2160));
  const plain = memoryBytes(planSizes(1920, 1080, { resolution: 'original' }, 2160));
  assert.ok(hd > 200 * MB && hd < 300 * MB, `${hd / MB} MB`);
  assert.ok(uhd > 900 * MB && uhd < 1100 * MB, `${uhd / MB} MB`);
  assert.ok(plain < hd, 'without a model it takes less');
});
