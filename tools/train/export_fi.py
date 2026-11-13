"""Writes an interpolation checkpoint as a model file for the extension: "FIM1", the length of a JSON
header, the header padded to four bytes, then the weights as little-endian 32-bit floats, in the
order extension/shared/framegen-fi.js reads them. The motion scale is folded into the last layer.

Usage: python export_fi.py <checkpoint.pt> <output.fimodel> <model name>
"""
import json
import pathlib
import struct
import sys

import torch

from interp import FLOW_SCALE, Interpolator


def keys(shape):
    out = ["head"]
    blocks = lambda prefix, n: [f"{prefix}.{i}.{part}" for i in range(n) for part in ("depthwise", "mix")]
    out += blocks("level4", shape["b1"]) + ["down8"] + blocks("level8", shape["b2"]) + ["down16"]
    out += blocks("level16", shape["b3"]) + ["up8"] + blocks("after8", shape["bu"]) + ["up4"]
    out += blocks("after4", shape["bu"]) + ["tail"]
    return out


def fi_bytes(state, shape, name, iteration):
    """The .fimodel file for an Interpolator state dict (keys without prefix)."""
    tensors = []
    for key in keys(shape):
        weight, bias = state[f"{key}.weight"].float().clone(), state[f"{key}.bias"].float().clone()
        if key == "tail":
            weight[:4] *= FLOW_SCALE
            bias[:4] *= FLOW_SCALE
        tensors += [weight.flatten(), bias.flatten()]
    used = {f"{k}.{p}" for k in keys(shape) for p in ("weight", "bias")}
    assert used == set(state) - {"luma", "scale"}, sorted(used ^ (set(state) - {"luma", "scale"}))
    weights = torch.cat(tensors).numpy().astype("<f4").tobytes()
    header = json.dumps({"format": 1, "name": name, "shape": shape, "iteration": iteration}).encode("utf-8")
    header += b" " * ((4 - len(header) % 4) % 4)
    return b"FIM1" + struct.pack("<I", len(header)) + header + weights


def main():
    checkpoint, output, name = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
    saved = torch.load(checkpoint, map_location="cpu")
    model = Interpolator(**saved["shape"])
    model.load_state_dict(saved["model"])
    data = fi_bytes(model.state_dict(), saved["shape"], name, saved["iteration"])
    output.write_bytes(data)
    print(f"{output}: {output.stat().st_size} bytes, iteration {saved['iteration']}")


if __name__ == "__main__":
    main()
