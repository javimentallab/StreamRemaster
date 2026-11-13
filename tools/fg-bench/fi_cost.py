"""Measures what a frame interpolation network of a given shape costs on a GPU, running WGSL through
wgpu with no browser. Weights are random: only the time matters.

The network runs once per pair of source frames. It takes both frames as luma unpacked to a quarter
of their resolution (16 channels each), goes down to 1/8 and 1/16 with stride-2 steps (unpack by 2
plus a 1x1 convolution), back up with a 1x1 convolution plus a pack by 2 and a skip connection, and
ends in 8 channels at 1/4: the motion both ways, an occlusion mask and spare room. Every level is
made of blocks of a 3x3 depthwise convolution plus a 1x1 convolution with a residual, channels in
groups of four, weights written into the shader as constants.

Each displayed frame then only needs the synthesis pass: two motion samples and two frame samples
per output pixel. It is measured apart, at the output size.

Usage: python fi_cost.py [runs per configuration]
"""
import json
import sys
import time

import numpy as np
import wgpu

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
IN_CHANNELS = 32
OUT_CHANNELS = 8
# (channels at 1/4, channels at 1/8 and 1/16, blocks at 1/4, 1/8, 1/16, blocks after each way up)
CONFIGS = [(16, 32, 1, 2, 3, 1), (24, 48, 2, 2, 3, 1), (32, 64, 2, 2, 4, 1)]
if len(sys.argv) > 2:  # e.g. '[[32,64,3,3,4,1],[48,96,2,2,3,1]]'
    CONFIGS = [tuple(c) for c in json.loads(sys.argv[2])]
INPUTS = [(1280, 720), (1920, 1080)]
OUTPUTS = [(2560, 1440), (3840, 2160)]
STORAGE = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.COPY_SRC
RNG = np.random.default_rng(1)

PARAMS = "struct P { w: u32, h: u32 }; @group(0) @binding(3) var<uniform> p: P;"
VECTORS = """
@group(0) @binding(0) var<storage, read> src: array<vec4f>;
@group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;
"""
HEAD = """@compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {
  if (id.x >= p.w || id.y >= p.h) { return; }"""


def numbers(count):
    return ", ".join(f"{x:.6f}" for x in RNG.uniform(-0.08, 0.08, count))


def conv1x1(inputs, outputs, residual=False, relu=True):
    n_in, n_out = inputs // 4, outputs // 4
    constants = "".join(f"const M_{o}_{i} = mat4x4f({numbers(16)});\n" for o in range(n_out) for i in range(n_in))
    constants += "".join(f"const B_{o} = vec4f({numbers(4)});\n" for o in range(n_out))
    res_binding = "@group(0) @binding(4) var<storage, read> res: array<vec4f>;" if residual else ""
    load = "".join(f"let v{i} = src[a + {i}u];\n" for i in range(n_in))
    write = ""
    for o in range(n_out):
        expr = " + ".join(f"M_{o}_{i} * v{i}" for i in range(n_in)) + f" + B_{o}"
        if residual:
            expr += f" + res[b + {o}u]"
        write += f"dst[b + {o}u] = {f'max({expr}, vec4f(0.0))' if relu else expr};\n"
    return f"""{VECTORS}{PARAMS}{res_binding}
{constants}{HEAD}
  let cell = id.y * p.w + id.x;
  let a = cell * {n_in}u; let b = cell * {n_out}u;
  {load}{write}
}}"""


def depthwise(channels):
    n = channels // 4
    constants = "".join(f"const W_{c}_{k} = vec4f({numbers(4)});\n" for c in range(n) for k in range(9))
    write = ""
    for c in range(n):
        terms = " + ".join(f"W_{c}_{k} * src[i{k} + {c}u]" for k in range(9))
        write += f"dst[i4 + {c}u] = {terms};\n"
    return f"""{VECTORS}{PARAMS}
{constants}{HEAD}
  let x0 = max(id.x, 1u) - 1u; let x2 = min(id.x + 1u, p.w - 1u);
  let y0 = (max(id.y, 1u) - 1u) * p.w; let y1 = id.y * p.w; let y2 = min(id.y + 1u, p.h - 1u) * p.w;
  let i0 = (y0 + x0) * {n}u; let i1 = (y0 + id.x) * {n}u; let i2 = (y0 + x2) * {n}u;
  let i3 = (y1 + x0) * {n}u; let i4 = (y1 + id.x) * {n}u; let i5 = (y1 + x2) * {n}u;
  let i6 = (y2 + x0) * {n}u; let i7 = (y2 + id.x) * {n}u; let i8 = (y2 + x2) * {n}u;
  {write}
}}"""


