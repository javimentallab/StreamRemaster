"""Per-pair look at the game validation clips: PSNR of the model and of the fade, whether the pair
crosses a cut (.cuts.npy), the mean frame change and the mean predicted motion. CPU only.

Usage: python diag_games.py <data dir> <checkpoint.pt> [pairs per clip]
"""
import pathlib
import sys

import numpy as np
import torch

import interp


def main():
    data, checkpoint = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pairs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    torch.set_num_threads(2)
    saved = torch.load(checkpoint, map_location="cpu")
    model = interp.Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    model.eval()
    rows = []
    with torch.no_grad():
        for path in interp.packed(data / "packed120" / "games-val"):
            clip, cuts = np.load(path, mmap_mode="r"), interp.cuts_of(path)
            for gap in (2, 4):
                for start in np.linspace(0, len(clip) - gap - 1, pairs).astype(int):
                    frames = torch.from_numpy(np.array(clip[start:start + gap + 1])).permute(0, 3, 1, 2).float() / 255
                    ours, fade = [], []
                    interp.score(model, frames, gap, ours, fade)
                    motion = model.motion(frames[:1], frames[-1:])[:, :2].abs().mean().item() * 4
                    change = (frames[-1] - frames[0]).abs().mean().item() * 255
                    crosses = bool(cuts.intersection(range(int(start), int(start) + gap)))
                    rows.append((path.stem, gap, int(start), crosses, change, motion, np.mean(ours), np.mean(fade)))
    print(f"shape {tuple(clip.shape)}  checkpoint {checkpoint}  iteration {saved['iteration']}")
    print("clip                          gap start cut  change  motion_px   ours   fade   diff")
    for name, gap, start, crosses, change, motion, ours, fade in rows:
        print(f"{name:29s} {gap:3d} {start:5d} {'X' if crosses else '.':>3s} {change:7.2f} {motion:9.2f} {ours:6.2f} {fade:6.2f} {ours - fade:+6.2f}")
    for gap in (2, 4):
        for label, keep in (("all", lambda r: True), ("no cut", lambda r: not r[3])):
            sel = [r for r in rows if r[1] == gap and keep(r)]
            if sel:
                print(f"gap {gap} {label:7s} n={len(sel):3d} ours {np.mean([r[6] for r in sel]):.3f} fade {np.mean([r[7] for r in sel]):.3f}")


if __name__ == "__main__":
    main()
