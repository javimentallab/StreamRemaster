// Starting smooth video and the subtitles by themselves when the page plays a video: the rules in
// common.js, the watcher (autostart.js) on a pretend page, and the manifests it relies on.
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const SHARED = new URL('../extension/shared/', import.meta.url);
const COMMON = readFileSync(new URL('common.js', SHARED), 'utf8');
const WATCHER = readFileSync(new URL('autostart.js', SHARED), 'utf8');
const manifest = (browser) => JSON.parse(readFileSync(new URL(`../extension/${browser}/manifest.json`, import.meta.url), 'utf8'));

function loadST(extra = {}) {
  const ctx = vm.createContext({ URL, Intl, setTimeout, clearTimeout, ...extra });
  vm.runInContext(COMMON, ctx);
  return ctx.ST;
}
const ST = loadST();

// ------------------------------------------------------------------------------- the rules

test('both options are off by default', () => {
  assert.equal(ST.DEFAULTS.fgAutoStart, false);
  assert.equal(ST.DEFAULTS.subsAutoStart, false);
});

const playing = { paused: false, ended: false, readyState: 4, videoWidth: 1920, width: 640, height: 360 };

test('isAutoStartVideo: a large video that is playing', () => {
  assert.equal(ST.isAutoStartVideo(playing), true);
  assert.equal(ST.isAutoStartVideo({ ...playing, width: 200, height: 150 }), true);
});

for (const [why, patch] of [
  ['paused', { paused: true }],
  ['ended', { ended: true }],
  ['nothing decoded yet', { readyState: 1 }],
  ['no picture (audio only)', { videoWidth: 0 }],
  ['too narrow', { width: 199 }],
  ['too short', { height: 149 }],
  ['hidden (no box)', { width: 0, height: 0 }],
]) {
  test(`isAutoStartVideo: not when ${why}`, () => {
    assert.equal(ST.isAutoStartVideo({ ...playing, ...patch }), false);
  });
}

test('isAutoStartVideo: nothing', () => {
  assert.equal(ST.isAutoStartVideo(null), false);
});

test('autoStartPageKey drops what follows "#"', () => {
  assert.equal(ST.autoStartPageKey('https://www.youtube.com/watch?v=a#t=10'), 'https://www.youtube.com/watch?v=a');
  assert.equal(ST.autoStartPageKey('https://www.twitch.tv/x'), 'https://www.twitch.tv/x');
  assert.equal(ST.autoStartPageKey(undefined), '');
});

test('tracker: once per video and feature', () => {
  const tracker = ST.autoStartTracker('page');
  const a = {};
  const b = {};
  assert.equal(tracker.take('fg', a), true);
  assert.equal(tracker.take('fg', a), false);
  assert.equal(tracker.take('subs', a), true);
  assert.equal(tracker.take('fg', b), true);
  assert.equal(tracker.take('other', a), false);
});

test('tracker: a manual "off" holds until the address changes', () => {
  const tracker = ST.autoStartTracker('page');
  const a = {};
  tracker.hold('fg');
  assert.equal(tracker.held('fg'), true);
  assert.equal(tracker.take('fg', a), false);
  assert.equal(tracker.take('subs', a), true);
  assert.equal(tracker.visit('page'), false);
  assert.equal(tracker.take('fg', a), false);
  assert.equal(tracker.visit('other page'), true);
  assert.equal(tracker.held('fg'), false);
  assert.equal(tracker.take('fg', a), true);
  assert.equal(tracker.take('subs', a), true);
});

// --------------------------------------------------------------------------- the manifests

test('the files injected for the watcher exist, and Firefox loads them all on every page', () => {
  assert.deepEqual([...ST.AUTO_FILES], [...ST.FG_FILES, 'autostart.js']);
  for (const file of ST.AUTO_FILES) assert.ok(existsSync(new URL(file, SHARED)), file);
  const scripts = manifest('firefox').content_scripts[0].js;
  for (const file of ST.AUTO_FILES) assert.ok(scripts.includes(file), file);
  assert.ok(scripts.indexOf('autostart.js') > scripts.indexOf('framegen-page.js'));
});

test('no new required permissions; every site only as an optional one in Chromium', () => {
  const chromium = manifest('chromium');
  assert.deepEqual(chromium.permissions, ['storage', 'tabCapture', 'offscreen', 'scripting', 'activeTab']);
  assert.deepEqual(chromium.optional_host_permissions, ['<all_urls>']);
  assert.equal(chromium.optional_permissions, undefined);
  assert.equal(chromium.host_permissions, undefined);
  assert.equal(chromium.content_scripts, undefined);
  assert.deepEqual([...ST.ALL_SITES.origins], chromium.optional_host_permissions);
  const firefox = manifest('firefox');
  assert.deepEqual(firefox.permissions, ['storage', '<all_urls>']);
  assert.equal(firefox.optional_permissions, undefined);
});

