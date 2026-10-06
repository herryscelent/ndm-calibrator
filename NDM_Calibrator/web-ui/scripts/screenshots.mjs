/**
 * Capture screenshots of the running Web Prototype at desktop and mobile sizes.
 * Requires the dev server (or preview) to be running.
 *
 * Usage:
 *   npm run dev -- --port 5199          (terminal 1)
 *   node scripts/screenshots.mjs        (terminal 2)
 *
 * BASE_URL can be used to point the script at another server. Desktop files keep
 * the historical names; mobile captures are written with a `_mobile` suffix.
 */
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(__dirname, process.env.SCREENSHOT_DIR ?? "../screenshots");
mkdirSync(outDir, { recursive: true });

const BASE = (process.env.BASE_URL ?? "http://localhost:5199").replace(/\/$/, "");
const WAIT_TIMEOUT = Number(process.env.SCREENSHOT_TIMEOUT ?? 10_000);
const STABLE_MS = Number(process.env.SCREENSHOT_STABLE_MS ?? 220);
const CHART_SETTLE_MS = Number(process.env.SCREENSHOT_CHART_SETTLE_MS ?? 1_800);

const viewports = [
  { key: "desktop", width: 1440, height: 900 },
  { key: "mobile", width: 390, height: 844 },
];

const pages = [
  { name: "dashboard", route: "dashboard", text: "项目首页", charts: 1, marks: 1 },
  { name: "data", route: "data", text: "数据管理", charts: 1, marks: 1, rows: 1 },
  { name: "model", route: "model", text: "模型定义" },
  { name: "parameters", route: "parameters", text: "参数配置", rows: 1 },
  { name: "identification", route: "identification", text: "参数辨识", charts: 1 },
  { name: "calibration", route: "calibration", text: "模型校准", charts: 1, marks: 1, rows: 1 },
  { name: "diagnostics_residuals", route: "diagnostics", text: "诊断分析", charts: 2, marks: 1 },
  { name: "uncertainty", route: "uncertainty", text: "可信度分析", charts: 1, marks: 1 },
  { name: "export", route: "export", text: "结果导出" },
];

function outputName(name, viewport) {
  return viewport.key === "desktop" ? `${name}.png` : `${name}_mobile.png`;
}

async function gotoRoute(page, route) {
  // domcontentloaded is deterministic even when a dev server keeps a HMR socket open.
  await page.goto(`${BASE}/#${route}`, { waitUntil: "domcontentloaded" });
  await page.locator("main").waitFor({ state: "visible", timeout: WAIT_TIMEOUT });
}

async function waitForText(page, text) {
  await page.waitForFunction(
    (expected) => {
      const main = document.querySelector("main");
      return Boolean(main && main.innerText.includes(expected));
    },
    text,
    { polling: 50, timeout: WAIT_TIMEOUT }
  );
}

async function waitForRows(page, minRows) {
  if (!minRows) return;
  await page.waitForFunction(
    (minimum) => document.querySelectorAll("main table tbody tr").length >= minimum,
    minRows,
    { polling: 50, timeout: WAIT_TIMEOUT }
  );
}

async function waitForCharts(page, { minCharts = 0, minMarks = 0 } = {}) {
  if (!minCharts && !minMarks) return;
  await page.waitForFunction(
    ({ minimumCharts, minimumMarks }) => {
      const isVisible = (element) => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.display !== "none" && style.visibility !== "hidden" && rect.width > 4 && rect.height > 4;
      };
      const charts = [...document.querySelectorAll("main .recharts-wrapper")].filter(isVisible);
      const marks = [
        ...document.querySelectorAll(
          "main .recharts-line-curve, main .recharts-bar-rectangle, main .recharts-area-area, main .recharts-scatter-symbol, main .recharts-pie-sector"
        ),
      ].filter(isVisible);
      return charts.length >= minimumCharts && marks.length >= minimumMarks && charts.every((chart) => {
        const surface = chart.querySelector("svg.recharts-surface");
        if (!surface) return false;
        const rect = surface.getBoundingClientRect();
        return rect.width > 4 && rect.height > 4;
      });
    },
    { minimumCharts: minCharts, minimumMarks: minMarks },
    { polling: 50, timeout: WAIT_TIMEOUT }
  );
}

