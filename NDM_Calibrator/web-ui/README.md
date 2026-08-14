# NDM-Calibrator Web UI Prototype

为《非线性动态模型参数辨识与校准软件 V1.0》(NDM-Calibrator) 设计的高保真、可交互 Web UI 原型。

本项目的目标是建立未来 PySide6 桌面软件的**视觉真值**和交互参考。所有数据均为明确的 mock/synthetic demonstration data，不实现真实参数辨识后端。

## 技术栈

React · TypeScript · Vite · shadcn/ui (风格) · Tailwind CSS · Recharts · TanStack Table · Lucide Icons

## 启动

```bash
npm install
npm run dev
```

浏览器打开 http://localhost:5173 (或终端提示的端口)。

## 构建

```bash
npm run build
npm run lint
```

## 截图

```bash
# 终端 1: 启动 dev server
npm run dev -- --port 5199

# 终端 2: 生成截图
node scripts/screenshots.mjs
```

截图输出到 `screenshots/`。

## 页面

1. Dashboard (项目首页)
2. Data (数据管理)
3. Model (模型定义)
4. Parameters (参数配置)
5. Identification (参数辨识)
6. Calibration (模型校准)
7. Diagnostics (诊断分析)
8. Uncertainty (可信度分析)
9. Export (结果导出)
10. Settings (设置)
11. About (关于)

## 目录结构

```text
src/
├── components/
│   ├── layout/      Topbar / Sidebar
│   ├── navigation/  导航配置
│   ├── metrics/     MetricCard
│   ├── charts/      图表主题 / 系列 token
│   └── common/      Button/Card/Badge/Input/Select/Tabs...
├── pages/           11 个页面
├── data/mock/       固定 mock 数据
├── lib/             cn() 工具
└── styles/          设计 token (Tailwind @theme)
```

## 文档

- [docs/UI_DESIGN_SYSTEM.md](docs/UI_DESIGN_SYSTEM.md) — 设计系统 (颜色/字体/间距/组件)
- [docs/QT_MAPPING.md](docs/QT_MAPPING.md) — Web → PySide6 移植对照
- [UI_AUDIT.md](UI_AUDIT.md) — 视觉审计
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) — 第三方依赖与许可证
