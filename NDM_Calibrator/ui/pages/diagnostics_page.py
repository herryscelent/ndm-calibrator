"""Diagnostics page: residuals, sensitivity, identifiability, correlation."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from ui.adapters.view_models import CalibrationAdapter
from ui.components.common import MetricCard, SectionPanel
from ui.plots.specialized import (
    CorrelationHeatmap,
    HistogramPlot,
    ResidualPlot,
    SensitivityPlot,
)
from ui.pages.base_page import BasePage


class DiagnosticsPage(BasePage):
    """Tabbed diagnostics view."""

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("诊断分析", "残差分析、参数敏感性与可辨识性诊断。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)

        self._build_residuals_tab()
        self._build_sensitivity_tab()
        self._build_identifiability_tab()
        self._build_correlation_tab()
        body.addWidget(self.tabs, 1)

    def _build_residuals_tab(self) -> None:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        cards = QHBoxLayout()
        self.res_mean = MetricCard("残差均值")
        self.res_std = MetricCard("残差标准差")
        self.res_max = MetricCard("最大绝对误差")
        self.res_acf = MetricCard("ACF 峰值")
        for c in (self.res_mean, self.res_std, self.res_max, self.res_acf):
            cards.addWidget(c)
        lay.addLayout(cards)

        self.resid_plot = ResidualPlot(theme_manager=self._theme)
        lay.addWidget(self.resid_plot, 1)

        self.res_diag_label = QLabel("")
        self.res_diag_label.setWordWrap(True)
        self.res_diag_label.setStyleSheet("color: #57606A;")
        lay.addWidget(self.res_diag_label)
        self.tabs.addTab(tab, "残差")

    def _build_sensitivity_tab(self) -> None:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        self.sens_plot = SensitivityPlot(theme_manager=self._theme)
        lay.addWidget(self.sens_plot, 1)
        self.sens_table = QTableWidget()
        self.sens_table.setColumnCount(3)
        self.sens_table.setHorizontalHeaderLabels(["参数", "RMS 归一化敏感度", "最大敏感度"])
        lay.addWidget(self.sens_table, 1)
        self.tabs.addTab(tab, "敏感度")

    def _build_identifiability_tab(self) -> None:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        cards = QHBoxLayout()
        self.id_cond = MetricCard("条件数")
        self.id_rank = MetricCard("秩")
        self.id_smin = MetricCard("最小奇异值")
        for c in (self.id_cond, self.id_rank, self.id_smin):
            cards.addWidget(c)
        lay.addLayout(cards)
        self.id_singular = HistogramPlot("奇异值", theme_manager=self._theme)
        lay.addWidget(self.id_singular, 1)
        self.id_warn = QLabel("")
        self.id_warn.setWordWrap(True)
        self.id_warn.setStyleSheet("color: #9A6700;")
        lay.addWidget(self.id_warn)
        self.tabs.addTab(tab, "可辨识性")

    def _build_correlation_tab(self) -> None:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)
        self.corr_plot = CorrelationHeatmap(theme_manager=self._theme)
        lay.addWidget(self.corr_plot, 2)
        self.corr_table = QTableWidget()
        self.corr_table.setColumnCount(3)
        self.corr_table.setHorizontalHeaderLabels(["参数 A", "参数 B", "相关系数"])
        lay.addWidget(self.corr_table, 1)
        self.tabs.addTab(tab, "相关性")

    # ------------------------------------------------------------------ #
    def on_result_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            return
        adapter = CalibrationAdapter(project.results.get("calibration"))
        if adapter.is_empty:
            self.set_empty_state("尚未生成诊断结果", "运行辨识并查看校准页后, 此处将显示残差与可辨识性分析。", "", "")
            self.set_empty()
            return
        self.show_content()
        self._fill_residuals(project, adapter)
        self._fill_sensitivity(adapter)
        self._fill_identifiability(adapter)
        self._fill_correlation(adapter)

    def _fill_residuals(self, project, adapter) -> None:
        first_out = project.model.outputs[0] if project.model else None
        if not first_out:
            return
        stats = adapter.residual_stats(first_out)
        resid = adapter.residual_series(first_out)
        if resid is not None:
            time = project.experiment.time
            self.resid_plot.plot_residuals(time, resid)
        self.res_mean.set_value(f"{stats.get('mean', 'N/A'):.4g}" if stats else "N/A")
        self.res_std.set_value(f"{stats.get('std', 'N/A'):.4g}" if stats else "N/A")
        self.res_max.set_value(f"{stats.get('max', 'N/A'):.4g}" if stats else "N/A")
        acf = adapter.data.get("residual_diagnosis", {}).get(first_out, {}).get("acf", [])
        peak = max((abs(a) for a in acf), default=0)
        self.res_acf.set_value(f"{peak:.4g}" if acf else "N/A")
        diag = adapter.residual_diagnosis(first_out)
        msg = diag.get("message", "")
        self.res_diag_label.setText(msg)

    def _fill_sensitivity(self, adapter) -> None:
        summary = adapter.sensitivity_summary()
        names = list(summary.keys())
        if not names:
            return
        rms = [summary[n]["rms"] for n in names]
        mx = [summary[n]["max"] for n in names]
        self.sens_plot.plot_sensitivity(names, rms)
        self.sens_table.setRowCount(len(names))
        for i, n in enumerate(names):
            self.sens_table.setItem(i, 0, QTableWidgetItem(n))
            self.sens_table.setItem(i, 1, QTableWidgetItem(f"{rms[i]:.6g}"))
            self.sens_table.setItem(i, 2, QTableWidgetItem(f"{mx[i]:.6g}"))

    def _fill_identifiability(self, adapter) -> None:
        ident = adapter.identifiability()
        if not ident:
            return
        cond = ident.get("condition_number")
        rank = ident.get("rank")
        sv = ident.get("singular_values", [])
        self.id_cond.set_value(f"{cond:.3e}" if cond is not None else "N/A")
        self.id_rank.set_value(f"{rank}" if rank is not None else "N/A")
        self.id_smin.set_value(f"{sv[-1]:.3e}" if sv else "N/A")
        if sv:
            self.id_singular.plot_samples(sv, interval=None)
            self.id_singular.plot.setLabel("bottom", "奇异值序号")
        warns = ident.get("warnings", [])
        self.id_warn.setText("\n".join(warns) if warns else "未检测到可辨识性警告")

    def _fill_correlation(self, adapter) -> None:
        names = adapter.data.get("identifiability", {}).get("parameter_names", [])
        corr = adapter.correlation_matrix()
        if corr is None or not names:
            return
        self.corr_plot.plot_correlation(corr, names)
        pairs = []
        n = len(names)
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((names[i], names[j], float(corr[i, j])))
        pairs.sort(key=lambda x: -abs(x[2]))
        self.corr_table.setRowCount(len(pairs))
        for row, (a, b, v) in enumerate(pairs):
            self.corr_table.setItem(row, 0, QTableWidgetItem(a))
            self.corr_table.setItem(row, 1, QTableWidgetItem(b))
            self.corr_table.setItem(row, 2, QTableWidgetItem(f"{v:.3f}"))

    def on_project_changed(self) -> None:
        self.on_result_changed()
