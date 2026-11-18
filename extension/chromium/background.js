// Chromium service worker: starts/stops the capture, keeps the run state and relays
// between the offscreen document (audio + WebSocket) and the overlay in the tab.
"use strict";

importScripts("common.js", "i18n.js", "engine-common.js");

const OFFSCREEN_URL = "offscreen.html";

async function hasOffscreen() {
  if (chrome.runtime.getContexts) {
    const ctx = await chrome.runtime.getContexts({ contextTypes: ["OFFSCREEN_DOCUMENT"] });
    return ctx.length > 0;
  }
  return chrome.offscreen.hasDocument ? chrome.offscreen.hasDocument() : false;
}

async function ensureOffscreen() {
  if (await hasOffscreen()) return;
  await chrome.offscreen.createDocument({
    url: OFFSCREEN_URL,
    reasons: ["USER_MEDIA"],
    justification: "Capture the tab audio and transcribe it, on the transcription server or on this computer.",
  });
}

async function closeOffscreen() {
  if (await hasOffscreen()) {
    try { await chrome.offscreen.closeDocument(); } catch (e) { /* already gone */ }
  }
}

function toTab(tabId, msg) {
  if (typeof tabId !== "number") return Promise.resolve();
  return chrome.tabs.sendMessage(tabId, Object.assign({ st: "overlay" }, msg)).catch(() => {});
}

async function injectOverlay(tabId) {
  await chrome.scripting.executeScript({ target: { tabId }, files: ["overlay.js"] });
}

async function start(tabId, streamId) {
  const settings = await ST.getSettings();
  await ST.i18n.init();
  await stop({ quiet: true });

  if (!ST.subsReady(settings)) {
    await Engine.setRun({ state: "error", error: settings.engine === "local" ? "local_missing" : "no_server", tabId: null });
    return;
  }
  if (!streamId) {
    await Engine.setRun({ state: "error", error: "capture", tabId: null });
    return;
  }
  try {
    await injectOverlay(tabId);
  } catch (e) {
    await Engine.setRun({ state: "error", error: "capture", tabId: null });
    return;
  }

  await Engine.setRun({ state: "connecting", tabId, detectedLang: null, error: null });
  await toTab(tabId, {
    op: "show", lines: settings.captionLines, fontSize: settings.fontSize,
    saveSrt: settings.saveSrt, status: ST.t("status_connecting"),
  });

  try {
    await ensureOffscreen();
    const msg = {
      target: "offscreen", cmd: "start", streamId,
      options: Engine.wsOptions(settings), serverUrl: settings.serverUrl,
      translating: Engine.isTranslating(settings),
      localModel: settings.engine === "local" ? settings.localModel : null,
    };
    // A just-created offscreen document may not be listening yet.
    for (let i = 0; ; i++) {
      try {
        await chrome.runtime.sendMessage(msg);
        break;
      } catch (e) {
        if (i >= 30) throw e;
        await new Promise((r) => setTimeout(r, 100));
      }
    }
  } catch (e) {
    console.error("[streamremaster] could not start the offscreen engine", e);
    await Engine.setRun({ state: "error", error: "capture" });
    await toTab(tabId, { op: "stop" });
  }
}

async function stop({ quiet = false, byUser = false } = {}) {
  const { runState } = await chrome.storage.local.get("runState");
  const settings = await ST.getSettings();
  // Turned off by hand: the page must not start them again by itself (autostart.js).
  if (byUser && runState && typeof runState.tabId === "number") {
    await toTab(runState.tabId, { st: "auto", cmd: "hold", feature: "subs" });
  }
  try { await chrome.runtime.sendMessage({ target: "offscreen", cmd: "stop" }); } catch (e) { /* none */ }
  await closeOffscreen();
  if (runState && typeof runState.tabId === "number") {
    await toTab(runState.tabId, { op: "stop", saveSrt: settings.saveSrt });
  }
  if (!quiet || (runState && runState.state !== "error")) {
    await Engine.setRun({ state: "idle", tabId: null, error: null });
  }
}

// The page in a tab saw a video playing and the user wants the subtitles started by themselves.
// Chromium only lets the extension capture a tab after the user invoked it there (its button:
// activeTab), and keeps that until the tab goes to another site; anywhere else the stream id is
// refused and nothing happens. A run in another tab, or an error still on screen, is left alone.
let autoStarting = false;

async function autoStart(tabId) {
  if (autoStarting) return "busy";
  autoStarting = true;
  try {
    const settings = await ST.getSettings();
    if (!settings.subsAutoStart || !ST.subsReady(settings)) return "off";
    const { runState } = await chrome.storage.local.get("runState");
    if (runState && typeof runState.tabId === "number") {
      if (runState.state === "error") return "busy";
      if (Engine.ACTIVE.includes(runState.state) && (await hasOffscreen())) {
        return runState.tabId === tabId ? "running" : "busy";
      }
    }
    let streamId;
    try {
      streamId = await chrome.tabCapture.getMediaStreamId({ targetTabId: tabId });
    } catch (e) {
      return "not_allowed";
    }
    await start(tabId, streamId);
    return "started";
  } finally {
    autoStarting = false;
  }
}

// After each load, the page gets the watcher back where the extension may still run scripts (the
// tabs where the user opened the popup, until they go to another site). Elsewhere this fails quietly.
// With access to every site the registered content scripts already do it.
async function armAutoStart(tabId) {
  const settings = await ST.getSettings();
  if (!settings.fgAutoStart && !settings.subsAutoStart) return;
  if (ST.wantsAutoScripts(settings, await ST.hasAllSites())) return;
  // Smooth video's files only when that option is on: with every site granted, this runs everywhere.
  const files = settings.fgAutoStart ? ST.AUTO_FILES : ST.WATCHER_FILES;
  try {
    await chrome.scripting.executeScript({ target: { tabId }, files });
  } catch (e) { /* no access to this tab */ }
}

