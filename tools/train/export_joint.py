"""Writes the single model file of the smooth video tab (.stmodel, read by
extension/shared/framegen-model.js): "SFM1", the length of a JSON header, the header padded to four
bytes ({"format": 1, "name", "sr": bytes, "fi": bytes}), then a whole .srmodel and a whole .fimodel.

Usage: python export_joint.py <joint.py checkpoint.pt> <output.stmodel> <model name>
       python export_joint.py --files <x.srmodel> <x.fimodel> <output.stmodel> <model name>
"""
import json
import pathlib
import struct
import sys


def combine(sr, fi, name, extra=None):
    header = json.dumps({"format": 1, "name": name, "sr": len(sr), "fi": len(fi), **(extra or {})}).encode("utf-8")
    header += b" " * ((4 - len(header) % 4) % 4)
    return b"SFM1" + struct.pack("<I", len(header)) + header + sr + fi


def main():
    if sys.argv[1] == "--files":
        sr, fi = pathlib.Path(sys.argv[2]).read_bytes(), pathlib.Path(sys.argv[3]).read_bytes()
        output, name = pathlib.Path(sys.argv[4]), sys.argv[5]
        data = combine(sr, fi, name)
    else:
        import torch
        from export import sr_bytes
        from export_fi import fi_bytes
        checkpoint, output, name = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
        saved = torch.load(checkpoint, map_location="cpu")
        state, shape, iteration = saved["model"], saved["shape"], saved["iteration"]
        part = lambda prefix: {k[len(prefix):]: v for k, v in state.items() if k.startswith(prefix)}
        sr = sr_bytes(part("sr."), shape["sr"]["channels"], shape["sr"]["blocks"], name, iteration,
                      shape["sr"].get("aligned", False))
        fi = fi_bytes(part("fi."), shape["fi"], name, iteration)
        data = combine(sr, fi, name, {"iteration": iteration})
    output.write_bytes(data)
    print(f"{output}: {len(data)} bytes")


if __name__ == "__main__":
    main()
