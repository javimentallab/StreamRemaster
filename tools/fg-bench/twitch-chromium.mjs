// Measures the stutter of the smooth video on a live Twitch stream, in a throwaway Brave/Chromium
// profile with the sound off, driven through the DevTools protocol. It never touches the user's own
// browser or the mouse. A control pass without the smooth video comes first, then one pass per model.
//
// Usage: node twitch-chromium.mjs <work dir> <browser.exe> [channel url] [display] [seconds per pass]
// With no channel, the most watched live stream of the directory. Prints one JSON line per pass.
import { spawn, spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..', '..');
const WORK = resolve(process.argv[2]);
const BROWSER = process.argv[3];
const CHANNEL = process.argv[4] && process.argv[4] !== '-' ? process.argv[4] : '';
const DISPLAY = process.argv[5] || '\\\\.\\DISPLAY2';
const SECONDS = Number(process.argv[6]) || 25;
const PORT = 9334;
const MARKER = 'st-fg-twitch-marker';

const sleep = (ms) => new Promise((done) => setTimeout(done, ms));
const report = (data) => console.log(JSON.stringify(data));

function prepareExtension() {
  const target = join(WORK, 'ext-bench-twitch');
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
const events = async (cdp) => JSON.parse((await cdp.js("document.documentElement.getAttribute('data-st-fg-events')")) || '[]');
const command = (cdp, payload) => cdp.js(`document.documentElement.setAttribute('data-st-fg-cmd', ${JSON.stringify(JSON.stringify(payload))})`);

// The player's own view of the video, also without the smooth video running.
const videoState = (cdp) => cdp.js(`(() => {
  const v = document.querySelector('video');
  if (!v) return null;
  const q = v.getVideoPlaybackQuality();
  return {paused: v.paused, ready: v.readyState, size: [v.videoWidth, v.videoHeight], rate: v.playbackRate,
          decoded: q.totalVideoFrames, dropped: q.droppedVideoFrames, time: +v.currentTime.toFixed(2),
          buffered: v.buffered.length ? +(v.buffered.end(v.buffered.length - 1) - v.currentTime).toFixed(2) : 0};
})()`);

async function pickChannel(cdp) {
  await cdp.send('Page.navigate', { url: 'https://www.twitch.tv/directory/all' });
  for (let i = 0; i < 30; i++) {
    await sleep(1000);
    const href = await cdp.js(`(() => { const a = document.querySelector('a[data-a-target="preview-card-image-link"]'); return a ? a.href : ''; })()`);
    if (href) return href;
  }
  throw new Error('no live stream found in the directory');
}

async function waitForVideo(cdp) {
  let steady = 0;
  const deadline = Date.now() + 90000;
  while (Date.now() < deadline) {
    const state = await cdp.js(`(() => {
      for (const sel of ['[data-a-target="content-classification-gate-overlay-start-watching-button"]',
                         '[data-a-target="player-overlay-mature-accept"]', 'button[data-a-target="consent-banner-accept"]']) {
        const b = document.querySelector(sel); if (b) b.click();
      }
      const v = document.querySelector('video');
      if (v) { v.muted = true; if (v.paused) v.play().catch(() => {}); }
      const ad = !!document.querySelector('[data-a-target="video-ad-label"], [data-a-target="video-ad-countdown"]');
      return {ad, ready: !!v && v.readyState >= 2 && !v.paused && v.videoWidth > 0};
    })()`);
    steady = state.ready && !state.ad ? steady + 1 : 0;
    if (steady >= 5) return true;
    await sleep(1000);
  }
  return false;
}

async function measure(cdp, label, running) {
  await sleep(3000); // the frame rate is measured and the timeline fitted first
  const v0 = await videoState(cdp);
  const first = running ? await status(cdp) : null;
  const t0 = Date.now();
  const fps = [];
  while (Date.now() - t0 < SECONDS * 1000) {
    await sleep(1000);
    if (running) fps.push((await status(cdp)).fps);
  }
  const elapsed = (Date.now() - t0) / 1000;
  const v1 = await videoState(cdp);
  const out = {
    pass: label, seconds: +elapsed.toFixed(1), size: v1.size, playbackRate: v1.rate, buffered: v1.buffered,
    decodedPerS: +((v1.decoded - v0.decoded) / elapsed).toFixed(2), droppedByBrowser: v1.dropped - v0.dropped,
  };
  if (running) {
    const last = await status(cdp);
    const rate = (key) => +((last.stats[key] - first.stats[key]) / elapsed).toFixed(1);
    const d = (key) => last.diag[key] - first.diag[key];
    Object.assign(out, {
      state: last.state, error: last.error, model: last.model, sourceHz: last.sourceHz, timeline: last.timeline,
      fpsMin: Math.min(...fps), fpsMax: Math.max(...fps), fpsPerSecond: fps,
      presentsPerS: rate('presents'), capturesPerS: rate('captures'), holdsPerS: rate('holds'),
      interpolateSkippedPerS: rate('interpolateSkipped'), upscaleSkippedPerS: rate('upscaleSkipped'),
      tickGapsOver20ms: last.gaps20 - first.gaps20, tickGapsOver50ms: last.gaps50 - first.gaps50,
      takenTwice: last.probe.identical - first.probe.identical, compared: last.probe.captures - first.probe.captures,
      skippedFrames: d('skipped'), skipEvents: d('skipEvents'), backwards: d('backwards'), waiting: d('waiting'),
      stalled: d('stalled'), rateChanges: d('rateChanges'), resizes: d('resizes'), rebuilds: d('rebuilds'),
      sourceResets: last.sourceResets,
    });
    out.events = (await events(cdp)).slice(-40);
  }
  report(out);
}

async function main() {
  const extension = prepareExtension();
  const profile = join(WORK, 'twitch-profile');
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
    const url = CHANNEL || await pickChannel(cdp);
    // the best quality the stream has ("chunked" is Twitch's name for the source)
    await cdp.send('Page.navigate', { url: 'https://www.twitch.tv/' });
    await sleep(4000);
    await cdp.js(`localStorage.setItem('video-quality', JSON.stringify({default: 'chunked'})); localStorage.setItem('volume', '0'); true`);
    await cdp.send('Page.navigate', { url });
    await sleep(8000);
    if (!(await waitForVideo(cdp))) {
      report({ failed: 'the stream did not start', url, title: await cdp.js('document.title') });
      return;
    }
    report({ url, title: await cdp.js('document.title'), video: await videoState(cdp), dpr: await cdp.js('devicePixelRatio') });
    if (!(await status(cdp))) {
      report({ failed: 'the test extension did not load' });
      return;
    }
    await measure(cdp, 'control (no smooth video)', false);
    for (const [label, id] of [['StreamRemaster', 'builtin-st'], ['none (cross-fade)', '']]) {
      await command(cdp, { cmd: 'model', id });
      await sleep(1000);
      await command(cdp, { cmd: 'start', target: 144 });
      await sleep(3000);
      await measure(cdp, label, true);
      await command(cdp, { cmd: 'stop' });
      await sleep(1500);
    }
    await measure(cdp, 'control again', false);
  } finally {
    if (cdp) await cdp.send('Browser.close').catch(() => {});
    await sleep(1500);
    if (child.exitCode === null) child.kill();
  }
}

main().catch((error) => { report({ failed: String(error.stack || error) }); process.exit(1); });
