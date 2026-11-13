"""Where does fine detail go? For the validation windows of joint.py (REDS and the games kept for
validation, centre 512, JPEG 60), with and without rain or snow:

- detail kept by each checkpoint: mean |Laplacian| of the shown frame over that of the real frame,
  on the most detailed quarter of the picture (where a distant background with fine texture is),
  for the upscaled key frame and the in-between frame;
- how much the present shader's sharpening is turned down by the mismatch test, on that same
  detailed quarter (should stay near 1 on clean footage) and on the pixels with rain or snow drawn
  on them (should go down), for the current test and for candidate replacements.

Usage: python diag_detail.py <data dir> <checkpoint.pt> [<checkpoint.pt> ...]
The mismatch test always uses the motion of the last checkpoint given.
"""
import pathlib
import random
import sys

import numpy as np
import torch
import torch.nn.functional as F

import interp
import joint
import weather

LUMA = torch.tensor([0.299, 0.587, 0.114]).view(1, 3, 1, 1)


def luma(x):
    return (x * LUMA).sum(1, keepdim=True)


def laplacian(x):
    k = torch.tensor([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=torch.float32).view(1, 1, 3, 3)
    return F.conv2d(F.pad(luma(x), (1, 1, 1, 1), mode="replicate"), k).abs()


def local_range(x):
    """max - min of the luma over the pixel and its 4 neighbours, as the shader computes it."""
    y = F.pad(luma(x), (1, 1, 1, 1), mode="replicate")
    stack = torch.stack([y[..., 1:-1, 1:-1], y[..., :-2, 1:-1], y[..., 2:, 1:-1], y[..., 1:-1, :-2], y[..., 1:-1, 2:]])
    return stack.max(0).values - stack.min(0).values


def warped_pair(a, b, motion, t=0.5):
    """The two frames pulled to instant t, as PRESENT_SHADER's mismatch() samples them."""
    n, _, h, w = a.shape
    f = F.interpolate(motion[:, :4], size=(h, w), mode="bilinear", align_corners=False)
    grid = torch.tensor([motion.shape[-1], motion.shape[-2]], dtype=a.dtype).view(1, 2, 1, 1)
    f01, f10 = f[:, 0:2] / grid, f[:, 2:4] / grid
    ft0 = -(1 - t) * t * f01 + t * t * f10
    ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10
    return interp.warp(a, ft0), interp.warp(b, ft1)


def neighbour_max(m):
    p = F.pad(m, (1, 1, 1, 1), mode="replicate")
    return torch.stack([p[..., 1:-1, 1:-1], p[..., :-2, 1:-1], p[..., 2:, 1:-1], p[..., 1:-1, :-2], p[..., 1:-1, 2:]]).max(0).values


def smoothstep(e0, e1, x):
    t = ((x - e0) / (e1 - e0)).clamp(0, 1)
    return t * t * (3 - 2 * t)


def box(x, r):
    return F.avg_pool2d(F.pad(x, (r, r, r, r), mode="replicate"), 2 * r + 1, 1)


def shifted(img, dx, dy):
    """img sampled at (x + dx, y + dy) pixels, bilinear, clamped: one bilinear tap of the shader."""
    n, _, h, w = img.shape
    ys = (torch.arange(h, dtype=torch.float32) + 0.5 + dy) / h * 2 - 1
    xs = (torch.arange(w, dtype=torch.float32) + 0.5 + dx) / w * 2 - 1
    gy, gx = torch.meshgrid(ys, xs, indexing="ij")
    grid = torch.stack([gx, gy], -1)[None].expand(n, h, w, 2)
    return F.grid_sample(img, grid, mode="bilinear", padding_mode="border", align_corners=False)


def four_tap(x, y):
    """What the shader can afford: four bilinear taps 1.5 texels away diagonally on each warped
    frame (about a 4 x 4 average), the difference of their means against their spread."""
    taps_x = torch.stack([luma(shifted(x, dx, dy)) for dx in (-1.5, 1.5) for dy in (-1.5, 1.5)])
    taps_y = torch.stack([luma(shifted(y, dx, dy)) for dx in (-1.5, 1.5) for dy in (-1.5, 1.5)])
    diff = (taps_x.mean(0) - taps_y.mean(0)).abs()
    spread = ((taps_x.max(0).values - taps_x.min(0).values) + (taps_y.max(0).values - taps_y.min(0).values)) / 2
    return diff, spread


def gates(x, y):
    """Sharpening factor (1 = untouched) for each candidate mismatch test."""
    out = {}
    diff, spread = four_tap(x, y)
    for floor in (0.02, 0.04):
        for low, high in ((0.5, 1.2), (0.8, 2.0), (1.0, 2.5)):
            out[f"4tap_f{floor}_{low}-{high}"] = 1 - smoothstep(low, high, diff / (spread + floor))
    miss = (luma(x) - luma(y)).abs()
    out["current"] = 1 - smoothstep(0.03, 0.12, neighbour_max(miss))
    for r in (1, 2, 3):
        blurred = (luma(box(x, r)) - luma(box(y, r))).abs()
        if r < 3:
            out[f"blur{r}"] = 1 - smoothstep(0.03, 0.12, neighbour_max(blurred))
        # relative to how much the picture varies there: subpixel misalignment of a sharp texture
        # gives a difference of the order of its own contrast; a drop that is in one frame and
        # not in the other gives much more than the blurred contrast of the other frame
        contrast = (box(local_range(x), r) + box(local_range(y), r)) / 2
        relative = neighbour_max(blurred) / (contrast + 0.02)
        for low, high in ((0.6, 1.5), (0.8, 2.0), (1.0, 2.5)):
            if r > 1:
                out[f"blur{r}_rel{low}-{high}"] = 1 - smoothstep(low, high, relative)
    return out


def model_from(path):
    saved = torch.load(path, map_location="cpu")
    shape = saved["shape"]
    fi = shape["fi"]
    model = joint.Joint(shape["sr"]["channels"], shape["sr"]["blocks"],
                        ",".join(str(fi[k]) for k in ("c1", "c2", "b1", "b2", "b3", "bu")),
                        aligned=shape["sr"].get("aligned", False))
    model.load_state_dict(saved["model"])
    return model.eval()


@torch.no_grad()
def main():
    torch.set_num_threads(8)
    data = pathlib.Path(sys.argv[1])
    paths = sys.argv[2:]
    models = [(pathlib.Path(p).parent.name, model_from(p)) for p in paths]
    joint.set_keys(4)
    gap, span = 2, joint.SPANS[2]
    sources = []
    for root in sorted(p for p in (data / "orig" / "val").iterdir() if p.is_dir())[:3]:
        names = sorted(root.glob("*.png"))
        sources.append(("reds", lambda s, n, names=names: torch.stack([interp.load(names[s + k]) for k in range(n)]), len(names), set()))
    for path in interp.packed(data / "packed120" / "games-val"):
        clip, cuts = np.load(path, mmap_mode="r"), interp.cuts_of(path)
        sources.append(("games", lambda s, n, clip=clip: torch.from_numpy(np.array(clip[s:s + n])).permute(0, 3, 1, 2).float() / 255, len(clip), cuts))
    detail = {}
    gate = {}
    for index, (kind, read, count, cuts) in enumerate(sources):
        starts = interp.valid_starts(count, cuts, span)
        for number, start in enumerate([starts[int(i)] for i in np.linspace(0, len(starts) - 1, 6)]):
            clean = joint._center(read(start, span + 1), 512)
            sky = "rain" if number % 2 == 0 else "snow"
            for variant, frames in ((kind, clean), (sky, weather.apply(clean.clone(), random.Random(1000 * index + number), sky))):
                keys = frames[[k * gap for k in range(joint.KEYS)]]
                small = joint.degrade(keys, 60)[None]
                real_key, real_mid = keys[-1:], frames[(joint.KEYS - 2) * gap + gap // 2][None]
                # the most detailed quarter of the real key frame
                lap_real = laplacian(real_key)
                busy = lap_real >= lap_real.flatten().quantile(0.75)
                particles = (luma(frames[(joint.KEYS - 2) * gap:]) - luma(clean[(joint.KEYS - 2) * gap:])).abs().amax(0, keepdim=True) > 0.03
                bicubic = F.interpolate(small[0], scale_factor=2, mode="bicubic", align_corners=False).clamp(0, 1)
                ratio = lambda shown, real, mask: (laplacian(shown)[mask].mean() / laplacian(real)[mask].mean()).item()
                detail.setdefault((variant, "bicubic", "key"), []).append(ratio(bicubic[-1:], real_key, busy))
                for name, model in models:
                    bigs, mids, motion = model(small, torch.tensor([[0.5]]))
                    detail.setdefault((variant, name, "key"), []).append(ratio(bigs[:, -1], real_key, busy))
                    detail.setdefault((variant, name, "mid"), []).append(ratio(mids[:, 0], real_mid, busy))
                x, y = warped_pair(bigs[:, -2], bigs[:, -1], motion)
                for test, g in gates(x, y).items():
                    if variant in ("reds", "games"):
                        gate.setdefault((variant, test, "detailed quarter"), []).append(g[busy].mean().item())
                    elif particles.any():
                        gate.setdefault((variant, test, "on particles"), []).append(g[particles].mean().item())
                        gate.setdefault((variant, test, "detailed quarter"), []).append(g[busy & ~particles].mean().item())
    print("== detail kept on the most detailed quarter (shown / real, 1 = all of it)")
    for key in sorted(detail):
        print(" ", key, round(float(np.mean(detail[key])), 3))
    print("== sharpening left by the mismatch test (1 = untouched)")
    for key in sorted(gate):
        print(" ", key, round(float(np.mean(gate[key])), 3))


if __name__ == "__main__":
    main()
