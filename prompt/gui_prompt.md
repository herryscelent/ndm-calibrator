# 前端升级任务：非线性动态模型参数辨识与校准软件 V1.0

## 0. 任务目标

在**不重写后端核心算法、不改变现有业务逻辑、不破坏已有测试**的前提下，对：

**《非线性动态模型参数辨识与校准软件 V1.0》**

进行完整的桌面 GUI 重构与视觉升级。

本次任务只负责：

* UI 架构；
* 页面布局；
* 视觉设计系统；
* QSS；
* 可复用 GUI 组件；
* 图表交互；
* Light / Dark Theme；
* 空状态；
* 加载状态；
* 错误状态；
* 操作反馈；
* 前后端 UI 接口适配。

核心技术路线冻结为：

> **PySide6 Qt Widgets + 自研 Fluent-inspired Design System + QSS + PyQtGraph + Matplotlib**

不要改成：

* QML
* Qt Quick
* QFluentWidgets
* WebView
* Electron
* React
* Flask
* FastAPI 前端
* 浏览器 Web App

本软件仍然是纯桌面 Qt Widgets 软件。

---

# 1. 核心设计目标

最终界面应同时具备：

1. Windows 11 Fluent 风格的现代感；
2. MATLAB / Origin / engineering workstation 一类工程软件的信息密度；
3. 数据分析 Dashboard 的清晰层级；
4. 科学计算软件需要的表格、图表、参数编辑能力；
5. Light / Dark 双主题；
6. 1366×768 最低可用；
7. 1920×1080 作为主要设计分辨率；
8. 高 DPI 适配；
9. 不使用廉价网页后台风格；
10. 不使用大量嵌套圆角卡片。

视觉原则：

> 简洁、专业、现代、克制、工程化。

不要做成：

* 游戏启动器；
* 手机 App；
* 电商后台；
* 霓虹科技风；
* 大量渐变；
* 玻璃拟态堆叠；
* 夸张动画；
* 巨大留白；
* 每个控件都塞进 Card。

---

# 2. 不得修改的部分

本次前端升级不得擅自修改：

* 参数辨识数学算法；
* ODE / discrete solver；
* 数据格式；
* 项目文件格式；
* Bootstrap 数学逻辑；
* sensitivity 数学定义；
* identifiability 数学逻辑；
* 已有 public API；
* 后端 result object；
* 测试期望值；
* 示例真实结果。

如 UI 需要后端提供额外状态，应：

1. 优先通过 adapter / view model 适配；
2. 不修改核心数值实现；
3. 将必要改动控制在接口层；
4. 在最终报告中列出。

---

# 3. 前端目录结构

如果现有结构不同，可以兼容调整，但建议新增：

```text
ui/
├─ main_window.py
│
├─ design/
│  ├─ tokens.py
│  ├─ colors.py
│  ├─ typography.py
│  ├─ spacing.py
│  ├─ radius.py
│  ├─ elevation.py
│  ├─ icons.py
│  └─ theme_manager.py
│
├─ styles/
│  ├─ base.qss
│  ├─ light.qss
│  ├─ dark.qss
│  ├─ tables.qss
│  ├─ forms.qss
│  └─ navigation.qss
│
├─ components/
│  ├─ sidebar.py
│  ├─ top_bar.py
│  ├─ page_header.py
│  ├─ metric_card.py
│  ├─ status_badge.py
│  ├─ section.py
│  ├─ parameter_table.py
│  ├─ plot_panel.py
│  ├─ toolbar.py
│  ├─ empty_state.py
│  ├─ loading_overlay.py
│  ├─ error_panel.py
│  ├─ confirm_dialog.py
│  ├─ toast.py
│  ├─ collapsible_panel.py
│  └─ property_editor.py
│
├─ plots/
│  ├─ base_plot.py
│  ├─ time_series_plot.py
│  ├─ measured_simulated_plot.py
│  ├─ residual_plot.py
│  ├─ convergence_plot.py
│  ├─ sensitivity_plot.py
│  ├─ correlation_heatmap.py
│  └─ bootstrap_plot.py
│
├─ pages/
│  ├─ dashboard_page.py
│  ├─ data_page.py
│  ├─ model_page.py
│  ├─ parameter_page.py
│  ├─ identification_page.py
│  ├─ calibration_page.py
│  ├─ diagnostics_page.py
│  ├─ uncertainty_page.py
│  ├─ export_page.py
│  └─ settings_page.py
│
└─ adapters/
   ├─ project_adapter.py
   ├─ identification_adapter.py
   ├─ results_adapter.py
   └─ plot_adapter.py
```

