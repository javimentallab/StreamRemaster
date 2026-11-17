// Transcription on this computer: log-mel frames, the tokenizer, Whisper's decoding rules
// and the streaming policy, around the GPU model in whisper-gpu.js. Engine.LocalSession
// has the same face as Engine.Session (the WebSocket one), so the capture code and the
// overlay don't care where the subtitles come from.
//
// Streaming works like WhisperLive: the audio since the last closed sentence (30 s at most)
// is transcribed again about once a second; sentences that are followed by another one, or
// that came out the same twice, are closed and dropped from the buffer.
"use strict";

var Whisper = globalThis.Whisper || {};
globalThis.Whisper = Whisper;

(function () {
  const SR = 16000;
  const HOP = 160;
  const NFFT = 400;
  const NBINS = NFFT / 2 + 1;

  // ------------------------------------------------------------------------ log-mel
  // Same numbers as Whisper's own front end: periodic Hann window of 400, hop 160, power
  // spectrum, Slaney mel filters (librosa's defaults, 0-8 kHz), log10, floor at max - 8,
  // then (x + 4) / 4.
  function hzToMel(f) {
    const fsp = 200 / 3, minLogHz = 1000, minLogMel = minLogHz / fsp, step = Math.log(6.4) / 27;
    return f >= minLogHz ? minLogMel + Math.log(f / minLogHz) / step : f / fsp;
  }
  function melToHz(m) {
    const fsp = 200 / 3, minLogHz = 1000, minLogMel = minLogHz / fsp, step = Math.log(6.4) / 27;
    return m >= minLogMel ? minLogHz * Math.exp(step * (m - minLogMel)) : fsp * m;
  }

  Whisper.melFilters = function (nMels) {
    const fft = new Float64Array(NBINS);
    for (let i = 0; i < NBINS; i++) fft[i] = (i * SR) / NFFT;
    const lo = hzToMel(0), hi = hzToMel(SR / 2);
    const pts = new Float64Array(nMels + 2);
    for (let i = 0; i < nMels + 2; i++) pts[i] = melToHz(lo + ((hi - lo) * i) / (nMels + 1));
    const out = new Float32Array(nMels * NBINS);
    for (let m = 0; m < nMels; m++) {
      const enorm = 2 / (pts[m + 2] - pts[m]);
      for (let k = 0; k < NBINS; k++) {
        const lower = (fft[k] - pts[m]) / (pts[m + 1] - pts[m]);
        const upper = (pts[m + 2] - fft[k]) / (pts[m + 2] - pts[m + 1]);
        out[m * NBINS + k] = Math.max(0, Math.min(lower, upper)) * enorm;
      }
    }
    return out;
  };

  Whisper.Mel = class {
    constructor(nMels) {
      this.nMels = nMels;
      this.filters = Whisper.melFilters(nMels);
      this.window = new Float32Array(NFFT);
      for (let n = 0; n < NFFT; n++) this.window[n] = 0.5 - 0.5 * Math.cos((2 * Math.PI * n) / NFFT);
      this.cos = new Float32Array(NBINS * NFFT);
      this.sin = new Float32Array(NBINS * NFFT);
      for (let k = 0; k < NBINS; k++) {
        for (let n = 0; n < NFFT; n++) {
          const a = (2 * Math.PI * ((k * n) % NFFT)) / NFFT;
          this.cos[k * NFFT + n] = Math.cos(a);
          this.sin[k * NFFT + n] = Math.sin(a);
        }
      }
      this.buf = new Float32Array(NFFT);
      this.power = new Float32Array(NBINS);
    }

    // log10 mel energies of the frame centred on sample `centre`; sample(i) gives the
    // audio (0 outside it).
    frame(sample, centre, out, outOffset) {
      // locals, not properties, inside the loops: some engines don't hoist them
      const x = this.buf, win = this.window, cos = this.cos, sin = this.sin, power = this.power, filters = this.filters;
      for (let n = 0; n < NFFT; n++) x[n] = sample(centre - NFFT / 2 + n) * win[n];
      for (let k = 0; k < NBINS; k++) {
        let re = 0, im = 0;
        const base = k * NFFT;
        for (let n = 0; n < NFFT; n++) {
          const v = x[n];
          re += v * cos[base + n];
          im += v * sin[base + n];
        }
        power[k] = re * re + im * im;
      }
      const nMels = this.nMels;
      for (let m = 0; m < nMels; m++) {
        let s = 0;
        const base = m * NBINS;
        for (let k = 0; k < NBINS; k++) s += filters[base + k] * power[k];
        out[outOffset + m] = Math.log10(Math.max(s, 1e-10));
      }
    }

    // Whole-clip version (tests, and the first pass of a session): frames for audio padded
    // with zeros to 30 s, normalised, frame-major [3000 * nMels].
    static normalise(frames) {
      let max = -Infinity;
      for (let i = 0; i < frames.length; i++) if (frames[i] > max) max = frames[i];
      const floor = max - 8;
      for (let i = 0; i < frames.length; i++) frames[i] = (Math.max(frames[i], floor) + 4) / 4;
      return frames;
    }

    clip(audio) {
      const out = new Float32Array(Whisper.N_FRAMES * this.nMels);
      const sample = (i) => (i >= 0 && i < audio.length ? audio[i] : 0);
      for (let f = 0; f < Whisper.N_FRAMES; f++) {
        if (f * HOP - NFFT / 2 >= audio.length) out.fill(-10, f * this.nMels, (f + 1) * this.nMels);
        else this.frame(sample, f * HOP, out, f * this.nMels);
      }
      return Whisper.Mel.normalise(out);
    }
  };

  // ---------------------------------------------------------------------- tokenizer
  // Only decoding is needed: token -> bytes through GPT-2's byte-to-character table.
  Whisper.Tokenizer = class {
    constructor(vocab) {
      const bs = [];
      for (let b = 33; b <= 126; b++) bs.push(b);
      for (let b = 161; b <= 172; b++) bs.push(b);
      for (let b = 174; b <= 255; b++) bs.push(b);
      const cs = bs.slice();
      let n = 0;
      for (let b = 0; b < 256; b++) {
        if (!bs.includes(b)) { bs.push(b); cs.push(256 + n); n++; }
      }
      const charToByte = new Map();
      bs.forEach((b, i) => charToByte.set(String.fromCharCode(cs[i]), b));
      this.bytes = [];
      for (const [tok, id] of Object.entries(vocab)) {
        const arr = [];
        for (const ch of tok) arr.push(charToByte.has(ch) ? charToByte.get(ch) : 63);
        this.bytes[id] = Uint8Array.from(arr);
      }
      this.decoder = new TextDecoder("utf-8");
    }

    decode(ids) {
      const parts = [];
      let len = 0;
      for (const id of ids) {
        const b = this.bytes[id];
        if (b) { parts.push(b); len += b.length; }
      }
      const all = new Uint8Array(len);
      let o = 0;
      for (const p of parts) { all.set(p, o); o += p.length; }
      return this.decoder.decode(all);
    }
  };

  // ----------------------------------------------------------------------- decoding
  Whisper.specialTokens = function (cfg, gen) {
    const eot = cfg.eos_token_id;
    const noTs = gen.no_timestamps_token_id;
    const langs = {};
    for (const [k, v] of Object.entries(gen.lang_to_id || {})) langs[k.replace(/[<|>]/g, "")] = v;
    return {
      eot,
      sot: cfg.decoder_start_token_id,
      transcribe: (gen.task_to_id || {}).transcribe,
      translate: (gen.task_to_id || {}).translate,
      noTimestamps: noTs,
      noSpeech: noTs - 1,
      tsBegin: noTs + 1,
      langs,
      suppress: gen.suppress_tokens || cfg.suppress_tokens || [],
      beginSuppress: gen.begin_suppress_tokens || cfg.begin_suppress_tokens || [220, eot],
      maxInitialTs: gen.max_initial_timestamp_index == null ? 50 : gen.max_initial_timestamp_index,
      multilingual: gen.is_multilingual !== false,
    };
  };

  function logSoftmax(logits) {
    let max = -Infinity;
    for (let i = 0; i < logits.length; i++) if (logits[i] > max) max = logits[i];
    let sum = 0;
    for (let i = 0; i < logits.length; i++) sum += Math.exp(logits[i] - max);
    const lse = max + Math.log(sum);
    const out = new Float32Array(logits.length);
    for (let i = 0; i < logits.length; i++) out[i] = logits[i] - lse;
    return out;
  }

  // Whisper's rules for the next token (openai/whisper decoding.py: SuppressBlank,
  // SuppressTokens, ApplyTimestampRules). `seq` = tokens sampled so far in this pass.
  Whisper.applyRules = function (logits, seq, sp) {
    const NEG = -Infinity;
    for (const t of sp.suppress) if (t < logits.length) logits[t] = NEG;
    // special tokens are never text
    for (let t = sp.eot + 1; t < sp.tsBegin; t++) logits[t] = NEG;
    if (seq.length === 0) for (const t of sp.beginSuppress) logits[t] = NEG;

    const last = seq.length >= 1 && seq[seq.length - 1] >= sp.tsBegin;
    const penult = seq.length < 2 || seq[seq.length - 2] >= sp.tsBegin;
    if (last) {
      if (penult) for (let t = sp.tsBegin; t < logits.length; t++) logits[t] = NEG;
      else for (let t = 0; t < sp.eot; t++) logits[t] = NEG;
    }
    let lastTs = -1;
    for (let i = seq.length - 1; i >= 0; i--) if (seq[i] >= sp.tsBegin) { lastTs = seq[i]; break; }
    if (lastTs >= 0) {
      const upTo = last && !penult ? lastTs : lastTs + 1;
      for (let t = sp.tsBegin; t < upTo; t++) logits[t] = NEG;
    }
    if (seq.length === 0) {
      for (let t = 0; t < sp.tsBegin; t++) logits[t] = NEG;
      for (let t = sp.tsBegin + sp.maxInitialTs + 1; t < logits.length; t++) logits[t] = NEG;
    }
    const lp = logSoftmax(logits);
    let tsMax = -Infinity;
    for (let t = sp.tsBegin; t < lp.length; t++) if (lp[t] > tsMax) tsMax = lp[t];
    let tsSum = 0;
    if (tsMax > -Infinity) for (let t = sp.tsBegin; t < lp.length; t++) tsSum += Math.exp(lp[t] - tsMax);
    const tsLogprob = tsMax + Math.log(tsSum || 1e-30);
    let textMax = -Infinity;
    for (let t = 0; t < sp.tsBegin; t++) if (lp[t] > textMax) textMax = lp[t];
    if (tsLogprob > textMax) for (let t = 0; t < sp.tsBegin; t++) { logits[t] = NEG; lp[t] = NEG; }
    return lp;
  };

  function argmax(a) {
    let best = 0, bv = -Infinity;
    for (let i = 0; i < a.length; i++) if (a[i] > bv) { bv = a[i]; best = i; }
    return best;
  }

  // The same short run of tokens over and over: the classic hallucination loop.
  Whisper.isLooping = function (seq) {
    for (let k = 1; k <= 12; k++) {
      const reps = k <= 2 ? 8 : 4;
      if (seq.length < k * reps) continue;
      let same = true;
      for (let r = 1; r < reps && same; r++) {
        for (let i = 0; i < k; i++) {
          if (seq[seq.length - 1 - i] !== seq[seq.length - 1 - i - r * k]) { same = false; break; }
        }
      }
      if (same) return k;
    }
    return 0;
  };

  // A loop found at the end of a run of tokens, cut back to one copy of the repeated part.
  Whisper.trimLoop = function (seq) {
    const k = Whisper.isLooping(seq);
    if (!k) return seq;
    const out = seq.slice();
    const repeats = () => {
      for (let i = 0; i < k; i++) if (out[out.length - 1 - i] !== out[out.length - 1 - i - k]) return false;
      return true;
    };
    while (out.length >= 2 * k && repeats()) out.length -= k;
    return out;
  };

  // Tokens -> segments {start, end, text, closed} with times in seconds inside the window.
  Whisper.segmentsFrom = function (seq, sp, tok, duration) {
    const out = [];
    let start = null;
    let text = [];
    for (const t of seq) {
      if (t >= sp.tsBegin) {
        const time = (t - sp.tsBegin) * 0.02;
        if (start === null || !text.length) {
          start = time;
        } else {
          out.push({ start, end: time, text: tok.decode(text), closed: true });
          text = [];
          start = null;
        }
      } else if (t < sp.eot) {
        if (start === null) start = 0;
        text.push(t);
      }
    }
    if (text.length) out.push({ start: start || 0, end: Math.max(duration, start || 0), text: tok.decode(text), closed: false });
    return out.filter((s) => s.text.trim());
  };

  // What Whisper writes over music and silence: the credits of the subtitles it was
  // trained on, and the sign-off of videos.
  const MADE_UP = /amara\.org|^\W*(subt[ií]tulos?( realizados)? por|subtitles by|sottotitoli|untertitel|sous-titr|legendas pela|¡?suscr[ií]bete|gracias por ver|thanks? (you )?(so much )?for watching|please subscribe|ご視聴|字幕)/i;
  Whisper.madeUp = (text) => MADE_UP.test(text.trim());

  Whisper.Transcriber = class {
    constructor(gpu, cfg, gen, tokenizer) {
      this.gpu = gpu;
      this.sp = Whisper.specialTokens(cfg, gen);
      this.tok = tokenizer;
    }

    // One pass over a window: mel [3000 * nMels] for `duration` seconds of real audio.
    // language: code or null (detected here); task: "transcribe" | "translate".
    async transcribe(mel, duration, { language, task }) {
      const sp = this.sp;
      if (this.gpu.setRules && !this.gpu.rulesSet) this.gpu.setRules(sp);
      await this.gpu.encode(mel);
      const first = await this.gpu.step(sp.sot, 0);
      const lp0 = logSoftmax(first);
      const noSpeech = Math.exp(lp0[sp.noSpeech]);
      let lang = language;
      let langProb = 1;
      if (sp.multilingual && (!lang || sp.langs[lang] == null)) {
        // softmax over the language tokens only
        let best = null, bv = -Infinity;
        for (const [code, id] of Object.entries(sp.langs)) if (first[id] > bv) { bv = first[id]; best = code; }
        let sum = 0;
        for (const id of Object.values(sp.langs)) sum += Math.exp(first[id] - bv);
        lang = best;
        langProb = 1 / sum;
      }
      const prompt = [];
      if (sp.multilingual) prompt.push(sp.langs[lang], task === "translate" ? sp.translate : sp.transcribe);
      let seq = [];
      let sumLp = 0;
      const wanted = 24 + Math.ceil(duration * 9);
      if (this.gpu.generate && prompt.length && !this.cpuRules) {
        // on the card, 16 tokens per read-back
        const r = await this.gpu.generate(prompt, 1, wanted, (toks) => Whisper.isLooping(toks) > 0);
        seq = Whisper.trimLoop(r.tokens);
        sumLp = r.sumLp;
      } else {
        // here, one read-back per token (English-only models, and the tests' reference)
        let logits = first;
        let pos = 1;
        for (const t of prompt) logits = await this.gpu.step(t, pos++);
        const maxTokens = Math.min(this.gpu.maxPos - pos - 1, wanted);
        while (seq.length < maxTokens) {
          const lp = Whisper.applyRules(logits, seq, sp);
          const t = argmax(lp);
          if (t === sp.eot) break;
          seq.push(t);
          sumLp += lp[t];
          if (Whisper.isLooping(seq)) { seq = Whisper.trimLoop(seq); break; }
          logits = await this.gpu.step(t, pos++);
        }
      }
      const avgLogprob = sumLp / Math.max(1, seq.length);
      const silent = noSpeech > 0.6 && avgLogprob < -1;
      return {
        language: lang,
        langProb,
        noSpeech,
        tokens: seq.length,
        avgLogprob,
        silent,
        segments: silent ? [] : Whisper.segmentsFrom(seq, sp, this.tok, duration).filter((x) => !Whisper.madeUp(x.text)),
      };
    }
  };

  // ---------------------------------------------------------------------- streaming
  const MIN_PASS_S = 1.0;        // audio needed before the first pass
  const NEW_AUDIO_S = 0.5;       // new audio between passes
  const MAX_WINDOW_S = 30;
  const CLIP_TO_S = 25;          // a window that never closes a sentence is cut to this
  const SEND_LAST = 10;          // closed segments sent with each update (like WhisperLive)

  Whisper.Stream = class {
    constructor(transcriber, mel, { language, task, onSegments, onLanguage, onError }) {
      this.tr = transcriber;
      this.melc = mel;
      this.language = language || null;
      this.task = task || "transcribe";
      this.onSegments = onSegments;
      this.onLanguage = onLanguage;
      this.onError = onError;
      this.audio = new Float32Array(SR * 40);
      this.audioStart = 0;     // absolute sample index of audio[0]
      this.total = 0;          // absolute samples received
      this.bufStart = 0;       // absolute sample where the open window starts
      this.lastPassAt = 0;     // this.total at the last pass
      this.cache = new Map();  // absolute frame -> Float32Array(nMels)
      this.done = [];
      this.prevLast = null;
      this.sameCount = 0;
      this.closed = false;
      this.busy = false;
    }

    push(f32) {
      const used = this.total - this.audioStart;
      if (used + f32.length > this.audio.length) {
        // drop what is before the window (keep 400 samples for the first frame's left half)
        const keepFrom = Math.max(this.audioStart, this.bufStart - NFFT);
        const keep = this.total - keepFrom;
        const size = Math.max(this.audio.length, (keep + f32.length) * 2);
        const next = new Float32Array(size);
        next.set(this.audio.subarray(keepFrom - this.audioStart, used));
        this.audio = next;
        this.audioStart = keepFrom;
      }
      this.audio.set(f32, this.total - this.audioStart);
      this.total += f32.length;
      this.kick();
    }

    sample(i) {
      if (i < this.audioStart || i >= this.total) return 0;
      return this.audio[i - this.audioStart];
    }

    kick() {
      if (this.busy || this.closed) return;
      const windowS = (this.total - this.bufStart) / SR;
      const fresh = (this.total - this.lastPassAt) / SR;
      if (windowS < MIN_PASS_S || fresh < NEW_AUDIO_S) return;
      this.busy = true;
      this.pass().catch((e) => { if (!this.closed && this.onError) this.onError(e); })
        .finally(() => { this.busy = false; if (!this.closed) setTimeout(() => this.kick(), 0); });
    }

    windowMel() {
      const n = this.melc.nMels;
      const out = new Float32Array(Whisper.N_FRAMES * n);
      const f0 = this.bufStart / HOP;
      const end = this.total;
      const sample = (i) => this.sample(i);
      for (let i = 0; i < Whisper.N_FRAMES; i++) {
        const f = f0 + i;
        const centre = f * HOP;
        if (centre - NFFT / 2 >= end) { out.fill(-10, i * n, (i + 1) * n); continue; }
        let cached = this.cache.get(f);
        if (!cached) {
          cached = new Float32Array(n);
          this.melc.frame(sample, centre, cached, 0);
          if (centre + NFFT / 2 <= end) this.cache.set(f, cached);   // complete frames only
        }
        out.set(cached, i * n);
      }
      for (const f of this.cache.keys()) if (f < f0) this.cache.delete(f);
      return Whisper.Mel.normalise(out);
    }

    rms(from, to) {
      let s = 0, n = 0;
      for (let i = Math.max(from, this.audioStart); i < to; i += 4) { const v = this.sample(i); s += v * v; n++; }
      return Math.sqrt(s / Math.max(1, n));
    }

    async pass() {
      if (this.total - this.bufStart > MAX_WINDOW_S * SR) {
        this.bufStart = Math.floor((this.total - CLIP_TO_S * SR) / HOP) * HOP;
        this.prevLast = null;
      }
      const start = this.bufStart;
      const end = this.total;
      this.lastPassAt = end;
      const duration = (end - start) / SR;
      // silence: nothing to transcribe, and no need to keep it in the window
      if (this.rms(start, end) < 0.002) {
        if (duration > 3) this.bufStart = Math.floor((end - SR) / HOP) * HOP;
        return;
      }
      const t0 = Date.now();
      const mel = this.windowMel();
      const t1 = Date.now();
      const res = await this.tr.transcribe(mel, duration, { language: this.language, task: this.task });
      if (this.closed) return;
      if (Whisper.debug) {
        console.info("[stream-transcription] pass", duration.toFixed(1) + " s", "mel", t1 - t0, "ms, model", Date.now() - t1, "ms,",
          res.tokens, "tokens,", res.language, res.langProb.toFixed(2), res.silent ? "silent" : "", res.segments.map((x) => x.text).join(" | "));
      }
      // The language is settled once the model is sure, or has said the same thing on
      // several windows long enough to tell (each fairly sure); until then every pass
      // detects it again.
      if (!this.language && res.language && !res.silent && duration >= 2 && res.langProb >= 0.5) {
        this.langVotes = this.langVotes && this.langVotes.lang === res.language
          ? { lang: res.language, n: this.langVotes.n + 1 } : { lang: res.language, n: 1 };
        if ((res.langProb >= 0.8 && duration >= 3) || this.langVotes.n >= 3) {
          this.language = res.language;
          this.onLanguage && this.onLanguage(res.language);
        }
      }
      if (res.silent) {
        if (duration > 5) this.bufStart = Math.floor((end - 2 * SR) / HOP) * HOP;
        this.emit(null);
        return;
      }
      // While the language is still open, a pass that isn't sure of it writes nonsense in
      // some other language (a short "Thank you." or a few Chinese characters): don't show it.
      if (!this.language && (duration < 2 || res.langProb < 0.5)) {
        this.emit(null);
        return;
      }
      // Timestamps past the audio are made up (the model is told the clip is 30 s long).
      const segs = res.segments
        .filter((s) => s.start < duration - 0.1)
        .map((s) => Object.assign({}, s, { end: Math.min(s.end, duration) }));
      let commit = 0;
      // a sentence is final once another one follows it, with a second of audio after it
      for (let i = 0; i < segs.length - 1; i++) if (segs[i].end <= duration - 1) commit = i + 1;
      const last = segs[segs.length - 1];
      if (commit < segs.length - 1) {
        this.sameCount = 0;
      } else if (last && last.closed && last.end <= duration - 0.3) {
        const same = this.prevLast && this.prevLast === last.text.trim();
        this.sameCount = same ? this.sameCount + 1 : 1;
        if (this.sameCount >= 2) commit = segs.length;
      } else {
        this.sameCount = 0;
      }
      this.prevLast = last ? last.text.trim() : null;
      const base = start / SR;
      let advance = 0;
      for (let i = 0; i < commit; i++) {
        const s = segs[i];
        this.done.push({ start: base + s.start, end: base + s.end, text: s.text });
        advance = s.end;
      }
      if (commit) {
        this.bufStart = Math.min(end, start + Math.floor((advance * SR) / HOP) * HOP);
        this.prevLast = null;
        this.sameCount = 0;
        if (this.done.length > 200) this.done.splice(0, this.done.length - 50);
      }
      const open = segs.slice(commit).map((s) => ({ start: base + s.start, end: base + s.end, text: s.text }));
      this.emit(open[0] || null, open.slice(1));
    }

    emit(partial, more) {
      const fmt = (x) => x.toFixed(3);
      const out = this.done.slice(-SEND_LAST).map((s) => ({ start: fmt(s.start), end: fmt(s.end), text: s.text, completed: true }));
      [partial, ...(more || [])].filter(Boolean).forEach((s) => out.push({ start: fmt(s.start), end: fmt(s.end), text: s.text, completed: false }));
      this.onSegments && this.onSegments(out);
    }

    close() { this.closed = true; }
  };

  // ------------------------------------------------------------------- session glue
  // The model stays loaded while this document lives, so stopping and starting again
  // (or a new tab) doesn't read the weights again.
  let loaded = null;   // { id, gpu, transcriber, mel }

  Whisper.load = async function (id, onProgress) {
    if (loaded && loaded.id === id && !loaded.gpu.lost) return loaded;
    if (loaded) { try { loaded.gpu.destroy(); } catch (e) { /* gone */ } loaded = null; }
    const meta = await Whisper.store.meta(id);
    if (!meta || !meta.complete) throw Object.assign(new Error("model not downloaded"), { code: "local_missing" });
    const device = await Whisper.requestDevice();
    const gpu = await Whisper.GpuModel.create(device, meta.config, (name) => Whisper.store.tensor(id, name), onProgress);
    const vocab = JSON.parse(await Whisper.store.text(id, "vocab.json"));
    const transcriber = new Whisper.Transcriber(gpu, meta.config, meta.generation, new Whisper.Tokenizer(vocab));
    loaded = { id, gpu, transcriber, mel: new Whisper.Mel(meta.config.num_mel_bins) };
    return loaded;
  };

  Whisper.unload = function () {
    if (loaded) { try { loaded.gpu.destroy(); loaded.gpu.device.destroy(); } catch (e) { /* gone */ } }
    loaded = null;
  };

  if (globalThis.Engine && Engine.Session) {
    Engine.LocalSession = class extends Engine.Session {
      constructor({ modelId, options, emit }) {
        super({ serverUrl: "", options, translating: false, emit });
        this.modelId = modelId;
      }

      connect() {
        this.watchdog = setInterval(() => this.check(), 2000);
        this.reloads = 0;
        // storage.local "debugLocal": true logs every pass (for checking speed)
        // Chromium's offscreen document, where this runs there, has no storage API.
        if (ext.storage && ext.storage.local) {
          ext.storage.local.get("debugLocal").then((r) => { Whisper.debug = !!r.debugLocal; }).catch(() => {});
        }
        this.load();
      }

      load() {
        this.setState("loading");
        Whisper.load(this.modelId).then((m) => {
          if (this.closed) return;
          this.model = m;
          this.stream = new Whisper.Stream(m.transcriber, m.mel, {
            language: this.options.language,
            task: this.options.task,
            onLanguage: (lang) => this.emit({ evt: "language", lang }),
            onSegments: (segments) => this.onSegments(segments),
            onError: (e) => this.fail(e),
          });
          this.ready = true;
          this.readyAt = Date.now();
          this.setState("listening");
        }).catch((e) => this.fail(e));
      }

      // A device the browser took away is not a full card: load the model again on a new device,
      // twice at most. Anything else ends the session with its real cause in the popup.
      fail(e) {
        if (this.closed) return;
        console.error("[stream-transcription] local engine:", e);
        const gpu = this.model && this.model.gpu;
        const message = String((e && e.message) || e || "");
        const lost = (gpu && gpu.lost) || /\blost\b|destroyed/i.test(message);
        if (lost && this.reloads < 2) {
          this.reloads++;
          console.warn("[stream-transcription] GPU device lost, loading the model again:", (gpu && gpu.lostReason) || message);
          if (this.stream) this.stream.close();
          this.stream = null;
          this.model = null;
          this.ready = false;
          Whisper.unload();
          setTimeout(() => { if (!this.closed) this.load(); }, 1000);
          return;
        }
        let code = e && e.code ? e.code : lost ? "local_lost" : (/out of memory|allocation/i.test(message) ? "local_vram" : "local_failed");
        if (code === "model_load") code = "local_vram";
        this.closed = true;
        clearInterval(this.watchdog);
        const detail = ((gpu && gpu.lostReason) || message).replace(/\s+/g, " ").slice(0, 160);
        this.setState("error", { error: code, detail });
        if (code === "local_vram" || code === "local_lost") Whisper.unload();
      }

      onSegments(segments) {
        this.lastPaintAt = Date.now();
        this.recovered();
        if (segments.some((s) => s && s.text && s.text.trim())) {
          this.hasText = true;
          this.setState("live");
        }
        this.emit({ evt: "segments", segments });
      }

      sendAudio(f32) {
        if (!this.ready || this.closed || !this.stream) return;
        let sum = 0;
        for (let i = 0; i < f32.length; i += 4) sum += f32[i] * f32[i];
        if (Math.sqrt(sum / Math.max(1, f32.length / 4)) > 0.01) this.lastLoudAt = Date.now();
        // A quiet stretch still counts as "answered": no subtitles are expected then.
        this.stream.push(f32);
      }

      close() {
        this.closed = true;
        clearInterval(this.watchdog);
        if (this.stream) this.stream.close();
      }
    };
  }

  Whisper.SR = SR;
})();
