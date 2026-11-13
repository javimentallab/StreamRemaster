"""Trains upscaling and frame interpolation together, as the extension runs them: every captured
frame is upscaled x2 by the recurrent upscaler of train.py (current frame, previous frame and a
state), the motion is measured once per pair on the captured (small) frames by the network of
interp.py, and the in-between frames are synthesized from the two upscaled frames. The loss is
taken on what is shown: the upscaled key frames and the upscaled in-between frames against the
real ones at full resolution, plus a temporal term against flicker.

Two phases. First pixels only (Charbonnier). Then a patch discriminator trained from scratch joins,
so the upscaler is pushed to draw plausible detail instead of the blurry average that a pixel loss
settles on. No weights from anyone else are used anywhere: the motion network can start from one
of our own runs (--init-fi).

The small frames are made on the fly from the 120 fps footage: halved (bicubic, antialiased) and,
most of the time, JPEG-compressed with 4:2:0 chroma at a random quality, standing in for the codec
of a stream.

With --aligned the upscaler also gets the previous upscaled frame, moved onto the current one with
the motion the interpolation network measured between the two captured frames (its 1->0 half): the
detail recovered in earlier frames is carried on instead of being guessed again. When the extension
has no motion for a frame (the first one, or one the GPU skipped), it gives the bilinear enlargement
of the current frame instead; training does the same on a share of the steps. --keys sets how many
captured frames a training window has (3: one step of history; 4: two).

--weather draws rain or snow (weather.py) over that share of the windows, targets included, since
it is part of the picture; --grain adds sensor grain to that share of the captured frames only, so
the upscaler learns not to sharpen it. --effects draws a game effect or moving vegetation
(effects.py: sparks, smoke or fire, a flash, swaying grass or rippling leaves) over that share.
--init starts the whole model from a joint.py checkpoint.

Usage: python joint.py --data <data dir> --run <run dir> [--init-fi runs/fi32x64-sync/best.pt]
       python joint.py --smoke     (a few iterations on the CPU with random data)
"""
import argparse
import io
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
from torch.utils.data import DataLoader

import interp
import effects
import overlays
import weather
from train import HIDDEN, Block, Upscaler

KEYS = 3  # captured frames per training window: the last two are the pair the in-between frames sit in
SPANS = {}


def set_keys(keys):
    global KEYS
    KEYS = keys
    SPANS.clear()
    SPANS.update({gap: (keys - 1) * gap for gap in set(interp.GAPS)})


set_keys(3)


def degrade(frames, quality, grain_rng=None):
    """[N, 3, H, W] in 0..1 -> [N, 3, H/2, W/2]: halved, sensor grain if grain_rng is given, then JPEG
    at the given quality (None = none)."""
    small = F.interpolate(frames, scale_factor=0.5, mode="bicubic", antialias=True, align_corners=False).clamp(0, 1)
    if grain_rng is not None:
        small = weather.grain(small, grain_rng)
    if quality is None:
        return small
    out = []
    for frame in small:
        image = Image.fromarray((frame.permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8))
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=quality, subsampling=2)
        out.append(torch.from_numpy(np.asarray(Image.open(buffer).convert("RGB"), dtype=np.float32).copy()).permute(2, 0, 1) / 255)
    return torch.stack(out)


def random_quality():
    return None if random.random() < 0.2 else random.randint(25, 90)


