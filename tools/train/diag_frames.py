"""Saves frames start..start+gap of a packed clip side by side (top row) and a crop at full size
(bottom row), plus the absolute difference first-last, to look at what changes between them.

Usage: python diag_frames.py <clip.npy> <start> <gap> <out.png> [crop y x size]
"""
import sys

import numpy as np
from PIL import Image


def main():
    clip = np.load(sys.argv[1], mmap_mode="r")
    start, gap, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    cy, cx, size = (int(v) for v in sys.argv[5:8]) if len(sys.argv) > 7 else (200, 400, 320)
    frames = [np.array(clip[start + k]) for k in range(gap + 1)]
    diff = np.clip(np.abs(frames[-1].astype(int) - frames[0].astype(int)) * 4, 0, 255).astype(np.uint8)
    small = [np.array(Image.fromarray(f).resize((640, 360), Image.BILINEAR)) for f in frames + [diff]]
    crops = [f[cy:cy + size, cx:cx + size] for f in frames + [diff]]
    crops = [np.pad(c, ((0, 360 - c.shape[0]), (0, 640 - c.shape[1]), (0, 0))) for c in crops]
    Image.fromarray(np.concatenate([np.concatenate(small, 1), np.concatenate(crops, 1)], 0)).save(out)
    for k in range(1, gap + 1):
        print(f"frame {start + k}: mean change from previous {np.abs(frames[k].astype(int) - frames[k - 1].astype(int)).mean():.2f}")


if __name__ == "__main__":
    main()
