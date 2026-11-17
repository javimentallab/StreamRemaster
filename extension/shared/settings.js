"use strict";

const $ = (id) => document.getElementById(id);
const t = (...a) => ST.t(...a);

let settings;
let info = null;            // last list_models answer
let pollTimer = null;
const knownJobState = {};   // id -> last seen state, to notice when a job finishes

document.addEventListener("DOMContentLoaded", init);

async function init() {
  await ST.i18n.init();
  ST.i18n.apply();
  document.title = t("settings_title");
  settings = await ST.getSettings();
  $("version").textContent = "StreamRemaster " + ext.runtime.getManifest().version;

  initServer();
  initModels();
  initFgModels();
  initSubtitles();
  initPerformance();
  initInterface();
  initUpdates();
  initToc();
  // Chromium only lets the extension start things in the tabs where the user clicked its button.
  for (const hint of document.querySelectorAll(".auto-hint")) hint.hidden = ST.isFirefox();

  if (settings.serverUrl) refreshModels();
  else showModelsMsg(t("error_no_server"), "warn");

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && settings.serverUrl) refreshModels();
  });
}

function setMsg(el, text, kind) {
  el.textContent = text || "";
  el.className = "msg" + (kind ? " " + kind : "");
}

function errText(code, detail) {
  const key = "err_" + code;
  const s = t(key);
  return s === key ? t("err_unknown", detail || code) : s;
}

// -------------------------------------------------------------------------------- server

function initServer() {
  $("serverUrl").value = settings.serverUrl ? ST.prettyServer(settings.serverUrl) : "";
  const go = async () => {
    const url = ST.normalizeServerUrl($("serverUrl").value);
    if (!url) return setMsg($("serverMsg"), t("server_bad_url"), "bad");
    setMsg($("serverMsg"), t("server_checking"));
    $("serverSave").disabled = true;
    const res = await ST.serverRequest(url, { st_action: "list_models" }, 20000);
    $("serverSave").disabled = false;
    if (!res.ok && res.error !== "unsupported") {
      return setMsg($("serverMsg"), t(res.error === "timeout" ? "server_timeout" : "server_unreachable"), "bad");
    }
    settings = await ST.setSettings({ serverUrl: url });
    $("serverUrl").value = ST.prettyServer(url);
    setMsg($("serverMsg"), res.ok ? ST.connectedText(res.models.length) : t("server_plain"), res.ok ? "ok" : "warn");
    applyModels(res);
  };
  $("serverSave").addEventListener("click", go);
  $("serverUrl").addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
}

// ------------------------------------------------------------------------------- updates
// On demand only. The extension never updates itself: "Update" opens the page to get it.

function initUpdates() {
  let page = "";
  $("updGo").addEventListener("click", () => { if (page) ext.tabs.create({ url: page }); });
  $("updCheck").addEventListener("click", async () => {
    $("updCheck").disabled = true;
    $("updGo").hidden = true;
    $("updHow").hidden = true;
    $("srvUpd").hidden = true;
    setMsg($("updMsg"), t("server_checking"));
    const res = await ST.checkForUpdate();
    $("updCheck").disabled = false;
    if (!res.ok) {
      setMsg($("updMsg"), t(res.error === "rate_limited" ? "update_rate_limited" : "update_failed"), "bad");
      return;
    }
    if (res.newer) {
      page = res.page;
      setMsg($("updMsg"), t("update_available", res.latest, res.current), "warn");
      $("updGo").hidden = false;
      $("updHow").textContent = t(ST.isFirefox() ? "update_how_firefox" : "update_how_chromium");
      $("updHow").hidden = false;
    } else {
      setMsg($("updMsg"), t("update_latest", res.current), "ok");
    }
    renderServerUpdate(res.latest);
  });
}

// Only for the Stream Transcription server (a plain WhisperLive one has its own updates).
function renderServerUpdate(latest) {
  if (!info || !info.st) return;
  const state = ST.serverUpdateState(info.version, latest);
  $("srvUpdText").textContent = state === "current" ? t("server_update_latest", info.version)
    : state === "newer" ? t("server_update_available", info.version, latest)
    : t("server_version_unknown");
  $("srvUpdCmd").textContent = ST.SERVER_UPDATE_COMMANDS;
  $("srvUpdCmd").hidden = state === "current";
  $("srvUpd").querySelector(".hint").hidden = state === "current";
  $("srvUpd").hidden = false;
}

