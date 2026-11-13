"""Finds the game frames that are not evenly spaced in time. For every frame k of a packed clip, the
model makes the frame at many instants t between k - 1 and k + 1 (at a quarter of the size, where
it follows the motion best) and keeps the t that matches frame k best. An evenly captured frame
sits at t = 0.5. Saves the t of every frame as <clip>.phase.npy (NaN where it cannot be told: the
ends, still frames, or no clear best) and, with --tolerance, the frames further than that from 0.5
as <clip>.offtime.npy, in the format of .cuts.npy (transitions k - 1 and k), which interp.py does
not cross. CPU only.

Usage: python time_phase.py <checkpoint.pt> <clip.npy>... [--tolerance 0.08] [--threads 8]
"""
import argparse
import pathlib
import time

import numpy as np
import torch
import torch.nn.functional as F

import interp

TIMES = np.round(np.arange(0.2, 0.8001, 0.04), 3)


def phases(model, clip):
    n, h, w, _ = clip.shape
    size = (h // 64 * 16, w // 64 * 16)
    small = []
    for k in range(n):
        frame = torch.from_numpy(np.array(clip[k])).permute(2, 0, 1)[None].float() / 255
        small.append(F.interpolate(frame, size=size, mode="bilinear", antialias=True, align_corners=False))
    result = np.full(n, np.nan, np.float32)
    times = torch.tensor(TIMES, dtype=torch.float32)
    for k in range(1, n - 1):
        a, real, b = small[k - 1], small[k], small[k + 1]
        if (b - a).abs().mean().item() < 1 / 255:
            continue
        motion = model.motion(a, b)
        frames = interp.synthesize(a.expand(len(TIMES), -1, -1, -1), b.expand(len(TIMES), -1, -1, -1),
                                   motion.expand(len(TIMES), -1, -1, -1), times)
        scores = -10 * torch.log10(((frames.clamp(0, 1) - real) ** 2).mean(dim=(1, 2, 3)).clamp_min(1e-10))
        best = int(scores.argmax())
        if scores[best] - scores.min() < 0.3:      # flat: the motion does not tell the instant
            continue
        result[k] = TIMES[best]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=pathlib.Path)
    parser.add_argument("clips", type=pathlib.Path, nargs="+")
    parser.add_argument("--tolerance", type=float)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    saved = torch.load(args.checkpoint, map_location="cpu")
    model = interp.Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    model.eval()
    with torch.no_grad():
        for path in args.clips:
            started = time.time()
            side = path.with_suffix(".phase.npy")
            if side.exists():
                t = np.load(side)
            else:
                t = phases(model, np.load(path, mmap_mode="r"))
                np.save(side, t)
            known = ~np.isnan(t)
            line = (f"{path.name}: known {known.mean() * 100:.0f}%  within 0.45-0.55 "
                    f"{np.mean(np.abs(t[known] - 0.5) < 0.051) * 100 if known.any() else 0:.0f}%  "
                    f"({time.time() - started:.0f} s)")
            if args.tolerance is not None:
                late = np.flatnonzero(known & (np.abs(t - 0.5) > args.tolerance))
                cuts = sorted(set((late - 1).tolist()) | set(late.tolist()))
                np.save(path.with_suffix(".offtime.npy"), np.array(cuts, dtype=np.int64))
                line += f"  off time {len(late)} frames"
            print(line, flush=True)


if __name__ == "__main__":
    main()
