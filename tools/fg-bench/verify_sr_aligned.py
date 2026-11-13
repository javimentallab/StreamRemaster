"""Checks that the WGSL the extension generates for an aligned upscaler (format 2) computes the same
picture as joint.py's AlignedUpscaler. Two consecutive real frames go through both: the first with no
motion (the current frame enlarged stands in for the previous upscaled one), the second with the
first one's upscaled output moved onto it by the motion network's 1->0 half. The motion itself is
computed in PyTorch and handed to both as the same rgba16float texture the interpolator writes
(verify_fi.py checks that part).

Usage: python verify_sr_aligned.py <joint checkpoint.pt> <shaders.json> <frame0.png> <frame1.png> <train dir>
"""
import json
import sys

import numpy as np
import torch
import torch.nn.functional as F
import wgpu
from PIL import Image

checkpoint, shaders_path, frame0, frame1, train_dir = sys.argv[1:6]
sys.path.insert(0, train_dir)
from joint import Joint, align, bilinear2  # noqa: E402
from train import HIDDEN  # noqa: E402


def load(path):
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)
    h, w = image.shape[0] // 16 * 16, image.shape[1] // 16 * 16
    return image[:h, :w]


def model_from(path):
    saved = torch.load(path, map_location="cpu")
    shape = saved["shape"]
    fi = shape["fi"]
    model = Joint(shape["sr"]["channels"], shape["sr"]["blocks"],
                  ",".join(str(fi[k]) for k in ("c1", "c2", "b1", "b2", "b3", "bu")), aligned=True)
    model.load_state_dict(saved["model"])
    return model.eval()


def torch_output(model, a, b):
    tensor = lambda x: torch.from_numpy(x.copy()).permute(2, 0, 1)[None].float() / 255
    first, second = tensor(a), tensor(b)
    with torch.no_grad():
        state = torch.zeros(1, HIDDEN, first.shape[2] // 2, first.shape[3] // 2)
        big0, state = model.sr.step(first, bilinear2(first), state)
        # the GPU keeps the upscaled frame in an 8-bit texture: round it the same way before reusing it
        big0 = (big0.clamp(0, 1) * 255).round() / 255
        motion = model.fi.motion(first, second)
        big1, _ = model.sr.step(second, align(big0, motion), state)
    to8 = lambda x: (x[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
    return to8(big1), motion[0, :4].permute(1, 2, 0).numpy().astype(np.float16)


def wgpu_output(a, b, motion, shaders):
    height, width = a.shape[:2]
    w, h = width // 2, height // 2
    cells = w * h
    device = wgpu.gpu.request_adapter_sync(power_preference="high-performance").request_device_sync()
    usage = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_DST
    make = lambda channels: device.create_buffer(size=cells * channels * 4, usage=usage)
    channels, blocks = shaders["channels"], shaders["blocks"]
    code = shaders["shaders"]
    params = device.create_buffer_with_data(data=np.array([w, h, 0, 0], dtype=np.uint32).tobytes(), usage=wgpu.BufferUsage.UNIFORM)
    inputs, scratch, t0, t1, output = make(64), make(channels), make(channels), make(channels), make(52)
    sampler = device.create_sampler(mag_filter="linear", min_filter="linear")
    res = lambda buf: {"buffer": buf, "offset": 0, "size": buf.size}
    pipeline = lambda text: device.create_compute_pipeline(layout="auto", compute={"module": device.create_shader_module(code=text), "entry_point": "main"})
    group = lambda p, entries: device.create_bind_group(layout=p.get_bind_group_layout(0), entries=[{"binding": k, "resource": v} for k, v in entries.items()])

    def texture(data, fmt="rgba8unorm", bpp=4):
        th, tw = data.shape[:2]
        tex = device.create_texture(size=(tw, th, 1), format=fmt, usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST)
        device.queue.write_texture({"texture": tex, "origin": (0, 0, 0)}, np.ascontiguousarray(data).tobytes(),
                                   {"bytes_per_row": tw * bpp, "rows_per_image": th}, (tw, th, 1))
        return tex

    rgba = lambda x: np.dstack([x, np.full(x.shape[:2], 255, dtype=np.uint8)])
    tex_a, tex_b = texture(rgba(a)), texture(rgba(b))
    still = texture(np.zeros((1, 1, 4), np.float16), "rgba16float", 8)
    flow = texture(motion, "rgba16float", 8)
    outs = [device.create_texture(size=(width * 2, height * 2, 1), format="rgba8unorm",
                                  usage=wgpu.TextureUsage.STORAGE_BINDING | wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_SRC)
            for _ in range(2)]
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

    def frame(current_tex, previous_big, motion_tex, out):
        encoder = device.create_command_encoder()
        p = encoder.begin_compute_pass()
        p.set_pipeline(unpack)
        p.set_bind_group(0, group(unpack, {0: current_tex.create_view(), 1: previous_big.create_view(), 2: res(output), 3: param,
                                           4: motion_tex.create_view(), 5: res(inputs), 6: sampler}))
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

    encoder = device.create_command_encoder()
    encoder.clear_buffer(output)
    device.queue.submit([encoder.finish()])
    frame(tex_a, tex_a, still, outs[0])
    frame(tex_b, outs[0], flow, outs[1])
    data = device.queue.read_texture({"texture": outs[1], "origin": (0, 0, 0)}, {"bytes_per_row": width * 2 * 4, "rows_per_image": height * 2},
                                     (width * 2, height * 2, 1))
    return np.frombuffer(data, dtype=np.uint8).reshape(height * 2, width * 2, 4)[:, :, :3]


def main():
    a, b = load(frame0), load(frame1)
    model = model_from(checkpoint)
    expected, motion = torch_output(model, a, b)
    actual = wgpu_output(a, b, motion, json.load(open(shaders_path, encoding="utf-8")))
    diff = np.abs(expected.astype(np.int32) - actual.astype(np.int32))
    print(json.dumps({"size": list(actual.shape), "mean_abs_diff": round(float(diff.mean()), 4), "max_abs_diff": int(diff.max()),
                      "pixels_off_by_more_than_2": round(float((diff > 2).mean()) * 100, 4)}))


main()
