// Shared helpers for every extension page (popup, settings, background, engines).
// Works in Chromium (chrome.*) and Firefox (browser.*).
"use strict";

var ext = globalThis.browser || globalThis.chrome;

var ST = globalThis.ST || {};
globalThis.ST = ST;

ST.DEFAULTS = {
  serverUrl: "",          // e.g. ws://192.168.1.10:9090  (empty = not configured yet)
  model: "",              // model id from the server ("" = server default)
  sourceLang: "",         // "" = auto-detect
  targetLang: "",         // "" = keep the original language
  captionLines: 2,
  fontSize: 22,
  saveSrt: false,
  useVad: true,
  precision: "auto",      // auto | int8 (half the GPU memory, same output)
  translatorDevice: "auto", // auto | cpu
  uiLang: "auto",         // auto | en | es
  popupTab: "subs",       // subs | fg
  fgTarget: "display",    // display | a number of frames per second
  fgResolution: "original", // original | display | an output height
  fgSharpen: "medium",       // off | soft | medium | strong: adaptive sharpening of what is shown
  fgModel: "builtin-st",  // id of the smooth video model ("" = none: plain cross-fade and scaling)
  fgAutoStart: false,     // turn smooth video on by itself when the page plays a video
  subsAutoStart: false,   // start the subtitles by themselves when the page plays a video
};

// ---------------------------------------------------------------------------- auto start
// autostart.js watches the page and turns the two features on by themselves when a video plays,
// if the user ticked those options. The rules live here so they can be tested without a browser.

// What the page side of smooth video needs, and the watcher after it.
ST.FG_FILES = ["common.js", "framegen.js", "framegen-sr.js", "framegen-fi.js", "framegen-model.js", "framegen-page.js"];
ST.AUTO_FILES = ST.FG_FILES.concat("autostart.js");
// The watcher alone, for the subtitles (they start from the background).
ST.WATCHER_FILES = ["common.js", "autostart.js"];

// Chromium: optional access to every site, asked for when the user ticks "turn on smooth video when a
// video plays". With it the watcher runs on every page; without it, only on the tabs where the user
// clicked the extension's button (activeTab). Firefox already has it from the install.
ST.ALL_SITES = { origins: ["<all_urls>"] };
ST.AUTO_SCRIPT_ID = "streamremaster-autostart";

ST.hasAllSites = async function () {
  if (ST.isFirefox()) return true;
  try {
    return !!(ext.permissions && (await ext.permissions.contains(ST.ALL_SITES)));
  } catch (e) {
    return false;
  }
};

// Call it straight from the click, before anything is awaited: the browser only asks during a user
// gesture. Resolves true when granted (or nothing had to be asked).
ST.askAllSites = function () {
  if (ST.isFirefox()) return Promise.resolve(true);
  if (!ext.permissions || !ext.permissions.request) return Promise.resolve(false);
  try {
    return Promise.resolve(ext.permissions.request(ST.ALL_SITES)).then((granted) => !!granted, () => false);
  } catch (e) {
    return Promise.resolve(false);
  }
};

// Whether the watcher and smooth video should be registered on every page (Chromium).
ST.wantsAutoScripts = function (settings, allSites) {
  return !!(allSites && settings && settings.fgAutoStart);
};

// Smaller than this it is a preview, an advert in a corner or a thumbnail playing on hover.
ST.AUTO_MIN_WIDTH = 200;
ST.AUTO_MIN_HEIGHT = 150;

// v: {paused, ended, readyState, videoWidth, width, height}, width and height in CSS pixels on screen.
ST.isAutoStartVideo = function (v) {
  return !!v && !v.paused && !v.ended && v.readyState >= 2 && v.videoWidth > 0 &&
    v.width >= ST.AUTO_MIN_WIDTH && v.height >= ST.AUTO_MIN_HEIGHT;
};

// The address of the page, without the part after "#": a new key means the user went elsewhere.
ST.autoStartPageKey = function (href) {
  const text = String(href || "");
  const hash = text.indexOf("#");
  return hash < 0 ? text : text.slice(0, hash);
};

// Remembers, for one page, which videos each feature has already been started on and whether the
// user turned it off by hand. A new address forgets both; a reload makes a new tracker.
ST.autoStartTracker = function (pageKey) {
  const FEATURES = ["fg", "subs"];
  let page = pageKey;
  let tried;
  let held;
  const forget = () => {
    tried = {};
    held = {};
    for (const feature of FEATURES) { tried[feature] = new WeakSet(); held[feature] = false; }
  };
  forget();
  return {
    // true when the address changed.
    visit(key) {
      if (key === page) return false;
      page = key;
      forget();
      return true;
    },
    hold(feature) { if (feature in held) held[feature] = true; },
    held(feature) { return !!held[feature]; },
    // true once per video and feature, and never while the user's "off" holds.
    take(feature, video) {
      if (!(feature in tried) || held[feature] || tried[feature].has(video)) return false;
      tried[feature].add(video);
      return true;
    },
  };
};

