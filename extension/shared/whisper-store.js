// Local Whisper models: which ones can be downloaded, and where they are kept.
//
// They come straight from the openai/whisper-* repositories on Hugging Face (MIT licence):
// the weights file is read as it downloads and every tensor is turned into half precision
// on the way in, so medium (3 GB of 32-bit weights) needs 1.5 GB on disk and never sits
// whole in memory. Everything goes to the extension's own IndexedDB, in parts of 32 MB.
"use strict";

var Whisper = globalThis.Whisper || {};
globalThis.Whisper = Whisper;

(function () {
  // download = bytes fetched; stored = bytes kept; vram = rough graphics memory in use.
  Whisper.CATALOG = [
    { id: "tiny", repo: "openai/whisper-tiny", download: 152e6, stored: 76e6, vram: 0.3e9 },
    { id: "base", repo: "openai/whisper-base", download: 292e6, stored: 146e6, vram: 0.5e9 },
    { id: "small", repo: "openai/whisper-small", download: 969e6, stored: 484e6, vram: 1.0e9 },
    { id: "medium", repo: "openai/whisper-medium", download: 3058e6, stored: 1528e6, vram: 2.4e9 },
    { id: "large-v3-turbo", repo: "openai/whisper-large-v3-turbo", download: 1620e6, stored: 1618e6, vram: 2.4e9 },
  ];
  Whisper.HF = "https://huggingface.co/";
  const PART = 16 * 1024 * 1024;   // elements per stored part (32 MB)
  const TEXT_FILES = ["config.json", "generation_config.json", "vocab.json"];

  // ------------------------------------------------------------------ half floats
  const f32 = new Float32Array(1);
  const u32 = new Uint32Array(f32.buffer);

  // 32-bit float bits -> 16-bit float bits, rounding to nearest even.
  function halfBits(u) {
    const sign = (u >>> 16) & 0x8000;
    let e = (u >>> 23) & 0xff;
    let m = u & 0x7fffff;
    if (e === 0xff) return sign | 0x7c00 | (m ? 0x200 : 0);
    e = e - 127 + 15;
    if (e >= 0x1f) return sign | 0x7c00;
    if (e <= 0) {
      if (e < -10) return sign;
      m |= 0x800000;
      const shift = 14 - e;
      let h = m >>> shift;
      const rem = m & ((1 << shift) - 1);
      const halfway = 1 << (shift - 1);
      if (rem > halfway || (rem === halfway && (h & 1))) h++;
      return sign | h;
    }
    let h = (e << 10) | (m >>> 13);
    const rem = m & 0x1fff;
    if (rem > 0x1000 || (rem === 0x1000 && (h & 1))) h++;
    return sign | h;
  }
  Whisper.halfBits = halfBits;
  Whisper.toHalf = function (x) { f32[0] = x; return halfBits(u32[0]); };
  Whisper.fromHalf = function (h) {
    const s = h & 0x8000 ? -1 : 1, e = (h >>> 10) & 0x1f, m = h & 0x3ff;
    if (e === 0) return s * m * Math.pow(2, -24);
    if (e === 31) return m ? NaN : s * Infinity;
    return s * (1 + m / 1024) * Math.pow(2, e - 15);
  };

  // --------------------------------------------------------- safetensors, streamed
  // feed() the file's bytes in order; onPart(name, index, Uint16Array) receives each part
  // of each tensor in half precision, onTensor(name, shape, parts) when one is complete.
  Whisper.HalfReader = class {
    constructor({ onPart, onTensor, keep }) {
      this.onPart = onPart;
      this.onTensor = onTensor;
      this.keep = keep || (() => true);
      this.head = new Uint8Array(0);
      this.tensors = null;
      this.pos = 0;       // offset inside the data section
      this.ti = 0;
      this.carry = new Uint8Array(0);
    }

    async feed(chunk) {
      if (!this.tensors) {
        const all = new Uint8Array(this.head.length + chunk.length);
        all.set(this.head);
        all.set(chunk, this.head.length);
        if (all.length < 8) { this.head = all; return; }
        const n = Number(new DataView(all.buffer, all.byteOffset, 8).getBigUint64(0, true));
        if (n > 100e6) throw Object.assign(new Error("bad safetensors header"), { code: "local_broken" });
        if (all.length < 8 + n) { this.head = all; return; }
        const header = JSON.parse(new TextDecoder().decode(all.subarray(8, 8 + n)));
        this.tensors = Object.entries(header).filter(([k]) => k !== "__metadata__")
          .map(([name, t]) => ({ name: Whisper.tensorName(name), dtype: t.dtype, shape: t.shape, a: t.data_offsets[0], b: t.data_offsets[1] }))
          .sort((x, y) => x.a - y.a);
        this.head = null;
        chunk = all.subarray(8 + n);
      }
      let off = 0;
      while (off < chunk.length && this.ti < this.tensors.length) {
        const t = this.tensors[this.ti];
        if (this.pos < t.a) {
          const skip = Math.min(t.a - this.pos, chunk.length - off);
          off += skip;
          this.pos += skip;
          continue;
        }
        if (!t.started) this.begin(t);
        const take = Math.min(t.b - this.pos, chunk.length - off);
        await this.convert(t, chunk.subarray(off, off + take));
        off += take;
        this.pos += take;
        if (this.pos === t.b) {
          await this.finish(t);
          this.ti++;
        }
      }
    }

    get done() { return !!this.tensors && this.ti >= this.tensors.length; }

    begin(t) {
      t.started = true;
      t.numel = t.shape.reduce((a, b) => a * b, 1);
      t.size = { F32: 4, F16: 2, BF16: 2 }[t.dtype];
      if (!t.size) throw Object.assign(new Error("unsupported dtype " + t.dtype), { code: "local_broken" });
      t.wanted = this.keep(t.name);
      t.out = 0;
      t.partIndex = 0;
      t.part = null;
      this.carry = new Uint8Array(0);
    }

    async convert(t, bytes) {
      if (!t.wanted) return;
      let src = bytes;
      if (this.carry.length) {
        src = new Uint8Array(this.carry.length + bytes.length);
        src.set(this.carry);
        src.set(bytes, this.carry.length);
      }
      const count = Math.floor(src.length / t.size);
      this.carry = src.slice(count * t.size);
      if (!count) return;
      // an aligned copy so typed views can read it
      const aligned = src.byteOffset % 4 === 0 && t.size === 4 ? src : src.slice(0, count * t.size);
      const view = t.size === 4
        ? new Uint32Array(aligned.buffer, aligned.byteOffset, count)
        : new Uint16Array(aligned.buffer, aligned.byteOffset, count);
      let i = 0;
      while (i < count) {
        if (!t.part) t.part = new Uint16Array(Math.min(PART, t.numel - t.partIndex * PART));
        const room = t.part.length - (t.out - t.partIndex * PART);
        const n = Math.min(room, count - i);
        const base = t.out - t.partIndex * PART;
        if (t.dtype === "F32") for (let j = 0; j < n; j++) t.part[base + j] = halfBits(view[i + j]);
        else if (t.dtype === "F16") t.part.set(view.subarray(i, i + n), base);
        else for (let j = 0; j < n; j++) t.part[base + j] = halfBits(view[i + j] << 16);
        i += n;
        t.out += n;
        if (t.out - t.partIndex * PART === t.part.length) {
          await this.onPart(t.name, t.partIndex, t.part);
          t.part = null;
          t.partIndex++;
        }
      }
    }

    async finish(t) {
      if (!t.wanted) return;
      if (t.out !== t.numel) throw Object.assign(new Error("short tensor " + t.name), { code: "local_broken" });
      if (this.onTensor) await this.onTensor(t.name, t.shape, t.partIndex);
    }
  };

  // Some exports leave out the "model." prefix.
  Whisper.tensorName = function (name) {
    return /^(encoder|decoder)\./.test(name) ? "model." + name : name;
  };
  // proj_out is the token table again (tied weights): not stored.
  Whisper.keepTensor = function (name) { return /^model\.(encoder|decoder)\./.test(name); };

  // -------------------------------------------------------------------- IndexedDB
  const DB = "streamremaster-whisper";
  let dbPromise = null;

  function db() {
    if (!dbPromise) {
      dbPromise = new Promise((resolve, reject) => {
        const req = indexedDB.open(DB, 1);
        req.onupgradeneeded = () => {
          const d = req.result;
          if (!d.objectStoreNames.contains("models")) d.createObjectStore("models", { keyPath: "id" });
          if (!d.objectStoreNames.contains("data")) d.createObjectStore("data");
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => { dbPromise = null; reject(req.error); };
      });
    }
    return dbPromise;
  }

  async function tx(stores, mode, fn) {
    const d = await db();
    return new Promise((resolve, reject) => {
      const t = d.transaction(stores, mode);
      let result;
      Promise.resolve(fn(t)).then((r) => { result = r; });
      t.oncomplete = () => resolve(result);
      t.onerror = () => reject(t.error);
      t.onabort = () => reject(t.error || new Error("aborted"));
    });
  }

  function req(r) {
    return new Promise((resolve, reject) => { r.onsuccess = () => resolve(r.result); r.onerror = () => reject(r.error); });
  }

  const key = (id, kind, name, i) => id + "|" + kind + "|" + name + (i == null ? "" : "|" + i);

  Whisper.store = {
    async list() {
      return tx(["models"], "readonly", (t) => req(t.objectStore("models").getAll()));
    },
    async meta(id) {
      return tx(["models"], "readonly", (t) => req(t.objectStore("models").get(id)));
    },
    async putMeta(meta) {
      return tx(["models"], "readwrite", (t) => { t.objectStore("models").put(meta); });
    },
    async putData(k, value) {
      return tx(["data"], "readwrite", (t) => { t.objectStore("data").put(value, k); });
    },
    async text(id, file) {
      return tx(["data"], "readonly", (t) => req(t.objectStore("data").get(key(id, "f", file))));
    },
    // the parts of one tensor, as Uint16Array
    async tensor(id, name) {
      const meta = await this.meta(id);
      const info = meta && meta.tensors[name];
      if (!info) return null;
      return tx(["data"], "readonly", async (t) => {
        const s = t.objectStore("data");
        const parts = [];
        for (let i = 0; i < info.parts; i++) parts.push(req(s.get(key(id, "t", name, i))));
        return (await Promise.all(parts)).map((b) => new Uint16Array(b));
      });
    },
    async remove(id) {
      return tx(["models", "data"], "readwrite", (t) => {
        t.objectStore("models").delete(id);
        t.objectStore("data").delete(IDBKeyRange.bound(id + "|", id + "|￿"));
      });
    },

    // Downloads and converts one model of the catalogue. onProgress(received, total).
    async download(id, { onProgress, signal } = {}) {
      const entry = Whisper.CATALOG.find((m) => m.id === id);
      if (!entry) throw Object.assign(new Error("unknown model"), { code: "local_unknown" });
      await this.remove(id);
      const base = Whisper.HF + entry.repo + "/resolve/main/";
      const meta = { id, repo: entry.repo, complete: false, tensors: {}, bytes: 0, added: Date.now() };
      try {
        for (const file of TEXT_FILES) {
          const r = await fetch(base + file, { signal });
          if (!r.ok) throw Object.assign(new Error(file + ": HTTP " + r.status), { code: "local_http" });
          const text = await r.text();
          await this.putData(key(id, "f", file), text);
          if (file === "config.json") meta.config = JSON.parse(text);
          if (file === "generation_config.json") meta.generation = JSON.parse(text);
        }
        await this.putMeta(meta);
        const r = await fetch(base + "model.safetensors", { signal });
        if (!r.ok || !r.body) throw Object.assign(new Error("weights: HTTP " + r.status), { code: "local_http" });
        const total = Number(r.headers.get("content-length")) || entry.download;
        const reader = new Whisper.HalfReader({
          keep: Whisper.keepTensor,
          onPart: async (name, i, part) => {
            await this.putData(key(id, "t", name, i), part.buffer);
            meta.bytes += part.byteLength;
          },
          onTensor: async (name, shape, parts) => { meta.tensors[name] = { shape, parts }; },
        });
        const rd = r.body.getReader();
        let got = 0;
        for (;;) {
          const { done, value } = await rd.read();
          if (done) break;
          got += value.length;
          await reader.feed(value);
          if (onProgress) onProgress(got, total);
        }
        if (!reader.done) throw Object.assign(new Error("download cut short"), { code: "local_http" });
        meta.complete = true;
        await this.putMeta(meta);
        return meta;
      } catch (e) {
        await this.remove(id).catch(() => {});
        throw e;
      }
    },
  };
})();
