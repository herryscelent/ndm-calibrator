"""Dashboard / project home page."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.components.common import MetricCard, PageHeader, SectionPanel
from ui.pages.base_page import BasePage


class WorkflowStep(QWidget):
    """One row of the workflow timeline."""

    clicked = Signal(str)

    def __init__(self, key: str, label: str, parent=None):
        super().__init__(parent)
        self.key = key
        self._state = "pending"
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(10)
        self.dot = QLabel("○")
        self.dot.setFixedWidth(20)
        self.label = QLabel(label)
        lay.addWidget(self.dot)
        lay.addWidget(self.label)
        lay.addStretch(1)
        self._apply_style()

    def set_state(self, state: str) -> None:
        self._state = state
        self._apply_style()

    def _apply_style(self) -> None:
        styles = {
            "completed": ("●", "#1A7F37"),
            "current": ("▶", "#0F6CBD"),
            "warning": ("●", "#9A6700"),
            "pending": ("○", "#9CA3AB"),
        }
        dot, color = styles.get(self._state, styles["pending"])
        self.dot.setText(dot)
        self.dot.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 600;")
        self.label.setStyleSheet("font-size: 13px;")

    def mousePressEvent(self, event):
        self.clicked.emit(self.key)
        super().mousePressEvent(event)


class DashboardPage(BasePage):
    """Project dashboard with summary, metric cards and workflow."""

    navigate_requested = Signal(str)

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("项目首页", "项目概览、工作流程与当前状态。")
        self._build_dashboard()

    def _build_dashboard(self) -> None:
        self.summary_panel = SectionPanel("项目信息")
        self.summary_grid = QVBoxLayout()
        self.summary_grid.setSpacing(4)
        self.summary_panel.add_layout(self.summary_grid)
        self.body().addWidget(self.summary_panel)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        self.metric_samples = MetricCard("样本数")
        self.metric_params = MetricCard("参数")
        self.metric_rmse = MetricCard("RMSE")
        self.metric_r2 = MetricCard("R²")
        for c in (self.metric_samples, self.metric_params, self.metric_rmse, self.metric_r2):
            cards_row.addWidget(c)
        self.body().addLayout(cards_row)

        self.workflow_panel = SectionPanel("工作流程")
        self.workflow_steps = {}
        steps = [
            ("data", "数据 (导入并映射数据)"),
            ("model", "模型 (定义动态模型)"),
            ("parameters", "参数 (配置待辨识参数)"),
            ("identification", "辨识 (运行参数辨识)"),
            ("calibration", "校准 (评估拟合质量)"),
            ("diagnostics", "诊断 (残差与可辨识性)"),
        ]
        for key, label in steps:
            step = WorkflowStep(key, label)
            step.clicked.connect(self.navigate_requested)
            self.workflow_steps[key] = step
            self.workflow_panel.add_widget(step)
        self.body().addWidget(self.workflow_panel)

    # ------------------------------------------------------------------ #
    def on_project_changed(self) -> None:
        app = self.window().app if hasattr(self.window(), "app") else None
        project = app.project if app else None
        if project is None:
            self._show_empty()
            return

        self.show_content()
        self._populate_summary(project)
        self._populate_metrics(project)
        self._update_workflow(project)

    def _show_empty(self) -> None:
        self.set_empty_state("新建或打开一个项目", "创建项目后, 在此查看项目概览与工作流程。", "")
        self.set_empty()

    def _populate_summary(self, project) -> None:
        summary = project.summary()
        lines = [
            ("项目名称", summary["name"]),
            ("模型", ", ".join(summary["model_states"]) if summary["model_states"] else "未定义"),
            ("数据来源", summary["data_source"] or "未导入"),
            ("项目文件", summary["file_path"] or "未保存"),
        ]
        self._clear_layout(self.summary_grid)
        for label, value in lines:
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("color: #57606A; min-width: 80px;")
            v = QLabel(value or "—")
            row.addWidget(l)
            row.addWidget(v, 1)
            self.summary_grid.addLayout(row)

    def _populate_metrics(self, project) -> None:
        exp = project.experiment
        self.metric_samples.set_value(f"{exp.n_points:,}" if exp else "Not available")
        n_free = len(project.parameters.free_parameters())
        n_total = len(project.parameters)
        self.metric_params.set_value(f"{n_free} free / {n_total - n_free} fixed")

        cal = project.results.get("calibration", {})
        metrics = cal.get("metrics", {}).get("summary", {})
        rmse = metrics.get("RMSE")
        r2 = metrics.get("R2")
        self.metric_rmse.set_value(f"{rmse:.4g}" if rmse is not None else "Not available")
        self.metric_r2.set_value(f"{r2:.4g}" if r2 is not None else "Not available")

    def _update_workflow(self, project) -> None:
        has_data = project.experiment is not None
        has_model = project.model is not None
        has_params = len(project.parameters) > 0
        has_result = "identification" in project.results
        has_cal = "calibration" in project.results

        states = {
            "data": "completed" if has_data else "pending",
            "model": "completed" if has_model else ("current" if has_data else "pending"),
            "parameters": "completed" if has_params else ("current" if has_model else "pending"),
            "identification": "completed" if has_result else ("current" if has_params else "pending"),
            "calibration": "completed" if has_cal else ("current" if has_result else "pending"),
            "diagnostics": "completed" if has_cal else ("pending" if has_result else "pending"),
        }
        for key, step in self.workflow_steps.items():
            step.set_state(states[key])

    @staticmethod
    def _clear_layout(layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            elif item.layout() is not None:
                DashboardPage._clear_layout(item.layout())
