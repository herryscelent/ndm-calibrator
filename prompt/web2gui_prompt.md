# NDM-Calibrator Web Reference → PySide6 Faithful Migration

## 0. 任务性质

这是一个：

> **冻结 Web UI 视觉参考 → PySide6 Qt Widgets 忠实迁移任务**

不是重新设计任务。

不是产品重构任务。

不是算法开发任务。

不是后端接入任务。

项目：

**《非线性动态模型参数辨识与校准软件 V1.0》**

内部名称：

**NDM-Calibrator**

当前工作区中已经存在一套经过视觉审核并冻结的 Web UI Reference。

该 Web Reference 包含或应包含：

* Web 源码；
* 最终截图；
* `UI_DESIGN_SYSTEM.md`；
* `QT_MAPPING.md`；
* `UI_AUDIT.md`；
* mock data；
* Manifest / SHA256 等冻结材料。

从现在开始：

$$
\boxed{\text{Web Reference = Visual Source of Truth}}
$$

PySide6 GUI 不得自行重新设计。

---

# 1. 首要原则

整个任务必须遵守：

> **Translate, do not redesign.**

即：

> 迁移，而不是重新设计。

禁止出现：

> “由于 Qt 更适合这样，所以我重新调整了布局。”

禁止出现：

> “为了更现代，我换了一套配色。”

禁止出现：

> “为了符合桌面习惯，我把 Sidebar 改成工具栏。”

除非 Web Reference 中的结构在 Qt Widgets 中确实无法合理实现，否则：

$$
\boxed{\text{布局、视觉层级、颜色、字体、间距、表格密度、图表比例应尽可能忠实复刻}}
$$

---

# 2. 第一阶段目标

本阶段只实现：

$$
\boxed{\text{PySide6 High-Fidelity Mock Frontend}}
$$

即：

* 页面可真实切换；
* 表格可交互；
* Tabs 可切换；
* Mock 参数辨识可运行；
* Mock 数据和 Web Reference 一致；
* 图表使用固定 Mock Data；
* Sidebar 可折叠；
* 页面状态可变化；
* Toast / Dialog 等可工作；
* 截图能够与 Web Reference 对照。

但：

**不接入真实参数辨识后端。**

---

# 3. 本阶段禁止接入

禁止修改或接入：

* SciPy optimization backend；
* ODE solver；
* Differential Evolution 真实计算；
* Least Squares 真实计算；
* Bootstrap 真实计算；
* sensitivity 真实计算；
* identifiability 真实计算；
* Excel 实际解析后端；
* 项目 `.ndmc` 正式持久化逻辑；
* 后端工程核心模块。

即使这些代码已经存在，也先不要接。

原因：

本阶段必须单独回答：

> **“PySide6 是否成功复刻冻结 Web UI？”**

不能把 GUI 问题和数值算法问题混在一起。

---

# 4. 旧 GUI 的处理

如果项目中已经存在旧版 PySide6 GUI：

**不得删除。**

不得覆盖。

不得大规模原地修改。

优先保留：

```text
ui_legacy/
```

或保持原目录不动。

新 GUI 放入独立结构，例如：

```text
ui_v2/
```

或：

```text
ui/
```

但必须确保旧 GUI 可以恢复。

只有在未来：

* 新 GUI Mock 验收通过；
* 新 GUI 后端接入通过；
* E2E 通过；

之后，才允许另行决定是否删除旧 GUI。

---

# 5. 技术栈冻结

使用：

* Python 3.11+
* PySide6
* Qt Widgets
* QSS
* PyQtGraph
* NumPy
* matplotlib，仅用于未来报告导出或必要的静态图

禁止：

* QML
* Qt Quick
* QFluentWidgets
* WebView
* Chromium
* Electron
* HTML embedded UI
* React embedded runtime
* Tkinter
* PyQt5
* PyQt6

核心技术路线：

$$
\boxed{
\text{PySide6 Qt Widgets}
+
\text{Custom QSS}
+
\text{PyQtGraph}
}
$$

---

# 6. 开始前必须审计 Web Reference

首先找到冻结的 Web Reference。

不要凭记忆开始写 Qt。

必须实际读取：

