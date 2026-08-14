import { chromium } from "playwright";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
for (const route of ["dashboard","data","model","parameters","identification","calibration","diagnostics","uncertainty","export"]) {
  await page.goto(`http://localhost:5199/#${route}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);
  const h1 = await page.locator("h1").first().textContent().catch(() => "(none)");
  console.log(`${route} -> h1: ${h1}`);
}
await browser.close();
