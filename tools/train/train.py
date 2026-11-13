"""Trains the upscaling network (x2). The shape matches what tools/fg-bench/sr_cost.py measured:
the input is unpacked to half resolution, and a recurrent state carries over from frame to frame
so that the result does not flicker.

Usage: python train.py --data <data dir> --run <run dir>
       python train.py --smoke     (a few iterations on the CPU with random data)
"""
import argparse
import json
import math
import pathlib
import random
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset

HIDDEN = 4


class Block(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.depthwise = nn.Conv2d(channels, channels, 3, padding=1, padding_mode="replicate", groups=channels)
        self.mix = nn.Conv2d(channels, channels, 1)

    def forward(self, x):
        return F.relu(self.mix(self.depthwise(x)) + x)


class Upscaler(nn.Module):
    def __init__(self, channels=24, blocks=4):
        super().__init__()
        self.head = nn.Conv2d(2 * 3 * 4 + HIDDEN, channels, 1)
        self.blocks = nn.Sequential(*[Block(channels) for _ in range(blocks)])
        self.tail = nn.Conv2d(channels, 3 * 16 + HIDDEN, 1)

    def step(self, current, previous, state):
        x = F.pixel_unshuffle(torch.cat([current, previous], 1), 2)
        y = self.tail(self.blocks(F.relu(self.head(torch.cat([x, state], 1)))))
        residual, state = y[:, :48], torch.tanh(y[:, 48:])
        base = F.interpolate(current, scale_factor=2, mode="bilinear", align_corners=False)
        return base + F.pixel_shuffle(residual, 4), state

    def forward(self, frames):
        batch, steps, _, height, width = frames.shape
        state = torch.zeros(batch, HIDDEN, height // 2, width // 2, device=frames.device)
        outputs = []
        for t in range(steps):
            previous = frames[:, max(t - 1, 0)]
            output, state = self.step(frames[:, t], previous, state)
            outputs.append(output)
        return torch.stack(outputs, 1)


def load(path):
    return torch.from_numpy(np.asarray(Image.open(path).convert("RGB"), dtype=np.float32).copy()).permute(2, 0, 1) / 255


class Clips(Dataset):
    """Reads the clips written by pack.py: decoding PNGs left the GPU idle 85 % of the time."""

    def __init__(self, data, split, steps, patch, epoch_size):
        root = data / "packed" / split
        self.pairs = [(path, path.with_name(path.name.replace("_lr", "_hr"))) for path in sorted(root.glob("*_lr.npy"))]
        self.steps, self.patch, self.epoch_size = steps, patch, epoch_size
        self.open = {}

    def __len__(self):
        return self.epoch_size

    def clip(self, path):
        if path not in self.open:
            self.open[path] = np.load(path, mmap_mode="r")
        return self.open[path]

    def __getitem__(self, _):
        low_path, high_path = random.choice(self.pairs)
        low_clip, high_clip = self.clip(low_path), self.clip(high_path)
        count, h, w, _ = low_clip.shape
        start = random.randrange(count - self.steps + 1)
        y, x = random.randrange(h - self.patch + 1), random.randrange(w - self.patch + 1)
        low = np.array(low_clip[start:start + self.steps, y:y + self.patch, x:x + self.patch])
        high = np.array(high_clip[start:start + self.steps, y * 2:(y + self.patch) * 2, x * 2:(x + self.patch) * 2])
        if random.random() < 0.5:
            low, high = low[::-1], high[::-1]
        if random.random() < 0.5:
            low, high = low[:, :, ::-1], high[:, :, ::-1]
        convert = lambda a: torch.from_numpy(a.copy()).permute(0, 3, 1, 2).float() / 255
        return convert(low), convert(high)


def charbonnier(a, b):
    return torch.sqrt((a - b) ** 2 + 1e-6).mean()


def loss_of(output, target, temporal_weight):
    pixels = charbonnier(output, target)
    # the change between frames has to match the real one: this is what removes the flicker
    temporal = charbonnier(output[:, 1:] - output[:, :-1], target[:, 1:] - target[:, :-1])
    return pixels + temporal_weight * temporal, pixels.item(), temporal.item()


def psnr(a, b):
    return -10 * math.log10(max(F.mse_loss(a.clamp(0, 1), b).item(), 1e-10))


@torch.no_grad()
def validate(model, data, device, clips=10, frames=20):
    root = data / "lr" / "val"
    results, baselines = [], []
    model.eval()
    for lr_clip in sorted(p for p in root.iterdir() if p.is_dir())[:clips]:
        hr_clip = data / "val" / "val_sharp" / lr_clip.name
        names = sorted(p.name for p in lr_clip.glob("*.png"))[:frames]
        low = torch.stack([load(lr_clip / n) for n in names])[None].to(device)
        high = torch.stack([load(hr_clip / n) for n in names])[None].to(device)
        output = model(low)
        base = F.interpolate(low[0], scale_factor=2, mode="bilinear", align_corners=False)
        results.append(psnr(output, high))
        baselines.append(psnr(base[None], high))
    model.train()
    return sum(results) / len(results), sum(baselines) / len(baselines)


def smoke():
    model = Upscaler()
    optimizer = torch.optim.Adam(model.parameters(), 2e-4)
    for _ in range(3):
        low = torch.rand(2, 4, 3, 48, 48)
        high = torch.rand(2, 4, 3, 96, 96)
        loss, _, _ = loss_of(model(low), high, 0.5)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print("smoke ok, parameters:", sum(p.numel() for p in model.parameters()), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=pathlib.Path)
    parser.add_argument("--run", type=pathlib.Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--channels", type=int, default=24)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=200000)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--patch", type=int, default=96)
    parser.add_argument("--temporal", type=float, default=0.5)
    parser.add_argument("--memory-fraction", type=float, default=0.42)
    args = parser.parse_args()
    if args.smoke:
        smoke()
        return

    torch.cuda.set_per_process_memory_fraction(args.memory_fraction)
    device = torch.device("cuda")
    args.run.mkdir(parents=True, exist_ok=True)
    model = Upscaler(args.channels, args.blocks).to(device)
    optimizer = torch.optim.Adam(model.parameters(), 2e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.iterations, 1e-6)
    latest = args.run / "latest.pt"
    iteration = 0
    if latest.exists():
        saved = torch.load(latest, map_location=device)
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        scheduler.load_state_dict(saved["scheduler"])
        iteration = saved["iteration"]
    loader = DataLoader(Clips(args.data, "train", args.steps, args.patch, 10 ** 9), batch_size=args.batch, num_workers=6, pin_memory=True)
    log = (args.run / "log.jsonl").open("a", encoding="utf-8")
    window = time.time()
    best = 0.0
    for low, high in loader:
        if iteration >= args.iterations:
            break
        low, high = low.to(device, non_blocking=True), high.to(device, non_blocking=True)
        loss, pixels, temporal = loss_of(model(low), high, args.temporal)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        iteration += 1
        if iteration % 100 == 0:
            rate = 100 / (time.time() - window)
            window = time.time()
            line = {"iteration": iteration, "loss": round(loss.item(), 5), "pixels": round(pixels, 5), "temporal": round(temporal, 5),
                    "per_second": round(rate, 2), "vram_mb": round(torch.cuda.max_memory_allocated() / 1e6)}
            print(json.dumps(line), flush=True)
            log.write(json.dumps(line) + "\n")
            log.flush()
        if iteration % 2000 == 0:
            score, baseline = validate(model, args.data, device)
            line = {"iteration": iteration, "val_psnr": round(score, 3), "bilinear_psnr": round(baseline, 3)}
            print(json.dumps(line), flush=True)
            log.write(json.dumps(line) + "\n")
            log.flush()
            state = {"model": model.state_dict(), "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(),
                     "iteration": iteration, "channels": args.channels, "blocks": args.blocks}
            torch.save(state, latest)
            if score > best:
                best = score
                torch.save(state, args.run / "best.pt")


if __name__ == "__main__":
    main()