* `UI_DESIGN_SYSTEM.md`
* `QT_MAPPING.md`
* 最终截图
* Web CSS / Tailwind theme tokens
* Mock data
* 主要页面源码

生成：

```text
WEB_REFERENCE_AUDIT.md
```

记录：

## Reference Identity

* Reference package path
* reference version
* manifest hash if available
* screenshot count
* source commit if available

## Design Tokens

实际提取：

* background
* surface
* sidebar
* border
* text-primary
* text-secondary
* accent
* accent-hover
* accent-subtle
* success
* warning
* danger

以及：

* typography
* spacing
* radius
* sidebar width
* topbar height
* page padding
* table row density
* chart proportions

如果：

`UI_DESIGN_SYSTEM.md`

与实际 CSS 存在冲突：

**不得自行猜测。**

优先级：

1. 冻结截图最终视觉；
2. 实际 Web source；
3. `UI_DESIGN_SYSTEM.md`。

记录冲突。

不要静默修正。

---

# 7. 禁止重新选颜色

Qt Theme 必须来自 Web Reference。

不要自行使用：

* Qt Fusion Dark；
* Breeze；
* Windows default；
* Material；
* Fluent random palette。

例如如果冻结 Web Reference 实际为：

```text
background       #F5F7FA
surface          #FFFFFF
sidebar          #F1F4F8
border           #DDE3EA

text-primary     #20252B
text-secondary   #5F6B78

accent           #356FE5
accent-hover     #285FCB
accent-subtle    #E7F0FF
```

则 Qt 使用完全相同或视觉等价的值。

不得为了“Qt 更自然”换色。

---

# 8. 第一阶段主题

如果冻结 Web Reference 当前只冻结 Light：

本阶段只完成：

$$
\boxed{\text{Light Theme}}
$$

不要自行添加 Dark Theme。

可以预留 `ThemeManager` 接口，但不要浪费当前任务时间设计第二套主题。

未来 Dark Theme 另做。

---

# 9. Design System

新建：

```text
ui_v2/
├── design/
│   ├── tokens.py
│   ├── theme.py
│   ├── typography.py
│   ├── spacing.py
│   ├── icons.py
│   └── metrics.py
```

禁止各页面散落：

```python
setStyleSheet("background: #fff")
```

所有关键视觉值统一管理。

---

# 10. QSS 架构

建议：

```text
ui_v2/styles/
├── base.qss
├── navigation.qss
├── forms.qss
├── tables.qss
├── tabs.qss
├── buttons.qss
└── plots.qss
```

可以最终组合加载。

所有 QSS selector 使用稳定的：

* objectName
* Qt Property

避免依赖脆弱的 widget 层级选择器。

---

# 11. 主窗口映射

Web：

```text
Topbar
Sidebar
Main Content
```

Qt：

```text
QMainWindow
└── centralWidget
    └── QHBoxLayout
        ├── Sidebar
        └── RightShell
            ├── Topbar
            └── QStackedWidget
```

如果冻结 Web Reference 结构不同，以 Reference 为准。

---

# 12. Sidebar

Web Reference 的 Sidebar 是关键视觉锚点。

必须忠实复刻：

* 展开宽度；
* 折叠宽度；
* Item 高度；
* icon size；
* icon/text gap；
* section spacing；
* active background；
* left accent indicator；
* hover state；
* bottom Settings/About 区域。

建议：

展开：

约：

```text
220 px
```

折叠：

约：

```text
68 px
```

但最终数字必须以 Web Reference 为准。

---

# 13. Sidebar Item

不得再做成旧 GUI 那种：

```text
[ 灰色矩形按钮 ]
[ 灰色矩形按钮 ]
[ 灰色矩形按钮 ]
```

未选中：

* transparent；
* 无 border；
* secondary text。

Hover：

* surface-hover。

Selected：

* accent-subtle；
* accent indicator；
* accent icon；
* primary text。

---

# 14. 图标

使用统一 SVG Line Icons。

优先复刻 Web Lucide icon 的语义。

可以：

* 获取对应 Lucide SVG；
* 将 SVG 作为项目资源；
* 或自行准备同等含义且许可证兼容的 SVG。

不得：

* Emoji；
* Windows emoji glyph；
* 多套 icon 风格混用；
* 随机 Unicode 符号代替正式图标。

所有图标资源必须记录许可证来源。

