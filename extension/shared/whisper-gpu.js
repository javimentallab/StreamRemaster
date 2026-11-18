// Whisper on the graphics card, with WebGPU: our own shaders, no outside runtime.
//
// The weights stay in half precision (two per 32-bit word, read with unpack2x16float, so
// no "shader-f16" feature is needed) and the sums run in 32-bit floats. The encoder turns
// 30 s of log-mel frames into 1500 positions once per pass; the decoder then runs one
// token at a time against a key/value cache, and hands back the logits so the decoding
// rules (timestamps, suppressed tokens, language) can live in plain JavaScript.
//
// Tensors use the Hugging Face names (model.encoder.layers.0.self_attn.q_proj.weight...).
// Every Whisper size has 64-wide attention heads, which the attention shader relies on.
"use strict";

var Whisper = globalThis.Whisper || {};
globalThis.Whisper = Whisper;

(function () {
  const HEAD = 64;
  const N_AUDIO = 1500;      // encoder positions for 30 s
  const N_FRAMES = 3000;     // mel frames for 30 s

  const COMMON = /* wgsl */ `
fn erf_(x: f32) -> f32 {
  // Abramowitz and Stegun 7.1.26, error below 1.5e-7
  let a = abs(x);
  let t = 1.0 / (1.0 + 0.3275911 * a);
  let y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * exp(-a * a);
  return select(-y, y, x >= 0.0);
}
fn gelu(x: f32) -> f32 { return 0.5 * x * (1.0 + erf_(x * 0.7071067811865476)); }
fn half(buf_word: u32, odd: bool) -> f32 {
  let v = unpack2x16float(buf_word);
  return select(v.x, v.y, odd);
}
// The decoder's running state. The sampler (SAMPLE) writes it; the decoder reads token and pos.
struct Step { token: u32, pos: u32, count: u32, done: u32, last: u32, penult: u32, lastTs: i32, sumLp: f32 }
`;

  // Y[M,N] (=|+=) act(X[M,K] . W[N,K]^T + b). flags: 1 gelu, 2 add to Y, 4 bias.
  // 64x64 tile per workgroup, 16 values of k at a time; each thread keeps 4x4 sums in four
  // vec4 registers (an array indexed in a loop can end up in slow memory on some compilers).
  const MATMUL = COMMON + /* wgsl */ `
struct P { M: u32, N: u32, K: u32, flags: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> X: array<f32>;
@group(0) @binding(2) var<storage, read> W: array<u32>;
@group(0) @binding(3) var<storage, read> B: array<u32>;
@group(0) @binding(4) var<storage, read_write> Y: array<f32>;
var<workgroup> xs: array<f32, 1024>;
var<workgroup> ws: array<f32, 1024>;
fn store(m: u32, nx: u32, v: vec4f) {
  if (m >= p.M) { return; }
  for (var j = 0u; j < 4u; j++) {
    let n = nx + 16u * j;
    if (n >= p.N) { continue; }
    var x = v[j];
    if ((p.flags & 4u) != 0u) { x += half(B[n / 2u], (n & 1u) == 1u); }
    if ((p.flags & 1u) != 0u) { x = gelu(x); }
    let o = m * p.N + n;
    if ((p.flags & 2u) != 0u) { x += Y[o]; }
    Y[o] = x;
  }
}
@compute @workgroup_size(16, 16)
fn main(@builtin(workgroup_id) wg: vec3u, @builtin(local_invocation_id) l: vec3u,
        @builtin(local_invocation_index) tid: u32) {
  let m0 = wg.y * 64u;
  let n0 = wg.x * 64u;
  var c0 = vec4f(0.0);
  var c1 = vec4f(0.0);
  var c2 = vec4f(0.0);
  var c3 = vec4f(0.0);
  for (var k0 = 0u; k0 < p.K; k0 += 16u) {
    for (var i = 0u; i < 4u; i++) {
      let idx = tid + i * 256u;
      let r = idx / 16u;
      let c = idx % 16u;
      let gm = m0 + r;
      let gk = k0 + c;
      var v = 0.0;
      if (gm < p.M && gk < p.K) { v = X[gm * p.K + gk]; }
      xs[c * 64u + r] = v;
    }
    for (var i = 0u; i < 2u; i++) {
      let idx = tid + i * 256u;
      let r = idx / 8u;
      let c = (idx % 8u) * 2u;
      let gn = n0 + r;
      let gk = k0 + c;
      var v = vec2f(0.0);
      if (gn < p.N && gk < p.K) { v = unpack2x16float(W[(gn * p.K + gk) / 2u]); }
      ws[c * 64u + r] = v.x;
      ws[(c + 1u) * 64u + r] = v.y;
    }
    workgroupBarrier();
    for (var k = 0u; k < 16u; k++) {
      let base = k * 64u;
      let a = vec4f(xs[base + l.y], xs[base + l.y + 16u], xs[base + l.y + 32u], xs[base + l.y + 48u]);
      let b = vec4f(ws[base + l.x], ws[base + l.x + 16u], ws[base + l.x + 32u], ws[base + l.x + 48u]);
      c0 += a.x * b;
      c1 += a.y * b;
      c2 += a.z * b;
      c3 += a.w * b;
    }
    workgroupBarrier();
  }
  store(m0 + l.y, n0 + l.x, c0);
  store(m0 + l.y + 16u, n0 + l.x, c1);
  store(m0 + l.y + 32u, n0 + l.x, c2);
  store(m0 + l.y + 48u, n0 + l.x, c3);
}`;

  // One row: y[n] (=|+=) act(x . W[n] + b). One workgroup per output, for the decoder.
  // flags as MATMUL; the output goes to Y[n + ystep * step.pos] (writes the token's key or
  // value straight into its row of the cache).
  const GEMV = COMMON + /* wgsl */ `
struct P { N: u32, K: u32, flags: u32, ystep: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> X: array<f32>;
@group(0) @binding(2) var<storage, read> W: array<u32>;
@group(0) @binding(3) var<storage, read> B: array<u32>;
@group(0) @binding(4) var<storage, read_write> Y: array<f32>;
@group(0) @binding(5) var<storage, read> step: Step;
var<workgroup> red: array<f32, 64>;
@compute @workgroup_size(64)
fn main(@builtin(workgroup_id) wg: vec3u, @builtin(local_invocation_index) t: u32) {
  let n = wg.x + wg.y * 32768u;
  var s = 0.0;
  if (n < p.N) {
    let row = n * p.K / 2u;
    for (var k = t; k < p.K / 2u; k += 64u) {
      let w = unpack2x16float(W[row + k]);
      s += X[2u * k] * w.x + X[2u * k + 1u] * w.y;
    }
  }
  red[t] = s;
  workgroupBarrier();
  for (var w = 32u; w > 0u; w = w / 2u) {
    if (t < w) { red[t] += red[t + w]; }
    workgroupBarrier();
  }
  if (t == 0u && n < p.N) {
    var v = red[0];
    if ((p.flags & 4u) != 0u) { v += half(B[n / 2u], (n & 1u) == 1u); }
    if ((p.flags & 1u) != 0u) { v = gelu(v); }
    let o = n + p.ystep * step.pos;
    if ((p.flags & 2u) != 0u) { v += Y[o]; }
    Y[o] = v;
  }
}`;

  const LAYERNORM = COMMON + /* wgsl */ `
struct P { M: u32, N: u32, pad0: u32, pad1: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> X: array<f32>;
@group(0) @binding(2) var<storage, read> G: array<u32>;
@group(0) @binding(3) var<storage, read> Bb: array<u32>;
@group(0) @binding(4) var<storage, read_write> Y: array<f32>;
var<workgroup> red: array<f32, 256>;
@compute @workgroup_size(256)
fn main(@builtin(workgroup_id) wg: vec3u, @builtin(local_invocation_index) t: u32) {
  let base = wg.x * p.N;
  var s = 0.0;
  for (var i = t; i < p.N; i += 256u) { s += X[base + i]; }
  red[t] = s;
  workgroupBarrier();
  for (var w = 128u; w > 0u; w = w / 2u) {
    if (t < w) { red[t] += red[t + w]; }
    workgroupBarrier();
  }
  let mean = red[0] / f32(p.N);
  workgroupBarrier();
  var q = 0.0;
  for (var i = t; i < p.N; i += 256u) { let d = X[base + i] - mean; q += d * d; }
  red[t] = q;
  workgroupBarrier();
  for (var w = 128u; w > 0u; w = w / 2u) {
    if (t < w) { red[t] += red[t + w]; }
    workgroupBarrier();
  }
  let inv = inverseSqrt(red[0] / f32(p.N) + 1e-5);
  for (var i = t; i < p.N; i += 256u) {
    let g = half(G[i / 2u], (i & 1u) == 1u);
    let b = half(Bb[i / 2u], (i & 1u) == 1u);
    Y[base + i] = (X[base + i] - mean) * inv * g + b;
  }
}`;

  // Attention with 64-wide heads, softmax computed on the fly (keys in blocks of 32).
  // Workgroup = 8 queries x 1 head, one thread per channel of the head.
  // dyn = 1: the number of keys is step.pos + 1 (the decoder's own cache).
  const ATTENTION = COMMON + /* wgsl */ `
struct P { Mq: u32, Mk: u32, D: u32, dyn: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> Q: array<f32>;
@group(0) @binding(2) var<storage, read> K: array<f32>;
@group(0) @binding(3) var<storage, read> V: array<f32>;
@group(0) @binding(4) var<storage, read_write> O: array<f32>;
@group(0) @binding(5) var<storage, read> step: Step;
var<workgroup> qs: array<f32, 520>;
var<workgroup> kv: array<f32, 2080>;
var<workgroup> sc: array<f32, 256>;
var<workgroup> mrow: array<f32, 8>;
var<workgroup> lrow: array<f32, 8>;
var<workgroup> corr: array<f32, 8>;
@compute @workgroup_size(64)
fn main(@builtin(workgroup_id) wg: vec3u, @builtin(local_invocation_index) t: u32) {
  let q0 = wg.x * 8u;
  let col = wg.y * 64u + t;
  var mk = p.Mk;
  if (p.dyn == 1u) { mk = step.pos + 1u; }
  for (var i = 0u; i < 8u; i++) {
    var v = 0.0;
    if (q0 + i < p.Mq) { v = Q[(q0 + i) * p.D + col] * 0.125; }
    qs[i * 65u + t] = v;
  }
  if (t < 8u) { mrow[t] = -1e30; lrow[t] = 0.0; }
  var accA = vec4f(0.0);   // queries 0-3 of the block
  var accB = vec4f(0.0);   // queries 4-7
  workgroupBarrier();
  for (var j0 = 0u; j0 < mk; j0 += 32u) {
    for (var i = 0u; i < 32u; i++) {
      var v = 0.0;
      if (j0 + i < mk) { v = K[(j0 + i) * p.D + col]; }
      kv[i * 65u + t] = v;
    }
    workgroupBarrier();
    let qi = t / 8u;
    for (var c = 0u; c < 4u; c++) {
      let kk = (t % 8u) * 4u + c;
      var s = 0.0;
      for (var e = 0u; e < 64u; e++) { s += qs[qi * 65u + e] * kv[kk * 65u + e]; }
      if (j0 + kk >= mk) { s = -1e30; }
      sc[qi * 32u + kk] = s;
    }
    workgroupBarrier();
    if (t < 8u) {
      let mo = mrow[t];
      var mx = mo;
      for (var kk = 0u; kk < 32u; kk++) { mx = max(mx, sc[t * 32u + kk]); }
      var sum = 0.0;
      for (var kk = 0u; kk < 32u; kk++) {
        let e = exp(sc[t * 32u + kk] - mx);
        sc[t * 32u + kk] = e;
        sum += e;
      }
      let cf = exp(mo - mx);
      lrow[t] = lrow[t] * cf + sum;
      mrow[t] = mx;
      corr[t] = cf;
    }
    workgroupBarrier();
    for (var i = 0u; i < 32u; i++) {
      var v = 0.0;
      if (j0 + i < mk) { v = V[(j0 + i) * p.D + col]; }
      kv[i * 65u + t] = v;
    }
    workgroupBarrier();
    accA *= vec4f(corr[0], corr[1], corr[2], corr[3]);
    accB *= vec4f(corr[4], corr[5], corr[6], corr[7]);
    for (var kk = 0u; kk < 32u; kk++) {
      let v = kv[kk * 65u + t];
      accA += vec4f(sc[kk], sc[32u + kk], sc[64u + kk], sc[96u + kk]) * v;
      accB += vec4f(sc[128u + kk], sc[160u + kk], sc[192u + kk], sc[224u + kk]) * v;
    }
    workgroupBarrier();
  }
  let outA = accA / vec4f(lrow[0], lrow[1], lrow[2], lrow[3]);
  let outB = accB / vec4f(lrow[4], lrow[5], lrow[6], lrow[7]);
  for (var i = 0u; i < 4u; i++) {
    if (q0 + i < p.Mq) { O[(q0 + i) * p.D + col] = outA[i]; }
    if (q0 + 4u + i < p.Mq) { O[(q0 + 4u + i) * p.D + col] = outB[i]; }
  }
}`;

  // Columns for a 3-wide 1-D convolution with padding 1, as a matmul input:
  // out[t, c*3 + k] = in[t*stride + k - 1, c].
  const IM2COL = /* wgsl */ `
struct P { Tin: u32, C: u32, Tout: u32, stride: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> X: array<f32>;
@group(0) @binding(2) var<storage, read_write> Y: array<f32>;
@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) g: vec3u) {
  let i = g.x + g.y * 65535u * 256u;
  let row = 3u * p.C;
  if (i >= p.Tout * row) { return; }
  let t = i / row;
  let r = i % row;
  let c = r / 3u;
  let k = r % 3u;
  let src = i32(t * p.stride + k) - 1;
  var v = 0.0;
  if (src >= 0 && u32(src) < p.Tin) { v = X[u32(src) * p.C + c]; }
  Y[i] = v;
}`;

  // Y[i] += W[i] (half), for the encoder's position table.
  const ADDHALF = COMMON + /* wgsl */ `
struct P { count: u32, pad0: u32, pad1: u32, pad2: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> W: array<u32>;
@group(0) @binding(2) var<storage, read_write> Y: array<f32>;
@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) g: vec3u) {
  let i = g.x + g.y * 65535u * 256u;
  if (i >= p.count) { return; }
  Y[i] += half(W[i / 2u], (i & 1u) == 1u);
}`;

  // Decoder input: token embedding + position embedding, both from the step uniform.
  const EMBED = COMMON + /* wgsl */ `
struct P { D: u32, pad0: u32, pad1: u32, pad2: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> E: array<u32>;
@group(0) @binding(2) var<storage, read> Pos: array<u32>;
@group(0) @binding(3) var<storage, read_write> Y: array<f32>;
@group(0) @binding(4) var<storage, read> step: Step;
@compute @workgroup_size(256)
fn main(@builtin(global_invocation_id) g: vec3u) {
  let n = g.x;
  if (n >= p.D) { return; }
  let e = step.token * p.D + n;
  let q = step.pos * p.D + n;
  Y[n] = half(E[e / 2u], (e & 1u) == 1u) + half(Pos[q / 2u], (q & 1u) == 1u);
}`;

  // Picks the next token from the logits, with Whisper's rules (the same as Whisper.applyRules
  // in whisper-local.js): suppressed tokens, the first token a timestamp of at most 1 s,
  // timestamps in pairs and never backwards, and a timestamp whenever all of them together
  // are likelier than the best word. Appends it to the token list and moves the state on;
  // after the end token it only marks the state done. One workgroup of 256.
  const SAMPLE = /* wgsl */ `
struct Step { token: u32, pos: u32, count: u32, done: u32, last: u32, penult: u32, lastTs: i32, sumLp: f32 }
struct P { vocab: u32, eot: u32, tsBegin: u32, maxInit: u32 }
@group(0) @binding(0) var<uniform> p: P;
@group(0) @binding(1) var<storage, read> L: array<f32>;
@group(0) @binding(2) var<storage, read> mask: array<u32>;
@group(0) @binding(3) var<storage, read_write> st: Step;
@group(0) @binding(4) var<storage, read_write> toks: array<u32>;
var<workgroup> rm: array<f32, 256>;
var<workgroup> rs: array<f32, 256>;
var<workgroup> ri: array<u32, 256>;
var<workgroup> wdone: u32;
var<workgroup> wcount: u32;
var<workgroup> wlast: u32;
var<workgroup> wpenult: u32;
var<workgroup> wlastTs: i32;
var<workgroup> wforce: u32;
const NEG = -3.0e38;
fn allowed(t: u32) -> bool {
  if (((mask[t / 32u] >> (t % 32u)) & 1u) == 1u) { return false; }
  let isTs = t >= p.tsBegin;
  if (wcount == 0u) {
    if (!isTs || t > p.tsBegin + p.maxInit) { return false; }
  }
  let lastTs = wcount >= 1u && wlast >= p.tsBegin;
  let penultTs = wcount < 2u || wpenult >= p.tsBegin;
  if (lastTs) {
    if (penultTs) { if (isTs) { return false; } }
    else { if (t < p.eot) { return false; } }
  }
  if (wlastTs >= 0 && isTs) {
    var upTo = u32(wlastTs) + 1u;
    if (lastTs && !penultTs) { upTo = u32(wlastTs); }
    if (t < upTo) { return false; }
  }
  return true;
}
fn lse(m1: f32, s1: f32, m2: f32, s2: f32) -> vec2f {
  let m = max(m1, m2);
  if (m <= NEG) { return vec2f(NEG, 0.0); }
  return vec2f(m, s1 * exp(m1 - m) + s2 * exp(m2 - m));
}
@compute @workgroup_size(256)
fn main(@builtin(local_invocation_index) t: u32) {
  if (t == 0u) {
    wdone = st.done; wcount = st.count; wlast = st.last; wpenult = st.penult; wlastTs = st.lastTs;
  }
  let done = workgroupUniformLoad(&wdone);
  if (done == 1u) { return; }
  // 1: best word and all timestamps together (log-sum-exp)
  var textMax = NEG;
  var tm = NEG;
  var ts = 0.0;
  for (var i = t; i < p.vocab; i += 256u) {
    if (!allowed(i)) { continue; }
    let v = L[i];
    if (i < p.tsBegin) { textMax = max(textMax, v); }
    else { let c = lse(tm, ts, v, 1.0); tm = c.x; ts = c.y; }
  }
  rm[t] = tm; rs[t] = ts; ri[t] = bitcast<u32>(textMax);
  workgroupBarrier();
  for (var w = 128u; w > 0u; w = w / 2u) {
    if (t < w) {
      let c = lse(rm[t], rs[t], rm[t + w], rs[t + w]);
      rm[t] = c.x; rs[t] = c.y;
      ri[t] = bitcast<u32>(max(bitcast<f32>(ri[t]), bitcast<f32>(ri[t + w])));
    }
    workgroupBarrier();
  }
  if (t == 0u) {
    var force = 0u;
    if (rs[0] > 0.0 && rm[0] + log(rs[0]) > bitcast<f32>(ri[0])) { force = 1u; }
    wforce = force;
  }
  let force = workgroupUniformLoad(&wforce);
  // 2: the pick, and the log-sum-exp of what is left (for its log-probability)
  var best = NEG;
  var bi = 0xffffffffu;
  var am = NEG;
  var asum = 0.0;
  for (var i = t; i < p.vocab; i += 256u) {
    if (!allowed(i) || (force == 1u && i < p.tsBegin)) { continue; }
    let v = L[i];
    if (v > best) { best = v; bi = i; }
    let c = lse(am, asum, v, 1.0); am = c.x; asum = c.y;
  }
  rm[t] = am; rs[t] = asum; ri[t] = bi;
  workgroupBarrier();
  // the best token is found with a second reduction over (value, index)
  for (var w = 128u; w > 0u; w = w / 2u) {
    if (t < w) {
      let c = lse(rm[t], rs[t], rm[t + w], rs[t + w]);
      rm[t] = c.x; rs[t] = c.y;
      let a = ri[t];
      let b = ri[t + w];
      var pick = a;
      if (a == 0xffffffffu) { pick = b; }
      else if (b != 0xffffffffu) {
        let va = L[a];
        let vb = L[b];
        if (vb > va || (vb == va && b < a)) { pick = b; }
      }
      ri[t] = pick;
    }
    workgroupBarrier();
  }
  if (t == 0u) {
    let tok = ri[0];
    if (tok == 0xffffffffu || tok == p.eot) {
      st.done = 1u;
      return;
    }
    toks[st.count] = tok;
    st.count = st.count + 1u;
    st.penult = st.last;
    st.last = tok;
    if (tok >= p.tsBegin) { st.lastTs = i32(tok); }
    st.sumLp = st.sumLp + L[tok] - (rm[0] + log(rs[0]));
    st.token = tok;
    st.pos = st.pos + 1u;
  }
}`;

  const GPU_USAGE = { STORAGE: 0x80, UNIFORM: 0x40, COPY_DST: 0x08, COPY_SRC: 0x04, MAP_READ: 0x01 };

  // Ask for the biggest buffers the card allows: the token table of large-v3-turbo is 133 MB.
  Whisper.requestDevice = async function () {
    if (!globalThis.navigator || !navigator.gpu) throw Object.assign(new Error("no WebGPU"), { code: "no_webgpu" });
    const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
    if (!adapter) throw Object.assign(new Error("no WebGPU adapter"), { code: "no_webgpu" });
    const lim = adapter.limits;
    const requiredLimits = {};
    for (const k of ["maxStorageBufferBindingSize", "maxBufferSize"]) {
      if (typeof lim[k] === "number" && lim[k] > 0) requiredLimits[k] = Math.min(lim[k], 4294967292);
    }
    const device = await adapter.requestDevice({ requiredLimits });
    if (device.addEventListener) {
      device.addEventListener("uncapturederror", (e) => console.error("[streamremaster] GPU:", e.error && e.error.message));
    }
    return device;
  };

  // cfg: config.json; weights: { name: { shape, parts: [Uint16Array...] } } or a function
  // name -> parts (Uint16Array list) that may return a promise.
  Whisper.GpuModel = class {
    static async create(device, cfg, getParts, onProgress) {
      const m = new Whisper.GpuModel(device, cfg);
      try {
        await m.upload(getParts, onProgress);
        device.pushErrorScope("out-of-memory");
        device.pushErrorScope("validation");
        m.build();
        const bad = await device.popErrorScope();
        const oom = await device.popErrorScope();
        if (oom) throw Object.assign(new Error("working buffers: " + oom.message), { code: "local_vram" });
        if (bad) throw Object.assign(new Error("shaders: " + bad.message), { code: "local_failed" });
      } catch (e) {
        m.destroy();
        throw e;
      }
      return m;
    }

    constructor(device, cfg) {
      this.device = device;
      this.cfg = cfg;
      this.d = cfg.d_model;
      this.nMels = cfg.num_mel_bins;
      this.encLayers = cfg.encoder_layers;
      this.decLayers = cfg.decoder_layers;
      this.heads = this.d / HEAD;
      this.vocab = cfg.vocab_size;
      this.ffnEnc = cfg.encoder_ffn_dim;
      this.ffnDec = cfg.decoder_ffn_dim;
      this.maxPos = cfg.max_target_positions || 448;
      this.w = {};
      this.buffers = [];
      this.lost = false;
      // The browser can take the device away (the card reset, the GPU process restarted, another
      // page's work): the session then loads the model again on a new one.
      device.lost && device.lost.then((info) => { this.lost = true; this.lostReason = (info && info.message) || "device lost"; });
    }

    buffer(size, usage) {
      const b = this.device.createBuffer({ size: Math.max(16, Math.ceil(size / 4) * 4), usage });
      this.buffers.push(b);
      return b;
    }

    names() {
      const n = [];
      const enc = "model.encoder.", dec = "model.decoder.";
      n.push(enc + "conv1.weight", enc + "conv1.bias", enc + "conv2.weight", enc + "conv2.bias",
        enc + "embed_positions.weight", enc + "layer_norm.weight", enc + "layer_norm.bias",
        dec + "embed_tokens.weight", dec + "embed_positions.weight", dec + "layer_norm.weight", dec + "layer_norm.bias");
      const lin = (p) => [p + ".weight", p + ".bias"];
      for (let i = 0; i < this.encLayers; i++) {
        const p = enc + "layers." + i + ".";
        n.push(...lin(p + "self_attn.q_proj"), p + "self_attn.k_proj.weight", ...lin(p + "self_attn.v_proj"),
          ...lin(p + "self_attn.out_proj"), ...lin(p + "self_attn_layer_norm"), ...lin(p + "fc1"), ...lin(p + "fc2"),
          ...lin(p + "final_layer_norm"));
      }
      for (let i = 0; i < this.decLayers; i++) {
        const p = dec + "layers." + i + ".";
        n.push(...lin(p + "self_attn.q_proj"), p + "self_attn.k_proj.weight", ...lin(p + "self_attn.v_proj"),
          ...lin(p + "self_attn.out_proj"), ...lin(p + "self_attn_layer_norm"),
          ...lin(p + "encoder_attn.q_proj"), p + "encoder_attn.k_proj.weight", ...lin(p + "encoder_attn.v_proj"),
          ...lin(p + "encoder_attn.out_proj"), ...lin(p + "encoder_attn_layer_norm"),
          ...lin(p + "fc1"), ...lin(p + "fc2"), ...lin(p + "final_layer_norm"));
      }
      return n;
    }

    async upload(getParts, onProgress) {
      const names = this.names();
      const dev = this.device;
      const SLICE = 8 * 1024 * 1024;
      let pending = 0;
      await this.fence();   // creates the fence buffers before the big writes
      for (let i = 0; i < names.length; i++) {
        const parts = await getParts(names[i]);
        if (!parts) throw Object.assign(new Error("missing tensor " + names[i]), { code: "local_broken" });
        const bytes = parts.reduce((a, p) => a + p.byteLength, 0);
        // A card that is full says so here, as an error scope; without asking, the
        // buffer would just be unusable later on.
        dev.pushErrorScope("out-of-memory");
        dev.pushErrorScope("validation");
        const buf = this.buffer(bytes, GPU_USAGE.STORAGE | GPU_USAGE.COPY_DST);
        const bad = await dev.popErrorScope();
        const oom = await dev.popErrorScope();
        if (oom || bad) {
          const what = names[i] + " (" + bytes + " bytes): " + (oom || bad).message;
          throw Object.assign(new Error(what), { code: oom ? "local_vram" : "local_failed" });
        }
        // In slices, waiting for the card every 16 MB: Firefox hands each write to its GPU
        // process through shared memory, and a few big ones in a row run it out.
        let off = 0;
        for (const p of parts) {
          for (let at = 0; at < p.byteLength; at += SLICE) {
            const n = Math.min(SLICE, p.byteLength - at);
            dev.queue.writeBuffer(buf, off + at, p.buffer, p.byteOffset + at, n);
            pending += n;
            if (pending >= 2 * SLICE) { await this.fence(); pending = 0; }
          }
          off += p.byteLength;
        }
        this.w[names[i]] = buf;
        if (onProgress) onProgress((i + 1) / names.length);
      }
      await this.fence();
    }

    // Waits for the queue: a 4-byte copy read back (onSubmittedWorkDone hangs in some
    // runtimes, mapAsync works everywhere).
    async fence() {
      if (!this.fenceSrc) {
        this.fenceSrc = this.buffer(4, GPU_USAGE.STORAGE | GPU_USAGE.COPY_SRC);
        this.fenceDst = this.buffer(4, GPU_USAGE.MAP_READ | GPU_USAGE.COPY_DST);
      }
      const enc = this.device.createCommandEncoder();
      enc.copyBufferToBuffer(this.fenceSrc, 0, this.fenceDst, 0, 4);
      this.device.queue.submit([enc.finish()]);
      await this.fenceDst.mapAsync(1);
      this.fenceDst.unmap();
    }

    pipeline(code) {
      this.pipes = this.pipes || {};
      if (!this.pipes[code]) {
        const module = this.device.createShaderModule({ code });
        this.pipes[code] = this.device.createComputePipeline({ layout: "auto", compute: { module, entryPoint: "main" } });
      }
      return this.pipes[code];
    }

    uniform(values) {
      const b = this.buffer(16, GPU_USAGE.UNIFORM | GPU_USAGE.COPY_DST);
      this.device.queue.writeBuffer(b, 0, new Uint32Array(values));
      return b;
    }

    op(code, buffers, groups) {
      const pipe = this.pipeline(code);
      const bind = this.device.createBindGroup({
        layout: pipe.getBindGroupLayout(0),
        entries: buffers.map((b, i) => ({ binding: i, resource: { buffer: b } })),
      });
      return { pipe, bind, groups };
    }

    // Spreads a long 1-D dispatch over two dimensions (65,535 groups per dimension).
    flat(count, perGroup, rowSpan) {
      const groups = Math.ceil(count / perGroup);
      if (groups <= 65535) return [groups, 1, 1];
      return [rowSpan || 65535, Math.ceil(groups / (rowSpan || 65535)), 1];
    }

    matmul(X, W, B, Y, M, N, K, flags) {
      return this.op(MATMUL, [this.uniform([M, N, K, flags | (B ? 4 : 0)]), X, W, B || W, Y],
        [Math.ceil(N / 64), Math.ceil(M / 64), 1]);
    }

    gemv(X, W, B, Y, N, K, flags, ystep) {
      const groups = N <= 32768 ? [N, 1, 1] : [32768, Math.ceil(N / 32768), 1];
      return this.op(GEMV, [this.uniform([N, K, flags | (B ? 4 : 0), ystep || 0]), X, W, B || W, Y, this.stepBuf], groups);
    }

    layernorm(X, G, B, Y, M, N) {
      return this.op(LAYERNORM, [this.uniform([M, N, 0, 0]), X, G, B, Y], [M, 1, 1]);
    }

    attention(Q, K, V, O, Mq, Mk, dyn) {
      return this.op(ATTENTION, [this.uniform([Mq, Mk, this.d, dyn ? 1 : 0]), Q, K, V, O, this.stepBuf],
        [Math.ceil(Mq / 8), this.heads, 1]);
    }

    build() {
      const S = GPU_USAGE.STORAGE, CD = GPU_USAGE.COPY_DST, CS = GPU_USAGE.COPY_SRC;
      const d = this.d, w = this.w, f = 4;
      this.stepBuf = this.buffer(32, S | CD | CS);
      this.toks = this.buffer(this.maxPos * 4, S | CS);
      this.genRead = this.buffer(32 + this.maxPos * 4, GPU_USAGE.MAP_READ | CD);

      // ---- encoder
      const T = N_AUDIO;
      const mel = this.mel = this.buffer(N_FRAMES * this.nMels * f, S | CD);
      const col1 = this.buffer(N_FRAMES * 3 * this.nMels * f, S);
      const h1 = this.buffer(N_FRAMES * d * f, S);
      const col2 = this.buffer(T * 3 * d * f, S);
      const x = this.buffer(T * d * f, S | CS);
      const a = this.buffer(T * d * f, S);
      const q = this.buffer(T * d * f, S);
      const k = this.buffer(T * d * f, S);
      const v = this.buffer(T * d * f, S);
      const o = this.buffer(T * d * f, S);
      const hid = this.buffer(T * this.ffnEnc * f, S);
      this.encOut = this.buffer(T * d * f, S | CS);
      const E = "model.encoder.";
      const ops = [];
      ops.push(this.op(IM2COL, [this.uniform([N_FRAMES, this.nMels, N_FRAMES, 1]), mel, col1],
        this.flat(N_FRAMES * 3 * this.nMels, 256)));
      ops.push(this.matmul(col1, w[E + "conv1.weight"], w[E + "conv1.bias"], h1, N_FRAMES, d, 3 * this.nMels, 1));
      ops.push(this.op(IM2COL, [this.uniform([N_FRAMES, d, T, 2]), h1, col2], this.flat(T * 3 * d, 256)));
      ops.push(this.matmul(col2, w[E + "conv2.weight"], w[E + "conv2.bias"], x, T, d, 3 * d, 1));
      ops.push(this.op(ADDHALF, [this.uniform([T * d, 0, 0, 0]), w[E + "embed_positions.weight"], x], this.flat(T * d, 256)));
      for (let i = 0; i < this.encLayers; i++) {
        const p = E + "layers." + i + ".";
        ops.push(this.layernorm(x, w[p + "self_attn_layer_norm.weight"], w[p + "self_attn_layer_norm.bias"], a, T, d));
        ops.push(this.matmul(a, w[p + "self_attn.q_proj.weight"], w[p + "self_attn.q_proj.bias"], q, T, d, d, 0));
        ops.push(this.matmul(a, w[p + "self_attn.k_proj.weight"], null, k, T, d, d, 0));
        ops.push(this.matmul(a, w[p + "self_attn.v_proj.weight"], w[p + "self_attn.v_proj.bias"], v, T, d, d, 0));
        ops.push(this.attention(q, k, v, o, T, T, false));
        ops.push(this.matmul(o, w[p + "self_attn.out_proj.weight"], w[p + "self_attn.out_proj.bias"], x, T, d, d, 2));
        ops.push(this.layernorm(x, w[p + "final_layer_norm.weight"], w[p + "final_layer_norm.bias"], a, T, d));
        ops.push(this.matmul(a, w[p + "fc1.weight"], w[p + "fc1.bias"], hid, T, this.ffnEnc, d, 1));
        ops.push(this.matmul(hid, w[p + "fc2.weight"], w[p + "fc2.bias"], x, T, d, this.ffnEnc, 2));
      }
      ops.push(this.layernorm(x, w[E + "layer_norm.weight"], w[E + "layer_norm.bias"], this.encOut, T, d));
      // keys and values of every decoder layer's cross-attention, once per pass
      const D = "model.decoder.";
      this.crossK = [];
      this.crossV = [];
      for (let i = 0; i < this.decLayers; i++) {
        const p = D + "layers." + i + ".encoder_attn.";
        const ck = this.buffer(T * d * f, S), cv = this.buffer(T * d * f, S);
        ops.push(this.matmul(this.encOut, w[p + "k_proj.weight"], null, ck, T, d, d, 0));
        ops.push(this.matmul(this.encOut, w[p + "v_proj.weight"], w[p + "v_proj.bias"], cv, T, d, d, 0));
        this.crossK.push(ck);
        this.crossV.push(cv);
      }
      this.encOps = ops;

      // ---- decoder, one token
      const L = this.maxPos;
      const dx = this.buffer(d * f, S);
      const da = this.buffer(d * f, S);
      const dq = this.buffer(d * f, S);
      const dout = this.buffer(d * f, S);
      const dh = this.buffer(this.ffnDec * f, S);
      this.logits = this.buffer(this.vocab * f, S | CS);
      this.readback = this.buffer(this.vocab * f, GPU_USAGE.MAP_READ | CD);
      const dec = [];
      dec.push(this.op(EMBED, [this.uniform([d, 0, 0, 0]), w[D + "embed_tokens.weight"], w[D + "embed_positions.weight"], dx, this.stepBuf],
        [Math.ceil(d / 256), 1, 1]));
      this.selfK = [];
      this.selfV = [];
      for (let i = 0; i < this.decLayers; i++) {
        const p = D + "layers." + i + ".";
        const sk = this.buffer(L * d * f, S), sv = this.buffer(L * d * f, S);
        this.selfK.push(sk);
        this.selfV.push(sv);
        dec.push(this.layernorm(dx, w[p + "self_attn_layer_norm.weight"], w[p + "self_attn_layer_norm.bias"], da, 1, d));
        dec.push(this.gemv(da, w[p + "self_attn.q_proj.weight"], w[p + "self_attn.q_proj.bias"], dq, d, d, 0, 0));
        dec.push(this.gemv(da, w[p + "self_attn.k_proj.weight"], null, sk, d, d, 0, d));
        dec.push(this.gemv(da, w[p + "self_attn.v_proj.weight"], w[p + "self_attn.v_proj.bias"], sv, d, d, 0, d));
        dec.push(this.attention(dq, sk, sv, dout, 1, 0, true));
        dec.push(this.gemv(dout, w[p + "self_attn.out_proj.weight"], w[p + "self_attn.out_proj.bias"], dx, d, d, 2, 0));
        dec.push(this.layernorm(dx, w[p + "encoder_attn_layer_norm.weight"], w[p + "encoder_attn_layer_norm.bias"], da, 1, d));
        dec.push(this.gemv(da, w[p + "encoder_attn.q_proj.weight"], w[p + "encoder_attn.q_proj.bias"], dq, d, d, 0, 0));
        dec.push(this.attention(dq, this.crossK[i], this.crossV[i], dout, 1, T, false));
        dec.push(this.gemv(dout, w[p + "encoder_attn.out_proj.weight"], w[p + "encoder_attn.out_proj.bias"], dx, d, d, 2, 0));
        dec.push(this.layernorm(dx, w[p + "final_layer_norm.weight"], w[p + "final_layer_norm.bias"], da, 1, d));
        dec.push(this.gemv(da, w[p + "fc1.weight"], w[p + "fc1.bias"], dh, this.ffnDec, d, 1, 0));
        dec.push(this.gemv(dh, w[p + "fc2.weight"], w[p + "fc2.bias"], dx, d, this.ffnDec, 2, 0));
      }
      dec.push(this.layernorm(dx, w[D + "layer_norm.weight"], w[D + "layer_norm.bias"], da, 1, d));
      dec.push(this.gemv(da, w[D + "embed_tokens.weight"], null, this.logits, this.vocab, d, 0, 0));
      this.decOps = dec;
      this.maskBuf = this.buffer(Math.ceil(this.vocab / 32) * 4, S | CD);
    }

    run(ops, encoder) {
      const pass = encoder.beginComputePass();
      for (const o of ops) {
        pass.setPipeline(o.pipe);
        pass.setBindGroup(0, o.bind);
        pass.dispatchWorkgroups(o.groups[0], o.groups[1], o.groups[2]);
      }
      pass.end();
    }

    // mel: Float32Array [3000 * nMels], frame-major (frame 0's bins, then frame 1's...).
    // Only queued: whatever reads a result next waits for it.
    // In small submissions, about a layer each: the card cannot stop a command buffer halfway, so
    // one big one makes whatever else is drawing (smooth video on the same card) miss refreshes.
    // Between submissions the driver can run the other work.
    async encode(mel) {
      if (this.lost) throw Object.assign(new Error("device lost"), { code: "model_load" });
      this.device.queue.writeBuffer(this.mel, 0, mel.buffer, mel.byteOffset, mel.byteLength);
      const slice = Math.max(1, Math.ceil(this.encOps.length / (this.encLayers + 1)));
      for (let at = 0; at < this.encOps.length; at += slice) {
        const enc = this.device.createCommandEncoder();
        this.run(this.encOps.slice(at, at + slice), enc);
        this.device.queue.submit([enc.finish()]);
      }
    }

    setState(token, pos, fresh) {
      const b = new ArrayBuffer(32);
      const u = new Uint32Array(b);
      u[0] = token;
      u[1] = pos;
      if (fresh) new Int32Array(b)[6] = -1;   // count, done, last, penult, sumLp = 0; lastTs = -1
      this.device.queue.writeBuffer(this.stepBuf, 0, b, 0, fresh ? 32 : 8);
    }

    // The rules' fixed part: sp from Whisper.specialTokens. Call once per model.
    setRules(sp) {
      const words = new Uint32Array(Math.ceil(this.vocab / 32));
      const off = (t) => { if (t >= 0 && t < this.vocab) words[t >>> 5] |= 1 << (t & 31); };
      for (const t of sp.suppress) off(t);
      for (let t = sp.eot + 1; t < sp.tsBegin; t++) off(t);
      this.device.queue.writeBuffer(this.maskBuf, 0, words);
      this.sampleOp = this.op(SAMPLE, [this.uniform([this.vocab, sp.eot, sp.tsBegin, sp.maxInitialTs | 0]),
        this.logits, this.maskBuf, this.stepBuf, this.toks], [1, 1, 1]);
      this.rulesSet = true;
    }

    // Greedy decoding on the card: feeds `prompt` from position `pos`, then samples up to
    // maxTokens, reading back every `chunk` tokens. onChunk(tokens) may return true to stop
    // (a loop). Returns { tokens, sumLp }.
    async generate(prompt, pos, maxTokens, onChunk, chunk = 16) {
      if (this.lost) throw Object.assign(new Error("device lost"), { code: "model_load" });
      maxTokens = Math.min(maxTokens, this.maxPos - pos - prompt.length - 1);
      for (let i = 0; i < prompt.length; i++) {
        this.setState(prompt[i], pos + i, i === prompt.length - 1);
        const enc = this.device.createCommandEncoder();
        this.run(i === prompt.length - 1 ? this.decOps.concat([this.sampleOp]) : this.decOps, enc);
        this.device.queue.submit([enc.finish()]);
      }
      let count = 1;   // tokens asked for so far (the prompt's last step sampled one)
      for (;;) {
        const steps = Math.min(chunk, maxTokens - count);
        // one submission per token (see encode), and only the last one reads back
        for (let i = 0; i < steps - 1; i++) {
          const one = this.device.createCommandEncoder();
          this.run(this.decOps.concat([this.sampleOp]), one);
          this.device.queue.submit([one.finish()]);
        }
        const enc = this.device.createCommandEncoder();
        this.run(this.decOps.concat([this.sampleOp]), enc);
        count += steps;
        enc.copyBufferToBuffer(this.stepBuf, 0, this.genRead, 0, 32);
        enc.copyBufferToBuffer(this.toks, 0, this.genRead, 32, this.maxPos * 4);
        this.device.queue.submit([enc.finish()]);
        await this.genRead.mapAsync(1);
        const raw = this.genRead.getMappedRange().slice(0);
        this.genRead.unmap();
        const state = new Uint32Array(raw, 0, 8);
        const sumLp = new Float32Array(raw, 28, 1)[0];
        const tokens = Array.from(new Uint32Array(raw, 32, state[2]));
        const stop = onChunk && onChunk(tokens);
        if (state[3] === 1 || stop || count >= maxTokens) return { tokens, sumLp };
      }
    }

    // Feeds one token at position pos; returns the logits for the next one (a copy).
    async step(token, pos) {
      if (this.lost) throw Object.assign(new Error("device lost"), { code: "model_load" });
      if (pos >= this.maxPos) throw new Error("too many tokens");
      this.setState(token, pos, false);
      const enc = this.device.createCommandEncoder();
      this.run(this.decOps, enc);
      enc.copyBufferToBuffer(this.logits, 0, this.readback, 0, this.vocab * 4);
      this.device.queue.submit([enc.finish()]);
      await this.readback.mapAsync(1);
      const out = new Float32Array(this.readback.getMappedRange().slice(0));
      this.readback.unmap();
      return out;
    }

    // For checking against a reference: copies a GPU buffer back.
    async read(buffer, floats) {
      const tmp = this.device.createBuffer({ size: floats * 4, usage: GPU_USAGE.MAP_READ | GPU_USAGE.COPY_DST });
      const enc = this.device.createCommandEncoder();
      enc.copyBufferToBuffer(buffer, 0, tmp, 0, floats * 4);
      this.device.queue.submit([enc.finish()]);
      await tmp.mapAsync(1);
      const out = new Float32Array(tmp.getMappedRange().slice(0));
      tmp.unmap();
      tmp.destroy();
      return out;
    }

    destroy() {
      this.buffers.forEach((b) => { try { b.destroy(); } catch (e) { /* gone */ } });
      this.buffers = [];
      this.w = {};
    }
  };

  Whisper.N_FRAMES = N_FRAMES;
  Whisper.N_AUDIO = N_AUDIO;
})();
