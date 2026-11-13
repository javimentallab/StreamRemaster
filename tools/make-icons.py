#!/usr/bin/env python3
"""Draws the extension icon (16/32/48/96/128 px) into extension/shared/icons/.

StreamRemaster: a rounded purple square with a play triangle that leaves two fading copies behind
it (the frames made in between) and a four-pointed sparkle (the AI that sharpens the picture).
Drawn at 8x and downsampled, so the small sizes stay crisp.
Run:  python tools/make-icons.py
"""
import math
import os

from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "extension", "shared", "icons")
SIZES = (16, 32, 48, 96, 128)


def draw(px):
    s = px * 8
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # background with a vertical gradient
    top, bottom = (128, 96, 255), (90, 56, 240)
    grad = Image.new("RGBA", (s, s))
    gd = ImageDraw.Draw(grad)
    for y in range(s):
        k = y / (s - 1)
        gd.line([(0, y), (s, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)) + (255,))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=255)
    img.paste(grad, (0, 0), mask)

    # the play triangle and the copies it leaves behind
    # (each on its own layer, so the faded ones blend with the purple instead of replacing it)
    def triangle(dx, alpha):
        layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        x0, x1 = s * (0.30 + dx), s * (0.72 + dx)
        ImageDraw.Draw(layer).polygon([(x0, s * 0.27), (x0, s * 0.79), (x1, s * 0.53)], fill=(255, 255, 255, alpha))
        layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (s, s), 0), mask))
        img.alpha_composite(layer)

    triangle(-0.20, 70)
    triangle(-0.10, 140)
    triangle(0.0, 255)
    d = ImageDraw.Draw(img)

    # sparkle: four points, top right
    cx, cy, big, small = s * 0.78, s * 0.22, s * 0.13, s * 0.035
    points = []
    for k in range(8):
        r = big if k % 2 == 0 else small
        angle = k * 3.14159265 / 4 - 3.14159265 / 2
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    d.polygon(points, fill=(255, 214, 92, 255))
    return img.resize((px, px), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for px in SIZES:
        draw(px).save(os.path.join(OUT, f"icon{px}.png"))
    print("icons:", ", ".join(str(p) for p in SIZES))


if __name__ == "__main__":
    main()