// Models that ship inside the extension. The background copies them into storage.local next to the
// ones the user adds, so every page reads them the same way; they cannot be deleted.
ST.BUILTIN_FG_MODELS = [
  { id: "builtin-st", kind: "st", name: "StreamRemaster", file: "models/streamremaster.stmodel" },
];

// When the page goes fullscreen, the window follows. Chromium keeps a captured tab's fullscreen
// inside the tab (the subtitles capture it), so the window has to be made fullscreen here; where
// the browser already did it, nothing changes. On the way out the window goes back to how it was
// (maximized, normal…), and only if it was this code that made it fullscreen.
ST.windowFullscreen = async function (windowId, on) {
  try {
    const { fsWindows } = await ext.storage.local.get("fsWindows");
    const before = fsWindows || {};
    const win = await ext.windows.get(windowId);
    if (on) {
      if (win.state === "fullscreen") return;
      before[windowId] = win.state;
      await ext.storage.local.set({ fsWindows: before });
      await ext.windows.update(windowId, { state: "fullscreen" });
    } else {
      const state = before[windowId];
      if (!state) return;
      delete before[windowId];
      await ext.storage.local.set({ fsWindows: before });
      if (win.state === "fullscreen") await ext.windows.update(windowId, { state });
    }
  } catch (e) {
    console.warn("[streamremaster] window fullscreen:", e);
  }
};

ST.installBuiltinModels = async function () {
  const { fgModels } = await ext.storage.local.get("fgModels");
  const models = {};
  for (const model of ST.BUILTIN_FG_MODELS) {
    try {
      const response = await fetch(ext.runtime.getURL(model.file));
      if (!response.ok) throw new Error(response.status);
      const buffer = await response.arrayBuffer();
      models[model.id] = { id: model.id, kind: model.kind, name: model.name, size: buffer.byteLength, builtin: true, data: ST.bufferToBase64(buffer) };
    } catch (error) {
      console.warn("[streamremaster] built-in model not installed:", model.file, error);
    }
  }
  // Built-in models first, then the user's own; an old built-in entry is replaced.
  for (const [id, model] of Object.entries(fgModels || {})) {
    if (!model.builtin) models[id] = model;
  }
  await ext.storage.local.set({ fgModels: models });
};

// Small binary payloads (the video models) travel through storage.local as base64.
ST.bufferToBase64 = function (buffer) {
  const bytes = new Uint8Array(buffer);
  let text = "";
  for (let i = 0; i < bytes.length; i += 0x8000) text += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(text);
};

ST.base64ToBuffer = function (data) {
  const text = atob(data);
  const bytes = new Uint8Array(text.length);
  for (let i = 0; i < text.length; i++) bytes[i] = text.charCodeAt(i);
  return bytes.buffer;
};

ST.getSettings = async function () {
  const { settings } = await ext.storage.local.get("settings");
  const merged = Object.assign({}, ST.DEFAULTS, settings || {});
  // the two built-in models of before became one, and so did their two choices
  if (merged.fgModel === "builtin-sr" || merged.fgModel === "builtin-fi") merged.fgModel = "builtin-st";
  delete merged.fgInterpModel;
  return merged;
};

ST.setSettings = async function (patch) {
  const cur = await ST.getSettings();
  const next = Object.assign(cur, patch);
  await ext.storage.local.set({ settings: next });
  return next;
};

// "192.168.1.10:9090", "http://host:9090", "wss://host/ws" ... -> a WebSocket URL.
ST.normalizeServerUrl = function (raw) {
  let s = String(raw || "").trim();
  if (!s) return "";
  if (/^https?:\/\//i.test(s)) s = s.replace(/^http/i, "ws");
  if (!/^wss?:\/\//i.test(s)) s = "ws://" + s;
  try {
    const u = new URL(s);
    if (!u.hostname) return "";
    if (!u.port && u.protocol === "ws:" && u.pathname === "/") u.port = "9090";
    return u.toString();
  } catch (e) {
    return "";
  }
};

ST.prettyServer = function (url) {
  try {
    const u = new URL(url);
    return u.host + (u.pathname !== "/" ? u.pathname : "");
  } catch (e) {
    return url || "";
  }
};

// One-shot request to the Stream Transcription extension of the server.
// Resolves {ok:true, ...} / {ok:false, error}. A plain WhisperLive server does not know
// the protocol and just closes the socket: that comes back as error "unsupported".
ST.serverRequest = function (url, payload, timeoutMs = 8000) {
  return new Promise((resolve) => {
    let done = false;
    let ws;
    const finish = (res) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      try { ws && ws.close(); } catch (e) { /* ignore */ }
      resolve(res);
    };
    const timer = setTimeout(() => finish({ ok: false, error: "timeout" }), timeoutMs);
    let opened = false;
    try {
      ws = new WebSocket(url);
    } catch (e) {
      finish({ ok: false, error: "bad_url" });
      return;
    }
    ws.onopen = () => {
      opened = true;
      ws.send(JSON.stringify(payload));
    };
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data && data.st) finish(data);
        else finish({ ok: false, error: "unsupported" });
      } catch (e) {
        finish({ ok: false, error: "unsupported" });
      }
    };
    ws.onerror = () => finish({ ok: false, error: opened ? "unsupported" : "unreachable" });
    ws.onclose = () => finish({ ok: false, error: opened ? "unsupported" : "unreachable" });
  });
};

