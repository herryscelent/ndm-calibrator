# NDM-Calibrator Web UI Prototype 开发任务

## 0. 项目目标

为：

**《非线性动态模型参数辨识与校准软件 V1.0》**

设计并实现一套高保真、可交互的 Web UI Prototype。

内部名称：

**NDM-Calibrator**

本项目的唯一目标是：

> 建立未来 PySide6 桌面软件的“视觉真值”和交互参考。

本项目不是最终产品，不实现真实参数辨识后端，不运行 SciPy ODE Solver，不实现真实 Bootstrap，不实现项目文件格式。

所有数据均使用明确标记的 synthetic/mock data。

最终 Web Prototype 应达到：

> 如果把浏览器外框去掉，它看起来已经像一套成熟的工程数值分析软件。

---

# 1. 技术栈冻结

使用：

* React
* TypeScript
* Vite
* shadcn/ui
* Tailwind CSS
* Recharts
* TanStack Table
* Lucide Icons

优先使用：

**shadcn/ui Mira 风格**

如果当前 shadcn CLI 中 Mira 需要通过官方 style 配置指定，则按官方方式初始化。

禁止使用：

* Ant Design
* Material UI
* Bootstrap
* Chakra UI
* QFluentWidgets
* Electron
* Next.js
* Vue
* Angular
* paid templates
* Tailwind Plus
* 第三方收费 shadcn blocks
* 无明确许可证的 UI package

只使用开源依赖。

---

# 2. 本阶段明确不做

不要实现：

* Python backend
* SciPy
* ODE solver
* parameter identification
* real optimization
* real Bootstrap
* real Excel parsing
* database
* authentication
* cloud API
* network API
* WebSocket
* Electron packaging

不要为了“功能完整”把前端原型变成第二套正式软件。

---

# 3. 产品定位

视觉方向：

**Modern engineering desktop software**

参考气质：

* Windows 11 Fluent
* Visual Studio
* MATLAB modern UI
* OriginLab
* modern scientific data applications

但不要直接复制任何产品页面。

最终效果应满足：

**现代，但不是娱乐化。**

**漂亮，但不是营销网站。**

**信息密度较高，但不拥挤。**

**以图表、参数表格和工程工作流为核心。**

---

# 4. 第一阶段只做 Light Theme

当前版本只完成：

[
\boxed{\text{Light Theme}}
]

不要同时开发 Dark Theme。

原因：

先冻结：

* typography
* spacing
* density
* surface hierarchy
* accent
* table
* charts
* page layout

等 Light 视觉验收完成后再派生 Dark。

代码层面可以预留 theme token，但不得因此增加当前开发复杂度。

---

# 5. 色彩方向

不要使用纯白页面 + 大量蓝色 Card。

建立克制的浅色工程主题。

建议初始 tokens：

```text
background              #F5F7FA
sidebar                  #F1F4F8
topbar                   #FFFFFF
surface                  #FFFFFF
surface-secondary        #F8FAFC
surface-hover            #EDF2F7
surface-selected         #E8F1FF

border                   #DDE3EA
border-strong            #C9D2DC

text-primary             #20252B
text-secondary           #687482
text-muted               #929CAA
text-disabled            #B4BCC5

accent                   #356FE5
accent-hover             #285FCB
accent-subtle            #E7F0FF

success                  #27875A
warning                  #B7791F
danger                   #C94A4A
info                     #356FE5
```

允许根据实际视觉结果微调。

但必须坚持：

**单一主 Accent。**

不要：

* 紫蓝渐变
* 彩虹 KPI
* 大量饱和颜色
* 每个模块一种颜色

---

# 6. 字体

优先：

```text
Inter
```

如果不希望增加字体依赖，则使用：

```text
"Segoe UI", system-ui, sans-serif
```

最终必须使用无需额外商业授权的字体方案。

建议：

