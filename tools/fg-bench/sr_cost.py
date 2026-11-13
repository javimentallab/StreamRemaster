"""Measures what an upscaling network of a given shape costs on a GPU, running WGSL through wgpu with
no browser, so a headless machine can do it. Weights are random: only the time matters.

The shape is the one the model will have: the input is unpacked to half resolution, runs through
blocks of a 3x3 depthwise convolution plus a 1x1 convolution with a residual, and is packed back
to twice the input resolution. Channels travel in groups of four and the weights are written into
the shader as constants, which is what makes it fast: no weight is ever read from memory.

Usage: python sr_cost.py [frames per configuration]
"""
import json
import sys
import time

import numpy as np
import wgpu

FRAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 40
HIDDEN = 4
INPUT_CHANNELS = 2 * 3 * 4 + HIDDEN  # current and previous frame unpacked, plus the recurrent state
OUTPUT_CHANNELS = 3 * 16 + HIDDEN    # 4x4 packed RGB at twice the input resolution, plus the state
CONFIGS = [(16, 3), (24, 4), (32, 4)]
if len(sys.argv) > 2:  # e.g. '[[32,6],[48,4]]'
    CONFIGS = [tuple(c) for c in json.loads(sys.argv[2])]
INPUTS = [(1280, 720), (1920, 1080)]
STORAGE = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.COPY_SRC
RNG = np.random.default_rng(1)

PARAMS = "struct P { w: u32, h: u32 }; @group(0) @binding(3) var<uniform> p: P;"
VECTORS = """
@group(0) @binding(0) var<storage, read> src: array<vec4f>;
@group(0) @binding(1) var<storage, read_write> dst: array<vec4f>;
"""


def numbers(count):
    return ", ".join(f"{x:.6f}" for x in RNG.uniform(-0.08, 0.08, count))


def conv1x1(inputs, outputs, residual):
    n_in, n_out = inputs // 4, outputs // 4
    constants = "".join(f"const M_{o}_{i} = mat4x4f({numbers(16)});\n" for o in range(n_out) for i in range(n_in))
    res_binding = "@group(0) @binding(4) var<storage, read> res: array<vec4f>;" if residual else ""
    load = "".join(f"let v{i} = src[a + {i}u];\n" for i in range(n_in))
    write = ""
    for o in range(n_out):
        sum_terms = " + ".join(f"M_{o}_{i} * v{i}" for i in range(n_in))
        extra = f" + res[b + {o}u]" if residual else ""
        write += f"dst[b + {o}u] = max({sum_terms}{extra}, vec4f(0.0));\n"
    return f"""{VECTORS}{PARAMS}{res_binding}
    {constants}
    @compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {{
      if (id.x >= p.w || id.y >= p.h) {{ return; }}
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
    {constants}
    @compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {{
      if (id.x >= p.w || id.y >= p.h) {{ return; }}
      let x0 = max(id.x, 1u) - 1u; let x2 = min(id.x + 1u, p.w - 1u);
      let y0 = (max(id.y, 1u) - 1u) * p.w; let y1 = id.y * p.w; let y2 = min(id.y + 1u, p.h - 1u) * p.w;
      let i0 = (y0 + x0) * {n}u; let i1 = (y0 + id.x) * {n}u; let i2 = (y0 + x2) * {n}u;
      let i3 = (y1 + x0) * {n}u; let i4 = (y1 + id.x) * {n}u; let i5 = (y1 + x2) * {n}u;
      let i6 = (y2 + x0) * {n}u; let i7 = (y2 + id.x) * {n}u; let i8 = (y2 + x2) * {n}u;
      {write}
    }}"""


def pack(channels):
    return f"""
    @group(0) @binding(0) var<storage, read> src: array<f32>;
    @group(0) @binding(1) var out: texture_storage_2d<rgba8unorm, write>;
    {PARAMS}
    const C = {channels}u;
    @compute @workgroup_size(64, 1) fn main(@builtin(global_invocation_id) id: vec3u) {{
      if (id.x >= p.w * 4u || id.y >= p.h * 4u) {{ return; }}
      let cell = (id.y / 4u) * p.w + id.x / 4u;
      let sub = (id.y % 4u) * 4u + id.x % 4u;
      let base = cell * C + sub * 3u;
      textureStore(out, id.xy, vec4f(src[base], src[base + 1u], src[base + 2u], 1.0));
    }}"""


