# 测试说明 — NDM-Calibrator V1.0

## 运行测试

```powershell
# Windows PowerShell
$env:QT_QPA_PLATFORM="offscreen"
python -m pytest tests
```

GUI 测试需要 `QT_QPA_PLATFORM=offscreen` (无显示环境)。
全部 96 个测试应在 2-3 分钟内完成。

## 测试结构

| 文件 | 覆盖内容 |
| --- | --- |
| `test_core.py` | 参数验证、模型解析、实验校验、项目序列化/反序列化、损坏文件处理 |
| `test_simulation.py` | 指数衰减解析解对照、一阶稳态/上升时间、四种积分器、插值、离散步进、发散处理 |
| `test_identification.py` | 四种算法的参数恢复、DE/Multi-start 可重复性、seed 记录、无噪声指数精确恢复 |
| `test_diagnostics.py` | 手工可算指标 (SSE/RMSE/MAE/R²)、残差 ACF、敏感性解析对照、可辨识性 (秩亏/高相关) |
| `test_uncertainty.py` | Bootstrap 输出维度/可重复性/区间覆盖、稳定性统计 |
| `test_data.py` | CSV/XLSX 加载、字段映射、数据校验、预处理 |
| `test_gui_smoke.py` | 主窗口创建、页面切换、主题切换、侧栏折叠、参数表格编辑、空状态/结果状态/错误状态 |

## 关键验收

- 指数衰减无噪声: `|k̂ − 0.35| < 1e-4`;
- 一阶低噪声: `|K̂ − 2.5| < 0.1`, `|τ̂ − 6.0| < 0.3` (least_squares);
- 固定 seed 的 DE/Bootstrap 重复运行结果一致;
- 错误模型允许拟合差, 但如实报告 (不伪造成功)。

## 数值正确性对照

- 指数衰减 vs 解析解 `x0·exp(-k·t)`: 最大误差 < 1e-4;
- 一阶系统稳态 → K·u;
- 一阶系统 63% 上升时间 ≈ τ;
- 线性模型灵敏度解析对照。