* Page title：22–24 px
* Section title：15–16 px
* Body：14 px
* Table：13–14 px
* Secondary：13 px
* Metric：26–30 px

不要：

* 超大 40–60 px Dashboard 字体
* 全页面粗体
* “Welcome back”式产品首页

---

# 7. 页面密度

采用：

**compact engineering interface**

而不是典型 SaaS Dashboard 的巨大留白。

基本 spacing：

```text
4
8
12
16
20
24
32
```

页面左右 padding：

约：

```text
24–32 px
```

Card 内部：

约：

```text
16–20 px
```

---

# 8. 圆角

控制：

```text
small    6 px
medium   8 px
large    10–12 px
```

禁止大量：

```text
20 px+
```

圆角。

---

# 9. 整体布局

Desktop first。

设计基准：

```text
1440 × 900
```

同时保证：

```text
1366 × 768
```

仍然可用。

布局：

```text
┌────────────────────────────────────────────────────────────┐
│ Topbar                                                     │
├──────────────┬─────────────────────────────────────────────┤
│              │                                             │
│ Sidebar      │ Main Content                                │
│              │                                             │
│              │                                             │
└──────────────┴─────────────────────────────────────────────┘
```

---

# 10. Sidebar

展开宽度：

```text
220 px
```

折叠宽度：

```text
68 px
```

支持点击折叠。

导航：

```text
项目首页

数据管理
模型定义
参数配置

参数辨识
模型校准

诊断分析
可信度分析

结果导出

----------------

设置
关于
```

使用 Lucide Icons。

禁止 Emoji。

---

# 11. Sidebar 视觉

默认导航项：

* transparent
* secondary text
* no border

Hover：

* surface-hover

Active：

* accent-subtle background
* accent icon
* text-primary
* 左侧 3 px accent indicator

不要做成：

“一排排灰色矩形按钮”。

---

# 12. Topbar

左侧：

```text
NDM Calibrator
```

中间或左侧次要位置：

```text
Second-order Mechanical System
```

状态：

```text
Saved
```

右侧：

* Save icon
* theme placeholder
* Settings
* Help

只保留必要控件。

---

# 13. 全局 Mock Project

整个 Prototype 使用同一套 synthetic project。

项目：

**Second-order Mechanical System Calibration**

数据：

```text
Samples      4860
Inputs       1
Outputs      1
States       2

Free Parameters:
k
c

Fixed:
m = 1.0
```

真实/模拟展示参数：

```text
k estimate = 2.514
c estimate = 0.176
m = 1.000 fixed
```

拟合结果：

```text
RMSE = 0.0418
MAE = 0.0312
R² = 0.9871
Runtime = 3.21 s
```

这些都必须明确属于：

**mock/synthetic demonstration data**

不要宣称是实际算法结果。

---

# 14. 必须实现的页面

共 9 个主要页面：

1. Dashboard
2. Data
3. Model
4. Parameters
5. Identification
6. Calibration
7. Diagnostics
8. Uncertainty
9. Export

另：

10. Settings
11. About

---

# 15. Dashboard

这是视觉重点之一。

Header：

```text
项目首页

查看当前模型、数据、参数辨识结果及整体工作流程。
```

右侧：

```text
[打开项目]
```

或：

```text
[新建项目]
```

但当前 mock project 默认加载。

---

# 16. Dashboard 顶部 Project Summary

不要做巨大 Hero。

使用紧凑的项目概要：

```text
Second-order Mechanical System Calibration

二阶质量—弹簧—阻尼动态模型
Synthetic demonstration project

Last updated: Aug 13, 2026
```

右侧显示：

```text
Ready
```

Status badge。

---

# 17. Dashboard Metric Cards

最多四个：

```text
Samples
4,860

Free Parameters
2

RMSE
0.0418

R²
0.9871
```

Card 应：

* 小
* 紧凑
* white surface
* thin border
* no heavy shadow

不要巨大数字。

