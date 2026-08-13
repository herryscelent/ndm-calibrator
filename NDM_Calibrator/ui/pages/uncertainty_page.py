"""Uncertainty page: multi-start stability and bootstrap."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.adapters.view_models import BootstrapAdapter, StabilityAdapter
from ui.components.common import MetricCard, SectionPanel
from ui.plots.specialized import HistogramPlot
from ui.pages.base_page import BasePage


class UncertaintyPage(BasePage):
    """Tabs: Multi-start stability and Bootstrap percentile intervals."""

    bootstrap_finished = Signal()

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("可信度分析", "多起点稳定性与 Bootstrap 参数可信度区间。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self._build_multistart_tab()
        self._build_bootstrap_tab()
        body.addWidget(self.tabs, 1)

    # ---------------- Multi-start ---------------- #
    def _build_multistart_tab(self) -> None:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)

        ctrl = QHBoxLayout()
        self.ms_run_btn = QPushButton("运行多起点稳定性分析")
        self.ms_run_btn.setObjectName("PrimaryButton")
        ctrl.addWidget(self.ms_run_btn)
        ctrl.addStretch(1)
        lay.addLayout(ctrl)

        cards = QHBoxLayout()
        self.ms_starts = MetricCard("起点数")
        self.ms_rate = MetricCard("成功率")
        self.ms_best = MetricCard("最优目标值")
        for c in (self.ms_starts, self.ms_rate, self.ms_best):
            cards.addWidget(c)
        lay.addLayout(cards)

        self.ms_table = QTableWidget()
        self.ms_table.setColumnCount(6)
        self.ms_table.setHorizontalHeaderLabels(["参数", "均值", "标准差", "变异系数", "最优值", "高变异?"])
        lay.addWidget(self.ms_table, 1)

        self.ms_plot = HistogramPlot("参数分布", theme_manager=self._theme)
        lay.addWidget(self.ms_plot, 2)

        self.ms_run_btn.clicked.connect(self._run_multistart)
        self.tabs.addTab(tab, "多起点稳定性")

    def _run_multistart(self) -> None:
        app = self.window().app
        if app is None:
            return
        try:
            result = app.run_stability_async({"n_starts": 10, "seed": 42})
            self._fill_multistart(StabilityAdapter(result))
        except Exception as exc:
            self.ms_table.setRowCount(1)
            self.ms_table.setItem(0, 0, QTableWidgetItem(f"错误: {exc}"))

    def _fill_multistart(self, adapter: StabilityAdapter) -> None:
        if adapter.is_empty:
            return
        self.ms_starts.set_value(f"{int(adapter.data.get('n_starts', 0))}")
        self.ms_rate.set_value(f"{adapter.success_rate:.0%}")
        self.ms_best.set_value(f"{adapter.best_objective:.4g}" if adapter.best_objective is not None else "N/A")
        params = adapter.parameters
        self.ms_table.setRowCount(len(params))
        for i, (name, info) in enumerate(params.items()):
            self.ms_table.setItem(i, 0, QTableWidgetItem(name))
            self.ms_table.setItem(i, 1, QTableWidgetItem(f"{info['mean']:.6g}"))
            self.ms_table.setItem(i, 2, QTableWidgetItem(f"{info['std']:.6g}"))
            self.ms_table.setItem(i, 3, QTableWidgetItem(f"{info['cv']:.3f}"))
            self.ms_table.setItem(i, 4, QTableWidgetItem(f"{info['best']:.6g}"))
            self.ms_table.setItem(i, 5, QTableWidgetItem("是" if info.get("high_variability") else "否"))

    # ---------------- Bootstrap ---------------- #
    def _build_bootstrap_tab(self) -> None:
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(16, 16, 16, 16)

        panel = SectionPanel("Bootstrap 设置")
        form = QFormLayout()
        self.boot_B = QSpinBox()
        self.boot_B.setRange(10, 1000)
        self.boot_B.setValue(100)
        form.addRow("B (重抽样次数)", self.boot_B)
        self.boot_seed = QSpinBox()
        self.boot_seed.setRange(0, 2**31 - 1)
        self.boot_seed.setValue(123)
        form.addRow("随机种子", self.boot_seed)
        self.boot_algo = QComboBox()
        self.boot_algo.addItem("非线性最小二乘", "least_squares")
        self.boot_algo.addItem("Nelder-Mead", "nelder_mead")
        form.addRow("重辨识算法", self.boot_algo)
        panel.add_layout(form)

        row = QHBoxLayout()
        self.boot_run_btn = QPushButton("运行 Bootstrap")
        self.boot_run_btn.setObjectName("PrimaryButton")
        row.addWidget(self.boot_run_btn)
        self.boot_status = QLabel("")
        self.boot_status.setStyleSheet("color: #57606A;")
        row.addWidget(self.boot_status)
        row.addStretch(1)
        lay.addWidget(panel)
        lay.addLayout(row)

        self.boot_table = QTableWidget()
        self.boot_table.setColumnCount(5)
        self.boot_table.setHorizontalHeaderLabels(["参数", "点估计", "中位数", "2.5%", "97.5%"])
        lay.addWidget(self.boot_table, 1)

        self.boot_param_selector = QComboBox()
        lay.addWidget(self.boot_param_selector)

        self.boot_plot = HistogramPlot("Bootstrap 分布 (percentile interval)", theme_manager=self._theme)
        lay.addWidget(self.boot_plot, 2)

        self.boot_run_btn.clicked.connect(self._run_bootstrap)
        self.boot_param_selector.currentIndexChanged.connect(self._update_boot_plot)
        self.tabs.addTab(tab, "Bootstrap")

    def _run_bootstrap(self) -> None:
        app = self.window().app
        if app is None:
            return
        options = {
            "B": self.boot_B.value(),
            "seed": self.boot_seed.value(),
            "algorithm": self.boot_algo.currentData(),
        }
        self.boot_run_btn.setEnabled(False)
        self.boot_status.setText("正在运行 Bootstrap…")
        try:
            result = app.run_bootstrap_async(options)
            self._fill_bootstrap(BootstrapAdapter(result))
            self.boot_status.setText("Bootstrap 完成")
        except Exception as exc:
            self.boot_status.setText(f"Bootstrap 失败: {exc}")
        finally:
            self.boot_run_btn.setEnabled(True)

    def _fill_bootstrap(self, adapter: BootstrapAdapter) -> None:
        if adapter.is_empty:
            return
        params = adapter.parameters
        self.boot_table.setRowCount(len(params))
        self.boot_param_selector.blockSignals(True)
        self.boot_param_selector.clear()
        for i, (name, info) in enumerate(params.items()):
            self.boot_table.setItem(i, 0, QTableWidgetItem(name))
            self.boot_table.setItem(i, 1, QTableWidgetItem(f"{info['mean']:.6g}"))
            self.boot_table.setItem(i, 2, QTableWidgetItem(f"{info['median']:.6g}"))
            self.boot_table.setItem(i, 3, QTableWidgetItem(f"{info['p2_5']:.6g}"))
            self.boot_table.setItem(i, 4, QTableWidgetItem(f"{info['p97_5']:.6g}"))
            self.boot_param_selector.addItem(name, name)
        self.boot_param_selector.blockSignals(False)
        if self.boot_param_selector.count():
            self._update_boot_plot()

    def _update_boot_plot(self) -> None:
        name = self.boot_param_selector.currentData()
        app = self.window().app
        if app is None or not name:
            return
        adapter = BootstrapAdapter(app.project.results.get("bootstrap") if app.project else None)
        samples = adapter.samples(name)
        info = adapter.parameters.get(name, {})
        if samples:
            point = info.get("mean")
            interval = (info.get("p2_5"), info.get("p97_5"))
            self.boot_plot.plot_samples(samples, point_estimate=point, interval=interval)
            self.boot_plot.plot.setLabel("bottom", f"{name} 估计值")

    def on_project_changed(self) -> None:
        self.on_result_changed()

    def on_result_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            return
        boot = BootstrapAdapter(project.results.get("bootstrap"))
        if not boot.is_empty:
            self._fill_bootstrap(boot)
        stab = StabilityAdapter(project.results.get("stability"))
        if not stab.is_empty:
            self._fill_multistart(stab)
