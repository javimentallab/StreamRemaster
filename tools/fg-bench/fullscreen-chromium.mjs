// Checks that the page's own fullscreen still works with smooth video on: opens a video in a
// throwaway profile with the sound off, presses the player's fullscreen button with smooth video
// off and then on, and reports what went fullscreen. Never touches the user's own browser.
//
// Usage: node fullscreen-chromium.mjs <work dir> <browser.exe> [video url] [display]
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..', '..');
const WORK = resolve(process.argv[2]);
const BROWSER = process.argv[3];
const URL_TO_TEST = process.argv[4] || 'https://www.twitch.tv/videos/2924071148';
const DISPLAY = process.argv[5] || '\\\\.\\DISPLAY2';
const PORT = 9334;
const MARKER = 'st-fg-fullscreen-marker';

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const report = (data) => console.log(JSON.stringify(data));

function prepareExtension() {
  const target = join(WORK, 'ext-fullscreen-chromium');
  rmSync(target, { recursive: true, force: true });
  cpSync(join(ROOT, 'dist', 'chromium'), target, { recursive: true });
  cpSync(join(HERE, 'fg-debug.js'), join(target, 'fg-debug.js'));
  const path = join(target, 'manifest.json');
  const manifest = JSON.parse(readFileSync(path, 'utf8'));
  manifest.host_permissions = ['<all_urls>'];
  manifest.content_scripts = [{
    matches: ['<all_urls>'], run_at: 'document_idle',
    js: ['common.js', 'framegen.js', 'framegen-sr.js', 'framegen-fi.js', 'framegen-model.js', 'framegen-page.js', 'fg-debug.js'],
  }];
  writeFileSync(path, JSON.stringify(manifest, null, 2));
  return target;
}

class Cdp {
  constructor(socket) {
    this.socket = socket;
    this.id = 0;
    this.waiting = new Map();
    socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data);
      const entry = this.waiting.get(message.id);
      if (!entry) return;
      this.waiting.delete(message.id);
      if (message.error) entry.reject(new Error(JSON.stringify(message.error)));
      else entry.resolve(message.result);
    });
  }

  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.waiting.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async js(expression, userGesture = false) {
    const result = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true, userGesture });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
    return result.result.value;
  }
}

async function connect() {
  for (let i = 0; i < 80; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find((t) => t.type === 'page' && t.url.startsWith('data:'));
      if (page) {
        const socket = new WebSocket(page.webSocketDebuggerUrl);
        await new Promise((resolve, reject) => {
          socket.addEventListener('open', resolve, { once: true });
          socket.addEventListener('error', reject, { once: true });
        });
        return new Cdp(socket);
      }
    } catch { /* not up yet */ }
    await sleep(250);
  }
  throw new Error('the browser did not expose its debugging port');
}

const status = async (cdp) => {
  const raw = await cdp.js("document.documentElement.getAttribute('data-st-fg-status')");
  return raw ? JSON.parse(raw) : null;
};
const command = (cdp, payload) => cdp.js(`document.documentElement.setAttribute('data-st-fg-cmd', ${JSON.stringify(JSON.stringify(payload))})`);

async function waitForVideo(cdp) {
  let steady = 0;
  const deadline = Date.now() + 90000;
  while (Date.now() < deadline) {
    const state = await cdp.js(`(() => {
      for (const sel of ['[data-a-target="player-overlay-mature-accept"]',
                         '[data-a-target="content-classification-gate-overlay-start-watching-button"]',
                         'button[data-a-target="consent-banner-accept"]']) {
        const b = document.querySelector(sel); if (b) b.click();
      }
      const v = [...document.querySelectorAll('video')].sort((a, b) => b.clientWidth - a.clientWidth)[0];
      if (v) { v.muted = true; if (v.paused) v.play().catch(() => {}); }
      return { ready: !!v && v.readyState >= 2 && !v.paused && v.videoWidth > 0 };
    })()`);
    steady = state.ready ? steady + 1 : 0;
    if (steady >= 4) return true;
    await sleep(1000);
  }
  return false;
}

