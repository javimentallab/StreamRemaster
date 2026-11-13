"""Trains the frame interpolation network. The shape is the one tools/fg-bench/fi_cost.py measured.

The network runs once per pair of source frames, on luma unpacked to a quarter of the resolution,
and gives at that quarter: the motion from the first frame to the second and back (in quarter-grid
pixels) and an occlusion mask. Any in-between instant t is then made by a cheap synthesis pass:
both frames are pulled along the motion scaled to t (the Super SloMo approximation) and blended
by the mask. The synthesis here is written the way the WGSL one samples: bilinear, clamped to the
edge, pixel centres.

Data: REDS at 120 fps (data/packed120/train/*.npy from pack120.py, data/orig/val/<clip>/*.png) and
game footage recorded at 120 fps (data/packed120/games/*.npy from xonotic_capture.sh and
pack_game.py; a map kept apart in data/packed120/games-val/ for validation). Pairs are taken 2, 4
or 5 frames apart (60, 30 and 24 fps sources) and the frames between them are the targets. A share
of the patches gets stream layers drawn over them (overlays.py): still text, a scrolling chat, a
camera box, logos.

Usage: python interp.py --data <data dir> --run <run dir>
       python interp.py --smoke      (a few iterations on the CPU with random data)
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

import overlays

LUMA = (0.299, 0.587, 0.114)
OUT_CHANNELS = 8      # motion 0->1 (2), motion 1->0 (2), mask logit (1), spare (3)
FLOW_SCALE = 4.0      # folded into the exported weights
GAPS = [2, 2, 4, 5]   # source frame spacing at 120 fps: 60, 60, 30 and 24 fps
TARGETS = 2           # in-between frames scored per pair
SIDE_CUTS = [".cuts.npy", ".offtime.npy"]   # side files with transitions a window must not cross


class Block(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.depthwise = nn.Conv2d(channels, channels, 3, padding=1, padding_mode="replicate", groups=channels)
        self.mix = nn.Conv2d(channels, channels, 1)

    def forward(self, x):
        return F.relu(self.mix(self.depthwise(x)) + x)


def blocks(channels, count):
    return nn.Sequential(*[Block(channels) for _ in range(count)])


def unpack2(x):
    """Half resolution, four times the channels, grouped by position: channel k*C + c, k = dy*2 + dx
    (the order of the WGSL unpack)."""
    n, c, h, w = x.shape
    return F.pixel_unshuffle(x, 2).view(n, c, 4, h // 2, w // 2).transpose(1, 2).reshape(n, 4 * c, h // 2, w // 2)


def pack2(x):
    n, c4, h, w = x.shape
    return F.pixel_shuffle(x.view(n, 4, c4 // 4, h, w).transpose(1, 2).reshape(n, c4, h, w), 2)


class Interpolator(nn.Module):
    def __init__(self, c1=24, c2=48, b1=2, b2=2, b3=3, bu=1):
        super().__init__()
        self.shape = dict(c1=c1, c2=c2, b1=b1, b2=b2, b3=b3, bu=bu)
        self.head = nn.Conv2d(32, c1, 1)
        self.level4 = blocks(c1, b1)
        self.down8 = nn.Conv2d(4 * c1, c2, 1)
        self.level8 = blocks(c2, b2)
        self.down16 = nn.Conv2d(4 * c2, c2, 1)
        self.level16 = blocks(c2, b3)
        self.up8 = nn.Conv2d(c2, 4 * c2, 1)
        self.after8 = blocks(c2, bu)
        self.up4 = nn.Conv2d(c2, 4 * c1, 1)
        self.after4 = blocks(c1, bu)
        self.tail = nn.Conv2d(c1, OUT_CHANNELS, 1)
        self.register_buffer("luma", torch.tensor(LUMA).view(1, 3, 1, 1))
        self.register_buffer("scale", torch.tensor([FLOW_SCALE] * 4 + [1.0] * (OUT_CHANNELS - 4)).view(1, -1, 1, 1))

    def motion(self, a, b):
        """a, b: [N, 3, H, W], H and W multiples of 16. Returns [N, 8, H/4, W/4]."""
        ya = (a * self.luma).sum(1, keepdim=True)
        yb = (b * self.luma).sum(1, keepdim=True)
        x = torch.cat([F.pixel_unshuffle(ya, 4), F.pixel_unshuffle(yb, 4)], 1)
        s4 = self.level4(F.relu(self.head(x)))
        s8 = self.level8(F.relu(self.down8(unpack2(s4))))
        s16 = self.level16(F.relu(self.down16(unpack2(s8))))
        u8 = self.after8(F.relu(pack2(self.up8(s16)) + s8))
        u4 = self.after4(F.relu(pack2(self.up4(u8)) + s4))
        return self.tail(u4) * self.scale


def warp(image, offset):
    """Samples image at each pixel centre plus offset (in uv units), bilinear, clamped to the edge."""
    n, _, h, w = image.shape
    ys = (torch.arange(h, device=image.device, dtype=image.dtype) + 0.5) / h
    xs = (torch.arange(w, device=image.device, dtype=image.dtype) + 0.5) / w
    grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
    u = grid_x[None] + offset[:, 0]
    v = grid_y[None] + offset[:, 1]
    grid = torch.stack([u * 2 - 1, v * 2 - 1], -1)
    return F.grid_sample(image, grid, mode="bilinear", padding_mode="border", align_corners=False)


def synthesize(a, b, motion, t):
    """The frame at instant t (tensor [N]) between a and b."""
    n, _, h, w = a.shape
    f = F.interpolate(motion[:, :5], size=(h, w), mode="bilinear", align_corners=False)
    grid = torch.tensor([w / 4, h / 4], device=a.device, dtype=a.dtype).view(1, 2, 1, 1)
    f01, f10 = f[:, 0:2] / grid, f[:, 2:4] / grid
    m = torch.sigmoid(f[:, 4:5])
    t = t.view(-1, 1, 1, 1)
    ft0 = -(1 - t) * t * f01 + t * t * f10
    ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10
    wa, wb = (1 - t) * m, t * (1 - m)
    return (wa * warp(a, ft0) + wb * warp(b, ft1)) / (wa + wb).clamp_min(1e-4)


def charbonnier(a, b):
    return torch.sqrt((a - b) ** 2 + 1e-6).mean()


def smoothness(motion):
    f = motion[:, :4]
    return (f[:, :, 1:] - f[:, :, :-1]).abs().mean() + (f[:, :, :, 1:] - f[:, :, :, :-1]).abs().mean()


def packed(folder):
    """The clips of a packed folder, without the side files (.cuts, .offtime, .phase) and unfinished ones."""
    return sorted(p for p in folder.glob("*.npy")
                  if not p.name.endswith((".cuts.npy", ".offtime.npy", ".phase.npy", ".partial.npy")))


def cuts_of(path):
    """Transitions k -> k + 1 that a window must not cross: camera switches and flashes (.cuts.npy
    from pack_game.py) and frames not evenly spaced in time (.offtime.npy from time_phase.py)."""
    cuts = set()
    for suffix in SIDE_CUTS:
        side = path.with_suffix(suffix)
        if side.exists():
            cuts |= set(np.load(side).tolist())
    return cuts


def valid_starts(count, cuts, gap):
    """First frames of the windows of gap + 1 frames that cross no cut."""
    return [s for s in range(count - gap) if not cuts.intersection(range(s, s + gap))]


class Pairs(Dataset):
    def __init__(self, data, patch, epoch_size, games_share=0.0, overlay=0.0):
        self.sets = [packed(data / "packed120" / "train"), packed(data / "packed120" / "games")]
        if not self.sets[0] and not self.sets[1]:
            raise SystemExit("no packed clips: run pack120.py or pack_game.py first")
        self.games_share = games_share if self.sets[1] else 0.0
        if not self.sets[0]:
            self.games_share = 1.0
        self.patch, self.epoch_size, self.overlay = patch, epoch_size, overlay
        self.open = {}

    def __len__(self):
        return self.epoch_size

    def clip(self, path):
        if path not in self.open:
            data = np.load(path, mmap_mode="r")
            cuts = cuts_of(path)
            self.open[path] = (data, {gap: valid_starts(len(data), cuts, gap) for gap in set(GAPS)})
        return self.open[path]

    def window_counts(self):
        """Valid windows per gap in each set, for the log."""
        return {name: {gap: sum(len(self.clip(p)[1][gap]) for p in paths) for gap in sorted(set(GAPS))}
                for name, paths in (("reds", self.sets[0]), ("games", self.sets[1]))}

    def __getitem__(self, _):
        gap = random.choice(GAPS)
        frames = self.patch_frames(gap)
        if random.random() < self.overlay:
            overlays.apply(frames, random, lambda: self.patch_frames(gap))
        picks = [random.randrange(1, gap) for _ in range(TARGETS)]
        targets = torch.stack([frames[k] for k in picks])
        times = torch.tensor([k / gap for k in picks])
        return frames[0], frames[-1], targets, times

    def patch_frames(self, gap):
        """gap + 1 consecutive frames of a random crop of a random clip, [gap + 1, 3, P, P]."""
        clips = self.sets[1] if random.random() < self.games_share else self.sets[0]
        for _ in range(50):
            clip, starts = self.clip(random.choice(clips))
            if starts[gap]:
                break
        else:
            raise RuntimeError(f"no clip has a valid window of gap {gap}")
        count, h, w, _ = clip.shape
        start = random.choice(starts[gap])
        # a random zoom out, so the same footage also teaches smaller motion at lower resolution
        zoom = random.uniform(0.5, 1.0)
        size = min(int(self.patch / zoom), h, w)
        y, x = random.randrange(h - size + 1), random.randrange(w - size + 1)
        frames = torch.from_numpy(np.array(clip[start:start + gap + 1, y:y + size, x:x + size])).permute(0, 3, 1, 2).float() / 255
        if size != self.patch:
            frames = F.interpolate(frames, size=(self.patch, self.patch), mode="bilinear", antialias=True, align_corners=False)
        if random.random() < 0.5:
            frames = frames.flip(0)
        if random.random() < 0.5:
            frames = frames.flip(3)
        if random.random() < 0.5:
            frames = frames.flip(2)
        return frames.contiguous()


def load(path):
    return torch.from_numpy(np.asarray(Image.open(path).convert("RGB"), dtype=np.float32).copy()).permute(2, 0, 1) / 255


def psnr(a, b):
    return -10 * math.log10(max(F.mse_loss(a.clamp(0, 1), b).item(), 1e-10))


def score(model, frames, gap, ours, fade):
    """Adds the PSNR of the in-between frames of [gap + 1, 3, H, W] for the model and the fade."""
    a, b = frames[:1], frames[-1:]
    motion = model.motion(a, b)
    for k in range(1, gap):
        t = torch.tensor([k / gap], device=frames.device)
        ours.append(psnr(synthesize(a, b, motion, t), frames[k:k + 1]))
        fade.append(psnr(a * (1 - k / gap) + b * (k / gap), frames[k:k + 1]))


@torch.no_grad()
def validate(model, data, device, clips=5, pairs=6):
    """PSNR of the in-between frames for 60 fps (gap 2) and 30 fps (gap 4) sources, against a plain
    cross-fade: on REDS validation clips (fps60, fps30), on the same clips cropped to 512 x 512 with
    stream layers drawn over them, always the same ones (fps60_layers, fps30_layers), and on the
    game clips kept for validation (fps60_games, fps30_games)."""
    model.eval()
    scores = {}
    roots = sorted(p for p in (data / "orig" / "val").iterdir() if p.is_dir())[:clips]
    names = {root: sorted(p.name for p in root.glob("*.png")) for root in roots}
    games = [(np.load(p, mmap_mode="r"), cuts_of(p)) for p in packed(data / "packed120" / "games-val")]

    def reds(root, start, gap):
        return torch.stack([load(root / names[root][start + k]) for k in range(gap + 1)]).to(device)

    for gap in (2, 4):
        results = {"": ([], []), "_layers": ([], []), "_games": ([], [])}
        for n, root in enumerate(roots):
            for m, start in enumerate(np.linspace(0, len(names[root]) - gap - 1, pairs).astype(int)):
                frames = reds(root, start, gap)
                score(model, frames, gap, *results[""])
                _, _, h, w = frames.shape
                y, x = (h - 512) // 2, (w - 512) // 2
                crop = frames[:, :, y:y + 512, x:x + 512].cpu().clone()
                other = roots[(n + 1) % len(roots)]
                rng = random.Random(1000 * n + m)
                layered = overlays.apply(crop, rng, lambda: reds(other, start, gap)[:, :, y:y + 512, x:x + 512].cpu())
                score(model, layered.to(device), gap, *results["_layers"])
        for clip, cuts in games:
            for start in np.linspace(0, len(clip) - gap - 1, pairs).astype(int):
                # move past a camera switch, so the score is about motion and not about cuts
                while start + gap < len(clip) - 1 and cuts.intersection(range(start, start + gap)):
                    start += 1
                frames = torch.from_numpy(np.array(clip[start:start + gap + 1])).permute(0, 3, 1, 2).float().to(device) / 255
                score(model, frames, gap, *results["_games"])
        for suffix, (ours, fade) in results.items():
            if ours:
                scores[f"fps{120 // gap}{suffix}"] = round(sum(ours) / len(ours), 3)
                scores[f"fps{120 // gap}{suffix}_fade"] = round(sum(fade) / len(fade), 3)
    model.train()
    return scores


def overall(scores):
    """What picks the best checkpoint: the mean of the 60 fps scores that were measured."""
    values = [scores[k] for k in ("fps60", "fps60_layers", "fps60_games") if k in scores]
    return sum(values) / len(values)


def step(model, batch, device, smooth_weight):
    a, b, targets, times = (x.to(device, non_blocking=True) for x in batch)
    motion = model.motion(a, b)
    loss = 0.0
    for k in range(TARGETS):
        loss = loss + charbonnier(synthesize(a, b, motion, times[:, k]), targets[:, k])
    loss = loss / TARGETS
    return loss + smooth_weight * smoothness(motion), loss.item()


def smoke():
    model = Interpolator()
    optimizer = torch.optim.Adam(model.parameters(), 3e-4)
    for _ in range(3):
        batch = (torch.rand(2, 3, 64, 64), torch.rand(2, 3, 64, 64), torch.rand(2, TARGETS, 3, 64, 64), torch.rand(2, TARGETS))
        loss, _ = step(model, batch, "cpu", 0.01)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print("smoke ok, parameters:", sum(p.numel() for p in model.parameters()), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=pathlib.Path)
    parser.add_argument("--run", type=pathlib.Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--shape", default="24,48,2,2,3,1")
    parser.add_argument("--iterations", type=int, default=150000)
    parser.add_argument("--batch", type=int, default=12)
    parser.add_argument("--patch", type=int, default=256)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--smooth", type=float, default=0.01)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--memory-fraction", type=float, default=0.42)
    parser.add_argument("--games-share", type=float, default=0.5, help="share of patches taken from game clips")
    parser.add_argument("--overlay", type=float, default=0.4, help="share of patches with stream layers drawn over")
    parser.add_argument("--ignore-offtime", action="store_true",
                        help="cross the frames time_phase.py marked as not evenly spaced (as the runs before it did)")
    args = parser.parse_args()
    if args.ignore_offtime:
        SIDE_CUTS.remove(".offtime.npy")
    if args.smoke:
        smoke()
        return

    c1, c2, b1, b2, b3, bu = (int(x) for x in args.shape.split(","))
    torch.cuda.set_per_process_memory_fraction(args.memory_fraction)
    device = torch.device("cuda")
    args.run.mkdir(parents=True, exist_ok=True)
    model = Interpolator(c1, c2, b1, b2, b3, bu).to(device)
    optimizer = torch.optim.Adam(model.parameters(), args.lr)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.iterations, 1e-6)
    latest = args.run / "latest.pt"
    iteration = 0
    if latest.exists():
        saved = torch.load(latest, map_location=device)
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        scheduler.load_state_dict(saved["scheduler"])
        iteration = saved["iteration"]
    pairs = Pairs(args.data, args.patch, 10 ** 9, args.games_share, args.overlay)
    loader = DataLoader(pairs, batch_size=args.batch, num_workers=args.workers, pin_memory=True, persistent_workers=True)
    log = (args.run / "log.jsonl").open("a", encoding="utf-8")
    counts = {"iteration": iteration, "windows": pairs.window_counts()}
    print(json.dumps(counts), flush=True)
    log.write(json.dumps(counts) + "\n")
    window = time.time()
    best = -1.0
    if (args.run / "best.json").exists():
        best = overall(json.loads((args.run / "best.json").read_text()))
    for batch in loader:
        if iteration >= args.iterations:
            break
        loss, pixels = step(model, batch, device, args.smooth)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        iteration += 1
        if iteration % 100 == 0:
            rate = 100 / (time.time() - window)
            window = time.time()
            line = {"iteration": iteration, "loss": round(loss.item(), 5), "pixels": round(pixels, 5),
                    "per_second": round(rate, 2), "vram_mb": round(torch.cuda.max_memory_allocated() / 1e6)}
            print(json.dumps(line), flush=True)
            log.write(json.dumps(line) + "\n")
            log.flush()
        if iteration % 2000 == 0:
            scores = validate(model, args.data, device)
            line = {"iteration": iteration, **scores}
            print(json.dumps(line), flush=True)
            log.write(json.dumps(line) + "\n")
            log.flush()
            state = {"model": model.state_dict(), "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(),
                     "iteration": iteration, "shape": model.shape}
            torch.save(state, latest)
            if overall(scores) > best:
                best = overall(scores)
                torch.save(state, args.run / "best.pt")
                (args.run / "best.json").write_text(json.dumps(line))


if __name__ == "__main__":
    main()