// -------------------------------------------------------------------------------- models

function initModels() {
  ST.STOCK_MODELS.forEach((m) => $("stockModels").append(new Option(m)));
  $("plainModel").value = settings.model;
  $("plainSave").addEventListener("click", async () => {
    settings = await ST.setSettings({ model: $("plainModel").value.trim() });
    showModelsMsg(t("saved"), "ok");
  });

  $("addBtn").addEventListener("click", () => startDownload($("addSource").value));
  $("addSource").addEventListener("keydown", (e) => { if (e.key === "Enter") startDownload($("addSource").value); });
}

function showModelsMsg(text, kind) {
  setMsg($("modelsMsg"), text, kind);
}

async function refreshModels() {
  const res = await ST.serverRequest(settings.serverUrl, { st_action: "list_models" }, 20000);
  applyModels(res);
}

function applyModels(res) {
  info = res;
  const managed = res.ok;
  $("modelsManaged").hidden = !managed;
  $("modelsPlain").hidden = managed || !(res.error === "unsupported");
  if (!res.ok && res.error !== "unsupported") {
    showModelsMsg(t(res.error === "timeout" ? "server_timeout" : "server_unreachable"), "bad");
    schedulePoll(false);
    return;
  }
  showModelsMsg("");
  if (!managed) return;

  $("addBlock").hidden = !res.management;
  renderModelList(res);
  renderSuggestions(res);
  renderJobs(res.jobs || []);
}

function renderModelList(res) {
  const list = $("modelList");
  list.textContent = "";
  $("noModels").hidden = res.models.length > 0;
  const selected = res.models.some((m) => m.id === settings.model) ? settings.model : res.default;

  res.models.forEach((m) => {
    const { name, org } = ST.splitModelId(m.id);
    const li = document.createElement("li");
    li.className = "model" + (m.id === selected ? " selected" : "");

    const infoEl = document.createElement("div");
    infoEl.className = "info";
    const nameEl = document.createElement("div");
    nameEl.className = "name";
    nameEl.textContent = name;
    nameEl.title = m.id;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.append(document.createTextNode([org, ST.formatBytes(m.size)].filter(Boolean).join(" · ")));
    if (m.id === selected) meta.append(badge(t("badge_selected"), "accent"));
    if (m.default) meta.append(badge(t("badge_default")));
    if (m.loaded) meta.append(badge(t("badge_loaded"), "ok"));
    infoEl.append(nameEl, meta);

    const actions = document.createElement("div");
    actions.className = "actions";
    if (m.id !== selected) {
      const use = button(t("use_model"), "btn ghost sm", async () => {
        settings = await ST.setSettings({ model: m.id, engine: "server" });
        renderModelList(info);
      });
      actions.append(use);
    }
    if (res.management && !m.default) {
      const del = button(t("delete_model"), "btn danger sm", () => deleteModel(m, name));
      actions.append(del);
    }
    li.append(infoEl, actions);
    list.append(li);
  });
}

function badge(text, kind) {
  const b = document.createElement("span");
  b.className = "badge" + (kind ? " " + kind : "");
  b.textContent = text;
  return b;
}

function button(text, cls, onClick) {
  const b = document.createElement("button");
  b.className = cls;
  b.textContent = text;
  b.addEventListener("click", onClick);
  return b;
}

async function deleteModel(m, name) {
  if (!confirm(t("confirm_delete", name, ST.formatBytes(m.size)))) return;
  const res = await ST.serverRequest(settings.serverUrl, { st_action: "delete_model", id: m.id }, 20000);
  if (!res.ok) {
    showModelsMsg(errText(res.error, res.detail), "bad");
    return;
  }
  if (settings.model === m.id) settings = await ST.setSettings({ model: "" });
  refreshModels();
}

function renderSuggestions(res) {
  const box = $("suggestions");
  box.textContent = "";
  const installed = new Set(res.models.map((m) => m.id));
  ST.SUGGESTED_MODELS.filter((id) => !installed.has(id)).forEach((id) => {
    const chip = button(ST.splitModelId(id).name, "chip", () => {
      $("addSource").value = id;
      $("addSource").focus();
    });
    chip.title = id;
    box.append(chip);
  });
}

