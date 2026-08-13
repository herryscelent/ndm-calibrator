"""Main application window: top bar, sidebar, stacked pages, status bar."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.application import Application
from app.constants import STATUS_ERROR, STATUS_LOADING, STATUS_READY, STATUS_RUNNING
from core.exceptions import NDMCError
from ui.components.sidebar import Sidebar
from ui.components.top_bar import TopBar
from ui.design.theme_manager import ThemeManager
from ui.pages.calibration_page import CalibrationPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.data_page import DataPage
from ui.pages.diagnostics_page import DiagnosticsPage
from ui.pages.export_page import ExportPage
from ui.pages.identification_page import IdentificationPage
from ui.pages.model_page import ModelPage
from ui.pages.parameter_page import ParameterPage
from ui.pages.settings_page import AboutPage, SettingsPage
from ui.pages.uncertainty_page import UncertaintyPage

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window wiring UI pages to the Application facade."""

    def __init__(self):
        super().__init__()
        self.app = Application()
        self.setWindowTitle("非线性动态模型参数辨识与校准软件 V1.0")
        self.resize(1400, 900)
        self.setMinimumSize(1100, 700)

        self._settings = QSettings("NDM-Calibrator", "NDM-Calibrator")

        # Central layout
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Theme manager must exist before building theme-aware widgets.
        self.theme = ThemeManager(QApplication.instance())

        self.top_bar = TopBar(self.theme)
        root.addWidget(self.top_bar)

        mid = QHBoxLayout()
        mid.setContentsMargins(0, 0, 0, 0)
        mid.setSpacing(0)

        self.sidebar = Sidebar(self.theme)
        mid.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        mid.addWidget(self.stack, 1)
        root.addLayout(mid, 1)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel(STATUS_READY)
        self.status_bar.addWidget(self.status_label)

        # Build pages
        self.pages: Dict[str, QWidget] = {}
        self._build_pages()
        self._connect_signals()
        self._restore_ui_state()

        # Apply theme before showing.
        self.theme.apply()

        # Start on dashboard with a welcome empty project state.
        self.navigate("dashboard")
        self._sync_top_bar()
        self.status(STATUS_READY)

    # ------------------------------------------------------------------ #
    def _build_pages(self) -> None:
        self.pages["dashboard"] = DashboardPage(self.theme)
        self.pages["data"] = DataPage(self.theme)
        self.pages["model"] = ModelPage(self.theme)
        self.pages["parameters"] = ParameterPage(self.theme)
        self.pages["identification"] = IdentificationPage(self.theme)
        self.pages["calibration"] = CalibrationPage(self.theme)
        self.pages["diagnostics"] = DiagnosticsPage(self.theme)
        self.pages["uncertainty"] = UncertaintyPage(self.theme)
        self.pages["export"] = ExportPage(self.theme)
        self.pages["settings"] = SettingsPage(self.theme)
        self.pages["about"] = AboutPage(self.theme)
        for page in self.pages.values():
            self.stack.addWidget(page)

    def _connect_signals(self) -> None:
        self.sidebar.navigation_requested.connect(self.navigate)
        self.top_bar.save_requested.connect(self.save_project)
        self.top_bar.open_requested.connect(self.open_project_dialog)
        self.top_bar.theme_toggle_requested.connect(self._toggle_theme)

        # Page signals
        self.pages["dashboard"].navigate_requested.connect(self.navigate)
        self.pages["identification"].identification_finished.connect(self._on_identification_done)
        self.pages["identification"].run_started.connect(lambda: self.status(STATUS_RUNNING))
        self.pages["identification"].run_cancelled.connect(lambda: self.status(STATUS_READY))

    def _build_shortcuts(self) -> None:
        def act(key, slot):
            a = QAction(self)
            a.setShortcut(QKeySequence(key))
            a.triggered.connect(slot)
            self.addAction(a)

        act("Ctrl+N", self.new_project_dialog)
        act("Ctrl+O", self.open_project_dialog)
        act("Ctrl+S", self.save_project)
        act("Ctrl+Shift+S", self.save_project_as)
        act("Ctrl+I", self.show_import_dialog)
        act("Ctrl+Enter", lambda: self.pages["identification"].start())
        act("Ctrl+,", lambda: self.navigate("settings"))
        act("F1", lambda: self.navigate("about"))

    # ------------------------------------------------------------------ #
    def _restore_ui_state(self) -> None:
        collapsed = self._settings.value("sidebar_collapsed", "false") == "true"
        self.sidebar.set_collapsed(collapsed)
        self._build_shortcuts()

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def navigate(self, key: str) -> None:
        page = self.pages.get(key)
        if page is None:
            return
        self.stack.setCurrentWidget(page)
        self.sidebar.select(key)
        page.refresh()

    # ------------------------------------------------------------------ #
    # Project actions
    # ------------------------------------------------------------------ #
    def new_project_dialog(self) -> None:
        if self._confirm_discard():
            self.app.new_project()
            self._after_project_change()

    def open_project_dialog(self) -> None:
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "打开项目", "", "NDM 项目 (*.ndmc)")
        if not path:
            return
        try:
            self.app.open_project(path)
            self._after_project_change()
        except NDMCError as exc:
            self._error_dialog("打开项目失败", str(exc))

    def save_project(self) -> None:
        if self.app.project is None:
            return
        try:
            if self.app.project.file_path is None:
                self.save_project_as()
            else:
                self.app.save_project()
                self._after_project_change()
        except NDMCError as exc:
            self._error_dialog("保存项目失败", str(exc))

    def save_project_as(self) -> None:
        if self.app.project is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "另存为项目", "", "NDM 项目 (*.ndmc)")
        if not path:
            return
        try:
            self.app.save_project(path)
            self._after_project_change()
        except NDMCError as exc:
            self._error_dialog("保存项目失败", str(exc))

    def _confirm_discard(self) -> bool:
        if self.app.project is None or not self.app.project.dirty:
            return True
        box = QMessageBox(self)
        box.setWindowTitle("未保存的修改")
        box.setText("当前项目有未保存的修改, 是否放弃?")
        box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        result = box.exec()
        if result == QMessageBox.StandardButton.Save:
            self.save_project()
            return not (self.app.project and self.app.project.dirty)
        return result == QMessageBox.StandardButton.Discard

    # ------------------------------------------------------------------ #
    # Data import
    # ------------------------------------------------------------------ #
    def show_import_dialog(self) -> None:
        if self.app.project is None:
            QMessageBox.information(self, "提示", "请先新建或打开一个项目。")
            self.navigate("dashboard")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "导入数据", "", "数据文件 (*.csv *.xlsx)"
        )
        if not path:
            return
        self._run_import(path)

    def _run_import(self, path: str) -> None:
        try:
            from data.loader import load_dataframe

            df, source = load_dataframe(path)
            # Auto-detect time/input/output columns.
            time_col, input_cols, output_cols = self._auto_map(df)
            self.app.import_data(path, time_col, input_cols, output_cols)
            self.pages["data"].set_dataframe(df)
            self._after_project_change()
            self.navigate("data")
            self.status(f"已导入 {source}")
        except NDMCError as exc:
            self._error_dialog("导入数据失败", str(exc))

    @staticmethod
    def _auto_map(df) -> tuple[str, list, list]:
        cols = list(df.columns)
        numeric = [c for c in cols if _is_numeric_col(df, c)]
        time_col = None
        for candidate in ("time", "t", "时间", "Time"):
            if candidate in cols and _is_numeric_col(df, candidate):
                time_col = candidate
                break
        if time_col is None and numeric:
            time_col = numeric[0]
            numeric = [c for c in numeric if c != time_col]
        inputs, outputs = [], []
        # Heuristic: last numeric column is the output, the rest are inputs.
        if numeric:
            outputs = [numeric[-1]]
            inputs = [c for c in numeric[:-1]]
        return time_col, inputs, outputs

    def reset_data(self) -> None:
        if self.app.project is not None:
            self.app.project.experiment = None
            self.app.project.mark_dirty()
            self._after_project_change()
            self.status("已清除数据映射")

    def apply_mapping_scheme(self, scheme: Dict) -> None:
        """Apply a column-mapping scheme (placeholder; the auto-map covers V1)."""
        pass

    # ------------------------------------------------------------------ #
    # Model / parameters helpers called by pages
    # ------------------------------------------------------------------ #
    def set_model(self, model) -> None:
        self.app.set_model(model)
        self._after_project_change()

    def sync_parameters_from_model(self) -> None:
        if self.app.project is None or self.app.project.model is None:
            raise NDMCError("请先定义模型")
        self.app.project.parameters.sync_from_names(self.app.project.model.parameters)
        self.app.project.mark_dirty()
        self._after_project_change()

    def validate_parameters(self) -> list:
        errors = []
        for p in self.app.project.parameters:
            try:
                p.validate()
            except ValueError as exc:
                errors.append(str(exc))
        return errors

    # ------------------------------------------------------------------ #
    # Background identification
    # ------------------------------------------------------------------ #
    def run_identification_async(self, algorithm: str, options: Dict[str, Any]):
        from ui.workers import RunWorker

        project = self.app.project
        options["seed"] = None if options.get("seed") is None else int(options["seed"])

        def work(token):
            from app.application import run_identification_for_project

            result = run_identification_for_project(project, algorithm, options)
            if token.cancelled():
                raise RuntimeError("操作已取消")
            return result

        worker = RunWorker(work, self)
        worker.finished_ok.connect(lambda _: self._on_identification_done())
        worker.finished_error.connect(self._on_worker_error)
        worker.start()
        self.status(STATUS_RUNNING)
        return worker

    def _on_identification_done(self) -> None:
        self.status(STATUS_COMPLETED)
        self.pages["identification"].on_identification_done()
        # Auto-run calibration + diagnostics so results pages populate.
        try:
            self._run_calibration()
        except Exception:
            pass
        self._after_project_change()
        self.navigate("calibration")

    def _run_calibration(self) -> None:
        project = self.app.project
        if project is None:
            return
        entry = project.results.get("identification", {})
        params = entry.get("result", {}).get("parameters")
        if not params:
            return
        from diagnostics.orchestrator import run_calibration_and_diagnostics

        run_calibration_and_diagnostics(project, params)

    def _on_worker_error(self, message: str) -> None:
        self.status(STATUS_ERROR)
        self.pages["identification"].on_identification_error(message)
        logger.error("后台任务失败: %s", message)

    # ------------------------------------------------------------------ #
    # Uncertainty helpers
    # ------------------------------------------------------------------ #
    def run_stability_async(self, options: Dict[str, Any]) -> Dict[str, Any]:
        from uncertainty.stability import run_multistart_stability

        return run_multistart_stability(self.app.project, options)

    def run_bootstrap_async(self, options: Dict[str, Any]) -> Dict[str, Any]:
        from uncertainty.bootstrap import run_bootstrap

        result = run_bootstrap(self.app.project, options)
        self.app.project.results["bootstrap"] = result
        self.app.project.mark_dirty()
        self._after_project_change()
        return result

    def export_results(self, dest: str, fmt: str, checks: Dict[str, bool]) -> str:
        from export.excel_exporter import export_excel
        from export.report_exporter import export_html_report

        if fmt == "excel":
            path = export_excel(self.app.project, dest, checks)
            return f"Excel 已导出: {path}"
        if fmt == "report":
            path = export_html_report(self.app.project, dest)
            return f"HTML 报告已导出: {path}"
        raise NDMCError(f"未知导出格式: {fmt}")

    # ------------------------------------------------------------------ #
    # Theme
    # ------------------------------------------------------------------ #
    def _toggle_theme(self) -> None:
        self.theme.toggle()
        self._after_project_change()

    # ------------------------------------------------------------------ #
    # Status / sync
    # ------------------------------------------------------------------ #
    def status(self, text: str) -> None:
        self.status_label.setText(text)

    def _after_project_change(self) -> None:
        self._sync_top_bar()
        # Refresh every page so results/state stay in sync regardless of which
        # page is currently visible.
        for page in self.pages.values():
            if hasattr(page, "on_project_changed"):
                page.on_project_changed()

    def _sync_top_bar(self) -> None:
        project = self.app.project
        if project is None:
            self.top_bar.set_project("未命名项目", False)
            self.setWindowTitle("非线性动态模型参数辨识与校准软件 V1.0")
            return
        self.top_bar.set_project(project.name, project.dirty)
        self.setWindowTitle(f"{project.name} — 非线性动态模型参数辨识与校准软件 V1.0")

    def _error_dialog(self, title: str, message: str) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setText(message)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()

    def closeEvent(self, event) -> None:
        if self._confirm_discard():
            self._settings.setValue("sidebar_collapsed", self.sidebar.is_collapsed())
            event.accept()
        else:
            event.ignore()


def _is_numeric_col(df, col) -> bool:
    import pandas as pd

    return pd.api.types.is_numeric_dtype(df[col])
