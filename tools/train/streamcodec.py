"""Compresses a short run of frames with a real video codec and gives back what a viewer decodes,
standing in for the stream: H.264 (Twitch and most live streams), AV1 and VP9 (YouTube). Unlike
JPEG on each frame, the artifacts depend on the motion: the first frame is coded on its own and
the next ones are predicted from it, so detail smears where things move, blocks follow the motion
and flat areas band, as they do on a stream.

The frames go to ffmpeg as raw RGB at the rate they were captured at (4:2:0 inside the codec, as
streams are) and come back as RGB. One encoder and one decoder process per call; with a few
small frames that costs tens of milliseconds, fine inside the data loader workers.

spec = (codec, quality, preset, b-frames), from random_spec() or written by hand for validation:
  ("h264", crf 18-51, x264 preset, 0-3), ("av1", crf 1-63, SVT-AV1 preset 0-13, unused),
  ("vp9", crf 0-63, cpu-used 0-8, unused).

Usage: python streamcodec.py   (self-test: round trip of random frames with each codec)
"""
import random
import subprocess

import numpy as np
import torch

X264_PRESETS = ("ultrafast", "superfast", "veryfast", "faster", "fast", "medium")


def random_spec(rng=random):
    """Codec settings like the ones streams use, from good to poor. Twitch: x264 or NVENC H.264 at
    about 6 Mbit/s for 1080p60; YouTube: VP9 or AV1. Measured on 128 px game patches (14-nov):
    x264 veryfast crf 20 ~31 dB, crf 30 ~26 dB; SVT-AV1 crf 30 ~33, crf 50 ~30; VP9 crf 30 ~34,
    crf 50 ~30. The ranges go from a good stream to a poor one."""
    r = rng.random()
    if r < 0.6:
        return ("h264", rng.randint(18, 33), rng.choice(X264_PRESETS), rng.choice((0, 0, 2, 3)))
    if r < 0.8:
        return ("av1", rng.randint(25, 52), rng.randint(9, 12), 0)
    return ("vp9", rng.randint(25, 50), rng.randint(5, 8), 0)


def _encoder_args(spec):
    codec, quality, preset, bframes = spec
    if codec == "h264":
        return ["-c:v", "libx264", "-preset", str(preset), "-crf", str(quality), "-bf", str(bframes),
                "-threads", "1", "-x264-params", "log-level=none", "-f", "matroska"]
    if codec == "av1":
        return ["-c:v", "libsvtav1", "-preset", str(preset), "-crf", str(quality),
                "-svtav1-params", "lp=1:tune=0", "-f", "matroska"]
    if codec == "vp9":
        return ["-c:v", "libvpx-vp9", "-deadline", "realtime", "-cpu-used", str(preset), "-crf", str(quality),
                "-b:v", "0", "-threads", "1", "-row-mt", "0", "-f", "matroska"]
    raise ValueError(f"unknown codec {codec}")


def compress(frames, spec, fps=60):
    """frames: [N, 3, H, W] float in 0..1 (H and W even). Returns the decoded frames, same shape."""
    n, _, h, w = frames.shape
    raw = (frames.permute(0, 2, 3, 1).clamp(0, 1).numpy() * 255 + 0.5).astype(np.uint8).tobytes()
    encode = ["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-framerate", str(fps),
              "-i", "-", "-pix_fmt", "yuv420p"] + _encoder_args(spec) + ["-"]
    coded = subprocess.run(encode, input=raw, capture_output=True, check=True).stdout
    decode = ["ffmpeg", "-v", "error", "-i", "-", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    out = subprocess.run(decode, input=coded, capture_output=True, check=True).stdout
    size = w * h * 3
    if len(out) < n * size:
        raise RuntimeError(f"{spec}: decoded {len(out) // size} of {n} frames")
    array = np.frombuffer(out[:n * size], np.uint8).reshape(n, h, w, 3)
    return torch.from_numpy(array.astype(np.float32) / 255).permute(0, 3, 1, 2).contiguous()


if __name__ == "__main__":
    import time
    # a moving pattern, so the predicted frames have something to do
    yy, xx = torch.meshgrid(torch.arange(128.0), torch.arange(128.0), indexing="ij")
    frames = torch.stack([torch.stack([(torch.sin((xx + 3 * k) / 5) + 1) / 2, (torch.cos((yy - 2 * k) / 7) + 1) / 2,
                                       ((xx + yy + 4 * k) % 32) / 32]) for k in range(4)])
    for spec in (("h264", 30, "veryfast", 0), ("h264", 38, "ultrafast", 2), ("av1", 45, 11, 0), ("vp9", 40, 8, 0)):
        start = time.time()
        out = compress(frames, spec, 60)
        mse = ((out - frames) ** 2).mean(dim=(1, 2, 3))
        psnr = [round(float(10 * torch.log10(1 / m)), 2) for m in mse]
        print(spec, tuple(out.shape), "psnr per frame", psnr, f"{(time.time() - start) * 1000:.0f} ms")
    print("random specs:", [random_spec() for _ in range(5)])
