"""Checks that the WGSL the extension generates for the interpolator computes the same as PyTorch:
the motion (network, f16 textures) and the in-between frame from the present shader.

Usage: python verify_fi.py <checkpoint.pt | random> <shaders.json> <frame0.png> <frame1.png> <train dir> [t]
With "random" it writes random.pt (an untrained model with exaggerated motion) and stops, so the
shaders can be dumped from it first.
Runs PyTorch on the CPU and the shaders on the GPU.
"""
import json
import sys

import numpy as np
import torch
import wgpu
from PIL import Image

checkpoint, shaders_path, frame0, frame1, train_dir = sys.argv[1:6]
T = float(sys.argv[6]) if len(sys.argv) > 6 else 0.4
sys.path.insert(0, train_dir)
from interp import Interpolator, synthesize  # noqa: E402


def load(path):
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8)
    h, w = image.shape[0] // 16 * 16, image.shape[1] // 16 * 16
    return image[:h, :w]


def model_from(path):
    saved = torch.load(path, map_location="cpu")
    shape, state = saved["shape"], saved["model"]
    if "fi" in shape:  # a joint.py checkpoint: its motion part
        shape = shape["fi"]
        state = {k[3:]: v for k, v in state.items() if k.startswith("fi.")}
    model = Interpolator(**shape)
    model.load_state_dict(state)
    return model.eval()


