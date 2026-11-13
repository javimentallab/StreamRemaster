"""Stores each training clip as one uncompressed array, so that a random crop costs a memory read
instead of decoding whole PNGs.

Usage: python pack.py <data dir>   (after prepare.py)
"""
import concurrent.futures
import pathlib
import sys

import numpy as np
from PIL import Image

DATA = pathlib.Path(sys.argv[1]).resolve()
WORKERS = 8


def read(folder, names):
    return np.stack([np.asarray(Image.open(folder / name).convert("RGB"), dtype=np.uint8) for name in names])


def pack(low_clip):
    output = DATA / "packed" / "train"
    low_path, high_path = output / f"{low_clip.name}_lr.npy", output / f"{low_clip.name}_hr.npy"
    if low_path.exists() and high_path.exists():
        return
    high_clip = DATA / "train" / "train_sharp" / low_clip.name
    names = sorted(path.name for path in low_clip.glob("*.png") if (high_clip / path.name).exists())
    np.save(high_path, read(high_clip, names))
    np.save(low_path, read(low_clip, names))


def main():
    (DATA / "packed" / "train").mkdir(parents=True, exist_ok=True)
    clips = sorted(path for path in (DATA / "lr" / "train").iterdir() if path.is_dir())
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
        for done, _ in enumerate(pool.map(pack, clips), 1):
            if done % 40 == 0:
                print(done, "/", len(clips), flush=True)
    print("packed", flush=True)


main()
