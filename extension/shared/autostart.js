// Turns smooth video and the subtitles on by themselves when the page plays a video, for the
// options the user ticked. Once per video and address; when the user turns a feature off by hand,
// it stays off on this page until the page is reloaded or goes to another address. Only the tab in
// view starts anything.
//
// Smooth video starts right here: framegen-page.js runs in this same content script. The subtitles
// go through the background, which owns the capture and decides: one tab at a time, and in Chromium
// only on tabs where the browser lets the extension capture.
"use strict";

(function () {
  if (globalThis.STAutoStart) return;

  // Players that swap or resize their <video> do not always fire an event this can hear.
  const CHECK_MS = 1000;

  const tracker = ST.autoStartTracker(ST.autoStartPageKey(location.href));
  let settings = null;
  let timer = null;

  const alive = () => !!(ext.runtime && ext.runtime.id);
  const wanted = () => !!settings && (settings.fgAutoStart || settings.subsAutoStart);

  // The largest video that is playing and big enough to be the one being watched.
  function playingVideo() {
    let best = null;
    let bestArea = 0;
    for (const video of document.querySelectorAll("video")) {
      const box = video.getBoundingClientRect();
      const probe = {
        paused: video.paused, ended: video.ended, readyState: video.readyState,
        videoWidth: video.videoWidth, width: box.width, height: box.height,
      };
      if (!ST.isAutoStartVideo(probe)) continue;
      const area = box.width * box.height;
      if (area > bestArea) { best = video; bestArea = area; }
    }
    return best;
  }

  function startFg(video) {
    const page = globalThis.STFramegenPage;
    // Already on (by hand, or on an earlier video that is still there): nothing to do yet.
    if (!page || page.status().running) return;
    if (!tracker.take("fg", video)) return;
    const target = settings.fgTarget === "display" ? 0 : Number(settings.fgTarget) || 0;
    Promise.resolve(page.start(target)).catch((error) => {
      console.warn("[streamremaster] smooth video did not start by itself:", error);
    });
  }

  function startSubs(video) {
    if (!tracker.take("subs", video)) return;
    Promise.resolve(ext.runtime.sendMessage({ cmd: "autoStart" })).catch(() => {});
  }

  function check() {
    if (!alive()) { quit(); return; }
    tracker.visit(ST.autoStartPageKey(location.href));
    if (!wanted() || document.visibilityState !== "visible") return;
    const video = playingVideo();
    if (!video) return;
    if (settings.fgAutoStart) startFg(video);
    if (settings.subsAutoStart) startSubs(video);
  }

  // Only polls while an option is ticked.
  function sync() {
    if (wanted() && !timer) timer = setInterval(check, CHECK_MS);
    else if (!wanted() && timer) { clearInterval(timer); timer = null; }
  }

  async function reload() {
    try {
      settings = await ST.getSettings();
    } catch (e) {
      return; // the extension was reloaded or removed
    }
    sync();
    check();
  }

  const onEvent = () => check();
  const onStorage = (changes, area) => { if (area === "local" && changes.settings) reload(); };
  const onMessage = (msg, _sender, sendResponse) => {
    if (!msg) return undefined;
    if (msg.st === "framegen" && msg.cmd === "stop") {
      tracker.hold("fg"); // only the popup sends it: the user turned smooth video off
    } else if (msg.st === "auto") {
      if (msg.cmd === "hold") tracker.hold(msg.feature);
      else if (msg.cmd === "check") {
        // The popup opened here, or an option was just ticked: settings may be newer.
        reload();
        sendResponse({ alive: true });
      }
    }
    return undefined;
  };

  // The extension went away: this copy can no longer start anything.
  function quit() {
    if (timer) clearInterval(timer);
    timer = null;
    document.removeEventListener("playing", onEvent, true);
    document.removeEventListener("visibilitychange", onEvent);
    try { ext.storage.onChanged.removeListener(onStorage); } catch (e) { /* gone */ }
    try { ext.runtime.onMessage.removeListener(onMessage); } catch (e) { /* gone */ }
  }

  // Media events do not bubble, but the capture phase sees them.
  document.addEventListener("playing", onEvent, true);
  document.addEventListener("visibilitychange", onEvent);
  ext.storage.onChanged.addListener(onStorage);
  ext.runtime.onMessage.addListener(onMessage);

  globalThis.STAutoStart = { check, tracker, playingVideo, settings: () => settings };
  reload();
})();
