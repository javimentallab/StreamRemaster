"""Runs the built Firefox add-on on a local clip with an upscaling model and/or an in-between frames
model, on the machine this script runs on, and reports what the extension itself says. Needs a
display; there is no sound in the clip.

Usage: python3 mint_browser.py <work dir> [--sr model.srmodel] [--fi model.fimodel] [--clip clip60.mp4]
                               [--seconds 8] [--shot shot.png] [output height...]
The work dir holds the clip and ext-firefox (a copy of dist/firefox plus fg-debug.js).
"""
import argparse
import base64
import functools
import http.server
import json
import os
import pathlib
import subprocess
import sys
import threading
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from marionette import Marionette  # noqa: E402

PARSER = argparse.ArgumentParser()
PARSER.add_argument("work")
PARSER.add_argument("heights", nargs="*")
PARSER.add_argument("--sr")
PARSER.add_argument("--fi")
PARSER.add_argument("--clip", default="clip60.mp4")
PARSER.add_argument("--seconds", type=float, default=8)
PARSER.add_argument("--shot")
ARGS = PARSER.parse_args()
WORK = pathlib.Path(ARGS.work).resolve()
encode = lambda path: base64.b64encode(pathlib.Path(path).read_bytes()).decode() if path else None
MODEL = encode(ARGS.sr)
INTERP = encode(ARGS.fi)
HEIGHTS = ARGS.heights or ["original"]
PORT = 2830
HTTP_PORT = 8793
PAGE = ('<!doctype html><title>sr-test</title><body style="margin:0;background:#000"><video src="/' + ARGS.clip
        + '" muted autoplay loop style="width:1280px;height:720px"></video>')
PREFS = {
    "marionette.port": PORT,
    "dom.webgpu.enabled": True,
    "gfx.webgpu.ignore-blocklist": True,
    "dom.webgpu.external-texture.enabled": True,
    "browser.shell.checkDefaultBrowser": False,
    "browser.aboutwelcome.enabled": False,
    "datareporting.policy.dataSubmissionEnabled": False,
    "toolkit.telemetry.enabled": False,
    "app.update.auto": False,
    "media.autoplay.default": 0,
    "media.volume_scale": "0.0",
    "widget.windows.window_occlusion_tracking.enabled": False,
}


def report(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    (WORK / "page.html").write_text(PAGE, encoding="utf-8")
    handler = functools.partial(Quiet, directory=str(WORK))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", HTTP_PORT), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def status(m):
    raw = m.js("return document.documentElement.getAttribute('data-st-fg-status');")
    return json.loads(raw) if raw else None


def command(m, **payload):
    text = json.dumps(payload)
    m.js(f"document.documentElement.setAttribute('data-st-fg-cmd', {json.dumps(text)});")


def measure(m, label, seconds):
    time.sleep(3)
    first = status(m)
    start = time.time()
    time.sleep(seconds / 2)
    if ARGS.shot:
        # The page's own canvas as a PNG, through a 2D copy (a WebGPU canvas has no toDataURL of its own frame).
        data = m.js("const c = document.querySelector('canvas'); const o = document.createElement('canvas');"
                    "o.width = c.width; o.height = c.height; o.getContext('2d').drawImage(c, 0, 0); return o.toDataURL('image/png');")
        pathlib.Path(ARGS.shot).write_bytes(base64.b64decode(data.split(",", 1)[1]))
    time.sleep(seconds / 2)
    last = status(m)
    elapsed = time.time() - start
    if not last.get("running") or not first.get("running"):
        report({"case": label, "not_running": {k: v for k, v in last.items() if k != "probe"}})
        return
    rate = lambda key: round((last["stats"].get(key, 0) - first["stats"].get(key, 0)) / elapsed, 1)
    report({"case": label, "state": last["state"], "error": last.get("error"), "sourceHz": last.get("sourceHz"),
            "input": last.get("input"), "canvas": last.get("size"), "model": last.get("model"), "modelReady": last.get("modelReady"),
            "interpolator": last.get("interpolator"), "interpolatorReady": last.get("interpolatorReady"),
            "presentsPerS": rate("presents"), "capturesPerS": rate("captures"), "upscaledPerS": rate("upscaled"),
            "upscaleSkippedPerS": rate("upscaleSkipped"), "interpolatedPerS": rate("interpolated"),
            "interpolateSkippedPerS": rate("interpolateSkipped"), "synthesizedPerS": rate("synthesized"),
            "gaps20": last["gaps20"] - first["gaps20"], "gaps50": last["gaps50"] - first["gaps50"]})


def main():
    profile = WORK / "firefox-profile"
    profile.mkdir(exist_ok=True)
    (profile / "user.js").write_text("".join(f"user_pref({json.dumps(k)}, {json.dumps(v)});\n" for k, v in PREFS.items()), encoding="utf-8")
    server = serve()
    env = dict(os.environ, DISPLAY=":0", XAUTHORITY=str(pathlib.Path.home() / ".Xauthority"), MOZ_DISABLE_RDD_SANDBOX="1")
    process = subprocess.Popen(["firefox", "--marionette", "--no-remote", "--profile", str(profile), "about:blank"], env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    m = None
    try:
        m = Marionette(PORT)
        report({"browser": m.cmd("WebDriver:NewSession", {"capabilities": {"alwaysMatch": {"timeouts": {"script": 30000, "pageLoad": 60000}}}})["capabilities"]["browserVersion"]})
        m.cmd("Addon:Install", {"path": str(WORK / "ext-firefox"), "temporary": True})
        m.cmd("WebDriver:Navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/page.html"})
        time.sleep(2)
        report({"gpu": m.js("return !!navigator.gpu;"), "playing": m.js("const v = document.querySelector('video'); return [v.paused, v.readyState, v.videoWidth];")})
        for height in HEIGHTS:
            command(m, cmd="setup", model=MODEL, interp=INTERP, resolution=height)
            time.sleep(1)
            command(m, cmd="start", target=0)
            time.sleep(6)
            measure(m, f"{'sr ' if MODEL else ''}{'fi ' if INTERP else ''}a {height}", ARGS.seconds)
            command(m, cmd="stop")
            time.sleep(1)
    finally:
        if m:
            try:
                m.cmd("Marionette:Quit")
            except Exception:
                pass
        server.shutdown()
        for _ in range(20):
            if process.poll() is not None:
                break
            time.sleep(0.25)
        if process.poll() is None:
            process.kill()


main()
