"""Picture of where the model fails on a video: scans windows of 3 frames (gap 2) like diag_video.py,
then saves the median one and the worst one (by model minus fade) as a grid:
  first | real middle | last
  fade  | model       | |model - real| x 4
and prints the motion the model found.

Usage: python diag_visual.py <video> <checkpoint.pt> <out prefix> [every]
"""
import subprocess
import sys

import numpy as np
import torch
from PIL import Image

import interp
from diag_video import size_of


def grid(frames, fade, ours):
    to = lambda x: (x.clamp(0, 1).permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    err = ((ours - frames[1]).abs() * 4).clamp(0, 1)
    top = np.concatenate([to(frames[0]), to(frames[1]), to(frames[2])], 1)
    bottom = np.concatenate([to(fade), to(ours), to(err)], 1)
    return np.concatenate([top, bottom], 0)


def main():
    path, checkpoint, prefix = sys.argv[1:4]
    every = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    torch.set_num_threads(4)
    saved = torch.load(checkpoint, map_location="cpu")
    model = interp.Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    model.eval()
    w, h = size_of(path)
    cw, ch = w // 16 * 16, h // 16 * 16
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"crop={cw}:{ch}", "-f", "rawvideo",
                             "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = cw * ch * 3
    buffer, index, found = [], 0, []
    t = torch.tensor([0.5])
    with torch.no_grad():
        while True:
            raw = proc.stdout.read(size)
            if len(raw) < size:
                break
            buffer = (buffer + [np.frombuffer(raw, np.uint8).reshape(ch, cw, 3)])[-3:]
            index += 1
            if index % every or len(buffer) < 3:
                continue
            frames = torch.from_numpy(np.stack(buffer)).permute(0, 3, 1, 2).float() / 255
            steps = (frames[1:] - frames[:-1]).abs().mean(dim=(1, 2, 3))
            if steps.min() < 1 / 255 or steps.max() > 2.5 * steps.min():
                continue
            a, b = frames[:1], frames[2:]
            motion = model.motion(a, b)
            ours = interp.synthesize(a, b, motion, t)[0]
            fade = (a[0] + b[0]) / 2
            gain = interp.psnr(ours[None], frames[1:2]) - interp.psnr(fade[None], frames[1:2])
            pixels = motion[0, :2].norm(dim=0) * 4      # quarter-grid px to full px
            found.append((gain, index, frames, fade, ours, pixels.mean().item(), pixels.max().item(),
                          torch.sigmoid(motion[0, 4]).mean().item()))
    found.sort(key=lambda r: r[0])
    for label, row in (("worst", found[0]), ("median", found[len(found) // 2]), ("best", found[-1])):
        gain, idx, frames, fade, ours, mean_px, max_px, mask = row
        Image.fromarray(grid(frames, fade, ours)).save(f"{prefix}-{label}.png")
        print(f"{label:6s} frame {idx}  gain {gain:+.2f} dB  motion mean {mean_px:.2f} px max {max_px:.1f} px  mask mean {mask:.2f}")
    for low, high in ((0, 2), (2, 4), (4, 8), (8, 100)):
        sel = [r[0] for r in found if low <= r[5] < high]
        if sel:
            print(f"   motion {low}-{high} px: n={len(sel):3d}  median gain {np.median(sel):+.2f}")
    print(f"windows {len(found)}  median gain {found[len(found) // 2][0]:+.2f}  share with gain > 0: "
          f"{np.mean([r[0] > 0 for r in found]) * 100:.0f}%")


if __name__ == "__main__":
    main()