async function startDownload(source) {
  source = String(source || "").trim();
  if (!source) return;
  setMsg($("addMsg"), t("server_checking"));
  $("addBtn").disabled = true;
  const res = await ST.serverRequest(settings.serverUrl, { st_action: "download_model", source }, 20000);
  $("addBtn").disabled = false;
  if (!res.ok) {
    setMsg($("addMsg"), errText(res.error, res.detail), "bad");
    return;
  }
  setMsg($("addMsg"), "");
  $("addSource").value = "";
  refreshModels();
}

function renderJobs(jobs) {
  const list = $("jobList");
  list.textContent = "";
  let running = false;
  let finished = false;

  jobs.forEach((j) => {
    const active = !["ready", "error"].includes(j.state);
    running = running || active;
    if (knownJobState[j.id] && knownJobState[j.id] !== j.state && j.state === "ready") finished = true;
    knownJobState[j.id] = j.state;

    const li = document.createElement("li");
    li.className = "job " + j.state;
    const top = document.createElement("div");
    top.className = "top-line";
    const name = document.createElement("span");
    name.className = "name";
    name.textContent = j.id.startsWith("url:") ? j.source : j.id;
    const status = document.createElement("span");
    status.className = "hint";
    status.textContent = jobText(j);
    top.append(name, status);
    li.append(top);

    if (active) {
      const track = document.createElement("div");
      track.className = "bar-track";
      const fill = document.createElement("div");
      fill.className = "bar-fill";
      if (j.state === "downloading" && j.total) {
        fill.style.width = Math.min(100, (100 * j.downloaded) / j.total).toFixed(1) + "%";
      } else {
        fill.classList.add("indeterminate");
      }
      track.append(fill);
      li.append(track);
    }
    if (j.state === "error") {
      const row = document.createElement("div");
      row.className = "row";
      row.append(button(t("retry"), "btn ghost sm", () => startDownload(j.source)));
      li.append(row);
    }
    list.append(li);
  });

  $("keepOpen").hidden = !running;
  if (finished) {
    // a model just finished: the list has changed
    setTimeout(refreshModels, 300);
  }
  schedulePoll(running);
}

function jobText(j) {
  switch (j.state) {
    case "downloading":
      return j.total
        ? t("job_downloading", ST.formatBytes(j.downloaded), ST.formatBytes(j.total))
        : t("job_downloading_nosize", ST.formatBytes(j.downloaded));
    case "converting": return t("job_converting");
    case "extracting": return t("job_extracting");
    case "ready": return t("job_ready");
    case "error": return t("job_error", errText(j.error, j.detail));
    default: return j.state;
  }
}

// While something downloads, ask every 2 s. Besides showing progress, this keeps
// servers that start on demand awake until the download ends.
function schedulePoll(active) {
  clearTimeout(pollTimer);
  if (active) pollTimer = setTimeout(refreshModels, 2000);
}

// ------------------------------------------------------------------- smooth video models
// StreamRemaster comes with the extension. Other models are downloaded from an address or chosen
// from a file; they stay in the browser's own storage. All of them run on this computer's card.

function initFgModels() {
  $("fgAutoStart").checked = !!settings.fgAutoStart;
  // Ticking it asks Chromium for every site, straight from the click. Said no: it stays ticked and
  // works where the user clicked the extension's button, as the note says.
  $("fgAutoStart").addEventListener("change", async (e) => {
    const asked = e.target.checked ? ST.askAllSites() : null;
    settings = await ST.setSettings({ fgAutoStart: e.target.checked });
    if (asked) asked.then(renderFgAutoHint);
  });
  $("fgAllowAll").addEventListener("click", (e) => {
    e.preventDefault();
    ST.askAllSites().then(renderFgAutoHint);
  });
  renderFgAutoHint();
  $("fgModelAdd").addEventListener("click", () => $("fgModelFile").click());
  $("fgModelFile").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    e.target.value = "";
    if (file) await addFgModel(await file.arrayBuffer().catch(() => null), file.name);
  });
  $("fgModelDownload").addEventListener("click", downloadFgModel);
  $("fgModelUrl").addEventListener("keydown", (e) => { if (e.key === "Enter") downloadFgModel(); });
  $("fgSourceSeg").addEventListener("click", async (e) => {
    const b = e.target.closest("button");
    if (!b || b.dataset.v === settings.fgSource) return;
    settings = await ST.setSettings({ fgSource: b.dataset.v });
    renderFgModels();
  });
  $("fgServerDownload").addEventListener("click", downloadServerFgModel);
  $("fgServerSource").addEventListener("keydown", (e) => { if (e.key === "Enter") downloadServerFgModel(); });
  renderFgModels();
  renderServerFgModels();
}