原则：

**页面不得直接承担复杂数值逻辑。**

---

# 4. 设计系统

必须建立统一 Design Tokens。

不要在不同页面随意写：

```python
setStyleSheet("font-size: 17px; ...")
```

统一从 tokens / QSS 管理。

---

# 5. 色彩体系

设计一个克制的工程软件配色。

要求支持：

* Light
* Dark
* System

默认：

**Light**

必须定义语义色，而不是到处直接使用十六进制颜色。

例如：

```text
background
surface
surface_secondary
surface_hover
border
border_strong
text_primary
text_secondary
text_disabled

accent
accent_hover
accent_pressed

success
warning
danger
info

plot_primary
plot_secondary
plot_measured
plot_simulated
plot_residual
```

颜色值由你自行设计，但要求：

* 高可读性；
* 对比度合理；
* 不使用大面积饱和蓝紫渐变；
* Dark mode 不是简单反色；
* 表格和图表 Dark mode 必须可读。

---

# 6. 字体体系

优先：

Windows：

`Segoe UI`

其他平台：

系统 Sans Serif fallback。

不要依赖需要额外分发的商业字体。

建议层级：

```text
Display / Page Title
Section Title
Body
Secondary
Caption
Metric Value
Monospace
```

不要设计超过 6 个字号层级。

要求：

* 主正文清晰；
* 表格紧凑；
* KPI 数字适当突出；
* 参数公式或代码字段可用 monospace；
* 不要大量使用粗体。

---

# 7. 间距体系

使用统一 spacing scale，例如：

```text
4
8
12
16
20
24
32
40
```

不要出现：

```text
margin = 13
padding = 27
```

这种随机尺寸。

---

# 8. 圆角

整体采用适度圆角。

建议：

* 输入框：6–8 px；
* 按钮：6–8 px；
* 小卡片：8–10 px；
* 大区域：8–12 px。

不要做成手机 App 那种 20–30 px 大圆角。

---

# 9. 主窗口布局

主窗口采用：

```text
┌──────────────────────────────────────────────────────────────┐
│ Top Bar                                                      │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│ Left Sidebar  │ Main Content                                 │
│               │                                              │
│               │                                              │
├───────────────┴──────────────────────────────────────────────┤
│ Status Bar                                                   │
└──────────────────────────────────────────────────────────────┘
```

---

# 10. Top Bar

高度保持紧凑。

包含：

左侧：

* 软件名称；
* 当前项目名称；
* 未保存状态 indicator。

右侧：

* Save；
* Theme；
* Settings；
* Help / About。

不要放十几个 toolbar icon。

项目名称过长必须：

* elide；
* tooltip 显示完整名称。

---

# 11. Sidebar

左侧导航是整个应用核心。

导航项：

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

────────────

设置
关于
```

使用统一图标。

不要使用 Emoji 当正式图标。

优先：

* Qt SVG icons；
* 内置 SVG icon set；
* 自有简洁 line icons。

Sidebar 支持：

### Expanded

约：

`210–230 px`

显示：

* 图标；
* 文字。

### Collapsed

约：

`64–72 px`

只显示图标。

折叠状态要保存到用户设置。

---

# 12. 导航行为

当前页面必须具有清楚 active state。

不要只改变文字颜色。

至少同时体现：

* accent indicator；
* background hover/active；
* icon state。

页面切换不要夸张动画。

如果做动画：

`120–180 ms`

淡入即可。

---

# 13. 页面 Header

每个页面统一：

```text
页面标题
一句简短说明                     Primary Action
```

例如：

```text
参数辨识
选择求解算法并估计当前模型未知参数。       [开始辨识]
```

下面进入页面正文。

不要每个页面自创完全不同布局。

---

# 14. Dashboard / 项目首页

首页不能只是大按钮。

设计为真正的项目 Dashboard。

顶部显示：

### Project Summary

* 当前项目
* 最后保存时间
* 当前模型
* 数据量
* 当前辨识状态

然后显示最多 4 个 metric cards：

```text
Samples
4,860

