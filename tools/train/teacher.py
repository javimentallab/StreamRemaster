"""RIFE as a teacher for the motion network (--teacher in joint.py).

RIFE (github.com/hzwer/Practical-RIFE, MIT; the network files and weights as packaged by
github.com/HolyWu/vs-rife, MIT) is far too slow for the extension (about 100 ms per in-between frame
at 1080p in WebGPU on an RTX 4070, against a budget of about 12 ms), but it measures motion much
better than our small network. Here it only looks at the clean full-resolution pair and gives, for
each instant t, the two warp fields and the in-between frame it would show; joint.py pulls our own
warp fields and frames towards them. Nothing of RIFE ships in the extension: the trained network is
still ours, it has learned from RIFE's answers.

The RIFE files are not in this repository: --teacher points at a folder with the package
rifemods/ (IFNet_HDv3_v4_25.py and warplayer.py from vs-rife, with an empty __init__.py) and
flownet_v4.25.pkl.
"""
import importlib
import pathlib
import sys

import torch
import torch.nn.functional as F


class Teacher:
    MODULO = 64

    def __init__(self, folder, device, version="4.25"):
        folder = pathlib.Path(folder)
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))
        mod = importlib.import_module("rifemods.IFNet_HDv3_v4_" + version.replace(".", "_")[2:])
        state = torch.load(folder / f"flownet_v{version}.pkl", map_location="cpu", weights_only=True)
        state = {k.replace("module.", ""): v for k, v in state.items() if "module." in k}
        self.net = mod.IFNet(1.0, False)
        self.net.load_state_dict(state, strict=False)
        self.net.eval().to(device, torch.half).requires_grad_(False)
        self.encode = mod.Head()
        self.encode.load_state_dict({k.replace("encode.", ""): v for k, v in state.items() if "encode." in k})
        self.encode.eval().to(device, torch.half).requires_grad_(False)
        self.warp = mod.warp
        self.device = device
        self.grids = {}

    def grid(self, h, w):
        if (h, w) not in self.grids:
            div = torch.tensor([(w - 1.0) / 2.0, (h - 1.0) / 2.0], dtype=torch.float, device=self.device)
            hor = torch.linspace(-1.0, 1.0, w, device=self.device).view(1, 1, 1, w).expand(-1, -1, h, -1)
            ver = torch.linspace(-1.0, 1.0, h, device=self.device).view(1, 1, h, 1).expand(-1, -1, -1, w)
            self.grids[(h, w)] = (div, torch.cat([hor, ver], 1))
        return self.grids[(h, w)]

    @torch.no_grad()
    def __call__(self, a, b, times):
        """a, b: [N, 3, H, W] in 0..1; times: [N, T]. Returns the in-between frames [N, T, 3, H, W] and
        the warp fields [N, T, 4, H, W] in uv units (fraction of the width and height): channels 0-1
        move a to instant t, 2-3 move b to it, the same meaning as ft0 and ft1 in joint.py."""
        n, _, h, w = a.shape
        t_count = times.shape[1]
        ph, pw = -(-h // self.MODULO) * self.MODULO, -(-w // self.MODULO) * self.MODULO
        pad = (0, pw - w, 0, ph - h)
        a16 = F.pad(a, pad, mode="replicate").half()
        b16 = F.pad(b, pad, mode="replicate").half()
        fa, fb = self.encode(a16), self.encode(b16)
        rep = lambda x: x.repeat_interleave(t_count, 0)
        tt = times.reshape(-1, 1, 1, 1).to(torch.half).expand(-1, 1, ph, pw)
        div, grid = self.grid(ph, pw)
        frame, flow = self.forward_with_flow(rep(a16), rep(b16), tt, div, grid, rep(fa), rep(fb))
        frame = frame[:, :, :h, :w].float().view(n, t_count, 3, h, w)
        flow = flow[:, :, :h, :w].float()
        # RIFE's flow is in pixels of the padded frame; grid_sample normalises it by (size - 1) / 2,
        # so in uv units (0..1 across the picture) it is pixels / (size - 1)
        scale = torch.tensor([pw - 1.0, ph - 1.0] * 2, device=flow.device).view(1, 4, 1, 1)
        return frame, (flow / scale).view(n, t_count, 4, h, w)

    def forward_with_flow(self, img0, img1, timestep, div, grid, f0, f1):
        """IFNet.forward of v4.25, step by step, also returning the final flow (IFNet itself only
        returns the frame)."""
        net, warp = self.net, self.warp
        img0, img1 = img0.clamp(0.0, 1.0), img1.clamp(0.0, 1.0)
        warped0, warped1 = img0, img1
        flow = mask = feat = None
        for i, block in enumerate([net.block0, net.block1, net.block2, net.block3, net.block4]):
            if flow is None:
                flow, mask, feat = block(torch.cat((img0, img1, f0, f1, timestep), 1), None, scale=net.scale_list[i])
            else:
                wf0 = warp(f0, flow[:, :2], div, grid)
                wf1 = warp(f1, flow[:, 2:4], div, grid)
                fd, mask, feat = block(torch.cat((warped0, warped1, wf0, wf1, timestep, mask, feat), 1), flow,
                                       scale=net.scale_list[i])
                flow = flow + fd
            warped0 = warp(img0, flow[:, :2], div, grid)
            warped1 = warp(img1, flow[:, 2:4], div, grid)
        m = torch.sigmoid(mask)
        return warped0 * m + warped1 * (1 - m), flow
