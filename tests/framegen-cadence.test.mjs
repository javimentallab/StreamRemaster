// Copies among the frames: a 60 fps video that carries 24, 25 or 30 pictures a second. The
// bookkeeping that tells copies from new pictures and spreads the new ones evenly.
import test from 'node:test';
import assert from 'node:assert/strict';

await import(new URL('../extension/shared/framegen.js', import.meta.url).href);
const { Cadence } = globalThis.STFramegen;

// Feeds frames 1..count of a video whose picture number at frame n is picture(n).
// Returns the frames that were told to leave, with the frame each one copies.
function feed(cadence, picture, count, from = 1) {
  const left = [];
  for (let n = from; n < from + count; n++) {
    const base = cadence.result(n, n - 1, picture(n) === picture(n - 1));
    if (base !== null) left.push([n, base]);
  }
  return left;
}

const film = (n) => Math.floor((n * 24) / 60); // 24 pictures a second in 60 frames: 2-3-2-3
const half = (n) => Math.floor(n / 2);         // 30 in 60
const fifty = (n) => Math.floor((n * 50) / 60);

test('a video with a new picture in every frame is left alone', () => {
  const cadence = new Cadence();
  assert.deepEqual(feed(cadence, (n) => n, 600), []);
  assert.equal(cadence.on, false);
  assert.equal(cadence.delay(1000), 0);
  assert.equal(cadence.at(300), 300);
  assert.equal(cadence.share(), 1);
});

test('24 pictures a second in 60 frames: the copies are found, each with the frame it copies', () => {
  const cadence = new Cadence();
  const left = feed(cadence, film, 240);
  assert.equal(cadence.on, true);
  assert.equal(cadence.maxRun, 2);
  assert.equal(left.length, 240 - film(240) + film(0)); // every frame that is not a new picture
  for (const [n, base] of left) {
    assert.equal(film(n), film(base), `frame ${n} copies ${base}`);
    assert.notEqual(film(base), film(base - 1), `${base} is where that picture first came`);
  }
});

test('24 in 60: the new pictures are shown evenly spaced, 2.5 frames apart', () => {
  const cadence = new Cadence();
  feed(cadence, film, 240);
  assert.ok(cadence.fit, 'a steady pace was found');
  assert.ok(Math.abs(cadence.fit.slope - 2.5) < 0.03, `slope ${cadence.fit.slope}`);
  assert.ok(Math.abs(cadence.share() - 0.4) < 0.005);
  const places = cadence.uniques.map((index) => cadence.at(index));
  for (let k = 1; k < places.length; k++) {
    assert.ok(Math.abs(places[k] - places[k - 1] - 2.5) < 0.03, `places ${places}`);
  }
  // never far from where the frame really came
  for (const index of cadence.uniques) assert.ok(Math.abs(cadence.at(index) - index) <= 0.6);
});

test('30 in 60 and 50 in 60 turn it on too', () => {
  const thirty = new Cadence();
  feed(thirty, half, 240);
  assert.equal(thirty.on, true);
  assert.equal(thirty.maxRun, 1);
  assert.ok(Math.abs(thirty.fit.slope - 2) < 0.03);
  const pal = new Cadence();
  feed(pal, fifty, 240);
  assert.equal(pal.on, true);
  assert.equal(pal.maxRun, 1);
});

test('a still picture keeps being refreshed: every third frame stays', () => {
  const cadence = new Cadence();
  const left = feed(cadence, () => 7, 120);
  const gone = new Set(left.map(([n]) => n));
  for (let n = 4; n < 118; n++) {
    assert.ok(!(gone.has(n) && gone.has(n + 1) && gone.has(n + 2)), `three in a row left at ${n}`);
  }
});

test('the delay grows gently while copies come and is given back when they stop', () => {
  const cadence = new Cadence();
  feed(cadence, film, 120);
  let now = 0;
  assert.equal(cadence.delay(now), 0);
  assert.equal(cadence.active, false, 'copies stay until the delay has grown');
  let last = 0;
  for (let i = 0; i < 300; i++) {
    now += 1000 / 144;
    const extra = cadence.delay(now);
    assert.ok(extra - last <= 1.5 / 144 + 1e-9, 'no jump');
    last = extra;
  }
  assert.ok(Math.abs(last - 2.5) < 1e-6, `two copies in a row and half a frame: ${last}`);
  assert.equal(cadence.active, true);
  feed(cadence, (n) => n, 240, 121); // the video goes on with a new picture in every frame
  assert.equal(cadence.on, false);
  for (let i = 0; i < 300; i++) { now += 1000 / 144; last = cadence.delay(now); }
  assert.equal(last, 0);
  assert.equal(cadence.active, false);
});

test('an uneven pace is shown as it comes', () => {
  const cadence = new Cadence();
  // copies here and there, in no pattern
  const stutter = (n) => n - Math.floor(n / 7) - Math.floor(n / 11) - 2 * Math.floor(n / 13);
  feed(cadence, stutter, 300);
  assert.equal(cadence.on, true);
  for (const index of cadence.uniques) {
    const place = cadence.at(index);
    assert.ok(place === index || Math.abs(place - index) <= 0.6);
  }
});

test('after a jump in the video the frame numbers start again', () => {
  const cadence = new Cadence();
  feed(cadence, film, 240);
  cadence.forget();
  assert.equal(cadence.fit, null);
  assert.equal(cadence.on, true, 'what kind of video it is stays known');
  assert.equal(cadence.at(10), 10);
});