---

# 15. Topbar

严格参考 Web Reference。

保留：

* NDM Calibrator
* 当前项目上下文
* Save 状态
* 必要 icon actions

不要增加 Ribbon。

不要加传统菜单栏：

```text
File Edit View Tools Help
```

除非 Reference 中存在。

---

# 16. 页面容器

使用：

```text
QStackedWidget
```

切换：

* Dashboard
* Data
* Model
* Parameters
* Identification
* Calibration
* Diagnostics
* Uncertainty
* Export
* Settings
* About

切换必须即时、稳定。

不需要复杂动画。

---

# 17. 页面公共 Header

实现复用：

```python
PageHeader
```

包含：

* title
* description
* optional primary action

确保全部页面：

* 标题基线一致；
* 描述间距一致；
* 右侧 action 对齐一致。

---

# 18. Dashboard

必须按冻结 Web Reference 复刻。

包括：

* 项目概要；
* KPI；
* 工作流程；
* Measured vs Simulated preview；
* Status。

Mock 项目数据必须与 Web Reference 完全一致。

禁止重新生成一套随机数据。

---

# 19. Mock Data

从 Web Reference 中移植同一套固定 Mock Data。

统一放入：

```text
ui_v2/mock/
├── project.py
├── time_series.py
├── parameters.py
├── convergence.py
├── residuals.py
├── diagnostics.py
└── bootstrap.py
```

严禁 GUI 页面内部手写随机数。

严禁：

```python
np.random.rand(...)
```

让每次截图结果不同。

全部 deterministic。

---

# 20. Data Page

目标：

尽可能复制冻结 Data Page。

推荐 Qt：

```text
QSplitter
├── Left:
│   QTableView
└── Right:
    ├── Column Mapping
    └── PyQtGraph
```

数据表：

必须使用：

```text
QTableView
+
QAbstractTableModel
```

不要：

```text
QTableWidget + thousands of QTableWidgetItem
```

---

# 21. Data Table

对照 Web：

* header 高度；
* row height；
* grid；
* hover；
* selection；
* numeric alignment；
* column width。

Mock 行数只需与 Web Reference 展示效果一致。

---

# 22. Column Mapping

使用：

```text
QTableView
+
QComboBox Delegate
```

或等价高质量实现。

Role：

* 时间
* 输入
* 输出
* 状态
* 忽略

不要使用颜色作为唯一状态表达。

---

# 23. Model Page

复刻：

* Model Structure
* Equation Editor
* model validation state

如果 Web Reference 中已经中文化，则 Qt 必须使用相同中文。

Equation Editor：

使用 monospace。

可以用：

```text
QPlainTextEdit
```

配合：

* line padding
* border
* validation message

本阶段不执行真实模型。

---

# 24. Parameters Page

这是关键验收页面。

必须复刻 Web 参数表。

使用：

```text
QTableView
+
custom model/delegate
```

字段跟 Reference 一致，例如：

* 参数
* 初值
* 下限
* 上限
* 状态
* 单位

支持 Mock 编辑。

Free / Fixed：

使用中文或 Reference 中冻结文本。

不要自己做高饱和彩色 Badge。

---

# 25. 参数校验 Demo

实现纯前端逻辑：

$$
lower < initial < upper
$$

如果违反：

显示和 Web Reference 一致的 Inline Error。

这是 UI Demo。

不得调用真实参数 backend。

---

# 26. Identification Page

严格复刻：

* algorithm selector；
* settings；
* main action；
* runtime summary；
* convergence plot；
* best parameters；
* status。

---

# 27. Mock Identification

点击：

```text
开始辨识
```

模拟状态：

```text
READY
→ RUNNING
→ COMPLETED
```

时长：

约 2–4 秒。

使用：

```text
QTimer
```

或轻量 mock worker。

不得真正运行优化。

---

# 28. Action Color Semantic

冻结规则：

### Ready

“开始辨识”

= Primary / Accent。

### Running

“取消辨识”

= Danger。

### Completed

Completed / 已完成

= Success。

禁止再次出现：

“开始辨识按钮是红色”

这种旧 GUI 问题。

---

# 29. Mock Convergence

使用 Web Reference 相同的 convergence points。

运行过程中可以逐段显示。