Parameters
3 free / 1 fixed

Best RMSE
0.0418

R²
0.987
```

如果尚未运行辨识：

不要显示虚构数字。

显示：

`Not available`

---

# 15. Workflow

Dashboard 显示工作流程：

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

状态：

* Completed
* Current
* Pending
* Warning

用户点击某一步可跳转对应页面。

---

# 16. Empty State

新项目刚打开时不能出现大量空白表格。

例如没有数据时：

```text
尚未导入实验数据

导入 CSV 或 XLSX 文件以开始参数辨识。

[导入数据]
```

空状态必须包含：

* 简洁 icon；
* 标题；
* 一句话说明；
* 一个 primary action。

---

# 17. 数据管理页面

布局：

```text
┌──────────────────────────────────────────────────────┐
│ Data Toolbar                                         │
├──────────────────────────────────────────────────────┤
│ Data Summary                                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Data Table / Preview                                 │
│                                                      │
├───────────────────────┬──────────────────────────────┤
│ Column Mapping        │ Data Preview Plot            │
└───────────────────────┴──────────────────────────────┘
```

Toolbar：

* Import CSV
* Import Excel
* Data Range
* Missing Values
* Reset

不要塞大量次级按钮。

---

# 18. 数据 Summary

显示少量 compact metrics：

* Rows
* Columns
* Missing
* Time span

不要把每一个统计量做一张卡。

---

# 19. 数据表格

使用：

`QTableView`

不要用大量 `QTableWidget` 临时堆数据。

要求：

* alternating rows；
* sticky / readable header；
* 数字右对齐；
* 列宽合理；
* 支持排序；
* 可复制；
* 大数据量时不要一次创建几万个 QWidget cell。

数据 Model 与 UI 解耦。

---

# 20. Column Mapping

映射功能采用紧凑 Property Editor / Table：

```text
Column             Role
time               Time
u                  Input
temperature        Output
ambient            Input
comment            Ignore
```

Role 使用 ComboBox。

状态颜色：

* Time
* Input
* Output
* Ignore

但不要依赖颜色作为唯一信息。

---

# 21. 模型定义页面

布局推荐：

```text
┌───────────────────────┬──────────────────────────────┐
│ Model Structure       │ Equation Editor              │
│                       │                              │
│ States                │ dx1/dt = ...                │
│ Inputs                │ dx2/dt = ...                │
│ Parameters            │ y = ...                     │
│ Outputs               │                              │
│ Initial Conditions    │                              │
├───────────────────────┴──────────────────────────────┤
│ Model Validation                                      │
└──────────────────────────────────────────────────────┘
```

---

# 22. 模型编辑器

公式编辑区域：

* monospace；
* 清晰行号可选；
* syntax feedback；
* error line highlight；
* validation button。

模型校验成功：

显示：

`Model valid`

失败：

显示具体：

* Undefined symbol；
* Missing equation；
* Invalid parameter；
* Equation mismatch。

不要弹出几十个 QMessageBox。

优先 inline validation panel。

---

# 23. 参数配置页面

这是重点页面之一。

顶部：

```text
参数配置
设置待辨识参数的初值、约束范围及固定状态。
```

主体：

`ParameterTable`

列：

```text
Parameter
Initial
Lower
Upper
Status
Unit
```

Unit 若后端没有单位信息可选，不强制。

Status：

* Free
* Fixed

---

# 24. 参数表格交互

要求：

* 双击编辑；
* 数字 validator；
* 非法值即时提示；
* `lower < initial < upper` inline error；
* Free / Fixed 使用简洁 toggle 或 ComboBox；
* Fixed 参数的 bounds 自动 disabled。

顶部动作：

* Add
* Remove
* Reset
* Validate

不要每行放四五个按钮。

---

# 25. 参数辨识页面

推荐布局：

```text
┌─────────────────────────────────────────────────────┐
│ Algorithm Settings                                  │
├──────────────────────┬──────────────────────────────┤
│ Algorithm            │ Runtime Summary              │
│ Configuration        │                              │
│                      │ Objective                    │
│                      │ Best Loss                    │
│                      │ Evaluations                  │
│                      │ Runtime                      │
├──────────────────────┴──────────────────────────────┤
│ Convergence Plot                                     │
├─────────────────────────────────────────────────────┤
│ Best Parameters                                      │
└─────────────────────────────────────────────────────┘
```

---

# 26. Algorithm Selector

使用清晰的 segmented / button group / list：

* Least Squares
* Nelder-Mead
* Differential Evolution
* Multi-start

不要用一个塞满内容的巨大 ComboBox。

选择算法后右侧动态出现对应配置。

---

# 27. Advanced Settings

高级配置不要默认全部展开。

例如：

```text
Algorithm Settings

