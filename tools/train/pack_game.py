"""Cuts a 120 fps game recording from xonotic_capture.sh into training clips for interp.py.

The recording is decoded once at low resolution to find the camera switches and the still
stretches (the spectator camera before it follows a bot). A switch is a frame whose picture as a
whole has almost nothing to do with the one before (correlation of the luma under 0.25). Of the
stretches between switches it keeps up to --keep of the busiest, LENGTH frames each, taken from
the middle, and writes each as data/packed120/<set>/<name>.npy (frames, 720, 1280, 3) like
pack120.py.

Quick turns and muzzle flashes in a first person shooter can look much like a switch, so the
doubtful steps inside a clip (correlation under 0.45) are written to <name>.cuts.npy (index i
means between frame i and i + 1) and interp.py never takes a pair across them.

Usage: python pack_game.py <video.avi> <data dir> [--set games] [--keep 3] [--length 240] [--delete]
"""
import argparse
import pathlib
import subprocess

import numpy as np

PROBE = (160, 90)


def frames(path, size):
    """Yields the frames of a video as uint8 arrays at size (width, height), RGB."""
    w, h = size
    command = ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h}:flags=area",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=w * h * 3 * 8) as process:
        while True:
            data = process.stdout.read(w * h * 3)
            if len(data) < w * h * 3:
                break
            yield np.frombuffer(data, np.uint8).reshape(h, w, 3)


def video_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout
    w, h = (int(x) for x in out.strip().split(","))
    return w, h


def correlation(small):
    """Correlation of the luma of each frame with the next one."""
    g = small.mean(axis=3)
    g = g - g.mean(axis=(1, 2), keepdims=True)
    g = g / (np.sqrt((g ** 2).mean(axis=(1, 2), keepdims=True)) + 1e-3)
    return (g[1:] * g[:-1]).mean(axis=(1, 2))


def stretches(corr, length):
    """Runs of frames with no switch inside, as (start, end) frame indices, end exclusive."""
    n = len(corr) + 1
    cuts = [0] + [i + 1 for i in np.flatnonzero(corr < 0.25)] + [n]
    runs = []
    for start, end in zip(cuts, cuts[1:]):
        start, end = start + 30, end - 30          # stay clear of the switch
        if end - start >= length:
            runs.append((start, end))
    return runs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=pathlib.Path)
    parser.add_argument("data", type=pathlib.Path)
    parser.add_argument("--set", default="games")
    parser.add_argument("--keep", type=int, default=3)
    parser.add_argument("--length", type=int, default=240)
    parser.add_argument("--delete", action="store_true")
    args = parser.parse_args()

    small = np.stack(list(frames(args.video, PROBE))).astype(np.float32)
    diff = np.abs(small[1:] - small[:-1]).mean(axis=(1, 2, 3))
    corr = correlation(small)
    picks = []
    for start, end in stretches(corr, args.length):
        middle = (start + end - args.length) // 2
        motion = float(np.mean(diff[middle:middle + args.length - 1]))
        if motion >= 1.0:                          # not the still spectator camera
            picks.append((motion, middle))
    picks = sorted(picks, reverse=True)[:args.keep]
    print(f"{args.video.name}: {len(small)} frames, {len(picks)} clips "
          + ", ".join(f"{m}..{m + args.length} (motion {v:.1f})" for v, m in sorted(picks, key=lambda p: p[1])), flush=True)

    out_dir = args.data / "packed120" / args.set
    out_dir.mkdir(parents=True, exist_ok=True)
    size = video_size(args.video)
    wanted = {m: k for k, (_, m) in enumerate(sorted(picks, key=lambda p: p[1]))}
    current = None
    for index, frame in enumerate(frames(args.video, size)):
        if index in wanted:
            path = out_dir / f"{args.video.stem}-{wanted[index]}.partial.npy"
            current = (np.lib.format.open_memmap(path, mode="w+", dtype=np.uint8, shape=(args.length, size[1], size[0], 3)),
                       index, path)
        if current is not None:
            array, first, path = current
            array[index - first] = frame
            if index - first == args.length - 1:
                array.flush()
                del array
                final = path.with_name(path.name.replace(".partial", ""))
                np.save(final.with_suffix(".cuts.npy"), np.flatnonzero(corr[first:first + args.length - 1] < 0.45))
                path.rename(final)
                current = None
    if args.delete:
        args.video.unlink()


if __name__ == "__main__":
    main()
