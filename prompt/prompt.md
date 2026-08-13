# Codex 开发任务：非线性动态模型参数辨识与校准软件 V1.0

## 0. 任务目标

请从零开发一套完整、可运行、可测试、具有桌面 GUI 的：

**《非线性动态模型参数辨识与校准软件 V1.0》**

英文内部项目名：

`NDM-Calibrator`

本项目不是科研论文 Demo，也不是简单地给 `scipy.optimize.curve_fit` 包一层 GUI。

软件必须形成完整工作流：

**项目创建 → 数据导入 → 动态模型定义 → 参数配置 → 数值求解 → 参数辨识 → 模型校准 → 残差与可辨识性诊断 → 参数可信度分析 → 结果可视化 → 项目保存 → 结果导出**

最终应达到“一个普通用户可以独立完成一次动态模型参数辨识任务”的完整软件程度。

---

# 1. 技术栈

优先使用：

* Python 3.11+
* PySide6
* NumPy
* SciPy
* pandas
* SymPy
* matplotlib
* openpyxl
* pytest

允许增加少量必要的成熟依赖，但必须：

1. 在 `requirements.txt` 中固定版本范围；
2. 不引入重量级 Web 框架；
3. 不需要云服务器；
4. 不需要 GPU；
5. 不需要 Docker 才能运行；
6. Windows 10/11 本地可直接运行。

软件采用桌面 GUI。

不得开发成 Jupyter Notebook 项目。

---

# 2. 软件数学对象

软件面向非线性动态模型。

连续时间模型：

[
\dot{x}(t)=f(x(t),u(t),\theta,t)
]

[
y(t)=g(x(t),u(t),\theta,t)
]

离散时间模型：

[
x_{k+1}=f(x_k,u_k,\theta,k)
]

[
y_k=g(x_k,u_k,\theta,k)
]

其中：

* (x)：状态变量；
* (u)：已知输入变量；
* (y)：观测输出；
* (\theta)：待辨识模型参数。

核心参数辨识问题：

[
\theta^*
========

\arg\min_{\theta\in\Omega}J(\theta)
]

默认加权最小二乘目标：

[
J(\theta)=
\frac{1}{N}
\sum_{i=1}^{N}
\sum_{j=1}^{m}
w_j
\left(
y_{ij}-\hat y_{ij}(\theta)
\right)^2
]

同时支持：

* SSE
* MSE
* RMSE 型目标
* MAE 型目标
* Huber robust loss

---

# 3. 产品边界

V1.0 只解决：

**根据已有实验/观测时序数据，对用户定义的非线性动态模型中的未知参数进行辨识、校准和可信度分析。**

明确不要加入：

* 神经网络
* 深度学习
* 大语言模型
* CFD
* 有限元
* 数字孪生
* 云计算
* 在线数据库
* 实时硬件通讯
* 多目标 Pareto 优化
* MCMC 贝叶斯推断
* GPU 加速
* 用户登录/权限管理
* 网络服务端

不要为了增加功能而偏离软件核心目标。

---

# 4. 软件总体架构

至少按照以下结构组织代码：

