# NDM-Calibrator V1.0

**非线性动态模型参数辨识与校准软件**

根据已有实验/观测时序数据，对用户定义的非线性动态模型中的未知参数进行辨识、校准和可信度分析。

## 功能概览

- **项目生命周期**: 新建 / 打开 / 保存 (.ndmc 项目格式, ZIP 容器, schema 1.0)
- **数据导入**: CSV / XLSX, 字段映射, 数据质量检查, 基础预处理
- **模型定义**: 5 个内置模型模板 + 用户自定义模型 (SymPy 安全解析, 禁用 eval)
- **参数配置**: 表格式参数编辑器, 边界校验, Free/Fixed 状态
- **数值求解**: solve_ivp (RK45 / DOP853 / Radau / BDF), ZOH / 线性输入插值
- **参数辨识**: 非线性最小二乘 / Nelder-Mead / Differential Evolution / Multi-start
- **模型校准**: SSE / MSE / RMSE / MAE / R² / 最大绝对误差 / Mean Error
- **诊断分析**: 残差统计与 ACF、参数敏感性、可辨识性 (条件数/奇异值/相关矩阵)
- **可信度分析**: Multi-start 稳定性、Residual Bootstrap (percentile interval)
- **结果导出**: Excel / CSV / 图片 / HTML 分析报告

## 环境要求

- Windows 10/11 (Linux/macOS 亦可运行)
- Python 3.11+
- 无需 GPU, 无需 Docker, 无需云服务器

## 安装方法

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

或直接使用 `run.bat` (Windows):

```powershell
run.bat
```

## 启动方法

```powershell
python -m app.main
```

## 测试方法

```powershell
QT_QPA_PLATFORM=offscreen python -m pytest tests
```

Windows PowerShell 下:

```powershell
$env:QT_QPA_PLATFORM="offscreen"; python -m pytest tests
```

## 示例方法

```powershell
# 重新生成全部示例数据 (含真值 metadata)
python scripts\generate_examples.py
```

软件内: 新建项目 → 数据管理 → 导入 `examples\first_order\data.csv` →
映射 time/u/x → 选择"一阶惯性系统"模型 → 参数配置 → 开始辨识。

## 目录结构

```text
NDM_Calibrator/
├─ app/            应用层 (入口/控制器/常量)
├─ core/           领域对象 (项目/模型/参数/实验/目标函数)
├─ data/           数据导入/映射/校验/预处理
├─ simulation/     ODE/离散求解器/插值/模拟器
├─ identification/ 参数辨识算法
├─ diagnostics/    校准指标/残差/敏感性/可辨识性
├─ uncertainty/    Bootstrap/置信区间/稳定性
├─ visualization/  可视化 (预留)
├─ export/         导出 (Excel/CSV/图片/HTML 报告)
├─ ui/             桌面 GUI (设计系统/组件/页面/适配器)
├─ examples/       示例数据
├─ tests/          pytest 测试套件
├─ scripts/        示例生成脚本
└─ docs/           文档
```

## 文档

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 架构设计
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) — 用户指南
- [docs/MODEL_FORMAT.md](docs/MODEL_FORMAT.md) — 模型格式
- [docs/ALGORITHMS.md](docs/ALGORITHMS.md) — 算法说明
- [docs/TESTING.md](docs/TESTING.md) — 测试说明
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — 变更日志
- [docs/UI_DESIGN_SYSTEM.md](docs/UI_DESIGN_SYSTEM.md) — UI 设计系统