// ------------------------------------------------- smooth video models kept on the server
// The server only keeps the files; the chosen one comes down and runs on this computer's card.

let serverFgInfo = null;

function fgServerErrorText(res) {
  switch (res.error) {
    case "unknown_action": case "unsupported": return t("fg_server_old");
    case "not_video_model": case "too_big": return t("fg_model_bad");
    case "invalid_source": return t("server_bad_url");
    case "timeout": return t("server_timeout");
    case "unreachable": return t("server_unreachable");
    default: return errText(res.error, res.detail);
  }
}

async function renderServerFgModels() {
  const list = $("fgServerList");
  list.textContent = "";
  $("fgServerAdd").hidden = true;
  if (!settings.serverUrl) {
    setMsg($("fgServerMsg"), t("error_no_server"), "warn");
    return;
  }
  setMsg($("fgServerMsg"), t("server_checking"));
  const res = await ST.serverRequest(settings.serverUrl, { st_action: "list_video_models" }, 20000);
  serverFgInfo = res;
  if (!res.ok) {
    setMsg($("fgServerMsg"), fgServerErrorText(res), "warn");
    return;
  }
  setMsg($("fgServerMsg"), res.models.length ? "" : t("fg_server_none"));
  $("fgServerAdd").hidden = !res.management;
  for (const model of res.models) {
    const id = ST.SERVER_FG_PREFIX + model.id;
    const selected = settings.fgSource === "server" && settings.fgModel === id;
    const item = document.createElement("li");
    item.className = "model" + (selected ? " selected" : "");
    const details = document.createElement("div");
    details.className = "info";
    const name = document.createElement("div");
    name.className = "name";
    name.textContent = model.name;
    name.title = model.id;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.append(document.createTextNode(t("fg_file_size", ST.formatBytes(model.size))));
    if (FG_PARTIAL[model.kind]) meta.append(badge(t(FG_PARTIAL[model.kind]), ""));
    if (selected) meta.append(badge(t("badge_selected"), "accent"));
    details.append(name, meta);
    const actions = document.createElement("div");
    actions.className = "actions";
    if (!selected) {
      actions.append(button(t("use_model"), "btn ghost sm", async (e) => {
        e.target.disabled = true;
        setMsg($("fgServerMsg"), t("fg_server_loading"));
        const taken = await ST.takeServerFgModel(settings.serverUrl, model.id);
        if (!taken.ok) {
          e.target.disabled = false;
          setMsg($("fgServerMsg"), fgServerErrorText(taken), "bad");
          return;
        }
        settings = await ST.setSettings({ fgSource: "server", fgModel: taken.id });
        setMsg($("fgServerMsg"), "");
        renderFgModels();
      }));
    }
    if (res.management) {
      actions.append(button(t("delete_model"), "btn danger sm", async () => {
        if (!confirm(t("confirm_delete", model.name, ST.formatBytes(model.size)))) return;
        const done = await ST.serverRequest(settings.serverUrl, { st_action: "delete_video_model", id: model.id }, 20000);
        if (!done.ok) {
          setMsg($("fgServerMsg"), fgServerErrorText(done), "bad");
          return;
        }
        if (settings.fgModel === id) settings = await ST.setSettings({ fgModel: "" });
        renderServerFgModels();
      }));
    }
    item.append(details, actions);
    list.append(item);
  }
}

async function downloadServerFgModel() {
  const source = $("fgServerSource").value.trim();
  if (!source) return;
  $("fgServerDownload").disabled = true;
  setMsg($("fgServerAddMsg"), t("server_checking"));
  const res = await ST.serverRequest(settings.serverUrl, { st_action: "download_video_model", source }, 60000);
  $("fgServerDownload").disabled = false;
  if (!res.ok) {
    setMsg($("fgServerAddMsg"), fgServerErrorText(res), "bad");
    return;
  }
  setMsg($("fgServerAddMsg"), "");
  $("fgServerSource").value = "";
  renderServerFgModels();
}

async function renderFgAutoHint() {
  $("fgAutoHint").hidden = await ST.hasAllSites();
}