```text
NDM_Calibrator/
├─ app/
│  ├─ main.py
│  ├─ application.py
│  └─ constants.py
│
├─ core/
│  ├─ project.py
│  ├─ model_definition.py
│  ├─ parameter.py
│  ├─ experiment.py
│  ├─ objective.py
│  └─ exceptions.py
│
├─ data/
│  ├─ loader.py
│  ├─ validator.py
│  ├─ preprocessing.py
│  └─ mapping.py
│
├─ simulation/
│  ├─ ode_solver.py
│  ├─ discrete_solver.py
│  ├─ interpolation.py
│  └─ simulator.py
│
├─ identification/
│  ├─ base.py
│  ├─ least_squares.py
│  ├─ nelder_mead.py
│  ├─ differential_evolution.py
│  ├─ multistart.py
│  └─ result.py
│
├─ diagnostics/
│  ├─ metrics.py
│  ├─ residuals.py
│  ├─ sensitivity.py
│  ├─ identifiability.py
│  └─ correlation.py
│
├─ uncertainty/
│  ├─ bootstrap.py
│  ├─ confidence_interval.py
│  └─ stability.py
│
├─ visualization/
│  ├─ fitting_plot.py
│  ├─ residual_plot.py
│  ├─ convergence_plot.py
│  ├─ parameter_plot.py
│  ├─ correlation_plot.py
│  └─ bootstrap_plot.py
│
├─ export/
│  ├─ excel_exporter.py
│  ├─ csv_exporter.py
│  ├─ figure_exporter.py
│  └─ report_exporter.py
│
├─ ui/
│  ├─ main_window.py
│  ├─ widgets/
│  └─ pages/
│     ├─ welcome_page.py
│     ├─ data_page.py
│     ├─ model_page.py
│     ├─ parameter_page.py
│     ├─ identification_page.py
│     ├─ calibration_page.py
│     ├─ diagnostics_page.py
│     ├─ uncertainty_page.py
│     └─ export_page.py
│
├─ examples/
├─ tests/
├─ docs/
├─ scripts/
├─ requirements.txt
├─ README.md
└─ pyproject.toml
```

可以根据实际工程需要调整，但必须保持：

**UI、数据、模型、求解、辨识、诊断、不确定性、导出相互解耦。**

严禁将所有逻辑堆进一个 `main.py`。

---

# 5. 模块一：项目管理

实现完整项目生命周期。

## 功能

支持：

* 新建项目
* 打开项目
* 保存项目
* 另存为
* 最近项目
* 项目基本信息
* 自动检测未保存修改
* 退出前提示保存

设计专用项目格式：

`.ndmc`

建议其内部采用 ZIP 容器，包括：

```text
project.json
model.json
parameters.json
settings.json
data/
results/
manifest.json
```

要求：

* 项目文件可重新打开；
* 打开后恢复数据映射、模型、参数、算法和结果；
* 做 schema version；
* 当前 schema 为 `1.0`；
* 对损坏项目给出友好错误信息。

---

# 6. 模块二：数据导入与管理

支持：

* CSV
* XLSX

用户导入后展示：

* 行数
* 列数
* 列名
* 数据类型
* 缺失值数量
* 最小值
* 最大值
* 均值
* 标准差

## 字段映射

用户必须能够指定：

* 时间列
* 一个或多个输入变量
* 一个或多个输出变量
* 可忽略变量

例如：

```text
time -> 时间
heater_power -> 输入
temperature -> 输出
ambient_temperature -> 输入
```

## 数据检查

自动检查：

* 时间是否单调递增
* 重复时间戳
* NaN
* Inf
* 非数值数据
* 时间间隔统计
* 数据长度
* 空数据

对异常数据不能直接崩溃。

## 基础预处理

V1.0 支持：

* 删除缺失行
* 线性插值缺失值
* 选择数据时间区间
* 数据预览
* 原始曲线可视化

所有预处理操作必须记录到项目配置中。

---

# 7. 模块三：动态模型定义

这是软件核心之一。

必须支持两种模式。

## A. 内置模型模板

至少提供：

### 1. 指数衰减模型

[
\dot x=-kx
]

### 2. 一阶惯性系统

[
\dot x=
-\frac{x}{\tau}
+
\frac{K}{\tau}u
]

### 3. 二阶质量-弹簧-阻尼模型

[
\dot x_1=x_2
]

[
\dot x_2=
-\frac{k}{m}x_1
-\frac{c}{m}x_2
+\frac{1}{m}u
]

### 4. Logistic 动态模型

[
\dot x=rx(1-x/K)
]

### 5. 简单非线性动态模型示例

例如：

[
\dot x=-a x-bx^3+cu
]

---

## B. 用户自定义模型

用户可定义：

* 状态变量
* 输入变量
* 输出变量
* 参数
* 初始状态
* 动态方程
* 输出方程

