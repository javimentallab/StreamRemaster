// Frame generation for HTML <video>, on WebGPU: takes the decoded frames of a video and paints the
// in-between frames on a canvas placed over it.
//
// Gecko is what shapes this file. It reports time far less often than it shows frames (about 25
// updates a second on a 60 fps video, for requestVideoFrameCallback and for currentTime alike), so
// frames are picked up on the display tick, from a continuous estimate of the media time. WebGPU
// also refuses a <video> as a copy source there, so frames enter through an external texture.
"use strict";

(globalThis.STFramegenInstall = function (root) {
  const COMMON_RATES = [23.976, 24, 25, 29.97, 30, 48, 50, 59.94, 60, 120];
  const RING_SIZE = 8;
  // How far behind the newest frame the output runs, in source frames: a pair must exist before
  // anything can be painted between its two frames (captured CAPTURE_LAG into its turn).
  const DELAY_FRAMES = 1.5;
  // A frame is taken this far into its turn, in source frames, not right at its start: the video
  // may not have swapped to it yet at that very moment, and a tick that lands just before the swap
  // would take the old frame twice.
  const CAPTURE_LAG = 0.25;
  // Without a frame from requestVideoFrameCallback for this long, the display tick captures again.
  const FRAME_CAPTURE_STALE_MS = 100;
  const FRAME_CAPTURE_DELAY_FRAMES = 2.25;
  // The frame timeline is fitted to the presentation times of the last few seconds of frames.
  const TIMELINE_WINDOW_S = 8;
  const TIMELINE_MIN_SPAN_S = 0.5;
  const TIMELINE_MIN_SAMPLES = 8;
  const RATE_WINDOW_MS = 1500;
  const MIN_SOURCE_HZ = 5;
  const SEEK_THRESHOLD_S = 0.1;
  const CLOCK_GAIN = 0.15;
  // Browser clocks round to 1 ms, so a tick can read slightly early against the output grid.
  const PRESENT_TOLERANCE_MS = 1.5;
  // Past this many unfinished upscales the GPU is behind: a frame goes without the network rather
  // than making the queue, and with it the delay, grow.
  const MAX_UPSCALES_IN_FLIGHT = 2;
  // The motion is worked out across at most this many source frames (frames never captured between).
  const MAX_MOTION_GAP = 4;
  const FIREFOX = /firefox/i.test(navigator.userAgent);

  // A continuous estimate of the media time, pulled gently towards each new currentTime reading.
  class MediaClock {
    constructor(video) {
      this.video = video;
      this.reset();
    }

    reset() {
      this.base = 0;
      this.baseAt = 0;
      this.last = NaN;
      this.ready = false;
    }

    now(t) {
      const video = this.video;
      const reading = video.currentTime;
      if (!this.ready) {
        this.base = reading;
        this.baseAt = t;
        this.last = reading;
        this.ready = true;
        return reading;
      }
      const rate = video.paused ? 0 : video.playbackRate || 1;
      const estimate = this.base + ((t - this.baseAt) / 1000) * rate;
      if (reading === this.last) return estimate;
      this.last = reading;
      const error = reading - estimate;
      if (Math.abs(error) > SEEK_THRESHOLD_S) {
        this.base = reading;
        this.baseAt = t;
        return reading;
      }
      this.base += error * CLOCK_GAIN;
      return estimate + error * CLOCK_GAIN;
    }
  }

  // The source frame rate, from the count of decoded frames: it is exact where the time readings
  // are not. 0 until a full window has been seen.
  class RateMeter {
    constructor(video) {
      this.video = video;
      this.reset();
    }

    reset() {
      this.startAt = 0;
      this.startFrames = 0;
      this.hz = 0;
    }

    // The video stopped: a window that spans the pause would read far too low.
    restart() {
      if (!this.hz) this.startAt = 0;
    }

    update(t) {
      const video = this.video;
      if (this.hz) return this.hz;
      if (!video.getVideoPlaybackQuality) return 0;
      if (video.readyState < 3) { this.startAt = 0; return 0; }
      const frames = video.getVideoPlaybackQuality().totalVideoFrames;
      if (!this.startAt) {
        this.startAt = t;
        this.startFrames = frames;
        return 0;
      }
      if (t - this.startAt < RATE_WINDOW_MS) return 0;
      const measured = ((frames - this.startFrames) * 1000) / (t - this.startAt) / (video.playbackRate || 1);
      if (!(measured >= MIN_SOURCE_HZ)) { this.startAt = 0; return 0; }
      const nearest = COMMON_RATES.reduce((a, b) => (Math.abs(b - measured) < Math.abs(a - measured) ? b : a));
      this.hz = Math.abs(nearest - measured) < measured * 0.03 ? nearest : measured;
      return this.hz;
    }
  }

  // Where the source frames sit in media time: frame n is shown from a + n / hz. Fitted by least
  // squares to the presentation times requestVideoFrameCallback reports (every frame in Chromium,
  // about 25 a second in Gecko, which is still plenty). This is what keeps the capture in step with
  // the video: a rate rounded to a common one (60 for a 59.94 stream) or a guessed phase lets the
  // moment a frame is taken drift until it falls on the very moment the video changes frame, and
  // from then on a frame is taken twice or missed at regular intervals.
  class FrameTimeline {
    constructor() {
      this.reset();
    }

    reset() {
      this.samples = [];
      this.lastMedia = NaN;
      this.lastN = 0;
      this.a = 0;
      this.hz = 0;
    }

    // A frame was presented at this media time. guessHz is the rough rate (RateMeter's).
    add(mediaTime, guessHz) {
      if (!(guessHz > 0) || !Number.isFinite(mediaTime)) return;
      const hz = this.hz || guessHz;
      if (!Number.isFinite(this.lastMedia) || mediaTime < this.lastMedia || mediaTime - this.lastMedia > 1) {
        // the first frame, a seek or a long gap: number from here, close to the clock-only numbering
        this.samples = [];
        this.hz = 0;
        this.lastN = Math.round(mediaTime * hz);
      } else {
        const step = Math.round((mediaTime - this.lastMedia) * hz);
        if (step <= 0) return; // the same frame again
        this.lastN += step;
      }
      this.lastMedia = mediaTime;
      this.samples.push([this.lastN, mediaTime]);
      while (this.samples.length && this.samples[0][1] < mediaTime - TIMELINE_WINDOW_S) this.samples.shift();
      this.fit(guessHz);
    }

    fit(guessHz) {
      const samples = this.samples;
      const count = samples.length;
      if (count < TIMELINE_MIN_SAMPLES || samples[count - 1][1] - samples[0][1] < TIMELINE_MIN_SPAN_S) return;
      const n0 = samples[0][0];
      let sn = 0, st = 0;
      for (const [n, t] of samples) { sn += n - n0; st += t; }
      const mn = sn / count, mt = st / count;
      let cov = 0, vn = 0;
      for (const [n, t] of samples) { cov += (n - n0 - mn) * (t - mt); vn += (n - n0 - mn) ** 2; }
      if (!(vn > 0) || !(cov > 0)) return;
      const hz = vn / cov;
      // Far from the measured rate: variable frame rate or broken timestamps, keep the clock alone.
      // Unless the fit lands right on a common rate: then it is the measured rate that is off (it
      // is taken once, over 1.5 s, and a page busy at that moment makes it read low, e.g. 57.75
      // for a 60 fps stream), and keeping it would drop a frame every few hundred milliseconds.
      const nearest = COMMON_RATES.reduce((a, b) => (Math.abs(b - hz) < Math.abs(a - hz) ? b : a));
      const onCommonRate = Math.abs(hz - nearest) < nearest * 0.002;
      if (Math.abs(hz - guessHz) > guessHz * 0.03 && !onCommonRate) return;
      this.hz = hz;
      this.a = mt - (mn + n0) / hz;
    }

    // The fractional frame number at a media time; the clock-only guess until a fit exists.
    position(media, guessHz) {
      return this.hz ? (media - this.a) * this.hz : media * guessHz;
    }
  }

  // The clock of the worker path, where every frame arrives on its own with its timestamp instead of
  // being read off the <video> on a display tick. In Chromium the frames are still captured on the
  // page's main thread (video.captureStream() copies the current frame there), stamped with the
  // moment of capture, and passed on to the worker; when the page stalls the frames of those
  // milliseconds are never captured, and the next ones arrive late. The worker cannot bring the
  // lost ones back, but it keeps painting through the stall and FrameGenerator bridges the gap with
  // the motion between the frames on either side (MAX_MOTION_GAP).
  //   - Frames are numbered by FrameTimeline from their timestamps (steps of the frame period).
  //   - When a frame on the fitted grid is on screen in the native video is learnt from the frames
  //     that arrive soonest: the lower envelope of arrival - grid time over the last seconds
  //     (lateness only ever adds).
  //   - The output runs behind the video by BASE_DELAY_FRAMES plus a delay that covers how late
  //     frames have been arriving lately: it grows at once (a pair must exist before it is shown)
  //     and shrinks slowly, so on a quiet page it stays near zero.
  const STREAM_OFFSET_WINDOW_S = 4;
  const STREAM_LATE_WINDOW_S = 15;
  const STREAM_DELAY_MARGIN_S = 0.008;
  const STREAM_DELAY_SHRINK = 0.02; // seconds of delay given back per second
  const STREAM_MAX_DELAY_S = 0.2;
  const STREAM_MIN_FRAMES = 5;
  const BASE_DELAY_FRAMES = 1.1;
  // A capture up to this much of a frame before its turn still counts as that frame (timing jitter).
  const STREAM_CAPTURE_SLACK = 0.35;

  class StreamTimer {
    constructor() {
      this.reset();
    }

    reset() {
      this.timeline = new FrameTimeline();
      this.deltas = [];
      this.guess = 0;
      this.lastTs = NaN;
      this.lastArrival = NaN;
      this.offsets = [];
      this.offset = NaN;
      this.lates = [];
      this.delay = 0;
      this.lastIndex = -Infinity;
      this.lastPosition = -Infinity;
    }

    get hz() {
      return this.timeline.hz || this.guess;
    }

    // A frame with timestamp ts (seconds) arrived at `arrival` (seconds, same clock as now() later).
    // Returns { index, reset }: index is null for a frame not to capture (the same one again, or
    // before the rate is known); reset says the numbering started over (a seek, a loop, a new source).
    frame(ts, arrival) {
      let reset = false;
      if (Number.isFinite(this.lastTs) && (ts < this.lastTs - 0.001 || ts - this.lastTs > 1)) {
        const delay = this.delay;
        this.reset();
        this.delay = delay; // the page stalls just as much as before
        reset = true;
      }
      if (ts === this.lastTs) return { index: null, reset };
      if (Number.isFinite(this.lastTs)) {
        this.deltas.push(ts - this.lastTs);
        if (this.deltas.length > 30) this.deltas.shift();
      }
      this.lastTs = ts;
      if (this.deltas.length < STREAM_MIN_FRAMES - 1) return { index: null, reset };
      const sorted = this.deltas.slice().sort((a, b) => a - b);
      const measured = 1 / sorted[sorted.length >> 1];
      const nearest = COMMON_RATES.reduce((a, b) => (Math.abs(b - measured) < Math.abs(a - measured) ? b : a));
      this.guess = Math.abs(nearest - measured) < measured * 0.03 ? nearest : measured;
      const tl = this.timeline;
      const before = tl.lastN;
      const hadFrames = Number.isFinite(tl.lastMedia);
      // A frame after a silence was captured late (the page stalled): its stamp is not its frame's
      // turn, so it stays out of the fit, which it would bend.
      const late = Number.isFinite(this.lastArrival) && arrival - this.lastArrival > 1.5 / this.guess;
      if (!late) tl.add(ts, this.guess);
      let index;
      if (tl.hz) {
        // The frame on screen when it was captured, on the fitted grid. A capture normally lands
        // within a few milliseconds of its frame's turn; one taken late shows the frame of that later
        // moment, and is numbered so.
        index = Math.floor((ts - tl.a) * tl.hz + STREAM_CAPTURE_SLACK);
      } else if (late && hadFrames) {
        index = tl.lastN + Math.floor((ts - tl.lastMedia) * this.guess + STREAM_CAPTURE_SLACK);
      } else {
        if (hadFrames && tl.lastN === before) return { index: null, reset };
        index = tl.lastN;
      }
      if (index <= this.lastIndex) return { index: null, reset };
      this.lastIndex = index;
      // Lateness against where the frame sits on the fitted grid, not against its own timestamp:
      // Chromium stamps captured frames with the moment of capture, which is late too when the page
      // stalls (and jitters by a few milliseconds besides).
      this.observeArrival(tl.hz ? tl.a + index / tl.hz : ts, arrival);
      return { index, reset };
    }

    // The window was in the background (its animation frames stopped): frames came in as the
    // browser pleased meanwhile, and the lateness measured then says nothing about now. Without
    // this the output kept up to 200 ms of delay for many seconds after coming back, looked for
    // frames already gone and stuttered.
    forgetLateness() {
      this.offsets = [];
      this.offset = NaN;
      this.lates = [];
      this.delay = 0;
      this.lastArrival = NaN;
      this.lastPosition = -Infinity;
    }

    observeArrival(ts, arrival) {
      const gap = arrival - ts;
      this.offsets.push([arrival, gap]);
      while (this.offsets.length && this.offsets[0][0] < arrival - STREAM_OFFSET_WINDOW_S) this.offsets.shift();
      let offset = Infinity;
      for (const [, g] of this.offsets) offset = Math.min(offset, g);
      this.offset = offset;
      // How long the output must lag to always have a frame after the instant it paints: how late
      // this frame is on the grid, or how long nothing arrived beyond one frame period (a stall,
      // whose frames were never captured), whichever is more.
      const silence = Number.isFinite(this.lastArrival) && this.guess ? arrival - this.lastArrival - 1 / this.guess : 0;
      this.lates.push([arrival, Math.max(gap - offset, silence)]);
      while (this.lates.length && this.lates[0][0] < arrival - STREAM_LATE_WINDOW_S) this.lates.shift();
      let late = 0;
      for (const [, l] of this.lates) late = Math.max(late, l);
      const wanted = Math.min(STREAM_MAX_DELAY_S, late > 0.003 ? late + STREAM_DELAY_MARGIN_S : 0);
      const elapsed = Number.isFinite(this.lastArrival) ? Math.max(0, arrival - this.lastArrival) : 0;
      this.delay = wanted >= this.delay ? wanted : Math.max(wanted, this.delay - STREAM_DELAY_SHRINK * elapsed);
      this.lastArrival = arrival;
    }

    // The fractional source frame to show at `now` (seconds); NaN until frames have come in. It never
    // goes back: when the delay grows the picture waits for time to catch up instead of replaying.
    position(now) {
      if (!this.guess || !Number.isFinite(this.offset)) return NaN;
      const p = this.timeline.position(now - this.offset - this.delay, this.guess) - BASE_DELAY_FRAMES;
      if (p < this.lastPosition && this.lastPosition - p < this.hz) return this.lastPosition;
      this.lastPosition = p;
      return p;
    }
  }

  const FULLSCREEN = `
    struct Out { @builtin(position) pos: vec4f, @location(0) uv: vec2f };
    @vertex fn vs(@builtin(vertex_index) i: u32) -> Out {
      let p = vec2f(f32((i << 1u) & 2u), f32(i & 2u));
      return Out(vec4f(p * 2.0 - 1.0, 0.0, 1.0), vec2f(p.x, 1.0 - p.y));
    }`;

  // The slot can be larger than the frame (the networks' multiple of 16): scale.xy = slot / frame,
  // so the frame lands pixel for pixel in the top-left corner and the band past it repeats its last
  // column and row. Nothing is stretched.
  // scale.zw: the last place sampled, one pixel inside the frame. Video arrives as 4:2:0 YUV whose
  // colour planes are padded past the picture (1080 rows are decoded as 1088); the clamp of
  // textureSampleBaseClampToEdge is not always applied to the colour plane, so sampling the last
  // row or the band past it blended in empty colour, which is green, and the band then repeated it
  // as green lines along the bottom or right edge. The same holds one pixel in from the left and top
  // edges: frames from a captured stream (Chromium's own thread) showed a green bar on the left.
  const CAPTURE_SHADER = FULLSCREEN + `
    @group(0) @binding(0) var frame: texture_external;
    @group(0) @binding(1) var smp: sampler;
    @group(0) @binding(2) var<uniform> scale: vec4f;
    @fragment fn fs(in: Out) -> @location(0) vec4f {
      return vec4f(textureSampleBaseClampToEdge(frame, smp, clamp(in.uv * scale.xy, vec2f(1.0) - scale.zw, scale.zw)).rgb, 1.0);
    }`;

  // The frame at instant t between a and b. With the interpolator's motion (in quarter-grid pixels,
  // both ways) both frames are pulled along it scaled to t and blended by the occlusion mask, as
  // tools/train/interp.py trains it. Without it the motion textures are zero and the mask is one
  // half, which is a plain cross-fade.
  const PRESENT_SHADER = FULLSCREEN + `
    @group(0) @binding(0) var a: texture_2d<f32>;
    @group(0) @binding(1) var b: texture_2d<f32>;
    @group(0) @binding(2) var smp: sampler;
    struct Params { p: vec4f, q: vec4f };
    // p: t, motion grid width and height, sharpening; q.x: 1 when the motion is the network's;
    // q.yz: the share of the slots that is picture (the rest is the edge band)
    @group(0) @binding(3) var<uniform> u: Params;
    @group(0) @binding(4) var flow: texture_2d<f32>;
    @group(0) @binding(5) var extra: texture_2d<f32>;
    // Four bilinear taps 1.5 texels away diagonally: the luma of about a 4 x 4 block around p.
    fn taps(tex: texture_2d<f32>, p: vec2f, d: vec2f) -> vec4f {
      let w = vec3f(0.299, 0.587, 0.114);
      return vec4f(dot(textureSampleLevel(tex, smp, p + vec2f(-d.x, -d.y), 0.0).rgb, w),
                   dot(textureSampleLevel(tex, smp, p + vec2f(d.x, -d.y), 0.0).rgb, w),
                   dot(textureSampleLevel(tex, smp, p + vec2f(-d.x, d.y), 0.0).rgb, w),
                   dot(textureSampleLevel(tex, smp, p + vec2f(d.x, d.y), 0.0).rgb, w));
    }
    fn spread(v: vec4f) -> f32 {
      return max(max(v.x, v.y), max(v.z, v.w)) - min(min(v.x, v.y), min(v.z, v.w));
    }
    // How much the two frames, each pulled to instant t, disagree, against how much the picture
    // varies there: large where the motion does not follow what is on screen (rain, snow, sparks
    // moving on their own), small on fine texture that is only a fraction of a pixel out, which is
    // what distant detail always is while the camera moves. Compared over a small block, not
    // pixel by pixel, for the same reason (tools/train/diag_detail.py measures both).
    fn mismatch(uv: vec2f) -> f32 {
      let t = u.p.x;
      let f = textureSampleLevel(flow, smp, uv, 0.0);
      let ft0 = (-(1.0 - t) * t * f.xy + t * t * f.zw) / u.p.yz;
      let ft1 = ((1.0 - t) * (1.0 - t) * f.xy - t * (1.0 - t) * f.zw) / u.p.yz;
      let d = 1.5 / vec2f(textureDimensions(a));
      let la = taps(a, uv + ft0, d);
      let lb = taps(b, uv + ft1, d);
      let diff = abs(dot(la - lb, vec4f(0.25)));
      return diff / ((spread(la) + spread(lb)) * 0.5 + 0.02);
    }
    fn synth(uv: vec2f) -> vec3f {
      let p = u.p;
      let t = p.x;
      let f = textureSampleLevel(flow, smp, uv, 0.0);
      let m = 1.0 / (1.0 + exp(-textureSampleLevel(extra, smp, uv, 0.0).x));
      let grid = p.yz;
      let f01 = f.xy / grid;
      let f10 = f.zw / grid;
      let ft0 = -(1.0 - t) * t * f01 + t * t * f10;
      let ft1 = (1.0 - t) * (1.0 - t) * f01 - t * (1.0 - t) * f10;
      let x = textureSampleLevel(a, smp, uv + ft0, 0.0).rgb;
      let y = textureSampleLevel(b, smp, uv + ft1, 0.0).rgb;
      let wa = (1.0 - t) * m;
      let wb = t * (1.0 - m);
      return (wa * x + wb * y) / max(wa + wb, 1e-4);
    }
    fn luma(c: vec3f) -> f32 { return dot(c, vec3f(0.299, 0.587, 0.114)); }
    // Adaptive sharpening: the difference from the mean of the four neighbours (one frame texel
    // away) is raised, then kept inside the neighbours' range so no halo or ringing appears. It
    // stays off on flat areas, where it would only raise noise and compression blocks, and eases
    // off on hard edges, which are already crisp and would only turn into stair steps. With the
    // network's motion it also eases off where the two frames disagree after being moved (small
    // things moving on their own, like rain or snow), so it does not raise what is already wrong.
    @fragment fn fs(in: Out) -> @location(0) vec4f {
      let uv = in.uv * u.q.yz;
      let c = synth(uv);
      var strength = u.p.w;
      if (strength > 0.0 && u.q.x > 0.5) {
        strength *= 1.0 - smoothstep(0.5, 1.2, mismatch(uv));
      }
      if (strength <= 0.0) { return vec4f(c, 1.0); }
      let d = 1.0 / vec2f(textureDimensions(a));
      let n = synth(uv - vec2f(0.0, d.y));
      let s = synth(uv + vec2f(0.0, d.y));
      let e = synth(uv + vec2f(d.x, 0.0));
      let w = synth(uv - vec2f(d.x, 0.0));
      let lo = min(c, min(min(n, s), min(e, w)));
      let hi = max(c, max(max(n, s), max(e, w)));
      let range = luma(hi) - luma(lo);
      let gain = 3.3 * strength * smoothstep(0.015, 0.08, range) * (1.0 - 0.7 * smoothstep(0.3, 0.6, range));
      let detail = c - (n + s + e + w) * 0.25;
      // a small margin past the neighbours' range, growing with the strength: crisper, still no halo
      let margin = 0.28 * strength * (hi - lo);
      return vec4f(clamp(c + gain * detail, lo - margin, hi + margin), 1.0);
    }`;

  class FrameGenerator {
    // width and height are the captured frames; the canvas is outputWidth x outputHeight. A model
    // adds an upscaled copy of every captured frame at twice their size.
    // An interpolator model replaces the cross-fade; it needs frame sizes that are multiples of 16.
    // contentWidth x contentHeight is the picture inside the captured frames when they carry an edge
    // band (see CAPTURE_SHADER); by default all of it.
    // video can be null: frames are then handed to capture() one by one (the worker, with VideoFrames)
    // and tick() is not used.
    constructor({ device, video = null, canvas, width, height, contentWidth = width, contentHeight = height, outputWidth = width, outputHeight = height, model = null, interpolator = null, sharpen = 0, onCapture = null, maxInFlight = MAX_UPSCALES_IN_FLIGHT }) {
      this.device = device;
      this.video = video;
      this.onCapture = onCapture;
      this.sharpen = sharpen; // 0 = off; about 0.3 soft to 0.9 strong
      this.maxInFlight = maxInFlight;
      this.inFlight = 0;
      this.nudging = false;
      this.destroyed = false;
      this.lastSlot = -1;
      this.clock = new MediaClock(video);
      this.rate = new RateMeter(video);
      this.timeline = new FrameTimeline();
      this.frameCallback = 0;
      // When the last frame was captured from requestVideoFrameCallback (see captureOnFrame).
      this.frameCapturedAt = -Infinity;
      this.frameCaptureOff = FIREFOX;
      if (video && typeof video.requestVideoFrameCallback === "function") {
        const onFrame = (_, metadata) => {
          if (this.destroyed) return;
          this.frameCallback = video.requestVideoFrameCallback(onFrame);
          if (metadata && typeof metadata.mediaTime === "number") {
            this.timeline.add(metadata.mediaTime, this.rate.hz);
            this.captureOnFrame(metadata.mediaTime);
          }
        };
        this.frameCallback = video.requestVideoFrameCallback(onFrame);
      }
      this.targetFps = 0; // 0 = every display tick
      this.ring = [];
      this.nextSlot = 0;
      this.lastIndex = -1;
      this.nextPresentAt = 0;
      this.stats = { captures: 0, presents: 0, holds: 0, upscaled: 0, upscaleSkipped: 0, interpolated: 0, interpolateSkipped: 0, synthesized: 0 };

      canvas.width = outputWidth;
      canvas.height = outputHeight;
      this.context = canvas.getContext("webgpu");
      const format = navigator.gpu.getPreferredCanvasFormat();
      this.context.configure({ device, format, alphaMode: "opaque" });

      this.sampler = device.createSampler({ magFilter: "linear", minFilter: "linear" });
      // Zero motion and a zero mask logit: the cross-fade.
      this.still = [0, 1].map(() => device.createTexture({ size: [1, 1], format: "rgba16float", usage: GPUTextureUsage.TEXTURE_BINDING }));
      this.stillViews = this.still.map((texture) => texture.createView());
      this.interpolator = null;
      if (interpolator && width % 16 === 0 && height % 16 === 0) {
        this.interpolator = new root.STFramegenFI.Interpolator(device, interpolator, width, height, RING_SIZE);
      }
      this.params = device.createBuffer({ size: 32, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
      this.contentWidth = contentWidth;
      this.contentHeight = contentHeight;
      this.shown = [contentWidth / width, contentHeight / height];
      this.captureScale = device.createBuffer({ size: 16, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
      device.queue.writeBuffer(this.captureScale, 0, new Float32Array([width / contentWidth, height / contentHeight,
        1 - 1 / contentWidth, 1 - 1 / contentHeight]));
      this.capturePipeline = this.pipeline(CAPTURE_SHADER, "rgba8unorm");
      this.presentPipeline = this.pipeline(PRESENT_SHADER, format);

      this.slots = [];
      for (let i = 0; i < RING_SIZE; i++) {
        const texture = device.createTexture({
          size: [width, height],
          format: "rgba8unorm",
          usage: GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_SRC | GPUTextureUsage.COPY_DST,
        });
        this.slots.push({ texture, view: texture.createView() });
      }
      this.upscaler = null;
      this.upscaledSlots = [];
      if (model) {
        this.upscaler = new root.STFramegenSR.Upscaler(device, model, width, height, this.sampler);
        for (let i = 0; i < RING_SIZE; i++) {
          const texture = device.createTexture({
            size: [width * 2, height * 2],
            format: "rgba8unorm",
            usage: GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.TEXTURE_BINDING,
          });
          this.upscaledSlots.push({ texture, view: texture.createView() });
        }
      }
      this.presentGroups = new Map();
    }

    pipeline(code, format) {
      const module = this.device.createShaderModule({ code });
      return this.device.createRenderPipeline({
        layout: "auto",
        vertex: { module, entryPoint: "vs" },
        fragment: { module, entryPoint: "fs", targets: [{ format }] },
        primitive: { topology: "triangle-list" },
      });
    }

    reset() {
      this.clock.reset();
      this.ring = [];
      this.nextSlot = 0;
      this.lastIndex = -1;
      this.nextPresentAt = 0;
      this.lastSlot = -1;
      if (this.upscaler) this.upscaler.resetState();
    }

    // Firefox only finishes GPU promises on its slow polls unless work keeps being submitted.
    nudge() {
      if (!FIREFOX || this.nudging) return;
      this.nudging = true;
      const again = () => {
        if (this.inFlight <= 0 || this.destroyed) { this.nudging = false; return; }
        this.device.queue.submit([]);
        setTimeout(again, 1);
      };
      setTimeout(again, 0);
    }

    // The element started playing something else.
    resetSource() {
      this.rate.reset();
      this.timeline.reset();
      this.reset();
    }

    // The source frame rate: the fitted one once there is a fit, else the measured one.
    sourceHz() {
      return this.timeline.hz || this.rate.hz;
    }

    // One display tick. Returns true when something was painted.
    tick(now) {
      const video = this.video;
      if (video.paused || video.seeking || !video.videoWidth) {
        this.rate.restart();
        return false;
      }
      const media = this.clock.now(now);
      const hz = this.rate.update(now);
      if (!hz) return false;
      const position = this.timeline.position(media, hz);
      const index = Math.floor(position - CAPTURE_LAG);
      if (index < this.lastIndex - hz) this.reset(); // a seek or a loop
      // Frames are being captured as the video shows them (captureOnFrame): the tick only paints.
      const onFrames = now - this.frameCapturedAt < FRAME_CAPTURE_STALE_MS;
      if (!onFrames && index > this.lastIndex) {
        this.lastIndex = index;
        this.capture(index);
      }
      // Captured on the video's frame callback, a frame comes in when the video shows it, which can
      // be a little after the clock expects it: running a bit further behind keeps the next frame
      // in hand (at 1.5 there were ~3 repeated pictures a second on Twitch).
      return this.present(position - (this.frameCaptureOff ? DELAY_FRAMES : FRAME_CAPTURE_DELAY_FRAMES), now);
    }

    // Chromium calls requestVideoFrameCallback for every frame, right when the video shows it, and
    // the <video> holds that very frame during the callback. Taking it there takes each frame once:
    // on the display tick, a tick that lands just before the video swaps frames takes the old one
    // twice and misses the next (measured on Twitch: 9-24 % of the captures were repeats, with as
    // many frames missed). Gecko calls it about 25 times a second, so there the tick keeps doing it.
    captureOnFrame(media) {
      const video = this.video;
      if (this.frameCaptureOff || !this.timeline.hz || video.paused || video.seeking) return;
      const index = Math.round(this.timeline.position(media, this.timeline.hz));
      this.frameCapturedAt = performance.now();
      if (index <= this.lastIndex) return;
      this.lastIndex = index;
      try {
        this.capture(index);
      } catch (error) {
        // Out of the page's own loop, nothing would catch this: hand the job back to the tick.
        console.warn("[streamremaster] capture on the video's frame callback failed:", error);
        this.frameCaptureOff = true;
        this.frameCapturedAt = -Infinity;
      }
    }

    // Firefox on Linux has WebGPU without external textures: there the frame goes through a 2D canvas.
    readFrame(slot, encoder, source = this.video) {
      const device = this.device;
      let external = null;
      if (!this.frameCanvas && typeof device.importExternalTexture === "function") {
        try {
          external = device.importExternalTexture({ source });
        } catch (error) {
          if (error.name !== "NotSupportedError") throw error;
        }
      }
      if (external) {
        const group = device.createBindGroup({
          layout: this.capturePipeline.getBindGroupLayout(0),
          entries: [{ binding: 0, resource: external }, { binding: 1, resource: this.sampler },
            { binding: 2, resource: { buffer: this.captureScale } }],
        });
        const pass = encoder.beginRenderPass({
          colorAttachments: [{ view: this.slots[slot].view, loadOp: "clear", storeOp: "store", clearValue: [0, 0, 0, 1] }],
        });
        pass.setPipeline(this.capturePipeline);
        pass.setBindGroup(0, group);
        pass.draw(3);
        pass.end();
        return;
      }
      const { texture } = this.slots[slot];
      if (!this.frameCanvas) {
        this.frameCanvas = new OffscreenCanvas(texture.width, texture.height);
        this.frameContext = this.frameCanvas.getContext("2d", { alpha: false });
      }
      // the picture pixel for pixel, then the edge band: its last column and row stretched out
      const cw = this.contentWidth;
      const ch = this.contentHeight;
      this.frameContext.drawImage(source, 0, 0, cw, ch);
      if (texture.width > cw) this.frameContext.drawImage(this.frameCanvas, cw - 1, 0, 1, ch, cw, 0, texture.width - cw, ch);
      if (texture.height > ch) this.frameContext.drawImage(this.frameCanvas, 0, ch - 1, texture.width, 1, 0, ch, texture.width, texture.height - ch);
      device.queue.copyExternalImageToTexture({ source: this.frameCanvas }, { texture }, [texture.width, texture.height]);
    }

    capture(index, source = this.video) {
      const device = this.device;
      const slot = this.nextSlot;
      this.nextSlot = (slot + 1) % RING_SIZE;
      const encoder = device.createCommandEncoder();
      this.readFrame(slot, encoder, source);
      // The motion from the frame before. It goes first: an aligned upscaler uses it to move the
      // previous upscaled frame onto this one. The frame before may be a few frames back when some
      // were never captured (the page stalled): the motion across the gap still fills it in
      // smoothly, where a cross-fade would show a jump.
      let motion = false;
      let before = null;
      for (const entry of this.ring) {
        if (entry.index < index && index - entry.index <= MAX_MOTION_GAP && (!before || entry.index > before.index)) before = entry;
      }
      if (this.interpolator && this.interpolator.ready && before) {
        if (this.inFlight < this.maxInFlight) {
          this.interpolator.run(encoder,
            { id: before.slot, view: this.slots[before.slot].view },
            { id: slot, view: this.slots[slot].view }, slot);
          motion = true;
          this.stats.interpolated++;
        } else {
          this.stats.interpolateSkipped++;
        }
      }
      let upscaled = false;
      if (this.upscaler && this.upscaler.ready) {
        if (this.inFlight < this.maxInFlight) {
          const previous = this.lastSlot >= 0 ? this.lastSlot : slot;
          const aligned = motion && before.upscaled
            ? { previous: { id: `u${before.slot}`, view: this.upscaledSlots[before.slot].view },
                motion: { id: `m${slot}`, view: this.interpolator.motionOf(slot).flowView } }
            : null;
          this.upscaler.run(encoder,
            { id: slot, view: this.slots[slot].view },
            { id: previous, view: this.slots[previous].view },
            { id: slot, view: this.upscaledSlots[slot].view }, aligned);
          upscaled = true;
          this.stats.upscaled++;
        } else {
          this.stats.upscaleSkipped++;
        }
      }
      device.queue.submit([encoder.finish()]);
      if (upscaled || motion) {
        this.inFlight++;
        device.queue.onSubmittedWorkDone().then(() => { this.inFlight--; }, () => { this.inFlight--; });
        this.nudge();
      }
      this.lastSlot = slot;
      this.ring = this.ring.filter((entry) => entry.slot !== slot);
      this.ring.push({ index, slot, upscaled, motion, motionFrom: motion ? before.index : null });
      this.stats.captures++;
      if (this.onCapture) this.onCapture(this.slots[slot].texture, index);
    }

    // The two captured frames around a fractional source position, and how far along between them.
    pair(position) {
      let before = null;
      let after = null;
      for (const entry of this.ring) {
        if (entry.index <= position && (!before || entry.index > before.index)) before = entry;
        if (entry.index > position && (!after || entry.index < after.index)) after = entry;
      }
      if (!before) return null;
      if (!after) return { a: before, b: before, t: 0, hold: true };
      return { a: before, b: after, t: (position - before.index) / (after.index - before.index), hold: false };
    }

    // A pair is shown from the same kind of frames: an upscaled one next to one that missed its turn
    // would be seen as the sharpness switching on and off.
    viewOf(entry, upscaled) {
      return (upscaled ? this.upscaledSlots : this.slots)[entry.slot].view;
    }

    // Takes the display ticks nearest an even grid at the target rate. Rates above the display's
    // simply use every tick.
    dueForPresent(now) {
      if (!this.targetFps) return true;
      if (now + PRESENT_TOLERANCE_MS < this.nextPresentAt) return false;
      this.nextPresentAt = Math.max(this.nextPresentAt + 1000 / this.targetFps, now);
      return true;
    }

    present(position, now) {
      if (!this.dueForPresent(now)) return false;
      const pair = this.pair(position);
      if (!pair) return false;
      if (pair.hold) this.stats.holds++;
      const device = this.device;
      const moving = !pair.hold && pair.b.motion && pair.b.motionFrom === pair.a.index;
      const motion = moving ? this.interpolator.motionOf(pair.b.slot) : null;
      const upscaled = pair.a.upscaled && pair.b.upscaled;
      const key = `${pair.a.slot}:${pair.b.slot}:${+upscaled}:${moving ? 1 : 0}`;
      let group = this.presentGroups.get(key);
      if (!group) {
        group = device.createBindGroup({
          layout: this.presentPipeline.getBindGroupLayout(0),
          entries: [
            { binding: 0, resource: this.viewOf(pair.a, upscaled) },
            { binding: 1, resource: this.viewOf(pair.b, upscaled) },
            { binding: 2, resource: this.sampler },
            { binding: 3, resource: { buffer: this.params } },
            { binding: 4, resource: motion ? motion.flowView : this.stillViews[0] },
            { binding: 5, resource: motion ? motion.extraView : this.stillViews[1] },
          ],
        });
        this.presentGroups.set(key, group);
      }
      if (moving) this.stats.synthesized++;
      const grid = this.interpolator ? [this.interpolator.w4, this.interpolator.h4] : [1, 1];
      device.queue.writeBuffer(this.params, 0, new Float32Array([pair.t, grid[0], grid[1], this.sharpen, moving ? 1 : 0,
        this.shown[0], this.shown[1], 0]));
      const encoder = device.createCommandEncoder();
      const pass = encoder.beginRenderPass({
        colorAttachments: [{
          view: this.context.getCurrentTexture().createView(),
          loadOp: "clear", storeOp: "store", clearValue: [0, 0, 0, 1],
        }],
      });
      pass.setPipeline(this.presentPipeline);
      pass.setBindGroup(0, group);
      pass.draw(3);
      pass.end();
      device.queue.submit([encoder.finish()]);
      this.stats.presents++;
      return true;
    }

    destroy() {
      this.destroyed = true;
      if (this.frameCallback && typeof this.video.cancelVideoFrameCallback === "function") {
        this.video.cancelVideoFrameCallback(this.frameCallback);
      }
      for (const slot of this.slots) slot.texture.destroy();
      for (const slot of this.upscaledSlots) slot.texture.destroy();
      if (this.upscaler) this.upscaler.destroy();
      if (this.interpolator) this.interpolator.destroy();
      for (const texture of this.still) texture.destroy();
      this.params.destroy();
      this.captureScale.destroy();
      this.slots = [];
      this.upscaledSlots = [];
      this.presentGroups.clear();
    }
  }

  const MAX_OUTPUT_HEIGHT = 2160;
  // Above this the network costs more than a frame on mid-range cards.
  const MAX_MODEL_INPUT_HEIGHT = 1080;
  const even = (n) => Math.max(2, Math.round(n / 2) * 2);

  // What to capture and what to paint for a video of width x height. options: { resolution
  // ("original", "display" or an output height), model, interpolator }; displayHeight is the
  // screen's height in device pixels, for "display". The network only runs when the output is
  // larger than the video.
  function planSizes(width, height, options, displayHeight) {
    let wanted = height;
    if (options.resolution === "display") wanted = displayHeight;
    else if (options.resolution !== "original") wanted = Number(options.resolution) || height;
    const outputHeight = even(Math.min(MAX_OUTPUT_HEIGHT, wanted));
    const useModel = !!options.model && outputHeight > height;
    // The picture is captured at its own size, pixel for pixel (a near-1 resize blurs everything).
    // The interpolator needs frames in multiples of 16: the slots get an edge band up to that size,
    // which is never shown (FrameGenerator's contentWidth and contentHeight).
    const inputHeight = even(Math.min(height, outputHeight, useModel ? MAX_MODEL_INPUT_HEIGHT : Infinity));
    const inputWidth = even((width * inputHeight) / height);
    const pad = options.interpolator ? (n) => Math.ceil(n / 16) * 16 : (n) => n;
    return {
      width: pad(inputWidth), height: pad(inputHeight), contentWidth: inputWidth, contentHeight: inputHeight,
      outputWidth: even((width * outputHeight) / height), outputHeight,
      model: useModel ? options.model : null,
      interpolator: options.interpolator || null,
    };
  }

  // The graphics memory a FrameGenerator built from that plan takes: the ring of captured frames,
  // their upscaled copies, the networks' buffers, and the canvas counted with three images (the
  // browser keeps a few to show them).
  function memoryBytes(plan) {
    const { width, height } = plan;
    let bytes = RING_SIZE * width * height * 4 + 3 * plan.outputWidth * plan.outputHeight * 4;
    if (plan.model) {
      bytes += RING_SIZE * (width * 2) * (height * 2) * 4 + root.STFramegenSR.memoryBytes(plan.model, width, height);
    }
    if (plan.interpolator && width % 16 === 0 && height % 16 === 0) {
      bytes += root.STFramegenFI.memoryBytes(plan.interpolator, width, height, RING_SIZE);
    }
    return bytes;
  }

  root.STFramegen = { FrameGenerator, MediaClock, RateMeter, FrameTimeline, StreamTimer, PRESENT_SHADER, planSizes, memoryBytes, BASE_DELAY_FRAMES };
})(globalThis);