完成后与 Web Screenshot 相同。

---

# 30. Calibration Page

这是最高优先级页面之一。

必须忠实复刻：

* RMSE
* MAE
* R²
* Runtime
* large measured/simulated plot
* parameter result table

图表面积比例必须接近 Web Reference。

不要让图只有：

200 px

高。

---

# 31. Calibration Plot

使用：

```text
PyQtGraph PlotWidget
```

必须支持：

* pan
* zoom
* reset
* legend
* tooltip/crosshair if reasonably implementable

颜色取 Design Tokens。

---

# 32. Plot Domain

必须使用与 Web Reference 相同完整数据范围。

例如 Reference：

$$
0\sim50\,s
$$

Qt 不能再出现：

> x 轴 0–50，但数据只到 4 s。

生成截图前必须程序化检查：

```text
min(x)
max(x)
```

与预期一致。

---

# 33. Diagnostics

Reference 中若采用 Tabs：

Qt 同样采用 Tabs / equivalent segmented navigation。

包括：

* 残差
* 敏感性
* 可辨识性
* 参数相关性

不要把所有内容塞到一个页面。

---

# 34. Residuals

至少：

* summary metrics
* residual time series
* secondary distribution plot

与 Reference 数值和数据形状一致。

---

# 35. Sensitivity

复刻 Web 横向 ranking。

PyQtGraph 若 horizontal bar 实现复杂：

可以自定义轻量 QWidget bar visualization。

但视觉必须接近。

---

# 36. Identifiability

显示：

* Condition Number
* Rank
* Min Singular Value
* status message
* singular value visualization

全部使用 Mock Data。

---

# 37. Correlation

对于小矩阵：

优先自定义：

```text
QTableView
```

或：

```text
QGraphicsView
```

绘制 heatmap。

无需引入 Matplotlib Canvas 破坏视觉统一。

颜色固定：

$$
[-1,1]
$$

---

# 38. Uncertainty

Tabs：

* Multi-start
* Bootstrap

Mock 数据与 Web Reference 一致。

Bootstrap：

* parameter selector
* result table
* distribution

---

# 39. Export

纯 UI Demo。

Checkbox 和 Format 与 Reference 一致。

点击 Export：

不真正生成科学结果文件。

可以：

* 模拟 0.5–1 秒；
* 显示 success toast。

不要偷偷实现一半真实后端。

---

# 40. Settings

只复刻当前 Reference 已有设置。

不要擅自扩充大量功能。

若 Reference 当前只冻结 Light：

Dark：

可以显示：

```text
后续版本
```

或不显示。

---

# 41. About

忠实复刻。

必须更新技术栈为：

* Python
* PySide6
* PyQtGraph

不要继续显示 React 技术栈。

但产品身份、版本和设计语言保持一致。

---

# 42. PyQtGraph Wrapper

不要让每个页面直接自己配置 PlotWidget。

建立：

```text
ui_v2/plots/
├── base_plot.py
├── time_series_plot.py
├── convergence_plot.py
├── residual_plot.py
├── sensitivity_plot.py
└── bootstrap_plot.py
```

统一：

* background
* axis
* grid
* legend
* font
* line width
* padding

---

# 43. QTableView Design

建立统一：

```python
EngineeringTableView
```

或统一 style。

保证：

* row height
* header
* hover
* selected state
* border
* numeric alignment
* typography

全部页面一致。

---

# 44. Metric Card

实现一个：

```python
MetricCard
```

只允许用于 Reference 中确实有 Metric Card 的地方。

禁止：

Card Everywhere。

---

# 45. Status Badge

统一：

```python
StatusBadge
```

状态：

* neutral
* info
* running
* success
* warning
* error

颜色必须和 Web Reference semantic tokens 对应。

---

# 46. Toast

实现简单：

```python
ToastManager
```

用于：

* 项目已保存
* 模型验证成功
* 参数辨识完成
* 导出完成

不要使用系统 notification。

---

# 47. Dialog

实现通用：

```python
ConfirmDialog
```

样式对照 Web Dialog。

不要直接使用毫无 QSS 的默认 QMessageBox 作为最终视觉。

---

# 48. Layout 禁止项

禁止大量：

```python
setGeometry(...)
move(...)
resize(...)
```

所有主要布局：