async function waitForVisualStability(page, stableMs = STABLE_MS) {
  // Recharts changes SVG attributes while animating. Wait for the rendered geometry
  // and visible control bounds to remain unchanged for a short continuous interval.
  await page.evaluate(() => {
    delete globalThis.__screenshotVisualState;
  });
  await page.waitForFunction(
    (requiredStableMs) => {
      const isVisible = (element) => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
      };
      const nodes = [
        ...document.querySelectorAll(
          "main .recharts-wrapper, main .recharts-wrapper svg, main .recharts-wrapper path, main .recharts-wrapper rect, main button, main input, main select, main [role='tab'], main [role='combobox'], main table"
        ),
      ].filter(isVisible);
      const signature = nodes
        .map((node) => {
          const rect = node.getBoundingClientRect();
          const geometry = [rect.x, rect.y, rect.width, rect.height].map((value) => Math.round(value * 10) / 10).join(",");
          const attributes = ["d", "transform", "x", "y", "width", "height", "clip-path", "style"]
            .map((name) => `${name}=${node.getAttribute(name) ?? ""}`)
            .join(";");
          return `${node.tagName}:${geometry}:${attributes.slice(0, 360)}`;
        })
        .join("|");
      const now = performance.now();
      const previous = globalThis.__screenshotVisualState;
      if (!previous || previous.signature !== signature) {
        globalThis.__screenshotVisualState = { signature, since: now };
        return false;
      }
      return now - previous.since >= requiredStableMs;
    },
    stableMs,
    { polling: 50, timeout: WAIT_TIMEOUT }
  );
}

async function waitForPageReady(page, options = {}) {
  const { text, charts = 0, marks = 0, rows = 0, stableMs = STABLE_MS } = options;
  await page.evaluate(async () => {
    if (document.fonts?.ready) await document.fonts.ready;
  });
  if (text) await waitForText(page, text);
  await waitForRows(page, rows);
  await waitForCharts(page, { minCharts: charts, minMarks: marks });
  // Recharts line drawing uses a clip animation whose path geometry can already
  // be stable while the visible series is still incomplete. Keep an explicit
  // settling floor, then require a stable rendered signature before capture.
  if (charts || marks) await page.waitForTimeout(CHART_SETTLE_MS);
  await waitForVisualStability(page, stableMs);
}

async function assertLayout(page, label) {
  const findings = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const issues = [];
    const isVisible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
    };
    const hasHorizontalScroller = (element) => {
      let current = element.parentElement;
      while (current) {
        const overflowX = getComputedStyle(current).overflowX;
        if (overflowX === "auto" || overflowX === "scroll") return true;
        current = current.parentElement;
      }
      return false;
    };

    if (document.documentElement.scrollWidth > viewportWidth + 1) {
      issues.push(`document scrollWidth ${document.documentElement.scrollWidth} > viewport ${viewportWidth}`);
    }

    for (const element of document.querySelectorAll("body *")) {
      if (!isVisible(element) || hasHorizontalScroller(element)) continue;
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      if ((style.position === "fixed" || style.position === "sticky") && (rect.left < -1 || rect.right > viewportWidth + 1)) {
        issues.push(`${element.tagName.toLowerCase()} escapes viewport (${Math.round(rect.left)}, ${Math.round(rect.right)})`);
      }
      if (element.matches("main button, main input, main select, main textarea, main [role='tab'], main [role='combobox']") && (rect.left < -1 || rect.right > viewportWidth + 1)) {
        issues.push(`interactive ${element.tagName.toLowerCase()} escapes viewport (${Math.round(rect.left)}, ${Math.round(rect.right)})`);
      }
    }

    const controls = [...document.querySelectorAll("main button, main input, main select, main textarea, main [role='tab'], main [role='combobox']")].filter(isVisible);
    for (let i = 0; i < controls.length; i += 1) {
      const first = controls[i];
      const firstRect = first.getBoundingClientRect();
      const centerInViewport = firstRect.bottom > 0 && firstRect.top < window.innerHeight;
      const inHorizontalScroller = hasHorizontalScroller(first);
      const fullyInViewport = firstRect.left >= -1 && firstRect.right <= viewportWidth + 1;
      if (centerInViewport && fullyInViewport && !inHorizontalScroller && !first.matches(":disabled, [aria-disabled='true']")) {
        const centerX = Math.max(0, Math.min(viewportWidth - 1, firstRect.left + firstRect.width / 2));
        const centerY = Math.max(0, Math.min(window.innerHeight - 1, firstRect.top + firstRect.height / 2));
        const topAtCenter = document.elementFromPoint(centerX, centerY);
        if (topAtCenter && topAtCenter !== first && !first.contains(topAtCenter)) {
          const topControl = topAtCenter.closest("button, input, select, textarea, [role='tab'], [role='combobox']");
          if (!topControl || topControl !== first) {
            issues.push(`interactive occluded at center: ${first.tagName.toLowerCase()}`);
          }
        }
      }
      for (let j = i + 1; j < controls.length; j += 1) {
        const second = controls[j];
        if (first.contains(second) || second.contains(first)) continue;
        const secondRect = second.getBoundingClientRect();
        const overlapWidth = Math.min(firstRect.right, secondRect.right) - Math.max(firstRect.left, secondRect.left);
        const overlapHeight = Math.min(firstRect.bottom, secondRect.bottom) - Math.max(firstRect.top, secondRect.top);
        if (overlapWidth > 2 && overlapHeight > 2) {
          issues.push(`interactive overlap: ${first.tagName.toLowerCase()} / ${second.tagName.toLowerCase()}`);
        }
      }
    }

    for (const chart of document.querySelectorAll("main .recharts-wrapper")) {
      if (!isVisible(chart)) continue;
      const rect = chart.getBoundingClientRect();
      if (rect.width < 20 || rect.height < 20) issues.push("chart has an unexpectedly small bounding box");
    }
    return [...new Set(issues)];
  });

  if (findings.length) {
    throw new Error(`Layout assertion failed for ${label}:\n- ${findings.join("\n- ")}`);
  }
}