test('wantsAutoScripts: only with every site and the smooth video option', () => {
  assert.equal(ST.wantsAutoScripts({ fgAutoStart: true }, true), true);
  assert.equal(ST.wantsAutoScripts({ fgAutoStart: true }, false), false);
  assert.equal(ST.wantsAutoScripts({ fgAutoStart: false, subsAutoStart: true }, true), false);
  assert.equal(ST.wantsAutoScripts(null, true), false);
});

test('askAllSites / hasAllSites in Chromium', async () => {
  const asked = [];
  let granted = false;
  const permissions = {
    contains: async () => granted,
    request: (p) => { asked.push([...p.origins]); granted = true; return Promise.resolve(true); },
  };
  const S = loadST({ chrome: { permissions, runtime: { getManifest: () => ({}) } } });
  assert.equal(await S.hasAllSites(), false);
  assert.equal(await S.askAllSites(), true);
  assert.deepEqual(asked, [['<all_urls>']]);
  assert.equal(await S.hasAllSites(), true);
  const refused = loadST({ chrome: { permissions: { request: () => Promise.reject(new Error('no gesture')) }, runtime: { getManifest: () => ({}) } } });
  assert.equal(await refused.askAllSites(), false);
});

test('askAllSites / hasAllSites in Firefox: nothing to ask', async () => {
  const S = loadST({ browser: { runtime: { getManifest: () => ({ browser_specific_settings: {} }) } } });
  assert.equal(await S.hasAllSites(), true);
  assert.equal(await S.askAllSites(), true);
});

// ------------------------------------------------------------------- the watcher on a page

function video(over = {}) {
  const { width = 640, height = 360, ...rest } = over;
  return { paused: false, ended: false, readyState: 4, videoWidth: 1280, ...rest, getBoundingClientRect: () => ({ width, height }) };
}

function page(settings) {
  const sent = [];
  const starts = [];
  const timers = [];
  const listeners = [];
  const fg = { running: false };
  const state = { videos: [], visibility: 'visible' };
  const stored = { settings };
  const chrome = {
    runtime: {
      id: 'test',
      onMessage: { addListener: (f) => listeners.push(f), removeListener() {} },
      sendMessage: async (m) => { sent.push(m); return {}; },
    },
    storage: {
      local: { get: async () => ({ settings: stored.settings }), set: async () => {} },
      onChanged: { addListener() {}, removeListener() {} },
    },
  };
  const ctx = vm.createContext({
    URL, Intl, console, Promise,
    setTimeout, clearTimeout,
    setInterval: (f) => { timers.push(f); return timers.length; },
    clearInterval: () => {},
    chrome,
    location: { href: 'https://video.example/watch?v=1' },
    document: {
      get visibilityState() { return state.visibility; },
      querySelectorAll: () => state.videos,
      addEventListener() {},
      removeEventListener() {},
    },
    STFramegenPage: {
      status: () => ({ running: fg.running }),
      start: async (target) => { starts.push(target); fg.running = true; return { running: true }; },
    },
  });
  vm.runInContext(COMMON, ctx);
  vm.runInContext(WATCHER, ctx);
  const tell = (msg) => {
    let answer;
    for (const f of listeners) f(msg, {}, (r) => { answer = r; });
    return answer;
  };
  const settle = () => new Promise((r) => setImmediate(r));
  return { ctx, sent, starts, timers, fg, state, tell, settle, check: () => ctx.STAutoStart.check() };
}

test('watcher: smooth video starts once per video, at the saved frame rate', async () => {
  const p = page({ fgAutoStart: true, fgTarget: '120' });
  await p.settle();
  assert.equal(p.timers.length, 1, 'it polls while the option is on');
  p.state.videos = [video({ width: 160, height: 90 })];
  p.check();
  assert.deepEqual(p.starts, [], 'a thumbnail is not a player');
  const first = video();
  p.state.videos = [first];
  p.check();
  p.check();
  assert.deepEqual(p.starts, [120]);
  p.fg.running = false; // it stopped on its own (the video could not be read, say)
  p.check();
  assert.deepEqual(p.starts, [120], 'not again on the same video');
  p.state.videos = [video()];
  p.check();
  assert.deepEqual(p.starts, [120, 120], 'again on a new video');
  assert.deepEqual(p.sent, [], 'the subtitles option is off');
});

test('watcher: "Match the screen" is target 0', async () => {
  const p = page({ fgAutoStart: true, fgTarget: 'display' });
  await p.settle();
  p.state.videos = [video()];
  p.check();
  assert.deepEqual(p.starts, [0]);
});