使用：

* QHBoxLayout
* QVBoxLayout
* QGridLayout
* QFormLayout
* QSplitter

确保：

* 1366×768
* 1440×900
* 1920×1080

都合理。

---

# 49. DPI

测试：

* 100%
* 125%
* 150%

Windows 环境优先。

不要写死字体像素导致缩放崩坏。

---

# 50. Reference Screenshot 环境

以 Web Reference 截图 viewport 为主要比较环境。

如果 Web 使用：

```text
1440×900
```

Qt 也尽量固定客户端内容区接近对应尺寸。

必须记录：

* 整个 Window size
* client size
* DPI scale
* OS
* Qt version

---

# 51. 每页都必须截图

生成：

```text
screenshots_qt/
01_dashboard.png
02_data.png
03_model.png
04_parameters.png
05_identification_ready.png
06_identification_running.png
07_identification_completed.png
08_calibration.png
09_diagnostics_residuals.png
10_diagnostics_correlation.png
11_uncertainty_bootstrap.png
12_export.png
```

所有截图必须来自真实 Qt 应用。

不得 Photoshop。

不得重新使用 Web 图片伪装。

---

# 52. Web / Qt Pair Comparison

建立：

```text
comparison/
```

将对应截图做成 side-by-side：

```text
Web | Qt
```

例如：

```text
comparison/
01_dashboard_compare.png
02_data_compare.png
...
```

可以用 PIL 自动生成。

---

# 53. 自动视觉差异仅作辅助

可以计算：

* image dimensions
* average color difference
* SSIM（如依赖已存在或合理增加）
* edge/layout rough difference

但是：

**不得用一个 SSIM 数字自动宣布视觉 PASS。**

因为：

* 浏览器字体渲染
* Qt 字体渲染
* anti-aliasing
* chart engine

天然会有差异。

最终以：

> 结构、比例、层级、颜色、密度、主要控件位置

为核心。

---

# 54. Visual Checklist

每个页面逐项检查：

## Geometry

* Sidebar width
* Topbar height
* page padding
* section spacing
* plot height
* table proportions

## Typography

* page title
* description
* table font
* KPI font
* labels

## Colors

* background
* surface
* border
* text
* accent
* success
* danger

## Components

* buttons
* table
* badge
* tabs
* inputs
* select

## Data

* mock value consistency
* plot x domain
* plot shape
* parameter values

---

# 55. Visual Tolerance

不是要求浏览器与 Qt 完全逐像素一致。

可接受：

* 1–3 px minor spacing difference；
* 系统字体 antialiasing 差异；
* SVG icon rasterization 轻微差异；
* Recharts / PyQtGraph line rendering 差异。

不可接受：

* Sidebar 明显更宽；
* 页面结构不同；
* Card 数量不同；
* 图比例明显不同；
* 按钮颜色语义不同；
* 字号层级明显不同；
* 表格密度明显不同；
* accent 不同；
* 信息顺序变化；
* 自行增加/删除关键 section。

---

# 56. 禁止“Qt 风格化”

严禁：

> “我认为桌面软件更应该使用这种结构。”

Web Reference 已经是经过审核的设计。

Qt 的任务是忠实表达。

禁止自行：

* 添加传统菜单；
* 改为 Ribbon；
* 把 Sidebar 改成 TreeView；
* 把 KPI 改成 GroupBox；
* 把 Tab 改成多个独立窗口；
* 加大量 QGroupBox 边框；
* 使用 Qt Fusion 灰色按钮；
* 使用系统默认蓝；
* 将 table 改为 spreadsheet 默认外观。

---

# 57. 禁止默认 Qt 控件裸奔

最终截图中不能明显出现没有设计过的：

* QPushButton
* QComboBox
* QLineEdit
* QTabWidget
* QScrollBar
* QHeaderView

全部必须经过 Design System/QSS 处理。

---

# 58. Native Behavior 与视觉冲突

若 native widget 在某平台无法实现 Web 视觉：

优先：

1. QSS；
2. lightweight custom delegate；
3. lightweight custom widget。

但不要为了 2 px 差异重写整个 Qt 控件体系。

保持：

$$
\text{视觉忠实}
+
\text{可维护性}
$$

平衡。

---

# 59. Accessibility

保留：

