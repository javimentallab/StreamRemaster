// The model file reader refuses anything malformed: a model comes from outside the extension.
import assert from 'node:assert/strict';
import { test } from 'node:test';

await import('../extension/shared/framegen-sr.js');
const { parseModel, buildShaders, weightCount } = globalThis.STFramegenSR;

function file({ channels = 8, blocks = 2, hidden = 4, format = 1, scale = 2, count, magic = 'SRM1', pad = true, aligned } = {}) {
  let header = JSON.stringify({ format, name: 'test', scale, channels, blocks, hidden, ...(aligned === undefined ? {} : { aligned }) });
  if (pad) header += ' '.repeat((4 - (header.length % 4)) % 4);
  const weights = new Float32Array(count ?? weightCount(channels, blocks, format === 2)).fill(0.5);
  const out = new Uint8Array(8 + header.length + weights.byteLength);
  out.set(new TextEncoder().encode(magic), 0);
  new DataView(out.buffer).setUint32(4, header.length, true);
  out.set(new TextEncoder().encode(header), 8);
  out.set(new Uint8Array(weights.buffer), 8 + header.length);
  return out.buffer;
}

test('a well-formed file is read', () => {
  const model = parseModel(file());
  assert.equal(model.channels, 8);
  assert.equal(model.blocks, 2);
  assert.equal(model.weights.length, weightCount(8, 2));
});

test('the production shape has the expected number of weights', () => {
  assert.equal(weightCount(24, 4), 5356);
});

for (const [name, options] of [
  ['magic', { magic: 'XXXX' }],
  ['format', { format: 3 }],
  ['format 2 without aligned', { format: 2 }],
  ['aligned in format 1', { format: 1, aligned: true }],
  ['scale', { scale: 4 }],
  ['hidden state', { hidden: 8 }],
  ['channels not in fours', { channels: 6, count: 100 }],
  ['too many blocks', { blocks: 99, count: 100 }],
  ['too few weights', { count: 10 }],
  ['too many weights', { count: weightCount(8, 2) + 1 }],
]) {
  test(`refuses a bad ${name}`, () => assert.throws(() => parseModel(file(options)), /bad model/));
}

test('refuses weights that are not numbers', () => {
  const buffer = file();
  const view = new DataView(buffer);
  view.setFloat32(buffer.byteLength - 4, NaN, true);
  assert.throws(() => parseModel(buffer), /bad model/);
});

test('refuses something that is not a file at all', () => {
  assert.throws(() => parseModel(new ArrayBuffer(3)), /bad model/);
  assert.throws(() => parseModel('nope'), /bad model/);
});

test('the generated shaders hold only numbers from the file', () => {
  const shaders = buildShaders(parseModel(file()));
  assert.equal(shaders.depthwise.length, 2);
  assert.equal(shaders.mix.length, 2);
  assert.match(shaders.head, /mat4x4f\(5\.00000000e-1/);
  assert.match(shaders.tail, /tanh\(/);
});

test('format 2 is the aligned upscaler: its head reads 64 channels', () => {
  const model = parseModel(file({ format: 2, aligned: true }));
  assert.equal(model.aligned, true);
  assert.equal(model.weights.length, weightCount(8, 2, true));
  assert.equal(weightCount(8, 2, true) - weightCount(8, 2), (64 - 28) * 8);
  const shaders = buildShaders(model);
  assert.match(shaders.unpack, /var flow: texture_2d<f32>/);
  assert.match(shaders.unpack, /dst\[i \+ 15u\]/);
  assert.doesNotMatch(buildShaders(parseModel(file())).unpack, /flow/);
});