Tolerance
Max Evaluations
Seed

▸ Advanced
```

展开后：

* rtol
* atol
* mutation
* recombination
* population
* worker options

减少视觉噪声。

---

# 28. Start / Cancel

Primary action：

`开始辨识`

运行后变为：

`取消`

必须明确显示：

* Running
* Completed
* Failed
* Cancelled

不要只用 spinner。

---

# 29. Loading State

长任务运行时：

* GUI 保持可交互；
* 当前页面显示运行状态；
* convergence plot 可实时更新则更新；
* status bar 同步显示；
* 不使用全屏 blocking loading。

可用轻量 loading overlay，但不要遮住整个应用。

---

# 30. Calibration 页面

这是最重要的结果展示页面。

顶部显示最多 4 个 KPI：

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

KPI 使用统一 `MetricCard`。

不要用巨大数字占半个屏幕。

---

# 31. Measured vs Simulated

Calibration 页面主体使用 PyQtGraph。

显示：

* Measured
* Simulated

要求：

* zoom；
* pan；
* auto range；
* legend；
* crosshair；
* hover / nearest point information；
* reset view；
* export PNG。

不要使用硬编码颜色。

颜色由 theme tokens 提供。

---

# 32. Plot Toolbar

图表统一 toolbar：

```text
Reset View
Auto Range
Crosshair
Legend
Export
```

用 icon + tooltip。

不要把按钮画在图内遮挡数据。

---

# 33. 图表技术方案

应用内交互图：

**PyQtGraph**

报告或静态导出：

**Matplotlib**

不要把所有交互图都改成 Matplotlib Canvas。

---

# 34. PyQtGraph Theme

必须随 Light / Dark 切换：

* background；
* axis；
* label；
* grid；
* line；
* legend。

不要出现：

Dark UI + 白色 Matplotlib default figure

这种割裂。

---

# 35. Diagnostics 页面

使用顶部 Tabs / Segmented Navigation：

```text
Residuals
Sensitivity
Identifiability
Correlation
```

不要把四种图同时塞一个页面。

---

# 36. Residuals Tab

布局：

上：

Residual summary：

* Mean
* Std
* Max Abs
* ACF peak

中：

Residual Time Series

下：

Histogram / Residual vs Fitted

不要使用 subplot 挤在一个小区域。

可通过内部 tab 切换 secondary plot。

---

# 37. Sensitivity Tab

显示：

* 参数 sensitivity 排名；
* normalized sensitivity；
* 数值表。

优先：

horizontal bar plot

参数名称必须完整可见。

---

# 38. Identifiability Tab

展示：

```text
Condition Number
Rank
Smallest Singular Value
```

下面：

* singular values plot；
* warning panel。

如果 condition number 很高：

显示 Warning，而不是 Danger。

如果矩阵 singular：

显示明确 diagnostic state。

---

# 39. Correlation 页面

实现参数相关矩阵 heatmap。

要求：

* 参数名轴标签；
* 数值 tooltip；
* 色标；
* ([-1,1]) 固定范围；
* 高相关参数列表。

高相关项：

```text
K ↔ tau     0.96
```

用表格列出。

---

# 40. 可信度分析页面

Tabs：

```text
Multi-start
Bootstrap
```

---

# 41. Multi-start

顶部：

* Number of starts
* Success rate
* Best objective

下面：

* 参数结果分布；
* run table；
* best/worst indication。

不要显示几十张小图。

---

# 42. Bootstrap

顶部控制：

* B
* seed
* algorithm
* Run Bootstrap

结果：

```text
Parameter   Estimate   Median   2.5%   97.5%
K           ...
tau         ...
```

下面选择参数：

`Parameter selector`

显示：

* histogram；
* percentile interval；
* point estimate。

---

# 43. Export 页面

布局保持非常清晰：

```text
Export Results