class Windows(interp.Pairs):
    """2 * gap + 1 frames: the frame before the pair (for the upscaler's previous frame and state),
    the pair, and the in-between targets. A share of them get rain or snow (weather) and a share get
    sensor grain on the captured frames only (grain), and a share game effects or moving vegetation
    (effects)."""
    weather = 0.0
    grain = 0.0
    effects = 0.0

    def clip(self, path):
        if path not in self.open:
            data = np.load(path, mmap_mode="r")
            cuts = interp.cuts_of(path)
            self.open[path] = (data, {span: interp.valid_starts(len(data), cuts, span) for span in SPANS.values()})
        return self.open[path]

    def window_counts(self):
        return {name: {gap: sum(len(self.clip(p)[1][span]) for p in paths) for gap, span in sorted(SPANS.items())}
                for name, paths in (("reds", self.sets[0]), ("games", self.sets[1]))}

    def __getitem__(self, _):
        gap = random.choice(interp.GAPS)
        span = SPANS[gap]
        frames = self.patch_frames(span)
        if random.random() < self.overlay:
            overlays.apply(frames, random, lambda: self.patch_frames(span))
        if random.random() < self.weather:
            weather.apply(frames, random)
        if random.random() < self.effects:
            effects.apply(frames, random)
        keys = frames[[k * gap for k in range(KEYS)]]
        small = degrade(keys, random_quality(), random if random.random() < self.grain else None)
        picks = [random.randrange(1, gap) for _ in range(interp.TARGETS)]
        targets = torch.stack([frames[(KEYS - 2) * gap + k] for k in picks])
        times = torch.tensor([k / gap for k in picks])
        return small, keys[1:], targets, times


def synthesize(a, b, motion, t):
    """interp.synthesize for frames larger than the ones the motion was measured on: the motion is in
    pixels of its own quarter grid, as framegen.js's PRESENT_SHADER reads it."""
    n, _, h, w = a.shape
    f = F.interpolate(motion[:, :5], size=(h, w), mode="bilinear", align_corners=False)
    grid = torch.tensor([motion.shape[-1], motion.shape[-2]], device=a.device, dtype=a.dtype).view(1, 2, 1, 1)
    f01, f10 = f[:, 0:2] / grid, f[:, 2:4] / grid
    m = torch.sigmoid(f[:, 4:5])
    t = t.view(-1, 1, 1, 1)
    ft0 = -(1 - t) * t * f01 + t * t * f10
    ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10
    wa, wb = (1 - t) * m, t * (1 - m)
    return (wa * interp.warp(a, ft0) + wb * interp.warp(b, ft1)) / (wa + wb).clamp_min(1e-4)


def bilinear2(x):
    return F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)


def align(big, motion):
    """The previous upscaled frame moved onto the current one: sampled where the 1->0 motion (in
    pixels of its quarter grid) points, bilinear and clamped, as framegen-sr.js's aligned unpack does."""
    n, _, h, w = big.shape
    f = F.interpolate(motion[:, 2:4], size=(h, w), mode="bilinear", align_corners=False)
    grid = torch.tensor([motion.shape[-1], motion.shape[-2]], device=big.device, dtype=big.dtype).view(1, 2, 1, 1)
    return interp.warp(big, f / grid)


class AlignedUpscaler(nn.Module):
    """x2 upscaler fed with the current frame (unpacked 2x2 to half resolution), the previous upscaled
    frame aligned to it (unpacked 4x4 to the same grid) and a recurrent state."""

    def __init__(self, channels=32, blocks=4):
        super().__init__()
        self.head = nn.Conv2d(3 * 4 + 3 * 16 + HIDDEN, channels, 1)
        self.blocks = nn.Sequential(*[Block(channels) for _ in range(blocks)])
        self.tail = nn.Conv2d(channels, 3 * 16 + HIDDEN, 1)

    def step(self, current, previous_big, state):
        x = torch.cat([F.pixel_unshuffle(current, 2), F.pixel_unshuffle(previous_big, 4), state], 1)
        y = self.tail(self.blocks(F.relu(self.head(x))))
        residual, state = y[:, :48], torch.tanh(y[:, 48:])
        return bilinear2(current) + F.pixel_shuffle(residual, 4), state


