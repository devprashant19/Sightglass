#!/usr/bin/env node
// Regenerates the screenshots in this folder from the built site.
//
//   cd web && npm run build && npx vite preview --port 4300 --strictPort    (leave running)
//   node docs/screenshots/capture.mjs                                       (from the repo root)
//
// It drives a headless Chromium over the DevTools protocol in real time, because the page's reveal
// animations never finish under --screenshot's virtual time. Needs Node 22 (global WebSocket) and
// Chrome, Edge or Chromium; set BROWSER to its path if it is not found. Do not run the API while
// capturing: the images show the precomputed mode a visitor to the static site sees.
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const spec = JSON.parse(readFileSync(join(here, "shots.json"), "utf8"));
const candidates = [
  process.env.BROWSER,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
].filter(Boolean);
const browser = candidates.find((p) => existsSync(p));
if (!browser) {
  console.error("No Chromium found. Set BROWSER to one.");
  process.exit(2);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const port = 9333;
const profile = mkdtempSync(join(tmpdir(), "sightglass-shots-"));
const proc = spawn(browser, ["--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars", `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });

let pages = null;
for (let i = 0; i < 50 && !pages; i++) {
  await sleep(200);
  pages = await fetch(`http://127.0.0.1:${port}/json/list`).then((r) => r.json()).catch(() => null);
}
const ws = new WebSocket(pages.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0;
const waiting = new Map();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && waiting.has(m.id)) {
    waiting.get(m.id)(m);
    waiting.delete(m.id);
  }
});
const send = (method, params = {}) => new Promise((r) => { const n = ++id; waiting.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });

await send("Page.enable");
for (const s of spec.shots) {
  await send("Emulation.setDeviceMetricsOverride", { width: spec.width, height: spec.height, deviceScaleFactor: 1, mobile: false });
  await send("Page.navigate", { url: `${spec.base}${s.path}` });
  await sleep(s.wait ?? 4000);
  if (s.scrollTo) {
    await send("Runtime.evaluate", { expression: `document.querySelector(${JSON.stringify(s.scrollTo)})?.scrollIntoView({block:'start'}); window.scrollBy(0, ${s.offset ?? 0});` });
    await sleep(s.after ?? 3000);
  }
  const shot = await send("Page.captureScreenshot", { format: "png" });
  const out = join(here, `${s.name}.png`);
  writeFileSync(out, Buffer.from(shot.result.data, "base64"));
  console.log(`  ${s.name}.png`);
}
ws.close();
proc.kill();
await sleep(500);
try { rmSync(profile, { recursive: true, force: true }); } catch { /* a temp folder */ }
console.log("Open each image before using it.");
