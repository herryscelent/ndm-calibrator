# UI Design System — NDM-Calibrator Web UI Prototype

本文档是 Web UI 原型的视觉真值，后续将用于 PySide6 桌面软件复刻。

## 设计原则

- **现代，但不娱乐化** — 工程数值分析软件的克制外观；
- **漂亮，但不是营销网站** — 无渐变、无霓虹、无 3D；
- **信息密度较高，但不拥挤** — compact engineering interface；
- **以图表、参数表格和工程工作流为核心**；
- **单一主 Accent**，无彩虹配色。

## Color (语义色)

| Token | 值 | 用途 |
| --- | --- | --- |
| `background` | `#F5F7FA` | 主背景 |
| `sidebar` | `#F1F4F8` | 侧边栏背景 |
| `topbar` | `#FFFFFF` | 顶部栏背景 |
| `surface` | `#FFFFFF` | 卡片/面板 |
| `surface-secondary` | `#F8FAFC` | 次要面板/表头 |
| `surface-hover` | `#EDF2F7` | hover 态 |
| `surface-selected` | `#E8F1FF` | active/选中态 |
| `border` | `#DDE3EA` | 边框 |
| `border-strong` | `#C9D2DC` | 强边框 |
| `text-primary` | `#20252B` | 主文本 |
| `text-secondary` | `#687482` | 次要文本 |
| `text-muted` | `#929CAA` | 弱文本 |
| `text-disabled` | `#B4BCC5` | 禁用 |
| `accent` | `#356FE5` | 主强调色 |
| `accent-hover` | `#285FCB` | 强调色 hover |
| `accent-subtle` | `#E7F0FF` | 强调色浅底 |
| `success` | `#27875A` | 成功 |
| `warning` | `#B7791F` | 警告 |
| `danger` | `#C94A4A` | 危险 |
| `info` | `#356FE5` | 信息 |

## Chart Series

| Token | 值 | 用途 |
| --- | --- | --- |
| `measured` | `#356FE5` | 实测数据线 |
| `simulated` | `#C0613F` | 模拟数据线 |
| `residual` | `#B7791F` | 残差 |
| `sensitivity` | `#687482` | 敏感度柱 |
| `bootstrap` | `#27875A` | bootstrap 分布 |
| `grid` | `#E6EBF1` | 图表网格 |

## Typography

字体：`Segoe UI` → `system-ui` → `sans-serif`（无商业字体依赖）。
等宽：`Cascadia Mono` → `Consolas`。

| 用途 | 字号 |
| --- | --- |
| Page title | 22px |
| Section title | 15px |
| Body | 14px |
| Table | 13px |
| Secondary / caption | 13px / 12px |
| Metric value | 24px |

## Spacing

`4 / 8 / 12 / 16 / 20 / 24 / 32`（Tailwind 默认 scale）。

- 页面左右 padding：`28px`
- Card 内部：`20px`
- Section 间距：`20px`

## Radius

| 级别 | 值 |
| --- | --- |
| small | 6px |
| medium | 8px |
| large | 10px |

禁止 20px+ 大圆角。

## Layout

| 区域 | 值 |
| --- | --- |
| Topbar 高 | 48px |
| Sidebar 展开宽 | 220px |
| Sidebar 折叠宽 | 68px |
| 基准 viewport | 1440×900 |
| 最低 | 1366×768 |

## Components

### Buttons

- Primary：`bg-accent` 白字，圆角 6px，高 36px；
- Secondary：`bg-surface-secondary` + border；
- Ghost：透明 + hover 浅底；
- Danger：红字 + 红边框（仅删除/取消）。

### Tables

- 紧凑行高，浅色表头 (`surface-secondary`)；
- 数字右对齐（`tabular-nums`）；
- 细分隔线，hover 浅底。

### Cards

仅用于 KPI / 少量 Summary / 独立结果面板。大图表、主表格、Tabs 不套 Card。

### Badge

状态语义：success / warning / danger / neutral / running / info。

### Tabs

segmented 样式：`surface-secondary` 容器 + 白色 active 项。

## Charts

- 统一 series token（见上）；
- thin grid、clean axis、subtle tooltip、minimal legend；
- 无渐变、无 3D、无霓虹。

## Theme

当前仅 Light。代码层已用 `@theme` 集中管理 token，Dark 派生时不改结构。
