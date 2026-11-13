"""Makes the low-resolution side of the training data: every REDS clip is halved and compressed the
way streaming video is, with a random codec and quality, so the network learns to undo both.

Usage: python prepare.py <data dir>   (expects <data dir>/{train,val}/*_sharp/<clip>/*.png)
"""
import concurrent.futures
import pathlib
import random
import subprocess
import sys
import tempfile

DATA = pathlib.Path(sys.argv[1]).resolve()
CODECS = [("libx264", 24, 38), ("libx265", 26, 40)]
WORKERS = 6


def degrade(clip):
    split = clip.parents[1].name
    out = DATA / "lr" / split / clip.name
    if len(list(out.glob("*.png"))) >= len(list(clip.glob("*.png"))):
        return clip.name
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(f"{split}/{clip.name}")
    codec, low, high = rng.choice(CODECS)
    crf = rng.randint(low, high)
    with tempfile.TemporaryDirectory() as tmp:
        encoded = pathlib.Path(tmp) / "clip.mkv"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-start_number", "0",
                        "-i", str(clip / "%08d.png"), "-vf", "scale=iw/2:ih/2:flags=bicubic",
                        "-c:v", codec, "-crf", str(crf), "-preset", "veryfast", "-pix_fmt", "yuv420p", str(encoded)], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(encoded), "-start_number", "0",
                        str(out / "%08d.png")], check=True)
    return clip.name


def main():
    clips = sorted(path for path in DATA.glob("*/*_sharp/*") if path.is_dir())
    print(len(clips), "clips", flush=True)
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
        for done, _ in enumerate(pool.map(degrade, clips), 1):
            if done % 20 == 0:
                print(done, "/", len(clips), flush=True)
    print("prepared", flush=True)


main()
