"""Rain and snow drawn over training patches, so the networks learn what a stream shows in bad
weather: many small things moving fast, each on its own, in no way tied to the camera. Without it
the motion network has never seen them, the aligned upscaler carries the previous frame onto drops
that are no longer there, and the upscaled picture shimmers.

Every particle has its own position, speed and direction (a shared wind plus some spread), and
snow flakes also sway sideways. Each one is drawn on every source frame at the place it has at
that instant, so the in-between frames used as targets stay exact. Rain drops are drawn as the
streak they leave during the exposure; flakes as soft dots. A frame has one to three depth layers:
far ones small, slow and faint, near ones large, fast and blurred. A light haze can go with them.

Also here: sensor grain for the captured frames (added before the codec, never to the targets), so
the upscaler learns to leave grain alone instead of sharpening it.

Nothing is taken from anywhere: all of it is random numbers.

Usage from joint.py: apply(frames, rng) where frames is [T, 3, P, P] in 0..1 (consecutive frames at
120 fps) and rng is a random.Random (or the random module); grain(small, rng) for captured frames.
python weather.py <output prefix> [count]   writes strips to check the look by eye.
"""
import math

import torch
import torch.nn.functional as F


def splat(points, weights, height, width):
    """Bilinear splat of points [N, 2] (x, y in pixels, pixel centres at +0.5) with weights [N]
    into a [height, width] map."""
    x = points[:, 0] - 0.5
    y = points[:, 1] - 0.5
    x0, y0 = x.floor(), y.floor()
    fx, fy = x - x0, y - y0
    out = torch.zeros(height * width)
    for dx, dy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        xi, yi = (x0 + dx).long(), (y0 + dy).long()
        inside = (xi >= 0) & (xi < width) & (yi >= 0) & (yi < height)
        out.index_add_(0, (yi * width + xi)[inside], (w * weights)[inside])
    return out.view(height, width)


def blur(maps, sigma):
    """Gaussian blur of [T, H, W] maps with a kernel whose peak is 1, so a dot keeps its brightness
    when it is spread into a larger, softer one."""
    if sigma < 0.45:
        return maps
    radius = max(1, int(math.ceil(sigma * 2.5)))
    xs = torch.arange(-radius, radius + 1, dtype=torch.float32)
    kernel = torch.exp(-xs ** 2 / (2 * sigma ** 2))
    x = maps[:, None]
    x = F.conv2d(F.pad(x, (radius, radius, 0, 0), mode="replicate"), kernel.view(1, 1, 1, -1))
    x = F.conv2d(F.pad(x, (0, 0, radius, radius), mode="replicate"), kernel.view(1, 1, -1, 1))
    return x[:, 0]