例如：

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
y = x1
```

### 安全要求

禁止直接对用户字符串执行 Python `eval()`。

使用 SymPy 或其他安全方式：

* 白名单函数
* 白名单符号
* 表达式解析
* 数学函数校验

支持基本函数：

* sin
* cos
* tan
* exp
* log
* sqrt
* abs

检测：

* 未定义变量
* 重名
* 非法表达式
* 方程数量与状态数量不匹配
* 参数缺失
* 初始条件缺失

模型保存前必须执行验证。

---

# 8. 模块四：参数配置

提供表格式参数编辑器。

字段：

| 参数  |  初值 |   下限 |  上限 | 状态  |
| --- | --: | ---: | --: | --- |
| K   | 1.0 | 0.01 |  20 | 待辨识 |
| tau |   5 | 0.01 | 100 | 待辨识 |

参数状态：

* Free / 待辨识
* Fixed / 固定

必须校验：

[
lower < initial < upper
]

允许用户：

* 新增参数
* 删除参数
* 修改参数
* 固定参数
* 恢复默认
* 从模型同步参数

---

# 9. 模块五：动态模型数值求解

连续模型统一通过：

`scipy.integrate.solve_ivp`

至少支持：

* RK45
* DOP853
* Radau
* BDF

默认：

`RK45`

配置：

* rtol
* atol
* max_step

处理不规则观测时间点。

输入 (u(t)) 通过插值获得。

至少实现：

* zero-order hold
* linear interpolation

若积分失败：

* 捕获错误
* 返回明确状态
* 不让 GUI 崩溃

---

# 10. 模块六：参数辨识

必须实现四类辨识方式。

## A. 非线性最小二乘

基于：

`scipy.optimize.least_squares`

支持：

* TRF
* Dogbox

如条件允许，可提供 LM，但需明确 LM 对 bounds 的限制。

---

## B. Nelder-Mead

用于无梯度局部搜索。

---

## C. Differential Evolution

用于全局参数搜索。

支持设置：

* population size
* mutation
* recombination
* max iterations
* seed

---

## D. Multi-start Least Squares

自动在参数边界内生成多个初值：

[
\theta_0^{(1)},...,\theta_0^{(M)}
]

分别求解。

最后：

* 按目标函数排序；
* 返回最佳解；
* 保存全部局部解；
* 展示局部最优分布。

---

# 11. 可重复性

所有涉及随机过程的功能必须支持：

`random_seed`

例如：

* Differential Evolution
* Multi-start
* Bootstrap

相同：

* 数据
* 模型
* 配置
* seed

应尽可能得到可重复结果。

结果中必须记录 seed。

---

# 12. 优化运行管理

优化页面必须展示：

* 当前算法
* 当前迭代/评估次数
* 当前 best loss
* 当前 best parameters
* 运行时间
* 状态

支持：

* 开始
* 取消
* 清除结果

长计算不能冻结 GUI。

使用：

* `QThread`
* 或 `QRunnable/QThreadPool`

计算必须在工作线程运行。

取消操作需要是安全的。

---

# 13. 模块七：模型校准与评价

参数辨识完成后自动计算：

* SSE
* MSE
* RMSE
* MAE
* (R^2)
* 最大绝对误差
* Mean Error

多输出模型：

分别计算各输出指标，同时提供汇总指标。

绘制：

### 实测—模拟时序图

同时显示：

* measured
* simulated

### 实测 vs 模拟散点图

增加：

[
y=x
]

参考线。

### 误差时序图

展示：

[
e_i=y_i-\hat y_i
]

---

# 14. 模块八：残差诊断

实现：

* 残差均值
* 残差标准差
* 残差直方图
* 残差时序图
* 残差 vs 预测值
* 残差自相关 ACF

ACF 至少实现前若干 lag。

允许用户设置最大 lag。

如果残差存在明显系统结构，在结果区给出：

“残差可能仍存在未建模动态结构”

注意：

此类提示必须写成统计诊断提示，不得做没有依据的绝对判断。

---

# 15. 参数敏感性分析

在最优参数：

[
\hat\theta
]

附近计算局部参数敏感性。

使用有限差分：

[
S_{ij}
======

\frac{\partial \hat y_i}
{\partial\theta_j}
]

需要合理处理：

* 参数尺度差异
* 极小参数
* 参数边界

提供：

* 原始 sensitivity
* normalized sensitivity

绘制参数敏感度图。

---

# 16. 参数可辨识性诊断

基于局部 Jacobian：

[
J
]

计算近似：

[
F=J^T J
]

输出：

* singular values
* condition number
* covariance approximation
* parameter correlation matrix

参数相关系数：

[
\rho_{ij}
=========

\frac{C_{ij}}
{\sqrt{C_{ii}C_{jj}}}
]

对高相关参数给出警告。

例如：

```text
|rho| > 0.95:
高度相关，参数可能难以独立辨识
```

阈值放入常量配置，不要散布 magic numbers。

对于：

* 奇异矩阵
* rank deficiency
* 样本不足

必须给出明确提示。

不得伪造置信度。

---

# 17. 模块九：参数可信度分析

V1.0 实现两部分。

## A. Multi-start Stability

对多个初值结果统计：

* 均值
* 标准差
* 最小值
* 最大值
* 变异系数
* 最优值
* 成功率

绘制不同起点最终参数分布。

---

## B. Bootstrap

至少实现 residual bootstrap。

流程：

1. 用最优参数得到拟合值；
2. 计算残差；
3. 对残差进行有放回抽样；
4. 构造 bootstrap 数据；
5. 重新辨识；
6. 重复 B 次。

用户可配置：

* B
* seed
* algorithm

默认 B 应适合桌面试运行，例如：

`100`

不能默认设置成极其耗时的 10,000。

输出每个参数：

* mean
* std
* median
* 2.5 percentile
* 97.5 percentile

即 percentile 95% interval。

明确在 UI 中称：

**Bootstrap percentile interval**

避免把所有 interval 都模糊称为严格统计置信区间。

绘制：

* 参数 histogram
* boxplot
* bootstrap distribution

---

# 18. 算法结果比较

用户运行多种算法后，可以进入“算法比较”。

展示：

| Algorithm | Objective | RMSE | Runtime | Evaluations | Success |
| --------- | --------: | ---: | ------: | ----------: | ------- |

允许选择任意结果作为：

**当前校准方案**

切换当前方案后：

* 参数结果
* 拟合图
* 残差
* 诊断

同步更新。

---

# 19. GUI 页面

主窗口使用左侧导航栏 + 右侧工作区。

建议页面：

```text
项目首页
数据管理
模型定义
参数配置
参数辨识
模型校准
诊断分析
可信度分析
结果导出
```

顶部：

* 软件名称
* 当前项目
* 保存状态

底部状态栏：

* Ready
* Loading...
* Running identification...
* Completed
* Error

---

# 20. UI 设计要求

界面风格：

* 简洁
* 工程软件风格
* 不追求花哨动画
* 信息密度适中
* 支持 1920×1080
* 最低兼容 1366×768

必须保证：

* 按钮命名统一
* 输入框有单位/说明
* 错误提示明确
* 不显示 Python traceback 给普通用户
* traceback 写入日志

图表：

* 可缩放
* 可保存 PNG
* 坐标名称和单位清晰
* 图例完整
* 不使用无意义 3D 图表

---

# 21. 日志系统

使用 Python `logging`。

记录：

* 软件启动
* 项目打开/保存
* 数据加载
* 模型验证
* 参数辨识开始
* 参数辨识结束
* 算法失败
* Bootstrap
* 导出
* uncaught exception

日志写入：

```text
logs/
```

---

# 22. 示例案例

必须随项目提供至少 4 个完全可运行的示例。

## Example 1：指数衰减

真实：

[
k=0.35
]

生成带轻微噪声数据。

要求软件能够恢复接近真实值的参数。

---

## Example 2：一阶动态系统

[
\dot x=-x/\tau+(K/\tau)u
]

真实：

```text
K = 2.5
tau = 6.0
```

使用阶跃或分段输入。

---

## Example 3：二阶质量弹簧阻尼

辨识：

* k
* c

m 固定。

---

## Example 4：非线性模型

[
\dot x=-a x-bx^3+cu
]

至少辨识：

* a
* b
* c

---

每个示例包含：

* CSV 数据
* 模型配置
* 参数真值
* README
* 推荐算法
* 期望结果范围

示例数据使用代码生成，不要伪装成真实实验数据。

---

# 23. 数据生成器

提供：

`scripts/generate_examples.py`

重新生成全部 synthetic examples。

固定 seed。

输出真值 metadata。

---

# 24. 导出系统

至少支持：

## Excel

一个 `.xlsx` 文件包含：

* Project Summary
* Parameters
* Metrics
* Algorithm Comparison
* Residual Statistics
* Identifiability
* Bootstrap Results

---

## CSV

支持独立导出：

* 参数
* 模拟序列
* 残差
* bootstrap samples

---

## 图片

支持：

* PNG
* SVG（如果实现成本合理）

---

## 分析报告

生成本地分析报告。

优先：

* HTML
* PDF 可作为附加功能

报告内容：

1. 项目信息
2. 数据摘要
3. 模型定义
4. 参数配置
5. 辨识算法
6. 参数估计结果
7. 拟合指标
8. 拟合曲线
9. 残差分析
10. 参数可辨识性
11. Bootstrap
12. 软件版本
13. 随机种子
14. 生成时间

---

# 25. 异常处理

需要系统测试以下错误：

* 文件不存在
* CSV 编码错误
* Excel 无数据
* 时间列包含字符串
* 时间不递增
* 数据全 NaN
* 参数范围错误
* 模型表达式非法
* 未定义符号
* ODE 积分失败
* 参数导致 NaN
* 参数导致爆炸
* 优化器失败
* 用户中途取消
* Bootstrap 部分失败
* 项目文件损坏

任何一个普通输入错误都不能导致应用直接退出。

---

# 26. 测试要求

使用：

`pytest`

至少覆盖：

## Core

* 参数验证
* 项目序列化
* 项目反序列化
* 模型解析

## Simulation

* 指数模型解析解对照
* 一阶系统结果
* interpolation

## Identification

用 synthetic data 验证参数恢复。

例如：

[
k_{true}=0.35
]

要求：

[
|\hat k-k_{true}|< tolerance
]

合理定义 tolerance。

## Metrics

使用人工可计算案例验证：

* RMSE
* MAE
* R²

## Diagnostics

* Jacobian shape
* correlation
* rank deficient case

## Bootstrap

* seed reproducibility
* output dimensions
* failure handling

## Persistence

保存 `.ndmc` → 打开 → 比较核心内容一致。

---

# 27. 代码质量

要求：

* type hints
* docstrings
* dataclasses / typed models
* 不使用大量全局变量
* 避免循环 import
* 避免巨大函数
* UI 与算法逻辑分离
* 不复制粘贴大量相同代码
* 不用注释凑代码行
* 不留下空壳模块
* 不留 TODO 作为“已实现功能”

核心业务逻辑必须有测试。

---

# 28. 性能要求

普通示例数据：

* N < 10,000
* 参数数量 < 20

软件应能够正常工作。

不要求高性能计算。

对于 Bootstrap / DE 等耗时操作：

* GUI 不冻结
* 有进度状态
* 可取消
* 结束后释放 worker

---

# 29. 软件信息

统一使用：

**中文名称：**
非线性动态模型参数辨识与校准软件

**版本：**
V1.0

**内部名称：**
NDM-Calibrator

任何：

* GUI
* README
* About
* 示例
* 导出报告
* 文档

不得出现互相冲突的软件名称或版本号。

---

# 30. 文档

生成：

```text
docs/
├─ ARCHITECTURE.md
├─ USER_GUIDE.md
├─ MODEL_FORMAT.md
├─ ALGORITHMS.md
├─ TESTING.md
└─ CHANGELOG.md
```

README 必须包含：

* 软件介绍
* 环境要求
* 安装方法
* 启动方法
* 测试方法
* 示例方法
* 目录结构

---

# 31. Windows 启动方式

提供：

`run.bat`

例如完成：

1. 检查 Python；
2. 检查/提示虚拟环境；
3. 启动应用。

另外 README 给出命令：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

---

# 32. 可执行文件构建

如果当前环境允许，增加 PyInstaller 配置：

```text
NDM_Calibrator.spec
```

提供：

```text
scripts/build_windows.ps1
```

能够生成 Windows 可执行版本。

如果当前执行环境不是 Windows：

* 不要假装已经成功构建 Windows exe；
* 只提交构建脚本；
* 在最终报告中明确说明未实际验证 Windows exe。

---

# 33. 开发阶段要求

不要一次性堆完代码后才测试。

按照以下顺序开发：

### Phase 1

项目骨架、数据结构、项目持久化。

### Phase 2

模型解析与数值求解。

### Phase 3

参数辨识。

### Phase 4

校准与诊断。

### Phase 5

Bootstrap 与稳定性。

### Phase 6

GUI。

### Phase 7

示例、测试、导出。

### Phase 8

完整集成测试和打包。

每阶段完成后运行相应测试。

---

# 34. 最终验收场景

必须实际运行下面的 E2E 流程：

1. 启动软件；
2. 新建项目；
3. 导入 Example 2；
4. 映射 time/u/y；
5. 选择一阶惯性模型；
6. 设置 K、tau；
7. 运行 Least Squares；
8. 得到 K、tau 估计；
9. 查看 fitted vs measured；
10. 查看 residual；
11. 查看 sensitivity；
12. 查看 parameter correlation；
13. 运行 multi-start；
14. 运行小规模 Bootstrap；
15. 保存项目；
16. 关闭；
17. 重新打开项目；
18. 验证结果仍存在；
19. 导出 Excel；
20. 导出分析报告。

该流程不能依赖人工修改源代码。

---

# 35. 数值正确性验收

至少满足：

### 指数衰减无噪声案例

辨识结果应非常接近真实参数。

### 一阶系统低噪声案例

K、tau 应恢复到合理误差范围。

### 固定 seed

DE / Bootstrap 重复运行必须具有可重复性。

### 错误模型

软件应允许拟合较差，但不能伪造“成功”。

报告应真实展示较差 RMSE 和残差结构。

---

# 36. 禁止行为

不得：

* 为增加代码量生成无意义类；
* 用注释凑行数；
* 创建大量重复文件；
* 把按钮做出来但无功能；
* 捕获所有 exception 后静默忽略；
* 写死示例结果；
* 伪造测试通过；
* 删除失败测试来得到绿色结果；
* 伪造 Windows exe 构建成功；
* 使用随机常数作为所谓“算法结果”；
* 使用 `eval()` 直接执行用户输入；
* 把 README 宣传内容当成实际功能。

---

# 37. 最终代码审计

完成实现后自行进行一次 audit：

检查：

1. 是否存在未使用模块；
2. 是否存在 GUI 空按钮；
3. 是否存在 TODO/FIXME；
4. 是否存在 hard-coded example result；
5. 是否存在 bare `except:`;
6. 是否存在未设置 seed 的随机路径；
7. 是否存在错误的统计学描述；
8. 是否存在项目保存后无法恢复的状态；
9. 是否存在文档声称支持但代码未支持的功能；
10. 软件名称和版本是否统一。

生成：

`FINAL_AUDIT.md`

列出：

* PASS
* WARN
* FAIL

有 FAIL 时先修复，再重新审计。

---

# 38. 测试记录

最终运行：

```bash
pytest -q
```

以及必要的 smoke tests。

把真实结果写入：

`TEST_REPORT.md`

必须记录：

* Python version
* OS
* dependency versions
* passed
* failed
* skipped
* warnings

不得手工虚构测试结果。

---

# 39. 生成 manifest 与 hashes

生成：

`MANIFEST.json`

记录所有最终需要交付的文件：

* path
* size
* SHA256

排除：

* `.git`
* `.venv`
* `__pycache__`
* `.pytest_cache`
* 临时文件
* build cache
* 大型无关缓存

另外生成：

`SHA256SUMS.txt`

---

# 40. 最终打包前清理

删除旧输出，确保不存在过期 zip。

Linux/macOS：

```bash
rm -rf deliverable
rm -f NDM_CALIBRATOR_V1_0_FINAL.zip
mkdir -p deliverable
```

PowerShell：

```powershell
Remove-Item -Recurse -Force deliverable -ErrorAction SilentlyContinue
Remove-Item -Force NDM_CALIBRATOR_V1_0_FINAL.zip -ErrorAction SilentlyContinue
New-Item -ItemType Directory deliverable | Out-Null
```

---

# 41. 最终交付内容

`deliverable/` 至少包含：

```text
source/
examples/
tests/
docs/
scripts/
README.md
requirements.txt
pyproject.toml
TEST_REPORT.md
FINAL_AUDIT.md
MANIFEST.json
SHA256SUMS.txt
```

如果 exe 构建成功且实际验证：

```text
dist/
```

否则不得生成假 exe。

---

# 42. 打包

最终生成：

```text
NDM_CALIBRATOR_V1_0_FINAL.zip
```

ZIP 必须包含：

* 完整源码
* 测试
* 示例数据
* 文档
* 构建脚本
* 测试报告
* 审计报告
* manifest
* hashes

不要包含：

* `.git`
* 虚拟环境
* Python cache
* 临时日志
* 旧 zip
* IDE cache

---

# 43. ZIP 校验

打包后必须重新读取 ZIP：

检查：

1. ZIP 可以正常打开；
2. 文件数量合理；
3. 必要文件存在；
4. 文件没有 0-byte 异常；
5. manifest 与实际文件匹配；
6. SHA256 可验证；
7. 没有将最终 ZIP 自己递归包含进 ZIP；
8. 没有 `.venv`、`.git`、cache。

生成最终 ZIP SHA256。

Linux：

```bash
sha256sum NDM_CALIBRATOR_V1_0_FINAL.zip
```

PowerShell：

```powershell
Get-FileHash .\NDM_CALIBRATOR_V1_0_FINAL.zip -Algorithm SHA256
```

---

# 44. 最终回复格式

全部完成后，不要只说“完成”。

返回：

## A. 实现结果

列出已经真正实现的核心模块。

## B. 项目结构

给出主要目录树。

## C. 测试结果

例如：

```text
pytest:
xxx passed
x skipped
x warnings
```

只能填写真实结果。

## D. E2E 验证

逐项说明最终验收场景是否 PASS。

## E. 已知限制

必须如实说明。

## F. 环境

记录：

* OS
* Python
* 关键 dependency versions

## G. Git 状态

如果目录属于 Git repository：

```bash
git status --short
git rev-parse HEAD
```

记录结果。

不要未经明确指示：

* force push
* overwrite main
* 删除其他分支
* 修改无关代码

## H. 最终交付物

输出：

```text
NDM_CALIBRATOR_V1_0_FINAL.zip
```

以及：

* absolute path
* file size
* SHA256

---

# 45. 核心原则

本任务的目标不是“尽可能写很多代码”。

目标是：

> 创建一套具有明确数学对象、完整工程工作流、可重复参数辨识、数值正确性验证、诊断分析、可信度分析、项目持久化和桌面 GUI 的非线性动态模型参数辨识软件。

任何功能只有在：

**实现 + 测试 + GUI 可访问 + 文档一致**

四项基本成立后，才允许声明“已完成”。

现在开始先检查工作目录和现有文件，然后按照上述 Phase 1–8 实施。不要因为任务量较大而缩减核心功能，也不要在中途等待人工确认；遇到不影响核心产品定义的小型技术选择时自行选择合理实现并记录到 `ARCHITECTURE.md`。
