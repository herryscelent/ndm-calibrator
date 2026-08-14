import { chromium } from "playwright";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto("http://localhost:5199/#dashboard", { waitUntil: "networkidle" });
await page.waitForTimeout(400);

// Sidebar width
const sidebar = await page.locator("aside").boundingBox();
console.log("sidebar width:", sidebar?.width);

// Topbar height
const header = await page.locator("header").boundingBox();
console.log("topbar height:", header?.height);

// Check accent color present on active nav
const activeBg = await page.locator("aside button").first().evaluate(el => getComputedStyle(el).backgroundColor);
console.log("active nav bg:", activeBg);

// Check sidebar background
const sidebarBg = await page.locator("aside").evaluate(el => getComputedStyle(el).backgroundColor);
console.log("sidebar bg:", sidebarBg);

// Check main content has padding
const main = await page.locator("main").evaluate(el => getComputedStyle(el).padding);
console.log("main padding:", main);

await browser.close();
