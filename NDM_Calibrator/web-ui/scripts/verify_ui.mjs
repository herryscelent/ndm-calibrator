import { chromium } from "playwright";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

const checks = [
  ["dashboard", ["项目首页", "工作流程", "实测值与模拟值", "样本数"]],
  ["data", ["数据管理", "字段映射", "数据预览", "position"]],
  ["model", ["模型定义", "模型结构", "方程编辑", "模型有效"]],
  ["parameters", ["参数配置", "参数", "状态", "k", "c", "m"]],
  ["identification", ["参数辨识", "算法选择", "最小二乘", "开始辨识"]],
  ["calibration", ["模型校准", "RMSE", "实测 vs 模拟", "参数结果"]],
  ["diagnostics", ["诊断分析", "残差", "敏感度", "可辨识性"]],
  ["uncertainty", ["可信度分析", "多起点分析", "Bootstrap"]],
  ["export", ["结果导出", "导出内容", "格式", "导出结果"]],
];

let failures = 0;
for (const [route, keywords] of checks) {
  await page.goto(`http://localhost:5199/#${route}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);
  const body = await page.textContent("body");
  for (const kw of keywords) {
    if (!body.includes(kw)) {
      console.log(`MISSING [${route}]: ${kw}`);
      failures++;
    }
  }
}
console.log(failures === 0 ? "ALL CONTENT PRESENT" : `${failures} missing keywords`);
await browser.close();
