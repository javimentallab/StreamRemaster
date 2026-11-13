"""Stream-like layers drawn over training patches, so the interpolation network also learns what a
live stream puts over the picture: text and panels that stay still while the game moves under
them, a chat or a ticker that scrolls at its own speed, a camera box in a corner showing other
footage, and half-transparent logos.

Every layer is drawn on each of the source frames at the position it has at that instant, so the
in-between frames used as targets stay exact: still layers are identical in all frames and
scrolling ones move by the same fraction of a pixel per 120 fps frame.

All the text is made up from random syllables and drawn with fonts installed on the system
(DejaVu or Liberation, both free for any use); nothing comes from real streams.

Usage from interp.py: apply(frames, rng, other) where frames is [T, 3, P, P] in 0..1, rng is a
random.Random (or the random module) and other() returns another [T, 3, P, P] patch.
"""
import functools
import pathlib

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont

FONT_FILES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]
SYLLABLES = ["ka", "lo", "mi", "ne", "ru", "to", "sa", "vi", "de", "po", "xa", "qu", "ber", "tor", "gg", "wp",
             "ez", "jaja", "lol", "si", "no", "ya", "um", "zor", "fi", "el", "an", "ox", "re", "ta"]
TOKENS = ["!!", "?", "...", ":)", ":D", "<3", "+1", "x2", "GG", "OK", "100", "42", "7", "#1", "LVL", "HP", "FPS"]


@functools.lru_cache(maxsize=None)
def fonts():
    found = [path for path in FONT_FILES if pathlib.Path(path).exists()]
    return found or [None]


@functools.lru_cache(maxsize=256)
def font(path, size):
    return ImageFont.truetype(path, size) if path else ImageFont.load_default(size)


def word(rng):
    if rng.random() < 0.15:
        return rng.choice(TOKENS)
    text = "".join(rng.choice(SYLLABLES) for _ in range(rng.randint(1, 3)))
    return text.capitalize() if rng.random() < 0.3 else text


def sentence(rng, words):
    return " ".join(word(rng) for _ in range(words))


def colour(rng, bright=None):
    if bright is None:
        bright = rng.random() < 0.6
    low, high = (150, 255) if bright else (0, 110)
    return tuple(rng.randint(low, high) for _ in range(3))


def rgba(image):
    """PIL RGBA image to a [4, H, W] tensor in 0..1."""
    return torch.from_numpy(np.asarray(image, dtype=np.float32).copy()).permute(2, 0, 1) / 255


def text_block(rng, width, lines, size, chat=False, words=None):
    """A block of text lines, with or without a panel behind, as RGBA."""
    path = rng.choice(fonts())
    face = font(path, size)
    gap = int(size * rng.uniform(1.15, 1.6))
    height = gap * lines + size // 2
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if rng.random() < 0.6:
        alpha = rng.choice([255, rng.randint(90, 230)])
        draw.rectangle([0, 0, width, height], fill=(*colour(rng, bright=False), alpha))
    text_colour = colour(rng, bright=True)
    stroke = rng.choice([0, 0, 1, 2])
    for k in range(lines):
        x = rng.randint(2, 8)
        y = k * gap + size // 4
        if chat:
            name = word(rng) + rng.choice(["", "_", "77", "x"]) + ":"
            draw.text((x, y), name, font=face, fill=(*colour(rng, bright=True), 255), stroke_width=stroke,
                      stroke_fill=(0, 0, 0, 255))
            x += int(draw.textlength(name + " ", font=face))
        draw.text((x, y), sentence(rng, words or rng.randint(1, 6)), font=face, fill=(*text_colour, 255),
                  stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return rgba(image)


def blend(frame, layer, x, y):
    """Draws an RGBA layer onto a [3, H, W] frame at integer x, y, clipped to the frame."""
    _, h, w = frame.shape
    _, lh, lw = layer.shape
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + lw, w), min(y + lh, h)
    if x0 >= x1 or y0 >= y1:
        return
    part = layer[:, y0 - y:y1 - y, x0 - x:x1 - x]
    alpha = part[3:4]
    frame[:, y0:y1, x0:x1] = frame[:, y0:y1, x0:x1] * (1 - alpha) + part[:3] * alpha


def shifted(layer, dx, dy, width, height):
    """The window [0, width) x [0, height) of a layer moved by a fractional dx, dy, bilinear."""
    _, lh, lw = layer.shape
    ys = (torch.arange(height, dtype=torch.float32) + 0.5 - dy) / lh * 2 - 1
    xs = (torch.arange(width, dtype=torch.float32) + 0.5 - dx) / lw * 2 - 1
    grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
    grid = torch.stack([grid_x, grid_y], -1)[None]
    return F.grid_sample(layer[None], grid, mode="bilinear", padding_mode="zeros", align_corners=False)[0]