* keyboard focus；
* Tab navigation；
* visible focus；
* tooltip；
* readable contrast。

不能为了仿 Web 把 focus outline 全删掉。

---

# 60. 第一阶段目录建议

```text
ui_v2/
├── main_window.py
│
├── design/
│   ├── tokens.py
│   ├── theme.py
│   ├── typography.py
│   ├── metrics.py
│   └── icons.py
│
├── styles/
│   ├── base.qss
│   ├── navigation.qss
│   ├── forms.qss
│   ├── tables.qss
│   ├── tabs.qss
│   └── buttons.qss
│
├── components/
│   ├── sidebar.py
│   ├── topbar.py
│   ├── page_header.py
│   ├── metric_card.py
│   ├── status_badge.py
│   ├── engineering_table.py
│   ├── toast.py
│   └── dialogs.py
│
├── plots/
│   ├── base_plot.py
│   ├── time_series_plot.py
│   ├── convergence_plot.py
│   ├── residual_plot.py
│   └── bootstrap_plot.py
│
├── pages/
│   ├── dashboard.py
│   ├── data.py
│   ├── model.py
│   ├── parameters.py
│   ├── identification.py
│   ├── calibration.py
│   ├── diagnostics.py
│   ├── uncertainty.py
│   ├── export.py
│   ├── settings.py
│   └── about.py
│
├── mock/
│   ├── project.py
│   ├── time_series.py
│   ├── parameters.py
│   ├── convergence.py
│   ├── diagnostics.py
│   └── bootstrap.py
│
└── tests/
```

根据项目现状可以合理调整。

---

# 61. 开发顺序

严格按：

## Phase 0

Web Reference Audit。

## Phase 1

Design Tokens + Theme + MainWindow。

## Phase 2

Sidebar + Topbar + PageHeader。

## Phase 3

Dashboard。

## Phase 4

Data。

## Phase 5

Parameters。

## Phase 6

Identification。

## Phase 7

Calibration。

## Phase 8

Diagnostics + Uncertainty。

## Phase 9

Model + Export + Settings + About。

## Phase 10

Screenshots + Comparison + Visual Audit。

不要一开始把 11 个页面全部写完再看截图。

---

# 62. 每阶段 Screenshot Gate

Dashboard 完成后：

先截图。

对比 Web。

存在明显问题：

先修。

再进入 Data。

Data 完成：

截图。

修。

如此继续。

避免最后一次性发现整个设计系统错了。

---

# 63. GUI Smoke Tests

使用 pytest / pytest-qt（如合理）。

至少：

* MainWindow create
* page navigation
* sidebar collapse
* parameter editing
* mock validation
* mock identification state
* tabs
* mock export
* toast
* application close

若环境支持：

offscreen tests。

---

# 64. Mock State Tests

验证：

```text
READY
RUNNING
COMPLETED
CANCELLED
ERROR
```

最少确保：

Identification：

* 开始
* 运行
* 完成
* 取消

UI 状态正确。

---

# 65. 不接后端的硬性检查

任务结束前搜索：

```text
scipy.optimize
solve_ivp
least_squares
differential_evolution
```

如果这些只存在于项目原后端没问题。

但：

```text
ui_v2/
```

不允许直接 import 它们。

第一阶段 GUI 只能使用 Mock Adapter。

---

# 66. Adapter 预留

允许创建：

```text
ui_v2/adapters/
```

当前实现：

```text
MockProjectAdapter
MockIdentificationAdapter
MockResultsAdapter
```

以后第二阶段替换为：

```text
RealProjectAdapter
RealIdentificationAdapter
RealResultsAdapter
```

UI 页面不需要重写。

---

# 67. 第一阶段完成定义

只有以下全部满足，才允许宣布：

**PySide6 Mock Migration Completed**

必须：

* 所有页面存在；
* 所有页面可访问；
* Web mock data 一致；
* Web design tokens 一致；
* screenshots 完整；
* comparison 完整；
* visual audit 完整；
* GUI smoke test PASS；
* 未接真实后端；
* 没有明显裸 Qt 默认控件；
* 没有重新设计。

---

# 68. Visual Audit

生成：

```text
QT_VISUAL_AUDIT.md
```

每项必须：

```text
PASS
WARN
FAIL
```

