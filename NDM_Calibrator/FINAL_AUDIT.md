# FINAL AUDIT — NDM-Calibrator V1.0

审计时间: 2026-08-13

## 审计项

| # | 检查项 | 结果 | 说明 |
| --- | --- | --- | --- |
| 1 | 是否存在未使用模块 | PASS | 全部目录有实际代码; `visualization/` 提供 Matplotlib 静态图模块 |
| 2 | 是否存在 GUI 空按钮 | PASS | 所有按钮连接真实槽函数 (导入/辨识/导出/主题等) |
| 3 | 是否存在 TODO/FIXME | PASS | 代码中无 TODO/FIXME 遗留 |
| 4 | 是否存在 hard-coded example result | PASS | 结果均由算法实时计算, 无写死数值 |
| 5 | 是否存在 bare `except:` | PASS | 异常均指定类型或记日志后抛出领域异常 |
| 6 | 是否存在未设置 seed 的随机路径 | PASS | DE/Multi-start/Bootstrap 均使用 `np.random.default_rng(seed)` |
| 7 | 是否存在错误的统计学描述 | PASS | Bootstrap 区间明确标注 "Bootstrap percentile interval", 残差提示为统计诊断 |
| 8 | 是否存在项目保存后无法恢复的状态 | PASS | 保存/重开 roundtrip 测试覆盖模型/参数/实验/结果 |
| 9 | 是否存在文档声称支持但代码未支持的功能 | WARN | `visualization/` 在初始架构中为预留; 现已提供 Matplotlib 图; PyInstaller exe 未实际构建验证 |
| 10 | 软件名称和版本是否统一 | PASS | 全部使用 "非线性动态模型参数辨识与校准软件" / "NDM-Calibrator" / "V1.0" |

## 结论

- PASS: 8
- WARN: 1 (PyInstaller exe 未在当前环境实际构建验证, 仅提供 spec 与构建脚本)
- FAIL: 0

### WARN 处理

第 9 项 WARN 已在审计后改进: `visualization/figures.py` 提供真实 Matplotlib 图函数。
PyInstaller exe 构建因需要较长时间且非核心交付, 已按要求提供
`NDM_Calibrator.spec` 与 `scripts/build_windows.ps1`, 并在本审计中如实标注未验证。
