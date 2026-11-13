"""Checks that the WGSL the extension generates computes the same picture as the PyTorch network:
two consecutive real frames go through both, so the recurrent state is covered too.

Usage: python verify_sr.py <checkpoint.pt> <shaders.json> <frame0.png> <frame1.png> <train dir>
Runs PyTorch on the CPU and the shaders on the GPU.
"""
import json
import sys

import numpy as np
import torch
import wgpu
from PIL import Image

checkpoint, shaders_path, frame0, frame1, train_dir = sys.argv[1:6]
sys.path.insert(0, train_dir)
from train import HIDDEN, Upscaler  # noqa: E402


def load(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)


def torch_output(a, b):
    saved = torch.load(checkpoint, map_location="cpu")
    model = Upscaler(saved["channels"], saved["blocks"])
    model.load_state_dict(saved["model"])
    model.eval()
    tensor = lambda x: torch.from_numpy(x.copy()).permute(2, 0, 1)[None].float() / 255
    first, second = tensor(a), tensor(b)
    with torch.no_grad():
        state = torch.zeros(1, HIDDEN, first.shape[2] // 2, first.shape[3] // 2)
        _, state = model.step(first, first, state)
        output, _ = model.step(second, first, state)
    return (output[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)


def wgpu_output(a, b, shaders):
    height, width = a.shape[:2]
    w, h = width // 2, height // 2
    cells = w * h
    device = wgpu.gpu.request_adapter_sync(power_preference="high-performance").request_device_sync()
    usage = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST
    make = lambda channels: device.create_buffer(size=cells * channels * 4, usage=usage)
    channels, blocks = shaders["channels"], shaders["blocks"]
    code = shaders["shaders"]
    params = device.create_buffer_with_data(data=np.array([w, h, 0, 0], dtype=np.uint32).tobytes(), usage=wgpu.BufferUsage.UNIFORM)
    inputs, scratch, t0, t1, output = make(28), make(channels), make(channels), make(channels), make(52)
    sampler = device.create_sampler(mag_filter="linear", min_filter="linear")
    res = lambda b: {"buffer": b, "offset": 0, "size": b.size}
    pipeline = lambda text: device.create_compute_pipeline(layout="auto", compute={"module": device.create_shader_module(code=text), "entry_point": "main"})
    group = lambda p, entries: device.create_bind_group(layout=p.get_bind_group_layout(0), entries=[{"binding": k, "resource": v} for k, v in entries.items()])

    def texture(data):
        tex = device.create_texture(size=(width, height, 1), format="rgba8unorm", usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST)
        rgba = np.dstack([data, np.full(data.shape[:2], 255, dtype=np.uint8)])
        device.queue.write_texture({"texture": tex, "origin": (0, 0, 0)}, rgba.tobytes(), {"bytes_per_row": width * 4, "rows_per_image": height}, (width, height, 1))
        return tex

    tex_a, tex_b = texture(a), texture(b)
    out = device.create_texture(size=(width * 2, height * 2, 1), format="rgba8unorm", usage=wgpu.TextureUsage.STORAGE_BINDING | wgpu.TextureUsage.COPY_SRC)
    param = res(params)

    head = pipeline(code["head"])
    steps = [(head, group(head, {0: res(inputs), 1: res(t0), 3: param}))]
    states, current = [t0, t1], 0
    for i in range(blocks):
        dw = pipeline(code["depthwise"][i])
        mix = pipeline(code["mix"][i])
        other = 1 - current
        steps.append((dw, group(dw, {0: res(states[current]), 1: res(scratch), 3: param})))
        steps.append((mix, group(mix, {0: res(scratch), 1: res(states[other]), 3: param, 4: res(states[current])})))
        current = other
    tail = pipeline(code["tail"])
    steps.append((tail, group(tail, {0: res(states[current]), 1: res(output), 3: param})))
    unpack = pipeline(code["unpack"])
    compose = pipeline(code["compose"])

    def frame(current_tex, previous_tex):
        encoder = device.create_command_encoder()
        p = encoder.begin_compute_pass()
        p.set_pipeline(unpack)
        p.set_bind_group(0, group(unpack, {0: current_tex.create_view(), 1: previous_tex.create_view(), 2: res(output), 3: param, 5: res(inputs)}))
        columns = (w + 63) // 64
        p.dispatch_workgroups(columns, h)
        for pipe, bound in steps:
            p.set_pipeline(pipe)
            p.set_bind_group(0, bound)
            p.dispatch_workgroups(columns, h)
        p.set_pipeline(compose)
        p.set_bind_group(0, group(compose, {0: res(output), 1: out.create_view(), 2: current_tex.create_view(), 3: param, 6: sampler}))
        p.dispatch_workgroups((w * 4 + 63) // 64, h * 4)
        p.end()
        device.queue.submit([encoder.finish()])

    frame(tex_a, tex_a)
    frame(tex_b, tex_a)
    data = device.queue.read_texture({"texture": out, "origin": (0, 0, 0)}, {"bytes_per_row": width * 2 * 4, "rows_per_image": height * 2}, (width * 2, height * 2, 1))
    return np.frombuffer(data, dtype=np.uint8).reshape(height * 2, width * 2, 4)[:, :, :3]


def main():
    a, b = load(frame0), load(frame1)
    expected = torch_output(a, b)
    actual = wgpu_output(a, b, json.load(open(shaders_path, encoding="utf-8")))
    diff = np.abs(expected.astype(np.int32) - actual.astype(np.int32))
    print(json.dumps({"size": list(actual.shape), "mean_abs_diff": round(float(diff.mean()), 4), "max_abs_diff": int(diff.max()),
                      "pixels_off_by_more_than_2": round(float((diff > 2).mean()) * 100, 4)}))


main()
