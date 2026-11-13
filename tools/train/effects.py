"""Game effects and moving vegetation drawn over training patches: what makes a stream "noisy"
besides rain and snow, and what a motion network trained on streets and plain game footage gets
wrong.

- sparks: bright embers and sparks, added to the light of the scene (not painted over it), thrown
  out and falling under gravity, each with its own life, flicker and a streak while it moves fast.
- smoke: half-transparent smoke, fog or fire glow drifting over the picture with its own motion,
  made of a few layers of soft noise that slide at different speeds so it also changes shape.
- flash: a muzzle flash or an explosion lighting the picture for one to a few frames, from a point.
- foliage: grass blades rooted in place and swaying, each with its own phase, plus gusts of wind;
  or a patch of the picture itself rippling like leaves in the wind.

As in weather.py, every element is drawn on each source frame where it is at that instant, so the
in-between frames used as targets stay exact. Nothing is taken from anywhere: random numbers only.

Usage from joint.py: apply(frames, rng, kind=None) with frames [T, 3, P, P] in 0..1 (consecutive
frames at 120 fps). python effects.py <output prefix> [count] writes strips to check by eye.
"""
import math

import torch
import torch.nn.functional as F

from weather import blur, splat

KINDS = ["sparks", "smoke", "flash", "foliage"]


def _gen(rng):
    return torch.Generator().manual_seed(rng.randrange(1 << 30))


def sparks(frames, rng):
    count, _, h, w = frames.shape
    size = max(h, w)
    g = _gen(rng)
    n = rng.randint(15, 250)
    warm = rng.random() < 0.7
    colour = torch.tensor([1.0, rng.uniform(0.45, 0.85), rng.uniform(0.1, 0.4)]) if warm else \
        torch.tensor([rng.uniform(0.5, 0.9), rng.uniform(0.7, 1.0), 1.0])
    # thrown from a few sources, or falling from all over
    sources = torch.rand(rng.randint(1, 3), 2, generator=g) * size
    pick = torch.randint(0, sources.shape[0], (n,), generator=g)
    start = sources[pick] + torch.randn(n, 2, generator=g) * size * rng.uniform(0.02, 0.3)
    speed = rng.uniform(1, 12)
    angle = torch.rand(n, generator=g) * 2 * math.pi
    velocity = torch.stack([torch.cos(angle), torch.sin(angle)], 1) * speed * (0.3 + torch.rand(n, 1, generator=g))
    gravity = rng.uniform(0, 0.25)                                       # pixels per frame per frame
    birth = (torch.rand(n, generator=g) * 2 - 1.2) * count                # some already alive, some born later
    life = count * (0.2 + 2 * torch.rand(n, generator=g))
    flicker = rng.uniform(0, 0.8)
    rate = 0.2 + torch.rand(n, generator=g) * 1.2                        # radians per frame
    phase = torch.rand(n, generator=g) * 2 * math.pi
    brightness = rng.uniform(0.5, 1.6) * (0.4 + torch.rand(n, generator=g))
    exposure = rng.uniform(0.3, 2.0)
    samples = max(2, int(speed * 1.3 * exposure / 0.5) + 2)
    s = torch.linspace(0, 1, samples) * exposure
    light = []
    for k in range(count):
        when = k - s                                                    # [S]
        age = when[None, :] - birth[:, None]                           # [N, S]
        pos = start[:, None, :] + velocity[:, None, :] * age[..., None]
        pos[..., 1] += 0.5 * gravity * age.clamp(min=0) ** 2
        alive = (age >= 0) & (age <= life[:, None])
        fade = (1 - age / life[:, None]).clamp(0, 1)
        shine = brightness[:, None] * fade * (1 + flicker * torch.sin(rate[:, None] * when[None, :] + phase[:, None]))
        weight = torch.where(alive, shine, torch.zeros(())) / samples * torch.clamp(velocity.norm(dim=1, keepdim=True) * exposure, min=1.0)
        light.append(splat(pos.reshape(-1, 2), weight.reshape(-1), size, size))
    light = torch.stack(light)
    core = blur(light, rng.uniform(0.3, 0.8))
    glow = blur(light, rng.uniform(2, 5)) * rng.uniform(0, 0.25)
    add = (core + glow)[:, None, :h, :w] * colour.view(1, 3, 1, 1)
    frames.add_(add)


