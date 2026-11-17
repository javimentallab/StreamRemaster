// Firefox background page: starts/stops the engine in the tab's content script, keeps
// the run state and relays engine events to the overlay.
"use strict";

const CONTENT_FILES = ["common.js", "engine-common.js", "overlay.js", "content.js"];

function toTab(tabId, msg) {
  if (typeof tabId !== "number") return Promise.resolve();
  return browser.tabs.sendMessage(tabId, msg).catch(() => {});
}

async function ping(tabId) {
  try {
    return await browser.tabs.sendMessage(tabId, { st: "engine", cmd: "ping" });
  } catch (e) {
    return null;
  }
}

// Tabs opened before the add-on was installed have no content script yet.
async function ensureContent(tabId) {
  if (await ping(tabId)) return true;
  try {
    for (const file of CONTENT_FILES) await browser.tabs.executeScript(tabId, { file });
  } catch (e) {
    return false;
  }
  return !!(await ping(tabId));
}

async function start(tabId) {
  const settings = await ST.getSettings();
  await ST.i18n.init();
  await stop({ quiet: true });

  if (!ST.subsReady(settings)) {
    await Engine.setRun({ state: "error", error: settings.engine === "local" ? "local_missing" : "no_server", tabId: null });
    return;
  }
  if (!(await ensureContent(tabId))) {
    await Engine.setRun({ state: "error", error: "capture", tabId: null });
    return;
  }
  await Engine.setRun({ state: "connecting", tabId, detectedLang: null, error: null, startedAt: Date.now() });
  await toTab(tabId, {
    st: "overlay", op: "show", lines: settings.captionLines, fontSize: settings.fontSize,
    saveSrt: settings.saveSrt, status: ST.t("status_connecting"),
  });
  await toTab(tabId, {
    st: "engine", cmd: "start", serverUrl: settings.serverUrl,
    options: Engine.wsOptions(settings), translating: Engine.isTranslating(settings),
    localModel: settings.engine === "local" ? settings.localModel : null,
  });
}

async function stop({ quiet = false, byUser = false } = {}) {
  const { runState } = await browser.storage.local.get("runState");
  const settings = await ST.getSettings();
  // Turned off by hand: the page must not start them again by itself (autostart.js).
  if (byUser && runState && typeof runState.tabId === "number") {
    await toTab(runState.tabId, { st: "auto", cmd: "hold", feature: "subs" });
  }
  if (runState && typeof runState.tabId === "number") {
    await toTab(runState.tabId, { st: "engine", cmd: "stop" });
    await toTab(runState.tabId, { st: "overlay", op: "stop", saveSrt: settings.saveSrt });
  }
  if (!quiet || (runState && runState.state !== "error")) {
    await Engine.setRun({ state: "idle", tabId: null, error: null });
  }
}

// The page in a tab saw a video playing and the user wants the subtitles started by themselves.
// A run in another tab, or an error still on screen, is left alone.
const START_GRACE_MS = 5000;
let autoStarting = false;

async function autoStart(tabId) {
  if (autoStarting) return "busy";
  autoStarting = true;
  try {
    const settings = await ST.getSettings();
    if (!settings.subsAutoStart || !ST.subsReady(settings)) return "off";
    const { runState } = await browser.storage.local.get("runState");
    if (runState && typeof runState.tabId === "number") {
      if (runState.state === "error") return "busy";
      if (Engine.ACTIVE.includes(runState.state)) {
        // A reloaded page loses its engine, and its "hello" may come after this message.
        const fresh = Date.now() - (runState.startedAt || 0) < START_GRACE_MS;
        const res = fresh ? null : await ping(runState.tabId);
        if (fresh || (res && res.capturing)) return runState.tabId === tabId ? "running" : "busy";
      }
    }
    await start(tabId);
    return "started";
  } finally {
    autoStarting = false;
  }
}

async function onEngine(msg, sender) {
  const { runState } = await browser.storage.local.get("runState");
  const tabId = runState && runState.tabId;
  if (!tabId || !sender.tab || sender.tab.id !== tabId) return;
  await ST.i18n.init();

  if (msg.evt === "hello") {
    // A fresh content script in the capturing tab = the page was reloaded and the
    // engine went with it. (Ignore our own injection right at start.)
    if (Engine.ACTIVE.includes(runState.state) && Date.now() - (runState.startedAt || 0) > 5000) {
      await Engine.setRun({ state: "idle", tabId: null });
    }
  } else if (msg.evt === "state") {
    await Engine.setRun({ state: msg.state, error: msg.error || null, detail: msg.detail || null });
    const text = Engine.overlayStatus(msg);
    if (text !== undefined) {
      await toTab(tabId, { st: "overlay", op: "status", text, bad: ["error", "stalled", "noresponse"].includes(msg.state) });
    }
  } else if (msg.evt === "segments") {
    await toTab(tabId, { st: "overlay", op: "segments", segments: msg.segments });
  } else if (msg.evt === "language") {
    await Engine.setRun({ detectedLang: msg.lang });
  }
}

browser.runtime.onMessage.addListener((msg, sender) => {
  if (!msg) return;
  if (msg.cmd === "pageFullscreen") {
    if (sender.tab) ST.windowFullscreen(sender.tab.windowId, !!msg.on);
    return;
  }
  if (msg.from === "engine") {
    onEngine(msg, sender);
    return;
  }
  if (msg.cmd === "autoStart") {
    return sender.tab ? autoStart(sender.tab.id).then((result) => ({ result })) : undefined;
  }
  switch (msg.cmd) {
    case "start":
      start(msg.tabId);
      break;
    case "stop":
      stop({ byUser: true });
      break;
    case "verify":
      (async () => {
        const { runState } = await browser.storage.local.get("runState");
        if (runState && Engine.ACTIVE.includes(runState.state)) {
          const res = await ping(runState.tabId);
          if (!res || !res.capturing) await Engine.setRun({ state: "idle", tabId: null });
        }
      })();
      break;
    case "style":
      browser.storage.local.get("runState").then(({ runState }) => {
        if (runState && runState.tabId) {
          toTab(runState.tabId, { st: "overlay", op: "style", lines: msg.captionLines, fontSize: msg.fontSize });
        }
      });
      break;
  }
});

// Whisper on this computer, for the content script's Engine.PortSession: the models live
// in this page's storage and it has the graphics card.
browser.runtime.onConnect.addListener((port) => {
  if (port.name !== "st-local") return;
  let session = null;
  const send = (msg) => { try { port.postMessage(msg); } catch (e) { /* tab gone */ } };
  port.onMessage.addListener((m) => {
    if (!m) return;
    if (m.cmd === "start" && !session) {
      session = new Engine.LocalSession({ modelId: m.modelId, options: m.options, emit: send });
      session.connect();
    } else if (m.audio && session) {
      session.sendAudio(m.audio instanceof Float32Array ? m.audio : new Float32Array(m.audio));
    }
  });
  port.onDisconnect.addListener(() => { if (session) session.close(); session = null; });
});

browser.tabs.onRemoved.addListener(async (tabId) => {
  const { runState } = await browser.storage.local.get("runState");
  if (runState && runState.tabId === tabId) Engine.setRun({ state: "idle", tabId: null });
});

browser.runtime.onStartup.addListener(() => {
  Engine.setRun({ state: "idle", tabId: null });
  ST.installBuiltinModels();
});
browser.runtime.onInstalled.addListener(() => {
  Engine.setRun({ state: "idle", tabId: null });
  ST.installBuiltinModels();
});