async function storedFgModels() {
  const { fgModels } = await ext.storage.local.get("fgModels");
  return fgModels || {};
}

// A model file can carry the upscaler, the in-between frames network or both; only a partial one says so.
const FG_PARTIAL = { sr: "fg_kind_sr", fi: "fg_kind_fi" };

async function downloadFgModel() {
  const raw = $("fgModelUrl").value.trim();
  if (!raw) return;
  let url;
  try {
    url = new URL(raw);
    if (url.protocol !== "https:" && url.protocol !== "http:") throw new Error("scheme");
  } catch (e) {
    setMsg($("fgModelMsg"), t("fg_download_failed", t("server_bad_url")), "bad");
    return;
  }
  $("fgModelDownload").disabled = true;
  setMsg($("fgModelMsg"), t("server_checking"));
  try {
    const response = await fetch(url.href, { credentials: "omit" });
    if (!response.ok) throw new Error("HTTP " + response.status);
    const length = Number(response.headers.get("content-length")) || 0;
    if (length > STFramegenModel.MAX_MODEL_BYTES) throw new Error("too big");
    const buffer = await response.arrayBuffer();
    if (await addFgModel(buffer, url.pathname.split("/").pop())) $("fgModelUrl").value = "";
  } catch (e) {
    setMsg($("fgModelMsg"), t("fg_download_failed", (e && e.message) || String(e)), "bad");
  } finally {
    $("fgModelDownload").disabled = false;
  }
}

// true when the model was added (and chosen).
async function addFgModel(buffer, fileName) {
  let model;
  try {
    if (!buffer || buffer.byteLength > STFramegenModel.MAX_MODEL_BYTES) throw new Error("size");
    model = STFramegenModel.parse(buffer);
  } catch (error) {
    setMsg($("fgModelMsg"), t("fg_model_bad"), "bad");
    return false;
  }
  const kind = model.kind;
  const id = `${kind}-${model.name}-${buffer.byteLength}`.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  const models = await storedFgModels();
  const data = ST.bufferToBase64(buffer);
  // the same file as one that comes with the extension: that one is chosen, nothing is added
  const same = Object.values(models).find((entry) => entry.builtin && entry.data === data);
  if (same) {
    settings = await ST.setSettings({ fgModel: same.id, fgSource: "local" });
    setMsg($("fgModelMsg"), "");
    renderFgModels();
    return true;
  }
  models[id] = { id, kind, name: model.name, size: buffer.byteLength, file: fileName || "", data };
  await ext.storage.local.set({ fgModels: models });
  settings = await ST.setSettings({ fgModel: id, fgSource: "local" });
  setMsg($("fgModelMsg"), "");
  renderFgModels();
  return true;
}

// The graphics memory line: a 1080p video shown as it is and, with an upscaler, taken to 4K.
function fgMemoryText(entry) {
  let model;
  try {
    model = STFramegenModel.parse(ST.base64ToBuffer(entry.data));
  } catch (e) {
    return "";
  }
  const at = (resolution) => STFramegen.memoryBytes(STFramegen.planSizes(1920, 1080,
    { resolution, model: model.sr, interpolator: model.fi }, 2160));
  const parts = [t("fg_memory", ST.formatBytes(at("original")))];
  if (model.sr) parts.push(t("fg_memory_4k", ST.formatBytes(at("2160"))));
  return parts.join(" · ");
}

function fgModelItem(model) {
  const item = document.createElement("li");
  const selected = model.id === settings.fgModel && settings.fgSource !== "server";
  item.className = "model" + (selected ? " selected" : "");
  const details = document.createElement("div");
  details.className = "info";
  const name = document.createElement("div");
  name.className = "name";
  name.textContent = model.name;
  if (model.file) name.title = model.file;
  const meta = document.createElement("div");
  meta.className = "meta";
  meta.append(document.createTextNode(t("fg_file_size", ST.formatBytes(model.size))));
  if (FG_PARTIAL[model.kind || "sr"]) meta.append(badge(t(FG_PARTIAL[model.kind || "sr"]), ""));
  if (model.hq) meta.append(badge(t("fg_hq_badge"), ""));
  if (selected) meta.append(badge(t("badge_selected"), "accent"));
  const memory = document.createElement("div");
  memory.className = "meta memory";
  memory.textContent = fgMemoryText(model);
  details.append(name, meta, memory);
  const actions = document.createElement("div");
  actions.className = "actions";
  if (!selected) {
    actions.append(button(t("use_model"), "btn ghost sm", async () => {
      settings = await ST.setSettings({ fgModel: model.id, fgSource: "local" });
      renderFgModels();
    }));
  }
  if (!model.builtin) actions.append(button(t("delete_model"), "btn danger sm", () => deleteFgModel(model)));
  item.append(details, actions);
  return item;
}