---

# 18. Dashboard Workflow

视觉化流程：

```text
Data
 ↓
Model
 ↓
Parameters
 ↓
Identification
 ↓
Calibration
 ↓
Diagnostics
```

当前 mock project：

全部 Completed。

用：

* check icon
* accent
* subtle connecting line

每一步可点击进入对应页面。

---

# 19. Dashboard Main Result Preview

首页右侧或下方展示：

**Measured vs Simulated**

小型预览图。

使用 Recharts LineChart。

Series：

* Measured
* Simulated

不要随机生成每次不同的数据。

将 mock data 写入固定 TypeScript 文件。

---

# 20. Data Page

Header：

```text
数据管理

导入、检查并映射动态系统实验数据。
```

工具栏：

```text
Import CSV
Import Excel
Select Range
Missing Values
Reset
```

按钮可以是 mock interaction。

---

# 21. Data Summary

显示：

```text
4,860 rows
4 columns
0 missing
81 min duration
```

使用 compact summary。

---

# 22. Data Table

使用：

**TanStack Table**

列示例：

```text
time
u
position
velocity
```

展示约 20–30 行。

支持：

* sort
* column visibility
* simple search/filter

无需真正分页几千行。

---

# 23. Column Mapping

右侧或下方：

```text
Column        Role
time          Time
u             Input
position      Output
velocity      State
```

Select 使用 shadcn Select。

---

# 24. Data Plot

显示：

* Input
* Output

用户可切换。

不要塞多个 chart card。

保持图表有足够面积。

---

# 25. Model Page

Header：

```text
模型定义

定义状态方程、输入、参数以及观测输出。
```

采用左右布局。

左侧：

**Model Structure**

```text
States
x1 position
x2 velocity

Input
u force

Parameters
m
c
k

Output
y = x1
```

---

# 26. Equation Editor

右侧：

```text
dx1/dt = x2

dx2/dt =
-(k/m) * x1
-(c/m) * x2
+(1/m) * u

y = x1
```

做成专业 equation/code editor 外观。

使用 monospace。

底部：

```text
✓ Model valid
```

不要真执行模型。

---

# 27. Parameter Page

这是视觉重点。

Header：

```text
参数配置

设置参数初值、搜索边界及固定状态。
```

右侧：

```text
[验证参数]
```

---

# 28. Parameter Table

使用 TanStack Table 或 styled table。

列：

```text
Parameter
Initial
Lower
Upper
Status
Unit
```

Mock：

```text
k     2.0    0.1    10.0    Free    N/m
c     0.2    0.01   3.0     Free    N·s/m
m     1.0     —      —      Fixed   kg
```

支持：

* inline editing appearance
* Free / Fixed
* row selection

上方：

```text
Add
Remove
Reset
```

---

# 29. Parameter Validation

底部显示：

```text
✓ All parameter settings are valid
```

另外准备一个可以交互触发的 error demo：

例如把：

```text
lower > initial
```

则显示：

```text
Initial value must be between lower and upper bounds.
```

纯前端 validation 即可。

---

# 30. Identification Page

Header：

```text
参数辨识

选择求解算法并运行模型参数估计。
```

右侧：

```text
[开始辨识]
```

---

# 31. Algorithm Selector

提供：

* Least Squares
* Nelder-Mead
* Differential Evolution
* Multi-start

用 Tabs / segmented cards。

默认：

```text
Least Squares
```

---

# 32. Algorithm Settings

显示：

```text
Method
TRF

Max evaluations
2000

Tolerance
1e-8

Seed
42
```

Advanced 设置折叠。

---

# 33. Mock Identification Interaction

点击：

```text
开始辨识
```

后模拟：

```text
Ready
→ Running
→ Completed
```

持续约：

2–4 秒。

Running 时动态显示：

```text
Evaluations
318 / 2000

Best Objective
0.0031

Elapsed
1.72 s
```

