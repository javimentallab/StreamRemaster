// Smooth video: the frames of a <video> go to the graphics card as the video shows them, and a
// canvas over the video is painted on every refresh of the screen with the picture that belongs to
// that instant, between the two frames around it.
//
// Two halves, kept apart:
//   - Schedule: no graphics, only time. Which frame was taken when, how far behind the video the
//     canvas runs, and which two frames (and how far between them) a given instant shows.
//   - Renderer: only graphics. Copies a frame in, runs the model's two networks on it (motion from
//     the frame before, and the upscaled copy) and paints the picture between two frames.
// The page side (framegen-page.js) owns the <video>, the canvas and the loop, and joins the two.
//
// Everything is measured in media time, in seconds: a frame is known by the media time at which
// the video starts showing it. No frame numbers and no frame rate to guess: a 59.94 fps stream, a
// variable one or one that skips frames are all the same case.
"use strict";

(function (root) {
  // ---- time ---------------------------------------------------------------------------------------

  const median = (list) => list.slice().sort((x, y) => x - y)[list.length >> 1];
  const clamp = (value, low, high) => Math.min(high, Math.max(low, value));

  // The video's clock moved by more than this against ours: it paused, sought, stalled or looped.
  const JUMP_MS = 50;
  const CLOCK_GAIN = 0.1;

  // Which instant of the video is on screen at a given time of the page's clock (milliseconds),
  // learnt from readings (this media time, at this moment). Each reading is off by up to a refresh
  // of the screen, so they are averaged; a reading far from the others is a jump.
  class Timebase {
    constructor() {
      this.reset();
    }

    reset() {
      this.offset = NaN;
      this.rate = 1;
    }

    get ready() {
      return Number.isFinite(this.offset);
    }

    // Returns true when the video jumped: what was known before no longer holds.
    sample(media, wall, rate = 1) {
      const offset = wall - (media * 1000) / rate;
      if (!this.ready || rate !== this.rate) {
        const jumped = this.ready;
        this.offset = offset;
        this.rate = rate;
        return jumped;
      }
      const error = offset - this.offset;
      if (Math.abs(error) > JUMP_MS) {
        this.offset = offset;
        return true;
      }
      this.offset += error * CLOCK_GAIN;
      return false;
    }

    mediaAt(wall) {
      return ((wall - this.offset) * this.rate) / 1000;
    }
  }

  // Frames a second from a running count of frames (the browser's count of decoded frames), over
  // the last two seconds. Only a rough figure: it tells how many frames lie between two timestamps.
  const COUNT_EVERY_MS = 250;
  const COUNT_WINDOW_MS = 2000;
  const COUNT_MIN_MS = 1000;

  class Counter {
    constructor() {
      this.reset();
    }

    reset() {
      this.readings = [];
      this.hz = 0;
    }

    add(count, wall, rate = 1) {
      const readings = this.readings;
      const last = readings[readings.length - 1];
      if (last && (count < last[1] || wall - last[0] > COUNT_WINDOW_MS)) this.readings.length = 0;
      else if (last && wall - last[0] < COUNT_EVERY_MS) return this.hz;
      readings.push([wall, count]);
      while (readings.length > 2 && wall - readings[1][0] >= COUNT_MIN_MS) readings.shift();
      const first = readings[0];
      if (wall - first[0] >= COUNT_MIN_MS) this.hz = ((count - first[1]) * 1000) / (wall - first[0]) / rate;
      return this.hz;
    }
  }

  // Where the frames sit in media time when the browser does not hand them over one by one (Gecko
  // reports about 25 frames a second of a 60 fps video). Each report is the exact timestamp of a
  // real frame, so the last one anchors the grid, and the spacing is the time between two reports
  // divided by the frames that lie between them (the rough rate tells how many).
  const GRID_STEPS = 40;
  const GRID_MAX_SKIP = 8;

  class Grid {
    constructor() {
      this.reset();
    }

    reset() {
      this.anchor = NaN;
      this.period = 0;
      this.steps = [];
    }

    sample(timestamp, rough) {
      if (Number.isFinite(this.anchor) && rough > 0) {
        const delta = timestamp - this.anchor;
        const frames = Math.round(delta * rough);
        if (delta > 0 && frames >= 1 && frames <= GRID_MAX_SKIP) {
          this.steps.push(delta / frames);
          if (this.steps.length > GRID_STEPS) this.steps.shift();
          this.period = median(this.steps);
        } else if (delta < 0 || frames > GRID_MAX_SKIP) {
          this.steps = [];
        }
      }
      this.anchor = timestamp;
    }

    // The frame on screen at a media time: { start, period }, or null while nothing is known.
    frameAt(media, rough) {
      const period = this.period || (rough > 0 ? 1 / rough : 0);
      if (!period) return null;
      const anchor = Number.isFinite(this.anchor) ? this.anchor : 0;
      return { start: anchor + Math.floor((media - anchor) / period + 1e-6) * period, period };
    }
  }

  // How far behind the video the canvas runs, in media seconds. To paint between two frames the
  // later one must already be here when the earlier one's turn comes. Each frame that comes in
  // tells how much delay that took: the time from the frame before it to the instant the video
  // stood at when it arrived. The delay is the most that was needed these last seconds, and a
  // little more: one frame's time on a calm page, more where frames come late or some never come.
  // It moves gently: a sudden change of delay would be seen as the picture jumping.
  const NEED_WINDOW_MS = 5000;
  const DELAY_SAFETY_S = 0.004;
  const DELAY_MAX_FRAMES = 2.5;
  const DELAY_GROW = 0.25;    // seconds of delay gained per second
  const DELAY_SHRINK = 0.02;  // and given back

  class Pacer {
    constructor() {
      this.reset();
    }

    reset() {
      this.needs = [];
      this.delay = NaN;
    }

    // A frame came in that needed this much delay to be on time (media seconds).
    arrival(need, wall) {
      this.needs.push([wall, need]);
      while (this.needs[0][0] < wall - NEED_WINDOW_MS) this.needs.shift();
    }

    update(period, seconds) {
      let most = -Infinity;
      for (const [, need] of this.needs) most = Math.max(most, need);
      if (!Number.isFinite(most)) most = period;
      const wanted = clamp(most + DELAY_SAFETY_S, 0, DELAY_MAX_FRAMES * period);
      if (!Number.isFinite(this.delay)) {
        this.delay = wanted;
      } else {
        const step = (wanted > this.delay ? DELAY_GROW : DELAY_SHRINK) * seconds;
        this.delay += clamp(wanted - this.delay, -step, step);
      }
      return this.delay;
    }
  }

  // Frames kept on the card at a time: the two being shown and the ones waiting their turn.
  const RING = 6;
  // In the tick-driven mode a frame is taken on a refresh in the first part of its turn. Gecko swaps
  // the frame in the <video> ahead of the moment its frame callback gives for it (it hands the
  // frame to the compositor before the screen shows it), by 13-17 ms on a 30 fps video, changing
  // from one run to the next: measured in Firefox 160 on a video with its frame number written on
  // it, every frame taken in the first half of its turn was the right one, even right at its start,
  // and past the half up to all of them were already the next one. A frame whose first refresh
  // comes later than this is left out: the motion spans the gap, where a frame taken as another
  // would make the picture jump. Never two in a row, so a refresh about as slow as the frames
  // still takes every other one.
  const SAFE_TO = 0.45;
  // Two frames further apart than this many frame times are not joined: the motion network was
  // never taught such leaps, and it is most likely a cut. The earlier one stays until the later's turn.
  const GAP_FRAMES = 4.5;
  // With no newer frame, the last one stays this many frame times; after that nothing is painted
  // and the video itself shows through.
  const HOLD_FRAMES = 4;
  const SPACINGS = 60;
  const MAX_SPACING_S = 0.25;

  class Schedule {
    constructor(ring = RING) {
      this.ring = ring;
      this.timebase = new Timebase();
      this.grid = new Grid();
      this.pacer = new Pacer();
      this.forget();
    }

    // The video jumped or changed: the frames in hand belong to another moment.
    forget() {
      this.frames = [];
      this.spacings = [];
      this.spacing = 0;
      this.lastSeen = NaN;
      this.lastView = NaN;
      this.pacer.reset();
    }

    reset() {
      this.timebase.reset();
      this.grid.reset();
      this.forget();
    }

    // A reading of the video's clock. True when it jumped (the frames in hand are then dropped).
    clock(media, wall, rate = 1) {
      const jumped = this.timebase.sample(media, wall, rate);
      if (jumped) {
        this.grid.reset();
        this.forget();
      }
      return jumped;
    }

    // The time one frame lasts, in media seconds; 0 while unknown.
    get period() {
      return this.grid.period || this.spacing;
    }

    // Tick-driven mode: the media time of the frame to take at this moment, or null when the one on
    // screen is already taken or it is too late in its turn to be sure of it (see SAFE_TO).
    // `rough`: frames a second, roughly.
    due(wall, rough) {
      if (!this.timebase.ready) return null;
      const media = this.timebase.mediaAt(wall);
      const cell = this.grid.frameAt(media, rough);
      if (!cell) return null;
      if (!this.grid.period) this.spacing = cell.period;
      if (Number.isFinite(this.lastSeen) && cell.start < this.lastSeen + cell.period / 2) return null;
      const at = (media - cell.start) / cell.period;
      const leftBefore = !Number.isFinite(this.lastSeen) || this.lastSeen < cell.start - 1.5 * cell.period;
      if (at > SAFE_TO && !leftBefore) return null;
      this.takenAt = at;
      return cell.start;
    }

    // A new frame is on offer, whether it ends up being taken or not.
    seen(media) {
      if (Number.isFinite(this.lastSeen)) {
        const spacing = media - this.lastSeen;
        if (spacing > 0 && spacing < MAX_SPACING_S) {
          this.spacings.push(spacing);
          if (this.spacings.length > SPACINGS) this.spacings.shift();
          // The mean of the usual spacings (a frame that never came leaves a double one out of it).
          // Not the median: timestamps rounded to the millisecond go 16, 17, 17, 16...
          const middle = median(this.spacings);
          const usual = this.spacings.filter((value) => value > middle * 0.6 && value < middle * 1.4);
          this.spacing = usual.reduce((sum, value) => sum + value, 0) / usual.length;
        }
      }
      this.lastSeen = media;
    }

    // The frame is being taken. Returns its record ({ media, slot, from, upscaled }; the caller
    // fills the last two in), the frame before it, and whether the two are close enough to work
    // out the motion between them.
    take(media, wall) {
      const frames = this.frames;
      const previous = frames.length ? frames[frames.length - 1] : null;
      let slot;
      if (frames.length >= this.ring) {
        slot = frames.shift().slot;
      } else {
        const used = new Set(frames.map((frame) => frame.slot));
        slot = 0;
        while (used.has(slot)) slot++;
      }
      const frame = { media, slot, from: null, upscaled: false };
      frames.push(frame);
      const reach = (this.period || MAX_SPACING_S / GAP_FRAMES) * GAP_FRAMES;
      const bridge = !!previous && media > previous.media && media - previous.media <= reach;
      // The delay this frame needed: from the frame before it (one frame's time back, when that
      // one is not to be joined with it) to where the video stood when it came in.
      const since = bridge ? previous.media : media - this.period;
      if (this.timebase.ready && this.period) this.pacer.arrival(this.timebase.mediaAt(wall) - since, wall);
      return { frame, previous, bridge };
    }

    // The canvas's delay behind the video right now, in milliseconds of the page's clock.
    get delayMs() {
      return Number.isFinite(this.pacer.delay) ? (this.pacer.delay * 1000) / this.timebase.rate : 0;
    }

    // What to paint at this moment: { a, b, t, moving } (the picture a share t of the way from frame
    // a to frame b; moving says the motion from a to b is known), or null for nothing.
    view(wall) {
      const period = this.period;
      if (!this.timebase.ready || !period || !this.frames.length) return null;
      const seconds = Number.isFinite(this.lastView) ? clamp((wall - this.lastView) / 1000, 0, 0.1) : 0;
      this.lastView = wall;
      const at = this.timebase.mediaAt(wall) - this.pacer.update(period, seconds);
      let a = null;
      let b = null;
      for (const frame of this.frames) {
        if (frame.media <= at) a = frame;
        else { b = frame; break; }
      }
      if (!a) return null;
      if (!b) return at - a.media > HOLD_FRAMES * period ? null : { a, b: a, t: 0, moving: false };
      const span = b.media - a.media;
      if (span > GAP_FRAMES * period) return { a, b: a, t: 0, moving: false };
      return { a, b, t: (at - a.media) / span, moving: b.from === a.media };
    }
  }

  // ---- sizes --------------------------------------------------------------------------------------

  const MAX_OUTPUT_HEIGHT = 2160;
  // The upscaling network doubles the picture, and above this it costs more than a frame's time.
  const MAX_UPSCALER_INPUT_HEIGHT = 1080;
  // The motion network works on frames whose sides are multiples of this.
  const BLOCK = 16;
  const even = (n) => Math.max(2, Math.round(n / 2) * 2);

  // The height the work is done for, from the height the player takes on screen in device pixels:
  // the first of these steps that is not far below it. Steps, so that dragging a window does not
  // call for new sizes at every pixel.
  const SHOWN_STEPS = [720, 1080, 1440, 2160];
  const SHOWN_SLACK = 0.85;
  function shownStep(pixels, screenHeight) {
    if (!(pixels > 0)) return screenHeight;
    const step = SHOWN_STEPS.find((height) => height >= pixels * SHOWN_SLACK) || SHOWN_STEPS[SHOWN_STEPS.length - 1];
    return Math.min(step, screenHeight);
  }

  // What to take and what to paint for a video of width x height. options: { resolution ("original",
  // "display" or an output height), model, interpolator }. `limit` is the tallest the picture can be
  // seen (the player's height, see shownStep): no choice goes past it, there is nothing to gain.
  // The upscaling network runs only when the output is taller than the video.
  //   width x height: the frames on the card. With a motion network they carry a band on the right
  //     and bottom up to a multiple of 16, never shown; the picture is contentWidth x contentHeight,
  //     pixel for pixel in the top-left corner.
  function planSizes(width, height, options, limit) {
    const wanted = options.resolution === "display" ? limit
      : options.resolution === "original" ? height
      : Number(options.resolution) || height;
    const outputHeight = even(Math.min(MAX_OUTPUT_HEIGHT, wanted, limit > 0 ? limit : Infinity));
    const model = options.model && outputHeight > height ? options.model : null;
    const contentHeight = even(Math.min(height, outputHeight, model ? MAX_UPSCALER_INPUT_HEIGHT : Infinity));
    const contentWidth = even((width * contentHeight) / height);
    const interpolator = options.interpolator || null;
    const pad = interpolator ? (n) => Math.ceil(n / BLOCK) * BLOCK : (n) => n;
    return {
      width: pad(contentWidth), height: pad(contentHeight), contentWidth, contentHeight,
      outputWidth: even((width * outputHeight) / height), outputHeight, model, interpolator,
    };
  }

  // The graphics memory a Renderer built from that plan takes: the frames, their upscaled copies,
  // the picture before sharpening, the networks' own buffers, and the canvas counted as three
  // pictures (the browser keeps a few to show them).
  function memoryBytes(plan) {
    const { width, height } = plan;
    const scale = plan.model ? 2 : 1;
    let bytes = RING * width * height * 4 + 3 * plan.outputWidth * plan.outputHeight * 4
      + width * scale * height * scale * 4;
    if (plan.model) {
      bytes += RING * (width * 2) * (height * 2) * 4 + root.STFramegenSR.memoryBytes(plan.model, width, height);
    }
    if (plan.interpolator) bytes += root.STFramegenFI.memoryBytes(plan.interpolator, width, height, RING);
    return bytes;
  }

  // ---- graphics -----------------------------------------------------------------------------------

  const TRIANGLE = `
    struct Out { @builtin(position) pos: vec4f, @location(0) uv: vec2f };
    @vertex fn vs(@builtin(vertex_index) i: u32) -> Out {
      let p = vec2f(f32((i << 1u) & 2u), f32(i & 2u));
      return Out(vec4f(p * 2.0 - 1.0, 0.0, 1.0), vec2f(p.x, 1.0 - p.y));
    }`;

  // The video frame into a slot. fit.xy = slot / picture, so the picture lands pixel for pixel in
  // the top-left corner; past it the band repeats the picture's edge. fit.zw is one pixel of the
  // picture: nothing is read closer to the frame's border than that. A video frame's colour planes
  // are half the size and padded past the picture with empty colour, which is green, and a read on
  // the very border blends it in.
  const TAKE_SHADER = TRIANGLE + `
    @group(0) @binding(0) var frame: texture_external;
    @group(0) @binding(1) var smp: sampler;
    @group(0) @binding(2) var<uniform> fit: vec4f;
    @fragment fn fs(in: Out) -> @location(0) vec4f {
      let uv = clamp(in.uv * fit.xy, fit.zw, vec2f(1.0) - fit.zw);
      return vec4f(textureSampleBaseClampToEdge(frame, smp, uv).rgb, 1.0);
    }`;

  // The picture a share t of the way from frame a to frame b. The motion network gives, on a grid a
  // quarter the size of the frame, the movement from a to b and from b to a in grid cells, and how
  // much to trust each frame at every point (things that one of the two hides). Each frame is read
  // where its content will be at t and the two are mixed by that trust and by how near in time each
  // is: this is how the model was trained, so it is not ours to change. With no motion the textures
  // are zero and it comes down to a plain fade from a to b.
  //
  // The alpha that comes out is how much sharpening the point takes afterwards: less where the two
  // frames, each brought to t, still disagree against how much the picture varies there (rain,
  // snow, sparks: things the motion does not follow), compared over a small block and not point by
  // point, so that fine distant detail, always a fraction of a pixel out while the camera moves,
  // keeps all of it.
  const BLEND_SHADER = TRIANGLE + `
    struct U { t: f32, check: f32, grid: vec2f, area: vec2f };
    @group(0) @binding(0) var a: texture_2d<f32>;
    @group(0) @binding(1) var b: texture_2d<f32>;
    @group(0) @binding(2) var smp: sampler;
    @group(0) @binding(3) var<uniform> u: U;
    @group(0) @binding(4) var motion: texture_2d<f32>;
    @group(0) @binding(5) var trust: texture_2d<f32>;
    const LUMA = vec3f(0.299, 0.587, 0.114);
    fn block(tex: texture_2d<f32>, p: vec2f, d: vec2f) -> vec4f {
      return vec4f(dot(textureSampleLevel(tex, smp, p + vec2f(-d.x, -d.y), 0.0).rgb, LUMA),
                   dot(textureSampleLevel(tex, smp, p + vec2f(d.x, -d.y), 0.0).rgb, LUMA),
                   dot(textureSampleLevel(tex, smp, p + vec2f(-d.x, d.y), 0.0).rgb, LUMA),
                   dot(textureSampleLevel(tex, smp, p + vec2f(d.x, d.y), 0.0).rgb, LUMA));
    }
    fn spread(v: vec4f) -> f32 {
      return max(max(v.x, v.y), max(v.z, v.w)) - min(min(v.x, v.y), min(v.z, v.w));
    }
    @fragment fn fs(in: Out) -> @location(0) vec4f {
      let uv = in.uv * u.area;
      let t = u.t;
      let m = textureSampleLevel(motion, smp, uv, 0.0);
      let ab = m.xy / u.grid;
      let ba = m.zw / u.grid;
      let pa = uv - (1.0 - t) * t * ab + t * t * ba;
      let pb = uv + (1.0 - t) * (1.0 - t) * ab - t * (1.0 - t) * ba;
      let keep = 1.0 / (1.0 + exp(-textureSampleLevel(trust, smp, uv, 0.0).x));
      let wa = (1.0 - t) * keep;
      let wb = t * (1.0 - keep);
      let colour = (wa * textureSampleLevel(a, smp, pa, 0.0).rgb + wb * textureSampleLevel(b, smp, pb, 0.0).rgb)
        / max(wa + wb, 1e-4);
      var sharpen = 1.0;
      if (u.check > 0.5) {
        let d = 1.5 / vec2f(textureDimensions(a));
        let la = block(a, pa, d);
        let lb = block(b, pb, d);
        let apart = abs(dot(la - lb, vec4f(0.25))) / ((spread(la) + spread(lb)) * 0.5 + 0.02);
        sharpen = 1.0 - smoothstep(0.5, 1.2, apart);
      }
      return vec4f(colour, sharpen);
    }`;

  // The blended picture onto the canvas, sharpened: what sets a point apart from the mean of its
  // four neighbours is raised, and the result kept within the neighbours' own range plus a small
  // margin, so no halo appears. Nothing on flat areas, where it would only raise noise and
  // compression blocks, and less on hard edges, which are crisp already and would turn into stairs.
  const SHARPEN_SHADER = TRIANGLE + `
    struct V { area: vec2f, strength: f32, pad: f32 };
    @group(0) @binding(0) var picture: texture_2d<f32>;
    @group(0) @binding(1) var smp: sampler;
    @group(0) @binding(2) var<uniform> v: V;
    const LUMA = vec3f(0.299, 0.587, 0.114);
    @fragment fn fs(in: Out) -> @location(0) vec4f {
      let uv = in.uv * v.area;
      let centre = textureSampleLevel(picture, smp, uv, 0.0);
      let c = centre.rgb;
      let strength = v.strength * centre.a;
      if (strength <= 0.0) { return vec4f(c, 1.0); }
      let d = 1.0 / vec2f(textureDimensions(picture));
      let n = textureSampleLevel(picture, smp, uv - vec2f(0.0, d.y), 0.0).rgb;
      let s = textureSampleLevel(picture, smp, uv + vec2f(0.0, d.y), 0.0).rgb;
      let e = textureSampleLevel(picture, smp, uv + vec2f(d.x, 0.0), 0.0).rgb;
      let w = textureSampleLevel(picture, smp, uv - vec2f(d.x, 0.0), 0.0).rgb;
      let low = min(c, min(min(n, s), min(e, w)));
      let high = max(c, max(max(n, s), max(e, w)));
      let range = dot(high - low, LUMA);
      let gain = 3.3 * strength * smoothstep(0.015, 0.08, range) * (1.0 - 0.7 * smoothstep(0.3, 0.6, range));
      let margin = 0.28 * strength * (high - low);
      return vec4f(clamp(c + gain * (c - (n + s + e + w) * 0.25), low - margin, high + margin), 1.0);
    }`;

  // Frames whose networks have not finished on the card. At this many, the card is behind, and the
  // next frame is left out whole rather than queued: the motion then spans the gap, and the picture
  // stays as sharp and as smooth as the card can make it. Gecko says late that work has finished,
  // so there the count runs higher with nothing wrong.
  const BUSY_AT = /firefox/i.test((root.navigator && root.navigator.userAgent) || "") ? 4 : 2;

  const pipelines = new WeakMap();

  class Renderer {
    // plan: what planSizes gives, plus sharpen (0 = off; about 0.35 soft to 0.9 strong).
    constructor({ device, canvas, plan }) {
      this.device = device;
      this.plan = plan;
      this.sharpen = plan.sharpen || 0;
      this.pending = 0;
      this.viaCanvas = typeof device.importExternalTexture !== "function";
      const { width, height } = plan;
      canvas.width = plan.outputWidth;
      canvas.height = plan.outputHeight;
      this.context = canvas.getContext("webgpu");
      const format = navigator.gpu.getPreferredCanvasFormat();
      this.context.configure({ device, format, alphaMode: "opaque" });

      this.sampler = device.createSampler({ magFilter: "linear", minFilter: "linear" });
      const texture = (w, h, usage, textureFormat = "rgba8unorm") => {
        const made = device.createTexture({ size: [w, h], format: textureFormat, usage });
        return { texture: made, view: made.createView() };
      };
      const TARGET = GPUTextureUsage.RENDER_ATTACHMENT | GPUTextureUsage.TEXTURE_BINDING;
      this.frames = [];
      this.upscaled = [];
      for (let i = 0; i < RING; i++) this.frames.push(texture(width, height, TARGET | GPUTextureUsage.COPY_DST | GPUTextureUsage.COPY_SRC));
      // no motion and even trust: the plain fade
      this.none = [texture(1, 1, GPUTextureUsage.TEXTURE_BINDING, "rgba16float"), texture(1, 1, GPUTextureUsage.TEXTURE_BINDING, "rgba16float")];
      this.interpolator = plan.interpolator ? new root.STFramegenFI.Interpolator(device, plan.interpolator, width, height, RING) : null;
      this.upscaler = null;
      if (plan.model) {
        this.upscaler = new root.STFramegenSR.Upscaler(device, plan.model, width, height, this.sampler);
        for (let i = 0; i < RING; i++) {
          this.upscaled.push(texture(width * 2, height * 2, GPUTextureUsage.STORAGE_BINDING | GPUTextureUsage.TEXTURE_BINDING));
        }
      }
      // The blended picture, before sharpening: one the size of the frames, one of their upscaled copies.
      this.blended = [null, null];
      this.makeBlended = (large) => texture(width * (large ? 2 : 1), height * (large ? 2 : 1), TARGET);

      const uniform = (floats) => {
        const buffer = device.createBuffer({ size: floats.length * 4, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
        device.queue.writeBuffer(buffer, 0, new Float32Array(floats));
        return buffer;
      };
      const { contentWidth, contentHeight } = plan;
      this.area = [contentWidth / width, contentHeight / height];
      this.fit = uniform([width / contentWidth, height / contentHeight, 1 / contentWidth, 1 / contentHeight]);
      this.blendValues = uniform([0, 0, 1, 1, 1, 1, 0, 0]);
      this.sharpenValues = uniform([this.area[0], this.area[1], this.sharpen, 0]);
      this.takePipeline = this.pipeline(TAKE_SHADER, "rgba8unorm");
      this.blendPipeline = this.pipeline(BLEND_SHADER, "rgba8unorm");
      this.directPipeline = this.pipeline(BLEND_SHADER, format);
      this.sharpenPipeline = this.pipeline(SHARPEN_SHADER, format);
      this.groups = new Map();
      this.stats = { taken: 0, left: 0, painted: 0, moved: 0, upscaled: 0, held: 0 };
    }

    // Compiled once per device: a new size of the player builds a new Renderer, and compiling its
    // shaders again each time held the picture for a moment.
    pipeline(code, format) {
      let cache = pipelines.get(this.device);
      if (!cache) pipelines.set(this.device, (cache = new Map()));
      const key = `${format}
${code}`;
      let pipeline = cache.get(key);
      if (!pipeline) {
        const module = this.device.createShaderModule({ code });
        pipeline = this.device.createRenderPipeline({
          layout: "auto",
          vertex: { module, entryPoint: "vs" },
          fragment: { module, entryPoint: "fs", targets: [{ format }] },
          primitive: { topology: "triangle-list" },
        });
        cache.set(key, pipeline);
      }
      return pipeline;
    }

    group(key, pipeline, resources) {
      let group = this.groups.get(key);
      if (!group) {
        group = this.device.createBindGroup({
          layout: pipeline.getBindGroupLayout(0),
          entries: resources.map((resource, binding) => ({ binding, resource })),
        });
        this.groups.set(key, group);
      }
      return group;
    }

    draw(encoder, view, pipeline, group) {
      const pass = encoder.beginRenderPass({
        colorAttachments: [{ view, loadOp: "clear", storeOp: "store", clearValue: [0, 0, 0, 1] }],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(0, group);
      pass.draw(3);
      pass.end();
    }

    get motionReady() {
      return !!(this.interpolator && this.interpolator.ready);
    }

    get upscalerReady() {
      return !!(this.upscaler && this.upscaler.ready);
    }

    // The card has not finished the frames before: this one is better left out (see BUSY_AT).
    busy() {
      const busy = (this.motionReady || this.upscalerReady) && this.pending >= BUSY_AT;
      if (busy) this.stats.left++;
      return busy;
    }

    // The video jumped: the upscaler's memory of the frames before is of no use.
    forget() {
      if (this.upscaler) this.upscaler.resetState();
    }

    // The video's current frame into the slot of `frame` (a Schedule record). Where the browser has
    // WebGPU without video textures (Firefox on Linux) it goes through a 2D canvas.
    read(encoder, source, slot) {
      const device = this.device;
      if (!this.viaCanvas) {
        let external = null;
        try {
          external = device.importExternalTexture({ source });
        } catch (error) {
          if (error.name !== "NotSupportedError") throw error;
          this.viaCanvas = true;
        }
        if (external) {
          // an external texture lives for this task only: its group cannot be kept
          const group = device.createBindGroup({
            layout: this.takePipeline.getBindGroupLayout(0),
            entries: [{ binding: 0, resource: external }, { binding: 1, resource: this.sampler },
              { binding: 2, resource: { buffer: this.fit } }],
          });
          this.draw(encoder, this.frames[slot].view, this.takePipeline, group);
          return;
        }
      }
      const { width, height, contentWidth, contentHeight } = this.plan;
      if (!this.scratch) {
        this.scratch = new OffscreenCanvas(width, height);
        this.scratchContext = this.scratch.getContext("2d", { alpha: false });
      }
      const context = this.scratchContext;
      context.drawImage(source, 0, 0, contentWidth, contentHeight);
      if (width > contentWidth) context.drawImage(this.scratch, contentWidth - 1, 0, 1, contentHeight, contentWidth, 0, width - contentWidth, contentHeight);
      if (height > contentHeight) context.drawImage(this.scratch, 0, contentHeight - 1, width, 1, 0, contentHeight, width, height - contentHeight);
      device.queue.copyExternalImageToTexture({ source: this.scratch }, { texture: this.frames[slot].texture }, [width, height]);
    }

    // Takes the video's current frame and sets the networks to work on it. `previous` is the
    // record of the frame before (or null) and `bridge` whether to work out the motion from it.
    // Fills in the frame's record: from (the frame its motion starts at) and upscaled.
    take(source, frame, previous, bridge) {
      const device = this.device;
      const slot = frame.slot;
      const encoder = device.createCommandEncoder();
      this.read(encoder, source, slot);
      const current = { id: slot, view: this.frames[slot].view };
      let moved = false;
      if (bridge && this.motionReady) {
        this.interpolator.run(encoder, { id: previous.slot, view: this.frames[previous.slot].view }, current, slot);
        frame.from = previous.media;
        moved = true;
        this.stats.moved++;
      }
      if (this.upscalerReady) {
        // The upscaler looks at the frame before as well: its upscaled copy, brought onto this
        // frame by the motion just worked out. Without either it works from this frame alone.
        const before = previous ? { id: previous.slot, view: this.frames[previous.slot].view } : current;
        const aligned = moved && previous.upscaled
          ? { previous: { id: `u${previous.slot}`, view: this.upscaled[previous.slot].view },
              motion: { id: `m${slot}`, view: this.interpolator.motionOf(slot).flowView } }
          : null;
        this.upscaler.run(encoder, current, before, { id: slot, view: this.upscaled[slot].view }, aligned);
        frame.upscaled = true;
        this.stats.upscaled++;
      }
      device.queue.submit([encoder.finish()]);
      if (moved || frame.upscaled) {
        this.pending++;
        const done = () => { this.pending--; };
        device.queue.onSubmittedWorkDone().then(done, done);
      }
      this.stats.taken++;
    }

    // Paints the picture a share t of the way from frame a to frame b (Schedule records).
    paint(a, b, t, moving) {
      const device = this.device;
      // Both from the same kind of frame: an upscaled one beside a plain one would be seen as the
      // sharpness going on and off.
      const large = a.upscaled && b.upscaled;
      const pictures = large ? this.upscaled : this.frames;
      const motion = moving ? this.interpolator.motionOf(b.slot) : null;
      const resources = [pictures[a.slot].view, pictures[b.slot].view, this.sampler, { buffer: this.blendValues },
        motion ? motion.flowView : this.none[0].view, motion ? motion.extraView : this.none[1].view];
      const key = `${a.slot}:${b.slot}:${+large}:${+moving}`;
      const grid = motion ? [this.interpolator.w4, this.interpolator.h4] : [1, 1];
      const sharpening = this.sharpen > 0;
      const encoder = device.createCommandEncoder();
      const canvas = this.context.getCurrentTexture().createView();
      if (sharpening) {
        // Two steps: the picture is blended once, whole, and then sharpened from that. Blending it
        // again for every neighbour the sharpening looks at would be five times the work.
        const index = +large;
        if (!this.blended[index]) this.blended[index] = this.makeBlended(large);
        const blended = this.blended[index];
        device.queue.writeBuffer(this.blendValues, 0, new Float32Array([t, moving ? 1 : 0, grid[0], grid[1], 1, 1, 0, 0]));
        this.draw(encoder, blended.view, this.blendPipeline, this.group(`b${key}`, this.blendPipeline, resources));
        this.draw(encoder, canvas, this.sharpenPipeline,
          this.group(`s${index}`, this.sharpenPipeline, [blended.view, this.sampler, { buffer: this.sharpenValues }]));
      } else {
        device.queue.writeBuffer(this.blendValues, 0, new Float32Array([t, 0, grid[0], grid[1], this.area[0], this.area[1], 0, 0]));
        this.draw(encoder, canvas, this.directPipeline, this.group(`d${key}`, this.directPipeline, resources));
      }
      device.queue.submit([encoder.finish()]);
      this.stats.painted++;
      if (a === b) this.stats.held++;
    }

    destroy() {
      for (const item of [...this.frames, ...this.upscaled, ...this.none, ...this.blended]) if (item) item.texture.destroy();
      for (const buffer of [this.fit, this.blendValues, this.sharpenValues]) buffer.destroy();
      if (this.upscaler) this.upscaler.destroy();
      if (this.interpolator) this.interpolator.destroy();
      this.groups.clear();
      this.frames = [];
      this.upscaled = [];
    }
  }

  root.STFramegen = { Timebase, Counter, Grid, Pacer, Schedule, Renderer, planSizes, shownStep, memoryBytes, RING };
})(globalThis);
