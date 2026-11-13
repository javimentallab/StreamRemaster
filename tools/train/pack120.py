"""Stores each 120 fps training clip (data/orig/train/<clip>/*.png) as one uncompressed array in
data/packed120/train/<clip>.npy, so a random crop is a memory read instead of decoding PNGs, and then
removes the PNGs of that clip (they can be downloaded again with fetch_reds120.sh).

Usage: python pack120.py <data dir>
"""
import concurrent.futures
import pathlib
import shutil
import sys

import numpy as np
from PIL import Image

DATA = pathlib.Path(sys.argv[1]).resolve()
WORKERS = 4


def pack(clip):
    out = DATA / "packed120" / "train" / f"{clip.name}.npy"
    names = sorted(clip.glob("*.png"))
    if not out.exists():
        first = np.asarray(Image.open(names[0]).convert("RGB"))
        partial = out.with_suffix(".partial.npy")
        array = np.lib.format.open_memmap(partial, mode="w+", dtype=np.uint8, shape=(len(names), *first.shape))
        for i, name in enumerate(names):
            array[i] = np.asarray(Image.open(name).convert("RGB"))
        array.flush()
        del array
        partial.rename(out)
    shutil.rmtree(clip)
    return clip.name


def main():
    (DATA / "packed120" / "train").mkdir(parents=True, exist_ok=True)
    clips = sorted(path for path in (DATA / "orig" / "train").iterdir() if path.is_dir())
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
        for done, name in enumerate(pool.map(pack, clips), 1):
            print(done, "/", len(clips), name, flush=True)
    print("packed", flush=True)


main()