// With the optional access to every site and "turn on smooth video when a video plays" ticked, the
// watcher and smooth video run on every page, as content scripts registered here. Without either,
// they go away. Called on start-up, when the access is granted or taken back and when the option
// changes. On a fresh grant, the pages already open get them too.
let syncingScripts = Promise.resolve();

function syncAutoScripts(injectOpenTabs = false) {
  syncingScripts = syncingScripts.then(() => doSyncAutoScripts(injectOpenTabs)).catch((e) => {
    console.warn("[streamremaster] auto start scripts:", e);
  });
  return syncingScripts;
}

async function doSyncAutoScripts(injectOpenTabs) {
  const want = ST.wantsAutoScripts(await ST.getSettings(), await ST.hasAllSites());
  const ids = [ST.AUTO_SCRIPT_ID];
  const have = (await chrome.scripting.getRegisteredContentScripts({ ids })).length > 0;
  if (want && !have) {
    await chrome.scripting.registerContentScripts([{
      id: ST.AUTO_SCRIPT_ID, matches: ["<all_urls>"], js: ST.AUTO_FILES, runAt: "document_idle",
    }]);
  } else if (!want && have) {
    await chrome.scripting.unregisterContentScripts({ ids });
  }
  if (want && injectOpenTabs) {
    for (const tab of await chrome.tabs.query({})) {
      chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ST.AUTO_FILES }).catch(() => {});
    }
  }
}

chrome.permissions.onAdded.addListener(() => syncAutoScripts(true));
chrome.permissions.onRemoved.addListener(() => syncAutoScripts());
chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "local" || !changes.settings) return;
  const before = (changes.settings.oldValue || {}).fgAutoStart;
  const after = (changes.settings.newValue || {}).fgAutoStart;
  if (!!before !== !!after) syncAutoScripts(!!after);
});

// Messages from the engine running in the offscreen document.
async function onEngine(msg) {
  const { runState } = await chrome.storage.local.get("runState");
  const tabId = runState && runState.tabId;
  if (!tabId) return;
  await ST.i18n.init();

  if (msg.evt === "state") {
    await Engine.setRun({ state: msg.state, error: msg.error || null, detail: msg.detail || null });
    const text = Engine.overlayStatus(msg);
    if (text !== undefined) await toTab(tabId, { op: "status", text, bad: ["error", "stalled", "noresponse"].includes(msg.state) });
  } else if (msg.evt === "segments") {
    await toTab(tabId, { op: "segments", segments: msg.segments });
  } else if (msg.evt === "language") {
    await Engine.setRun({ detectedLang: msg.lang });
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg) return;
  if (msg.cmd === "pageFullscreen") {
    if (sender.tab) ST.windowFullscreen(sender.tab.windowId, !!msg.on);
    sendResponse({});
    return;
  }
  if (msg.from === "engine") {
    onEngine(msg);
    return;
  }
  if (msg.cmd === "autoStart") {
    if (!sender.tab) return;
    autoStart(sender.tab.id).then((result) => sendResponse({ result }));
    return true;
  }
  switch (msg.cmd) {
    case "start":
      start(msg.tabId, msg.streamId);
      break;
    case "fgAutoStart":
      // Saved here: the permission prompt can close the popup that sent it.
      ST.setSettings({ fgAutoStart: !!msg.on });
      break;
    case "stop":
      stop({ byUser: true });
      break;
    case "verify":
      (async () => {
        const { runState } = await chrome.storage.local.get("runState");
        if (runState && Engine.ACTIVE.includes(runState.state) && !(await hasOffscreen())) {
          await Engine.setRun({ state: "idle", tabId: null });
        }
      })();
      break;
    case "style":
      chrome.storage.local.get("runState").then(({ runState }) => {
        if (runState && runState.tabId) {
          toTab(runState.tabId, { op: "style", lines: msg.captionLines, fontSize: msg.fontSize });
        }
      });
      break;
  }
  sendResponse({});
});

chrome.tabs.onRemoved.addListener(async (tabId) => {
  const { runState } = await chrome.storage.local.get("runState");
  if (runState && runState.tabId === tabId) stop();
});

// A reload or a navigation wipes the overlay. Put it back if we still may; otherwise stop.
chrome.tabs.onUpdated.addListener(async (tabId, info) => {
  if (info.status !== "complete") return;
  const { runState } = await chrome.storage.local.get("runState");
  if (!runState || runState.tabId !== tabId || !Engine.ACTIVE.includes(runState.state)) return;
  const settings = await ST.getSettings();
  try {
    await injectOverlay(tabId);
    await toTab(tabId, {
      op: "show", lines: settings.captionLines, fontSize: settings.fontSize, saveSrt: settings.saveSrt,
    });
  } catch (e) {
    stop();
  }
});

chrome.tabs.onUpdated.addListener((tabId, info) => {
  if (info.status === "complete") armAutoStart(tabId);
});

// Nothing survives a browser restart: no stale "REC" badge.
chrome.runtime.onStartup.addListener(() => {
  Engine.setRun({ state: "idle", tabId: null });
  ST.installBuiltinModels();
  syncAutoScripts();
});
chrome.runtime.onInstalled.addListener(() => {
  Engine.setRun({ state: "idle", tabId: null });
  ST.installBuiltinModels();
  syncAutoScripts();
});
