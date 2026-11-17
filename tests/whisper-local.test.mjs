// Whisper on this computer: the parts that don't need a graphics card. The shaders are
// checked against PyTorch on a real card with tools/whisper-local/check.js.
import assert from 'node:assert/strict';
import { test } from 'node:test';

await import('../extension/shared/whisper-store.js');
await import('../extension/shared/whisper-gpu.js');
await import('../extension/shared/whisper-local.js');
const W = globalThis.Whisper;

test('half precision: exact values, rounding to even, overflow and tiny numbers', () => {
  assert.equal(W.toHalf(1), 0x3c00);
  assert.equal(W.toHalf(-2), 0xc000);
  assert.equal(W.toHalf(0), 0);
  assert.equal(W.toHalf(65504), 0x7bff);
  assert.equal(W.toHalf(1e6), 0x7c00);
  assert.equal(W.toHalf(-Infinity), 0xfc00);
  assert.ok((W.toHalf(NaN) & 0x7c00) === 0x7c00 && (W.toHalf(NaN) & 0x3ff) !== 0);
  assert.equal(W.toHalf(Math.pow(2, -24)), 1);            // smallest subnormal
  assert.equal(W.toHalf(Math.pow(2, -26)), 0);            // below half of it
  // 1 + 2^-11 is halfway between 1 and the next half: ties go to the even one (1)
  assert.equal(W.toHalf(1 + Math.pow(2, -11)), 0x3c00);
  assert.equal(W.toHalf(1 + 3 * Math.pow(2, -11)), 0x3c02);
  for (const x of [0.1, -3.14159, 1234.5, 6.1e-5, -7e-6, 0.999]) {
    const back = W.fromHalf(W.toHalf(x));
    assert.ok(Math.abs(back - x) <= Math.abs(x) * 1e-3 + 6e-8, `${x} -> ${back}`);
  }
});

function safetensors(tensors) {
  // tensors: [{ name, dtype, shape, values }]
  let offset = 0;
  const header = { __metadata__: { format: 'pt' } };
  const blobs = [];
  for (const t of tensors) {
    let bytes;
    if (t.dtype === 'F32') bytes = new Uint8Array(Float32Array.from(t.values).buffer);
    else bytes = new Uint8Array(Uint16Array.from(t.values.map((v) => W.toHalf(v))).buffer);
    header[t.name] = { dtype: t.dtype, shape: t.shape, data_offsets: [offset, offset + bytes.length] };
    blobs.push(bytes);
    offset += bytes.length;
  }
  const json = new TextEncoder().encode(JSON.stringify(header));
  const out = new Uint8Array(8 + json.length + offset);
  new DataView(out.buffer).setBigUint64(0, BigInt(json.length), true);
  out.set(json, 8);
  let at = 8 + json.length;
  for (const b of blobs) { out.set(b, at); at += b.length; }
  return out;
}

test('safetensors read in pieces of any size: every tensor in half precision, names normalised', async () => {
  const a = Array.from({ length: 37 }, (_, i) => i * 0.25 - 3);
  const b = Array.from({ length: 10 }, (_, i) => -i * 1.5);
  const file = safetensors([
    { name: 'encoder.conv1.bias', dtype: 'F32', shape: [37], values: a },
    { name: 'model.decoder.layer_norm.weight', dtype: 'F16', shape: [2, 5], values: b },
    { name: 'proj_out.weight', dtype: 'F32', shape: [3], values: [1, 2, 3] },
  ]);
  for (const step of [1, 3, 7, 64, file.length]) {
    const got = {};
    const done = {};
    const reader = new W.HalfReader({
      keep: W.keepTensor,
      onPart: (name, i, part) => { (got[name] = got[name] || [])[i] = Array.from(part); },
      onTensor: (name, shape, parts) => { done[name] = { shape, parts }; },
    });
    for (let i = 0; i < file.length; i += step) await reader.feed(file.subarray(i, i + step));
    assert.ok(reader.done, `step ${step}`);
    assert.deepEqual(Object.keys(done).sort(), ['model.decoder.layer_norm.weight', 'model.encoder.conv1.bias']);
    assert.deepEqual(done['model.decoder.layer_norm.weight'], { shape: [2, 5], parts: 1 });
    assert.deepEqual(got['model.encoder.conv1.bias'][0].map(W.fromHalf), a);
    assert.deepEqual(got['model.decoder.layer_norm.weight'][0].map(W.fromHalf), b);
  }
});

test('mel filters: Slaney shape, 80 and 128 bands', () => {
  for (const n of [80, 128]) {
    const f = W.melFilters(n);
    assert.equal(f.length, n * 201);
    assert.ok(f.every((v) => v >= 0));
    // every band covers some frequencies, the first ones start at the bottom
    for (let m = 0; m < n; m++) assert.ok(f.subarray(m * 201, (m + 1) * 201).some((v) => v > 0), `band ${m}`);
    assert.ok(f[1] > 0);
  }
});

