// The popup's two tabs and the frame generation one. Loaded after popup.js, whose $, t and
// settings it shares. Frame generation needs no server, so this tab works without one.
"use strict";

const FG_TARGETS = [60, 75, 90, 100, 120, 144, 165, 180, 240];
const FG_FILES = ST.FG_FILES;
const FG_RESOLUTIONS = [["1080", "1080p"], ["1440", "1440p"], ["2160", "4K"]];
const FG_POLL_MS = 500;

let fgStatus = { running: false, state: "off" };
let fgTimer = null;
let fgSettings = null;

document.addEventListener("DOMContentLoaded", initTabs);

async function initTabs() {
  await ST.i18n.init();
  fgSettings = await ST.getSettings();
  fillTargets();
  fillResolutions();
  fillSharpen();
  await fillModels();
  $("fgResolution").addEventListener("change", onFgResolution);
  $("fgSharpen").addEventListener("change", () => fgReconfigure({ fgSharpen: $("fgSharpen").value }));
  $("fgModel").addEventListener("change", onFgModel);
  $("fgSourceSeg").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) onFgSource(b.dataset.v);
  });
  $("fgManageModels").addEventListener("click", (e) => { e.preventDefault(); openSettings("fgmodels"); });
  $("tabs").addEventListener("click", (e) => {
    const button = e.target.closest("[data-tab]");
    if (!button) return;
    selectTab(button.dataset.tab);
    ST.setSettings({ popupTab: button.dataset.tab });
  });
  $("fgToggle").addEventListener("click", onFgToggle);
  $("fgTarget").addEventListener("change", onFgTarget);
  $("fgMeter").checked = fgSettings.fgMeter !== false;
  $("fgMeter").addEventListener("change", () => fgReconfigure({ fgMeter: $("fgMeter").checked }));
  $("fgAutoStart").checked = !!fgSettings.fgAutoStart;
  $("fgAutoStart").addEventListener("change", onFgAutoStart);
  $("fgAllowAll").addEventListener("click", onFgAllowAll);
  // Chromium only lets the extension into the tabs where the user clicked its button, unless it was
  // given every site (smooth video). The subtitles always need the click: tab capture asks for it.
  for (const hint of document.querySelectorAll(".auto-hint")) hint.hidden = ST.isFirefox();
  renderFgAutoHint();
  selectTab(fgSettings.popupTab);
  if (fgSettings.fgAutoStart || fgSettings.subsAutoStart) armAutoStart();
}

function selectTab(name) {
  const fg = name === "fg";
  $("panelSubs").hidden = fg;
  $("panelFg").hidden = !fg;
  for (const button of $("tabs").querySelectorAll("[data-tab]")) {
    const on = button.dataset.tab === name;
    button.classList.toggle("on", on);
    button.setAttribute("aria-selected", String(on));
  }
  clearInterval(fgTimer);
  fgTimer = null;
  if (fg) {
    refreshFg();
    fgTimer = setInterval(refreshFg, FG_POLL_MS);
  }
}

function fillTargets() {
  const select = $("fgTarget");
  select.append(new Option(t("fg_target_display"), "display"));
  FG_TARGETS.forEach((fps) => select.append(new Option(String(fps), String(fps))));
  select.value = String(fgSettings.fgTarget);
  if (!select.value) select.value = "display";
}

const FG_SHARPEN = ["off", "soft", "medium", "strong"];

function fillSharpen() {
  const select = $("fgSharpen");
  FG_SHARPEN.forEach((level) => select.append(new Option(t(`fg_sharpen_${level}`), level)));
  select.value = fgSettings.fgSharpen;
  if (!select.value) select.value = "medium";
}

function fillResolutions() {
  const select = $("fgResolution");
  select.append(new Option(t("fg_res_original"), "original"));
  select.append(new Option(t("fg_target_display"), "display"));
  FG_RESOLUTIONS.forEach(([value, label]) => select.append(new Option(label, value)));
  select.value = String(fgSettings.fgResolution);
  if (!select.value) select.value = "original";
}

// One choice. On this computer: StreamRemaster, which comes with the extension, then the models the
// user downloaded. On the server: the models it keeps (taken from it when chosen). Then none (the
// plain cross-fade). Either way the model runs on this computer's graphics card. A model file can
// carry the upscaler, the in-between frames network or both.
let fgModelEntries = {};
const fgParsed = new Map();   // id -> parsed model, for the graphics memory estimate

function fgHint(text, kind) {
  const hint = $("fgServerHint");
  hint.textContent = text || "";
  hint.className = "hint" + (kind ? " " + kind : "");
  hint.hidden = !text;
}