test('watcher: turned off by hand, it stays off until the page goes elsewhere', async () => {
  const p = page({ fgAutoStart: true, subsAutoStart: true });
  await p.settle();
  p.state.videos = [video()];
  p.check();
  assert.equal(p.starts.length, 1);
  assert.equal(p.sent.length, 1);
  p.tell({ st: 'framegen', cmd: 'stop' });
  p.tell({ st: 'auto', cmd: 'hold', feature: 'subs' });
  p.fg.running = false;
  p.state.videos = [video()];
  p.check();
  assert.equal(p.starts.length, 1);
  assert.equal(p.sent.length, 1);
  p.ctx.location.href = 'https://video.example/watch?v=2';
  p.check();
  assert.equal(p.starts.length, 2);
  assert.equal(p.sent.length, 2);
});

test('watcher: the subtitles are asked of the background once per video', async () => {
  const p = page({ subsAutoStart: true });
  await p.settle();
  const v = video();
  p.state.videos = [v];
  p.check();
  p.check();
  assert.deepEqual(p.sent.map((m) => m.cmd), ['autoStart']);
  assert.deepEqual(p.starts, [], 'the smooth video option is off');
});

test('watcher: nothing starts in a tab out of view, or with both options off', async () => {
  const hidden = page({ fgAutoStart: true, subsAutoStart: true });
  await hidden.settle();
  hidden.state.visibility = 'hidden';
  hidden.state.videos = [video()];
  hidden.check();
  assert.deepEqual([hidden.starts, hidden.sent], [[], []]);
  hidden.state.visibility = 'visible';
  hidden.check();
  assert.equal(hidden.starts.length, 1);

  const off = page({});
  await off.settle();
  assert.equal(off.timers.length, 0, 'no polling');
  off.state.videos = [video()];
  off.check();
  assert.deepEqual([off.starts, off.sent], [[], []]);
});

test('watcher: answers the popup, so it is not injected twice', async () => {
  const p = page({});
  await p.settle();
  assert.deepEqual({ ...p.tell({ st: 'auto', cmd: 'check' }) }, { alive: true });
  assert.equal(p.tell({ st: 'overlay', op: 'show' }), undefined);
});

test('watcher: the two options are independent, also when the popup opens on the tab', async () => {
  for (const [settings, fg, subs] of [
    [{ fgAutoStart: true }, 1, 0],
    [{ subsAutoStart: true }, 0, 1],
    [{ fgAutoStart: true, subsAutoStart: true }, 1, 1],
  ]) {
    const p = page(settings);
    await p.settle();
    p.state.videos = [video()];
    p.tell({ st: 'auto', cmd: 'check' }); // what the popup sends when it opens
    await p.settle();
    await p.settle();
    assert.equal(p.starts.length, fg, JSON.stringify(settings) + ' smooth video');
    assert.equal(p.sent.length, subs, JSON.stringify(settings) + ' subtitles');
  }
});

// ------------------------------------------------------------- the Chromium service worker

function event() {
  const fns = [];
  return { addListener: (f) => fns.push(f), fire: (...a) => fns.map((f) => f(...a)) };
}

function chromiumWorker({ settings = {}, allSites = false } = {}) {
  const calls = { registered: [], injected: [], captured: [], files: [] };
  const stored = { settings, runState: { state: 'idle', tabId: null } };
  const registered = new Set();
  const perms = { granted: allSites };
  const storageChanged = event();
  const chrome = {
    runtime: {
      id: 'test', getManifest: () => ({}), getURL: (p) => p, onMessage: event(), onStartup: event(), onInstalled: event(),
      sendMessage: async () => {}, getContexts: async () => [],
    },
    storage: {
      local: {
        get: async (key) => ({ [key]: stored[key] }),
        set: async (data) => {
          for (const [key, value] of Object.entries(data)) {
            const oldValue = stored[key];
            stored[key] = value;
            storageChanged.fire({ [key]: { oldValue, newValue: value } }, 'local');
          }
        },
      },
      onChanged: storageChanged,
    },
    permissions: { contains: async () => perms.granted, onAdded: event(), onRemoved: event() },
    scripting: {
      getRegisteredContentScripts: async ({ ids }) => ids.filter((id) => registered.has(id)).map((id) => ({ id })),
      registerContentScripts: async (list) => { for (const s of list) { registered.add(s.id); calls.registered.push(s); } },
      unregisterContentScripts: async ({ ids }) => { ids.forEach((id) => registered.delete(id)); },
      executeScript: async (opts) => { calls.injected.push(opts.target.tabId); calls.files.push([...opts.files]); },
    },
    tabs: { onRemoved: event(), onUpdated: event(), query: async () => [{ id: 7 }, { id: 8 }], sendMessage: async () => {} },
    tabCapture: { getMediaStreamId: async (o) => { calls.captured.push(o.targetTabId); return 'stream'; } },
    offscreen: { createDocument: async () => {}, closeDocument: async () => {} },
    action: { setBadgeText: async () => {}, setBadgeBackgroundColor: async () => {} },
  };
  const fetch = async () => ({ ok: true, json: async () => ({}), arrayBuffer: async () => new ArrayBuffer(4) });
  const ctx = vm.createContext({ URL, Intl, console, Promise, setTimeout, clearTimeout, btoa, fetch, navigator: { language: 'en' }, chrome });
  ctx.importScripts = (...files) => {
    for (const f of files) vm.runInContext(readFileSync(new URL(f, SHARED), 'utf8'), ctx);
  };
  vm.runInContext(readFileSync(new URL('../extension/chromium/background.js', import.meta.url), 'utf8'), ctx);
  // A message from the page in tab 7, with the answer the worker sends back (if any).
  const ask = (msg) => new Promise((resolve) => {
    const keep = chrome.runtime.onMessage.fire(msg, { tab: { id: 7 } }, resolve)[0];
    if (keep !== true) resolve(undefined);
  });
  const settle = async () => { for (let i = 0; i < 20; i++) await new Promise((r) => setImmediate(r)); };
  return { chrome, ctx, calls, stored, registered, perms, ask, settle };
}

