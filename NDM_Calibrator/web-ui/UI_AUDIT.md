# UI Audit — NDM-Calibrator Web UI Prototype

审计时间: 2026-08-14

## 页面审计

| 页面 | 结果 | 说明 |
| --- | --- | --- |
| Dashboard | PASS | 项目概要 + 4 KPI + 工作流 + 拟合预览图 |
| Data | PASS | 数据概要 + TanStack 表格(排序/筛选) + 列映射 + 曲线 |
| Model | PASS | 左结构/右方程编辑器 + Model valid badge |
| Parameters | PASS | 可编辑参数表 + Free/Fixed + 实时校验 + error demo |
| Identification | PASS | 算法选择 + 设置(Advanced 折叠) + mock 运行 + 收敛图 |
| Calibration | PASS | 4 KPI + 主拟合图(400px) + 参数结果表 |
| Diagnostics | PASS | Residuals/Sensitivity/Identifiability/Correlation 四 tab |
| Uncertainty | PASS | Multi-start + Bootstrap (percentile interval) |
| Export | PASS | checkbox + 格式 + 路径 + mock 导出反馈 |

## 视觉审计

| 项 | 结果 | 说明 |
| --- | --- | --- |
| Sidebar | PASS | active 有 accent-subtle 底 + 左 3px accent 指示, 非灰按钮 |
| Typography | PASS | 22/15/14/13px 层级清晰, 无超大字体 |
| Spacing | PASS | 28px 页面 padding, 20px card 内边距 |
| Tables | PASS | 紧凑行高, 数字 tabular, 浅表头 |
| Charts | PASS | 统一 series token, thin grid, 无渐变 |
| Color hierarchy | PASS | 单一 accent `#356FE5`, 语义色克制 |
| Engineering density | PASS | compact, 无大留白, 非网页后台风 |

## 交互审计

| 交互 | 状态 |
| --- | --- |
| Sidebar 导航 + 折叠 | PASS |
| 表格排序/筛选 | PASS |
| 诊断 Tabs | PASS |
| 算法选择 | PASS |
| mock 辨识 (Ready→Running→Completed) | PASS |
| 参数校验 error demo | PASS |
| Bootstrap 参数选择 | PASS |
| 导出 mock 反馈 | PASS |
| Toast | PASS |

## 结论

- PASS: 全部
- WARN: 无
- FAIL: 无

所有页面与交互均已实现并通过内容验证（Playwright 检查关键文案与布局尺寸）。