function fgGroup(select, label, list) {
  if (!list.length) return;
  const element = document.createElement("optgroup");
  element.label = label;
  list.forEach(([text, value]) => element.append(new Option(text, value)));
  select.append(element);
}

async function fillModels() {
  const { fgModels } = await ext.storage.local.get("fgModels");
  fgModelEntries = fgModels || {};
  const models = Object.values(fgModelEntries);
  const select = $("fgModel");
  select.textContent = "";
  fgHint("");
  $("fgSourceSeg").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === fgSettings.fgSource));
  if (fgSettings.fgSource === "server") {
    await fillServerModels(select);
  } else {
    fgGroup(select, t("fg_builtin"), models.filter((model) => model.builtin)
      .map((model) => [model.hq ? `${model.name} · ${t("fg_hq_badge")}` : model.name, model.id]));
    fgGroup(select, t("fg_downloaded_title"), models.filter((model) => !model.builtin && !model.server).map((model) => [model.name, model.id]));
  }
  select.append(new Option(t("fg_model_none"), ""));
  select.value = fgSettings.fgModel;
  if (select.value !== fgSettings.fgModel) select.value = "";
  renderFgMemory();
}

async function fillServerModels(select) {
  if (!fgSettings.serverUrl) return fgHint(t("error_no_server"), "warn");
  fgHint(t("server_checking"));
  const res = await ST.serverRequest(fgSettings.serverUrl, { st_action: "list_video_models" }, 20000);
  if (!res.ok) {
    const old = res.error === "unknown_action" || res.error === "unsupported";
    return fgHint(t(old ? "fg_server_old" : res.error === "timeout" ? "server_timeout" : "server_unreachable"), "warn");
  }
  fgHint(res.models.length ? "" : t("fg_server_none"));
  fgGroup(select, t("engine_server"), res.models.map((model) => [model.name, ST.SERVER_FG_PREFIX + model.id]));
}

// Where the models come from. The choice goes to that place's usual model: the built-in one here,
// the first one the server has there.
async function onFgSource(source) {
  if (source === fgSettings.fgSource) return;
  fgSettings = await ST.setSettings({ fgSource: source });
  await fillModels();
  const select = $("fgModel");
  if (select.value === "" || select.value !== fgSettings.fgModel) {
    const first = Array.from(select.options).find((o) => o.value && !o.disabled);
    select.value = source === "local" ? ST.DEFAULTS.fgModel : first ? first.value : "";
    await onFgModel();
  }
}

function parsedFgModel(id) {
  if (!id || !fgModelEntries[id]) return null;
  if (!fgParsed.has(id)) {
    let parsed = null;
    try {
      parsed = STFramegenModel.parse(ST.base64ToBuffer(fgModelEntries[id].data));
    } catch (e) { /* unreadable: no estimate */ }
    fgParsed.set(id, parsed);
  }
  return fgParsed.get(id);
}

// While it runs, what this video takes; otherwise what a 1080p video would take with these choices.
function renderFgMemory() {
  const el = $("fgMemory");
  if (fgStatus.running && fgStatus.memory) {
    el.textContent = t("fg_memory_now", ST.formatBytes(fgStatus.memory));
    return;
  }
  const model = parsedFgModel($("fgModel").value);
  const options = { resolution: $("fgResolution").value, model: model && model.sr, interpolator: model && model.fi };
  const plan = STFramegen.planSizes(1920, 1080, options, Math.round(screen.height * devicePixelRatio));
  el.textContent = t("fg_memory", ST.formatBytes(STFramegen.memoryBytes(plan)));
}

async function fgReconfigure(patch) {
  await ST.setSettings(patch);
  if (fgStatus.running) {
    const status = await fgAsk({ cmd: "reconfigure" });
    if (status) renderFg(status);
  }
}

function onFgResolution() {
  renderFgMemory();
  fgReconfigure({ fgResolution: $("fgResolution").value });
}

async function onFgModel() {
  const select = $("fgModel");
  const value = select.value;
  if (value.startsWith(ST.SERVER_FG_PREFIX) && fgSettings.serverUrl) {
    select.disabled = true;
    fgHint(t("fg_server_loading"));
    const res = await ST.takeServerFgModel(fgSettings.serverUrl, value.slice(ST.SERVER_FG_PREFIX.length));
    select.disabled = false;
    if (!res.ok) {
      fgHint(t(res.error === "timeout" ? "server_timeout" : "server_unreachable"), "warn");
      return;
    }
    fgHint("");
    fgParsed.delete(value);
    fgModelEntries = (await ext.storage.local.get("fgModels")).fgModels || {};
  }
  fgSettings = await ST.setSettings({ fgModel: value });
  renderFgMemory();
  fgReconfigure({ fgModel: value });
}

