"""Side-by-side comparison of upscalers, to judge them by eye: our model, the WebSR networks
(websr.py) and classic scaling.

For a few validation clips it writes the PSNR of every method, a PNG with the most detailed crop of one
frame for the methods in --show (enlarged x2 without smoothing) and, for --videos, a short MP4 with the
methods in --video-methods side by side so that flicker can be seen. Runs on the CPU.

Usage: python compare.py --data <data dir> --model <best.pt> --websr <dir with cnn-2x-*.json> --out <dir>
"""
import argparse
import json
import pathlib
import subprocess
import tempfile

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont

from train import Upscaler, load, psnr
from websr import WebSR

LABELS = {"bilinear": "Bilineal", "bicubic": "Bicúbico", "ours": "Nuestro 24x4", "original": "Original"}


def label(name):
    if name in LABELS:
        return LABELS[name]
    size, kind = name.split("-")[2:4]
    return f"WebSR {size.upper()} {dict(rl='real', an='anime', d3='3D').get(kind, kind)}"


def to_image(tensor):
    return Image.fromarray((tensor.clamp(0, 1).permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8))


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def detailed_crop(high, width, height):
    """Top-left corner of the crop with the most fine detail in the original frame."""
    gray = high.mean(0)
    energy = (gray[:, 1:] - gray[:, :-1]).abs()[:-1] + (gray[1:] - gray[:-1]).abs()[:, :-1]
    best, corner = -1.0, (0, 0)
    for y in range(0, energy.shape[0] - height, 20):
        for x in range(0, energy.shape[1] - width, 20):
            value = energy[y:y + height, x:x + width].sum().item()
            if value > best:
                best, corner = value, (y, x)
    return corner


def panel_row(images, labels, scale):
    width, height = images[0].size
    label_height = 44
    sheet = Image.new("RGB", (width * scale * len(images), height * scale + label_height), (20, 20, 20))
    draw = ImageDraw.Draw(sheet)
    for i, (image, text) in enumerate(zip(images, labels)):
        sheet.paste(image.resize((width * scale, height * scale), Image.NEAREST), (i * width * scale, label_height))
        draw.text((i * width * scale + 12, 8), text, fill=(255, 255, 255), font=font(26))
    return sheet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=pathlib.Path, required=True)
    parser.add_argument("--model", type=pathlib.Path, required=True)
    parser.add_argument("--websr", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--clips", nargs="+", default=["000", "005", "011", "015", "020", "025"])
    parser.add_argument("--videos", nargs="+", default=["011", "020"])
    parser.add_argument("--show", nargs="+", default=["bicubic", "ours", "cnn-2x-s-rl", "cnn-2x-m-rl", "cnn-2x-l-rl", "original"])
    parser.add_argument("--video-methods", nargs="+", default=["bicubic", "ours", "cnn-2x-l-rl", "original"])
    parser.add_argument("--frames", type=int, default=100)
    parser.add_argument("--frame", type=int, default=30)
    args = parser.parse_args()
    torch.set_num_threads(4)
    args.out.mkdir(parents=True, exist_ok=True)

    saved = torch.load(args.model, map_location="cpu")
    model = Upscaler(saved["channels"], saved["blocks"])
    model.load_state_dict(saved["model"])
    model.eval()
    websr = {path.stem.replace("-3d", "-d3"): WebSR(path) for path in sorted(args.websr.glob("cnn-2x-*.json"))}
    summary = {"iteration": saved["iteration"], "clips": {}}

    for name in args.clips:
        lr_dir, hr_dir = args.data / "lr" / "val" / name, args.data / "val" / "val_sharp" / name
        names = sorted(p.name for p in lr_dir.glob("*.png"))[:args.frames]
        low = torch.stack([load(lr_dir / n) for n in names])
        high = torch.stack([load(hr_dir / n) for n in names])
        with torch.no_grad():
            outputs = {"bilinear": F.interpolate(low, scale_factor=2, mode="bilinear", align_corners=False),
                       "bicubic": F.interpolate(low, scale_factor=2, mode="bicubic", align_corners=False),
                       "ours": model(low[None])[0]}
            for key, network in websr.items():
                outputs[key] = torch.cat([network(low[i:i + 10]) for i in range(0, len(low), 10)])
        outputs = {key: value.clamp(0, 1) for key, value in outputs.items()}
        outputs["original"] = high
        summary["clips"][name] = {key: round(psnr(value, high), 2) for key, value in outputs.items() if key != "original"}

        t = min(args.frame, len(names) - 1)
        y, x = detailed_crop(high[t], 320, 200)
        panel_row([to_image(outputs[k][t, :, y:y + 200, x:x + 320]) for k in args.show], [label(k) for k in args.show], 2) \
            .save(args.out / f"recorte-{name}.png")

        if name in args.videos:
            y, x = detailed_crop(high[t], 320, 360)
            with tempfile.TemporaryDirectory() as tmp:
                for i in range(len(names)):
                    panel_row([to_image(outputs[k][i, :, y:y + 360, x:x + 320]) for k in args.video_methods],
                              [label(k) for k in args.video_methods], 2).save(pathlib.Path(tmp) / f"{i:04d}.png")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", str(pathlib.Path(tmp) / "%04d.png"),
                                "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(args.out / f"video-{name}.mp4")], check=True)
        print(name, json.dumps(summary["clips"][name]), flush=True)

    keys = list(next(iter(summary["clips"].values())))
    summary["mean"] = {k: round(sum(c[k] for c in summary["clips"].values()) / len(summary["clips"]), 3) for k in keys}
    print("mean", json.dumps(summary["mean"]), flush=True)
    (args.out / "resumen.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
