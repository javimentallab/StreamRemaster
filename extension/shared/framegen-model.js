// The smooth video tab has a single model choice. A combined file ("SFM1") carries both networks:
// "SFM1", the length of a JSON header, the header padded to four bytes ({"format": 1, "name",
// "sr": bytes, "fi": bytes}), then a whole .srmodel file and a whole .fimodel file, in that order,
// with the byte lengths the header gives (0 for a part that is not there). A lone .srmodel or
// .fimodel is still accepted: it is a model with only that part.
"use strict";

(function (root) {
  const MAGIC = 0x314d4653; // "SFM1"
  const MAX_MODEL_BYTES = 16 * 1024 * 1024;

  const bad = (why) => new Error(`invalid model file: ${why}`);

  // "st" (combined), "sr", "fi" or null, from the first four bytes.
  function kindOf(buffer) {
    if (!(buffer instanceof ArrayBuffer) || buffer.byteLength < 4) return null;
    const magic = new DataView(buffer).getUint32(0, true);
    if (magic === MAGIC) return "st";
    return root.STFramegenFI.kindOf(buffer);
  }

  // { kind, name, sr, fi }: sr and fi are what STFramegenSR / STFramegenFI.parseModel give, or null.
  function parse(buffer) {
    const kind = kindOf(buffer);
    if (kind === "sr") {
      const sr = root.STFramegenSR.parseModel(buffer);
      return { kind, name: sr.name, sr, fi: null };
    }
    if (kind === "fi") {
      const fi = root.STFramegenFI.parseModel(buffer);
      return { kind, name: fi.name, sr: null, fi };
    }
    if (kind !== "st") throw bad("magic");
    if (buffer.byteLength < 8 || buffer.byteLength > MAX_MODEL_BYTES) throw bad("size");
    const view = new DataView(buffer);
    const headerLength = view.getUint32(4, true);
    if (headerLength > buffer.byteLength - 8) throw bad("header length");
    let header;
    try {
      header = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 8, headerLength)));
    } catch (e) {
      throw bad("header");
    }
    const { format, name, sr: srBytes, fi: fiBytes } = header || {};
    if (format !== 1) throw bad("format");
    for (const n of [srBytes, fiBytes]) if (!Number.isInteger(n) || n < 0) throw bad("part length");
    if (!srBytes && !fiBytes) throw bad("empty");
    const start = 8 + headerLength + ((4 - (headerLength % 4)) % 4);
    if (buffer.byteLength !== start + srBytes + fiBytes) throw bad("parts length");
    const sr = srBytes ? root.STFramegenSR.parseModel(buffer.slice(start, start + srBytes)) : null;
    const fi = fiBytes ? root.STFramegenFI.parseModel(buffer.slice(start + srBytes)) : null;
    return { kind, name: String(name || "model").slice(0, 80), sr, fi };
  }

  root.STFramegenModel = { kindOf, parse, MAX_MODEL_BYTES };
})(globalThis);
