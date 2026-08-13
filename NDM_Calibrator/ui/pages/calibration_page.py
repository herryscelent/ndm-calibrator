"""Model calibration page: fit quality KPIs and measured vs simulated plot."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import QHBoxLayout

from ui.adapters.view_models import CalibrationAdapter
from ui.components.common import MetricCard, SectionPanel
from ui.plots.specialized import MeasuredSimulatedPlot, ResidualPlot
from ui.pages.base_page import BasePage


class CalibrationPage(BasePage):
    """Show fit metrics and the measured/simulated comparison."""

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("模型校准", "评估参数辨识后的模型拟合质量。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        cards = QHBoxLayout()
        cards.setSpacing(12)
        self.metric_rmse = MetricCard("RMSE")
        self.metric_mae = MetricCard("MAE")
        self.metric_r2 = MetricCard("R²")
        self.metric_runtime = MetricCard("辨识用时")
        for c in (self.metric_rmse, self.metric_mae, self.metric_r2, self.metric_runtime):
            cards.addWidget(c)
        body.addLayout(cards)

        self.fit_panel = SectionPanel("实测 vs 模拟")
        self.fit_plot = MeasuredSimulatedPlot(theme_manager=self._theme)
        self.fit_panel.add_widget(self.fit_plot)
        body.addWidget(self.fit_panel, 1)

        self.resid_panel = SectionPanel("误差时序")
        self.resid_plot = ResidualPlot(theme_manager=self._theme)
        self.resid_panel.add_widget(self.resid_plot)
        body.addWidget(self.resid_panel, 1)

    def on_result_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            return
        cal = project.results.get("calibration")
        adapter = CalibrationAdapter(cal)
        if adapter.is_empty:
            self.set_empty_state("尚未运行辨识", "先在“参数辨识”页运行算法, 然后在此查看拟合质量。", "", "")
            self.set_empty()
            return
        self.show_content()
        rmse = adapter.metric("RMSE")
        mae = adapter.metric("MAE")
        r2 = adapter.metric("R2")
        self.metric_rmse.set_value(f"{rmse:.4g}" if rmse is not None else "N/A")
        self.metric_mae.set_value(f"{mae:.4g}" if mae is not None else "N/A")
        self.metric_r2.set_value(f"{r2:.4g}" if r2 is not None else "N/A")

        entry = project.results.get("identification", {})
        rt = entry.get("result", {}).get("runtime_seconds")
        self.metric_runtime.set_value(f"{rt:.2f}s" if rt is not None else "N/A")

        # Draw measured vs simulated using the stored prediction.
        ctx = None
        params = entry.get("result", {}).get("parameters")
        if params and project.model and project.experiment:
            from identification.base import build_context

            try:
                ctx = build_context(project)
                free_names = ctx.free_names
                theta = np.array([params[n] for n in free_names], dtype=float)
                predicted = ctx.predict_outputs(theta)
                first_out = project.model.outputs[0]
                measured = ctx.measured_outputs()[first_out]
                self.fit_plot.plot_fit(project.experiment.time, measured, predicted[first_out])
                resid = measured - predicted[first_out]
                self.resid_plot.plot_residuals(project.experiment.time, resid)
            except Exception:
                pass

    def on_project_changed(self) -> None:
        self.on_result_changed()
