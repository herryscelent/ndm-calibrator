# ARCHITECTURE — NDM-Calibrator V1.0

## 1. 总体架构

分层结构, UI 与数值逻辑解耦:

```
┌──────────────────────────────────────────────┐
│ ui/  桌面 GUI (PySide6)                      │
│  ├─ design/   设计令牌/主题/图标             │
│  ├─ components/ 可复用组件                   │
│  ├─ plots/    PyQtGraph 交互图               │
│  ├─ pages/    业务页面                       │
│  └─ adapters/ 结果 → UI 数据适配器           │
├──────────────────────────────────────────────┤
│ app/  应用层 (Application 门面/入口/常量)    │
├──────────────────────────────────────────────┤
│ core/ 领域对象 (Project/Model/Parameter/...) │
├──────────────────────────────────────────────┤
│ data/ simulation/ identification/            │
│ diagnostics/ uncertainty/ export/            │
│   数值与业务服务                             │
└──────────────────────────────────────────────┘
```

核心原则:

- UI 只通过 `Application` 门面访问业务逻辑;
- 页面不直接依赖 scipy/SymPy 内部细节, 通过 `ui/adapters` 读取结果;
- 长任务在 `QThread` 中运行 (见 `ui/workers.py`), 支持取消;
- 异常在服务层抛出领域异常 (`core/exceptions.py`), UI 捕获后友好提示。

## 2. 数据流

```
实验数据 (CSV/XLSX)
   → data/loader 读取
   → data/mapping 映射为 Experiment (time/inputs/outputs)
   → data/validator 质量检查
   → data/preprocessing 预处理 (drop/interpolate/range)
模型定义 (内置模板 / 用户 SymPy 表达式)
   → core/model_definition 安全解析与验证
   → simulation/simulator 数值求解 (solve_ivp)
参数辨识
   → identification/* 目标函数 + 优化算法
   → identification/result 结果对象
校准与诊断
   → diagnostics/* 指标/残差/敏感性/可辨识性
可信度
   → uncertainty/* bootstrap / stability
持久化
   → core/project (.ndmc ZIP)
导出
   → export/* Excel/CSV/图片/HTML
```

## 3. 关键模块

### core/project.py

`.ndmc` 为 ZIP 容器, 包含 `project.json`/`model.json`/`parameters.json`/
`settings.json`/`results/results.json`/`data/experiment.json` 与 `manifest.json`
(schema version 1.0)。打开时校验 schema 与必备成员, 损坏时抛出
`CorruptedProjectError`。

### core/model_definition.py

用户表达式通过 SymPy `sympify` 解析, 使用白名单函数
(sin/cos/tan/exp/log/sqrt/abs 等) 与显式符号集合, **禁止 `eval()`**。
解析后校验: 未定义符号、重名、方程数量与状态数量匹配、初始条件完整。

### simulation/simulator.py

对每个参数集, 将参数代入符号表达式后 `lambdify` 一次, 构造 `rhs(t,x)`;
输入 u(t) 通过 ZOH / 线性插值在积分器所需时间点求值。`solve_ivp`
(RK45 默认) 求解, 失败/发散返回状态而非抛出。

### identification/base.py

`IdentificationContext` 封装目标函数: 固定参数 + 自由参数 → 模拟 → 目标值。
目标类型: sse/mse/rmse/mae/huber, 多输出加权聚合。

### diagnostics/identifiability.py

在最优参数处用中心差分构造 Jacobian J, 计算 `F=JᵀJ` 的奇异值、条件数、
近似协方差与参数相关矩阵; 高相关 (>0.95) 与秩亏给出统计提示, 阈值在
`app/constants.py`。

### uncertainty/bootstrap.py

Residual bootstrap: 用最优参数算拟合值与残差 → 有放回抽样 → 构造伪数据 →
重辨识 → B 次。输出 percentile interval (2.5%/97.5%), 明确标注为
**Bootstrap percentile interval**, 非严格统计置信区间。

## 4. 可重复性

所有随机算法 (DE / Multi-start / Bootstrap) 接受 `seed`, 使用
`np.random.default_rng(seed)`, 结果中记录 seed。

## 5. 设计取舍 (记录)

- 求解失败不抛出, 返回 (success=False, message) 以便优化器/UI 优雅降级;
- least_squares 的残差向量按输出拼接, 支持多输出同时拟合;
- Nelder-Mead 不支持边界, 采用软罚函数纳入边界;
- 发散判定阈值 `1e20` (状态绝对值), 覆盖"有限但爆炸"的情况;
- Bootstrap 默认 B=100, 上限 1000, 防止桌面死机;
- 报告图使用 Matplotlib (白底出版风格), 应用内交互图使用 PyQtGraph。
