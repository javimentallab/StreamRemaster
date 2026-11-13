// Writes the WGSL the extension generates for an interpolation model file, the order it runs it in
// and the present shader, so verify_fi.py can run exactly that.
//
// Usage: node dump-fi-shaders.mjs <model.fimodel> <shaders.json>
import { readFileSync, writeFileSync } from 'node:fs';

await import(new URL('../../extension/shared/framegen-sr.js', import.meta.url).href);
await import(new URL('../../extension/shared/framegen-fi.js', import.meta.url).href);
await import(new URL('../../extension/shared/framegen.js', import.meta.url).href);
const { parseModel, buildShaders, buildPlan } = globalThis.STFramegenFI;
const bytes = readFileSync(process.argv[2]);
const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const model = parseModel(buffer);
const code = buildShaders(model);
writeFileSync(process.argv[3], JSON.stringify({
  shape: model.shape, luma: code.luma, texture: code.texture, plan: buildPlan(code),
  present: globalThis.STFramegen.PRESENT_SHADER,
}));
console.log(`${model.name}: ${JSON.stringify(model.shape)}`);
