"""Tries the possible readings of the WebSR weight layout on the demo image and prints how far each one
is from the reference, to find the one that matches.
"""
import itertools
import json
import pathlib
import sys

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

d = pathlib.Path(sys.argv[1])
L = json.load(open(d / "demo-anime4k-cnn-2x-s.json"))["layers"]
image = np.asarray(Image.open(d / "demo-test.png").convert("RGB"), dtype=np.float32) / 255
reference = torch.from_numpy(np.asarray(Image.open(d / "demo-tf-pred.png").convert("RGB"), dtype=np.float32) / 255).permute(2, 0, 1)[None]
x = torch.from_numpy(image).permute(2, 0, 1)[None]


def run(transpose, x_major, base_mode, shuffle_swap, alpha, pad):
    taps = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    if not x_major:
        taps = [(b, a) for a, b in taps]

    def m(values, count):
        t = torch.tensor(values, dtype=torch.float32).view(count, 4, 4)
        return t.transpose(1, 2) if transpose else t

    def conv(inputs, layer):
        count = len(inputs)
        mm = m(layer["weights"], 9 * count)
        w = torch.zeros(4, 4 * count, 3, 3)
        for p in range(count):
            for k, (dx, dy) in enumerate(taps):
                w[:, p * 4:(p + 1) * 4, dy + 1, dx + 1] = mm[p * 9 + k]
        return F.conv2d(F.pad(torch.cat(inputs, 1), (1, 1, 1, 1), mode=pad), w, torch.tensor(layer["bias"]))

    rgba = torch.cat([x, torch.full_like(x[:, :1], alpha)], 1)
    h = conv([rgba], L["conv2d_tf"])
    for n in ("conv2d_1_tf", "conv2d_2_tf", "conv2d_last_tf"):
        h = conv([F.relu(h), F.relu(-h)], L[n])
    if shuffle_swap:
        h = h[:, [0, 2, 1, 3]]
    residual = F.pixel_shuffle(h, 2)
    if base_mode == "bilinear":
        base = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)
    elif base_mode == "bicubic":
        base = F.interpolate(x, scale_factor=2, mode="bicubic", align_corners=False)
    else:
        base = F.interpolate(x, scale_factor=2, mode="nearest")
    return (base + residual).clamp(0, 1)


results = []
with torch.no_grad():
    for combo in itertools.product([True, False], [True, False], ["bilinear", "bicubic", "nearest"], [False, True], [1.0, 0.0], ["replicate", "constant"]):
        y = run(*combo)
        diff = (y - reference).abs()[:, :, 4:-4, 4:-4]
        results.append((diff.mean().item() * 255, diff.max().item() * 255, combo))
for mean, mx, combo in sorted(results)[:8]:
    print(f"mean {mean:.2f}  max {mx:.1f}  transpose={combo[0]} x_major={combo[1]} base={combo[2]} swap={combo[3]} alpha={combo[4]} pad={combo[5]}")
