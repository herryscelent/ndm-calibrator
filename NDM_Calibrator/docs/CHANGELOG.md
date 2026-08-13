# 变更日志 — NDM-Calibrator

## V1.0 (2026-08-13)

### 新增

- 完整项目生命周期 (新建/打开/保存/另存为), `.ndmc` ZIP 项目格式 (schema 1.0);
- 数据导入 (CSV/XLSX)、字段映射、质量检查与基础预处理;
- 5 个内置模型模板 + SymPy 安全自定义模型解析 (禁止 eval);
- 表格式参数编辑器 (Free/Fixed, 边界校验);
- ODE 数值求解 (RK45/DOP853/Radau/BDF) + 输入插值 (ZOH/线性);
- 四种参数辨识算法: 非线性最小二乘 / Nelder-Mead / Differential Evolution / Multi-start;
- 可重复性支持 (seed);
- 校准指标 (SSE/MSE/RMSE/MAE/R²/最大绝对误差/Mean Error);
- 残差诊断 (统计/时序/ACF/结构提示);
- 参数敏感性分析 (有限差分, 原始+归一化);
- 可辨识性诊断 (奇异值/条件数/协方差/相关矩阵, 阈值集中管理);
- Multi-start 稳定性分析;
- Residual Bootstrap (percentile interval, 默认 B=100);
- 结果导出: Excel / CSV / 图片 / HTML 报告;
- 日志系统 (logs/);
- Fluent 风格桌面 GUI (Light/Dark 主题, PyQtGraph 交互图);
- 4 个可运行示例 (指数衰减/一阶/二阶弹簧阻尼/非线性) + 生成脚本;
- 96 项 pytest 测试 + GUI smoke tests;
- Windows 启动脚本 run.bat, PyInstaller spec。

### 工程化

- 分层架构: UI / 应用 / 领域 / 服务 解耦;
- 全部魔法数字收敛到 `app/constants.py`;
- 领域异常体系, UI 不显示 traceback (写入日志)。