使用固定 deterministic mock progression。

不要随机。

---

# 34. Convergence Plot

Recharts LineChart。

显示：

```text
Objective vs Evaluations
```

运行过程中可以逐步显示预定义点。

---

# 35. Best Parameters

完成后：

```text
k = 2.514
c = 0.176
```

带：

```text
Completed
```

badge。

---

# 36. Calibration Page

这是整个 Prototype 最重要页面。

Header：

```text
模型校准

比较实验观测与当前辨识模型的拟合结果。
```

---

# 37. Calibration KPI

顶部：

```text
RMSE
0.0418

MAE
0.0312

R²
0.9871

Runtime
3.21 s
```

四张紧凑 metric cards。

---

# 38. Main Calibration Plot

占据页面主要空间。

显示：

```text
Measured
Simulated
```

Recharts。

要求：

* Tooltip
* Legend
* Grid
* Responsive
* meaningful x axis

不要 chart 高度只有 200 px。

建议：

```text
360–430 px
```

---

# 39. Parameter Result Table

下方：

```text
Parameter    Estimate    Initial    Change
k            2.514       2.000      +25.7%
c            0.176       0.200      -12.0%
m            1.000       1.000      Fixed
```

---

# 40. Diagnostics Page

Tabs：

```text
Residuals
Sensitivity
Identifiability
Correlation
```

---

# 41. Residuals

Summary：

```text
Mean        0.0012
Std         0.0417
Max Abs     0.129
ACF Peak    0.087
```

Main chart：

Residual vs Time。

Secondary：

可切换：

```text
Histogram
Residual vs Fitted
```

---

# 42. Sensitivity

水平 Bar Chart：

```text
k
c
```

展示：

Normalized sensitivity。

下面表：

```text
Parameter
Sensitivity
Rank
```

---

# 43. Identifiability

顶部：

```text
Condition Number
31.7

Rank
2 / 2

Min Singular Value
0.184
```

状态：

```text
Good
```

下面 Singular Values chart。

再放一个说明：

```text
No strong local identifiability issue detected in the current mock example.
```

---

# 44. Correlation

Heatmap：

```text
      k       c
k    1.00    0.73
c    0.73    1.00
```

可以自己用 CSS Grid 做，因为只有小矩阵。

下方：

```text
Highest parameter correlation

k ↔ c
0.73
```

---

# 45. Uncertainty Page

Tabs：

```text
Multi-start
Bootstrap
```

---

# 46. Multi-start

顶部：

```text
Starts
20

Successful
20

Success rate
100%

Best RMSE
0.0418
```

绘制参数 distribution。

可以使用：

* scatter
* simple dot distribution
* bar

不要引入额外图表库。

---

# 47. Bootstrap

顶部：

```text
Bootstrap samples
100

Seed
42

Status
Completed
```

表格：

```text
Parameter   Estimate   Median   P2.5    P97.5
k           2.514      2.509    2.41    2.62
c           0.176      0.178    0.15    0.21
```

下方：

Parameter selector：

```text
k
c
```

选择后显示 distribution chart。

---

# 48. Export Page

Header：

```text
结果导出

选择需要包含的分析内容和导出格式。
```

Checkbox：

```text
Project Summary
Parameters
Metrics
Simulation
Residuals
Diagnostics
Bootstrap
```

Formats：

```text
Excel
CSV
HTML Report
PNG Figures
```

Destination：

Mock path field。

按钮：

```text
[导出结果]
```

点击后显示：

```text
Export completed

6 files generated
```

不要真的写文件。

---

# 49. Settings Page

只做 UI。

Appearance：

```text
Light
Dark (Coming later)
System (Coming later)
```

Current：

Light。

UI：

```text
Sidebar
Expanded / Collapsed

Plot Grid
On / Off

Decimal Precision
4
```

---

# 50. About

简单：

