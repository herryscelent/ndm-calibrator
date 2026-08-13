# 模型定义格式 — NDM-Calibrator V1.0

## 概述

模型由状态、输入、参数、动态方程（ODE）、输出与输出方程组成。
软件支持两种来源：

1. **内置模型模板** — 在 UI 中直接选择；
2. **用户自定义模型** — 以文本格式输入，经 SymPy 安全解析。

## 内置模型

| 模板 | 方程 | 参数 | 说明 |
| --- | --- | --- | --- |
| 指数衰减 | dx/dt = -k·x | k | 衰减 |
| 一阶惯性 | dx/dt = (-x + K·u)/τ | K, τ | 一阶动态 |
| 二阶弹簧阻尼 | dx1/dt=x2; dx2/dt=(-k·x1 - c·x2 + u)/m | k, c, m | 二阶 |
| Logistic | dx/dt = r·x·(1 - x/K) | r, K | 生长 |
| 非线性三次 | dx/dt = -a·x - b·x³ + c·u | a, b, c | 非线性 |

## 用户自定义模型格式

文本格式（UI 中编辑）：

```text
states:
x1
x2

inputs:
u

parameters:
k
c
b

dx1/dt = x2
dx2/dt = -k*x1 - c*x2 + b*u

outputs:
y

y = x1
```

### 语法说明

- `states` / `inputs` / `parameters` / `outputs` 小节后每行一个符号名;
- 动态方程形式 `dx<name>/dt = <表达式>`, 每个状态必须恰好一条;
- 输出方程 `<输出名> = <表达式>`; 若未提供输出方程, 输出默认等于同名状态;
- 支持函数: `sin cos tan exp log sqrt abs sign tanh` (以及 `ln` 别名);
- 运算符: `+ - * / **` (幂), 括号, 数字常量;
- 可选 `#` 注释行。

### 示例

指数衰减自定义形式:

```text
states:
x

parameters:
k

dx/dt = -k*x

outputs:
x
```

## 安全解析

- **禁止 `eval()`**; 所有表达式经 SymPy `sympify` 解析;
- 使用白名单函数集与显式符号集合, 未定义符号会被拒绝;
- 检测并拒绝: 未定义变量、符号重名、缺失方程、缺失初始条件。

## 序列化

模型以 `model.json` 存入 `.ndmc` 项目文件:

```json
{
  "kind": "builtin",
  "builtin_key": "first_order"
}
```

用户自定义模型保存完整定义:

```json
{
  "kind": "user",
  "states": ["x1", "x2"],
  "inputs": ["u"],
  "parameters": ["k", "c", "b"],
  "dynamics": {"dx1/dt": "x2", "dx2/dt": "-k*x1 - c*x2 + b*u"},
  "outputs": ["x1"],
  "output_equations": {"x1": "x1"},
  "initial_conditions": {"x1": 0.0, "x2": 0.0},
  "description": "用户自定义模型"
}
```
