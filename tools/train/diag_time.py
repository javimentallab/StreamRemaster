"""Is the real middle frame really in the middle? For each pair (gap 2) of a set of clips, makes the
model's frame at many instants t and keeps the one closest to the real middle frame. If the best t
wanders away from 0.5, the footage is not evenly spaced in time and no interpolation can get it
right at t = 0.5. CPU only, at half size.

Usage: python diag_time.py <folder of packed clips> <checkpoint.pt> [pairs per clip] [max clips]
"""
import pathlib
import sys

import numpy as np
import torch
import torch.nn.functional as F

import interp

TIMES = np.linspace(0.1, 0.9, 17)


def main():
    folder, checkpoint = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pairs = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    torch.set_num_threads(4)
    saved = torch.load(checkpoint, map_location="cpu")
    model = interp.Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    model.eval()
    best_t, at_half, at_best, fade_half = [], [], [], []
    with torch.no_grad():
        for path in interp.packed(folder)[:limit]:
            clip, cuts = np.load(path, mmap_mode="r"), interp.cuts_of(path)
            for start in np.linspace(0, len(clip) - 3, pairs).astype(int):
                while start + 2 < len(clip) - 1 and cuts.intersection(range(start, start + 2)):
                    start += 1
                frames = torch.from_numpy(np.array(clip[start:start + 3])).permute(0, 3, 1, 2).float() / 255
                h, w = frames.shape[2:]
                frames = F.interpolate(frames, size=(h // 32 * 16, w // 32 * 16), mode="bilinear", antialias=True,
                                       align_corners=False)
                a, real, b = frames[:1], frames[1:2], frames[2:]
                motion = model.motion(a, b)
                scores = [interp.psnr(interp.synthesize(a, b, motion, torch.tensor([t], dtype=torch.float32)), real) for t in TIMES]
                k = int(np.argmax(scores))
                best_t.append(TIMES[k])
                at_best.append(scores[k])
                at_half.append(scores[8])
                fade_half.append(interp.psnr((a + b) / 2, real))
    best_t = np.array(best_t)
    print(f"{folder.name}: pairs {len(best_t)}  best t: median {np.median(best_t):.2f}, "
          f"share within 0.45-0.55 {np.mean(np.abs(best_t - 0.5) < 0.051) * 100:.0f}%, "
          f"mean |t-0.5| {np.mean(np.abs(best_t - 0.5)):.3f}")
    print(f"   PSNR at t=0.5 {np.mean(at_half):.2f}  at best t {np.mean(at_best):.2f}  fade {np.mean(fade_half):.2f}")
    print("   histogram of best t:", np.histogram(best_t, bins=[0, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 1])[0].tolist())


if __name__ == "__main__":
    main()