def still_text(frames, rng):
    size = frames.shape[-1]
    width = rng.randint(size // 4, size)
    layer = text_block(rng, width, rng.randint(1, 4), rng.randint(9, 26))
    x, y = rng.randint(-width // 4, size - width // 2), rng.randint(-8, size - 12)
    for frame in frames:
        blend(frame, layer, x, y)


def scrolling_text(frames, rng):
    """A chat column going up (or a ticker going sideways) by the same fraction of a pixel per frame."""
    count, _, size, _ = frames.shape
    speed = rng.uniform(0.15, 4.0) * rng.choice([1, -1])
    travel = int(abs(speed) * count) + 2
    if rng.random() < 0.7:
        width, height = rng.randint(size // 4, size // 2 + 20), rng.randint(size // 3, size)
        strip = text_block(rng, width, (height + travel) // 14 + 2, rng.randint(9, 18), chat=True)
        start = rng.uniform(0, max(strip.shape[1] - height - travel, 0))
        x, y = rng.randint(-10, size - width // 2), rng.randint(-10, size - height // 2)
        for k, frame in enumerate(frames):
            offset = -(start + travel / 2) + speed * k
            blend(frame, shifted(strip, 0, offset, width, height), x, y)
    else:
        height = rng.randint(14, 34)
        strip = text_block(rng, size * 3, 1, int(height * 0.7), words=size // 6)
        strip = strip[:, :height] if strip.shape[1] >= height else F.pad(strip, (0, 0, 0, height - strip.shape[1]))
        start = rng.uniform(0, size)
        y = rng.randint(0, size - height)
        for k, frame in enumerate(frames):
            blend(frame, shifted(strip, -(start + size / 2) + speed * k, 0, size, height), 0, y)


def camera_box(frames, rng, other):
    """Other footage in a box, still or sliding in slowly, with an optional border."""
    count, _, size, _ = frames.shape
    box = rng.randint(size // 4, size // 2)
    inset = F.interpolate(other, size=(box, box), mode="bilinear", antialias=True, align_corners=False)
    border = rng.choice([0, 0, 1, 2, 3])
    if border:
        frame_colour = torch.tensor(colour(rng), dtype=torch.float32).view(3, 1, 1) / 255
        inset = F.pad(inset, (border,) * 4)
        inset[:, :, :border], inset[:, :, -border:] = frame_colour, frame_colour
        inset[:, :, :, :border], inset[:, :, :, -border:] = frame_colour, frame_colour
    corner = rng.randrange(4)
    x = 4 if corner % 2 == 0 else size - inset.shape[-1] - 4
    y = 4 if corner < 2 else size - inset.shape[-1] - 4
    x, y = x + rng.randint(-20, 20), y + rng.randint(-20, 20)
    alpha = torch.ones(1, *inset.shape[-2:])
    for k, frame in enumerate(frames):
        blend(frame, torch.cat([inset[k], alpha]), x, y)


def logo(frames, rng):
    size = frames.shape[-1]
    side = rng.randint(16, size // 3)
    image = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    alpha = rng.randint(60, 255)
    for _ in range(rng.randint(1, 4)):
        x0, y0 = rng.randint(0, side // 2), rng.randint(0, side // 2)
        shape = [x0, y0, rng.randint(x0 + side // 3, side), rng.randint(y0 + side // 3, side)]
        fill = (*colour(rng), alpha)
        if rng.random() < 0.5:
            draw.ellipse(shape, fill=fill)
        else:
            draw.rectangle(shape, fill=fill)
    if rng.random() < 0.5:
        draw.text((2, side // 3), word(rng)[:6], font=font(rng.choice(fonts()), max(side // 4, 8)),
                  fill=(255, 255, 255, alpha))
    layer = rgba(image)
    x, y = rng.randint(-side // 3, size - side // 2), rng.randint(-side // 3, size - side // 2)
    for frame in frames:
        blend(frame, layer, x, y)


def apply(frames, rng, other):
    """Draws one to three stream layers onto frames [T, 3, P, P] in place and returns them."""
    kinds = [still_text, scrolling_text, scrolling_text, camera_box, logo]
    for kind in rng.sample(kinds, rng.randint(1, 3)):
        if kind is camera_box:
            camera_box(frames, rng, other())
        else:
            kind(frames, rng)
    return frames.clamp_(0, 1)


def preview(path, seed=1, size=256, count=5):
    """Writes a strip of overlaid random-noise frames, to check the layers by eye."""
    import random
    rng = random.Random(seed)
    base = torch.linspace(0, 1, size).view(1, 1, 1, size).expand(count, 3, size, size).clone()
    other = lambda: torch.rand(count, 3, 64, 64).repeat_interleave(4, 2).repeat_interleave(4, 3)
    out = apply(base, rng, other)
    strip = (out.permute(2, 0, 3, 1).reshape(size, count * size, 3) * 255).byte().numpy()
    Image.fromarray(strip).save(path)


if __name__ == "__main__":
    import sys
    for seed in range(int(sys.argv[2]) if len(sys.argv) > 2 else 4):
        preview(f"{sys.argv[1]}-{seed}.png", seed)
