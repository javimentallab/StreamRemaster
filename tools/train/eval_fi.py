"""Scores several interpolation checkpoints on the same validation windows (CPU only), so runs trained
with different data filters can be compared: once with every game window (offtime frames crossed)
and once without the frames time_phase.py marked as off time.

Usage: python eval_fi.py <data dir> <pairs per clip> <checkpoint.pt> [<checkpoint.pt> ...]
"""
import json
import pathlib
import sys

import torch

import interp


def main():
    data, pairs = pathlib.Path(sys.argv[1]), int(sys.argv[2])
    checkpoints = [pathlib.Path(p) for p in sys.argv[3:]]
    torch.set_num_threads(4)
    device = torch.device("cpu")
    for mode in ("all", "sync"):
        if mode == "all" and ".offtime.npy" in interp.SIDE_CUTS:
            interp.SIDE_CUTS.remove(".offtime.npy")
        if mode == "sync" and ".offtime.npy" not in interp.SIDE_CUTS:
            interp.SIDE_CUTS.append(".offtime.npy")
        for path in checkpoints:
            saved = torch.load(path, map_location="cpu")
            model = interp.Interpolator(**saved["shape"])
            model.load_state_dict(saved["model"])
            scores = interp.validate(model, data, device, pairs=pairs)
            gains = {k: round(scores[k] - scores[k + "_fade"], 2) for k in scores if not k.endswith("_fade")}
            print(json.dumps({"games": mode, "run": path.parent.name, "gain": gains}), flush=True)


if __name__ == "__main__":
    main()
