# UI Audit — NDM-Calibrator Web UI Prototype

审计时间: 2026-08-26（响应式/遮挡复查）

截图同步: 2026-08-26。完成移动端溢出、长文本、控件遮挡和图表动画
稳定性复查后重新采集截图；当前 reference 集包含 11 张桌面图和 5 张
交互状态图，Web 工作树另保留移动端截图作为响应式证据。

## 页面审计

| 页面 | 结果 | 说明 |
| --- | --- | --- |
| Dashboard | PASS | 项目概要 + 4 KPI + 工作流 + 拟合预览图 |
| Data | PASS | 数据概要 + TanStack 表格(排序/筛选) + 列映射 + 曲线 |
| Model | PASS | 左结构/右方程编辑器 + 模型有效状态 |
| Parameters | PASS | 可编辑参数表 + 待辨识/固定 + 实时校验 |
| Identification | PASS | 算法选择 + 高级设置折叠 + 演示运行 + 收敛图 |
| Calibration | PASS | 4 KPI + 主拟合图(400px) + 参数结果表 |
| Diagnostics | PASS | 残差/敏感度/可辨识性/相关性四个标签页 |
| Uncertainty | PASS | 多起点分析 + Bootstrap 百分位区间 |
| Export | PASS | 复选框 + 格式 + 路径 + 演示导出反馈 |

## 视觉审计

| 项 | 结果 | 说明 |
| --- | --- | --- |
| Sidebar | PASS | active 有 accent-subtle 底 + 左 3px accent 指示, 非灰按钮 |
| Typography | PASS | 22/15/14/13px 层级清晰, 无超大字体 |
| Spacing | PASS | 28px 页面 padding, 20px card 内边距 |
| Tables | PASS | 紧凑行高, 数字 tabular, 浅表头 |
| Charts | PASS | 统一 series token, thin grid, 无渐变 |
| Color hierarchy | PASS | 主蓝、成功绿、警告黄和危险红按语义使用 |
| Engineering density | WARN | 仪表盘已减弱卡片感，其他页面仍需持续控制 Card 密度 |
| Language consistency | PASS | 可见 UI 已中文化；算法与技术栈专名保留英文 |
| Primary action semantics | PASS | 开始辨识使用主蓝，运行中切换为危险色取消 |
| Status color consistency | PASS | 已完成统一为成功绿，主蓝仅表示选中、运行和主操作 |
| Chart domain utilization | PASS | 首页和校准曲线截图已重新生成并覆盖完整 0-50 s 时间域 |
| Secondary text contrast | PASS | secondary 文本由 `#687482` 加深为 `#5F6B78` |

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

- PASS: 核心交互与布局
- WARN: 构建仍有 Vite 大 chunk 和 Fast Refresh 提示，不影响视觉冻结
- FAIL: 无

V1.0 Freeze Pass 已完成：源码、Design System、审计文档和全部截图已同步；校准图与辨识完成态截图均来自当前运行页面，不再使用旧视觉参考。
