"""Integrated high-fidelity Qt application window.

The ``ui_v2`` pages keep the visual language of the migration reference, while
this window owns the application facade and all cross-page lifecycle actions.
Pages never create a second project or run numerical work in the GUI thread.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QInputDialog, QMainWindow, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from app.application import Application
from core.exceptions import NDMCError
from ui.workers import CancelledError, RunWorker

from .backend import import_frame
from .components import AlertDialog, Sidebar, Toast, Topbar, UnsavedChangesDialog
from .pages import PAGE_CLASSES, DashboardPage

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main shell and controller for the integrated ``ui_v2`` experience."""

    def __init__(self):
        super().__init__()
        self.app = Application()
        # Keep user preferences that are meaningful across launches (for
        # example plot grid and displayed precision).  Sidebar geometry is a
        # session concern and is deliberately kept on the Sidebar instance;
        # persisting it made a later launch unexpectedly start collapsed.
        self._settings = QSettings("NDM-Calibrator", "NDM-Calibrator")
        self._worker: RunWorker | None = None
        self._worker_kind = ""
        self._last_import_path: Path | None = None
        self._last_import_frame = None
        self._closed = False

        self.setWindowTitle("NDM Calibrator")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        shell = QWidget(objectName="AppShell")
        root = QHBoxLayout(shell)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        self.topbar = Topbar()
        right_layout.addWidget(self.topbar)
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack, 1)
        root.addWidget(right, 1)
        self.setCentralWidget(shell)

        self.pages: dict[str, QWidget] = {}
        self.scrolls: dict[str, QScrollArea] = {}
        for key, cls in PAGE_CLASSES.items():
            page = cls()
            page.toast_requested.connect(self.show_toast)
            if isinstance(page, DashboardPage):
                page.navigate_requested.connect(self.navigate)
            # New pages expose these optional signals; using getattr keeps the
            # window compatible with the frozen reference and custom pages.
            for signal_name, slot in (
                ("new_project_requested", self.new_project_dialog),
                ("open_project_requested", self.open_project_dialog),
                ("import_requested", self._import_signal),
                ("model_changed", self._after_project_change),
                ("parameters_changed", self._after_project_change),
            ):
                signal = getattr(page, signal_name, None)
                if signal is not None and hasattr(signal, "connect"):
                    try:
                        signal.connect(slot)
                    except (TypeError, RuntimeError):
                        logger.debug("无法连接页面信号 %s", signal_name, exc_info=True)

            scroll = QScrollArea(objectName="PageScroll")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QScrollArea.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setWidget(page)
            self.pages[key] = page
            self.scrolls[key] = scroll
            self.stack.addWidget(scroll)

        self.sidebar.navigation_requested.connect(self.navigate)
        self.sidebar.collapse_requested.connect(self.sidebar.toggle)
        self.topbar.new_requested.connect(self.new_project_dialog)
        self.topbar.open_requested.connect(self.open_project_dialog)
        self.topbar.save_requested.connect(self.save_project)
        self.topbar.theme_requested.connect(self._theme_notice)
        self.topbar.settings_requested.connect(lambda: self.navigate("settings"))
        self.topbar.about_requested.connect(lambda: self.navigate("about"))

        self.toast = Toast(shell)
        self._build_shortcuts()
        self._restore_ui_state()
        self.navigate("dashboard")
        self._sync_top_bar()

    # ------------------------------------------------------------------ #
    # Navigation and state refresh
    # ------------------------------------------------------------------ #
    def navigate(self, key: str):
        if key not in self.scrolls:
            return
        self.stack.setCurrentWidget(self.scrolls[key])
        self.sidebar.select(key)
        page = self.pages[key]
        # Most pages expose ``on_result_changed`` as an alias of
        # ``on_project_changed``.  Call one hook only; invoking both caused
        # duplicate redraws and duplicate completion toasts.
        method = getattr(page, "on_project_changed", None)
        if method is None:
            method = getattr(page, "on_result_changed", None)
        if method is not None:
            try:
                method()
            except Exception:
                logger.debug("页面刷新失败: %s", key, exc_info=True)

    def show_toast(self, message: str):
        self.toast.show_message(str(message))

    def _after_project_change(self, *_args):
        self._sync_top_bar()
        for key, page in self.pages.items():
            method = getattr(page, "on_project_changed", None)
            if method is None:
                method = getattr(page, "on_result_changed", None)
            if method is not None:
                try:
                    method()
                except Exception:
                    logger.debug("页面刷新失败: %s", key, exc_info=True)

    def _sync_top_bar(self):
        project = self.app.project
        if project is None:
            self.topbar.project_context.setText("未命名项目")
            self.topbar.saved_badge.setText("未创建")
            self.topbar.saved_badge.setProperty("badge", "neutral")
            title = "NDM Calibrator"
        else:
            self.topbar.project_context.setText(project.name or "未命名项目")
            self.topbar.project_context.setToolTip(project.name or "未命名项目")
            self.topbar.saved_badge.setText("未保存" if project.dirty else "已保存")
            self.topbar.saved_badge.setProperty("badge", "warning" if project.dirty else "success")
            title = f"{project.name} — NDM Calibrator"
        self.topbar.saved_badge.style().unpolish(self.topbar.saved_badge)
        self.topbar.saved_badge.style().polish(self.topbar.saved_badge)
        self.setWindowTitle(title)

    def _theme_notice(self):
        self.show_toast("当前迁移版本使用浅色主题")

    # ------------------------------------------------------------------ #
    # Project lifecycle
    # ------------------------------------------------------------------ #
    def new_project_dialog(self):
        if not self._confirm_discard():
            return
        name, accepted = QInputDialog.getText(self, "新建项目", "项目名称:", text="未命名项目")
        if not accepted:
            return
        name = name.strip() or "未命名项目"
        description, accepted = QInputDialog.getText(self, "新建项目", "项目描述 (可选):")
        if not accepted:
            description = ""
        self.app.new_project(name, description)
        self._last_import_path = None
        self._last_import_frame = None
        self._after_project_change()
        self.navigate("model")
        self.show_toast(f"已新建项目: {name}")

    def open_project_dialog(self):
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "打开项目", "", "NDM 项目 (*.ndmc)")
        if not path:
            return
        try:
            self.app.open_project(path)
            self._last_import_path = None
            self._last_import_frame = None
            self._after_project_change()
            self.navigate("dashboard")
            self.show_toast("项目已打开")
        except NDMCError as exc:
            self._error_dialog("打开项目失败", str(exc))

    def save_project(self):
        project = self.app.project
        if project is None:
            self.show_toast("请先新建或打开项目")
            return False
        try:
            if project.file_path is None:
                return self.save_project_as()
            self.app.save_project()
            self._after_project_change()
            self.show_toast("项目已保存")
            return True
        except NDMCError as exc:
            self._error_dialog("保存项目失败", str(exc))
            return False

    def save_project_as(self):
        if self.app.project is None:
            self.show_toast("请先新建或打开项目")
            return False
        path, _ = QFileDialog.getSaveFileName(self, "另存为项目", "", "NDM 项目 (*.ndmc)")
        if not path:
            return False
        try:
            self.app.save_project(path)
            self._after_project_change()
            self.show_toast("项目已另存")
            return True
        except NDMCError as exc:
            self._error_dialog("保存项目失败", str(exc))
            return False

    def _confirm_discard(self) -> bool:
        project = self.app.project
        if project is None or not project.dirty:
            return True
        choice = UnsavedChangesDialog.ask(self, "未保存的修改", "当前项目有未保存的修改，是否保存？")
        if choice == "save":
            return bool(self.save_project())
        return choice == "discard"

    # ------------------------------------------------------------------ #
    # Data import and mapping
    # ------------------------------------------------------------------ #
    def _import_signal(self, value: Any = None):
        if isinstance(value, (str, Path)):
            self._run_import(str(value))
        else:
            self.show_import_dialog()

    def show_import_dialog(self):
        if self.app.project is None:
            self.show_toast("请先新建或打开项目")
            self.navigate("dashboard")
            return
        path, _ = QFileDialog.getOpenFileName(self, "导入实验数据", "", "数据文件 (*.csv *.xlsx *.xlsm)")
        if path:
            self._run_import(path)

    def _run_import(self, path: str):
        try:
            page = self.pages.get("data")
            # Let the v2 data page retain its raw frame and editable role
            # mapping.  The fallback keeps this controller usable with a
            # minimal/custom data page.
            if page is not None and hasattr(page, "import_file"):
                ok = bool(page.import_file(path))
                if not ok:
                    return
                df = getattr(page, "_raw_df", None)
                summary = {
                    "source": Path(path).name,
                    "quality_warnings": self.app.project.settings.get("data", {}).get("quality_warnings", []) if self.app.project else [],
                }
            else:
                df, summary = import_frame(self.app, path)
            self._last_import_path = Path(path)
            self._last_import_frame = df
            if page is not None:
                for method_name in ("set_dataframe", "set_frame"):
                    method = getattr(page, method_name, None)
                    if method is not None:
                        method(df)
                        break
                setter = getattr(page, "set_mapping_summary", None)
                if setter is not None:
                    setter(summary)
            self._after_project_change()
            self.navigate("data")
            warnings = summary.get("quality_warnings") or []
            self.show_toast(f"已导入 {summary.get('source', Path(path).name)}" + (f" · {len(warnings)} 条质量提示" if warnings else ""))
        except (NDMCError, ValueError, KeyError) as exc:
            self._error_dialog("导入数据失败", str(exc))

    def apply_mapping_scheme(self, scheme: dict[str, Any]):
        """Apply a role mapping selected on the data page."""

        if self.app.project is None:
            raise NDMCError("请先新建项目")
        path = self._last_import_path
        df = self._last_import_frame
        if df is None and path is not None:
            from data.loader import load_dataframe

            df, _ = load_dataframe(path)
        if df is None:
            return
        from data.mapping import map_columns
        from data.validator import describe_dataframe, validate_series

        time_col = scheme.get("time")
        inputs = list(scheme.get("inputs", []))
        outputs = list(scheme.get("outputs", []))
        ignored = list(scheme.get("ignored", []))
        experiment = map_columns(df, time_col, inputs, outputs, ignored)
        project = self.app.project
        project.experiment = experiment
        project.mapping = {"time": time_col, "inputs": {c: c for c in inputs}, "outputs": {c: c for c in outputs}, "ignored": ignored}
        project.settings.setdefault("data", {})["quality_warnings"] = validate_series(experiment.time, experiment.inputs, experiment.outputs)
        project.settings["data"]["summary"] = describe_dataframe(df)
        project.mark_dirty()
        self._after_project_change()
        self.show_toast("字段映射已应用")

    def reset_data(self):
        project = self.app.project
        if project is None:
            return
        project.experiment = None
        project.mapping = {}
        project.settings.pop("data", None)
        project.mark_dirty()
        page = self.pages.get("data")
        if page is not None:
            clear = getattr(page, "clear_dataframe", None)
            if clear:
                clear()
        self._after_project_change()
        self.show_toast("数据已清除")

    def preprocess_data(self, operation: str, **kwargs):
        project = self.app.project
        if project is None or project.experiment is None:
            raise NDMCError("请先导入数据")
        from data import preprocessing

        history = project.preprocess_log
        if operation == "drop_nan":
            project.experiment = preprocessing.drop_nan_rows(project.experiment, history)
        elif operation == "interpolate":
            project.experiment = preprocessing.interpolate_nan(project.experiment, history)
        elif operation == "range":
            project.experiment = preprocessing.select_time_range(project.experiment, kwargs.get("start"), kwargs.get("end"), history)
        else:
            raise NDMCError(f"未知预处理操作: {operation}")
        project.mark_dirty()
        self._after_project_change()

    # ------------------------------------------------------------------ #
    # Model and parameter helpers
    # ------------------------------------------------------------------ #
    def set_model(self, model):
        self.app.set_model(model)
        self._after_project_change()

    def sync_parameters_from_model(self):
        project = self.app.project
        if project is None or project.model is None:
            raise NDMCError("请先定义模型")
        project.parameters.sync_from_names(project.model.parameters)
        project.mark_dirty()
        self._after_project_change()

    def update_parameter_table(self, rows):
        """Persist rows emitted by the compact v2 parameter grid."""

        project = self.app.project
        if project is None:
            return
        from core.parameter import Parameter, ParameterTable

        table = ParameterTable()
        for row in rows:
            try:
                name, initial, lower, upper, status = row[:5]
                free = str(status) not in ("固定", "fixed", "False", "false")
                p = Parameter(str(name), float(initial), float(lower) if str(lower) not in ("—", "-") else -1e12, float(upper) if str(upper) not in ("—", "-") else 1e12, free)
                table.add(p)
            except (TypeError, ValueError):
                continue
        self.app.set_parameter_table(table)
        self._after_project_change()

    def validate_parameters(self) -> list[str]:
        project = self.app.project
        if project is None:
            return []
        errors = []
        for p in project.parameters:
            try:
                p.validate()
            except ValueError as exc:
                errors.append(str(exc))
        return errors

    # ------------------------------------------------------------------ #
    # Background numerical work
    # ------------------------------------------------------------------ #
    def _start_worker(self, kind: str, fn: Callable, on_ok: Callable[[Any], None] | None = None):
        if self._worker is not None and self._worker.isRunning():
            raise NDMCError("已有后台任务正在运行")
        worker = RunWorker(fn, self)
        self._worker = worker
        self._worker_kind = kind

        def done(result):
            if self._worker is worker:
                self._worker = None
            if on_ok:
                on_ok(result)
            self._after_project_change()
            worker.deleteLater()

        def failed(message):
            if self._worker is worker:
                self._worker = None
            if kind == "identification":
                page = self.pages.get("identification")
                if page is not None:
                    handler = getattr(page, "on_identification_error", None)
                    if handler:
                        handler(message)
            elif kind in ("bootstrap", "stability"):
                page = self.pages.get("uncertainty")
                handler = getattr(page, "on_analysis_error", None) if page else None
                if handler:
                    handler(kind, message)
            if "取消" not in str(message):
                self.show_toast(f"{kind} 失败: {message}")
            self._after_project_change()
            worker.deleteLater()

        worker.finished_ok.connect(done)
        worker.finished_error.connect(failed)
        worker.start()
        return worker

    def run_identification_async(self, algorithm: str, options: dict[str, Any]):
        project = self.app.project
        if project is None:
            raise NDMCError("请先新建或打开项目")
        # A new run supersedes the currently displayed fit.  Clearing the
        # current artifact up front prevents a cancelled/failed run from
        # being mistaken for the previous successful result.
        for key in ("identification", "calibration", "diagnostics"):
            project.results.pop(key, None)
        project.mark_dirty()
        project.settings.setdefault("identification", {}).update({
            k: options[k] for k in (
                "rtol", "atol", "input_interpolation", "solver_method", "objective",
                "huber_delta", "method", "max_iterations", "tolerance",
            ) if k in options
        })

        def work(token):
            if token.cancelled():
                raise CancelledError()
            run_options = dict(options)
            run_options["_cancel_token"] = token
            from app.application import run_identification_for_project

            result = run_identification_for_project(project, algorithm, run_options)
            if token.cancelled():
                project.results.pop("identification", None)
                project.results.pop("calibration", None)
                raise CancelledError()
            # Calibration and diagnostics can involve many simulations for
            # sensitivity/identifiability.  Keep that work in the worker so
            # the GUI thread only updates widgets when everything is ready.
            calibration_error = None
            try:
                from diagnostics.orchestrator import run_calibration_and_diagnostics

                run_calibration_and_diagnostics(
                    project,
                    result.get("parameters", {}),
                )
            except Exception as exc:
                # A fit is still useful when a post-fit diagnostic fails; the
                # page will show the fit and surface this secondary warning.
                calibration_error = str(exc)
            if token.cancelled():
                project.results.pop("identification", None)
                project.results.pop("calibration", None)
                raise CancelledError()
            return {"identification": result, "calibration_error": calibration_error}

        def done(payload):
            if self.app.project is not project:
                return
            result = payload.get("identification", payload) if isinstance(payload, dict) else payload
            page = self.pages.get("identification")
            if page is not None:
                handler = getattr(page, "on_identification_done", None)
                if handler:
                    try:
                        handler(result)
                    except TypeError:
                        handler()
            calibration_error = payload.get("calibration_error") if isinstance(payload, dict) else None
            if calibration_error:
                self.show_toast(f"校准/诊断计算失败: {calibration_error}")
            self.navigate("calibration")
            self.show_toast("参数辨识已完成")

        return self._start_worker("identification", work, done)

    def cancel_worker(self):
        if self._worker is not None:
            self._worker.cancel()

    def wait_for_worker(self, timeout_ms: int = 5000) -> bool:
        """Request cancellation and wait briefly for a running task to exit."""

        worker = self._worker
        if worker is None:
            return True
        worker.cancel()
        if worker.isRunning():
            worker.wait(max(0, int(timeout_ms)))
        return not worker.isRunning()

    def _run_calibration(self):
        project = self.app.project
        if project is None:
            return None
        entry = project.results.get("identification", {})
        params = entry.get("result", {}).get("parameters")
        if not params:
            return None
        from diagnostics.orchestrator import run_calibration_and_diagnostics

        try:
            result = run_calibration_and_diagnostics(project, params)
        except Exception as exc:
            logger.warning("校准/诊断计算失败: %s", exc)
            self.show_toast(f"校准计算失败: {exc}")
            return None
        self._after_project_change()
        return result

    def run_bootstrap_async(self, options: dict[str, Any], callback: Callable[[Any], None] | None = None):
        project = self.app.project
        if project is None:
            raise NDMCError("请先新建或打开项目")
        project.results.pop("bootstrap", None)
        project.mark_dirty()

        def work(token):
            if token.cancelled():
                raise CancelledError()
            run_options = dict(options)
            run_options["_cancel_token"] = token
            from app.application import run_bootstrap_for_project

            result = run_bootstrap_for_project(project, run_options)
            if token.cancelled():
                project.results.pop("bootstrap", None)
                raise CancelledError()
            return result

        def done(result):
            if self.app.project is project and callback is not None:
                callback(result)

        return self._start_worker("bootstrap", work, done if callback is not None else None)

    def run_stability_async(self, options: dict[str, Any], callback: Callable[[Any], None] | None = None):
        project = self.app.project
        if project is None:
            raise NDMCError("请先新建或打开项目")
        project.results.pop("stability", None)
        project.mark_dirty()

        def work(token):
            if token.cancelled():
                raise CancelledError()
            run_options = dict(options)
            run_options["_cancel_token"] = token
            from app.application import run_stability_for_project

            result = run_stability_for_project(project, run_options)
            if token.cancelled():
                project.results.pop("stability", None)
                raise CancelledError()
            return result

        def done(result):
            if self.app.project is project and callback is not None:
                callback(result)

        return self._start_worker("stability", work, done if callback is not None else None)

    # ------------------------------------------------------------------ #
    # Export and settings
    # ------------------------------------------------------------------ #
    def export_results(self, dest: str, fmt: str, checks: dict[str, bool] | None = None) -> str:
        project = self.app.project
        if project is None:
            raise NDMCError("请先新建或打开项目")
        checks = checks or {"summary": True, "parameters": True, "metrics": True, "simulation": True, "residuals": True, "diagnostics": True, "bootstrap": True}
        if not any(checks.values()):
            raise NDMCError("请至少选择一项导出内容")
        dest_path = Path(dest).expanduser()
        dest_path.mkdir(parents=True, exist_ok=True)
        if fmt in ("excel", "xlsx"):
            from export.excel_exporter import export_excel

            return export_excel(project, dest_path, checks)
        if fmt in ("csv", "CSV"):
            from export.csv_exporter import export_csv

            paths = export_csv(project, dest_path, checks)
            return "\n".join(paths)
        if fmt in ("png", "figures", "image"):
            from export.figure_exporter import export_figures

            return "\n".join(export_figures(project, dest_path, checks))
        if fmt in ("report", "html"):
            from export.report_exporter import export_html_report

            return export_html_report(project, dest_path, checks)
        raise NDMCError(f"未知导出格式: {fmt}")

    # ------------------------------------------------------------------ #
    def _build_shortcuts(self):
        shortcuts = (
            ("Ctrl+N", self.new_project_dialog),
            ("Ctrl+O", self.open_project_dialog),
            ("Ctrl+S", self.save_project),
            ("Ctrl+Shift+S", self.save_project_as),
            ("Ctrl+I", self.show_import_dialog),
            ("Ctrl+Enter", lambda: getattr(self.pages.get("identification"), "start", lambda: None)()),
            ("Ctrl+,", lambda: self.navigate("settings")),
            ("F1", lambda: self.navigate("about")),
        )
        for sequence, slot in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(sequence))
            action.triggered.connect(slot)
            self.addAction(action)

    def _restore_ui_state(self):
        # The migration reference keeps the collapse state in memory for the
        # current session only.  SettingsPage still exposes the control, but
        # a fresh MainWindow always starts expanded.
        return None

    def _error_dialog(self, title: str, message: str):
        AlertDialog.show_message(self, title, str(message))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "toast") and self.toast.isVisible():
            self.toast.reposition()

    def closeEvent(self, event):
        # Stop numerical work before asking about unsaved changes; otherwise a
        # worker could still mutate the project while the modal dialog is open.
        if self._worker is not None and self._worker.isRunning():
            self.wait_for_worker()
        if not self._confirm_discard():
            event.ignore()
            return
        self._closed = True
        event.accept()
