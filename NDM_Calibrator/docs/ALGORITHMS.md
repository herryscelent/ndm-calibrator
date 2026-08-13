# 算法说明 — NDM-Calibrator V1.0

## 1. 目标函数

默认加权最小二乘目标:

J(θ) = (1/N) · Σᵢ Σⱼ wⱼ (yᵢⱼ − ŷᵢⱼ(θ))²

支持目标类型: `sse` / `mse` / `rmse` / `mae` / `huber`。
多输出模型对各输出加权聚合。`huber` 的 δ 可配置。

## 2. 数值求解

连续模型统一通过 `scipy.integrate.solve_ivp`:

- 方法: RK45 (默认) / DOP853 / Radau / BDF;
- 容差: rtol, atol 可配置; max_step 可选;
- 输入 u(t) 通过 **zero-order hold** 或 **线性插值** 在积分器所需时间点取值;
- 处理不规则观测时间点 (t_eval = 实验时间点)。

积分失败/发散时返回明确状态, 不抛出异常:

- NaN/Inf;
- 状态绝对值超过 `1e20` (爆炸)。

## 3. 参数辨识算法

### 3.1 非线性最小二乘 (least_squares)

基于 `scipy.optimize.least_squares`, 方法 `TRF` / `Dogbox`。
残差向量按输出拼接, 支持多输出同时拟合。加权通过 sqrt(w)·(measured−predicted)。

> 注: 经典的 LM (`method='lm'`) 不支持边界约束, 本软件不将其作为独立选项暴露。

### 3.2 Nelder-Mead

无梯度局部搜索 (`scipy.optimize.minimize`)。因 Nelder-Mead 不支持硬边界,
采用软罚函数将参数约束在边界内。

### 3.3 Differential Evolution

全局搜索 (`scipy.optimize.differential_evolution`), 可配置:

- population size;
- mutation;
- recombination;
- max iterations;
- seed (可重复)。

### 3.4 Multi-start Least Squares

在参数边界内生成 M 个初值 (分层抽样 + 洗牌), 分别运行局部最小二乘,
按目标值排序, 返回最优解并保留全部局部解供稳定性分析。

## 4. 可重复性

所有随机算法 (DE / Multi-start / Bootstrap) 使用 `np.random.default_rng(seed)`,
相同数据+模型+配置+seed 得到可重复结果; seed 记录在结果中。

## 5. 校准指标

每个输出独立计算并汇总 (均值):

- SSE / MSE / RMSE / MAE;
- R² (R² = 1 − SSE/(N·Var(y)));
- 最大绝对误差;
- Mean Error (残差均值)。

## 6. 残差诊断

- 残差均值/标准差/极值;
- 残差时序图;
- 残差自相关 ACF (前 N 个 lag, 阈值 |ACF| > 1.96/√n);
- 当超过阈值 lag 数 ≥ 3 时给出统计提示: "残差可能仍存在未建模动态结构"。

> 该提示是统计诊断, 不构成绝对判断。

## 7. 参数敏感性

在最优参数 θ̂ 处, 用中心有限差分估计 Jacobian:

Sᵢⱼ = ∂ŷᵢ/∂θⱼ

步长为相对扰动 `step_frac × |θⱼ|` (默认 1e-3), 处理参数尺度差异。
提供原始灵敏度与归一化灵敏度 (θⱼ/|y| 缩放)。

## 8. 可辨识性诊断

在最优解处构造 F = JᵀJ, 输出:

- 奇异值;
- 条件数;
- 近似协方差 (JᵀJ)⁻¹·σ²;
- 参数相关矩阵 ρᵢⱼ = Cᵢⱼ/√(Cᵢᵢ·Cⱼⱼ)。

警告规则 (阈值在 `app/constants.py`):

- 秩亏 (rank < 参数数) → 明确提示部分参数不可辨识;
- |ρ| > 0.95 → "高度相关, 参数可能难以独立辨识";
- 条件数 > 1e12 → 提示对噪声敏感。

## 9. 参数可信度

### Multi-start Stability

对多个起点结果统计每个参数的均值/标准差/变异系数/最优值/成功率,
变异系数 > 0.5 标记为高变异。

### Bootstrap (residual bootstrap)

1. 用最优参数计算拟合值;
2. 计算残差;
3. 有放回抽样残差;
4. 构造 bootstrap 数据;
5. 重新辨识;
6. 重复 B 次 (默认 100, 上限 1000)。

输出每个参数的 mean/std/median/2.5%/97.5% 分位数,
即 **Bootstrap percentile interval** (明确标注, 非严格置信区间)。
