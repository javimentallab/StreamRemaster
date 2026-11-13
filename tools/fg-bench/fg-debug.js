// Test-only content script, added by youtube.py to its own copy of the build and never packaged.
// The page asks through data-st-fg-cmd and reads data-st-fg-status. It also compares each captured
// frame with the one before: a capture identical to its predecessor is a frame taken twice.
"use strict";

(function () {
  const root = document.documentElement;
  const page = globalThis.STFramegenPage;
  const REGION = { w: 128, h: 72 };
  const BYTES_PER_ROW = 512;
  const free = [];
  const results = new Map();
  let seq = 0;
  let nextToCompare = 0;
  let previous = null;
  let pending = 0;
  let nudging = false;
  const probe = { captures: 0, identical: 0, unread: 0 };

  function compareInOrder() {
    while (results.has(nextToCompare)) {
      const data = results.get(nextToCompare);
      results.delete(nextToCompare);
      nextToCompare++;
      if (data === null) { previous = null; continue; }
      if (previous) {
        probe.captures++;
        let same = true;
        for (let i = 0; i < data.length; i += 4) {
          if (data[i] !== previous[i] || data[i + 1] !== previous[i + 1]) { same = false; break; }
        }
        if (same) probe.identical++;
      }
      previous = data;
    }
  }

  function nudge(device) {
    if (nudging) return;
    nudging = true;
    const again = () => {
      if (pending <= 0) { nudging = false; return; }
      device.queue.submit([]);
      setTimeout(again, 1);
    };
    setTimeout(again, 0);
  }

  page.onCapture = (texture) => {
    const device = page.device();
    const id = seq++;
    if (!free.length && pending < 24) {
      free.push(device.createBuffer({ size: BYTES_PER_ROW * REGION.h, usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ }));
    }
    const buffer = free.pop();
    if (!buffer) { probe.unread++; results.set(id, null); compareInOrder(); return; }
    const origin = [Math.floor((texture.width - REGION.w) / 2), Math.floor((texture.height - REGION.h) / 2)];
    const encoder = device.createCommandEncoder();
    encoder.copyTextureToBuffer({ texture, origin }, { buffer, bytesPerRow: BYTES_PER_ROW }, [REGION.w, REGION.h]);
    device.queue.submit([encoder.finish()]);
    pending++;
    nudge(device);
    buffer.mapAsync(GPUMapMode.READ).then(() => {
      const copy = new Uint8Array(buffer.getMappedRange()).slice();
      buffer.unmap();
      free.push(buffer);
      results.set(id, copy);
    }).catch(() => { results.set(id, null); }).finally(() => { pending--; compareInOrder(); });
  };

  new MutationObserver(() => {
    const raw = root.getAttribute("data-st-fg-cmd");
    if (!raw) return;
    root.removeAttribute("data-st-fg-cmd");
    const command = JSON.parse(raw);
    if (command.cmd === "setup") {
      const models = {};
      if (command.model) models.test = { id: "test", kind: "sr", name: "test", size: 1, data: command.model };
      if (command.interp) models.testfi = { id: "testfi", kind: "fi", name: "test-fi", size: 1, data: command.interp };
      ext.storage.local.set({ fgModels: models })
        .then(() => ST.setSettings({
          fgResolution: command.resolution, fgModel: command.model ? "test" : "", fgInterpModel: command.interp ? "testfi" : "",
        }))
        .then(() => root.setAttribute("data-st-fg-setup", "done"));
    }
    if (command.cmd === "start") page.start(command.target);
    if (command.cmd === "target") page.setTarget(command.target);
    if (command.cmd === "stop") page.stop();
  }).observe(root, { attributes: true, attributeFilter: ["data-st-fg-cmd"] });

  setInterval(() => {
    root.setAttribute("data-st-fg-status", JSON.stringify(Object.assign(page.status(), { probe })));
  }, 250);
})();
