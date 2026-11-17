"""Makes the checkpoint time_phase.py needs (an interp.py Interpolator) from the motion network of a
joint.py checkpoint: the "fi." part of its model, with its shape.

Usage: python phase_judge.py <joint.py checkpoint.pt> <output.pt>
"""
import sys

import torch


def main():
    saved = torch.load(sys.argv[1], map_location="cpu")
    state = {k[3:]: v for k, v in saved["model"].items() if k.startswith("fi.")}
    if not state:
        raise SystemExit("no motion network in that checkpoint")
    torch.save({"model": state, "shape": saved["shape"]["fi"]}, sys.argv[2])
    print("saved", sys.argv[2], saved["shape"]["fi"])


if __name__ == "__main__":
    main()