def layer(count, size, rng, kind, depth):
    """One depth layer (0 far .. 1 near) of rain or snow over `count` frames: [T, H, W] opacity and
    its colour [3]."""
    if kind == "rain":
        speed = rng.uniform(4, 14) + depth * rng.uniform(6, 30)        # pixels per 120 fps frame
        angle = math.radians(rng.uniform(-25, 25))                       # from straight down
        spread_angle, spread_speed = math.radians(4), 0.15
        exposure = rng.uniform(0.3, 2.0)                                 # in 120 fps frames: up to a 1/60 shutter
        density = rng.uniform(40, 350) * (1.3 - depth)                  # particles per 256 x 256
        alpha = rng.uniform(0.12, 0.45) * (0.6 + 0.6 * depth)
        sigma = 0.3 + depth * rng.uniform(0.2, 1.4)
        sway = 0.0
        tint = rng.uniform(0.7, 1.0)
        colour = torch.tensor([tint * rng.uniform(0.9, 1.0), tint * rng.uniform(0.93, 1.0), tint])
    else:
        speed = rng.uniform(0.2, 1.5) + depth * rng.uniform(0.5, 5)
        angle = math.radians(rng.uniform(-40, 40))
        spread_angle, spread_speed = math.radians(25), 0.35
        exposure = rng.uniform(0.0, 1.0)
        density = rng.uniform(40, 600) * (1.3 - depth)
        alpha = rng.uniform(0.5, 0.95)
        sigma = 0.35 + depth * rng.uniform(0.4, 3.0)
        sway = rng.uniform(0, 3) * (0.5 + depth)
        tint = rng.uniform(0.85, 1.0)
        colour = torch.tensor([tint, tint, min(1.0, tint * 1.03)])
    if rng.random() < 0.5:
        angle = -angle
    # particles live on a box a margin larger than the patch and wrap around it: one leaving at the
    # bottom comes back at the top, out of sight, so the density stays even at any speed
    margin = speed * 1.4 * exposure + sway + 4 * sigma + 4
    box = size + 2 * margin
    n = max(1, int(density * box ** 2 / 256 ** 2))
    seed = rng.randrange(1 << 30)
    g = torch.Generator().manual_seed(seed)
    start = torch.rand(n, 2, generator=g) * box
    speeds = speed * (1 + spread_speed * (torch.rand(n, generator=g) * 2 - 1))
    angles = angle + spread_angle * (torch.rand(n, generator=g) * 2 - 1)
    velocity = torch.stack([torch.sin(angles), torch.cos(angles)], 1) * speeds[:, None]
    phase = torch.rand(n, generator=g) * 2 * math.pi
    period = 40 + torch.rand(n, generator=g) * 160                      # frames per sway
    brightness = 0.6 + 0.4 * torch.rand(n, generator=g)
    length = (speeds * exposure).max().item()
    samples = max(1, int(math.ceil(length / 0.5)) + 1)                  # one dot every half pixel along the streak
    s = torch.linspace(0, 1, samples) * exposure                       # time back from the frame instant
    maps = []
    for k in range(count):
        when = k - s                                                    # [S]
        pos = start[:, None, :] + velocity[:, None, :] * when[None, :, None]
        if sway:
            pos[..., 0] += sway * torch.sin(2 * math.pi * when[None, :] / period[:, None] + phase[:, None])
        # wrap the head of each particle and keep its streak attached to it
        head = pos[:, :1, :]
        pos = pos - head + (torch.remainder(head, box) - margin)
        # the dots of a streak add up to the same opacity per pixel, whatever its length
        weight = (brightness * torch.clamp(speeds * exposure, min=1.0) / samples)[:, None].expand(n, samples)
        maps.append(splat(pos.reshape(-1, 2), weight.reshape(-1), size, size))
    maps = blur(torch.stack(maps), sigma)
    return (maps * alpha).clamp(0, 0.95), colour


def apply(frames, rng, kind=None):
    """Draws rain or snow onto frames [T, 3, P, P] in place and returns them."""
    count, _, height, width = frames.shape
    size = max(height, width)
    kind = kind or ("rain" if rng.random() < 0.55 else "snow")
    if rng.random() < 0.4:
        # haze: the far rain or snow too dense to see one by one
        amount = rng.uniform(0.03, 0.18)
        grey = rng.uniform(0.55, 0.9)
        frames.mul_(1 - amount).add_(grey * amount)
    layers = rng.randint(1, 3)
    depths = sorted(rng.uniform(0, 1) for _ in range(layers))
    for depth in depths:
        opacity, colour = layer(count, size, rng, kind, depth)
        opacity = opacity[:, None, :height, :width]
        frames.mul_(1 - opacity).add_(colour.view(1, 3, 1, 1) * opacity)
    return frames.clamp_(0, 1)


def grain(small, rng):
    """Sensor grain on captured frames [N, 3, h, w] in 0..1: new noise every frame, mostly in the
    brightness, a little in the colour, sometimes slightly clumped."""
    sigma = rng.uniform(0.006, 0.035)
    g = torch.Generator().manual_seed(rng.randrange(1 << 30))
    luma = torch.randn(small.shape[0], 1, *small.shape[2:], generator=g) * sigma
    chroma = torch.randn(small.shape, generator=g) * sigma * rng.uniform(0, 0.5)
    noise = luma + chroma
    if rng.random() < 0.4:
        noise = F.avg_pool2d(F.pad(noise, (1, 1, 1, 1), mode="replicate"), 3, 1) * 2
    # less noise in the darkest and brightest parts, as a sensor after its tone curve
    level = small.mean(1, keepdim=True)
    shape = 0.4 + 2.4 * level * (1 - level)
    return (small + noise * shape).clamp(0, 1)


def preview(prefix, seed, size=256, count=9):
    import random
    rng = random.Random(seed)
    xs = torch.linspace(0, 1, size)
    base = (0.15 + 0.5 * xs.view(1, size) * xs.view(size, 1)).expand(count, 3, size, size).clone()
    kind = "rain" if seed % 2 == 0 else "snow"
    out = apply(base, rng, kind)
    strip = (out[::2].permute(2, 0, 3, 1).reshape(size, -1, 3) * 255).byte().numpy()
    from PIL import Image
    Image.fromarray(strip).save(f"{prefix}-{kind}-{seed}.png")


if __name__ == "__main__":
    import sys
    for seed in range(int(sys.argv[2]) if len(sys.argv) > 2 else 4):
        preview(sys.argv[1], seed)
