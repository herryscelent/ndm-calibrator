# Third-Party Notices — NDM-Calibrator Web UI Prototype

本项目使用以下开源依赖。所有依赖均为开源 (MIT / Apache-2.0 / BSD) 许可证，无收费或来源不明 package。

## 核心运行时依赖

| Package | 版本 | 用途 | 许可证 |
| --- | --- | --- | --- |
| react | 19.2.8 | UI 框架 | MIT |
| react-dom | 19.2.8 | DOM 渲染 | MIT |
| recharts | 3.10.1 | 图表 | MIT |
| @tanstack/react-table | 8.21.3 | 数据表格 | MIT |
| lucide-react | 1.31.0 | 图标 | ISC |
| class-variance-authority | 0.7.1 | 组件变体 | Apache-2.0 |
| clsx | 2.1.1 | class 合并 | MIT |
| tailwind-merge | 3.6.0 | Tailwind class 合并 | MIT |

## UI 基础组件 (Radix UI)

| Package | 版本 | 许可证 |
| --- | --- | --- |
| @radix-ui/react-checkbox | 1.3.11 | MIT |
| @radix-ui/react-collapsible | 1.1.20 | MIT |
| @radix-ui/react-dialog | 1.1.23 | MIT |
| @radix-ui/react-dropdown-menu | 2.1.24 | MIT |
| @radix-ui/react-label | 2.1.15 | MIT |
| @radix-ui/react-progress | 1.1.16 | MIT |
| @radix-ui/react-scroll-area | 1.2.18 | MIT |
| @radix-ui/react-select | 2.3.7 | MIT |
| @radix-ui/react-separator | 1.1.15 | MIT |
| @radix-ui/react-tabs | 1.1.21 | MIT |
| @radix-ui/react-tooltip | 1.2.16 | MIT |

## 构建工具链

| Package | 版本 | 许可证 |
| --- | --- | --- |
| vite | 8.2.1 | MIT |
| @vitejs/plugin-react | 6.0.5 | MIT |
| typescript | 6.0.3 | Apache-2.0 |
| tailwindcss | 4.3.3 | MIT |
| @tailwindcss/vite | 4.3.3 | MIT |
| oxlint | 1.78.0 | MIT |
| playwright | 1.62.1 | Apache-2.0 (仅开发/截图) |

## 说明

- 本 Prototype 未使用 shadcn CLI 拉取模板；组件 API 遵循 shadcn/ui 风格, 由项目自行实现, 无第三方收费 blocks 或付费模板。
- 所有依赖经 `npm ls` 审计, 无已知漏洞。
