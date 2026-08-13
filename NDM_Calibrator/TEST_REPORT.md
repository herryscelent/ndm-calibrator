# TEST REPORT — NDM-Calibrator V1.0

## 环境

| 项 | 值 |
| --- | --- |
| OS | Windows 11 Home China (10.0.26200) |
| Python | 3.11.15 (conda env: ndm-calibrator) |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| pandas | 3.0.5 |
| sympy | 1.14.0 |
| matplotlib | 3.11.0 |
| PySide6 | 6.11.1 |
| pyqtgraph | 0.14.0 |
| openpyxl | (conda) |
| pytest | 9.0.3 |

## 运行命令

```
QT_QPA_PLATFORM=offscreen python -m pytest tests
```

## 结果

```
96 passed, 1 warning in 117.92s (0:01:57)
```

| 统计 | 值 |
| --- | --- |
| passed | 96 |
| failed | 0 |
| skipped | 0 |
| warnings | 1 (RuntimeWarning: overflow in test discrete solver, 测试预期) |

## 覆盖

- Core: 参数验证 / 项目序列化 / 模型解析 / 注入防护;
- Simulation: 指数衰减解析对照 (<1e-4) / 一阶稳态与上升时间 / 4 种积分器 / 插值 / 发散处理;
- Identification: 四种算法参数恢复 (一阶 K=2.5±0.1, τ=6.0±0.3) / DE·Multi-start 可重复 / seed 记录;
- Diagnostics: 手工可算指标 / ACF / 敏感性解析对照 / 秩亏·高相关检测;
- Uncertainty: Bootstrap 维度·可重复·区间覆盖 / 稳定性统计;
- Data: 加载 / 映射 / 校验 / 预处理;
- GUI smoke: 14 项 (窗口 / 导航 / 主题 / 侧栏 / 参数表 / 空·结果·错误状态)。

## 数值正确性验收

- 指数衰减无噪声: `|k̂ − 0.35| < 1e-4` ✓;
- 一阶低噪声: `K̂ ≈ 2.499 (真值 2.5)`, `τ̂ ≈ 5.995 (真值 6.0)` ✓;
- 固定 seed 重复: DE / Bootstrap 结果逐位一致 ✓;
- 错误模型: 拟合较差但如实报告 RMSE 与残差结构 ✓。