def torch_output(model, a, b):
    tensor = lambda x: torch.from_numpy(x.copy()).permute(2, 0, 1)[None].float() / 255
    first, second = tensor(a), tensor(b)
    with torch.no_grad():
        motion = model.motion(first, second)
        frame = synthesize(first, second, motion, torch.tensor([T]))
    return motion[0].permute(1, 2, 0).numpy(), (frame[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)


def wgpu_output(shaders, a, b):
    height, width = a.shape[:2]
    w4, h4 = width // 4, height // 4
    adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    d = adapter.request_device_sync(required_limits={
        "max-storage-buffer-binding-size": adapter.limits["max-storage-buffer-binding-size"],
        "max-buffer-size": adapter.limits["max-buffer-size"],
    })
    shape = shaders["shape"]
    c1, c2 = shape["c1"], shape["c2"]
    n4, n8, n16 = w4 * h4, w4 * h4 // 4, w4 * h4 // 16
    sizes = {"in4": (n4, 32), "q0": (n4, c1), "q1": (n4, c1), "q2": (n4, c1), "qs": (n4, c1), "out": (n4, 8),
             "u8": (n8, 4 * c1), "e0": (n8, c2), "e1": (n8, c2), "e2": (n8, c2), "es": (n8, c2),
             "u16": (n16, 4 * c2), "s0": (n16, c2), "s1": (n16, c2), "ss": (n16, c2)}
    buffers = {k: d.create_buffer(size=n * c * 4, usage=wgpu.BufferUsage.STORAGE) for k, (n, c) in sizes.items()}
    uniform = lambda data: d.create_buffer_with_data(data=data, usage=wgpu.BufferUsage.UNIFORM)
    levels = {4: (w4, h4), 8: (w4 // 2, h4 // 2), 16: (w4 // 4, h4 // 4)}
    params = {k: uniform(np.array([w, h, 0, 0], dtype=np.uint32).tobytes()) for k, (w, h) in levels.items()}
    whole = lambda b: {"buffer": b, "offset": 0, "size": b.size}

    def texture(data):
        tex = d.create_texture(size=(width, height, 1), format="rgba8unorm",
                               usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST)
        rgba = np.concatenate([data, np.full((height, width, 1), 255, np.uint8)], 2)
        d.queue.write_texture({"texture": tex}, rgba.tobytes(), {"bytes_per_row": width * 4, "rows_per_image": height}, (width, height, 1))
        return tex

    ta, tb = texture(a), texture(b)
    motion_usage = wgpu.TextureUsage.STORAGE_BINDING | wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_SRC
    flow = d.create_texture(size=(w4, h4, 1), format="rgba16float", usage=motion_usage)
    extra = d.create_texture(size=(w4, h4, 1), format="rgba16float", usage=motion_usage)

    def compute(code):
        return d.create_compute_pipeline(layout="auto", compute={"module": d.create_shader_module(code=code), "entry_point": "main"})

    def group(pipeline, entries):
        return d.create_bind_group(layout=pipeline.get_bind_group_layout(0),
                                   entries=[{"binding": k, "resource": v} for k, v in entries.items()])

    encoder = d.create_command_encoder()
    cpass = encoder.begin_compute_pass()

    def run(pipeline, bind, w, h):
        cpass.set_pipeline(pipeline)
        cpass.set_bind_group(0, bind)
        cpass.dispatch_workgroups((w + 63) // 64, h)

    luma = compute(shaders["luma"])
    run(luma, group(luma, {0: ta.create_view(), 2: tb.create_view(), 1: whole(buffers["in4"]), 3: whole(params[4])}), w4, h4)
    for step in shaders["plan"]:
        pipeline = compute(step["shader"])
        entries = {int(k): whole(buffers[v]) for k, v in step["buffers"].items()}
        entries[3] = whole(params[step["level"]])
        w, h = levels[step["level"]]
        run(pipeline, group(pipeline, entries), w, h)
    tex = compute(shaders["texture"])
    run(tex, group(tex, {0: whole(buffers["out"]), 1: flow.create_view(), 2: extra.create_view(), 3: whole(params[4])}), w4, h4)
    cpass.end()

    out = d.create_texture(size=(width, height, 1), format="rgba8unorm",
                           usage=wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.COPY_SRC)
    module = d.create_shader_module(code=shaders["present"])
    present = d.create_render_pipeline(layout="auto", vertex={"module": module, "entry_point": "vs"},
                                       fragment={"module": module, "entry_point": "fs", "targets": [{"format": "rgba8unorm"}]},
                                       primitive={"topology": "triangle-list"})
    sampler = d.create_sampler(mag_filter="linear", min_filter="linear")
    # t, motion grid, sharpening off; then the flag that the motion is the network's
    p = uniform(np.array([T, w4, h4, 0, 1, 0, 0, 0], dtype=np.float32).tobytes())
    bind = group(present, {0: ta.create_view(), 1: tb.create_view(), 2: sampler, 3: whole(p), 4: flow.create_view(), 5: extra.create_view()})
    rpass = encoder.begin_render_pass(color_attachments=[{"view": out.create_view(), "load_op": "clear", "store_op": "store",
                                                          "clear_value": (0, 0, 0, 1)}])
    rpass.set_pipeline(present)
    rpass.set_bind_group(0, bind)
    rpass.draw(3)
    rpass.end()
    d.queue.submit([encoder.finish()])

    def read(texture_, w, h, bpp, dtype):
        raw = d.queue.read_texture({"texture": texture_}, {"bytes_per_row": w * bpp, "rows_per_image": h}, (w, h, 1))
        return np.frombuffer(raw, dtype=dtype).reshape(h, w, -1)

    motion = np.concatenate([read(flow, w4, h4, 8, np.float16), read(extra, w4, h4, 8, np.float16)], 2).astype(np.float32)
    return motion, read(out, width, height, 4, np.uint8)[:, :, :3]


def main():
    if checkpoint == "random":
        torch.manual_seed(3)
        model = Interpolator()
        with torch.no_grad():
            model.tail.weight.mul_(6)
            model.tail.bias[:4] = torch.tensor([3.0, -2.0, -2.5, 1.5]) / 4
        torch.save({"model": model.state_dict(), "shape": model.shape, "iteration": 0}, "random.pt")
        print("wrote random.pt")
        return
    a, b = load(frame0), load(frame1)
    model = model_from(checkpoint)
    shaders = json.load(open(shaders_path))
    ref_motion, ref_frame = torch_output(model, a, b)
    gpu_motion, gpu_frame = wgpu_output(shaders, a, b)
    flow_err = np.abs(gpu_motion[..., :5] - ref_motion[..., :5])
    scale = np.abs(ref_motion[..., :5]).mean(axis=(0, 1))
    frame_err = np.abs(gpu_frame.astype(int) - ref_frame.astype(int))
    print(json.dumps({
        "size": [a.shape[1], a.shape[0]], "t": T,
        "motion_mean_abs": [round(float(x), 3) for x in scale],
        "motion_err_max": round(float(flow_err.max()), 4), "motion_err_mean": round(float(flow_err.mean()), 5),
        "frame_err_max": int(frame_err.max()), "frame_err_mean": round(float(frame_err.mean()), 4),
        "frame_err_over_2": round(float((frame_err > 2).mean()), 6),
        "fade_err_mean": round(float(np.abs(((1 - T) * a + T * b) - ref_frame).mean()), 2),
    }))


main()
