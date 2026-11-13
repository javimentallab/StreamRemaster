// The single model file of the smooth video tab: an upscaler and an interpolator together, or either alone.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

await import('../extension/shared/framegen-sr.js');
await import('../extension/shared/framegen-fi.js');
await import('../extension/shared/framegen-model.js');
const { parse, kindOf } = globalThis.STFramegenModel;
const FI = globalThis.STFramegenFI;
const SR = globalThis.STFramegenSR;

function framed(magic, header, payloads) {
  let text = JSON.stringify(header);
  text += ' '.repeat((4 - (text.length % 4)) % 4);
  const size = payloads.reduce((n, p) => n + p.byteLength, 0);
  const out = new Uint8Array(8 + text.length + size);
  out.set(new TextEncoder().encode(magic), 0);
  new DataView(out.buffer).setUint32(4, text.length, true);
  out.set(new TextEncoder().encode(text), 8);
  let at = 8 + text.length;
  for (const p of payloads) { out.set(new Uint8Array(p), at); at += p.byteLength; }
  return out.buffer;
}

const fiShape = { c1: 8, c2: 8, b1: 1, b2: 1, b3: 1, bu: 1 };
const fiFile = () => framed('FIM1', { format: 1, name: 'fi', shape: fiShape }, [new Float32Array(FI.weightCount(fiShape)).fill(0.1).buffer]);
const srFile = () => framed('SRM1', { format: 1, name: 'sr', scale: 2, channels: 8, blocks: 1, hidden: 4 },
  [new Float32Array(SR.weightCount(8, 1)).fill(0.1).buffer]);
const combined = (sr, fi, extra = {}) => framed('SFM1', { format: 1, name: 'both', sr: sr.byteLength, fi: fi.byteLength, ...extra }, [sr, fi]);

test('a combined file gives both parts', () => {
  const model = parse(combined(srFile(), fiFile()));
  assert.equal(model.kind, 'st');
  assert.equal(model.name, 'both');
  assert.equal(model.sr.channels, 8);
  assert.deepEqual(model.fi.shape, fiShape);
});

test('a lone .srmodel or .fimodel is a model with one part', () => {
  const sr = parse(srFile());
  assert.equal(sr.kind, 'sr');
  assert.equal(sr.fi, null);
  const fi = parse(fiFile());
  assert.equal(fi.kind, 'fi');
  assert.equal(fi.sr, null);
});

test('a combined file may leave a part out', () => {
  const model = parse(combined(new ArrayBuffer(0), fiFile()));
  assert.equal(model.sr, null);
  assert.ok(model.fi);
});

test('wrong lengths and broken parts are refused', () => {
  const sr = srFile();
  const fi = fiFile();
  assert.throws(() => parse(framed('SFM1', { format: 1, name: 'x', sr: sr.byteLength + 4, fi: fi.byteLength }, [sr, fi])));
  assert.throws(() => parse(framed('SFM1', { format: 1, name: 'x', sr: 0, fi: 0 }, [])));
  assert.throws(() => parse(framed('SFM1', { format: 2, name: 'x', sr: sr.byteLength, fi: fi.byteLength }, [sr, fi])));
  assert.throws(() => parse(combined(fi, sr)));
  assert.throws(() => parse(new TextEncoder().encode('XXXXxxxx').buffer));
});

test('the kind comes from the first bytes', () => {
  assert.equal(kindOf(combined(srFile(), fiFile())), 'st');
  assert.equal(kindOf(srFile()), 'sr');
  assert.equal(kindOf(fiFile()), 'fi');
  assert.equal(kindOf(new ArrayBuffer(2)), null);
});

test('the built-in model is a combined file with both parts', () => {
  const data = readFileSync(new URL('../extension/shared/models/streamremaster.stmodel', import.meta.url));
  const model = parse(data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength));
  assert.equal(model.kind, 'st');
  assert.ok(model.sr && model.fi);
});
