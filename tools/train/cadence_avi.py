"""Frame cadence of a video: the mean change between consecutive frames (grey, 320 x 180), divided
by its local mean (9 frames) so that only the step-to-step unevenness is left. An even cadence
gives a flat autocorrelation of that ratio; a capture that adds or drops game time every N frames
gives a peak at lag N.

Usage: python cadence_avi.py <video> [label]
"""
import subprocess
import sys

import numpy as np

W, H = 320, 180


def autocorr(x, lag):
    a, b = x[:-lag], x[lag:]
    keep = ~(np.isnan(a) | np.isnan(b))
    a, b = a[keep], b[keep]
    return float(np.mean((a - a.mean()) * (b - b.mean())) / (a.std() * b.std() + 1e-9))


def main():
    path = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else path
    if path.endswith(".npy"):
        # a packed clip [N, H, W, 3]: grey by luma, then about 320 wide by striding
        clip = np.load(path, mmap_mode="r")
        step = max(1, clip.shape[2] // W)
        frames = np.stack([np.asarray(f[::step, ::step], np.float32) @ np.float32([0.299, 0.587, 0.114])
                           for f in clip]).astype(np.int16)
    else:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}:flags=area", "-f", "rawvideo",
                              "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
        frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    c = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    local = np.convolve(c, np.ones(9) / 9, "same")
    # the linear range of the measure: some motion, not so much that the difference saturates
    ok = (local > 1.5) & (local < 12)
    r = np.where(ok, c / np.maximum(local, 1e-3), np.nan)
    lags = {lag: autocorr(r, lag) for lag in range(1, 9)}
    spread = np.nanstd(r)
    typical = np.nanmedian(np.abs(r - 1))
    print(f"{label:24s} usable {ok.mean() * 100:4.1f}%  spread {spread:.3f}  median |r-1| {typical:.3f}  autocorr " +
          " ".join(f"{lag}:{v:+.2f}" for lag, v in lags.items()))
    run = np.flatnonzero(np.convolve(ok, np.ones(32), "valid") == 32)
    if len(run):
        k = run[len(run) // 2]
        print("   sample:", " ".join(f"{v:.1f}" for v in c[k:k + 32]))


if __name__ == "__main__":
    main()
