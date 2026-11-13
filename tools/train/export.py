"""Writes a training checkpoint as a model file for the extension: "SRM1", the length of a JSON
header, the header padded to four bytes, then the weights as little-endian 32-bit floats.

Usage: python export.py <checkpoint.pt> <output.srmodel> <model name>
"""
import json
import pathlib
import struct
import sys

import torch

HIDDEN = 4


def sr_bytes(state, channels, blocks, name, iteration, aligned=False):
    """The .srmodel file for an Upscaler state dict (keys without prefix). Format 2 is joint.py's
    AlignedUpscaler: same layers, its head reads the aligned previous upscaled frame too."""
    keys = ["head.weight", "head.bias"]
    for i in range(blocks):
        keys += [f"blocks.{i}.depthwise.weight", f"blocks.{i}.depthwise.bias", f"blocks.{i}.mix.weight", f"blocks.{i}.mix.bias"]
    keys += ["tail.weight", "tail.bias"]
    assert set(keys) == set(state), sorted(set(keys) ^ set(state))
    weights = torch.cat([state[key].float().flatten() for key in keys]).numpy().astype("<f4").tobytes()
    header = json.dumps({"format": 2 if aligned else 1, "name": name, "scale": 2, "channels": channels, "blocks": blocks,
                         "hidden": HIDDEN, "aligned": bool(aligned), "iteration": iteration}).encode("utf-8")
    header += b" " * ((4 - len(header) % 4) % 4)
    return b"SRM1" + struct.pack("<I", len(header)) + header + weights


def main():
    checkpoint, output, name = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
    saved = torch.load(checkpoint, map_location="cpu")
    data = sr_bytes(saved["model"], saved["channels"], saved["blocks"], name, saved["iteration"])
    output.write_bytes(data)
    print(f"{output}: {output.stat().st_size} bytes, iteration {saved['iteration']}")


if __name__ == "__main__":
    main()