class Bench:
    def __init__(self):
        self.adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        limits = self.adapter.limits
        self.device = self.adapter.request_device_sync(required_limits={
            "max-storage-buffer-binding-size": limits["max-storage-buffer-binding-size"],
            "max-buffer-size": limits["max-buffer-size"],
        })
        self.flag = self.device.create_buffer(size=4, usage=wgpu.BufferUsage.COPY_SRC | wgpu.BufferUsage.COPY_DST)

    def pipeline(self, code):
        module = self.device.create_shader_module(code=code)
        return self.device.create_compute_pipeline(layout="auto", compute={"module": module, "entry_point": "main"})

    def tensor(self, cells, channels):
        return self.device.create_buffer(size=cells * channels * 4, usage=STORAGE)

    def group(self, pipeline, resources):
        entries = [{"binding": k, "resource": v} for k, v in resources.items()]
        return self.device.create_bind_group(layout=pipeline.get_bind_group_layout(0), entries=entries)

    def build(self, width, height, channels, blocks):
        d = self.device
        w, h = width // 2, height // 2
        cells = w * h
        params = d.create_buffer_with_data(data=np.array([w, h], dtype=np.uint32).tobytes(), usage=wgpu.BufferUsage.UNIFORM)
        param = {"buffer": params, "offset": 0, "size": 8}
        res = lambda b: {"buffer": b, "offset": 0, "size": b.size}

        source = self.tensor(cells, INPUT_CHANNELS)
        d.queue.write_buffer(source, 0, RNG.uniform(0, 1, cells * INPUT_CHANNELS).astype(np.float32).tobytes())
        states = [self.tensor(cells, channels) for _ in range(blocks + 1)]
        scratch = self.tensor(cells, channels)
        output = self.tensor(cells, OUTPUT_CHANNELS)
        texture = d.create_texture(size=(width * 2, height * 2, 1), format="rgba8unorm", usage=wgpu.TextureUsage.STORAGE_BINDING)

        steps = []
        head = self.pipeline(conv1x1(INPUT_CHANNELS, channels, False))
        steps.append((head, self.group(head, {0: res(source), 1: res(states[0]), 3: param}), w, h))
        for i in range(blocks):
            dw = self.pipeline(depthwise(channels))
            mix = self.pipeline(conv1x1(channels, channels, True))
            steps.append((dw, self.group(dw, {0: res(states[i]), 1: res(scratch), 3: param}), w, h))
            steps.append((mix, self.group(mix, {0: res(scratch), 1: res(states[i + 1]), 3: param, 4: res(states[i])}), w, h))
        tail = self.pipeline(conv1x1(channels, OUTPUT_CHANNELS, False))
        steps.append((tail, self.group(tail, {0: res(states[-1]), 1: res(output), 3: param}), w, h))
        packer = self.pipeline(pack(OUTPUT_CHANNELS))
        steps.append((packer, self.group(packer, {0: res(output), 1: texture.create_view(), 3: param}), w * 4, h * 4))
        return steps

    def run(self, steps):
        d = self.device
        encoder = d.create_command_encoder()
        compute = encoder.begin_compute_pass()
        for pipeline, group, w, h in steps:
            compute.set_pipeline(pipeline)
            compute.set_bind_group(0, group)
            compute.dispatch_workgroups((w + 63) // 64, h)
        compute.end()
        d.queue.submit([encoder.finish()])
        d.queue.read_buffer(self.flag)  # waits for everything submitted before it


def macs(channels, blocks):
    return INPUT_CHANNELS * channels + blocks * (9 * channels + channels * channels) + channels * OUTPUT_CHANNELS


def main():
    bench = Bench()
    print(json.dumps({"adapter": bench.adapter.info.get("device"), "backend": bench.adapter.info.get("backend_type"), "wgpu": wgpu.__version__}), flush=True)
    for width, height in INPUTS:
        for channels, blocks in CONFIGS:
            start = time.perf_counter()
            steps = bench.build(width, height, channels, blocks)
            bench.run(steps)  # the first pass carries the shader compilation
            setup = time.perf_counter() - start
            times = []
            for _ in range(FRAMES):
                start = time.perf_counter()
                bench.run(steps)
                times.append((time.perf_counter() - start) * 1000)
            times.sort()
            print(json.dumps({
                "input": f"{width}x{height}", "output": f"{width * 2}x{height * 2}", "channels": channels, "blocks": blocks,
                "gmac": round(macs(channels, blocks) * (width // 2) * (height // 2) / 1e9, 2),
                "ms_p10": round(times[len(times) // 10], 2), "ms_p50": round(times[len(times) // 2], 2),
                "setup_s": round(setup, 1), "fits_60fps": times[len(times) // 2] < 16.6,
            }), flush=True)


main()