def _noise(g, size, cells):
    """Soft value noise [size, size] in about 0..1, from a cells x cells grid, tileable."""
    grid = torch.rand(1, 1, cells, cells, generator=g)
    grid = torch.cat([grid, grid[..., :1, :]], 2)
    grid = torch.cat([grid, grid[..., :, :1]], 3)
    return F.interpolate(grid, size=(size + size // cells, size + size // cells), mode="bicubic", align_corners=True)[0, 0, :size, :size]


def _slide(field, dx, dy):
    """A tileable field moved by a fractional dx, dy (wrapping), bilinear."""
    ix, iy = math.floor(dx), math.floor(dy)
    fx, fy = dx - ix, dy - iy
    rolled = lambda sx, sy: torch.roll(field, shifts=(sy, sx), dims=(0, 1))
    top = rolled(ix, iy) * (1 - fx) + rolled(ix + 1, iy) * fx
    bottom = rolled(ix, iy + 1) * (1 - fx) + rolled(ix + 1, iy + 1) * fx
    return top * (1 - fy) + bottom * fy


def smoke(frames, rng):
    count, _, h, w = frames.shape
    size = max(h, w)
    g = _gen(rng)
    fire = rng.random() < 0.25
    base = torch.tensor([1.0, rng.uniform(0.35, 0.6), rng.uniform(0.05, 0.2)]) if fire else \
        torch.full((3,), rng.choice([rng.uniform(0.05, 0.25), rng.uniform(0.5, 0.95)]))
    opacity = rng.uniform(0.4, 0.9)
    drift = (rng.uniform(-2, 2), rng.uniform(-2.5, 1) if not fire else rng.uniform(-4, -0.5))
    octaves = []
    for cells, weight in ((rng.randint(2, 4), 0.55), (rng.randint(5, 9), 0.3), (rng.randint(10, 18), 0.15)):
        speed = rng.uniform(0.6, 1.6)
        octaves.append((_noise(g, size, cells), weight, drift[0] * speed + rng.uniform(-0.5, 0.5), drift[1] * speed + rng.uniform(-0.5, 0.5)))
    # where the smoke is: a soft region, or everywhere (fog)
    if rng.random() < 0.6:
        cy, cx = rng.uniform(0.2, 0.8) * size, rng.uniform(0.2, 0.8) * size
        radius = rng.uniform(0.25, 0.7) * size
        yy, xx = torch.meshgrid(torch.arange(size, dtype=torch.float32), torch.arange(size, dtype=torch.float32), indexing="ij")
        region = torch.exp(-(((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * radius ** 2)))
    else:
        region = torch.ones(size, size)
    threshold = rng.uniform(0.3, 0.6)
    for k in range(count):
        density = sum(weight * _slide(field, dx * k, dy * k) for field, weight, dx, dy in octaves)
        # the sum of octaves is flatter than each one: stretch it back to about 0..1
        density = ((density - 0.5) * 2.6 + 0.5).clamp(0, 1)
        alpha = ((density - threshold) / (1 - threshold)).clamp(0, 1) * region * opacity
        alpha = alpha[None, :h, :w]
        if fire:
            frames[k].add_(alpha * base.view(3, 1, 1) * 1.3)
        else:
            frames[k].mul_(1 - alpha).add_(base.view(3, 1, 1) * alpha)


def flash(frames, rng):
    count, _, h, w = frames.shape
    peak = rng.uniform(0, count - 1)
    width = rng.uniform(0.4, 3.0)                                      # frames
    strength = rng.uniform(0.15, 0.9)
    colour = torch.tensor([1.0, rng.uniform(0.75, 1.0), rng.uniform(0.4, 0.9)])
    cy, cx = rng.uniform(0, h), rng.uniform(0, w)
    radius = rng.uniform(0.1, 1.2) * max(h, w)
    yy, xx = torch.meshgrid(torch.arange(h, dtype=torch.float32), torch.arange(w, dtype=torch.float32), indexing="ij")
    shape = torch.exp(-(((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * radius ** 2)))
    for k in range(count):
        pulse = math.exp(-((k - peak) ** 2) / (2 * width ** 2)) * strength
        if pulse > 1e-3:
            # light adds to the scene in proportion to what is there, plus a little on its own
            frames[k].add_((frames[k] * 0.8 + 0.2) * shape * pulse * colour.view(3, 1, 1))


def foliage(frames, rng):
    if rng.random() < 0.6:
        grass(frames, rng)
    else:
        ripple(frames, rng)


def grass(frames, rng):
    """Blades rooted in a field that covers part of the patch, swaying with their own phase."""
    count, _, h, w = frames.shape
    size = max(h, w)
    g = _gen(rng)
    top = rng.uniform(0.0, 0.7) * size                                # the field fills the patch below this line
    n = int(rng.uniform(600, 3000) * (size - top) / size)
    root = torch.stack([torch.rand(n, generator=g) * (size + 20) - 10,
                        top + torch.rand(n, generator=g) * (size - top + 30)], 1)
    length = rng.uniform(6, 40) * (0.5 + torch.rand(n, generator=g))
    lean = (torch.rand(n, generator=g) * 2 - 1) * 0.4 + rng.uniform(-0.4, 0.4)   # radians from upright
    amplitude = rng.uniform(0.05, 0.45) * (0.5 + torch.rand(n, generator=g))
    rate = rng.uniform(0.03, 0.25) * (0.7 + 0.6 * torch.rand(n, generator=g))     # radians per frame
    phase = root[:, 0] * rng.uniform(0.0, 0.08) + torch.rand(n, generator=g) * rng.uniform(0.5, 6.3)
    gust = rng.uniform(0, 0.3)
    hue = rng.random()
    shade = 0.5 + 0.5 * torch.rand(n, generator=g)
    tint = torch.tensor([0.25 + 0.4 * hue, 0.45 + 0.25 * hue, 0.08 + 0.1 * hue])
    # the ground under the blades: darker, so the field reads as one surface
    ground = tint * rng.uniform(0.3, 0.6)
    cover = rng.uniform(0.5, 0.95)
    yy = torch.arange(h, dtype=torch.float32).view(h, 1)
    edge = ((yy - top) / 8).clamp(0, 1)[None]
    samples = int(length.max().item() / 0.6) + 2                        # a dot every 0.6 pixel or less
    s = torch.linspace(0, 1, samples)
    colours = (tint[None, :] * shade[:, None])                          # [N, 3]
    for k in range(count):
        frames[k].mul_(1 - edge * cover).add_(ground.view(3, 1, 1) * edge * cover)
        sway = lean + amplitude * torch.sin(rate * k + phase) + gust * math.sin(0.05 * k + 1.3)
        # a blade bends more towards its tip
        bend = sway[:, None] * s[None, :] ** 1.5
        dx = torch.cumsum(torch.sin(bend), 1) / samples * length[:, None]
        dy = -torch.cumsum(torch.cos(bend), 1) / samples * length[:, None]
        pos = torch.stack([root[:, None, 0] + dx, root[:, None, 1] + dy], -1).reshape(-1, 2)
        layer = []
        for c in range(3):
            weight = (colours[:, c:c + 1] * (0.6 + 0.4 * s[None, :])).expand(n, samples).reshape(-1)
            layer.append(splat(pos, weight * length.repeat_interleave(samples) / samples * 1.2, size, size))
        cover_map = splat(pos, (length[:, None] / samples * 1.2).expand(n, samples).reshape(-1), size, size)
        alpha = cover_map.clamp(0, 1)[None, :h, :w]
        paint = torch.stack(layer)[:, :h, :w] / cover_map.clamp(min=1e-3)[None, :h, :w]
        frames[k].mul_(1 - alpha).add_(paint.clamp(0, 1) * alpha)


def ripple(frames, rng):
    """A patch of the picture moving like leaves in the wind: a smooth displacement field that
    swings back and forth, out of step from place to place."""
    count, _, h, w = frames.shape
    size = max(h, w)
    g = _gen(rng)
    amplitude = rng.uniform(0.5, 4.0)                                  # pixels
    rate = rng.uniform(0.04, 0.3)                                      # radians per frame
    phase = _noise(g, size, rng.randint(3, 10))[:h, :w] * rng.uniform(3, 12)
    direction = _noise(g, size, rng.randint(2, 6))[:h, :w] * 2 * math.pi
    mask = (_noise(g, size, rng.randint(2, 5))[:h, :w] - rng.uniform(0.2, 0.5)).clamp(0, 1)
    mask = (mask / mask.max().clamp(min=1e-3)).clamp(0, 1)
    yy, xx = torch.meshgrid(torch.arange(h, dtype=torch.float32), torch.arange(w, dtype=torch.float32), indexing="ij")
    for k in range(count):
        swing = amplitude * mask * torch.sin(rate * k + phase)
        sx, sy = xx + swing * torch.cos(direction), yy + swing * torch.sin(direction)
        grid = torch.stack([(sx + 0.5) / w * 2 - 1, (sy + 0.5) / h * 2 - 1], -1)[None]
        frames[k] = F.grid_sample(frames[k][None], grid, mode="bilinear", padding_mode="border", align_corners=False)[0]


def apply(frames, rng, kind=None):
    """Draws one effect onto frames [T, 3, P, P] in place and returns them."""
    kind = kind or rng.choice(KINDS)
    {"sparks": sparks, "smoke": smoke, "flash": flash, "foliage": foliage}[kind](frames, rng)
    return frames.clamp_(0, 1)


def preview(prefix, seed, size=256, count=9):
    import random
    rng = random.Random(seed)
    xs = torch.linspace(0, 1, size)
    checker = ((torch.arange(size).view(1, size) // 16 + torch.arange(size).view(size, 1) // 16) % 2).float()
    base = (0.2 + 0.35 * xs.view(1, size) * xs.view(size, 1) + 0.15 * checker).expand(count, 3, size, size).clone()
    kind = KINDS[seed % len(KINDS)]
    out = apply(base, rng, kind)
    strip = (out[::2].permute(2, 0, 3, 1).reshape(size, -1, 3) * 255).byte().numpy()
    from PIL import Image
    Image.fromarray(strip).save(f"{prefix}-{kind}-{seed}.png")


if __name__ == "__main__":
    import sys
    for seed in range(int(sys.argv[2]) if len(sys.argv) > 2 else 8):
        preview(sys.argv[1], seed)