test('log-mel of silence is the floor, a tone lights up its band', () => {
  const mel = new W.Mel(80);
  const silent = mel.clip(new Float32Array(16000));
  assert.ok(silent.every((v) => Math.abs(v - (-10 + 4) / 4) < 1e-6));
  const tone = new Float32Array(16000);
  for (let i = 0; i < tone.length; i++) tone[i] = 0.5 * Math.sin((2 * Math.PI * 1000 * i) / 16000);
  const m = mel.clip(tone);
  const frame = m.subarray(50 * 80, 51 * 80);
  let best = 0;
  for (let i = 1; i < 80; i++) if (frame[i] > frame[best]) best = i;
  // 1 kHz sits around band 26 of 80 (Slaney scale, 0-8 kHz)
  assert.ok(best >= 24 && best <= 28, `band ${best}`);
  // after the audio, the 30 s window is padding at the floor (max - 8)
  const after = m.subarray(200 * 80, 201 * 80);
  assert.ok(after.every((v) => Math.abs(v - after[0]) < 1e-6));
});

test('tokenizer: GPT-2 byte table, spaces and multi-byte characters', () => {
  // "Ġ" is the byte 0x20; "Ã©" are the two bytes of "é"
  const tok = new W.Tokenizer({ 'Hola': 0, 'Ġmundo': 1, 'Ã©': 2, 'Ġcaf': 3, '<|endoftext|>': 4 });
  assert.equal(tok.decode([0, 1]), 'Hola mundo');
  assert.equal(tok.decode([3, 2]), ' café');
});

const cfg = { eos_token_id: 50257, decoder_start_token_id: 50258, suppress_tokens: [] };
const gen = {
  no_timestamps_token_id: 50363, lang_to_id: { '<|en|>': 50259, '<|es|>': 50262 },
  task_to_id: { transcribe: 50359, translate: 50358 }, suppress_tokens: [1, 2], begin_suppress_tokens: [220, 50257],
  max_initial_timestamp_index: 50, is_multilingual: true,
};
const sp = W.specialTokens(cfg, gen);
const VOCAB = sp.tsBegin + 1501;
const logits = (hot, rest = -5) => { const l = new Float32Array(VOCAB).fill(rest); for (const [t, v] of Object.entries(hot)) l[t] = v; return l; };
const argmax = (a) => a.indexOf(Math.max(...a));

test('special tokens come from the model files', () => {
  assert.equal(sp.eot, 50257);
  assert.equal(sp.sot, 50258);
  assert.equal(sp.noSpeech, 50362);
  assert.equal(sp.tsBegin, 50364);
  assert.equal(sp.transcribe, 50359);
  assert.equal(sp.langs.es, 50262);
});

test('timestamp rules: start with one, at most 1 s in, pairs, never backwards', () => {
  // first token: text is not allowed, and neither is a timestamp past 1.00 s
  let lp = W.applyRules(logits({ 100: 9, [sp.tsBegin + 80]: 8, [sp.tsBegin + 10]: 1 }), [], sp);
  assert.equal(argmax(lp), sp.tsBegin + 10);
  // after "<|0.20|> text": text or a later timestamp; not an earlier one
  lp = W.applyRules(logits({ [sp.tsBegin + 5]: 9, [sp.tsBegin + 30]: 2, 300: 1 }), [sp.tsBegin + 10, 300], sp);
  assert.equal(argmax(lp), sp.tsBegin + 30);
  // after "<|0.20|> text <|0.60|>": no text (needs a timestamp or the end)
  lp = W.applyRules(logits({ 300: 9, [sp.tsBegin + 30]: 2 }), [sp.tsBegin + 10, 300, sp.tsBegin + 30], sp);
  assert.equal(argmax(lp), sp.tsBegin + 30);
  // after a pair: text, not a third timestamp
  lp = W.applyRules(logits({ [sp.tsBegin + 40]: 9, 300: 2 }), [sp.tsBegin + 10, 300, sp.tsBegin + 30, sp.tsBegin + 30], sp);
  assert.equal(argmax(lp), 300);
  // suppressed and special tokens never come out
  lp = W.applyRules(logits({ 1: 9, [sp.sot]: 9, [sp.noSpeech]: 9, 300: 1 }, -30), [sp.tsBegin, 400], sp);
  assert.equal(argmax(lp), 300);
  // many timestamps that are each unlikely still win together over the best text token
  lp = W.applyRules(logits({ 300: 1 }, -5), [sp.tsBegin, 400], sp);
  assert.ok(argmax(lp) > sp.tsBegin);
});

