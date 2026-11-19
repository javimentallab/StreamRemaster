"""Runs the built Firefox add-on with Whisper on this computer, the way a user would: downloads a
model in Settings → Models on this computer, plays a clip in a page, starts the subtitles and
prints what the overlay shows. Meant for the Mint's 2060; no sound comes out (volume scale 0).

Usage: python3 mint_firefox.py <work dir> <clip.wav> [--model tiny] [--seconds 30] [--lang auto]
The work dir holds ext-firefox (a copy of dist/firefox); the clip is copied next to it.
"""
import argparse
import functools
import http.server
import json
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from marionette import Marionette  # noqa: E402


def js(m, script):
    """Runs in the page's own scope (the extension page's ST and ext included)."""
    return m.cmd("WebDriver:ExecuteScript", {"script": script, "args": [], "sandbox": None}).get("value")

PARSER = argparse.ArgumentParser()
PARSER.add_argument("work")
PARSER.add_argument("clip")
PARSER.add_argument("--model", default="tiny")
PARSER.add_argument("--seconds", type=float, default=30)
PARSER.add_argument("--lang", default="")
ARGS = PARSER.parse_args()
WORK = pathlib.Path(ARGS.work).resolve()
PORT = 2831
HTTP_PORT = 8794
PREFS = {
    "marionette.port": PORT,
    "dom.webgpu.enabled": True,
    "gfx.webgpu.ignore-blocklist": True,
    "browser.shell.checkDefaultBrowser": False,
    "browser.aboutwelcome.enabled": False,
    "datareporting.policy.dataSubmissionEnabled": False,
    "toolkit.telemetry.enabled": False,
    "app.update.auto": False,
    "media.autoplay.default": 0,
    "media.volume_scale": "0.0",
    "devtools.console.stdout.content": True,
    "devtools.console.stdout.chrome": True,
}
# a fixed internal address for the add-on, so its pages can be opened directly
UUID = "5b1a6c1e-2f43-4d0c-9a51-0c0ffee0c0de"
PREFS["extensions.webextensions.uuids"] = json.dumps({"stream-transcription@javimentallab": UUID})