ST.connectedText = function (n) {
  return n === 1 ? ST.t("server_ok_one_model") : ST.t("server_ok_models", n);
};

ST.formatBytes = function (n) {
  if (!n) return "0 MB";
  if (n >= 1e9) return (n / 1e9).toFixed(1).replace(/\.0$/, "") + " GB";
  if (n < 1e6) return Math.max(1, Math.round(n / 1e3)) + " KB";
  return Math.round(n / 1e6) + " MB";
};

// "Systran/faster-whisper-large-v3" -> {name: "faster-whisper-large-v3", org: "Systran"}
ST.splitModelId = function (id) {
  if (!id) return { name: "", org: "" };
  if (id.startsWith("url:")) return { name: id.slice(4), org: "" };
  const i = id.indexOf("/");
  return i < 0 ? { name: id, org: "" } : { name: id.slice(i + 1), org: id.slice(0, i) };
};

// Size names a plain WhisperLive server understands (no model management).
ST.STOCK_MODELS = ["tiny", "base", "small", "medium", "large-v3", "large-v3-turbo"];

// Suggestions on the "add model" form. All tested with faster-whisper.
ST.SUGGESTED_MODELS = [
  "Systran/faster-whisper-small",
  "Systran/faster-whisper-medium",
  "Systran/faster-whisper-large-v3",
  "deepdml/faster-whisper-large-v3-turbo-ct2",
];

// Languages Whisper can recognise (ISO 639-1, plus haw/jw/yue). Names come from
// Intl.DisplayNames in the interface language, so they never need translating.
ST.WHISPER_LANGS = [
  "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs",
  "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu",
  "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka",
  "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml",
  "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt",
  "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw",
  "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo",
  "yue", "zh",
];

// Languages the server's translator (SMALL100 / M2M100) can write.
ST.TRANSLATION_LANGS = [
  "af", "am", "ar", "az", "ba", "be", "bg", "bn", "br", "bs", "ca", "cs", "cy", "da",
  "de", "el", "en", "es", "et", "fa", "fi", "fr", "ga", "gl", "gu", "ha", "he", "hi",
  "hr", "ht", "hu", "hy", "id", "ig", "is", "it", "ja", "jv", "ka", "kk", "km", "kn",
  "ko", "lb", "lg", "ln", "lo", "lt", "lv", "mg", "mk", "ml", "mn", "mr", "ms", "my",
  "ne", "nl", "no", "ns", "oc", "or", "pa", "pl", "ps", "pt", "ro", "ru", "sd", "si",
  "sk", "sl", "so", "sq", "sr", "ss", "su", "sv", "sw", "ta", "th", "tl", "tn", "tr",
  "uk", "ur", "uz", "vi", "wo", "xh", "yi", "yo", "zh", "zu",
];

ST.languageName = function (code, uiLang) {
  const alias = { jw: "jv", haw: "haw", yue: "yue", ns: "nso" };
  try {
    const dn = new Intl.DisplayNames([uiLang || "en"], { type: "language" });
    const name = dn.of(alias[code] || code);
    if (name && name !== code) return name.charAt(0).toLocaleUpperCase(uiLang) + name.slice(1);
  } catch (e) { /* ignore */ }
  return code;
};

ST.sortedLanguages = function (codes, uiLang) {
  return codes
    .map((c) => ({ code: c, name: ST.languageName(c, uiLang) }))
    .sort((a, b) => a.name.localeCompare(b.name, uiLang));
};

// ------------------------------------------------------------------------------- updates
// Only when the user presses "Check for updates": nothing is checked in the background.
// The extension never replaces itself: it says there is a new version and opens the page
// to get it (the add-on's page on AMO in Firefox, the release on GitHub in Chromium).

ST.REPO = "javimentallab/stream-transcription";
ST.RELEASES_API = "https://api.github.com/repos/" + ST.REPO + "/releases/latest";
ST.RELEASES_PAGE = "https://github.com/" + ST.REPO + "/releases/latest";
ST.AMO_PAGE = "https://addons.mozilla.org/firefox/addon/stream-transcription/";