// Presses the page's own fullscreen button, as a click with a user gesture, and reports.
async function tryFullscreen(cdp, label) {
  const before = await cdp.js(`(() => {
    const b = document.querySelector('[data-a-target="player-fullscreen-button"], .ytp-fullscreen-button');
    if (!b) return 'no button';
    const r = b.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  })()`);
  if (typeof before === 'string') { report({ label, failed: before }); return; }
  await cdp.js(`window.__fsErrors = []; document.addEventListener('fullscreenerror', (e) => window.__fsErrors.push(String(e.target && e.target.className)), { once: true }); true`);
  // A real mouse click on the button: the player's own handler runs with a real user gesture.
  await cdp.js(`(() => { const v = document.querySelector('video'); v && v.dispatchEvent(new MouseEvent('mousemove', { bubbles: true })); })()`);
  await sleep(300);
  if (label.endsWith('dblclick')) {
    const v = await cdp.js(`(() => { const r = [...document.querySelectorAll('video')].sort((a, b) => b.clientWidth - a.clientWidth)[0].getBoundingClientRect();
      return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    for (const clickCount of [1, 2]) {
      for (const type of ['mousePressed', 'mouseReleased']) {
        await cdp.send('Input.dispatchMouseEvent', { type, x: v.x, y: v.y, button: 'left', clickCount });
      }
    }
  } else if (label.endsWith('key f')) {
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'f', code: 'KeyF', text: 'f', windowsVirtualKeyCode: 70 });
    await cdp.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'f', code: 'KeyF', windowsVirtualKeyCode: 70 });
  } else {
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cdp.send('Input.dispatchMouseEvent', { type, x: before.x, y: before.y, button: 'left', clickCount: 1 });
    }
  }
  await sleep(2000);
  const after = await cdp.js(`(() => {
    const f = document.fullscreenElement;
    const v = [...document.querySelectorAll('video')].sort((a, b) => b.clientWidth - a.clientWidth)[0];
    const c = v && v.nextElementSibling && v.nextElementSibling.tagName === 'CANVAS' ? v.nextElementSibling : null;
    return {
      fullscreen: f ? (f.tagName + '.' + String(f.className).slice(0, 60)) : null,
      errors: window.__fsErrors,
      video: v ? [v.clientWidth, v.clientHeight] : null,
      canvas: c ? [c.clientWidth, c.clientHeight, c.style.visibility] : null,
      inner: [innerWidth, innerHeight],
    };
  })()`);
  report({ label, ...after });
  if (after.fullscreen) {
    await cdp.js('document.exitFullscreen().then(() => true, () => false)', true);
    await sleep(1500);
  }
}

async function main() {
  const extension = prepareExtension();
  const profile = join(WORK, 'chromium-profile-fs');
  mkdirSync(profile, { recursive: true });
  const child = spawn(BROWSER, [
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
    `--load-extension=${extension}`, `--disable-extensions-except=${extension}`,
    '--disable-features=DisableLoadExtensionCommandLineSwitch',
    '--mute-audio', '--autoplay-policy=no-user-gesture-required', '--no-first-run', '--no-default-browser-check',
    '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
    `data:text/html,<title>${MARKER}</title>`,
  ], { stdio: 'ignore' });
  let cdp = null;
  try {
    cdp = await connect();
    spawnSync('python', ['-I', '-X', 'utf8', join(HERE, 'place_window.py'), MARKER, DISPLAY], { stdio: 'inherit' });
    await cdp.send('Page.enable');
    await cdp.send('Page.navigate', { url: URL_TO_TEST });
    await sleep(8000);
    if (!(await waitForVideo(cdp))) { report({ failed: 'the video did not start' }); return; }
    await sleep(3000);
    await tryFullscreen(cdp, 'smooth video off, button');
    await tryFullscreen(cdp, 'smooth video off, dblclick');
    await tryFullscreen(cdp, 'smooth video off, key f');
    await command(cdp, { cmd: 'start', target: 0 });
    await sleep(6000);
    const s = await status(cdp);
    report({ started: s && { running: s.running, state: s.state, error: s.error, fps: s.fps, interpolator: s.interpolator } });
    await tryFullscreen(cdp, 'smooth video on, button');
    await tryFullscreen(cdp, 'smooth video on, dblclick');
    await tryFullscreen(cdp, 'smooth video on, key f');
    const s2 = await status(cdp);
    report({ afterwards: s2 && { running: s2.running, state: s2.state, error: s2.error, fps: s2.fps } });
    await command(cdp, { cmd: 'stop' });
  } finally {
    if (cdp) await cdp.send('Browser.close').catch(() => {});
    await sleep(1500);
    if (child.exitCode === null) child.kill();
  }
}

main().catch((error) => { report({ failed: String(error.stack || error) }); process.exit(1); });
