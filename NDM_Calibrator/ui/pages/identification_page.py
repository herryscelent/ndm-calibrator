"""Parameter identification page: algorithm selection and run control."""

from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
)

from core.exceptions import NDMCError
from identification.manager import algorithm_labels
from ui.adapters.view_models import IdentificationAdapter
from ui.components.common import SectionPanel, StatusBadge
from ui.plots.specialized import ConvergencePlot
from ui.pages.base_page import BasePage


class IdentificationPage(BasePage):
    """Run identification algorithms in a background worker."""

    identification_finished = Signal()
    run_started = Signal()
    run_cancelled = Signal()

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("参数辨识", "选择求解算法并估计当前模型未知参数。")
        self._worker = None
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        # Algorithm selection
        self.alg_panel = SectionPanel("算法选择")
        self.alg_group = QButtonGroup(self)
        self.alg_radios = {}
        for key, label in algorithm_labels().items():
            rb = QRadioButton(label)
            rb.setProperty("algo", key)
            self.alg_group.addButton(rb)
            self.alg_radios[key] = rb
            self.alg_panel.add_widget(rb)
        first = next(iter(self.alg_radios.values()))
        first.setChecked(True)
        self.alg_group.buttonClicked.connect(self._on_algorithm_changed)
        body.addWidget(self.alg_panel)

        # Settings
        self.settings_panel = SectionPanel("算法设置")
        form = QFormLayout()
        form.setSpacing(8)

        self.method_combo = None
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2**31 - 1)
        self.seed_spin.setValue(0)
        self.seed_spin.setSpecialValueText("随机")
        form.addRow("随机种子", self.seed_spin)

        self.maxiter_spin = QSpinBox()
        self.maxiter_spin.setRange(1, 100000)
        self.maxiter_spin.setValue(1000)
        form.addRow("最大迭代", self.maxiter_spin)

        self.rtol_spin = QDoubleSpinBox()
        self.rtol_spin.setDecimals(8)
        self.rtol_spin.setRange(1e-12, 1.0)
        self.rtol_spin.setValue(1e-6)
        form.addRow("rtol", self.rtol_spin)

        self.atol_spin = QDoubleSpinBox()
        self.atol_spin.setDecimals(10)
        self.atol_spin.setRange(1e-12, 1.0)
        self.atol_spin.setValue(1e-9)
        form.addRow("atol", self.atol_spin)

        self.settings_panel.add_layout(form)
        body.addWidget(self.settings_panel)

        # Run controls
        control = QHBoxLayout()
        self.start_btn = QPushButton("开始辨识")
        self.start_btn.setObjectName("PrimaryButton")
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.badge = StatusBadge("就绪", "neutral")
        control.addWidget(self.start_btn)
        control.addWidget(self.cancel_btn)
        control.addWidget(self.badge)
        control.addStretch(1)
        body.addLayout(control)

        # Runtime summary
        self.runtime_panel = SectionPanel("运行摘要")
        self.runtime_label = QLabel("尚未运行辨识。")
        self.runtime_label.setWordWrap(True)
        self.runtime_panel.add_widget(self.runtime_label)
        body.addWidget(self.runtime_panel)

        # Convergence
        self.conv_panel = SectionPanel("收敛过程")
        self.conv_plot = ConvergencePlot(theme_manager=self._theme)
        self.conv_panel.add_widget(self.conv_plot)
        body.addWidget(self.conv_panel, 1)

        self.start_btn.clicked.connect(self.start)
        self.cancel_btn.clicked.connect(self.cancel)

    def _on_algorithm_changed(self) -> None:
        pass

    def current_algorithm(self) -> str:
        for key, rb in self.alg_radios.items():
            if rb.isChecked():
                return key
        return "least_squares"

    def _collect_options(self) -> Dict:
        seed = self.seed_spin.value()
        options = {
            "seed": None if self.seed_spin.value() == 0 and self.seed_spin.specialValueText() == "随机" else seed,
            "max_iterations": self.maxiter_spin.value(),
            "rtol": self.rtol_spin.value(),
            "atol": self.atol_spin.value(),
        }
        algo = self.current_algorithm()
        if algo == "least_squares":
            options["method"] = "trf"
        elif algo == "differential_evolution":
            options["population"] = 15
            options["mutation"] = (0.5, 1.0)
            options["recombination"] = 0.7
        elif algo == "multistart":
            options["n_starts"] = 10
        return options

    # ------------------------------------------------------------------ #
    def start(self) -> None:
        app = self.window().app
        if app is None:
            return
        from ui.workers import RunWorker

        algo = self.current_algorithm()
        options = self._collect_options()
        try:
            options["seed"] = None
            worker = app.run_identification_async(algo, options)
        except NDMCError as exc:
            self.badge.set_status("error", str(exc))
            return
        self._worker = worker
        self.badge.set_status("running", "运行中…")
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.runtime_label.setText("正在运行参数辨识… 请稍候。")
        self.run_started.emit()

    def cancel(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            self.badge.set_status("warning", "正在取消…")
            self.cancel_btn.setEnabled(False)

    def on_identification_done(self) -> None:
        self._worker = None
        self.badge.set_status("success", "已完成")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.identification_finished.emit()

    def on_identification_error(self, message: str) -> None:
        self._worker = None
        self.badge.set_status("error", "失败")
        self.runtime_label.setText(f"辨识失败: {message}")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

    def on_result_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            return
        entry = project.results.get("identification")
        adapter = IdentificationAdapter(entry)
        if adapter.is_empty:
            self.runtime_label.setText("尚未运行辨识。")
            return
        self.runtime_label.setText(
            f"算法: {algorithm_labels().get(adapter.algorithm, adapter.algorithm)}\n"
            f"目标值: {adapter.objective_value:.6g} | 用时: {adapter.runtime:.2f}s | 成功: {adapter.success}"
        )

    def on_project_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None or project.model is None:
            self.set_empty_state("请先定义模型", "在“模型定义”页设置动态模型后, 才能进行参数辨识。", "", "")
            self.set_empty()
            return
        self.show_content()
        self.on_result_changed()
