"""Where in the picture a 60 Hz alternation (one step big, the next small) lives: per pixel, the
energy of the frame-to-frame change at the alternating frequency, summed over short windows so a
drifting phase does not cancel it. Saves a heat map next to a frame, and prints the share of that
energy in each region of a 4 x 4 grid.

Usage: python diag_alternation.py <video> <out.png> [frames]
"""
import subprocess
import sys

import numpy as np
from PIL import Image

W, H, WINDOW = 320, 180, 16


def main():
    path, out = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    if path.endswith(".npy"):
        clip = np.load(path, mmap_mode="r")[:limit]
        sy, sx = max(1, clip.shape[1] // H), max(1, clip.shape[2] // W)
        frames = np.stack([np.asarray(f[::sy, ::sx][:H, :W], np.float32) @ np.float32([0.299, 0.587, 0.114])
                           for f in clip])
    else:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-frames:v", str(limit), "-vf",
                              f"scale={W}:{H}:flags=area", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True, check=True).stdout
        frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    d = np.abs(np.diff(frames, axis=0))
    sign = np.where(np.arange(WINDOW) % 2 == 0, 1.0, -1.0)[:, None, None]
    alt = np.zeros((H, W), np.float32)
    total = np.zeros((H, W), np.float32)
    for start in range(0, len(d) - WINDOW, WINDOW):
        block = d[start:start + WINDOW]
        alt += np.abs((block * sign).sum(0)) / WINDOW
        total += block.mean(0)
    heat = alt / max(alt.max(), 1e-6)
    ratio = alt / np.maximum(total, 1e-3)
    picture = np.concatenate([frames[len(frames) // 2] / 255, heat, np.clip(ratio, 0, 1)], 1)
    Image.fromarray((picture * 255).astype(np.uint8)).save(out)
    print(f"alternating energy / total change, whole picture: {alt.sum() / total.sum():.3f}")
    for gy in range(4):
        cells = []
        for gx in range(4):
            ys, xs = slice(gy * H // 4, (gy + 1) * H // 4), slice(gx * W // 4, (gx + 1) * W // 4)
            cells.append(f"{alt[ys, xs].sum() / max(total[ys, xs].sum(), 1e-3):.2f}")
        print("   " + "  ".join(cells))


if __name__ == "__main__":
    main()
