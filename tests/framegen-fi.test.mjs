// The interpolation model reader refuses anything malformed: a model comes from outside the extension.
import assert from 'node:assert/strict';
import { test } from 'node:test';

await import('../extension/shared/framegen-sr.js');
await import('../extension/shared/framegen-fi.js');
const { parseModel, buildShaders, buildPlan, weightCount, kindOf } = globalThis.STFramegenFI;

const SHAPE = { c1: 8, c2: 8, b1: 1, b2: 1, b3: 1, bu: 1 };

function file({ shape = SHAPE, format = 1, count, magic = 'FIM1' } = {}) {
  let header = JSON.stringify({ format, name: 'test', shape });
  header += ' '.repeat((4 - (header.length % 4)) % 4);
  const weights = new Float32Array(count ?? weightCount(shape)).fill(0.5);
  const out = new Uint8Array(8 + header.length + weights.byteLength);
  out.set(new TextEncoder().encode(magic), 0);
  new DataView(out.buffer).setUint32(4, header.length, true);
  out.set(new TextEncoder().encode(header), 8);
  out.set(new Uint8Array(weights.buffer), 8 + header.length);
  return out.buffer;
}

test('a well-formed file is read', () => {
  const model = parseModel(file());
  assert.equal(model.kind, 'fi');
  assert.deepEqual(model.shape, SHAPE);
  assert.equal(model.weights.length, weightCount(SHAPE));
});

test('the production shape has the weights tools/train/interp.py trains', () => {
  assert.equal(weightCount({ c1: 24, c2: 48, b1: 2, b2: 2, b3: 3, bu: 1 }), 48536);
});

test('the kind of a model file comes from its first bytes', () => {
  assert.equal(kindOf(file()), 'fi');
  assert.equal(kindOf(new TextEncoder().encode('SRM1xxxx').buffer), 'sr');
  assert.equal(kindOf(new ArrayBuffer(2)), null);
  assert.equal(kindOf('nope'), null);
});

for (const [name, options] of [
  ['magic', { magic: 'SRM1' }],
  ['format', { format: 2 }],
  ['missing shape', { shape: null, count: 10 }],
  ['channels not in fours', { shape: { ...SHAPE, c1: 6 }, count: 100 }],
  ['too many blocks', { shape: { ...SHAPE, b3: 99 }, count: 100 }],
  ['too few weights', { count: 10 }],
  ['too many weights', { count: weightCount(SHAPE) + 1 }],
]) {
  test(`refuses a bad ${name}`, () => assert.throws(() => parseModel(file(options)), /bad model/));
}

test('refuses weights that are not numbers', () => {
  const buffer = file();
  new DataView(buffer).setFloat32(buffer.byteLength - 4, Infinity, true);
  assert.throws(() => parseModel(buffer), /bad model/);
});

test('the plan uses every weight once and keeps the skip connections alive', () => {
  const code = buildShaders(parseModel(file({ shape: { c1: 24, c2: 48, b1: 2, b2: 2, b3: 3, bu: 1 } })));
  const plan = buildPlan(code);
  assert.equal(plan.length, 1 + 4 + 2 + 4 + 2 + 6 + 2 + 2 + 2 + 2 + 1);
  // a step never writes the buffer it reads
  for (const step of plan) {
    assert.notEqual(step.buffers[0], step.buffers[1]);
    if (step.buffers[4]) assert.notEqual(step.buffers[4], step.buffers[1]);
  }
  // the 1/4 and 1/8 results the way up adds back are not overwritten before they are used
  const skipOf = (shader) => plan.find((s) => s.shader === shader).buffers[4];
  for (const [pack, from] of [[code.pack8, code.unpack8], [code.pack4, code.unpack4]]) {
    const skip = skipOf(pack);
    const start = plan.findIndex((s) => s.shader === from);
    const end = plan.findIndex((s) => s.shader === pack);
    assert.equal(plan[start].buffers[0], skip);
    for (const step of plan.slice(start, end)) assert.notEqual(step.buffers[1], skip);
  }
  assert.equal(plan.at(-1).buffers[1], 'out');
});

test('the generated shaders hold only numbers from the file', () => {
  const code = buildShaders(parseModel(file()));
  assert.match(code.head, /mat4x4f\(5\.00000000e-1/);
  for (const text of [code.head, code.tail, code.down8, code.up4]) assert.doesNotMatch(text, /test/);
});
