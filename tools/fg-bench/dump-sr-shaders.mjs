// Writes the WGSL the extension generates for a model file, so verify_sr.py can run exactly that.
//
// Usage: node dump-sr-shaders.mjs <model.srmodel> <shaders.json>
import { readFileSync, writeFileSync } from 'node:fs';

await import(new URL('../../extension/shared/framegen-sr.js', import.meta.url).href);
const bytes = readFileSync(process.argv[2]);
const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const model = globalThis.STFramegenSR.parseModel(buffer);
writeFileSync(process.argv[3], JSON.stringify({ channels: model.channels, blocks: model.blocks, shaders: globalThis.STFramegenSR.buildShaders(model) }));
console.log(`${model.name}: ${model.channels} channels, ${model.blocks} blocks`);