[ ] Project Summary
[ ] Parameters
[ ] Metrics
[ ] Simulation
[ ] Residuals
[ ] Diagnostics
[ ] Bootstrap

Format:
Excel
CSV
HTML Report
Images

Destination:
...

[Export]
```

完成后显示：

* 路径；
* 文件数量；
* success message。

---

# 44. Settings 页面

至少支持：

### Appearance

* Light
* Dark
* System

### UI

* Sidebar expanded/collapsed
* Default plot grid
* Number formatting
* Decimal precision

### Application

* Recent projects count
* Autosave preference
* Log directory

设置即时生效。

---

# 45. Theme Manager

统一实现：

```python
ThemeManager
```

负责：

* application palette；
* QSS；
* icon variant；
* plot theme；
* matplotlib theme；
* persistence。

Theme 切换不应要求重启程序。

---

# 46. 状态颜色

统一语义：

```text
Success
Warning
Error
Info
Neutral
Running
```

例如：

* Valid model → Success
* High correlation → Warning
* Integration failed → Error
* Identification running → Running

不要每个页面发明不同绿色/黄色/红色。

---

# 47. Status Badge

统一使用：

```text
● Valid
● Running
● Warning
● Failed
```

Badge 只用于状态。

不要把所有普通标签做成 pill。

---

# 48. 错误处理 UI

普通输入错误优先使用：

* inline error；
* error panel；
* status bar；
* toast。

严重错误才使用 Modal Dialog。

不得将 traceback 展示给普通用户。

Dialog 可以提供：

`查看详细信息`

显示简化错误信息。

---

# 49. Toast / Info Feedback

实现轻量 Toast / notification：

例如：

```text
Project saved
Excel exported
Model validated
Identification cancelled
```

持续约：

2–4 秒。

不要使用系统通知。

---

# 50. Confirm Dialog

仅用于：

* 删除；
* 覆盖；
* 丢弃未保存内容；
* 清空结果。

不要每个普通按钮都弹确认框。

---

# 51. Accessibility

要求：

* keyboard navigation；
* Tab order 合理；
* shortcut；
* tooltips；
* Light / Dark 都有足够 contrast；
* 状态不能只靠颜色；
* focus state 可见。

---

# 52. 快捷键

至少：

```text
Ctrl+N     New Project
Ctrl+O     Open
Ctrl+S     Save
Ctrl+Shift+S Save As
Ctrl+I     Import Data
Ctrl+Enter Start Identification
Esc        Cancel / Close transient UI
Ctrl+,     Settings
F1         Help
```

若快捷键冲突则合理调整。

---

# 53. High DPI

必须测试：

* 100%
* 125%
* 150%

不要 hard-code pixel-perfect geometry 导致高 DPI 崩坏。

优先 Layout 管理器。

禁止大量：

```python
widget.setGeometry(...)
```

---

# 54. Responsive Desktop Layout

最低：

1366×768

目标：

1920×1080

在较窄窗口：

* sidebar 可折叠；
* metric cards 自动换行；
* splitters 可调；
* 表格保持可用；
* 图表不能被压到高度 100 px。

---

# 55. Splitter

数据页、模型页等适合区域采用：

`QSplitter`

例如：

```text
Column Mapping | Data Plot
```

让用户调整空间。

保存 splitter state。

---

# 56. Scroll

页面整体如果内容较多：

使用统一：

`QScrollArea`

但：

* sidebar 不滚动；
* topbar 不滚动；
* 页面 header 尽量可见。

禁止嵌套大量 ScrollArea。

---

# 57. 表单规范

Label 永远在：

* input 上方；
* 或左侧固定宽度。

避免：

```text
Parameter:
[        ]
```

和其他页面又完全不同。

统一 field height。

---

# 58. Primary / Secondary / Danger Button

设计三种主要按钮：

### Primary

关键操作：

* Start
* Import
* Export
* Save

### Secondary

普通操作。

### Danger

仅：

* Delete
* Clear
* Destructive Reset

不要到处红按钮。

---

# 59. Icon Button

Icon-only button 必须：

* tooltip；
* hover；
* focus；
* accessible name。

---

# 60. 图标规范

所有图标采用统一视觉语言：

* line icon；
* stroke 类似；
* 统一尺寸。

不要：

* emoji；
* 彩色混用；
* Material + FontAwesome + Windows icon 三套混用。

---

# 61. About 页面

简洁显示：

```text
非线性动态模型参数辨识与校准软件
V1.0