def report(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    shutil.copy(ARGS.clip, WORK / "clip.wav")
    (WORK / "page.html").write_text('<!doctype html><title>subs-test</title><body style="background:#222;height:600px">'
                                    '<audio src="/clip.wav" controls></audio>', encoding="utf-8")
    handler = functools.partial(Quiet, directory=str(WORK))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", HTTP_PORT), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main():
    profile = WORK / "firefox-profile-subs"
    profile.mkdir(exist_ok=True)
    (profile / "user.js").write_text("".join(f"user_pref({json.dumps(k)}, {json.dumps(v)});\n" for k, v in PREFS.items()),
                                     encoding="utf-8")
    server = serve()
    env = dict(os.environ, DISPLAY=":0", XAUTHORITY=str(pathlib.Path.home() / ".Xauthority"), MOZ_REMOTE_ALLOW_SYSTEM_ACCESS="1")
    log = open(WORK / "firefox.log", "w")
    process = subprocess.Popen(["firefox", "--marionette", "--no-remote", "--profile", str(profile), "about:blank"], env=env,
                               stdout=log, stderr=subprocess.STDOUT)
    m = None
    try:
        m = Marionette(PORT)
        caps = m.cmd("WebDriver:NewSession", {"capabilities": {"alwaysMatch": {"timeouts": {"script": 120000, "pageLoad": 60000}}}})
        report({"browser": caps["capabilities"]["browserVersion"]})
        addon = m.cmd("Addon:Install", {"path": str(WORK / "ext-firefox"), "temporary": True})["value"]
        base = f"moz-extension://{UUID}/"
        report({"addon": addon})

        # Settings → Models on this computer: download the model with its own button
        # Marionette won't navigate to an add-on page: open it from the browser window instead
        before = set(m.cmd("WebDriver:GetWindowHandles"))
        m.cmd("Marionette:SetContext", {"value": "chrome"})
        js(m, "const w = Services.wm.getMostRecentWindow('navigator:browser');"
              f"w.gBrowser.selectedTab = w.gBrowser.addTab({json.dumps(base + 'settings.html#local')},"
              " { triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal() }); return true;")
        m.cmd("Marionette:SetContext", {"value": "content"})
        time.sleep(2)
        new = [h for h in m.cmd("WebDriver:GetWindowHandles") if h not in before]
        m.cmd("WebDriver:SwitchToWindow", {"handle": new[0]})
        time.sleep(2)
        report({"gpu": js(m, "return document.getElementById('localGpu').textContent;")})
        if os.environ.get("BUFTEST"):
            report({"buffers": js(m, """return (async () => {
              const a = await navigator.gpu.requestAdapter(); const d = await a.requestDevice({ requiredLimits: {
                maxStorageBufferBindingSize: a.limits.maxStorageBufferBindingSize, maxBufferSize: a.limits.maxBufferSize } });
              const out = [a.limits.maxBufferSize, a.limits.maxStorageBufferBindingSize];
              const keep = [];
              for (const mb of [16, 32, 64, 80, 128, 256, 256, 256, 256]) {
                d.pushErrorScope('out-of-memory');
                keep.push(d.createBuffer({ size: mb * 1048576, usage: 0x80 | 0x08 }));
                const e = await d.popErrorScope();
                out.push(mb + (e ? ' OOM' : ' ok'));
              }
              return out; })();""")})
        if os.environ.get("SHOTS2"):
            # smooth video models on the server (mock_server.py on port 9197, its folder holds "Otro modelo")
            shot = lambda name: (WORK / name).write_bytes(__import__("base64").b64decode(m.cmd("WebDriver:TakeScreenshot", {"full": True})["value"]))
            raw = (WORK / "ext-firefox" / "models" / "streamremaster.stmodel").read_bytes()
            size = int.from_bytes(raw[4:8], "little")
            header = json.loads(raw[8:8 + size])
            header["name"] = "Subido al servidor"
            text = json.dumps(header).encode()
            text += b" " * ((4 - len(text) % 4) % 4)
            (WORK / "subido.stmodel").write_bytes(raw[:4] + len(text).to_bytes(4, "little") + text + raw[8 + size + (4 - size % 4) % 4:])
            m.cmd("WebDriver:SetWindowRect", {"width": 1100, "height": 1000})
            js(m, "return ST.setSettings({ serverUrl: 'ws://127.0.0.1:9197', fgSource: 'local', fgModel: 'builtin-st' }).then(() => true);")
            js(m, "location.reload(); return true;")
            time.sleep(3)
            report({"serverList": js(m, "return { names: [...document.querySelectorAll('#fgServerList .name')].map((n) => n.textContent),"
                                        " msg: document.getElementById('fgServerMsg').textContent, add: !document.getElementById('fgServerAdd').hidden };")})
            js(m, f"document.getElementById('fgServerSource').value = 'http://127.0.0.1:{HTTP_PORT}/subido.stmodel';"
                  "document.getElementById('fgServerDownload').click(); return true;")
            time.sleep(3)
            report({"afterUpload": js(m, "return { names: [...document.querySelectorAll('#fgServerList .name')].map((n) => n.textContent),"
                                         " msg: document.getElementById('fgServerAddMsg').textContent };")})
            js(m, "[...document.querySelectorAll('#fgServerList li')].find((l) => l.querySelector('.name').textContent === 'Otro modelo')"
                  ".querySelector('.actions .btn').click(); return true;")
            time.sleep(3)
            report({"chosen": js(m, "return ST.getSettings().then((s) => ({ source: s.fgSource, model: s.fgModel,"
                                    " seg: [...document.querySelectorAll('#fgSourceSeg button')].map((b) => b.textContent + (b.classList.contains('on') ? ' *' : '')),"
                                    " serverInUse: !document.getElementById('fgServerInUse').hidden,"
                                    " stored: null }));")})
            js(m, "document.getElementById('fgmodels').scrollIntoView(); return true;")
            shot("settings-fg-server.png")
            m.cmd("Marionette:SetContext", {"value": "chrome"})
            js(m, "const w = Services.wm.getMostRecentWindow('navigator:browser');"
                  f"w.gBrowser.selectedTab = w.gBrowser.addTab({json.dumps(base + 'popup.html')},"
                  " { triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal() }); return true;")
            m.cmd("Marionette:SetContext", {"value": "content"})
            time.sleep(2)
            m.cmd("WebDriver:SwitchToWindow", {"handle": m.cmd("WebDriver:GetWindowHandles")[-1]})
            m.cmd("WebDriver:SetWindowRect", {"width": 420, "height": 900})
            js(m, "document.getElementById('tabFg').click(); return true;")
            time.sleep(2)
            shot("popup-fg-server.png")
            report({"popupServer": js(m, "const s = document.getElementById('fgModel'); return { groups: [...s.children].map((c) => c.tagName === 'OPTGROUP'"
                                         " ? c.label + ': ' + [...c.children].map((o) => o.text).join(', ') : c.text), value: s.value,"
                                         " hint: document.getElementById('fgServerHint').textContent, memory: document.getElementById('fgMemory').textContent };")})
            # back to this computer: the built-in model again
            js(m, "document.querySelector('#fgSourceSeg button[data-v=\"local\"]').click(); return true;")
            time.sleep(2)
            report({"popupLocal": js(m, "const s = document.getElementById('fgModel'); return ST.getSettings().then((st) => ({ value: s.value, source: st.fgSource,"
                                        " groups: [...s.children].map((c) => c.tagName === 'OPTGROUP' ? c.label + ': ' + [...c.children].map((o) => o.text).join(', ') : c.text) }));")})
            # a server that is not there
            js(m, "return ST.setSettings({ serverUrl: 'ws://127.0.0.1:9199', fgSource: 'server' }).then(() => true);")
            js(m, "location.reload(); return true;")
            time.sleep(3)
            js(m, "document.getElementById('tabFg').click(); return true;")
            time.sleep(2)
            report({"noServer": js(m, "return document.getElementById('fgServerHint').textContent;")})
            return
        if os.environ.get("SHOTS"):
            # the model options: Settings with a smooth video model downloaded from an address, then
            # both popup tabs. The model is served by the test's own web server.
            raw = (WORK / "ext-firefox" / "models" / "streamremaster.stmodel").read_bytes()
            size = int.from_bytes(raw[4:8], "little")
            header = json.loads(raw[8:8 + size])
            header["name"] = "Otro modelo"
            text = json.dumps(header).encode()
            text += b" " * ((4 - len(text) % 4) % 4)
            (WORK / "otro.stmodel").write_bytes(raw[:4] + len(text).to_bytes(4, "little") + text + raw[8 + size + (4 - size % 4) % 4:])
            shot = lambda name: (WORK / name).write_bytes(__import__("base64").b64decode(m.cmd("WebDriver:TakeScreenshot", {"full": True})["value"]))
            m.cmd("WebDriver:SetWindowRect", {"width": 1100, "height": 1000})
            js(m, "return ST.setSettings({ engine: 'local', fgModel: 'builtin-st' }).then(() => true);")
            js(m, f"document.getElementById('fgModelUrl').value = 'http://127.0.0.1:{HTTP_PORT}/otro.stmodel';"
                  "document.getElementById('fgModelDownload').click(); return true;")
            time.sleep(3)
            report({"fgDownload": js(m, "return { msg: document.getElementById('fgModelMsg').textContent,"
                                        " own: [...document.querySelectorAll('#fgModelList .name')].map((n) => n.textContent),"
                                        " builtin: [...document.querySelectorAll('#fgBuiltinList li')].map((l) => l.innerText) };")})
            js(m, "location.reload(); return true;")
            time.sleep(3)
            shot("settings-full.png")
            report({"settingsTop": js(m, "return { seg: [...document.querySelectorAll('#engineSeg button')].map((b) => b.textContent + (b.classList.contains('on') ? ' *' : '')),"
                                         " toc: [...document.querySelectorAll('.toc a')].map((a) => a.textContent),"
                                         " localInUse: !document.getElementById('localInUse').hidden, fgGpu: document.getElementById('fgGpu').textContent };")})
            m.cmd("Marionette:SetContext", {"value": "chrome"})
            js(m, "const w = Services.wm.getMostRecentWindow('navigator:browser');"
                  f"w.gBrowser.selectedTab = w.gBrowser.addTab({json.dumps(base + 'popup.html')},"
                  " { triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal() }); return true;")
            m.cmd("Marionette:SetContext", {"value": "content"})
            time.sleep(2)
            m.cmd("WebDriver:SwitchToWindow", {"handle": m.cmd("WebDriver:GetWindowHandles")[-1]})
            m.cmd("WebDriver:SetWindowRect", {"width": 420, "height": 900})
            js(m, "document.getElementById('tabSubs').click(); return true;")
            time.sleep(1)
            shot("popup-subs.png")
            js(m, "document.getElementById('tabFg').click(); return true;")
            time.sleep(1)
            shot("popup-fg.png")
            report({"popupFg": js(m, "const s = document.getElementById('fgModel'); return { groups: [...s.children].map((c) => c.tagName === 'OPTGROUP'"
                                     " ? c.label + ': ' + [...c.children].map((o) => o.text).join(', ') : c.text), memory: document.getElementById('fgMemory').textContent };")})
            js(m, "const r = document.getElementById('fgResolution'); r.value = '2160'; r.dispatchEvent(new Event('change')); return true;")
            time.sleep(1)
            report({"memory4k": js(m, "return document.getElementById('fgMemory').textContent;")})
            return
        row = f"[...document.querySelectorAll('#localList li')].find((l) => l.querySelector('.name').textContent === {json.dumps(ARGS.model)})"
        if not js(m, f"return !!{row}.querySelector('.badge.ok');"):
            js(m, f"{row}.querySelector('.actions .btn').click();")
            start = time.time()
            last = ""
            while True:
                time.sleep(2)
                done = js(m, f"return !!{row}.querySelector('.badge.ok');")
                hint = js(m, f"const h = {row}.querySelector('.hint'); return h ? h.textContent : '';")
                msg = js(m, "return document.getElementById('localMsg').textContent;")
                if hint != last:
                    print("  ", hint, flush=True)
                    last = hint
                if done or msg:
                    report({"downloaded": done, "seconds": round(time.time() - start), "message": msg})
                    break
        if os.environ.get("POPUP"):
            # the popup as a page: back to "no server", then "Use this computer"
            js(m, "return ST.setSettings({ engine: 'server', serverUrl: '', targetLang: 'fr' }).then(() => true);")
            m.cmd("Marionette:SetContext", {"value": "chrome"})
            js(m, "const w = Services.wm.getMostRecentWindow('navigator:browser');"
                  f"w.gBrowser.selectedTab = w.gBrowser.addTab({json.dumps(base + 'popup.html')},"
                  " { triggeringPrincipal: Services.scriptSecurityManager.getSystemPrincipal() }); return true;")
            m.cmd("Marionette:SetContext", {"value": "content"})
            time.sleep(2)
            handles = m.cmd("WebDriver:GetWindowHandles")
            m.cmd("WebDriver:SwitchToWindow", {"handle": handles[-1]})
            time.sleep(1)
            m.cmd("WebDriver:SetWindowRect", {"width": 420, "height": 900})
            shot = lambda name: (WORK / name).write_bytes(__import__("base64").b64decode(m.cmd("WebDriver:TakeScreenshot", {"full": True})["value"]))
            shot("popup-setup.png")
            report({"setupVisible": js(m, "return !document.getElementById('setupCard').hidden;")})
            js(m, "document.getElementById('setupLocal').click(); return true;")
            time.sleep(2)
            shot("popup-local.png")
            report({"popup": js(m, "return { models: [...document.getElementById('model').options].map((o) => o.text),"
                                   " picked: document.getElementById('model').value, foot: document.getElementById('srvText').textContent,"
                                   " target: document.getElementById('targetLang').value,"
                                   " frenchDisabled: [...document.getElementById('targetLang').options].find((o) => o.value === 'fr').disabled,"
                                   " englishDisabled: [...document.getElementById('targetLang').options].find((o) => o.value === 'en').disabled,"
                                   " hint: !document.getElementById('localTargetHint').hidden, button: !document.getElementById('toggleBtn').disabled };")})
            return
        if os.environ.get("BENCH"):
            # the engine's own pieces, loaded into the settings page, timed one by one
            js(m, "for (const f of ['whisper-gpu.js', 'whisper-local.js']) { const e = document.createElement('script'); e.src = f; "
                  "document.head.append(e); } return true;")
            time.sleep(2)
            report({"bench": js(m, """return (async () => {
              const m = await Whisper.load(%s); const g = m.gpu; const r = {}; let t;
              const ms = () => Math.round(performance.now() - t);
              t = performance.now(); for (let i = 0; i < 10; i++) await g.fence(); r.fence_x10 = ms();
              const mel = new Float32Array(3000 * g.nMels).fill(-0.5);
              t = performance.now(); await g.encode(mel); r.encode_first = ms();
              t = performance.now(); await g.encode(mel); r.encode = ms();
              t = performance.now(); for (let i = 0; i < 10; i++) await g.step(220, i); r.step_x10 = ms();
              t = performance.now();
              for (let i = 0; i < 10; i++) {
                g.device.queue.writeBuffer(g.stepBuf, 0, new Uint32Array([220, i, 0, 0]));
                const enc = g.device.createCommandEncoder(); g.run(g.decOps, enc); g.device.queue.submit([enc.finish()]);
              }
              await g.fence(); r.steps_no_readback_x10 = ms();
              t = performance.now();
              const enc = g.device.createCommandEncoder(); for (let i = 0; i < 10; i++) g.run(g.decOps, enc);
              g.device.queue.submit([enc.finish()]); await g.fence(); r.steps_one_submit_x10 = ms();
              r.dispatches_per_step = g.decOps.length;
              return r; })();""" % json.dumps(ARGS.model))})
            return
        settings_tab = m.cmd("WebDriver:GetWindowHandle")["value"]
        js(m, "return ext.storage.local.set({ debugLocal: true }).then(() => true);")
        js(m, f"return ST.setSettings({{ engine: 'local', localModel: {json.dumps(ARGS.model)}, sourceLang: {json.dumps(ARGS.lang)}, targetLang: '' }});")

        # the page with the clip, in a second tab
        page_tab = m.cmd("WebDriver:NewWindow", {"type": "tab"})["handle"]
        m.cmd("WebDriver:SwitchToWindow", {"handle": page_tab})
        m.cmd("WebDriver:Navigate", {"url": f"http://127.0.0.1:{HTTP_PORT}/page.html"})
        time.sleep(2)
        m.cmd("WebDriver:SwitchToWindow", {"handle": settings_tab})
        tab_id = js(m, "return ext.tabs.query({ url: 'http://127.0.0.1/*' }).then((t) => t[0] && t[0].id);")
        js(m, f"ext.runtime.sendMessage({{ cmd: 'start', tabId: {tab_id} }}); return true;")
        m.cmd("WebDriver:SwitchToWindow", {"handle": page_tab})
        time.sleep(1)
        js(m, "document.querySelector('audio').play(); return true;")
        start = time.time()
        shown = ""
        status = ""
        while time.time() - start < ARGS.seconds:
            time.sleep(0.5)
            got = js(m, "const h = document.querySelector('streamremaster-overlay'); if (!h) return ['', ''];"
                       "const r = h.shadowRoot; return [r.querySelector('.line').textContent, r.querySelector('.status').hidden ? '' : r.querySelector('.status').textContent];")
            if got[1] != status:
                status = got[1]
                print(f"  {time.time() - start:5.1f} s  [status] {status}", flush=True)
            if got[0] != shown:
                shown = got[0]
                print(f"  {time.time() - start:5.1f} s  {shown}", flush=True)
        m.cmd("WebDriver:SwitchToWindow", {"handle": settings_tab})
        report({"runState": js(m, "return ext.storage.local.get('runState').then((r) => r.runState);")})
        js(m, "ext.runtime.sendMessage({ cmd: 'stop' }); return true;")
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
        log.close()
        lines = [ln for ln in open(WORK / "firefox.log", errors="replace") if "stream-transcription" in ln or "WebGPU" in ln]
        print("".join(lines[-60:]), end="")


main()
