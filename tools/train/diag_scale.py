"""Does the size of the motion limit the model on game footage? Scores the game validation clips at
full size and scaled down (motion in pixels shrinks the same), model against fade. CPU only.

Usage: python diag_scale.py <data dir> <checkpoint.pt> [pairs per clip]
"""
import pathlib
import sys

import numpy as np
import torch
import torch.nn.functional as F

import interp


def main():
    data, checkpoint = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pairs = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    torch.set_num_threads(4)
    saved = torch.load(checkpoint, map_location="cpu")
    model = interp.Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    model.eval()
    clips = [(np.load(p, mmap_mode="r"), interp.cuts_of(p)) for p in interp.packed(data / "packed120" / "games-val")]
    with torch.no_grad():
        for scale in (1.0, 0.5, 0.25):
            for gap in (2, 4):
                ours, fade = [], []
                for clip, cuts in clips:
                    for start in np.linspace(0, len(clip) - gap - 1, pairs).astype(int):
                        while start + gap < len(clip) - 1 and cuts.intersection(range(start, start + gap)):
                            start += 1
                        frames = torch.from_numpy(np.array(clip[start:start + gap + 1])).permute(0, 3, 1, 2).float() / 255
                        if scale != 1.0:
                            h, w = frames.shape[2:]
                            size = (int(h * scale) // 16 * 16, int(w * scale) // 16 * 16)
                            frames = F.interpolate(frames, size=size, mode="bilinear", antialias=True, align_corners=False)
                        else:
                            frames = frames[:, :, :frames.shape[2] // 16 * 16, :frames.shape[3] // 16 * 16]
                        interp.score(model, frames, gap, ours, fade)
                print(f"scale {scale:4.2f} gap {gap}: ours {np.mean(ours):.2f}  fade {np.mean(fade):.2f}  gain {np.mean(ours) - np.mean(fade):+.2f}")


if __name__ == "__main__":
    main()