def unpack2(channels):
    """Cell (x, y) at half resolution gets the four cells under it, one after another. p is the
    half-resolution size; the source is 2p (rounded down to even sizes beforehand)."""
    n = channels // 4
    copies = ""
    for k, (dx, dy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
        for c in range(n):
            copies += f"dst[b + {k * n + c}u] = src[((id.y * 2u + {dy}u) * p.w * 2u + id.x * 2u + {dx}u) * {n}u + {c}u];\n"
    return f"""{VECTORS}{PARAMS}
{HEAD}
  let b = (id.y * p.w + id.x) * {4 * n}u;
  {copies}
}}"""


def pack2(channels):
    """The reverse at twice the resolution, adding a skip connection. p is the full size."""
    n = channels // 4
    copies = "".join(f"dst[o + {c}u] = max(src[i + {c}u] + res[o + {c}u], vec4f(0.0));\n" for c in range(n))
    return f"""{VECTORS}{PARAMS}
@group(0) @binding(4) var<storage, read> res: array<vec4f>;
{HEAD}
  let k = (id.y % 2u) * 2u + id.x % 2u;
  let i = ((id.y / 2u) * (p.w / 2u) + id.x / 2u) * {4 * n}u + k * {n}u;
  let o = (id.y * p.w + id.x) * {n}u;
  {copies}
}}"""


LUMA = f"""
@group(0) @binding(0) var a: texture_2d<f32>;
@group(0) @binding(2) var b: texture_2d<f32>;
@group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;
{PARAMS}
const Y = vec3f(0.299, 0.587, 0.114);
{HEAD}
  let o = (id.y * p.w + id.x) * 8u;
  let c = vec2i(id.xy) * 4;
  for (var r = 0; r < 4; r++) {{
    var la: vec4f; var lb: vec4f;
    for (var x = 0; x < 4; x++) {{
      la[x] = dot(textureLoad(a, c + vec2i(x, r), 0).rgb, Y);
      lb[x] = dot(textureLoad(b, c + vec2i(x, r), 0).rgb, Y);
    }}
    dst[o + u32(r)] = la;
    dst[o + 4u + u32(r)] = lb;
  }}
}}"""

# Motion as an rgba16float texture so the synthesis gets hardware filtering.
TO_TEXTURE = f"""
@group(0) @binding(0) var<storage, read> src: array<vec4f>;
@group(0) @binding(1) var flow: texture_storage_2d<rgba16float, write>;
@group(0) @binding(2) var extra: texture_storage_2d<rgba16float, write>;
{PARAMS}
{HEAD}
  let i = (id.y * p.w + id.x) * 2u;
  textureStore(flow, id.xy, src[i]);
  textureStore(extra, id.xy, src[i + 1u]);
}}"""

SYNTH = """
struct S { w: u32, h: u32, t: f32, pad: f32 };
@group(0) @binding(0) var a: texture_2d<f32>;
@group(0) @binding(1) var b: texture_2d<f32>;
@group(0) @binding(2) var flow: texture_2d<f32>;
@group(0) @binding(3) var extra: texture_2d<f32>;
@group(0) @binding(4) var smp: sampler;
@group(0) @binding(5) var out: texture_storage_2d<rgba8unorm, write>;
@group(0) @binding(6) var<uniform> s: S;
@compute @workgroup_size(16, 16) fn main(@builtin(global_invocation_id) id: vec3u) {
  if (id.x >= s.w || id.y >= s.h) { return; }
  let size = vec2f(f32(s.w), f32(s.h));
  let uv = (vec2f(id.xy) + 0.5) / size;
  let f = textureSampleLevel(flow, smp, uv, 0.0);
  let m = 1.0 / (1.0 + exp(-textureSampleLevel(extra, smp, uv, 0.0).x));
  let t = s.t;
  let ft0 = -(1.0 - t) * t * f.xy + t * t * f.zw;
  let ft1 = (1.0 - t) * (1.0 - t) * f.xy - t * (1.0 - t) * f.zw;
  let ca = textureSampleLevel(a, smp, uv + ft0, 0.0).rgb;
  let cb = textureSampleLevel(b, smp, uv + ft1, 0.0).rgb;
  let wa = (1.0 - t) * m; let wb = t * (1.0 - m);
  textureStore(out, id.xy, vec4f((wa * ca + wb * cb) / max(wa + wb, 1e-4), 1.0));
}"""


class Bench:
    def __init__(self):
        self.adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        limits = self.adapter.limits
        self.device = self.adapter.request_device_sync(required_limits={
            "max-storage-buffer-binding-size": limits["max-storage-buffer-binding-size"],
            "max-buffer-size": limits["max-buffer-size"],
        })
        self.flag = self.device.create_buffer(size=4, usage=wgpu.BufferUsage.COPY_SRC | wgpu.BufferUsage.COPY_DST)
        self.params = {}

    def pipeline(self, code):
        module = self.device.create_shader_module(code=code)
        return self.device.create_compute_pipeline(layout="auto", compute={"module": module, "entry_point": "main"})

    def param(self, w, h):
        if (w, h) not in self.params:
            buf = self.device.create_buffer_with_data(data=np.array([w, h], dtype=np.uint32).tobytes(), usage=wgpu.BufferUsage.UNIFORM)
            self.params[(w, h)] = {"buffer": buf, "offset": 0, "size": 8}
        return self.params[(w, h)]

    def tensor(self, cells, channels):
        return self.device.create_buffer(size=cells * channels * 4, usage=STORAGE)

    def group(self, pipeline, resources):
        entries = [{"binding": k, "resource": v} for k, v in resources.items()]
        return self.device.create_bind_group(layout=pipeline.get_bind_group_layout(0), entries=entries)

    def frame(self, w, h):
        d = self.device
        tex = d.create_texture(size=(w, h, 1), format="rgba8unorm",
                               usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.STORAGE_BINDING)
        d.queue.write_texture({"texture": tex}, RNG.integers(0, 255, w * h * 4, dtype=np.uint8).tobytes(),
                              {"bytes_per_row": w * 4, "rows_per_image": h}, (w, h, 1))
        return tex

    def level(self, steps, x, cells, channels, blocks, param, w, h):
        """Blocks at one level; x is the buffer holding the level's input, returned buffer holds its output."""
        res = lambda b: {"buffer": b, "offset": 0, "size": b.size}
        scratch = self.tensor(cells, channels)
        dw = self.pipeline(depthwise(channels))
        mix = self.pipeline(conv1x1(channels, channels, residual=True))
        for _ in range(blocks):
            y = self.tensor(cells, channels)
            steps.append((dw, self.group(dw, {0: res(x), 1: res(scratch), 3: param}), w, h))
            steps.append((mix, self.group(mix, {0: res(scratch), 1: res(y), 3: param, 4: res(x)}), w, h))
            x = y
        return x

    def build(self, width, height, c1, c2, b1, b2, b3, bu):
        d = self.device
        res = lambda b: {"buffer": b, "offset": 0, "size": b.size}
        w4, h4 = width // 16 * 4, height // 16 * 4  # quarter, kept divisible down to 1/16
        w8, h8, w16, h16 = w4 // 2, h4 // 2, w4 // 4, h4 // 4
        p4, p8, p16 = self.param(w4, h4), self.param(w8, h8), self.param(w16, h16)
        fa, fb = self.frame(width, height), self.frame(width, height)
        steps = []

        x = self.tensor(w4 * h4, IN_CHANNELS)
        luma = self.pipeline(LUMA)
        steps.append((luma, self.group(luma, {0: fa.create_view(), 2: fb.create_view(), 1: res(x), 3: p4}), w4, h4))
        head = self.pipeline(conv1x1(IN_CHANNELS, c1))
        s4 = self.tensor(w4 * h4, c1)
        steps.append((head, self.group(head, {0: res(x), 1: res(s4), 3: p4}), w4, h4))
        s4 = self.level(steps, s4, w4 * h4, c1, b1, p4, w4, h4)

        def down(x, cin, cout, cells, param, w, h):
            u = self.tensor(cells, 4 * cin)
            un = self.pipeline(unpack2(cin))
            steps.append((un, self.group(un, {0: res(x), 1: res(u), 3: param}), w, h))
            y = self.tensor(cells, cout)
            conv = self.pipeline(conv1x1(4 * cin, cout))
            steps.append((conv, self.group(conv, {0: res(u), 1: res(y), 3: param}), w, h))
            return y

        def up(x, skip, cin, cout, cells_low, cells_high, param_low, param_high, wl, hl, wh, hh):
            u = self.tensor(cells_low, 4 * cout)
            conv = self.pipeline(conv1x1(cin, 4 * cout, relu=False))
            steps.append((conv, self.group(conv, {0: res(x), 1: res(u), 3: param_low}), wl, hl))
            y = self.tensor(cells_high, cout)
            pk = self.pipeline(pack2(cout))
            steps.append((pk, self.group(pk, {0: res(u), 1: res(y), 3: param_high, 4: res(skip)}), wh, hh))
            return y

        s8 = down(s4, c1, c2, w8 * h8, p8, w8, h8)
        s8 = self.level(steps, s8, w8 * h8, c2, b2, p8, w8, h8)
        s16 = down(s8, c2, c2, w16 * h16, p16, w16, h16)
        s16 = self.level(steps, s16, w16 * h16, c2, b3, p16, w16, h16)
        u8 = up(s16, s8, c2, c2, w16 * h16, w8 * h8, p16, p8, w16, h16, w8, h8)
        u8 = self.level(steps, u8, w8 * h8, c2, bu, p8, w8, h8)
        u4 = up(u8, s4, c2, c1, w8 * h8, w4 * h4, p8, p4, w8, h8, w4, h4)
        u4 = self.level(steps, u4, w4 * h4, c1, bu, p4, w4, h4)
        out = self.tensor(w4 * h4, OUT_CHANNELS)
        tail = self.pipeline(conv1x1(c1, OUT_CHANNELS, relu=False))
        steps.append((tail, self.group(tail, {0: res(u4), 1: res(out), 3: p4}), w4, h4))
        usage = wgpu.TextureUsage.STORAGE_BINDING | wgpu.TextureUsage.TEXTURE_BINDING
        flow = d.create_texture(size=(w4, h4, 1), format="rgba16float", usage=usage)
        extra = d.create_texture(size=(w4, h4, 1), format="rgba16float", usage=usage)
        tt = self.pipeline(TO_TEXTURE)
        steps.append((tt, self.group(tt, {0: res(out), 1: flow.create_view(), 2: extra.create_view(), 3: p4}), w4, h4))
        return steps, (fa, fb, flow, extra)

    def synth(self, textures, width, height):
        d = self.device
        fa, fb, flow, extra = textures
        out = d.create_texture(size=(width, height, 1), format="rgba8unorm", usage=wgpu.TextureUsage.STORAGE_BINDING)
        smp = d.create_sampler(mag_filter="linear", min_filter="linear")
        uni = d.create_buffer_with_data(data=np.array([width, height], dtype=np.uint32).tobytes() + np.array([0.4, 0], dtype=np.float32).tobytes(),
                                        usage=wgpu.BufferUsage.UNIFORM)
        pipe = self.pipeline(SYNTH)
        group = self.group(pipe, {0: fa.create_view(), 1: fb.create_view(), 2: flow.create_view(), 3: extra.create_view(),
                                  4: smp, 5: out.create_view(), 6: {"buffer": uni, "offset": 0, "size": 16}})
        return pipe, group, width, height

    def run(self, steps, synth=None):
        d = self.device
        encoder = d.create_command_encoder()
        compute = encoder.begin_compute_pass()
        for pipeline, group, w, h in steps:
            compute.set_pipeline(pipeline)
            compute.set_bind_group(0, group)
            compute.dispatch_workgroups((w + 63) // 64, h)
        if synth:
            pipeline, group, w, h = synth
            compute.set_pipeline(pipeline)
            compute.set_bind_group(0, group)
            compute.dispatch_workgroups((w + 15) // 16, (h + 15) // 16)
        compute.end()
        d.queue.submit([encoder.finish()])
        d.queue.read_buffer(self.flag)

    def timed(self, fn):
        fn()  # compilation
        times = []
        for _ in range(RUNS):
            start = time.perf_counter()
            fn()
            times.append((time.perf_counter() - start) * 1000)
        times.sort()
        return round(times[len(times) // 10], 2), round(times[len(times) // 2], 2)


def params(c1, c2, b1, b2, b3, bu):
    block = lambda c: 9 * c + c + c * c + c
    return (IN_CHANNELS * c1 + c1 + b1 * block(c1) + 4 * c1 * c2 + c2 + b2 * block(c2) + 4 * c2 * c2 + c2
            + b3 * block(c2) + c2 * 4 * c2 + 4 * c2 + bu * block(c2) + c2 * 4 * c1 + 4 * c1 + bu * block(c1)
            + c1 * OUT_CHANNELS + OUT_CHANNELS)


def main():
    bench = Bench()
    print(json.dumps({"adapter": bench.adapter.info.get("device"), "backend": bench.adapter.info.get("backend_type")}), flush=True)
    empty = lambda: bench.run([])
    print(json.dumps({"empty_submit_ms": bench.timed(empty)}), flush=True)
    for width, height in INPUTS:
        for config in CONFIGS:
            steps, textures = bench.build(width, height, *config)
            p10, p50 = bench.timed(lambda: bench.run(steps))
            print(json.dumps({"input": f"{width}x{height}", "config": config, "params": params(*config),
                              "network_ms_p10": p10, "network_ms_p50": p50}), flush=True)
        for ow, oh in [(width, height)] + [o for o in OUTPUTS if o[0] == width * 2]:
            synth = bench.synth(textures, ow, oh)
            p10, p50 = bench.timed(lambda: bench.run([], synth))
            print(json.dumps({"input": f"{width}x{height}", "synth_output": f"{ow}x{oh}", "synth_ms_p10": p10, "synth_ms_p50": p50}), flush=True)


main()