test('segments from tokens, with an unfinished last one', () => {
  const tok = { decode: (ids) => ids.map((i) => `w${i}`).join(' ') };
  const ts = (s) => sp.tsBegin + Math.round(s / 0.02);
  const seq = [ts(0), 10, 11, ts(2), ts(2), 12, ts(3.5), ts(3.5), 13];
  const segs = W.segmentsFrom(seq, sp, tok, 5);
  assert.deepEqual(segs.map((s) => [s.start, s.end, s.text, s.closed]), [
    [0, 2, 'w10 w11', true], [2, 3.5, 'w12', true], [3.5, 5, 'w13', false],
  ]);
});

test('loops are spotted, normal text is not', () => {
  assert.equal(W.isLooping([5, 6, 7, 5, 6, 7, 5, 6, 7, 5, 6, 7]), 3);
  assert.equal(W.isLooping([9, 9, 9, 9, 9, 9, 9, 9]), 1);
  assert.equal(W.isLooping([1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3]), 0);
  assert.equal(W.isLooping([9, 9, 9, 9]), 0);
});

test('made-up credits are dropped', () => {
  assert.ok(W.madeUp(' Subtítulos por la comunidad de Amara.org'));
  assert.ok(W.madeUp('Thanks for watching!'));
  assert.ok(!W.madeUp('Gracias por venir.'));
});

// A stand-in for the model: returns what `script` says for each pass.
function fakeStream(script) {
  let pass = 0;
  const calls = [];
  let stream = null;
  const tr = {
    async transcribe(mel, duration) {
      calls.push(duration);
      const out = script(pass++, duration, stream.bufStart / 16000);
      return Object.assign({ language: 'es', langProb: 0.99, silent: false, noSpeech: 0, avgLogprob: -0.2 }, out);
    },
  };
  const updates = [];
  const mel = new W.Mel(80);
  stream = new W.Stream(tr, mel, { language: null, task: 'transcribe', onSegments: (s) => updates.push(s), onLanguage: () => {} });
  return { stream, updates, calls };
}

async function feed(stream, seconds, loud = true) {
  for (let i = 0; i < seconds * 2; i++) {
    const chunk = new Float32Array(8000);
    if (loud) for (let j = 0; j < chunk.length; j++) chunk[j] = 0.1 * Math.sin(j / 3);
    stream.push(chunk);
    while (stream.busy) await new Promise((r) => setTimeout(r, 1));
  }
}

test('streaming: a sentence closes once another follows it, and leaves the window', async () => {
  const { stream, updates, calls } = fakeStream((n, d, from) => {
    if (from > 0) return { segments: [{ start: 0, end: d, text: 'Qué tal', closed: false }] };
    if (d < 3) return { segments: [{ start: 0, end: d, text: 'Hola', closed: false }] };
    return { segments: [{ start: 0, end: 1.5, text: 'Hola.', closed: true }, { start: 1.5, end: d, text: 'Qué tal', closed: false }] };
  });
  await feed(stream, 4);
  const last = updates[updates.length - 1];
  assert.deepEqual(last.map((s) => [s.text, s.completed]), [['Hola.', true], ['Qué tal', false]]);
  assert.equal(last[0].start, '0.000');
  assert.equal(last[0].end, '1.500');
  // the window now starts after "Hola."
  assert.equal(stream.bufStart, 1.5 * 16000);
  assert.ok(calls[calls.length - 1] < 4);
});

test('streaming: the last sentence closes when two passes agree', async () => {
  const { stream, updates } = fakeStream((n, d) => ({ segments: [{ start: 0, end: Math.min(d, 1.2), text: 'Vale.', closed: d >= 2 }] }));
  await feed(stream, 3.5);
  const done = updates[updates.length - 1].filter((s) => s.completed);
  assert.deepEqual(done.map((s) => s.text), ['Vale.']);
});

test('streaming: made-up times past the audio are dropped', async () => {
  const { stream, updates } = fakeStream((n, d) => ({ segments: [
    { start: 0, end: 0.8, text: 'Uno.', closed: true },
    { start: d + 2, end: d + 4, text: 'Inventado', closed: true },
  ] }));
  await feed(stream, 2.5);
  const texts = updates.flat().map((s) => s.text);
  assert.ok(texts.includes('Uno.'));
  assert.ok(!texts.includes('Inventado'));
});

test('streaming: silence is not transcribed, and does not pile up in the window', async () => {
  const { stream, calls } = fakeStream(() => ({ segments: [] }));
  await feed(stream, 6, false);
  assert.equal(calls.length, 0);
  assert.ok(stream.total - stream.bufStart <= 3.5 * 16000);
});
