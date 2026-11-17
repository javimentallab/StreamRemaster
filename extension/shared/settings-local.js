// Settings → Transcription models: where the speech becomes text (on the server or on this
// computer), and the Whisper models that run in the browser (whisper-store.js): download, choose
// and delete them. Also names the graphics card for both model sections.
"use strict";

(function () {
  const $ = (id) => document.getElementById(id);
  const t = (...a) => ST.t(...a);
  const jobs = {};   // id -> { got, total, abort }
  let current = null;

  document.addEventListener("DOMContentLoaded", async () => {
    await ST.i18n.init();
    current = await ST.getSettings();
    $("engineSeg").addEventListener("click", async (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      current = await ST.setSettings({ engine: b.dataset.v });
      render();
    });
    ext.storage.onChanged.addListener((changes, area) => {
      if (area === "local" && changes.settings) {
        current = Object.assign({}, ST.DEFAULTS, changes.settings.newValue || {});
        render();
      }
    });
    showGpu();
    render();
  });

  async function showGpu() {
    const show = (text, kind) => {
      for (const id of ["localGpu", "fgGpu"]) {
        $(id).textContent = text;
        $(id).className = "msg " + kind;
      }
    };
    try {
      const adapter = navigator.gpu && (await navigator.gpu.requestAdapter({ powerPreference: "high-performance" }));
      if (!adapter) throw new Error("none");
      let info = adapter.info;
      if (!info && adapter.requestAdapterInfo) info = await adapter.requestAdapterInfo();
      const name = info && (info.description || [info.vendor, info.architecture].filter(Boolean).join(" "));
      show(t("local_gpu", name || "WebGPU"), "ok");
    } catch (e) {
      show(t("error_no_webgpu"), "bad");
    }
  }

  function button(text, cls, onClick) {
    const b = document.createElement("button");
    b.className = cls;
    b.textContent = text;
    b.addEventListener("click", onClick);
    return b;
  }

  function badge(text, kind) {
    const b = document.createElement("span");
    b.className = "badge" + (kind ? " " + kind : "");
    b.textContent = text;
    return b;
  }

  async function render() {
    const local = current.engine === "local";
    $("engineSeg").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === current.engine));
    $("serverInUse").hidden = local;
    $("localInUse").hidden = !local;
    let stored = [];
    try { stored = await Whisper.store.list(); } catch (e) { /* none */ }
    const have = new Map(stored.filter((m) => m.complete).map((m) => [m.id, m]));
    const list = $("localList");
    list.textContent = "";
    Whisper.CATALOG.forEach((c) => {
      const li = document.createElement("li");
      const done = have.get(c.id);
      const job = jobs[c.id];
      const selected = !!done && current.localModel === c.id;
      li.className = "model" + (selected ? " selected" : "");

      const info = document.createElement("div");
      info.className = "info";
      const name = document.createElement("div");
      name.className = "name";
      name.textContent = c.id;
      name.title = c.repo;
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.append(document.createTextNode(t("local_sizes", ST.formatBytes(c.download), ST.formatBytes(done ? done.bytes : c.stored),
        ST.formatBytes(c.vram))));
      if (done) meta.append(badge(t("badge_downloaded"), "ok"));
      if (selected && current.engine === "local") meta.append(badge(t("badge_selected"), "accent"));
      info.append(name, meta);
      if (job) {
        const status = document.createElement("div");
        status.className = "hint";
        status.textContent = t("local_progress", ST.formatBytes(job.got), ST.formatBytes(job.total));
        const track = document.createElement("div");
        track.className = "bar-track";
        const fill = document.createElement("div");
        fill.className = "bar-fill";
        fill.style.width = (job.total ? Math.min(100, (100 * job.got) / job.total) : 0).toFixed(1) + "%";
        track.append(fill);
        info.append(status, track);
        job.status = status;
        job.fill = fill;
      }

      const actions = document.createElement("div");
      actions.className = "actions";
      if (job) {
        actions.append(button(t("local_cancel"), "btn ghost sm", () => job.abort.abort()));
      } else if (done) {
        if (!selected || current.engine !== "local") {
          actions.append(button(t("use_model"), "btn ghost sm", async () => {
            current = await ST.setSettings({ localModel: c.id, engine: "local" });
            render();
          }));
        }
        actions.append(button(t("delete_model"), "btn danger sm", async () => {
          if (!confirm(t("local_confirm_delete", c.id, ST.formatBytes(done.bytes)))) return;
          await Whisper.store.remove(c.id);
          if (current.localModel === c.id) current = await ST.setSettings({ localModel: "" });
          render();
        }));
      } else {
        actions.append(button(t("download"), "btn sm", () => download(c)));
      }
      li.append(info, actions);
      list.append(li);
    });
    $("localKeepOpen").hidden = !Object.keys(jobs).length;
  }

  async function download(c) {
    const abort = new AbortController();
    jobs[c.id] = { got: 0, total: c.download, abort };
    setMsg("", "");
    render();
    let lastPaint = 0;
    try {
      await Whisper.store.download(c.id, {
        signal: abort.signal,
        onProgress: (got, total) => {
          const job = jobs[c.id];
          job.got = got;
          job.total = total;
          const now = Date.now();
          if (now - lastPaint < 250 || !job.fill) return;
          lastPaint = now;
          job.fill.style.width = Math.min(100, (100 * got) / total).toFixed(1) + "%";
          job.status.textContent = t("local_progress", ST.formatBytes(got), ST.formatBytes(total));
        },
      });
      delete jobs[c.id];
      // the first model downloaded becomes the one in use
      if (!current.localModel) current = await ST.setSettings({ localModel: c.id });
    } catch (e) {
      delete jobs[c.id];
      if (!abort.signal.aborted) {
        console.error("[stream-transcription] local download", e);
        const why = e && e.name === "QuotaExceededError" ? e.name : (e && e.message) || String(e);
        setMsg(t("local_download_failed", why), "bad");
      }
    }
    render();
  }

  function setMsg(text, kind) {
    const el = $("localMsg");
    el.textContent = text;
    el.className = "msg" + (kind ? " " + kind : "");
  }
})();
