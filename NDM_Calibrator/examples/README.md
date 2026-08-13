# 示例案例

示例数据均由 `scripts/generate_examples.py` 用固定 seed 生成
(真实模型 + 轻微噪声), 每个示例附带 `metadata.json` 记录真值与推荐算法。

| 示例 | 模型 | 真实参数 | 推荐算法 |
| --- | --- | --- | --- |
| exponential_decay | 指数衰减 dx/dt = -k·x | k=0.35 | least_squares |
| first_order | 一阶惯性 dx/dt = (-x+K·u)/τ | K=2.5, τ=6.0 | least_squares |
| second_order | 二阶弹簧阻尼 | k=30, c=2 (m=1 固定) | least_squares |
| cubic_nonlinear | 非线性 -a·x-b·x³+c·u | a=0.5, b=0.8, c=1.2 | differential_evolution |

## 在软件中使用

1. 新建项目;
2. 数据管理 → 导入 `data.csv`;
3. 选择对应内置模型;
4. 参数配置 (可用 metadata 中的真值作为参考初始);
5. 运行推荐算法;
6. 对比辨识结果与 `metadata.json` 中的 `expected_range`。

## 重新生成

```powershell
python scripts\generate_examples.py
```