```text
NDM Calibrator

非线性动态模型参数辨识与校准软件

Prototype UI
Version 1.0
```

技术：

```text
React
TypeScript
Vite
shadcn/ui
Tailwind CSS
Recharts
TanStack Table
```

不要加入营销性内容。

---

# 51. shadcn 组件优先

尽量复用官方组件：

* Button
* Card
* Table
* Input
* Select
* Tabs
* Tooltip
* Dialog
* Dropdown Menu
* Badge
* Separator
* Checkbox
* Progress
* Scroll Area
* Sheet
* Collapsible

不要为了造轮子大量自己实现基础控件。

---

# 52. Card 使用原则

严格禁止“Card Everywhere”。

Card 只用于：

* KPI
* 少量 Summary
* 独立的 compact result panel

以下内容不要强制 Card：

* Page
* 大 Chart
* Main Table
* Section
* Tabs

大图表直接放在页面 Section 内即可。

---

# 53. Chart Style

所有 Recharts 使用统一样式。

必须定义：

```text
measured
simulated
residual
sensitivity
bootstrap
```

系列 token。

不要每个图自己选颜色。

图表：

* thin grid
* clean axis
* subtle tooltip
* minimal legend
* no gradients
* no 3D
* no neon

---

# 54. Table Style

工程风格。

要求：

* compact row height
* light header
* subtle row hover
* numeric alignment
* thin separators

不要：

* 巨大 padding
* 过度圆角
* 每行 Card 化

---

# 55. Icon

统一：

**Lucide**

建议：

```text
LayoutDashboard
Database
FunctionSquare / Sigma
SlidersHorizontal
Play
LineChart
Activity
ShieldCheck
Download
Settings
Info
```

如果某个 icon 名在当前 Lucide 中不存在，选择含义最接近的现有 icon。

不要为了遵循示例而造成 build failure。

---

# 56. Interaction

Prototype 必须真的可以点击。

至少：

* Sidebar page navigation
* collapse sidebar
* table sorting
* tabs
* algorithm selection
* mock identification
* parameter validation demo
* diagnostics tab
* bootstrap parameter selection
* export mock interaction
* dialog
* tooltip

不能只是静态截图页面。

---

# 57. Toast

使用 shadcn 对应 toast/sonner 方案。

用于：

```text
Project saved
Model validated
Identification completed
Export completed
```

---

# 58. 动画

只允许轻微：

* hover
* opacity
* collapse
* progress

时长：

```text
120–200 ms
```

禁止：

* flying cards
* zoom transitions
* bouncing
* gradient animation

---

# 59. Responsive

主要针对 Desktop。

最低：

```text
1280 px
```

必须正常。

在较窄宽度：

* Sidebar collapsible
* KPI wrap
* two-column section → one-column if needed

不需要专门做手机布局。

---

# 60. Demo Data

统一放在：

```text
src/data/mock/
```

例如：

```text
project.ts
timeSeries.ts
parameters.ts
convergence.ts
residuals.ts
bootstrap.ts
diagnostics.ts
```

不要把几十个数字直接写在 JSX 中。

---

# 61. TypeScript

必须：

* strict mode
* no obvious `any`
* typed mock data
* typed component props

---

# 62. Component Architecture

建议：

```text
src/
├── components/
│   ├── layout/
│   ├── navigation/
│   ├── metrics/
│   ├── charts/
│   ├── tables/
│   └── common/
│
├── pages/
├── data/mock/
├── hooks/
├── lib/
├── styles/
└── types/
```

不要所有页面写到：

```text
App.tsx
```

---

# 63. Design Tokens

所有核心视觉参数集中管理。

至少包括：

* colors
* spacing
* radius
* typography
* chart series
* layout dimensions

生成：

```text
docs/UI_DESIGN_SYSTEM.md
```

---

# 64. UI_DESIGN_SYSTEM.md

必须记录：

## Color

每一个 semantic token 及值。

