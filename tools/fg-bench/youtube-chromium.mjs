// Tries the built Chromium extension on a real YouTube video, in a throwaway profile with the sound
// off, driven through the DevTools protocol. It never touches the user's own browser or the mouse.
//
// Usage: node youtube-chromium.mjs <work dir> <browser.exe> [video url]
// Prints one JSON line per measurement.
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..', '..');
const WORK = resolve(process.argv[2]);
const BROWSER = process.argv[3];
const URL_TO_TEST = process.argv[4] || 'https://www.youtube.com/watch?v=aqz-KE-bpKQ';
const PORT = 9333;
const MARKER = 'st-fg-window-marker';

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const report = (data) => console.log(JSON.stringify(data));

function prepareExtension() {
  const target = join(WORK, 'ext-bench-chromium');
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

  async js(expression) {
    const result = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
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
const pageSummary = (cdp) => cdp.js("({host: location.host, title: document.title, text: document.body.innerText.slice(0, 200)})");

async function dismissConsent(cdp) {
  if (!(await cdp.js('location.host')).includes('consent.')) return;
  await cdp.js(`(() => {
    const buttons = [...document.querySelectorAll('button')];
    const reject = buttons.find(b => /rechazar|reject/i.test(b.getAttribute('aria-label') || b.textContent));
    (reject || buttons[0]).click();
  })()`);
  await sleep(4000);
}

async function waitForVideo(cdp) {
  let steady = 0;
  const deadline = Date.now() + 60000;
  while (Date.now() < deadline) {
    const state = await cdp.js(`(() => {
      const v = document.querySelector('video');
      const player = document.getElementById('movie_player');
      const skip = document.querySelector('.ytp-skip-ad-button, .ytp-ad-skip-button-modern');
      if (skip) skip.click();
      if (player && player.mute) { player.mute(); if (v && v.paused) player.playVideo(); }
      if (v) v.muted = true;
      return {ad: !!(player && player.classList.contains('ad-showing')),
              ready: !!v && v.readyState >= 2 && !v.paused && v.videoWidth > 0};
    })()`);
    steady = state.ready && !state.ad ? steady + 1 : 0;
    if (steady >= 3) return true;
    await sleep(1000);
  }
  return false;
}

async function measure(cdp, label, seconds) {
  await sleep(2000); // the target change settles
  const first = await status(cdp);
  const samples = [];
  const start = Date.now();
  while (Date.now() - start < seconds * 1000) {
    await sleep(1000);
    samples.push((await status(cdp)).fps);
  }
  const last = await status(cdp);
  const elapsed = (Date.now() - start) / 1000;
  const rate = (key) => +((last.stats[key] - first.stats[key]) / elapsed).toFixed(1);
  report({
    video: await cdp.js(`(() => { const v = document.querySelector('video'); const p = document.getElementById('movie_player');
      return {paused: v.paused, ended: v.ended, ready: v.readyState, time: Math.round(v.currentTime), size: [v.videoWidth, v.videoHeight],
              ad: !!(p && p.classList.contains('ad-showing')), frames: v.getVideoPlaybackQuality().totalVideoFrames}; })()`),
    sourceResets: last.sourceResets,
    target: label, state: last.state, error: last.error, sourceHz: last.sourceHz, canvas: last.size,
    fpsPerSecond: samples,
    presentsPerS: rate('presents'), capturesPerS: rate('captures'), holdsPerS: rate('holds'),
    gapsOver20ms: last.gaps20 - first.gaps20, gapsOver50ms: last.gaps50 - first.gaps50,
    comparedFrames: last.probe.captures - first.probe.captures,
    identicalFrames: last.probe.identical - first.probe.identical,
    unreadFrames: last.probe.unread - first.probe.unread,
  });
}

async function main() {
  const extension = prepareExtension();
  const profile = join(WORK, 'chromium-profile');
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
    spawnSync('python', ['-I', '-X', 'utf8', join(HERE, 'place_window.py'), MARKER], { stdio: 'inherit' });
    await cdp.send('Page.enable');
    await cdp.send('Page.navigate', { url: URL_TO_TEST });
    await sleep(6000);
    await dismissConsent(cdp);
    if (!(await waitForVideo(cdp))) {
      report({ failed: 'the video did not start', page: await pageSummary(cdp) });
      return;
    }
    await cdp.js("(() => { const p = document.getElementById('movie_player'); if (p && p.setPlaybackQualityRange) p.setPlaybackQualityRange('hd1080', 'hd1080'); })()");
    await sleep(5000);
    await waitForVideo(cdp); // changing the quality can leave it paused
    report({
      page: (await pageSummary(cdp)).title,
      video: await cdp.js("(() => { const v = document.querySelector('video'); return [v.videoWidth, v.videoHeight]; })()"),
      dpr: await cdp.js('devicePixelRatio'),
      gpu: await cdp.js("navigator.gpu ? 'webgpu' : 'no webgpu'"),
    });
    if (!(await status(cdp))) {
      report({ failed: 'the test extension did not load', page: await pageSummary(cdp) });
      return;
    }
    await command(cdp, { cmd: 'start', target: 144 });
    await sleep(4000); // the frame rate is measured first
    await measure(cdp, 144, 14);
    for (const target of [120, 90, 60, 0]) {
      await command(cdp, { cmd: 'target', target });
      await measure(cdp, target, 8);
    }
    await command(cdp, { cmd: 'stop' });
    await sleep(1000);
    const after = await status(cdp);
    report({ afterStop: { running: after.running, state: after.state, error: after.error } });
  } finally {
    if (cdp) await cdp.send('Browser.close').catch(() => {});
    await sleep(1500);
    if (child.exitCode === null) child.kill();
  }
}

main().catch((error) => { report({ failed: String(error.stack || error) }); process.exit(1); });
