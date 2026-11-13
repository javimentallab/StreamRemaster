"""Frame cadence of packed clips: the mean change between consecutive frames, to spot repeated
frames or uneven steps (a capture at 120 fps of a game that updates less often).

Usage: python diag_cadence.py <clip.npy>...
"""
import sys

import numpy as np


def main():
    for path in sys.argv[1:]:
        clip = np.load(path, mmap_mode="r")
        changes = []
        for k in range(1, len(clip)):
            a = np.asarray(clip[k - 1, ::4, ::4], dtype=np.int16)
            b = np.asarray(clip[k, ::4, ::4], dtype=np.int16)
            changes.append(np.abs(b - a).mean())
        c = np.array(changes)
        still = c < 0.15 * np.median(c)
        # how even the steps are: the change of each frame relative to the mean of its neighbours
        ratio = c[1:-1] / np.maximum((c[:-2] + c[2:]) / 2, 1e-3)
        print(f"{path.split('/')[-1]:34s} median {np.median(c):5.2f}  near-repeats {still.mean() * 100:5.1f}%  "
              f"uneven(|ratio-1|>0.5) {(np.abs(ratio - 1) > 0.5).mean() * 100:5.1f}%")
        print("   first 48:", " ".join(f"{v:.1f}" for v in c[:48]))


if __name__ == "__main__":
    main()
