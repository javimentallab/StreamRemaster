"""Degradations of a real stream, written for StreamRemaster (the idea of two rounds of blur, resize,
noise and compression comes from the Real-ESRGAN paper; nothing of its code or weights is used).

A frame that reaches the viewer was first captured or produced (a lens or a renderer's blur, a
resize, sensor noise, a first compression: the streamer's encoder) and then went through the
platform (another resize to the size sent out, a bit more blur and noise, a second compression:
the video codec the viewer decodes). Trained on that, the upscaler learns to clean the compression
before it adds detail, instead of taking blocks and noise for detail and sharpening them.

degrade(frames, rng, fps) takes clean [N, 3, H, W] frames in 0..1 (H and W even) and returns
[N, 3, H/2, W/2]. The settings are drawn once per window (a stream keeps them); the noise is
drawn for every frame.
"""
import io
import math
import random

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

import streamcodec


def blur_kernel(rng, sigma_range, size_range=(7, 21)):
    """An anisotropic Gaussian kernel, turned by a random angle; sometimes a box-like one."""
    size = rng.randrange(size_range[0], size_range[1] + 1, 2)
    sx = rng.uniform(*sigma_range)
    sy = sx if rng.random() < 0.4 else rng.uniform(*sigma_range)
    theta = rng.uniform(0, math.pi)
    r = torch.arange(size, dtype=torch.float32) - size // 2
    y, x = torch.meshgrid(r, r, indexing="ij")
    c, s = math.cos(theta), math.sin(theta)
    u, v = c * x + s * y, -s * x + c * y
    power = 2.0 if rng.random() < 0.8 else rng.uniform(1.0, 4.0)   # 2 = Gaussian; more = flatter
    k = torch.exp(-0.5 * ((u / sx).abs() ** power + (v / sy).abs() ** power))
    return k / k.sum()


def blur(x, kernel):
    n, c, h, w = x.shape
    pad = kernel.shape[-1] // 2
    if pad >= min(h, w):
        return x
    weight = kernel.to(x)[None, None].repeat(c, 1, 1, 1)
    return F.conv2d(F.pad(x, (pad, pad, pad, pad), mode="reflect"), weight, groups=c)


def resize(x, size, rng):
    down = size[0] < x.shape[-2]
    mode = rng.choice(["area", "bilinear", "bicubic"] if down else ["bilinear", "bicubic"])
    if mode == "area":
        return F.interpolate(x, size=size, mode="area").clamp(0, 1)
    return F.interpolate(x, size=size, mode=mode, antialias=down, align_corners=False).clamp(0, 1)


def noise(x, rng, sigma_range, poisson_range):
    """Gaussian (in colour or the same in all channels) or Poisson-like (stronger in bright areas),
    new for every frame."""
    gen = torch.Generator().manual_seed(rng.randrange(1 << 30))
    gray = rng.random() < 0.4
    shape = (x.shape[0], 1 if gray else 3, *x.shape[-2:])
    if rng.random() < 0.6:
        sigma = rng.uniform(*sigma_range) / 255
        n = torch.randn(shape, generator=gen) * sigma
    else:
        scale = rng.uniform(*poisson_range)
        n = torch.randn(shape, generator=gen) * (x.mean(1, keepdim=True) if gray else x).clamp_min(0).sqrt() * scale / 10
    return (x + n).clamp(0, 1)


def jpeg(x, quality):
    out = []
    for frame in x:
        image = Image.fromarray((frame.permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8))
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=quality, subsampling=2)
        out.append(torch.from_numpy(np.asarray(Image.open(buffer).convert("RGB"), dtype=np.float32).copy()).permute(2, 0, 1) / 255)
    return torch.stack(out)


def degrade(frames, rng=random, fps=60, codec_share=0.75):
    x = frames.float()
    h, w = x.shape[-2:]
    th, tw = h // 2, w // 2

    # 1. the source: blur, a resize around the final size, noise, the streamer's first compression
    if rng.random() < 0.8:
        x = blur(x, blur_kernel(rng, (0.2, 2.0)))
    u = rng.choice([1.0, rng.uniform(0.6, 1.0), rng.uniform(1.0, 1.6)])
    mid = (max(16, round(th * u / 2) * 2), max(16, round(tw * u / 2) * 2))
    x = resize(x, mid, rng)
    if rng.random() < 0.4:
        x = noise(x, rng, (1, 10), (0.05, 1.2))
    if rng.random() < 0.7:
        x = jpeg(x, rng.randint(35, 95))

    # 2. the platform: a lighter blur, the size sent out, a little noise, the codec the viewer decodes
    if rng.random() < 0.5:
        x = blur(x, blur_kernel(rng, (0.2, 1.5), (5, 13)))
    x = resize(x, (th, tw), rng)
    if rng.random() < 0.25:
        x = noise(x, rng, (1, 6), (0.05, 0.6))
    roll = rng.random()
    # the video codecs refuse very small frames (SVT-AV1 wants 64 pixels a side): JPEG there
    if roll < codec_share and min(th, tw) >= 64:
        x = streamcodec.compress(x, streamcodec.random_spec(rng), fps)
    elif roll < codec_share + (1 - codec_share) * 0.8:
        x = jpeg(x, rng.randint(30, 90))
    return x.clamp(0, 1)


if __name__ == "__main__":
    # a quick look: python realistic.py <frame.png> <out.png>  (left the clean half, right degraded x2)
    import sys
    clean = torch.from_numpy(np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.float32).copy()).permute(2, 0, 1)[None] / 255
    clean = clean[..., : clean.shape[-2] // 2 * 2, : clean.shape[-1] // 2 * 2]
    rows = []
    for seed in range(4):
        small = degrade(clean.repeat(2, 1, 1, 1), random.Random(seed))
        rows.append(torch.cat([F.interpolate(clean, scale_factor=0.5, mode="bicubic", antialias=True)[0].clamp(0, 1), small[0]], 2))
    grid = torch.cat(rows, 1)
    Image.fromarray((grid.permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)).save(sys.argv[2])
