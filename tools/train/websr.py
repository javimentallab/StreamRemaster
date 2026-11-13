"""PyTorch version of the WebSR networks (github.com/sb2702/websr, MIT), the Anime4K CNN x2 S, M and L
shapes with the weights from its weights/anime4k/*.json, so they can be compared with our model on the
same clips. It follows the WGSL layers of WebSR: every weight block is a column-major mat4x4f (output
channel = row, input channel = column), the 3x3 taps go x-major from (-1,-1), the hidden layers see a
CReLU of their inputs, and the result is a 2x2 residual added to a bilinear upscale (S: the same value
on R, G and B; M and L: one per colour).
"""
import json

import torch
import torch.nn.functional as F

TAPS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


def mats(values, count):
    """count 4x4 matrices [out, in] from the column-major floats."""
    return torch.tensor(values, dtype=torch.float32).view(count, 4, 4).transpose(1, 2)


def conv3x3(inputs, layer):
    """inputs: list of 4-channel tensors, already in the order the matrices expect."""
    count = len(inputs)
    m = mats(layer["weights"], 9 * count)
    weight = torch.zeros(4, 4 * count, 3, 3)
    for part in range(count):
        for tap, (dx, dy) in enumerate(TAPS):
            weight[:, part * 4:(part + 1) * 4, dy + 1, dx + 1] = m[part * 9 + tap]
    x = F.pad(torch.cat(inputs, 1), (1, 1, 1, 1), mode="replicate")
    return F.conv2d(x, weight, torch.tensor(layer["bias"], dtype=torch.float32))


def conv1x1(inputs, matrices, bias=None):
    weight = torch.cat(list(matrices), 1)[:, :, None, None]
    return F.conv2d(torch.cat(inputs, 1), weight, bias)


def pos(x):
    return F.relu(x)


def neg(x):
    return F.relu(-x)


class WebSR:
    def __init__(self, path):
        data = json.load(open(path, encoding="utf-8"))
        self.size = data["name"].split("-")[-1]
        self.layers = data["layers"]

    def __call__(self, frames):
        """frames: [N, 3, H, W] in 0..1 -> [N, 3, 2H, 2W]"""
        rgba = torch.cat([frames, torch.ones_like(frames[:, :1])], 1)
        residual = getattr(self, "net_" + self.size)(rgba)
        base = F.interpolate(frames, scale_factor=2, mode="bilinear", align_corners=False)
        return base + residual

    def net_s(self, rgba):
        L = self.layers
        x = conv3x3([rgba], L["conv2d_tf"])
        for name in ("conv2d_1_tf", "conv2d_2_tf", "conv2d_last_tf"):
            x = conv3x3([pos(x), neg(x)], L[name])
        return F.pixel_shuffle(x, 2).repeat(1, 3, 1, 1)

    def net_m(self, rgba):
        L = self.layers
        outs = [conv3x3([rgba], L["conv2d_tf"])]
        for i in range(1, 7):
            outs.append(conv3x3([pos(outs[-1]), neg(outs[-1])], L[f"conv2d_{i}_tf"]))
        colours = []
        for name in ("conv2d_7_tf", "conv2d_7_tf1", "conv2d_7_tf2"):
            m = mats(L[name]["weights"], 14)
            inputs, matrices = [], []
            for i, b in enumerate(outs):
                inputs += [pos(b), neg(b)]
                matrices += [m[2 * i], m[2 * i + 1]]
            colours.append(F.pixel_shuffle(conv1x1(inputs, matrices, torch.tensor(L[name]["bias"], dtype=torch.float32)), 2))
        return torch.cat(colours, 1)

    def net_l(self, rgba):
        L = self.layers
        a, b = conv3x3([rgba], L["conv2d_tf"]), conv3x3([rgba], L["conv2d_tf1"])
        outs = [(a, b)]
        for i in range(1, 7):
            a, b = outs[-1]
            inputs = [pos(a), pos(b), neg(a), neg(b)]
            outs.append((conv3x3(inputs, L[f"conv2d_{i}_tf"]), conv3x3(inputs, L[f"conv2d_{i}_tf1"])))
        colours = []
        for name in ("conv2d_last_tf", "conv2d_last_tf1", "conv2d_last_tf2"):
            m = mats(L[name]["weights"], 28)
            inputs, matrices = [], []
            for i, (a, b) in enumerate(outs):
                inputs += [pos(a), neg(a), pos(b), neg(b)]
                matrices += [m[4 * i], m[4 * i + 2], m[4 * i + 1], m[4 * i + 3]]
            colours.append(F.pixel_shuffle(conv1x1(inputs, matrices, torch.tensor(L[name]["bias"], dtype=torch.float32)), 2))
        return torch.cat(colours, 1)