NDM-Calibrator

Python
PySide6
NumPy
SciPy
PyQtGraph
```

包含：

* version；
* build information；
* license info；
* dependency info。

不要写营销话术。

---

# 62. 图表导出

应用内 PyQtGraph 图表必须支持导出：

* PNG

如果实现稳定，可增加：

* SVG。

导出图片必须：

* 有 title；
* axis labels；
* legend；
* 高分辨率；
* 背景正确。

---

# 63. Matplotlib Export Theme

报告图不能直接继承 Dark UI。

默认报告图采用：

* white background；
* publication-friendly style。

避免黑底图出现在 PDF / HTML 报告。

---

# 64. 性能

UI 不得因为：

* 10,000 rows；
* plot update；
* large table；

明显冻结。

数据表优先：

Model/View。

Plot 更新避免逐点反复 addItem。

---

# 65. 页面状态

每个页面明确支持：

```text
EMPTY
READY
RUNNING
SUCCESS
WARNING
ERROR
```

不要通过一堆：

```python
if data is None
```

散落实现。

可以建立 PageState pattern。

---

# 66. 前后端 Adapter

UI 不应直接知道 SciPy result 的所有内部细节。

建立：

```text
IdentificationViewModel
CalibrationViewModel
DiagnosticsViewModel
BootstrapViewModel
```

或者轻量 Adapter。

主要目的是：

将后端对象映射为 UI 可显示数据。

不要为形式主义引入重量级 MVVM 框架。

---

# 67. GUI Smoke Tests

增加 GUI smoke tests。

至少测试：

* MainWindow 创建；
* 页面切换；
* Light/Dark 切换；
* Sidebar collapse；
* Parameter table 基础编辑；
* Project state 更新；
* Empty state；
* Result state；
* Error state。

若 CI 无 display：

使用 Qt offscreen。

---

# 68. Screenshot 验收

请为主要页面生成截图。

至少：

```text
01_dashboard_light.png
02_data_light.png
03_model_light.png
04_parameters_light.png
05_identification_light.png
06_calibration_light.png
07_diagnostics_light.png
08_uncertainty_light.png

09_dashboard_dark.png
10_calibration_dark.png
```

要求：

* 使用真实示例项目；
* 不使用 Photoshop mockup；
* 不伪造不存在的数据；
* 由实际运行 GUI 截图。

---

# 69. GUI Review

截图生成后执行一次视觉 review。

检查：

### Alignment

* 标题是否齐；
* 表格是否齐；
* card 高度是否一致。

### Spacing

* 是否过密；
* 是否过空。

### Typography

* 是否字号过多；
* 是否过度加粗。

### Color

* Light/Dark 是否正常；
* accent 是否过度使用。

### Engineering density

* 是否过度 Card 化；
* 是否像网页后台。

### Graph

* 是否图太小；
* 是否 legend 挡数据；
* 是否 axis 不清楚。

发现问题后必须修复。

---

# 70. 禁止典型 AI GUI 问题

重点检查并禁止：

### 1

所有内容都有巨大圆角 Card。

### 2

每个页面顶部都是 4 个随机 KPI。

只有结果有意义时才显示 KPI。

### 3

巨大字体：

```text
Welcome Back!
```

本软件不需要。

### 4

彩色渐变 header。

不要。

### 5

按钮没有真实功能。

禁止。

### 6

图表用随机数据填充。

禁止。

### 7

大量 Emoji。

禁止。

### 8

UI 空白巨大。

禁止。

### 9

重要参数隐藏在过度简化页面。

禁止。

### 10

为了视觉效果降低工程软件操作效率。

禁止。

---

# 71. 第一优先级页面

如果开发时间有限，视觉质量优先保证：

1. Main Window
2. Dashboard
3. Data
4. Parameters
5. Identification
6. Calibration
7. Diagnostics
8. Uncertainty

Settings / About 可以简单一些。

---

# 72. UI 验收标准

完成后 GUI 应给人以下印象：

> 这是一套现代的工程数值分析软件，而不是一个 Python 学生课程设计。

同时必须保证：

* 参数表格高效；
* 数据查看方便；
* 模型编辑清楚；
* 辨识运行状态明确；
* 结果图占据足够视觉空间；
* Diagnostic 信息容易理解；
* GUI 不妨碍专业操作。

---

# 73. 视觉参考方向

只参考视觉语言，不复制代码、资产或具体页面：

* Windows 11 Fluent
* Visual Studio
* VS Code Settings
* MATLAB modern desktop
* OriginLab
* modern engineering dashboards

最终界面必须形成自己的统一设计系统。

---

# 74. 最终前端测试流程

实际运行：

1. 启动软件；
2. Dashboard 正常显示；
3. Sidebar 展开/收起；
4. Light → Dark → System；
5. Import Example；
6. Data Page 显示表格和曲线；
7. Model Page 显示模型；
8. Parameter Page 编辑参数；
9. Identification Page 启动辨识；
10. Running 状态正常；
11. Calibration 页面显示真实结果；
12. Measured/Simulated 图可缩放；
13. Diagnostics 页面正常；
14. Bootstrap 页面正常；
15. 导出；
16. 窗口缩放；
17. 1366×768 检查；
18. 1920×1080 检查；
19. 125% DPI 检查；
20. 生成 Light/Dark 截图。

---

# 75. 最终 Audit

新增：

`GUI_AUDIT.md`

至少记录：

```text
Theme system
PASS / WARN / FAIL

