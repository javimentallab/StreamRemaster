// The neural frame interpolator: once per pair of captured frames it estimates the motion both ways
// and an occlusion mask, at a quarter of the resolution, into two small textures. Every displayed
// frame then only needs the synthesis in framegen.js, which pulls both frames along that motion
// scaled to the instant being shown. The network is the one tools/train/interp.py trains.
//
// A model file is data only: "FIM1", the length of a JSON header, the header, then the weights as
// little-endian 32-bit floats. The shaders are generated here, from numbers, with the same building
// blocks as the upscaler (framegen-sr.js).
"use strict";

(function (root) {
  const MAGIC = 0x314d4946; // "FIM1"
  const IN_CHANNELS = 32;   // luma of both frames, unpacked 4x4
  const OUT_CHANNELS = 8;   // motion 0->1, motion 1->0, mask logit, spare
  const MAX_MODEL_BYTES = 8 * 1024 * 1024;
  // The network works on a quarter of the frame and goes down twice more.
  const ALIGN = 16;

  function bad(reason) {
    return Object.assign(new Error("bad model: " + reason), { code: "bad_model" });
  }

  // Sizes of every weight tensor, in file order: [weights, bias] pairs.
  function layout({ c1, c2, b1, b2, b3, bu }) {
    const conv = (i, o) => [i * o, o];
    const block = (c) => [9 * c, c, c * c, c];
    const blocks = (c, n) => Array.from({ length: n }, () => block(c)).flat();
    return [
      ...conv(IN_CHANNELS, c1), ...blocks(c1, b1),
      ...conv(4 * c1, c2), ...blocks(c2, b2),
      ...conv(4 * c2, c2), ...blocks(c2, b3),
      ...conv(c2, 4 * c2), ...blocks(c2, bu),
      ...conv(c2, 4 * c1), ...blocks(c1, bu),
      ...conv(c1, OUT_CHANNELS),
    ];
  }

  function weightCount(shape) {
    return layout(shape).reduce((a, b) => a + b, 0);
  }

  // The kind of model file, from its first four bytes: "sr", "fi" or null.
  function kindOf(buffer) {
    if (!(buffer instanceof ArrayBuffer) || buffer.byteLength < 4) return null;
    const magic = new DataView(buffer).getUint32(0, true);
    if (magic === MAGIC) return "fi";
    if (magic === 0x314d5253) return "sr";
    return null;
  }

  function parseModel(buffer) {
    if (!(buffer instanceof ArrayBuffer)) throw bad("not a buffer");
    if (buffer.byteLength < 8 || buffer.byteLength > MAX_MODEL_BYTES) throw bad("size");
    const view = new DataView(buffer);
    if (view.getUint32(0, true) !== MAGIC) throw bad("magic");
    const headerLength = view.getUint32(4, true);
    if (headerLength > buffer.byteLength - 8) throw bad("header length");
    let header;
    try {
      header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 8, headerLength)));
    } catch (e) {
      throw bad("header");
    }
    const { format, name, shape } = header || {};
    if (format !== 1 || !shape || typeof shape !== "object") throw bad("format");
    const clean = {};
    for (const key of ["c1", "c2"]) {
      const c = shape[key];
      if (!Number.isInteger(c) || c < 4 || c > 64 || c % 4) throw bad("channels");
      clean[key] = c;
    }
    for (const key of ["b1", "b2", "b3", "bu"]) {
      const n = shape[key];
      if (!Number.isInteger(n) || n < 0 || n > 8) throw bad("blocks");
      clean[key] = n;
    }
    const start = 8 + headerLength + ((4 - (headerLength % 4)) % 4);
    if (buffer.byteLength !== start + weightCount(clean) * 4) throw bad("weights length");
    const weights = new Float32Array(buffer.slice(start));
    for (const value of weights) if (!Number.isFinite(value)) throw bad("weights");
    return { kind: "fi", name: String(name || "model").slice(0, 80), shape: clean, weights };
  }

  const PARAMS = "struct P { w: u32, h: u32 }; @group(0) @binding(3) var<uniform> p: P;";
  const HEAD = "@compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {\n"
    + "  if (id.x >= p.w || id.y >= p.h) { return; }";

  // Luma of both frames, each 4x4 block of pixels as 16 channels (row after row), a first.
  function lumaShader() {
    return `${PARAMS}
    @group(0) @binding(0) var a: texture_2d<f32>;
    @group(0) @binding(2) var b: texture_2d<f32>;
    @group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;
    const Y = vec3f(0.299, 0.587, 0.114);
    ${HEAD}
      let o = (id.y * p.w + id.x) * 8u;
      let c = vec2i(id.xy) * 4;
      for (var r = 0; r < 4; r++) {
        var la: vec4f; var lb: vec4f;
        for (var x = 0; x < 4; x++) {
          la[x] = dot(textureLoad(a, c + vec2i(x, r), 0).rgb, Y);
          lb[x] = dot(textureLoad(b, c + vec2i(x, r), 0).rgb, Y);
        }
        dst[o + u32(r)] = la;
        dst[o + 4u + u32(r)] = lb;
      }
    }`;
  }

  // Half resolution, the four cells under each one after another. p is the half-resolution size.
  function unpackShader(channels) {
    const n = channels / 4;
    let copies = "";
    [[0, 0], [1, 0], [0, 1], [1, 1]].forEach(([dx, dy], k) => {
      for (let c = 0; c < n; c++) {
        copies += `  dst[b + ${k * n + c}u] = src[((id.y * 2u + ${dy}u) * p.w * 2u + id.x * 2u + ${dx}u) * ${n}u + ${c}u];\n`;
      }
    });
    return `@group(0) @binding(0) var<storage, read> src: array<vec4f>;
    @group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;
    ${PARAMS}
    ${HEAD}
      let b = (id.y * p.w + id.x) * ${4 * n}u;
${copies}}`;
  }

  // The reverse at twice the resolution, plus the skip connection. p is the full size.
  function packShader(channels) {
    const n = channels / 4;
    let copies = "";
    for (let c = 0; c < n; c++) copies += `  dst[o + ${c}u] = max(src[i + ${c}u] + res[o + ${c}u], vec4f(0.0));\n`;
    return `@group(0) @binding(0) var<storage, read> src: array<vec4f>;
    @group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;
    @group(0) @binding(4) var<storage, read> res: array<vec4f>;
    ${PARAMS}
    ${HEAD}
      let k = (id.y % 2u) * 2u + id.x % 2u;
      let i = ((id.y / 2u) * (p.w / 2u) + id.x / 2u) * ${4 * n}u + k * ${n}u;
      let o = (id.y * p.w + id.x) * ${n}u;
${copies}}`;
  }

  function textureShader() {
    return `${PARAMS}
    @group(0) @binding(0) var<storage, read> src: array<vec4f>;
    @group(0) @binding(1) var flow: texture_storage_2d<rgba16float, write>;
    @group(0) @binding(2) var extra: texture_storage_2d<rgba16float, write>;
    ${HEAD}
      let i = (id.y * p.w + id.x) * 2u;
      textureStore(flow, id.xy, src[i]);
      textureStore(extra, id.xy, src[i + 1u]);
    }`;
  }

  // Every shader of the network, in the order they run, with the level each one runs at.
  function buildShaders(model) {
    const { convolution, depthwise } = root.STFramegenSR;
    const { c1, c2, b1, b2, b3, bu } = model.shape;
    let at = 0;
    const take = (n) => { const part = model.weights.subarray(at, at + n); at += n; return part; };
    const relu = (expr) => `max(${expr}, vec4f(0.0))`;
    const plain = (expr) => expr;
    const conv = (i, o, finish) => convolution(take(i * o), take(o), i, o, finish);
    const blocks = (c, n) => Array.from({ length: n }, () => ({
      depthwise: depthwise(take(9 * c), take(c), c),
      mix: convolution(take(c * c), take(c), c, c, (expr, o) => relu(`${expr} + res[b + ${o}u]`),
        "@group(0) @binding(4) var<storage, read> res: array<vec4f>;"),
    }));
    const shaders = {
      luma: lumaShader(),
      head: conv(IN_CHANNELS, c1, relu), level4: blocks(c1, b1),
      unpack4: unpackShader(c1), down8: conv(4 * c1, c2, relu), level8: blocks(c2, b2),
      unpack8: unpackShader(c2), down16: conv(4 * c2, c2, relu), level16: blocks(c2, b3),
      up8: conv(c2, 4 * c2, plain), pack8: packShader(c2), after8: blocks(c2, bu),
      up4: conv(c2, 4 * c1, plain), pack4: packShader(c1), after4: blocks(c1, bu),
      tail: conv(c1, OUT_CHANNELS, plain),
      texture: textureShader(),
    };
    if (at !== model.weights.length) throw bad("weights left over");
    return shaders;
  }

  // The order the network's shaders run in, with the level (4, 8 or 16: the fraction of the frame)
  // and the buffers bound to each binding, by name. Buffers at 1/4: in4, q0-q2, qs (scratch), out;
  // at 1/8: u8, e0-e2, es; at 1/16: u16, s0, s1, ss. Binding 3 is always the level's size.
  function buildPlan(code) {
    const plan = [];
    const step = (shader, level, buffers) => plan.push({ shader, level, buffers });
    const levelBlocks = (list, level, cur, other, scratch) => {
      for (const block of list) {
        step(block.depthwise, level, { 0: cur, 1: scratch });
        step(block.mix, level, { 0: scratch, 1: other, 4: cur });
        [cur, other] = [other, cur];
      }
      return [cur, other];
    };
    step(code.head, 4, { 0: "in4", 1: "q0" });
    const [s4, q4] = levelBlocks(code.level4, 4, "q0", "q1", "qs");
    step(code.unpack4, 8, { 0: s4, 1: "u8" });
    step(code.down8, 8, { 0: "u8", 1: "e0" });
    const [s8, e8] = levelBlocks(code.level8, 8, "e0", "e1", "es");
    step(code.unpack8, 16, { 0: s8, 1: "u16" });
    step(code.down16, 16, { 0: "u16", 1: "s0" });
    const [s16] = levelBlocks(code.level16, 16, "s0", "s1", "ss");
    step(code.up8, 16, { 0: s16, 1: "u16" });
    step(code.pack8, 8, { 0: "u16", 1: "e2", 4: s8 });
    const [u8] = levelBlocks(code.after8, 8, "e2", e8, "es");
    step(code.up4, 8, { 0: u8, 1: "u8" });
    step(code.pack4, 4, { 0: "u8", 1: "q2", 4: s4 });
    const [u4] = levelBlocks(code.after4, 4, "q2", q4, "qs");
    step(code.tail, 4, { 0: u4, 1: "out" });
    return plan;
  }

  class Interpolator {
    // width and height: the captured frames, multiples of 16.
    constructor(device, model, width, height, slots) {
      if (width % ALIGN || height % ALIGN) throw new Error("frame size must be a multiple of 16");
      this.device = device;
      this.model = model;
      this.ready = false;
      this.w4 = width / 4;
      this.h4 = height / 4;
      const { c1, c2 } = model.shape;
      const n4 = this.w4 * this.h4;
      const n8 = n4 / 4;
      const n16 = n4 / 16;
      const usage = GPUBufferUsage.STORAGE;
      const buffer = (cells, channels) => device.createBuffer({ size: cells * channels * 4, usage });
      this.buffers = {
        in4: buffer(n4, IN_CHANNELS), q: [buffer(n4, c1), buffer(n4, c1), buffer(n4, c1)], qs: buffer(n4, c1),
        u8: buffer(n8, 4 * c1), e: [buffer(n8, c2), buffer(n8, c2), buffer(n8, c2)], es: buffer(n8, c2),
        u16: buffer(n16, 4 * c2), s: [buffer(n16, c2), buffer(n16, c2)], ss: buffer(n16, c2),
        out: buffer(n4, OUT_CHANNELS),
      };
      const param = (w, h) => {
        const b = device.createBuffer({ size: 16, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
        device.queue.writeBuffer(b, 0, new Uint32Array([w, h, 0, 0]));
        return b;
      };
      this.params = [param(this.w4, this.h4), param(this.w4 / 2, this.h4 / 2), param(this.w4 / 4, this.h4 / 4)];
      // One pair of motion textures per ring slot: the motion from the previous frame to that one.
      this.motion = [];
      for (let i = 0; i < slots; i++) {
        const make = () => device.createTexture({
          size: [this.w4, this.h4], format: "rgba16float",
          usage: GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.TEXTURE_BINDING,
        });
        const flow = make();
        const extra = make();
        this.motion.push({ flow, extra, flowView: flow.createView(), extraView: extra.createView() });
      }
      this.lumaGroups = new Map();
      this.compile().catch((e) => console.warn("[streamremaster] interpolator unavailable:", e));
    }

    async compile() {
      const code = buildShaders(this.model);
      const device = this.device;
      const make = (text) => device.createComputePipelineAsync({
        layout: "auto", compute: { module: device.createShaderModule({ code: text }), entryPoint: "main" },
      });
      const B = this.buffers;
      const byName = {
        in4: B.in4, q0: B.q[0], q1: B.q[1], q2: B.q[2], qs: B.qs, u8: B.u8, e0: B.e[0], e1: B.e[1], e2: B.e[2], es: B.es,
        u16: B.u16, s0: B.s[0], s1: B.s[1], ss: B.ss, out: B.out,
      };
      const [p4, p8, p16] = this.params;
      const [w4, h4] = [this.w4, this.h4];
      const sizes = { 4: [w4, h4, p4], 8: [w4 / 2, h4 / 2, p8], 16: [w4 / 4, h4 / 4, p16] };
      const plan = buildPlan(code);
      const pipelines = await Promise.all([make(code.luma), make(code.texture), ...plan.map((s) => make(s.shader))]);
      const [luma, texture, ...rest] = pipelines;
      this.luma = luma;
      this.texture = texture;
      this.steps = plan.map((s, i) => {
        const [w, h, param] = sizes[s.level];
        const entries = Object.entries({ ...s.buffers, 3: null }).map(([binding, name]) => ({
          binding: Number(binding), resource: { buffer: name ? byName[name] : param },
        }));
        return { pipeline: rest[i], group: device.createBindGroup({ layout: rest[i].getBindGroupLayout(0), entries }), w, h };
      });
      this.textureGroups = this.motion.map((m) => device.createBindGroup({
        layout: texture.getBindGroupLayout(0),
        entries: [
          { binding: 0, resource: { buffer: B.out } }, { binding: 1, resource: m.flowView },
          { binding: 2, resource: m.extraView }, { binding: 3, resource: { buffer: p4 } },
        ],
      }));
      this.ready = true;
    }

    lumaGroup(a, b) {
      const key = `${a.id}:${b.id}`;
      let group = this.lumaGroups.get(key);
      if (!group) {
        group = this.device.createBindGroup({
          layout: this.luma.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: a.view }, { binding: 2, resource: b.view },
            { binding: 1, resource: { buffer: this.buffers.in4 } }, { binding: 3, resource: { buffer: this.params[0] } },
          ],
        });
        this.lumaGroups.set(key, group);
      }
      return group;
    }

    // Records the network for frames a then b ({id, view}) into the encoder; the motion lands in
    // the textures of ring slot `slot`.
    run(encoder, a, b, slot) {
      const pass = encoder.beginComputePass();
      const dispatch = (pipeline, group, w, h) => {
        pass.setPipeline(pipeline);
        pass.setBindGroup(0, group);
        pass.dispatchWorkgroups(Math.ceil(w / 64), h);
      };
      dispatch(this.luma, this.lumaGroup(a, b), this.w4, this.h4);
      for (const s of this.steps) dispatch(s.pipeline, s.group, s.w, s.h);
      dispatch(this.texture, this.textureGroups[slot], this.w4, this.h4);
      pass.end();
    }

    motionOf(slot) {
      return this.motion[slot];
    }

    destroy() {
      const B = this.buffers;
      for (const b of [B.in4, ...B.q, B.qs, B.u8, ...B.e, B.es, B.u16, ...B.s, B.ss, B.out, ...this.params]) b.destroy();
      for (const m of this.motion) { m.flow.destroy(); m.extra.destroy(); }
      this.lumaGroups.clear();
      this.ready = false;
    }
  }

  root.STFramegenFI = { parseModel, buildShaders, buildPlan, weightCount, kindOf, Interpolator, ALIGN, MAX_MODEL_BYTES };
})(globalThis);