## Typography

字号和用途。

## Spacing

spacing scale。

## Radius

圆角。

## Layout

Sidebar / Topbar / page padding。

## Components

* Buttons
* Tables
* Cards
* Badge
* Tabs

## Charts

数据系列颜色和图表规范。

这个文件以后将用于：

**PySide6 复刻。**

---

# 65. Qt Mapping 文档

生成：

```text
docs/QT_MAPPING.md
```

为以后 PySide6 移植记录：

```text
Web Component → Qt Equivalent
```

例如：

```text
Sidebar
→ QWidget + QVBoxLayout

Navigation Item
→ QPushButton

Page Stack
→ QStackedWidget

Data Table
→ QTableView

Tabs
→ QTabWidget / custom segmented control

Select
→ QComboBox

Metric Card
→ custom QWidget

Main Line Chart
→ PyQtGraph PlotWidget

Dialog
→ QDialog

Toast
→ overlay QWidget
```

并记录：

* spacing
* exact color token
* size
* layout relation

---

# 66. Screenshot 任务

运行 Prototype 后生成实际截图。

至少：

```text
screenshots/
01_dashboard.png
02_data.png
03_model.png
04_parameters.png
05_identification.png
06_calibration.png
07_diagnostics_residuals.png
08_diagnostics_correlation.png
09_uncertainty_bootstrap.png
10_export.png
```

使用：

```text
1440 × 900
```

或接近的固定 viewport。

截图必须来自真实运行 Web Prototype。

---

# 67. Screenshot Review

生成截图后逐个检查：

## Sidebar

* 是否像连续灰按钮？
* active state 是否明显？

## Hierarchy

* Page title
* section
* body
* metric

是否有明确层级？

## Density

是否像工程软件？

## Card

是否过多？

## Chart

是否够大？

## Table

是否信息密度合理？

## Alignment

是否有不齐？

## Whitespace

是否过大？

发现问题必须修复。

---

# 68. 特别避免上一版 Qt GUI 的问题

重点避免：

1. 主背景一整片黑/灰；
2. Sidebar 每一项都是灰色矩形按钮；
3. 没有 accent；
4. 标题、辅助文字、正文几乎一个层级；
5. metric 漂浮在空白区域；
6. 页面没有 surface hierarchy；
7. 图标过暗；
8. 页面内容过散；
9. 工程信息密度不足；
10. 看起来像 Qt 默认主题。

Prototype 必须明显解决以上问题。

---

# 69. 不复制第三方页面

可以使用 shadcn 官方开源组件。

但不要：

* 复制商业模板；
* 复制 Tailwind Plus 页面；
* 复制收费 dashboard；
* 下载未知来源设计资产。

所有页面布局应针对 NDM-Calibrator 自行组合。

---

# 70. Dependencies Audit

完成后检查：

```bash
npm ls
```

记录主要 dependency。

生成：

```text
THIRD_PARTY_NOTICES.md
```

记录直接使用的主要开源依赖及许可证类型。

不要未经核查加入收费或来源不明 package。

---

# 71. Build

必须实际执行：

```bash
npm install
npm run build
```

以及：

```bash
npm run lint
```

如果存在 tests：

```bash
npm test
```

不得只依赖 dev server。

---

# 72. Dev Launch

README 给出：

```bash
npm install
npm run dev
```

---

# 73. Visual Audit

最终生成：

```text
UI_AUDIT.md
```

记录：

```text
Dashboard            PASS/WARN/FAIL
Data                 PASS/WARN/FAIL
Model                PASS/WARN/FAIL
Parameters           PASS/WARN/FAIL
Identification       PASS/WARN/FAIL
Calibration          PASS/WARN/FAIL
Diagnostics          PASS/WARN/FAIL
Uncertainty          PASS/WARN/FAIL
Export               PASS/WARN/FAIL

Sidebar              PASS/WARN/FAIL
Typography           PASS/WARN/FAIL
Spacing              PASS/WARN/FAIL
Tables               PASS/WARN/FAIL
Charts               PASS/WARN/FAIL
Color hierarchy      PASS/WARN/FAIL
Engineering density  PASS/WARN/FAIL
```