function fgTargetValue() {
  return $("fgTarget").value === "display" ? 0 : Number($("fgTarget").value);
}

async function fgTabId() {
  const [tab] = await ext.tabs.query({ active: true, currentWindow: true });
  return tab ? tab.id : null;
}

// null when the tab has no content script (or the page does not allow one).
async function fgAsk(message) {
  const id = await fgTabId();
  if (id === null) return null;
  try {
    return await ext.tabs.sendMessage(id, Object.assign({ st: "framegen" }, message));
  } catch (e) {
    return null;
  }
}

// Chromium runs the page side on demand, under activeTab, so it needs no access to every site.
// In Firefox this covers the tabs opened before the add-on was installed.
async function fgInject(files = FG_FILES) {
  const id = await fgTabId();
  if (id === null) return false;
  try {
    if (ext.scripting) {
      await ext.scripting.executeScript({ target: { tabId: id }, files });
    } else {
      for (const file of files) await ext.tabs.executeScript(id, { file });
    }
    return true;
  } catch (e) {
    return false;
  }
}

// The watcher that starts the two features by themselves (autostart.js). Firefox already runs it on
// every page; Chromium may only run it on a tab once the user opened this popup there, and from then
// on the background puts it back after each load, until the tab goes to another site. Used by both
// tabs of the popup.
async function armAutoStart() {
  const id = await fgTabId();
  if (id === null) return;
  let answer = null;
  try {
    answer = await ext.tabs.sendMessage(id, { st: "auto", cmd: "check" });
  } catch (e) {
    answer = null;
  }
  if (!answer) await fgInject(ST.AUTO_FILES);
}

async function renderFgAutoHint() {
  $("fgAutoHint").hidden = await ST.hasAllSites();
}

// Ticking it asks Chromium for every site, straight from the click (the browser only asks during a
// user gesture). Said no: the box stays ticked and works where the user clicked the button, as the
// note under it says, with a link to ask again. The choice goes through the background, because the
// permission prompt can close this popup before an await here comes back.
async function onFgAutoStart() {
  const on = $("fgAutoStart").checked;
  const asked = on ? ST.askAllSites() : null;
  if (on && !ST.isFirefox()) {
    ext.runtime.sendMessage({ cmd: "fgAutoStart", on: true }).catch(() => {});
  } else {
    fgSettings = await ST.setSettings({ fgAutoStart: on });
  }
  if (!asked) return;
  await asked;
  renderFgAutoHint();
  armAutoStart();
}

function onFgAllowAll(e) {
  e.preventDefault();
  ST.askAllSites().then(renderFgAutoHint);
}

async function refreshFg() {
  const status = await fgAsk({ cmd: "status" });
  renderFg(status || { running: false, state: "off" });
}

async function onFgToggle() {
  const button = $("fgToggle");
  button.disabled = true;
  try {
    if (fgStatus.running) {
      renderFg((await fgAsk({ cmd: "stop" })) || { running: false, state: "off" });
      return;
    }
    const start = { cmd: "start", target: fgTargetValue() };
    let status = await fgAsk(start);
    if (!status && (await fgInject())) status = await fgAsk(start);
    renderFg(status || { running: false, state: "off", error: "unavailable" });
  } finally {
    button.disabled = false;
  }
}

function onFgTarget() {
  ST.setSettings({ fgTarget: $("fgTarget").value });
  if (fgStatus.running) fgAsk({ cmd: "target", target: fgTargetValue() }).then((s) => { if (s) renderFg(s); });
}

function fgErrorText(code) {
  switch (code) {
    case "no_video": return t("fg_no_video");
    case "no_webgpu": return t("fg_no_webgpu");
    case "cannot_read": return t("fg_cannot_read");
    default: return t("fg_unavailable");
  }
}

function renderFg(status) {
  fgStatus = status;
  const running = !!status.running;
  $("fgToggle").classList.toggle("running", running);
  $("fgToggleLabel").textContent = t(running ? "fg_stop" : "fg_start");
  const message = $("fgMsg");
  if (status.error) {
    setMsg(message, fgErrorText(status.error), "bad");
  } else if (status.state === "on") {
    setMsg(message, t("fg_state_on", status.fps, Math.round(status.sourceHz)), "ok");
  } else if (status.state === "measuring") {
    setMsg(message, t("fg_state_measuring"), "");
  } else {
    setMsg(message, t("fg_state_off"), "");
  }
  renderFgMemory();
}