检查：

```text
Reference integrity
Main window geometry
Sidebar
Topbar
Dashboard
Data
Model
Parameters
Identification
Calibration
Diagnostics
Uncertainty
Export
Settings
About

Color tokens
Typography
Spacing
Radius
Tables
Forms
Buttons
Tabs
Badges
Plots
Mock data consistency

1366x768
1440x900
1920x1080
125% DPI
```

不得习惯性全部 PASS。

发现视觉差异：

如实 WARN。

---

# 69. Known Differences

生成：

```text
KNOWN_VISUAL_DIFFERENCES.md
```

例如：

```text
Recharts axis labels use browser text rasterization;
PyQtGraph uses Qt font rendering, resulting in ~1–2 px baseline differences.
```

可以接受。

但如果：

```text
Qt calibration plot is much smaller than Web reference.
```

这是 FAIL，不是 Known Difference。

---

# 70. 第二阶段禁止自动开始

第一阶段完成后：

**立即停止。**

不要自动：

* 接真实后端；
* 修改算法；
* 删除 Mock；
* 替换旧 GUI；
* 做 exe；
* 做正式软著材料。

先把：

* Qt screenshots；
* compare screenshots；
* audit；
* ZIP；

交回用户审核。

只有用户明确批准以后：

才进入：

**Phase 2 — Real Backend Integration**

---

# 71. README

生成：

```text
README_QT_MIGRATION.md
```

包含：

* 任务目标
* Reference 位置
* 启动方法
* screenshot 方法
* tests
* design system
* 当前只使用 Mock 的说明
* 下一阶段接口

---

# 72. 启动命令

提供一个明确入口，例如：

```powershell
python -m ui_v2
```

或：

```powershell
python -m ui_v2.main
```

不要要求用户修改源码启动。

---

# 73. Screenshot Script

提供：

```text
scripts/capture_qt_ui.py
```

或适合当前平台的自动截图方案。

尽可能自动：

* open page
* set deterministic window size
* wait for render
* capture

Identification completed 状态：

允许自动触发 Mock progression。

---

# 74. Comparison Script

生成：

```text
scripts/build_ui_comparison.py
```

读取：

```text
web_reference/screenshots/
screenshots_qt/
```

生成：

```text
comparison/
```

Side-by-side。

不得修改原截图。

---

# 75. Reference Copy

最终交付中不要复制整个 Web 项目导致包极度膨胀。

可以保存：

```text
reference/
├── REFERENCE_INFO.md
└── WEB_REFERENCE_SHA256.txt
```

如果用户明确要求包含完整 Web reference，再复制。

否则仅记录来源/hash。

---

# 76. 最终测试

运行：

```powershell
pytest -q
```

以及：

```powershell
python -m ui_v2
```

进行 smoke run。

真实记录：

* passed
* failed
* skipped
* warnings

---

# 77. 代码 Audit

检查：

* TODO
* FIXME
* empty slots
* unused page
* missing button handler
* bare except
* hard-coded random data inside pages
* direct scipy backend imports
* raw default Qt control
* duplicated color literals
* duplicated spacing literals

生成：

```text
QT_MIGRATION_CODE_AUDIT.md
```

---

# 78. 最终清理

清理：

* `__pycache__`
* `.pytest_cache`
* temp screenshots
* old comparison outputs
* stale zip
* logs
* build caches

不要删除用户原项目结果。

---

# 79. 最终交付目录

创建：

```text
deliverable_qt_mock/
├── source/
├── screenshots_qt/
├── comparison/
├── docs/
│   ├── WEB_REFERENCE_AUDIT.md
│   ├── README_QT_MIGRATION.md
│   ├── QT_VISUAL_AUDIT.md
│   ├── KNOWN_VISUAL_DIFFERENCES.md
│   └── QT_MIGRATION_CODE_AUDIT.md
│
├── scripts/
├── tests/
├── MANIFEST.json
└── SHA256SUMS.txt
```

---

# 80. Manifest 生成顺序

必须在：

* code 完成
* screenshot 完成
* comparison 完成
* docs 完成
* tests 完成
* cleanup 完成

之后，

**最后生成 Manifest。**

不要再重复之前：

> Manifest 生成后又新增截图

导致 Manifest 过期的问题。