存在 FAIL 必须继续修复。

---

# 74. 最终交付目录

整理：

```text
deliverable/
├── source/
├── screenshots/
├── docs/
│   ├── UI_DESIGN_SYSTEM.md
│   └── QT_MAPPING.md
├── README.md
├── UI_AUDIT.md
├── THIRD_PARTY_NOTICES.md
├── MANIFEST.json
└── SHA256SUMS.txt
```

不要包含：

```text
node_modules/
dist cache
.git/
IDE cache
old zip
```

`dist/` 可以单独包含最终 build，如果体积合理。

---

# 75. Manifest

生成：

```text
MANIFEST.json
```

记录：

* relative path
* size
* SHA256

同时生成：

```text
SHA256SUMS.txt
```

---

# 76. 清理旧输出

PowerShell：

```powershell
Remove-Item -Recurse -Force deliverable -ErrorAction SilentlyContinue
Remove-Item -Force NDM_CALIBRATOR_WEB_UI_PROTOTYPE_V1.zip -ErrorAction SilentlyContinue
New-Item -ItemType Directory deliverable | Out-Null
```

Linux/macOS：

```bash
rm -rf deliverable
rm -f NDM_CALIBRATOR_WEB_UI_PROTOTYPE_V1.zip
mkdir -p deliverable
```

---

# 77. 最终 ZIP

生成：

```text
NDM_CALIBRATOR_WEB_UI_PROTOTYPE_V1.zip
```

禁止把：

```text
node_modules
.git
cache
旧 ZIP
```

打进去。

---

# 78. ZIP 校验

打包完成后重新读取 ZIP。

检查：

* 可以正常解压；
* 必要文件存在；
* screenshots 完整；
* docs 完整；
* source 完整；
* manifest 一致；
* 无 node_modules；
* 无递归 ZIP；
* 无大量临时文件。

---

# 79. SHA256

PowerShell：

```powershell
Get-FileHash .\NDM_CALIBRATOR_WEB_UI_PROTOTYPE_V1.zip -Algorithm SHA256
```

Linux/macOS：

```bash
sha256sum NDM_CALIBRATOR_WEB_UI_PROTOTYPE_V1.zip
```

---

# 80. 最终回复

完成后返回：

## A. Implementation

列出真正实现的页面与交互。

## B. Stack

列出实际 dependency。

## C. Build

真实报告：

```text
npm run build
PASS / FAIL
```

## D. Lint

真实报告。

## E. Visual Audit

汇总 PASS/WARN。

## F. Screenshots

列出所有截图。

## G. Known limitations

必须真实说明。

## H. Final artifact

输出：

```text
NDM_CALIBRATOR_WEB_UI_PROTOTYPE_V1.zip
```

并提供：

* absolute path
* size
* SHA256

---

# 81. 本项目最重要的原则

当前阶段：

[
\boxed{
\text{UI质量 > 功能数量}
}
]

不要为了显得完整而实现假后端。

真正需要交付的是：

> 一套经过认真设计、能够交互、页面完整、视觉统一、适合后续 PySide6 忠实复刻的高保真工程软件 Web Prototype。

它必须能够作为未来桌面 GUI 开发的唯一视觉参考。

现在开始：

1. 初始化项目；
2. 建立 Design System；
3. 完成 Layout；
4. Dashboard；
5. Data；
6. Model；
7. Parameters；
8. Identification；
9. Calibration；
10. Diagnostics；
11. Uncertainty；
12. Export；
13. Screenshot；
14. Visual Audit；
15. 修复；
16. Build；
17. Manifest/Hash；
18. 最终打包。