test('Chromium: with every site granted, the watcher and smooth video are registered for every page', async () => {
  const w = chromiumWorker({ settings: { fgAutoStart: true } });
  w.chrome.runtime.onStartup.fire();
  await w.settle();
  assert.equal(w.registered.size, 0, 'not without the permission');
  w.perms.granted = true;
  w.chrome.permissions.onAdded.fire({ origins: ['<all_urls>'] });
  await w.settle();
  assert.equal(w.registered.size, 1);
  const script = w.calls.registered[0];
  assert.deepEqual([...script.matches], ['<all_urls>']);
  assert.deepEqual([...script.js], [...w.ctx.ST.AUTO_FILES]);
  assert.deepEqual(w.calls.injected, [7, 8], 'the pages already open get it too');
  w.perms.granted = false;
  w.chrome.permissions.onRemoved.fire({ origins: ['<all_urls>'] });
  await w.settle();
  assert.equal(w.registered.size, 0);
});

test('Chromium: unticking smooth video takes the scripts away; the subtitles option alone does not register them', async () => {
  const w = chromiumWorker({ settings: { fgAutoStart: true }, allSites: true });
  w.chrome.runtime.onInstalled.fire();
  await w.settle();
  assert.equal(w.registered.size, 1);
  await w.ctx.ST.setSettings({ fgAutoStart: false, subsAutoStart: true });
  await w.settle();
  assert.equal(w.registered.size, 0);
});

test('Chromium: the popup saves "smooth video when a video plays" through the worker', async () => {
  const w = chromiumWorker({ allSites: true });
  w.chrome.runtime.onMessage.fire({ cmd: 'fgAutoStart', on: true }, {}, () => {});
  await w.settle();
  assert.equal(w.stored.settings.fgAutoStart, true);
  assert.equal(w.registered.size, 1);
});

test('Chromium: only the subtitles option starts the subtitles', async () => {
  const fgOnly = chromiumWorker({ settings: { fgAutoStart: true, serverUrl: 'ws://x:9090/' } });
  assert.deepEqual({ ...(await fgOnly.ask({ cmd: 'autoStart' })) }, { result: 'off' });
  assert.deepEqual(fgOnly.calls.captured, []);
  const subs = chromiumWorker({ settings: { subsAutoStart: true, serverUrl: 'ws://x:9090/' } });
  assert.deepEqual({ ...(await subs.ask({ cmd: 'autoStart' })) }, { result: 'started' });
  assert.deepEqual(subs.calls.captured, [7]);
});

test('Chromium: after a page load, smooth video files go in only when that option is on', async () => {
  const subsOnly = chromiumWorker({ settings: { subsAutoStart: true }, allSites: true });
  subsOnly.chrome.tabs.onUpdated.fire(7, { status: 'complete' });
  await subsOnly.settle();
  assert.deepEqual(subsOnly.calls.files, [[...subsOnly.ctx.ST.WATCHER_FILES]]);
  const fgNoAccess = chromiumWorker({ settings: { fgAutoStart: true } });
  fgNoAccess.chrome.tabs.onUpdated.fire(7, { status: 'complete' });
  await fgNoAccess.settle();
  assert.deepEqual(fgNoAccess.calls.files, [[...fgNoAccess.ctx.ST.AUTO_FILES]], 'activeTab only: injected by the worker');
  const fgRegistered = chromiumWorker({ settings: { fgAutoStart: true }, allSites: true });
  fgRegistered.chrome.tabs.onUpdated.fire(7, { status: 'complete' });
  await fgRegistered.settle();
  assert.deepEqual(fgRegistered.calls.files, [], 'the registered content scripts already did it');
});