async function capture(page, name, viewport, readyOptions = {}) {
  await waitForPageReady(page, readyOptions);
  await assertLayout(page, `${name} (${viewport.key})`);
  const fileName = outputName(name, viewport);
  await page.screenshot({ path: resolve(outDir, fileName) });
  console.log(`saved: ${fileName}`);
}

async function captureDiagnosticsTabs(page, viewport) {
  await gotoRoute(page, "diagnostics");
  await waitForPageReady(page, { text: "诊断分析", charts: 2, marks: 1 });

  await page.getByRole("tab", { name: "敏感度", exact: true }).click();
  await waitForPageReady(page, { text: "归一化敏感度", charts: 1, marks: 1, rows: 1 });
  await capture(page, "diagnostics_sensitivity", viewport, { charts: 1, marks: 1, rows: 1 });

  await page.getByRole("tab", { name: "相关性", exact: true }).click();
  await waitForPageReady(page, { text: "最高参数相关性" });
  await capture(page, "diagnostics_correlation", viewport, { text: "最高参数相关性" });
}

async function captureUncertaintyBootstrap(page, viewport) {
  await gotoRoute(page, "uncertainty");
  await page.getByRole("tab", { name: "Bootstrap", exact: true }).click();
  await waitForPageReady(page, { text: "Bootstrap 样本数", charts: 1, marks: 1, rows: 1 });
  await capture(page, "uncertainty_bootstrap", viewport, { text: "Bootstrap 样本数", charts: 1, marks: 1, rows: 1 });
}

async function captureIdentificationStates(page, viewport) {
  await gotoRoute(page, "identification");
  await page.getByRole("button", { name: "高级设置", exact: true }).click();
  await waitForPageReady(page, { text: "rtol", charts: 1 });
  await capture(page, "identification_advanced", viewport, { text: "rtol", charts: 1 });

  await page.getByRole("button", { name: "开始辨识", exact: true }).click();
  await waitForText(page, "运行中");
  await page.locator('[role="progressbar"]').waitFor({ state: "visible", timeout: WAIT_TIMEOUT });
  // The first convergence point is asynchronous; wait for it instead of sleeping a fixed duration.
  await waitForCharts(page, { minCharts: 1, minMarks: 1 });
  await capture(page, "identification_running", viewport, { text: "运行中", charts: 1, marks: 1, stableMs: 120 });

  await waitForText(page, "已完成");
  await waitForText(page, "最佳参数:");
  await capture(page, "identification_completed", viewport, { text: "最佳参数:", charts: 1, marks: 1 });
}

async function captureExportResult(page, viewport) {
  await gotoRoute(page, "export");
  await page.getByRole("button", { name: "导出结果", exact: true }).click();
  await waitForText(page, "导出完成");
  await capture(page, "export_result", viewport, { text: "导出完成" });
}

const browser = await chromium.launch();
try {
  for (const viewport of viewports) {
    const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height } });
    const page = await context.newPage();
    try {
      for (const definition of pages) {
        await gotoRoute(page, definition.route);
        await capture(page, definition.name, viewport, definition);
      }
      await captureDiagnosticsTabs(page, viewport);
      await captureUncertaintyBootstrap(page, viewport);
      await captureIdentificationStates(page, viewport);
      await captureExportResult(page, viewport);
    } finally {
      await context.close();
    }
  }
} finally {
  await browser.close();
}
console.log("done");
