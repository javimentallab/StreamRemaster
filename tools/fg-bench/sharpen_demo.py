"""Shows the adaptive sharpening of the extension's present shader on real frames, and checks that the
shader compiles: a REDS validation frame and a game frame are halved and JPEG-compressed (quality 60,
as joint.py validates), upscaled by a joint.py checkpoint on the CPU, then drawn through
PRESENT_SHADER (dumped from framegen.js by dump-fi-shaders.mjs) on the GPU with wgpu, once per
sharpening strength. Writes a picture per frame: bicubic | model | soft | medium | strong | real, and
prints how far each strength moves the picture away from or towards the real frame (PSNR).

Usage: python sharpen_demo.py <data dir> <joint checkpoint.pt> <shaders.json> <output dir>
"""
import json
import pathlib
import sys

import numpy as np
import torch
import torch.nn.functional as F
import wgpu
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "train"))
import interp  # noqa: E402
from joint import Joint, degrade  # noqa: E402

STRENGTHS = [("model", 0.0), ("soft", 0.35), ("medium", 0.6), ("strong", 0.9)]


def frames(data):
    root = sorted(p for p in (data / "orig" / "val").iterdir() if p.is_dir())[0]
    yield "reds", interp.load(sorted(root.glob("*.png"))[50])
    clip = np.load(interp.packed(data / "packed120" / "games-val")[0], mmap_mode="r")
    yield "games", torch.from_numpy(np.array(clip[100])).permute(2, 0, 1).float() / 255


def present(device, shader, image, strength):
    height, width = image.shape[:2]
    texture = device.create_texture(size=(width, height, 1), format="rgba8unorm",
                                    usage=wgpu.TextureUsage.TEXTURE_BINDING | wgpu.TextureUsage.COPY_DST)
    rgba = np.concatenate([image, np.full((height, width, 1), 255, np.uint8)], 2)
    device.queue.write_texture({"texture": texture}, rgba.tobytes(), {"bytes_per_row": width * 4, "rows_per_image": height},
                               (width, height, 1))
    still = [device.create_texture(size=(1, 1, 1), format="rgba16float", usage=wgpu.TextureUsage.TEXTURE_BINDING) for _ in range(2)]
    out = device.create_texture(size=(width, height, 1), format="rgba8unorm",
                                usage=wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.COPY_SRC)
    module = device.create_shader_module(code=shader)
    pipeline = device.create_render_pipeline(layout="auto", vertex={"module": module, "entry_point": "vs"},
                                             fragment={"module": module, "entry_point": "fs", "targets": [{"format": "rgba8unorm"}]},
                                             primitive={"topology": "triangle-list"})
    params = device.create_buffer_with_data(data=np.array([0.0, 1.0, 1.0, strength, 0, 0, 0, 0], dtype=np.float32).tobytes(),
                                            usage=wgpu.BufferUsage.UNIFORM)
    sampler = device.create_sampler(mag_filter="linear", min_filter="linear")
    entries = {0: texture.create_view(), 1: texture.create_view(), 2: sampler,
               3: {"buffer": params, "offset": 0, "size": params.size}, 4: still[0].create_view(), 5: still[1].create_view()}
    group = device.create_bind_group(layout=pipeline.get_bind_group_layout(0),
                                     entries=[{"binding": k, "resource": v} for k, v in entries.items()])
    encoder = device.create_command_encoder()
    rpass = encoder.begin_render_pass(color_attachments=[{"view": out.create_view(), "load_op": "clear", "store_op": "store",
                                                          "clear_value": (0, 0, 0, 1)}])
    rpass.set_pipeline(pipeline)
    rpass.set_bind_group(0, group)
    rpass.draw(3)
    rpass.end()
    device.queue.submit([encoder.finish()])
    raw = device.queue.read_texture({"texture": out}, {"bytes_per_row": width * 4, "rows_per_image": height}, (width, height, 1))
    return np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 4)[:, :, :3]


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return 10 * np.log10(255 ** 2 / max(mse, 1e-10))


def main():
    data, checkpoint, shaders, out_dir = (pathlib.Path(x) for x in sys.argv[1:5])
    out_dir.mkdir(parents=True, exist_ok=True)
    shader = json.loads(shaders.read_text())["present"]
    saved = torch.load(checkpoint, map_location="cpu")
    shape = saved["shape"]
    fi = shape["fi"]
    model = Joint(shape["sr"]["channels"], shape["sr"]["blocks"],
                  ",".join(str(fi[k]) for k in ("c1", "c2", "b1", "b2", "b3", "bu")))
    model.load_state_dict(saved["model"])
    model.eval()
    device = wgpu.gpu.request_adapter_sync(power_preference="high-performance").request_device_sync()
    to8 = lambda x: (x.clamp(0, 1).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)
    for name, frame in frames(data):
        _, h, w = frame.shape
        s = min(h, w, 512) // 32 * 32
        real = frame[:, (h - s) // 2:(h - s) // 2 + s, (w - s) // 2:(w - s) // 2 + s]
        small = degrade(real[None], 60)
        with torch.no_grad():
            # the extension carries the recurrent state from frame to frame: warm it up as a still video would
            state = torch.zeros(1, 4, s // 4, s // 4)
            for _ in range(4):
                big, state = model.sr.step(small, small, state)
        bicubic = F.interpolate(small, scale_factor=2, mode="bicubic", align_corners=False)[0]
        real8, big8 = to8(real), to8(big[0])
        tiles = [to8(bicubic)]
        scores = {"bicubic": round(psnr(tiles[0], real8), 2)}
        for label, strength in STRENGTHS:
            shown = present(device, shader, big8, strength)
            tiles.append(shown)
            scores[label] = round(psnr(shown, real8), 2)
        tiles.append(real8)
        crop = lambda t: t[s // 4:s // 4 + 192, s // 4:s // 4 + 192]
        strip = np.concatenate([np.kron(crop(t), np.ones((2, 2, 1), np.uint8)) for t in tiles], 1)
        Image.fromarray(strip).save(out_dir / f"sharpen-{name}.png")
        print(json.dumps({"frame": name, "psnr": scores}), flush=True)


if __name__ == "__main__":
    main()