---

# 81. MANIFEST.json

记录：

* relative_path
* size
* SHA256

覆盖交付目录所有应交付文件。

Manifest 自己可排除自身 hash，规则需写清楚。

---

# 82. SHA256SUMS

生成：

```text
SHA256SUMS.txt
```

记录全部交付文件 hash。

---

# 83. Manifest 一致性测试

必须程序化检查：

```text
files_on_disk
vs
files_in_manifest
```

要求：

```text
missing = 0
unexpected = 0
hash_mismatch = 0
```

否则不得打包。

---

# 84. 删除旧 ZIP

PowerShell：

```powershell
Remove-Item -Force `
  NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip `
  -ErrorAction SilentlyContinue
```

Linux：

```bash
rm -f NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip
```

---

# 85. 最终打包

生成：

```text
NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip
```

ZIP 不包含：

* `.git`
* `.venv`
* `__pycache__`
* `.pytest_cache`
* old ZIP
* temp screenshots
* IDE settings
* unrelated backend result data

---

# 86. ZIP 内容校验

打包后：

**必须重新打开 ZIP。**

检查：

* ZIP 可读；
* 文件总数合理；
* screenshots 存在；
* comparison 存在；
* docs 存在；
* source 存在；
* tests 存在；
* manifest 存在；
* hashes 存在。

---

# 87. 解压后二次校验

将最终 ZIP 解压到：

```text
_tmp_verify_qt_migration/
```

重新运行：

* Manifest completeness；
* SHA256；
* required file check。

最终：

```text
missing = 0
unexpected = 0
hash mismatch = 0
```

然后删除临时验证目录。

---

# 88. ZIP SHA256

PowerShell：

```powershell
Get-FileHash `
  .\NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip `
  -Algorithm SHA256
```

Linux：

```bash
sha256sum NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip
```

记录。

---

# 89. Git 状态

如果项目属于 Git repository：

执行：

```bash
git status --short
git rev-parse HEAD
```

记录。

不得：

* force push
* reset --hard
* delete unrelated branch
* overwrite main
* amend unrelated commit

除非另有明确要求。

---

# 90. 最终回复格式

完成后必须返回：

## A. Reference

* Web Reference
* version/hash

## B. PySide6 Implementation

列出实际迁移页面。

## C. Mock Status

确认：

```text
Real backend connected: NO
Mock frontend: YES
```

## D. Tests

真实 pytest 结果。

## E. Screenshot Comparison

列出：

```text
Web
Qt
Compare
```

文件。

## F. Visual Audit

汇总：

* PASS
* WARN
* FAIL

如果存在 FAIL：

不得宣布完成。

## G. Known Differences

列出可接受浏览器/Qt 渲染差异。

## H. Git

* branch
* HEAD
* worktree status

## I. Final ZIP

```text
NDM_CALIBRATOR_QT_MOCK_MIGRATION_V1.zip
```

提供：

* absolute path
* size
* SHA256

---

# 91. 最终硬性原则

本阶段不是：

> “用 PySide6 做一个类似的软件。”

而是：

$$
\boxed{
\text{用 PySide6 忠实实现已经冻结的软件视觉设计}
}
$$

Web Reference 已经完成：

> **Design**

当前任务只完成：

> **Translation**

不得重新设计。

---

# 92. 停止条件

一旦：

* Mock Qt GUI 完成；
* screenshots 完成；
* comparison 完成；
* audit 无 FAIL；
* tests 通过；
* final ZIP 验证通过；

立即停止。

不要进入真实后端集成。

等待用户审核截图和交付包后，再开始下一阶段。

现在开始：

1. 定位冻结 Web Reference；
2. 审计 Reference；
3. 提取 Design Tokens；
4. 建立 PySide6 Design System；
5. MainWindow；
6. Sidebar / Topbar；
7. Dashboard；
8. Data；
9. Parameters；
10. Identification；
11. Calibration；
12. Diagnostics / Uncertainty；
13. Remaining pages；
14. Qt screenshots；
15. Web/Qt comparison；
16. Visual Audit；
17. Smoke tests；
18. Code audit；
19. Cleanup；
20. Manifest / SHA256；
21. Final ZIP；
22. 解压后二次验证；
23. 停止并返回结果。
