// Runs the extension's local Whisper engine under Deno (its WebGPU, on the Mint's 2060)
// and compares it with whisper_ref.py's numbers, then transcribes the whole clip the way
// the extension does (streaming, 0.5 s at a time) and prints the subtitles.
//
// Usage: deno run -A --unstable-webgpu check.js <extension shared dir> <model dir> <wav> <ref dir> [lang] [task]
const [shared, modelDir, wavPath, refDir, lang = "es", task = "transcribe"] = Deno.args;

globalThis.Engine = undefined;
for (const f of ["whisper-store.js", "whisper-gpu.js", "whisper-local.js"]) {
  // classic scripts: evaluate them in the global scope
  (0, eval)(await Deno.readTextFile(`${shared}/${f}`));
}
const W = globalThis.Whisper;

function readF32(path) {
  const b = Deno.readFileSync(path);
  return new Float32Array(b.buffer, b.byteOffset, b.byteLength / 4);
}

function readWav(path) {
  const b = Deno.readFileSync(path);
  const dv = new DataView(b.buffer, b.byteOffset, b.byteLength);
  let off = 12;
  while (off < b.length) {
    const id = String.fromCharCode(...b.subarray(off, off + 4));
    const size = dv.getUint32(off + 4, true);
    if (id === "data") {
      const n = size / 2;
      const out = new Float32Array(n);
      for (let i = 0; i < n; i++) out[i] = dv.getInt16(off + 8 + i * 2, true) / 32768;
      return out;
    }
    off += 8 + size + (size & 1);
  }
  throw new Error("no data chunk");
}

function compare(name, a, b) {
  let maxd = 0, maxv = 0, sum = 0;
  for (let i = 0; i < a.length; i++) {
    const d = Math.abs(a[i] - b[i]);
    if (d > maxd) maxd = d;
    if (Math.abs(b[i]) > maxv) maxv = Math.abs(b[i]);
    sum += d;
  }
  console.log(`${name}: max diff ${maxd.toExponential(3)} (max |ref| ${maxv.toFixed(3)}), mean diff ${(sum / a.length).toExponential(3)}`);
}

const cfg = JSON.parse(await Deno.readTextFile(`${modelDir}/config.json`));
const gen = JSON.parse(await Deno.readTextFile(`${modelDir}/generation_config.json`));
const vocab = JSON.parse(await Deno.readTextFile(`${modelDir}/vocab.json`));

// weights, streamed through the same converter the download uses
let t0 = performance.now();
const tensors = new Map();
const reader = new W.HalfReader({
  keep: W.keepTensor,
  onPart: (name, i, part) => { if (!tensors.has(name)) tensors.set(name, []); tensors.get(name)[i] = part; },
});
const file = await Deno.open(`${modelDir}/model.safetensors`);
for await (const chunk of file.readable) await reader.feed(chunk);
console.log(`converted ${tensors.size} tensors in ${((performance.now() - t0) / 1000).toFixed(1)} s, complete: ${reader.done}`);

t0 = performance.now();
const device = await W.requestDevice();
device.addEventListener && device.addEventListener("uncapturederror", (e) => console.error("GPU error:", e.error.message));
if (Deno.env.get("DEBUG_BUFFERS")) {
  const orig = device.createBuffer.bind(device);
  device.createBuffer = (desc) => {
    device.pushErrorScope("out-of-memory");
    device.pushErrorScope("validation");
    const b = orig(desc);
    device.popErrorScope().then((e) => e && console.error("validation", desc.size, desc.usage, e.message));
    device.popErrorScope().then((e) => e && console.error("oom", desc.size, desc.usage, e.message));
    return b;
  };
}
const gpu = await W.GpuModel.create(device, cfg, (name) => tensors.get(name));
console.log(`uploaded and built in ${((performance.now() - t0) / 1000).toFixed(1)} s`);

const audio = readWav(wavPath);
const melc = new W.Mel(cfg.num_mel_bins);
t0 = performance.now();
const mel = melc.clip(audio.subarray(0, 480000));
console.log(`mel in ${(performance.now() - t0).toFixed(0)} ms`);
compare("mel", mel, readF32(`${refDir}/mel.f32`));

