"""Tries the built Firefox add-on on a real YouTube video, in a throwaway Zen profile with its sound
scaled to zero, driven through Marionette. It never touches the user's own browser or the mouse.

Usage: python -I -X utf8 youtube.py <work dir> [video url]
Prints one JSON line per measurement.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path(sys.argv[1]).resolve()
URL = sys.argv[2] if len(sys.argv) > 2 else "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
BROWSER = r"C:\Program Files\Zen Browser\zen.exe"
PORT = 2829
MARKER = "st-fg-window-marker"
PREFS = {
    "marionette.port": PORT,
    "browser.shell.checkDefaultBrowser": False,
    "browser.aboutwelcome.enabled": False,
    "zen.welcome-screen.seen": True,
    "datareporting.policy.dataSubmissionEnabled": False,
    "toolkit.telemetry.enabled": False,
    "app.update.auto": False,
    "media.autoplay.default": 0,
    "media.volume_scale": "0.0",
    "widget.windows.window_occlusion_tracking.enabled": False,
}
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # -I leaves the script's folder out
from place_window import place_window  # noqa: E402
from marionette import Marionette  # noqa: E402


def prepare_extension():
    source = ROOT / "dist" / "firefox"
    target = WORK / "ext-bench"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    shutil.copy(ROOT / "tools" / "fg-bench" / "fg-debug.js", target / "fg-debug.js")
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["content_scripts"][0]["js"].append("fg-debug.js")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return target


def report(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def page_summary(m):
    return m.js("return {host: location.host, title: document.title, text: document.body.innerText.slice(0, 200)};")


def dismiss_consent(m):
    if "consent." not in m.js("return location.host;"):
        return
    m.js("""
      const buttons = [...document.querySelectorAll('button')];
      const reject = buttons.find(b => /rechazar|reject/i.test(b.getAttribute('aria-label') || b.textContent));
      (reject || buttons[0]).click();
    """)
    time.sleep(4)


def resume_player(m):
    # Through the site's own player: it pauses again a video started behind its back.
    m.js("""
      const player = window.wrappedJSObject.document.getElementById('movie_player');
      if (player && player.mute) { player.mute(); player.playVideo(); }
    """, sandbox="system")


def wait_for_video(m):
    steady = 0
    deadline = time.time() + 60
    while time.time() < deadline:
        state = m.js("""
          const v = document.querySelector('video');
          const player = document.getElementById('movie_player');
          const skip = document.querySelector('.ytp-skip-ad-button, .ytp-ad-skip-button-modern');
          if (skip) skip.click();
          if (v) v.muted = true;
          return {ad: !!(player && player.classList.contains('ad-showing')),
                  ready: !!v && v.readyState >= 2 && !v.paused && v.videoWidth > 0, t: v ? v.currentTime : -1};
        """)
        if state and state["ready"] and not state["ad"]:
            steady += 1
            if steady >= 3:
                return True
        else:
            steady = 0
            resume_player(m)
        time.sleep(1)
    return False


def set_quality(m):
    m.js("""
      const player = (window.wrappedJSObject || window).document.getElementById('movie_player');
      if (player && player.setPlaybackQualityRange) player.setPlaybackQualityRange('hd1080', 'hd1080');
    """, sandbox="system")


def status(m):
    raw = m.js("return document.documentElement.getAttribute('data-st-fg-status');")
    return json.loads(raw) if raw else None


def command(m, **payload):
    text = json.dumps(payload)
    m.js(f"document.documentElement.setAttribute('data-st-fg-cmd', {json.dumps(text)});")


def video_state(m):
    return m.js("""const v = document.querySelector('video'); const p = document.getElementById('movie_player');
      const reason = document.querySelector('.ytp-error-content-wrap-reason');
      return {paused: v.paused, ended: v.ended, ready: v.readyState, time: Math.round(v.currentTime), size: [v.videoWidth, v.videoHeight],
              src: v.src.slice(0, 24), ad: !!(p && p.classList.contains('ad-showing')),
              frames: v.getVideoPlaybackQuality().totalVideoFrames, playerError: reason ? reason.textContent.slice(0, 120) : null};""")


def measure(m, label, seconds):
    time.sleep(2)  # the target change settles
    first = status(m)
    samples = []
    start = time.time()
    while time.time() - start < seconds:
        time.sleep(1)
        samples.append(status(m)["fps"])
    last = status(m)
    elapsed = time.time() - start
    d = lambda key: last["stats"][key] - first["stats"][key]
    report({
        "video": video_state(m),
        "sourceResets": last.get("sourceResets"),
        "target": label,
        "state": last["state"],
        "error": last.get("error"),
        "sourceHz": last.get("sourceHz"),
        "canvas": last.get("size"),
        "fpsPerSecond": samples,
        "presentsPerS": round(d("presents") / elapsed, 1),
        "capturesPerS": round(d("captures") / elapsed, 1),
        "holdsPerS": round(d("holds") / elapsed, 1),
        "gapsOver20ms": last["gaps20"] - first["gaps20"],
        "gapsOver50ms": last["gaps50"] - first["gaps50"],
        "comparedFrames": last["probe"]["captures"] - first["probe"]["captures"],
        "identicalFrames": last["probe"]["identical"] - first["probe"]["identical"],
        "unreadFrames": last["probe"]["unread"] - first["probe"]["unread"],
    })


def main():
    extension = prepare_extension()
    profile = WORK / "zen-profile-yt"
    profile.mkdir(exist_ok=True)
    (profile / "user.js").write_text("".join(f"user_pref({json.dumps(k)}, {json.dumps(v)});\n" for k, v in PREFS.items()), encoding="utf-8")
    process = subprocess.Popen([BROWSER, "--marionette", "-no-remote", "-profile", str(profile), "about:blank"])
    m = None
    try:
        m = Marionette(PORT)
        m.cmd("WebDriver:NewSession", {"capabilities": {"alwaysMatch": {"timeouts": {"script": 30000, "pageLoad": 60000}}}})
        m.cmd("Addon:Install", {"path": str(extension), "temporary": True})
        m.js(f"document.title = {json.dumps(MARKER)};")
        place_window(MARKER)
        m.cmd("WebDriver:Navigate", {"url": URL})
        dismiss_consent(m)
        if not wait_for_video(m):
            report({"failed": "the video did not start", "page": page_summary(m)})
            return
        set_quality(m)
        time.sleep(5)
        report({"page": page_summary(m)["title"], "video": m.js("const v = document.querySelector('video'); return [v.videoWidth, v.videoHeight];"),
                "dpr": m.js("return devicePixelRatio;")})
        if len(sys.argv) > 3 and sys.argv[3] == "control":  # same page, no frame generation
            for _ in range(14):
                time.sleep(5)
                report({"control": video_state(m)})
            return
        if status(m) is None:
            time.sleep(1)
        command(m, cmd="start", target=144)
        time.sleep(4)  # the frame rate is measured first
        probe = """const v = document.querySelector('video'); const q = v.getVideoPlaybackQuality();
          return {paused: v.paused, seeking: v.seeking, time: v.currentTime, total: q.totalVideoFrames,
                  dropped: q.droppedVideoFrames, ready: v.readyState, videos: document.querySelectorAll('video').length};"""
        before = m.js(probe)
        time.sleep(2)
        after = m.js(probe)
        current = status(m)
        report({"diag": {"before": before, "after": after, "ticks": current.get("ticks"),
                         "sourceResets": current.get("sourceResets"), "state": current["state"]}})
        if current["state"] != "on":
            return
        measure(m, 144, 14)
        for target in (120, 90, 60, 0):
            command(m, cmd="target", target=target)
            measure(m, target, 8)
        command(m, cmd="stop")
        time.sleep(1)
        report({"afterStop": {k: v for k, v in status(m).items() if k in ("running", "state", "error")}})
    finally:
        if m:
            try:
                m.cmd("Marionette:Quit")
            except Exception:
                pass
        for _ in range(20):
            if process.poll() is not None:
                break
            time.sleep(0.25)
        if process.poll() is None:
            process.kill()


main()
