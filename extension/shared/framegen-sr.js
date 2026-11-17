// The neural upscaler (x2): reads a model file, writes its weights into WGSL as constants and runs it
// on the captured frames. Channels travel in groups of four and no weight is ever read from memory:
// measured on a GTX-class card that is ten times faster than looping over a weights buffer.
//
// A model file is data only: "SRM1", the length of a JSON header, the header, then the weights as
// little-endian 32-bit floats. The shaders are generated here, from numbers.
//
// Format 1 reads the current and the previous captured frame. Format 2 ("aligned") reads the current
// frame and the previous UPSCALED frame moved onto it with the interpolation network's motion, so the
// detail found in earlier frames carries on; without motion it gets the current frame enlarged.
"use strict";

(globalThis.STFramegenSRInstall = function (root) {
  const MAGIC = 0x314d5253; // "SRM1"
  const HIDDEN = 4;
  const INPUT_CHANNELS = 2 * 3 * 4 + HIDDEN; // current and previous frame unpacked, plus the state
  // current frame unpacked 2x2, the aligned previous upscaled frame unpacked 4x4, plus the state
  const ALIGNED_INPUT_CHANNELS = 3 * 4 + 3 * 16 + HIDDEN;
  const inputsOf = (aligned) => (aligned ? ALIGNED_INPUT_CHANNELS : INPUT_CHANNELS);
  const OUTPUT_CHANNELS = 3 * 16 + HIDDEN;   // RGB packed 4x4, plus the state
  const STATE_VECTOR = OUTPUT_CHANNELS / 4 - 1;
  const MAX_MODEL_BYTES = 8 * 1024 * 1024;

  function weightCount(channels, blocks, aligned = false) {
    return inputsOf(aligned) * channels + channels
      + blocks * (9 * channels + channels + channels * channels + channels)
      + channels * OUTPUT_CHANNELS + OUTPUT_CHANNELS;
  }

  function bad(reason) {
    return Object.assign(new Error("bad model: " + reason), { code: "bad_model" });
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
    const { format, scale, channels, blocks, hidden, name, aligned } = header || {};
    if ((format !== 1 && format !== 2) || scale !== 2 || hidden !== HIDDEN) throw bad("format");
    if ((format === 2) !== (aligned === true)) throw bad("format");
    if (!Number.isInteger(channels) || channels < 4 || channels > 64 || channels % 4) throw bad("channels");
    if (!Number.isInteger(blocks) || blocks < 1 || blocks > 16) throw bad("blocks");
    const start = 8 + headerLength + ((4 - (headerLength % 4)) % 4);
    const count = weightCount(channels, blocks, format === 2);
    if (buffer.byteLength !== start + count * 4) throw bad("weights length");
    const weights = new Float32Array(buffer.slice(start));
    for (const value of weights) if (!Number.isFinite(value)) throw bad("weights");
    return { name: String(name || "model").slice(0, 80), channels, blocks, weights, aligned: format === 2 };
  }

  // Compiled pipelines per device and shader text. The shaders depend only on the model, not on the
  // video's size, so when the video changes size (an ad, another quality) the upscaler is rebuilt
  // with the pipelines already compiled instead of going without the model for seconds.
  const compiled = new WeakMap();
  function cachedPipeline(device, text) {
    let cache = compiled.get(device);
    if (!cache) compiled.set(device, (cache = new Map()));
    let pipeline = cache.get(text);
    if (!pipeline) {
      pipeline = device.createComputePipelineAsync({
        layout: "auto", compute: { module: device.createShaderModule({ code: text }), entryPoint: "main" },
      });
      pipeline.catch(() => cache.delete(text));
      cache.set(text, pipeline);
    }
    return pipeline;
  }

  const literal = (x) => x.toExponential(8);
  const PARAMS = "struct P { w: u32, h: u32 }; @group(0) @binding(3) var<uniform> p: P;";
  const VECTORS = `
    @group(0) @binding(0) var<storage, read> src: array<vec4f>;
    @group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;`;
  const MAIN_HEAD = "@compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {\n"
    + "  if (id.x >= p.w || id.y >= p.h) { return; }";

  // weights: [output][input]; finish wraps each output group's expression.
  function convolution(weights, bias, inputs, outputs, finish, extra = "") {
    const nIn = inputs / 4;
    const nOut = outputs / 4;
    let constants = "";
    for (let o = 0; o < nOut; o++) {
      const b = [];
      for (let r = 0; r < 4; r++) b.push(literal(bias[o * 4 + r]));
      constants += `const B${o} = vec4f(${b.join(", ")});\n`;
      for (let i = 0; i < nIn; i++) {
        const m = [];
        for (let column = 0; column < 4; column++) {
          for (let row = 0; row < 4; row++) m.push(literal(weights[(o * 4 + row) * inputs + i * 4 + column]));
        }
        constants += `const M${o}_${i} = mat4x4f(${m.join(", ")});\n`;
      }
    }
    let load = "";
    for (let i = 0; i < nIn; i++) load += `  let v${i} = src[a + ${i}u];\n`;
    let body = "";
    for (let o = 0; o < nOut; o++) {
      const terms = [];
      for (let i = 0; i < nIn; i++) terms.push(`M${o}_${i} * v${i}`);
      body += `  dst[b + ${o}u] = ${finish(`${terms.join(" + ")} + B${o}`, o)};\n`;
    }
    return `${VECTORS}\n${PARAMS}\n${extra}\n${constants}${MAIN_HEAD}
      let cell = id.y * p.w + id.x;
      let a = cell * ${nIn}u; let b = cell * ${nOut}u;
${load}${body}}`;
  }

  function depthwise(weights, bias, channels) {
    const n = channels / 4;
    let constants = "";
    for (let c = 0; c < n; c++) {
      const b = [];
      for (let k = 0; k < 4; k++) b.push(literal(bias[c * 4 + k]));
      constants += `const B${c} = vec4f(${b.join(", ")});\n`;
      for (let k = 0; k < 9; k++) {
        const w = [];
        for (let comp = 0; comp < 4; comp++) w.push(literal(weights[(c * 4 + comp) * 9 + k]));
        constants += `const W${c}_${k} = vec4f(${w.join(", ")});\n`;
      }
    }
    let body = "";
    for (let c = 0; c < n; c++) {
      const terms = [];
      for (let k = 0; k < 9; k++) terms.push(`W${c}_${k} * src[i${k} + ${c}u]`);
      body += `  dst[i4 + ${c}u] = ${terms.join(" + ")} + B${c};\n`;
    }
    return `${VECTORS}\n${PARAMS}\n${constants}${MAIN_HEAD}
      let x0 = max(id.x, 1u) - 1u; let x2 = min(id.x + 1u, p.w - 1u);
      let y0 = (max(id.y, 1u) - 1u) * p.w; let y1 = id.y * p.w; let y2 = min(id.y + 1u, p.h - 1u) * p.w;
      let i0 = (y0 + x0) * ${n}u; let i1 = (y0 + id.x) * ${n}u; let i2 = (y0 + x2) * ${n}u;
      let i3 = (y1 + x0) * ${n}u; let i4 = (y1 + id.x) * ${n}u; let i5 = (y1 + x2) * ${n}u;
      let i6 = (y2 + x0) * ${n}u; let i7 = (y2 + id.x) * ${n}u; let i8 = (y2 + x2) * ${n}u;
${body}}`;
  }

  // Packs both frames to half resolution, in the order the network was trained with.
  function unpackShader() {
    return `${PARAMS}
    @group(0) @binding(0) var cur: texture_2d<f32>;
    @group(0) @binding(1) var prev: texture_2d<f32>;
    @group(0) @binding(2) var<storage, read> state: array<vec4f>;
    @group(0) @binding(5) var<storage, read_write> dst: array<vec4f>;
    ${MAIN_HEAD}
      let c = vec2i(id.xy) * 2;
      let a0 = textureLoad(cur, c, 0).rgb;
      let a1 = textureLoad(cur, c + vec2i(1, 0), 0).rgb;
      let a2 = textureLoad(cur, c + vec2i(0, 1), 0).rgb;
      let a3 = textureLoad(cur, c + vec2i(1, 1), 0).rgb;
      let b0 = textureLoad(prev, c, 0).rgb;
      let b1 = textureLoad(prev, c + vec2i(1, 0), 0).rgb;
      let b2 = textureLoad(prev, c + vec2i(0, 1), 0).rgb;
      let b3 = textureLoad(prev, c + vec2i(1, 1), 0).rgb;
      let cell = id.y * p.w + id.x;
      let i = cell * 7u;
      dst[i] = vec4f(a0.r, a1.r, a2.r, a3.r);
      dst[i + 1u] = vec4f(a0.g, a1.g, a2.g, a3.g);
      dst[i + 2u] = vec4f(a0.b, a1.b, a2.b, a3.b);
      dst[i + 3u] = vec4f(b0.r, b1.r, b2.r, b3.r);
      dst[i + 4u] = vec4f(b0.g, b1.g, b2.g, b3.g);
      dst[i + 5u] = vec4f(b0.b, b1.b, b2.b, b3.b);
      dst[i + 6u] = state[cell * ${OUTPUT_CHANNELS / 4}u + ${STATE_VECTOR}u];
    }`;
  }

  // Format 2: the current frame 2x2 and the previous upscaled frame 4x4 per cell, the latter sampled
  // where the motion from the current frame back to the previous one points (bilinear, clamped), in
  // the channel order of joint.py's AlignedUpscaler (pixel_unshuffle: colour, then row, then column).
  function alignedUnpackShader() {
    return `${PARAMS}
    @group(0) @binding(0) var cur: texture_2d<f32>;
    @group(0) @binding(1) var big: texture_2d<f32>;
    @group(0) @binding(2) var<storage, read> state: array<vec4f>;
    @group(0) @binding(4) var flow: texture_2d<f32>;
    @group(0) @binding(5) var<storage, read_write> dst: array<vec4f>;
    @group(0) @binding(6) var smp: sampler;
    fn moved(x: u32, y: u32) -> vec3f {
      let uv = (vec2f(f32(x), f32(y)) + 0.5) / vec2f(f32(p.w * 4u), f32(p.h * 4u));
      let f = textureSampleLevel(flow, smp, uv, 0.0).zw / vec2f(textureDimensions(flow));
      return textureSampleLevel(big, smp, uv + f, 0.0).rgb;
    }
    ${MAIN_HEAD}
      let c = vec2i(id.xy) * 2;
      let a0 = textureLoad(cur, c, 0).rgb;
      let a1 = textureLoad(cur, c + vec2i(1, 0), 0).rgb;
      let a2 = textureLoad(cur, c + vec2i(0, 1), 0).rgb;
      let a3 = textureLoad(cur, c + vec2i(1, 1), 0).rgb;
      let cell = id.y * p.w + id.x;
      let i = cell * ${ALIGNED_INPUT_CHANNELS / 4}u;
      dst[i] = vec4f(a0.r, a1.r, a2.r, a3.r);
      dst[i + 1u] = vec4f(a0.g, a1.g, a2.g, a3.g);
      dst[i + 2u] = vec4f(a0.b, a1.b, a2.b, a3.b);
      for (var dy = 0u; dy < 4u; dy++) {
        let y = id.y * 4u + dy;
        let s0 = moved(id.x * 4u, y);
        let s1 = moved(id.x * 4u + 1u, y);
        let s2 = moved(id.x * 4u + 2u, y);
        let s3 = moved(id.x * 4u + 3u, y);
        dst[i + 3u + dy] = vec4f(s0.r, s1.r, s2.r, s3.r);
        dst[i + 7u + dy] = vec4f(s0.g, s1.g, s2.g, s3.g);
        dst[i + 11u + dy] = vec4f(s0.b, s1.b, s2.b, s3.b);
      }
      dst[i + 15u] = state[cell * ${OUTPUT_CHANNELS / 4}u + ${STATE_VECTOR}u];
    }`;
  }

  // The network's detail added onto a bilinear enlargement of the frame.
  function composeShader() {
    return `${PARAMS}
    @group(0) @binding(0) var<storage, read> res: array<vec4f>;
    @group(0) @binding(1) var out: texture_storage_2d<rgba8unorm, write>;
    @group(0) @binding(2) var cur: texture_2d<f32>;
    @group(0) @binding(6) var smp: sampler;
    @compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {
      if (id.x >= p.w * 4u || id.y >= p.h * 4u) { return; }
      let cell = (id.y / 4u) * p.w + id.x / 4u;
      let sub = (id.y % 4u) * 4u + id.x % 4u;
      let uv = (vec2f(id.xy) + 0.5) / vec2f(f32(p.w * 4u), f32(p.h * 4u));
      let base = textureSampleLevel(cur, smp, uv, 0.0).rgb;
      let i = cell * ${OUTPUT_CHANNELS / 4}u + sub / 4u;
      let comp = sub % 4u;
      let r = res[i][comp];
      let g = res[i + 4u][comp];
      let b = res[i + 8u][comp];
      textureStore(out, id.xy, vec4f(clamp(base + vec3f(r, g, b), vec3f(0.0), vec3f(1.0)), 1.0));
    }`;
  }

  function buildShaders(model) {
    const { channels, blocks, weights } = model;
    const inputs = inputsOf(model.aligned);
    let at = 0;
    const take = (n) => { const part = weights.subarray(at, at + n); at += n; return part; };
    const relu = (expr) => `max(${expr}, vec4f(0.0))`;
    const headWeights = take(inputs * channels);
    const head = convolution(headWeights, take(channels), inputs, channels, relu);
    const depth = [];
    const mix = [];
    for (let i = 0; i < blocks; i++) {
      const dw = take(9 * channels);
      depth.push(depthwise(dw, take(channels), channels));
      const mixWeights = take(channels * channels);
      mix.push(convolution(mixWeights, take(channels), channels, channels,
        (expr, o) => relu(`${expr} + res[b + ${o}u]`),
        "@group(0) @binding(4) var<storage, read> res: array<vec4f>;"));
    }
    const tailWeights = take(channels * OUTPUT_CHANNELS);
    const tail = convolution(tailWeights, take(OUTPUT_CHANNELS), channels, OUTPUT_CHANNELS,
      (expr, o) => (o === STATE_VECTOR ? `tanh(${expr})` : expr));
    return { unpack: model.aligned ? alignedUnpackShader() : unpackShader(), head, depthwise: depth, mix, tail, compose: composeShader() };
  }

  class Upscaler {
    constructor(device, model, width, height, sampler) {
      this.device = device;
      this.sampler = sampler;
      this.w = width / 2;
      this.h = height / 2;
      this.ready = false;
      this.stateDirty = true;
      this.aligned = !!model.aligned;
      // zero motion, for frames that have none: the aligned network then gets the current frame enlarged
      this.still = device.createTexture({ size: [1, 1], format: "rgba16float", usage: GPUTextureUsage.TEXTURE_BINDING });
      this.stillView = { id: "still", view: this.still.createView() };
      const cells = this.w * this.h;
      const usage = GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST;
      const buffer = (channels) => device.createBuffer({ size: cells * channels * 4, usage });
      this.params = device.createBuffer({ size: 16, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
      device.queue.writeBuffer(this.params, 0, new Uint32Array([this.w, this.h, 0, 0]));
      this.input = buffer(inputsOf(this.aligned));
      this.scratch = buffer(model.channels);
      this.states = [buffer(model.channels), buffer(model.channels)];
      this.output = buffer(OUTPUT_CHANNELS);
      this.buffers = [this.input, this.scratch, ...this.states, this.output];
      this.frameGroups = new Map();
      this.compile(model).catch((e) => console.warn("[streamremaster] upscaler unavailable:", e));
    }

    // Asynchronous: a pipeline compiled on the first frame would freeze the video for seconds.
    async compile(model) {
      const code = buildShaders(model);
      const make = (text) => cachedPipeline(this.device, text);
      const [unpack, head, tail, compose, depth, mix] = await Promise.all([
        make(code.unpack), make(code.head), make(code.tail), make(code.compose),
        Promise.all(code.depthwise.map(make)), Promise.all(code.mix.map(make)),
      ]);
      const res = (b) => ({ buffer: b });
      const group = (pipeline, entries) => this.device.createBindGroup({
        layout: pipeline.getBindGroupLayout(0),
        entries: Object.entries(entries).map(([binding, resource]) => ({ binding: Number(binding), resource })),
      });
      const params = res(this.params);
      this.unpack = unpack;
      this.compose = compose;
      const steps = [{ pipeline: head, group: group(head, { 0: res(this.input), 1: res(this.states[0]), 3: params }) }];
      let current = 0;
      for (let i = 0; i < depth.length; i++) {
        const other = 1 - current;
        steps.push({ pipeline: depth[i], group: group(depth[i], { 0: res(this.states[current]), 1: res(this.scratch), 3: params }) });
        steps.push({ pipeline: mix[i], group: group(mix[i], { 0: res(this.scratch), 1: res(this.states[other]), 3: params, 4: res(this.states[current]) }) });
        current = other;
      }
      steps.push({ pipeline: tail, group: group(tail, { 0: res(this.states[current]), 1: res(this.output), 3: params }) });
      this.steps = steps;
      this.ready = true;
    }

    frameGroup(current, previous, output, motion) {
      const key = `${current.id}:${previous.id}:${output.id}:${motion ? motion.id : ""}`;
      let groups = this.frameGroups.get(key);
      if (!groups) {
        const params = { buffer: this.params };
        const unpackEntries = [
          { binding: 0, resource: current.view }, { binding: 1, resource: previous.view },
          { binding: 2, resource: { buffer: this.output } }, { binding: 3, resource: params },
          { binding: 5, resource: { buffer: this.input } },
        ];
        if (this.aligned) unpackEntries.push({ binding: 4, resource: motion.view }, { binding: 6, resource: this.sampler });
        groups = {
          unpack: this.device.createBindGroup({ layout: this.unpack.getBindGroupLayout(0), entries: unpackEntries }),
          compose: this.device.createBindGroup({
            layout: this.compose.getBindGroupLayout(0),
            entries: [
              { binding: 0, resource: { buffer: this.output } }, { binding: 1, resource: output.view },
              { binding: 2, resource: current.view }, { binding: 3, resource: params },
              { binding: 6, resource: this.sampler },
            ],
          }),
        };
        this.frameGroups.set(key, groups);
      }
      return groups;
    }

    resetState() {
      this.stateDirty = true;
    }

    // Records the whole network into the encoder. Textures are {id, view}. An aligned model takes
    // `aligned` = {previous: the previous upscaled frame, motion: the motion texture of this pair}; when
    // it is missing, the current frame stands in for the previous one, with no motion.
    run(encoder, current, previous, output, aligned = null) {
      if (this.stateDirty) {
        encoder.clearBuffer(this.output);
        this.stateDirty = false;
      }
      let motion = null;
      if (this.aligned) {
        previous = aligned ? aligned.previous : current;
        motion = aligned ? aligned.motion : this.stillView;
      }
      const groups = this.frameGroup(current, previous, output, motion);
      const pass = encoder.beginComputePass();
      const columns = Math.ceil(this.w / 64);
      const run = (pipeline, group) => {
        pass.setPipeline(pipeline);
        pass.setBindGroup(0, group);
        pass.dispatchWorkgroups(columns, this.h);
      };
      run(this.unpack, groups.unpack);
      for (const step of this.steps) run(step.pipeline, step.group);
      pass.setPipeline(this.compose);
      pass.setBindGroup(0, groups.compose);
      pass.dispatchWorkgroups(Math.ceil(this.w * 4 / 64), this.h * 4);
      pass.end();
    }

    destroy() {
      for (const b of this.buffers) b.destroy();
      this.params.destroy();
      this.still.destroy();
      this.frameGroups.clear();
      this.ready = false;
    }
  }

  // The graphics memory the Upscaler's buffers take for captured frames of width x height.
  function memoryBytes(model, width, height) {
    const cells = (width / 2) * (height / 2);
    return 4 * cells * (inputsOf(!!model.aligned) + 3 * model.channels + OUTPUT_CHANNELS);
  }

  root.STFramegenSR = { parseModel, buildShaders, weightCount, memoryBytes, Upscaler, MAX_MODEL_BYTES, convolution, depthwise, literal };
})(globalThis);