class Joint(nn.Module):
    def __init__(self, sr_channels=32, sr_blocks=4, fi_shape="32,64,2,2,4,1", aligned=False, skip_align=0.15):
        super().__init__()
        c1, c2, b1, b2, b3, bu = (int(x) for x in fi_shape.split(","))
        self.aligned = aligned
        self.skip_align = skip_align
        self.sr = (AlignedUpscaler if aligned else Upscaler)(sr_channels, sr_blocks)
        self.fi = interp.Interpolator(c1, c2, b1, b2, b3, bu)
        self.shape = {"sr": {"channels": sr_channels, "blocks": sr_blocks, "aligned": aligned}, "fi": self.fi.shape}

    def forward(self, small, times):
        """small: [N, K, 3, h, w], the captured frames in order. Returns the upscaled frames after the
        first [N, K-1, 3, 2h, 2w] and the in-between frames of the last pair [N, T, 3, 2h, 2w]."""
        frames = small.unbind(1)
        n, _, h, w = frames[0].shape
        state = torch.zeros(n, HIDDEN, h // 2, w // 2, device=small.device, dtype=small.dtype)
        if self.aligned:
            big, state = self.sr.step(frames[0], bilinear2(frames[0]), state)
        else:
            big, state = self.sr.step(frames[0], frames[0], state)
        bigs, motion = [], None
        for k in range(1, len(frames)):
            motion = self.fi.motion(frames[k - 1], frames[k])
            if self.aligned:
                skip = self.training and random.random() < self.skip_align
                previous = bilinear2(frames[k]) if skip else align(big, motion)
                big, state = self.sr.step(frames[k], previous, state)
            else:
                big, state = self.sr.step(frames[k], frames[k - 1], state)
            bigs.append(big)
        mids = torch.stack([synthesize(bigs[-2], bigs[-1], motion, times[:, k]) for k in range(times.shape[1])], 1)
        return torch.stack(bigs, 1), mids, motion


class Critic(nn.Module):
    """Patch discriminator, spectral-normalised, from scratch."""

    def __init__(self, width=48):
        super().__init__()
        sn = nn.utils.spectral_norm
        self.net = nn.Sequential(
            sn(nn.Conv2d(3, width, 3, 1, 1)), nn.LeakyReLU(0.2),
            sn(nn.Conv2d(width, width * 2, 4, 2, 1)), nn.LeakyReLU(0.2),
            sn(nn.Conv2d(width * 2, width * 4, 4, 2, 1)), nn.LeakyReLU(0.2),
            sn(nn.Conv2d(width * 4, width * 4, 4, 2, 1)), nn.LeakyReLU(0.2),
            sn(nn.Conv2d(width * 4, 1, 3, 1, 1)))

    def forward(self, x):
        return self.net(x * 2 - 1)


def generator_loss(model, batch, device, temporal_weight, smooth_weight):
    small, keys, targets, times = (x.to(device, non_blocking=True) for x in batch)
    bigs, mids, motion = model(small, times)
    pixels = (interp.charbonnier(bigs, keys) + interp.charbonnier(mids, targets)) / 2
    temporal = interp.charbonnier(bigs[:, 1] - bigs[:, 0], keys[:, 1] - keys[:, 0])
    loss = pixels + temporal_weight * temporal + smooth_weight * interp.smoothness(motion)
    fakes = torch.cat([bigs.flatten(0, 1), mids.flatten(0, 1)])
    reals = torch.cat([keys.flatten(0, 1), targets.flatten(0, 1)])
    return loss, pixels.item(), fakes, reals


# ----- validation -----

def _center(frames, size):
    _, _, h, w = frames.shape
    s = min(size, h, w) // 32 * 32
    y, x = (h - s) // 2, (w - s) // 2
    return frames[:, :, y:y + s, x:x + s]


@torch.no_grad()
def validate(model, data, device, samples_dir=None, iteration=0, windows=4):
    """Fixed windows of REDS validation clips and of the games kept for validation, centre 512 crop,
    JPEG quality 60. Scores: upscaled key frame (key) against bicubic (key_bicubic), in-between frame
    (mid) against the cross-fade of the bicubic frames (mid_fade), for 60 and 30 fps sources. At 60
    fps the same windows are also scored with rain or snow drawn over them (kinds rain and snow)."""
    model.eval()
    sources = []
    roots = sorted(p for p in (data / "orig" / "val").iterdir() if p.is_dir())[:3]
    for root in roots:
        names = sorted(root.glob("*.png"))
        sources.append(("reds", lambda s, n, names=names: torch.stack([interp.load(names[s + k]) for k in range(n)]),
                        len(names), set()))
    for path in interp.packed(data / "packed120" / "games-val"):
        clip, cuts = np.load(path, mmap_mode="r"), interp.cuts_of(path)
        sources.append(("games", lambda s, n, clip=clip: torch.from_numpy(np.array(clip[s:s + n])).permute(0, 3, 1, 2).float() / 255,
                        len(clip), cuts))
    scores, sheet = {}, []
    for gap in (2, 4):
        span = SPANS[gap]
        acc = {}
        for index, (source_kind, read, count, cuts) in enumerate(sources):
            starts = interp.valid_starts(count, cuts, span)
            for number, start in enumerate([starts[int(i)] for i in np.linspace(0, len(starts) - 1, windows)] if starts else []):
                clean = _center(read(start, span + 1), 512)
                variants = [(source_kind, clean)]
                if gap == 2:
                    # at 60 fps every window is also scored with rain (even windows) or snow (odd
                    # ones), always the same drops for the same window
                    sky = "rain" if number % 2 == 0 else "snow"
                    variants.append((sky, weather.apply(clean.clone(), random.Random(1000 * index + number), sky)))
                    # and with one effect, a different one for each window (sparks, smoke, flash, foliage)
                    effect = effects.KINDS[number % len(effects.KINDS)]
                    variants.append((effect, effects.apply(clean.clone(), random.Random(5000 + 1000 * index + number), effect)))
                for kind, frames in variants:
                    keys = frames[[k * gap for k in range(KEYS)]]
                    small = degrade(keys, 60)[None].to(device)
                    times = torch.tensor([[0.5]], device=device)
                    target_mid = frames[(KEYS - 2) * gap + gap // 2][None].to(device)
                    bigs, mids, _ = model(small, times)
                    bicubic = F.interpolate(small[0], scale_factor=2, mode="bicubic", align_corners=False).clamp(0, 1)
                    fade = (bicubic[-2] + bicubic[-1]) / 2
                    key = keys[-1][None].to(device)
                    for name, value in (("key", interp.psnr(bigs[:, -1], key)), ("key_bicubic", interp.psnr(bicubic[-1:], key)),
                                        ("mid", interp.psnr(mids[:, 0], target_mid)), ("mid_fade", interp.psnr(fade[None], target_mid))):
                        acc.setdefault(f"fps{120 // gap}_{kind}_{name}", []).append(value)
                    # pictures at 60 fps: bicubic | ours | real, fade | ours | real; one per source from
                    # its second window, and rain and snow on the first REDS clip and the first game
                    weathered = kind in ("rain", "snow")
                    effected = kind in effects.KINDS
                    wanted = ((number == 1 and not weathered and not effected)
                              or (weathered and number in (1, 2) and index in (0, len(roots)))
                              or (effected and index == 0))
                    if samples_dir is not None and gap == 2 and wanted and len(sheet) < 16:
                        crop = lambda x: x[..., 64:320, 64:320]
                        row = torch.cat([crop(bicubic[-1]), crop(bigs[0, -1]), crop(key[0]), crop(fade), crop(mids[0, 0]), crop(target_mid[0])], 2)
                        sheet.append((kind, row.cpu()))
        for k, v in acc.items():
            scores[k] = round(sum(v) / len(v), 3)
    if samples_dir is not None and sheet:
        samples_dir.mkdir(parents=True, exist_ok=True)
        grid = torch.cat([row for _, row in sheet], 1).clamp(0, 1)
        Image.fromarray((grid.permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8)).save(samples_dir / f"it{iteration:06d}.png")
    model.train()
    return scores


def overall(scores):
    keys = [k for k in scores if k.startswith("fps60_") and (k.endswith("_key") or k.endswith("_mid"))]
    return sum(scores[k] for k in keys) / max(len(keys), 1)


def smoke():
    model = Joint(16, 2, "8,16,1,1,1,1", aligned=True)
    critic = Critic(8)
    optimizer = torch.optim.Adam(model.parameters(), 2e-4)
    for _ in range(3):
        hr = torch.rand(2, KEYS, 3, 64, 64)
        small = torch.stack([degrade(effects.apply(weather.apply(x.clone(), random), random), 50, random) for x in hr])
        batch = (small, hr[:, 1:], torch.rand(2, interp.TARGETS, 3, 64, 64), torch.rand(2, interp.TARGETS))
        loss, _, fakes, reals = generator_loss(model, batch, "cpu", 0.5, 0.01)
        loss = loss - 0.005 * critic(fakes).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print("smoke ok, parameters: sr", sum(p.numel() for p in model.sr.parameters()),
          "fi", sum(p.numel() for p in model.fi.parameters()), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=pathlib.Path)
    parser.add_argument("--run", type=pathlib.Path)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--sr", default="32,4", help="upscaler channels,blocks")
    parser.add_argument("--fi", default="32,64,2,2,4,1", help="interpolator shape")
    parser.add_argument("--init-fi", type=pathlib.Path,
                        help="start the motion network from this checkpoint (interp.py's, or a joint.py one: its fi part)")
    parser.add_argument("--init", type=pathlib.Path,
                        help="start the whole model (upscaler and motion) from this joint.py checkpoint")
    parser.add_argument("--weather", type=float, default=0.0, help="share of windows with rain or snow")
    parser.add_argument("--grain", type=float, default=0.0, help="share of windows with sensor grain on the captured frames")
    parser.add_argument("--effects", type=float, default=0.0, help="share of windows with a game effect or moving vegetation")
    parser.add_argument("--aligned", action="store_true", help="upscaler fed with the previous upscaled frame, aligned")
    parser.add_argument("--keys", type=int, default=3, help="captured frames per training window")
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--adversarial-from", type=int, default=40000)
    parser.add_argument("--adversarial", type=float, default=0.005)
    parser.add_argument("--critic-images", type=int, default=8, help="shown frames per batch the critic sees")
    parser.add_argument("--critic-crop", type=int, default=128, help="side of the crop the critic sees")
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--patch", type=int, default=256, help="full-resolution patch side")
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--fi-lr", type=float, default=1e-4)
    parser.add_argument("--temporal", type=float, default=0.5)
    parser.add_argument("--smooth", type=float, default=0.01)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--memory-fraction", type=float, default=0.42)
    parser.add_argument("--games-share", type=float, default=0.5)
    parser.add_argument("--overlay", type=float, default=0.4)
    args = parser.parse_args()
    set_keys(args.keys)
    if args.smoke:
        smoke()
        return

    channels, blocks = (int(x) for x in args.sr.split(","))
    torch.cuda.set_per_process_memory_fraction(args.memory_fraction)
    device = torch.device("cuda")
    args.run.mkdir(parents=True, exist_ok=True)
    model = Joint(channels, blocks, args.fi, aligned=args.aligned).to(device)
    critic = Critic().to(device)
    optimizer = torch.optim.Adam([{"params": model.sr.parameters(), "lr": args.lr},
                                  {"params": model.fi.parameters(), "lr": args.fi_lr}])
    critic_optimizer = torch.optim.Adam(critic.parameters(), 1e-4, betas=(0.5, 0.999))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, args.iterations, 1e-6)
    latest = args.run / "latest.pt"
    iteration = 0
    if latest.exists():
        saved = torch.load(latest, map_location=device)
        model.load_state_dict(saved["model"])
        critic.load_state_dict(saved["critic"])
        optimizer.load_state_dict(saved["optimizer"])
        critic_optimizer.load_state_dict(saved["critic_optimizer"])
        scheduler.load_state_dict(saved["scheduler"])
        iteration = saved["iteration"]
    elif args.init:
        model.load_state_dict(torch.load(args.init, map_location=device)["model"])
    elif args.init_fi:
        state = torch.load(args.init_fi, map_location=device)["model"]
        if any(k.startswith("fi.") for k in state):
            state = {k[3:]: v for k, v in state.items() if k.startswith("fi.")}
        model.fi.load_state_dict(state)
    windows = Windows(args.data, args.patch, 10 ** 9, args.games_share, args.overlay)
    windows.weather, windows.grain, windows.effects = args.weather, args.grain, args.effects
    loader = DataLoader(windows, batch_size=args.batch, num_workers=args.workers, pin_memory=True, persistent_workers=True)
    log = (args.run / "log.jsonl").open("a", encoding="utf-8")
    counts = {"iteration": iteration, "windows": windows.window_counts(), "shape": model.shape}
    print(json.dumps(counts), flush=True)
    log.write(json.dumps(counts) + "\n")
    if iteration == 0:
        line = {"iteration": 0, **validate(model, args.data, device, args.run / "samples", 0)}
        print(json.dumps(line), flush=True)
        log.write(json.dumps(line) + "\n")
    window = time.time()
    best = -1.0
    if (args.run / "best.json").exists():
        best = overall(json.loads((args.run / "best.json").read_text()))
    for batch in loader:
        if iteration >= args.iterations:
            break
        adversarial = iteration >= args.adversarial_from
        loss, pixels, fakes, reals = generator_loss(model, batch, device, args.temporal, args.smooth)
        critic_loss = 0.0
        if adversarial:
            # the critic sees a few of the shown frames, as random crops: all of them at full size
            # does not fit next to the other users of the GPU, and texture is judged locally anyway
            pick = torch.randperm(fakes.shape[0], device=fakes.device)[:args.critic_images]
            size = min(args.critic_crop, fakes.shape[-1], fakes.shape[-2])
            y = random.randrange(fakes.shape[-2] - size + 1)
            x = random.randrange(fakes.shape[-1] - size + 1)
            fakes = fakes[pick, :, y:y + size, x:x + size]
            reals = reals[pick, :, y:y + size, x:x + size]
            # critic: hinge loss on real frames against what is shown
            d_loss = F.relu(1 - critic(reals)).mean() + F.relu(1 + critic(fakes.detach())).mean()
            critic_optimizer.zero_grad(set_to_none=True)
            d_loss.backward()
            critic_optimizer.step()
            critic_loss = d_loss.item()
            loss = loss - args.adversarial * critic(fakes).mean()
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        iteration += 1
        if iteration % 100 == 0:
            rate = 100 / (time.time() - window)
            window = time.time()
            line = {"iteration": iteration, "loss": round(loss.item(), 5), "pixels": round(pixels, 5), "critic": round(critic_loss, 4),
                    "per_second": round(rate, 2), "vram_mb": round(torch.cuda.max_memory_allocated() / 1e6)}
            print(json.dumps(line), flush=True)
            log.write(json.dumps(line) + "\n")
            log.flush()
        if iteration % 2000 == 0:
            scores = validate(model, args.data, device, args.run / "samples", iteration)
            line = {"iteration": iteration, **scores}
            print(json.dumps(line), flush=True)
            log.write(json.dumps(line) + "\n")
            log.flush()
            state = {"model": model.state_dict(), "critic": critic.state_dict(), "optimizer": optimizer.state_dict(),
                     "critic_optimizer": critic_optimizer.state_dict(), "scheduler": scheduler.state_dict(),
                     "iteration": iteration, "shape": model.shape}
            torch.save(state, latest)
            if iteration % 10000 == 0:
                torch.save(state, args.run / f"it{iteration:06d}.pt")
            # the pixel-only phase keeps its best; once the critic joins, PSNR is no longer the judge
            if not adversarial and overall(scores) > best:
                best = overall(scores)
                torch.save(state, args.run / "best-pixels.pt")
                (args.run / "best.json").write_text(json.dumps(line))


if __name__ == "__main__":
    main()
