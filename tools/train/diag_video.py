"""Gain of a checkpoint over the plain fade on a video, pair by pair: windows of gap + 1 frames taken
every `every` frames, skipping windows with a camera switch or flash (a step far above the others).
CPU only. The frames are cropped to multiples of 16.

Usage: python diag_video.py <video> <checkpoint.pt>[,<checkpoint.pt>...] [every]
"""
import subprocess
import sys

import numpy as np
import torch

import interp


def size_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
    w, h = (int(v) for v in out.strip().split(","))
    return w, h


def main():
    path, checkpoints = sys.argv[1], sys.argv[2].split(",")
    every = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    torch.set_num_threads(4)
    models = []
    for c in checkpoints:
        saved = torch.load(c, map_location="cpu")
        m = interp.Interpolator(**saved["shape"])
        m.load_state_dict(saved["model"])
        models.append(m.eval())
    w, h = size_of(path)
    cw, ch = w // 16 * 16, h // 16 * 16
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"crop={cw}:{ch}", "-f", "rawvideo",
                             "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frame_bytes = cw * ch * 3
    buffer, index = [], 0
    results = {gap: [[] for _ in range(len(models) + 1)] for gap in (2, 4)}
    with torch.no_grad():
        while True:
            raw = proc.stdout.read(frame_bytes)
            if len(raw) < frame_bytes:
                break
            buffer.append(np.frombuffer(raw, np.uint8).reshape(ch, cw, 3))
            buffer = buffer[-5:]
            index += 1
            if index % every or len(buffer) < 5:
                continue
            frames = torch.from_numpy(np.stack(buffer)).permute(0, 3, 1, 2).float() / 255
            steps = (frames[1:] - frames[:-1]).abs().mean(dim=(1, 2, 3))
            if steps.min() < 1 / 255 or steps.max() > 2.5 * steps.median():
                continue          # still, or a switch / flash inside the window
            for gap in (2, 4):
                window = frames[:gap + 1]
                for n, m in enumerate(models):
                    ours, fade = [], []
                    interp.score(m, window, gap, ours, fade)
                    results[gap][n].append(np.mean(ours))
                results[gap][-1].append(np.mean(fade))
    for gap, columns in results.items():
        fade = np.mean(columns[-1])
        gains = "  ".join(f"{c.split('/')[-2]} {np.mean(col):.2f} ({np.mean(col) - fade:+.2f})"
                          for c, col in zip(checkpoints, columns[:-1]))
        print(f"gap {gap}  n={len(columns[-1])}  fade {fade:.2f}  {gains}")


if __name__ == "__main__":
    main()