t0 = performance.now();
await gpu.encode(mel);
await gpu.fence();
console.log(`encoder in ${(performance.now() - t0).toFixed(0)} ms`);
t0 = performance.now();
await gpu.encode(mel);
await gpu.fence();
console.log(`encoder again in ${(performance.now() - t0).toFixed(0)} ms`);
compare("encoder", await gpu.read(gpu.encOut, 1500 * cfg.d_model), readF32(`${refDir}/enc.f32`));

const info = JSON.parse(await Deno.readTextFile(`${refDir}/info.json`));
let logits = await gpu.step(info.prompt[0], 0);
compare("logits after SOT", logits, readF32(`${refDir}/logits_sot.f32`));
for (let i = 1; i < info.prompt.length; i++) logits = await gpu.step(info.prompt[i], i);
compare("logits after prompt", logits, readF32(`${refDir}/logits_prompt.f32`));
t0 = performance.now();
for (let i = 0; i < 20; i++) await gpu.step(220, 3 + i);
console.log(`decoder: ${((performance.now() - t0) / 20).toFixed(1)} ms per token`);

const tok = new W.Tokenizer(vocab);
const tr = new W.Transcriber(gpu, cfg, gen, tok);
t0 = performance.now();
const one = await tr.transcribe(mel, Math.min(30, audio.length / 16000), { language: lang === "auto" ? null : lang, task });
console.log(`one pass in ${(performance.now() - t0).toFixed(0)} ms, language ${one.language} (${one.langProb.toFixed(2)}), no speech ${one.noSpeech.toFixed(3)}, avg logprob ${one.avgLogprob.toFixed(3)}`);
one.segments.forEach((s) => console.log(`  [${s.start.toFixed(2)} - ${s.end.toFixed(2)}]${s.closed ? "" : " (open)"} ${s.text}`));
// the same pass with the rules applied here, one token at a time: must give the same text
tr.cpuRules = true;
t0 = performance.now();
const ref = await tr.transcribe(mel, Math.min(30, audio.length / 16000), { language: one.language, task });
tr.cpuRules = false;
const same = JSON.stringify(ref.segments) === JSON.stringify(one.segments);
console.log(`rules on the card ${same ? "match" : "DIFFER from"} the ones here (${(performance.now() - t0).toFixed(0)} ms one token at a time), avg logprob ${ref.avgLogprob.toFixed(3)}`);
if (!same) ref.segments.forEach((s) => console.log(`  here: [${s.start.toFixed(2)} - ${s.end.toFixed(2)}] ${s.text}`));

// streaming, as the extension does it, at real speed with no waiting
console.log("streaming:");
if (Deno.env.get("DEBUG_LANG")) {
  const orig = tr.transcribe.bind(tr);
  tr.transcribe = async (m, dur, o) => {
    const r = await orig(m, dur, o);
    console.log(`    pass ${dur.toFixed(1)} s: ${r.language} ${r.langProb.toFixed(2)} silent=${r.silent} ${r.segments.map((x) => x.text).join(" | ")}`);
    return r;
  };
}
let last = [];
let passes = 0;
const stream = new W.Stream(tr, melc, {
  language: lang === "auto" ? null : lang, task,
  onSegments: (segs) => { last = segs; passes++; },
  onLanguage: (l) => console.log("  language detected:", l),
  onError: (e) => console.error("  stream error", e),
});
t0 = performance.now();
for (let i = 0; i < audio.length; i += 8000) {
  stream.push(audio.subarray(i, Math.min(audio.length, i + 8000)));
  while (stream.busy) await new Promise((r) => setTimeout(r, 5));
}
stream.push(new Float32Array(16000 * 3));   // a little silence to close the last sentence
while (stream.busy) await new Promise((r) => setTimeout(r, 5));
console.log(`  ${passes} passes in ${((performance.now() - t0) / 1000).toFixed(1)} s for ${(audio.length / 16000).toFixed(1)} s of audio`);
last.forEach((s) => console.log(`  [${s.start} - ${s.end}] ${s.completed ? "" : "(open) "}${s.text}`));
Deno.exit(0);
