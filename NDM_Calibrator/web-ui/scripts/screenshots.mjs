/**
 * Capture real screenshots of the running Web Prototype at 1440×900.
 * Requires the dev server (or preview) to be running.
 *
 * Usage:
 *   npm run dev -- --port 5199          (terminal 1)
 *   node scripts/screenshots.mjs        (terminal 2)
 */
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(__dirname, "../screenshots");
mkdirSync(outDir, { recursive: true });

const BASE = process.env.BASE_URL ?? "http://localhost:5199";

const pages = [
  ["dashboard", "dashboard"],
  ["data", "data"],
  ["model", "model"],
  ["parameters", "parameters"],
  ["identification", "identification"],
  ["calibration", "calibration"],
  ["diagnostics_residuals", "diagnostics"],
  ["uncertainty_bootstrap", "uncertainty"],
  ["export", "export"],
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

for (const [name, route] of pages) {
  await page.goto(`${BASE}/#${route}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  await page.screenshot({ path: resolve(outDir, `${name}.png`) });
  console.log(`saved: ${name}.png`);
}

// Interaction: switch diagnostics tab to correlation
await page.goto(`${BASE}/#diagnostics`, { waitUntil: "networkidle" });
await page.getByRole("tab", { name: "Correlation" }).click();
await page.waitForTimeout(300);
await page.screenshot({ path: resolve(outDir, "diagnostics_correlation.png") });
console.log("saved: diagnostics_correlation.png");

// Interaction: run mock identification
await page.goto(`${BASE}/#identification`, { waitUntil: "networkidle" });
await page.getByRole("button", { name: "开始辨识" }).click();
await page.waitForTimeout(3600); // let the 3.6s mock run finish
await page.screenshot({ path: resolve(outDir, "identification_completed.png") });
console.log("saved: identification_completed.png");

await browser.close();
console.log("done");