Sidebar
PASS / WARN / FAIL

High DPI
PASS / WARN / FAIL

Data table
PASS / WARN / FAIL

Plot interaction
PASS / WARN / FAIL

Light theme
PASS / WARN / FAIL

Dark theme
PASS / WARN / FAIL

Empty states
PASS / WARN / FAIL

Loading states
PASS / WARN / FAIL

Error states
PASS / WARN / FAIL

1366×768
PASS / WARN / FAIL

1920×1080
PASS / WARN / FAIL
```

有 FAIL 必须继续修复。

---

# 76. 最终交付

保留原有完整项目交付结构，同时额外包含：

```text
docs/
└─ UI_DESIGN_SYSTEM.md

screenshots/
├─ 01_dashboard_light.png
├─ ...
└─ 10_calibration_dark.png

GUI_AUDIT.md
```

`UI_DESIGN_SYSTEM.md` 必须说明：

* Design principles；
* color tokens；
* typography；
* spacing；
* radius；
* button hierarchy；
* status semantics；
* theme behavior；
* plot styling；
* reusable components。

---

# 77. 与原软件 Prompt 的关系

这是一个：

**Frontend Upgrade Prompt**

不是新的完整软件重写任务。

因此：

* 保留原后端；
* 保留原数值实现；
* 保留原测试；
* 保留原项目格式；
* 保留原示例；
* 保留原导出逻辑；
* 只在必要时增加 UI adapter。

如果当前代码还没有 GUI，则直接使用上述设计实现 GUI。

如果已有旧 GUI：

不要在旧 GUI 上简单追加 QSS。

应先审计：

* MainWindow；
* Page；
* Navigation；
* Component；
* Styling；

然后在不影响核心业务代码的情况下重构 UI 层。

---

# 78. 最终原则

整个前端设计遵循：

> **Modern enough to feel polished.**
>
> **Dense enough to remain an engineering tool.**
>
> **Simple enough to remain maintainable.**

最终目标不是“看起来像网页”。

最终目标是：

> **做出一套如果用户不知道它是 Python/PySide6 开发，也会认为它是一款成熟桌面工程软件的 GUI。**

现在开始：

1. 检查现有 GUI；
2. 识别可保留的后端接口；
3. 建立 Design System；
4. 完成 MainWindow + Sidebar；
5. 逐页迁移；
6. 完成 PyQtGraph；
7. 完成 Light/Dark；
8. 运行 GUI smoke tests；
9. 生成真实截图；
10. 完成 GUI_AUDIT.md；
11. 修复所有 FAIL；
12. 再执行最终项目测试与打包。11
