"""Checks websr.py against the reference output that WebSR ships with its demo (TensorFlow prediction
of the S network on src/demo/test.png): how far plain bilinear is, how far our version is, and how
well our residual correlates with the reference residual.

Usage: python websr_check.py <dir with demo-test.png, demo-tf-pred.png and the .json weights>
"""
import pathlib
import sys

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from websr import WebSR

d = pathlib.Path(sys.argv[1])
image = Image.open(d / "demo-test.png")
print("test.png mode", image.mode, "size", image.size)
reference = torch.from_numpy(np.asarray(Image.open(d / "demo-tf-pred.png").convert("RGB"), dtype=np.float32) / 255).permute(2, 0, 1)[None]
x = torch.from_numpy(np.asarray(image.convert("RGB"), dtype=np.float32) / 255).permute(2, 0, 1)[None]
base = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)
inner = lambda t: t[:, :, 4:-4, 4:-4]
print(f"bilinear only: mean {inner((base - reference).abs()).mean() * 255:.2f}/255")
ref_res = inner(reference - base).mean(1).flatten()
for name in ["demo-anime4k-cnn-2x-s.json", "cnn-2x-s-an.json", "cnn-2x-s-rl.json"]:
    with torch.no_grad():
        y = WebSR(d / name)(x).clamp(0, 1)
    res = inner(y - base).mean(1).flatten()
    corr = torch.corrcoef(torch.stack([res, ref_res]))[0, 1].item()
    print(f"{name}: mean {inner((y - reference).abs()).mean() * 255:.2f}/255, residual correlation {corr:.3f}, "
          f"residual std ours {res.std() * 255:.2f} reference {ref_res.std() * 255:.2f}")