async function renderFgModels() {
  const server = settings.fgSource === "server";
  $("fgSourceSeg").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === settings.fgSource));
  $("fgLocalInUse").hidden = server;
  $("fgServerInUse").hidden = !server;
  if (serverFgInfo) renderServerFgModels();
  const models = Object.values(await storedFgModels());
  const builtin = models.filter((model) => model.builtin);
  const own = models.filter((model) => !model.builtin && !model.server);
  $("fgBuiltinList").textContent = "";
  builtin.forEach((model) => $("fgBuiltinList").append(fgModelItem(model)));
  $("fgModelList").textContent = "";
  own.forEach((model) => $("fgModelList").append(fgModelItem(model)));
  $("fgNoModels").hidden = own.length > 0;
}

async function deleteFgModel(model) {
  if (model.builtin) return;
  if (!confirm(t("confirm_delete", model.name, ST.formatBytes(model.size)))) return;
  const models = await storedFgModels();
  delete models[model.id];
  await ext.storage.local.set({ fgModels: models });
  // back to the one that comes with the extension
  if (settings.fgModel === model.id) settings = await ST.setSettings({ fgModel: ST.DEFAULTS.fgModel });
  renderFgModels();
}

// ----------------------------------------------------------------------------- subtitles

function initSubtitles() {
  const preview = $("preview").firstElementChild;
  const paint = () => {
    preview.style.fontSize = settings.fontSize + "px";
    preview.style.lineHeight = Math.round(settings.fontSize * 1.38) + "px";
    document.querySelectorAll("#lines button").forEach((b) => {
      b.classList.toggle("on", Number(b.dataset.v) === Number(settings.captionLines));
    });
  };
  $("fontSize").value = settings.fontSize;
  $("saveSrt").checked = settings.saveSrt;
  $("useVad").checked = settings.useVad;
  $("subsAutoStart").checked = !!settings.subsAutoStart;
  paint();

  $("lines").addEventListener("click", async (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    settings = await ST.setSettings({ captionLines: Number(b.dataset.v) });
    paint();
  });
  $("fontSize").addEventListener("input", (e) => { settings.fontSize = Number(e.target.value); paint(); });
  $("fontSize").addEventListener("change", async (e) => { settings = await ST.setSettings({ fontSize: Number(e.target.value) }); });
  $("saveSrt").addEventListener("change", async (e) => { settings = await ST.setSettings({ saveSrt: e.target.checked }); });
  $("useVad").addEventListener("change", async (e) => { settings = await ST.setSettings({ useVad: e.target.checked }); });
  $("subsAutoStart").addEventListener("change", async (e) => { settings = await ST.setSettings({ subsAutoStart: e.target.checked }); });
  $("resetPos").addEventListener("click", async () => {
    await ext.storage.local.remove("overlayPos");
    $("resetMsg").textContent = t("position_reset_done");
  });
}

// --------------------------------------------------------------------------- performance

function initPerformance() {
  $("precision").value = settings.precision;
  $("translatorDevice").value = settings.translatorDevice;
  $("precision").addEventListener("change", async (e) => { settings = await ST.setSettings({ precision: e.target.value }); });
  $("translatorDevice").addEventListener("change", async (e) => { settings = await ST.setSettings({ translatorDevice: e.target.value }); });
}

// ----------------------------------------------------------------------------- interface

function initInterface() {
  $("uiLang").value = settings.uiLang;
  $("uiLang").addEventListener("change", async (e) => {
    settings = await ST.setSettings({ uiLang: e.target.value });
    location.reload();
  });
}

function initToc() {
  const links = Array.from(document.querySelectorAll(".toc a"));
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      links.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + en.target.id));
    });
  }, { rootMargin: "-20% 0px -70% 0px" });
  document.querySelectorAll(".panel").forEach((p) => obs.observe(p));
  if (location.hash) {
    const el = document.querySelector(location.hash);
    if (el) setTimeout(() => el.scrollIntoView(), 50);
  }
}