// "v2.1.0", "2.1", "2.2.0-beta.1" -> {nums: [2, 1, 0], pre: [...]}; anything else -> null.
ST.parseVersion = function (v) {
  const m = /^\s*v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?\s*$/
    .exec(v == null ? "" : String(v));
  if (!m) return null;
  return { nums: [Number(m[1]), Number(m[2] || 0), Number(m[3] || 0)], pre: m[4] ? m[4].split(".") : [] };
};

// Semantic versioning order: -1, 0 or 1; null if either is not a version.
ST.compareVersions = function (a, b) {
  const x = ST.parseVersion(a);
  const y = ST.parseVersion(b);
  if (!x || !y) return null;
  for (let i = 0; i < 3; i++) {
    if (x.nums[i] !== y.nums[i]) return x.nums[i] < y.nums[i] ? -1 : 1;
  }
  // 2.0.0-beta < 2.0.0
  if (!x.pre.length || !y.pre.length) return x.pre.length === y.pre.length ? 0 : (x.pre.length ? -1 : 1);
  for (let i = 0; i < Math.max(x.pre.length, y.pre.length); i++) {
    const p = x.pre[i];
    const q = y.pre[i];
    if (p === undefined) return -1;
    if (q === undefined) return 1;
    if (p === q) continue;
    const pn = /^\d+$/.test(p);
    const qn = /^\d+$/.test(q);
    if (pn && qn) return Number(p) < Number(q) ? -1 : 1;
    if (pn !== qn) return pn ? -1 : 1;     // numbers go before words
    return p < q ? -1 : 1;
  }
  return 0;
};

ST.isFirefox = function () {
  try { return !!ext.runtime.getManifest().browser_specific_settings; } catch (e) { return false; }
};

// Asks GitHub for the latest release. Resolves
//   {ok: true, current, latest, newer, page}   or   {ok: false, error}
// with error "timeout" | "network" | "rate_limited" | "no_release" | "http" | "bad_reply".
// The browser sends its own User-Agent (an extension cannot change it in Chromium, and the
// browser's is the least telling one anyway); no cookies, no referrer.
ST.checkForUpdate = async function (opts = {}) {
  const current = opts.current || ext.runtime.getManifest().version;
  const fetchFn = opts.fetch || globalThis.fetch;
  const timeoutMs = opts.timeoutMs || 8000;
  const ctrl = typeof AbortController === "function" ? new AbortController() : null;
  let timer;
  const timeout = new Promise((resolve) => {
    timer = setTimeout(() => {
      try { ctrl && ctrl.abort(); } catch (e) { /* ignore */ }
      resolve({ ok: false, error: "timeout" });
    }, timeoutMs);
  });
  const ask = (async () => {
    let res;
    try {
      res = await fetchFn(ST.RELEASES_API, {
        headers: { Accept: "application/vnd.github+json" },
        cache: "no-store", credentials: "omit", referrerPolicy: "no-referrer",
        signal: ctrl ? ctrl.signal : undefined,
      });
    } catch (e) {
      return { ok: false, error: "network" };
    }
    if (res.status === 403 || res.status === 429) return { ok: false, error: "rate_limited" };
    if (res.status === 404) return { ok: false, error: "no_release" };
    if (!res.ok) return { ok: false, error: "http" };
    let data;
    try { data = await res.json(); } catch (e) { return { ok: false, error: "bad_reply" }; }
    const latest = data && typeof data.tag_name === "string" ? data.tag_name.trim().replace(/^v/i, "") : "";
    const cmp = ST.compareVersions(latest, current);
    if (cmp === null) return { ok: false, error: "bad_reply" };
    const own = "https://github.com/" + ST.REPO + "/releases/";
    const release = typeof data.html_url === "string" && data.html_url.startsWith(own) ? data.html_url : ST.RELEASES_PAGE;
    return { ok: true, current, latest, newer: cmp > 0, page: ST.isFirefox() ? ST.AMO_PAGE : release };
  })();
  try {
    return await Promise.race([ask, timeout]);
  } finally {
    clearTimeout(timer);
  }
};

// The server's version (newer servers send it with every answer) against the latest release:
// "unknown" (it does not say: older server), "newer" (a newer release exists) or "current".
ST.serverUpdateState = function (serverVersion, latest) {
  const cmp = ST.compareVersions(latest, serverVersion);
  if (cmp === null) return "unknown";
  return cmp > 0 ? "newer" : "current";
};

// What the README says to run, on the computer where the server is.
ST.SERVER_UPDATE_COMMANDS = "cd stream-transcription\ngit pull\ncd server\ndocker compose up -d --build";
