# QT Mapping — Web Prototype → PySide6 复刻对照

本文档记录 Web UI 原型中每个组件对应的 PySide6 实现，供后续桌面软件移植时参考。

## 布局结构

| Web Component | Qt Equivalent | 说明 |
| --- | --- | --- |
| App shell (flex column) | `QMainWindow` + `QVBoxLayout` | 顶栏 + 中区 |
| Topbar | `QWidget` (fixed 48px) | 背景 `#FFFFFF`, 底边框 |
| Sidebar | `QWidget` + `QVBoxLayout` | 宽 220/68px, 背景 `#F1F4F8` |
| Sidebar 折叠 | `setFixedWidth()` + 动画 | 160ms 过渡 |
| Main content (overflow-y) | `QScrollArea` | padding 28px |
| Page stack | `QStackedWidget` | 页面切换 |

## Navigation

| Web Component | Qt Equivalent |
| --- | --- |
| Navigation Item | `QPushButton` (checkable) |
| Active indicator (左侧 3px) | 按钮左侧 `QFrame` 或 border-left |
| Icon (Lucide) | 自定义 line icon / QIcon |

## 表单与控件

| Web Component | Qt Equivalent |
| --- | --- |
| Button (primary/secondary/ghost/danger) | `QPushButton` + QSS variant |
| Input | `QLineEdit` |
| Select | `QComboBox` |
| Checkbox | `QCheckBox` |
| Tabs | `QTabWidget` 或自定义 segmented `QButtonGroup` |
| Tooltip | `QToolTip` |
| Badge | `QLabel` + QSS |
| Progress | `QProgressBar` |

## 表格

| Web Component | Qt Equivalent |
| --- | --- |
| Data Table (TanStack) | `QTableView` + `QAbstractTableModel` |
| Sorting | `QSortFilterProxyModel` |
| Column mapping Select | `QComboBox` delegate |

## 图表

| Web Component | Qt Equivalent |
| --- | --- |
| LineChart (Recharts) | `PyQtGraph PlotWidget` |
| BarChart | `PyQtGraph BarGraphItem` |
| Correlation heatmap | `PyQtGraph ImageItem` 或自绘 |
| Histogram | `PyQtGraph BarGraphItem` |

## 弹层

| Web Component | Qt Equivalent |
| --- | --- |
| Dialog | `QDialog` |
| Toast | overlay `QWidget` (QTimer 自动隐藏) |
| Dropdown Menu | `QMenu` |

## 设计参数映射

| 参数 | Web 值 | Qt 值 |
| --- | --- | --- |
| 主背景 | `#F5F7FA` | `QPalette.Window` |
| surface | `#FFFFFF` | `QPalette.Base` |
| text-primary | `#20252B` | `QPalette.WindowText` |
| accent | `#356FE5` | QSS `accent` |
| 圆角 | 6/8/10px | QSS `border-radius` |
| 字体 | Segoe UI | QSS `font-family` |
| 表格行高 | compact | `setDefaultSectionSize` |

## 交互行为

- 侧边栏折叠保存到用户设置 (QSettings)；
- 图表主题随 Light/Dark 切换；
- 长任务在 `QThread` 运行, UI 不冻结；
- 状态用 Badge 语义色, 不依赖单一颜色。
