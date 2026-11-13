"""Side-by-side of in-between frames, to judge them by eye: a validation clip is taken as a low frame
rate source (one frame in every --gap of the 120 fps footage), the frames in between are rebuilt
with a plain cross-fade and with the model, and the real ones are shown next to them.

Writes <out>/<clip>.mp4 (fade | model | real, played at half speed so the in-between frames can be
seen) and <out>/<clip>-<n>.png (one in-between frame, the three side by side, cropped).

Usage: python compare_fi.py --data <data dir> --model <checkpoint.pt> --out <dir> [--clips 000 005] [--gap 4]
Runs on the CPU.
"""
import argparse
import pathlib
import subprocess

import numpy as np
import torch
from PIL import Image, ImageDraw

from interp import Interpolator, load, psnr, synthesize


def to_image(t):
    return (t[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)


def label(array, text):
    image = Image.fromarray(array)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 12 + 9 * len(text), 26], fill=(0, 0, 0))
    draw.text((6, 6), text, fill=(255, 255, 255))
    return np.asarray(image)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=pathlib.Path, required=True)
    parser.add_argument("--model", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--clips", nargs="+", default=["000", "005", "011"])
    parser.add_argument("--gap", type=int, default=4)
    parser.add_argument("--frames", type=int, default=160)
    parser.add_argument("--scale", type=float, default=0.5, help="video size relative to 1280x720 per panel")
    args = parser.parse_args()
    torch.set_num_threads(8)
    saved = torch.load(args.model, map_location="cpu")
    model = Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    model.eval()
    args.out.mkdir(parents=True, exist_ok=True)
    for clip in args.clips:
        root = args.data / "orig" / "val" / clip
        names = sorted(p.name for p in root.glob("*.png"))[:args.frames + 1]
        frames_dir = args.out / f"{clip}-frames"
        frames_dir.mkdir(exist_ok=True)
        ours_scores, fade_scores = [], []
        n = 0
        with torch.no_grad():
            for start in range(0, len(names) - args.gap, args.gap):
                a = load(root / names[start])[None]
                b = load(root / names[start + args.gap])[None]
                motion = model.motion(a, b)
                for k in range(args.gap):
                    real = load(root / names[start + k])[None]
                    if k == 0:
                        ours, fade = a, a
                    else:
                        t = k / args.gap
                        ours = synthesize(a, b, motion, torch.tensor([t]))
                        fade = a * (1 - t) + b * t
                        ours_scores.append(psnr(ours, real))
                        fade_scores.append(psnr(fade, real))
                    panels = [label(to_image(fade), "fundido"), label(to_image(ours), "IA"), label(to_image(real), "real")]
                    row = np.concatenate(panels, 1)
                    if args.scale != 1:
                        img = Image.fromarray(row)
                        row = np.asarray(img.resize((int(img.width * args.scale), int(img.height * args.scale)), Image.BICUBIC))
                    Image.fromarray(row).save(frames_dir / f"{n:05d}.png")
                    if k == args.gap // 2 and start == args.gap * 8:
                        Image.fromarray(np.concatenate(panels, 1)).save(args.out / f"{clip}-{start + k}.png")
                    n += 1
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(120 // 2), "-i", str(frames_dir / "%05d.png"),
                        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(args.out / f"{clip}.mp4")], check=True)
        for p in frames_dir.glob("*.png"):
            p.unlink()
        frames_dir.rmdir()
        print(clip, {"ours": round(sum(ours_scores) / len(ours_scores), 2), "fade": round(sum(fade_scores) / len(fade_scores), 2)}, flush=True)


main()
