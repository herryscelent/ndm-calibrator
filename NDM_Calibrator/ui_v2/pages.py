from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from PySide6.QtCore import QSortFilterProxyModel, Qt, QTimer, Signal, QSize, QModelIndex
from PySide6.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QSpinBox, QSplitter, QTabWidget, QTableView, QVBoxLayout,
    QWidget, QFileDialog, QInputDialog, QMessageBox,
)

from . import tokens as t
from .components import Card, ComboBoxDelegate, ConfirmDialog, DoubleSpinBoxDelegate, MetricCard, PageHeader, SimpleTableModel, badge, button, section_title, table_view
from ui.design.icons import icon
from .mock_data import BOOTSTRAP, CONVERGENCE, DATA_ROWS, HISTOGRAM, METRICS, PARAMETERS, PROJECT, RESIDUALS, TIME_SERIES
from .plots import EngineeringPlot

from core.exceptions import DataError, DataValidationError, ModelError, NDMCError
from core.model_definition import (
    DynamicModel,
    builtin_model_keys,
    builtin_model_labels,
    get_builtin_model,
)
from core.parameter import Parameter, ParameterTable
from ui.components.parameter_table import ParameterTableModel


def _window_app(widget: QWidget):
    """Return the optional Application facade attached by MainWindow.

    The frozen Mock window intentionally did not require a backend.  Looking
    the facade up lazily keeps every page usable in that mode while allowing
    the same page to operate on a real ``Project`` when one is attached.
    """

    window = widget.window()
    return getattr(window, "app", None)


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return [str(col) for col in df.columns if pd.to_numeric(df[col], errors="coerce").notna().any()]


def _auto_mapping(df: pd.DataFrame, model: DynamicModel | None = None) -> tuple[str | None, list[str], list[str], list[str]]:
    """Infer time/input/output/ignored columns using names then numeric order."""

    columns = [str(c) for c in df.columns]
    numeric = _numeric_columns(df)
    time_col = next((candidate for candidate in ("time", "t", "Time", "时间") if candidate in columns and candidate in numeric), None)
    if time_col is None and numeric:
        time_col, numeric = numeric[0], numeric[1:]
    else:
        numeric = [c for c in numeric if c != time_col]

    if model is not None:
        output_candidates = [name for name in model.outputs if name in numeric]
        input_candidates = [name for name in model.inputs if name in numeric and name not in output_candidates]
        # A model may use semantic names while the file uses generic columns;
        # fill unmatched roles deterministically from the remaining columns.
        remaining = [c for c in numeric if c not in output_candidates and c not in input_candidates]
        output_candidates += remaining[: max(0, len(model.outputs) - len(output_candidates))]
        input_candidates += [c for c in remaining if c not in output_candidates]
        outputs = output_candidates or (numeric[-1:] if numeric else [])
        inputs = input_candidates
    else:
        outputs = numeric[-1:] if numeric else []
        inputs = numeric[:-1] if numeric else []
    ignored = [c for c in columns if c != time_col and c not in inputs and c not in outputs]
    return time_col, inputs, outputs, ignored


def _clone_experiment(experiment):
    """Copy an Experiment without sharing mutable NumPy arrays."""

    if experiment is None:
        return None
    from core.experiment import Experiment

    return Experiment(
        time=np.array(experiment.time, dtype=float, copy=True),
        inputs={name: np.array(values, dtype=float, copy=True) for name, values in experiment.inputs.items()},
        outputs={name: np.array(values, dtype=float, copy=True) for name, values in experiment.outputs.items()},
        ignored=list(experiment.ignored),
    )


class BasePage(QWidget):
    toast_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(t.PAGE_PADDING, t.PAGE_PADDING, t.PAGE_PADDING, t.PAGE_PADDING)
        self.root.setSpacing(20)

    def add_header(self, title: str, description: str, action: QWidget | None = None):
        self.root.addWidget(PageHeader(title, description, action))


class DashboardPage(BasePage):
    navigate_requested = Signal(str)
    new_project_requested = Signal()
    open_project_requested = Signal()

    def __init__(self):
        super().__init__()
        actions = QWidget()
        action_row = QHBoxLayout(actions)
        action_row.setContentsMargins(0, 0, 0, 0)
        new_project = button("新建项目", "secondary")
        open_project = button("打开项目", "primary", "folder")
        new_project.clicked.connect(self.new_project_requested)
        open_project.clicked.connect(self.open_project_requested)
        self.new_project_button = new_project
        self.open_project_button = open_project
        action_row.addWidget(new_project)
        action_row.addWidget(open_project)
        self.add_header("项目首页", "查看当前模型、数据、参数辨识结果及整体工作流程。", actions)

        summary = Card()
        self.summary_name = section_title(PROJECT["name"])
        self.summary_description = QLabel(PROJECT["description"], objectName="BodySecondary")
        self.summary_updated = QLabel(f"最后更新：{PROJECT['updated']}", objectName="Muted")
        self.summary_badge = badge("● 就绪", "success")
        summary.layout().addWidget(self.summary_name)
        summary.layout().addWidget(self.summary_description)
        summary.layout().addWidget(self.summary_updated)
        summary.layout().addWidget(self.summary_badge, 0, Qt.AlignmentFlag.AlignLeft)
        self.root.addWidget(summary)

        metrics = QHBoxLayout()
        self.metric_samples = MetricCard("样本数", f"{PROJECT['samples']:,}")
        self.metric_params = MetricCard("待辨识参数", "2")
        self.metric_rmse = MetricCard("RMSE", f"{METRICS['RMSE']:.4f}")
        self.metric_r2 = MetricCard("R²", f"{METRICS['R2']:.4f}")
        for card in (self.metric_samples, self.metric_params, self.metric_rmse, self.metric_r2):
            metrics.addWidget(card, 1)
        self.root.addLayout(metrics)

        body = QHBoxLayout()
        body.setSpacing(24)
        body.setAlignment(Qt.AlignmentFlag.AlignTop)
        workflow = QWidget()
        self.workflow_panel = workflow
        flow_layout = QVBoxLayout(workflow)
        flow_layout.setContentsMargins(0, 0, 0, 0)
        flow_layout.addWidget(section_title("工作流程"))
        line = QFrame(objectName="SectionLine")
        flow_layout.addWidget(line)
        for key, label in (("data", "数据管理"), ("model", "模型定义"), ("parameters", "参数配置"), ("identification", "参数辨识"), ("calibration", "模型校准"), ("diagnostics", "诊断分析")):
            item = QPushButton(label)
            item.setIcon(icon("check_circle", t.ACCENT))
            item.setIconSize(QSize(16, 16))
            item.setStyleSheet(f"text-align:left; color:{t.TEXT_PRIMARY}; min-height:34px;")
            item.clicked.connect(partial(self.navigate_requested.emit, key))
            flow_layout.addWidget(item)
        flow_layout.addStretch(1)
        body.addWidget(workflow, 2)

        plot_area = QWidget()
        plot_layout = QVBoxLayout(plot_area)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        plot_layout.addWidget(section_title("实测值与模拟值"))
        plot = EngineeringPlot("时间 (s)", "position", 220)
        self.dashboard_plot = plot
        plot.setMaximumHeight(260)
        xs = [r[0] for r in TIME_SERIES]
        plot.line(xs, [r[1] for r in TIME_SERIES], t.ACCENT, "实测值")
        plot.line(xs, [r[2] for r in TIME_SERIES], t.CHART_SIMULATED, "模拟值")
        plot.plot.setXRange(0, 50, padding=0)
        plot_layout.addWidget(plot)
        body.addWidget(plot_area, 3, Qt.AlignmentFlag.AlignTop)
        self.root.addLayout(body, 1)

    def on_project_changed(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        self.summary_name.setText(project.name or "未命名项目")
        self.summary_description.setText(project.description or "")
        self.summary_updated.setText(f"最后更新：{project.modified_at or project.created_at}")
        self.summary_badge.setText("● 未保存" if project.dirty else "● 就绪")
        self.summary_badge.setProperty("badge", "warning" if project.dirty else "success")
        self.summary_badge.style().unpolish(self.summary_badge)
        self.summary_badge.style().polish(self.summary_badge)
        exp = project.experiment
        self.metric_samples.set_value(f"{exp.n_points:,}" if exp else "—")
        free = len(project.parameters.free_parameters())
        self.metric_params.set_value(str(free))
        metrics = project.results.get("calibration", {}).get("metrics", {}).get("summary", {})
        self.metric_rmse.set_value(f"{metrics['RMSE']:.4g}" if metrics.get("RMSE") is not None else "—")
        self.metric_r2.set_value(f"{metrics['R2']:.4g}" if metrics.get("R2") is not None else "—")
        # Redraw the dashboard plot from the current experiment/result when
        # available; keep the deterministic reference plot until then.
        if exp is not None:
            self.dashboard_plot.clear()
            x = exp.time.tolist()
            for name, values in exp.outputs.items():
                self.dashboard_plot.line(x, values.tolist(), t.ACCENT, f"实测 · {name}")
                prediction = None
                cal = project.results.get("calibration", {})
                if isinstance(cal, dict):
                    prediction = cal.get("predicted", {}).get(name)
                if prediction is not None:
                    self.dashboard_plot.line(x, prediction, t.CHART_SIMULATED, f"模拟 · {name}")
        else:
            self.dashboard_plot.clear()


class DataPage(BasePage):
    """Data import, mapping, validation and preprocessing surface.

    ``ui_v2`` starts in a deterministic Mock state so screenshots and smoke
    tests remain stable.  Once a MainWindow exposes ``app`` (the regular
    :class:`app.application.Application` facade), all changes are written to
    ``app.project`` and the same controls operate on real CSV/XLSX data.
    """

    ROLE_OPTIONS = ["时间", "输入", "输出", "状态", "忽略"]

    def __init__(self):
        super().__init__()
        self._source_path: str | None = None
        self._raw_df: pd.DataFrame | None = None
        self._raw_experiment = None
        self._experiment = None
        self._bound_project = None
        self._mapping_dirty = False

        actions = QWidget()
        action_row = QHBoxLayout(actions)
        action_row.setContentsMargins(0, 0, 0, 0)
        import_csv = button("导入 CSV", "secondary", "folder")
        import_excel = button("导入 Excel", "secondary", "folder")
        import_csv.setToolTip("从 CSV 文件导入实验数据")
        import_excel.setToolTip("从 XLSX 文件导入实验数据")
        import_csv.clicked.connect(partial(self._import_dialog, "csv"))
        import_excel.clicked.connect(partial(self._import_dialog, "excel"))
        self.import_csv_button = import_csv
        self.import_excel_button = import_excel
        action_row.addWidget(import_csv)
        action_row.addWidget(import_excel)
        self.add_header("数据管理", "导入、检查并映射动态系统实验数据。", actions)

        summary = QHBoxLayout()
        self.summary_labels: list[QLabel] = []
        for text in ("4,860 行", "|", "4 列", "|", "0 个缺失值", "|", "时长 81 分钟"):
            label = QLabel(text, objectName="BodySecondary")
            self.summary_labels.append(label)
            summary.addWidget(label)
        summary.addStretch(1)
        choose_range = button("选择范围", "secondary")
        choose_range.setToolTip("按时间范围筛选当前实验数据")
        choose_range.clicked.connect(self.select_time_range)
        missing = button("处理缺失值", "secondary")
        missing.setToolTip("删除或插值处理 NaN/Inf")
        missing.clicked.connect(self.process_missing)
        reset = button("重置", "secondary", "reset")
        reset.setToolTip("恢复导入后的原始数据和映射")
        reset.clicked.connect(self.reset_data)
        self.range_button = choose_range
        self.missing_button = missing
        self.reset_button = reset
        summary.addWidget(choose_range)
        summary.addWidget(missing)
        summary.addWidget(reset)
        self.root.addLayout(summary)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.data_splitter = splitter
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        title_row = QHBoxLayout()
        title_row.addWidget(section_title("数据预览"))
        title_row.addStretch(1)
        search = QLineEdit()
        search.setPlaceholderText("筛选…")
        search.setMaximumWidth(180)
        search.setClearButtonEnabled(True)
        self.search = search
        title_row.addWidget(search)
        left_layout.addLayout(title_row)
        self.data_model = SimpleTableModel(["time", "u", "position", "velocity"], DATA_ROWS)
        self.data_proxy = QSortFilterProxyModel(self)
        self.data_proxy.setSourceModel(self.data_model)
        self.data_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.data_proxy.setFilterKeyColumn(-1)
        search.textChanged.connect(self.data_proxy.setFilterFixedString)
        # Keep a stable, inspectable grid at the minimum desktop width.  The
        # table owns horizontal scrolling instead of forcing the page shell to
        # overflow when imported files contain long or numerous columns.
        data_table = table_view(self.data_proxy, 28, [180, 180, 180, 180])
        self.data_table = data_table
        left_layout.addWidget(data_table)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(section_title("字段映射"))
        mapping_rows = [["time", "时间"], ["u", "输入"], ["position", "输出"], ["velocity", "状态"]]
        self.mapping_model = SimpleTableModel(["字段", "角色"], mapping_rows, {1})
        self.mapping_model.dataChanged.connect(self._on_mapping_changed)
        self.mapping_table = table_view(self.mapping_model, 30, [125, 170])
        self.mapping_table.setItemDelegateForColumn(1, ComboBoxDelegate(self.ROLE_OPTIONS, self.mapping_table))
        self.mapping_table.setMaximumHeight(190)
        right_layout.addWidget(self.mapping_table)
        mapping_actions = QHBoxLayout()
        auto_map = button("自动映射", "secondary", "reset")
        auto_map.setToolTip("根据列名、数值类型和当前模型推断字段角色")
        auto_map.clicked.connect(self.auto_map)
        apply_map = button("应用映射", "primary", "check")
        apply_map.setToolTip("验证并写入当前字段映射")
        apply_map.clicked.connect(self.apply_mapping)
        self.auto_map_button = auto_map
        self.apply_mapping_button = apply_map
        mapping_actions.addWidget(auto_map)
        mapping_actions.addWidget(apply_map)
        mapping_actions.addStretch(1)
        right_layout.addLayout(mapping_actions)
        chart_row = QHBoxLayout()
        chart_row.addWidget(section_title("数据曲线"))
        chart_row.addStretch(1)
        selector = QComboBox()
        selector.addItems(["输出 · position", "状态 · velocity"])
        self.series_selector = selector
        chart_row.addWidget(selector)
        right_layout.addLayout(chart_row)
        plot = EngineeringPlot("时间 (s)", "值", 290)
        self.data_plot = plot
        selector.currentIndexChanged.connect(self._update_plot)
        self._update_plot()
        right_layout.addWidget(plot)
        splitter.addWidget(right)
        splitter.setSizes([690, 460])
        self.root.addWidget(splitter, 1)

    # ------------------------------------------------------------------ #
    # Import and mapping
    # ------------------------------------------------------------------ #
    def _import_dialog(self, kind: str) -> None:
        if kind == "csv":
            filter_text = "CSV 文件 (*.csv)"
        else:
            filter_text = "Excel 文件 (*.xlsx *.xlsm)"
        path, _ = QFileDialog.getOpenFileName(self, "导入数据", "", filter_text)
        if path:
            self.import_file(path)

    def import_file(self, path: str | Path) -> bool:
        """Load a file, auto-map its numeric columns and persist the result."""

        try:
            from data.loader import load_dataframe

            df, source = load_dataframe(path)
            self._source_path = str(path)
            self._raw_df = df.copy()
            self._set_dataframe(df)

            model = None
            app = _window_app(self)
            if app is not None and getattr(app, "project", None) is not None:
                model = getattr(app.project, "model", None)
            time_col, inputs, outputs, ignored = _auto_mapping(df, model)
            if time_col is None:
                raise DataValidationError("未找到可用的时间列")
            self._set_mapping_rows(df.columns, time_col, inputs, outputs, ignored)

            # Importing into a fresh UI is a natural way to start a project;
            # existing projects are left untouched until a valid mapping is
            # available.  Application.import_data performs the same mapping
            # through the domain service and records the source metadata.
            if app is not None:
                if getattr(app, "project", None) is None:
                    app.new_project(Path(path).stem or "未命名项目")
                self._apply_mapping_to_project(show_toast=False)
            else:
                self._build_preview_experiment(show_toast=False)
            refresh = getattr(self.window(), "_after_project_change", None)
            if callable(refresh):
                refresh()
            self.toast_requested.emit(f"已载入 {source}")
            return True
        except (DataError, DataValidationError, OSError, ValueError) as exc:
            self.toast_requested.emit(f"导入失败：{exc}")
            return False

    def _set_dataframe(self, df: pd.DataFrame) -> None:
        headers = [str(c) for c in df.columns]
        rows = []
        for values in df.itertuples(index=False, name=None):
            row = []
            for value in values:
                if pd.isna(value):
                    row.append("")
                elif isinstance(value, (float, np.floating)):
                    row.append(f"{float(value):.6g}")
                else:
                    row.append(str(value))
            rows.append(row)
        self.data_model.headers = headers
        self.data_model.replace_rows(rows)
        for column, width in enumerate([180] * len(headers)):
            self.data_table.setColumnWidth(column, width)
        self._update_summary(df=df)

    def _set_mapping_rows(
        self,
        columns: Iterable[object],
        time_col: str | None,
        inputs: Iterable[str],
        outputs: Iterable[str],
        ignored: Iterable[str],
    ) -> None:
        input_set, output_set, ignored_set = set(inputs), set(outputs), set(ignored)
        rows = []
        for raw in columns:
            col = str(raw)
            role = "时间" if col == time_col else "输入" if col in input_set else "输出" if col in output_set else "忽略" if col in ignored_set else "忽略"
            rows.append([col, role])
        self.mapping_model.replace_rows(rows)

    def auto_map(self) -> bool:
        if self._raw_df is None:
            self.toast_requested.emit("请先导入数据")
            return False
        app = _window_app(self)
        model = getattr(getattr(app, "project", None), "model", None) if app is not None else None
        time_col, inputs, outputs, ignored = _auto_mapping(self._raw_df, model)
        if time_col is None:
            self.toast_requested.emit("未找到可用的时间列")
            return False
        self._set_mapping_rows(self._raw_df.columns, time_col, inputs, outputs, ignored)
        self.toast_requested.emit("已根据列名和数值类型自动映射")
        return self.apply_mapping()

    def _on_mapping_changed(self, *_args) -> None:
        self._mapping_dirty = True

    def _mapping_roles(self) -> tuple[str | None, list[str], list[str], list[str]]:
        time_col = None
        inputs: list[str] = []
        outputs: list[str] = []
        ignored: list[str] = []
        for row in self.mapping_model.rows:
            if len(row) < 2:
                continue
            col, role = str(row[0]), str(row[1])
            if role == "时间":
                if time_col is not None:
                    raise DataValidationError("只能映射一个时间列")
                time_col = col
            elif role == "输入":
                inputs.append(col)
            elif role in ("输出", "状态"):
                outputs.append(col)
            else:
                ignored.append(col)
        if not time_col:
            raise DataValidationError("请指定时间列")
        if not inputs and not outputs:
            raise DataValidationError("至少映射一个输入或输出列")
        return time_col, inputs, outputs, ignored

    def _build_preview_experiment(self, show_toast: bool = True):
        if self._raw_df is None:
            return None
        from data.mapping import map_columns

        time_col, inputs, outputs, ignored = self._mapping_roles()
        experiment = map_columns(self._raw_df, time_col, inputs, outputs, ignored)
        self._raw_experiment = _clone_experiment(experiment)
        self._experiment = experiment
        self._update_summary(experiment=experiment)
        self._set_plot_series(experiment)
        if show_toast:
            self.toast_requested.emit("字段映射已应用")
        return experiment

    def _apply_mapping_to_project(self, show_toast: bool = True):
        app = _window_app(self)
        if app is None:
            return self._build_preview_experiment(show_toast=show_toast)
        if getattr(app, "project", None) is None:
            raise NDMCError("请先新建或打开项目")
        if not self._source_path:
            if self._raw_df is None:
                raise DataValidationError("没有可用的数据文件")
        time_col, inputs, outputs, ignored = self._mapping_roles()
        # A reopened .ndmc stores the mapped arrays but not the original file
        # path.  Persist an edited mapping directly from the reconstructed
        # frame in that case; freshly imported files still use the facade's
        # loader and retain their source metadata.
        source_path = Path(self._source_path) if self._source_path else None
        if source_path is not None and source_path.is_file():
            app.import_data(source_path, time_col, inputs, outputs, ignored)
        else:
            from data.mapping import map_columns
            from data.validator import describe_dataframe, validate_series

            experiment = map_columns(self._raw_df, time_col, inputs, outputs, ignored)
            project = app.project
            project.mapping = {
                "time": time_col,
                "inputs": {name: name for name in inputs},
                "outputs": {name: name for name in outputs},
                "ignored": ignored,
            }
            project.column_types = {str(col): str(dtype) for col, dtype in self._raw_df.dtypes.items()}
            project.experiment = experiment
            project.settings.setdefault("data", {})["quality_warnings"] = validate_series(
                experiment.time, experiment.inputs, experiment.outputs
            )
            project.settings["data"]["summary"] = describe_dataframe(self._raw_df)
            if hasattr(app, "clear_results"):
                app.clear_results()
            project.mark_dirty()
        project = app.project
        self._raw_experiment = _clone_experiment(project.experiment)
        self._experiment = project.experiment
        self._bound_project = project
        self._mapping_dirty = False
        self._update_summary(experiment=project.experiment)
        self._set_plot_series(project.experiment)
        if hasattr(project, "mark_dirty"):
            project.mark_dirty()
        refresh = getattr(self.window(), "_after_project_change", None)
        if callable(refresh):
            refresh()
        if show_toast:
            self.toast_requested.emit("字段映射已应用")
        return project.experiment

    def apply_mapping(self) -> bool:
        try:
            self._apply_mapping_to_project()
            return True
        except (DataError, DataValidationError, NDMCError, ValueError) as exc:
            self.toast_requested.emit(f"映射失败：{exc}")
            return False

    # ------------------------------------------------------------------ #
    # Validation and preprocessing
    # ------------------------------------------------------------------ #
    def _current_experiment(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        return getattr(project, "experiment", None) or self._experiment or self._raw_experiment

    def validate_data(self) -> list[str]:
        experiment = self._current_experiment()
        if experiment is None:
            self.toast_requested.emit("请先导入并应用字段映射")
            return []
        from data.validator import validate_series

        try:
            warnings = validate_series(experiment.time, experiment.inputs, experiment.outputs)
        except DataValidationError as exc:
            self.toast_requested.emit(f"数据校验失败：{exc}")
            return [str(exc)]
        if warnings:
            self.toast_requested.emit("数据校验完成：" + "；".join(warnings[:2]))
        else:
            self.toast_requested.emit("数据校验通过")
        return warnings

    def process_missing(self, method: str | None = None) -> bool:
        experiment = self._current_experiment()
        if experiment is None:
            self.toast_requested.emit("请先导入并应用字段映射")
            return False
        if method is None:
            options = ["删除缺失行", "线性插值"]
            value, ok = QInputDialog.getItem(self, "处理缺失值", "处理方式", options, 0, False)
            if not ok:
                return False
            method = value
        history = list(getattr(getattr(_window_app(self), "project", None), "preprocess_log", []) or [])
        try:
            from data.preprocessing import drop_nan_rows, interpolate_nan

            if method in ("drop", "删除", "删除缺失行"):
                new = drop_nan_rows(experiment, history)
            elif method in ("interpolate", "插值", "线性插值"):
                new = interpolate_nan(experiment, history)
            else:
                raise DataValidationError(f"未知缺失值处理方式: {method}")
            self._set_processed_experiment(new, history)
            self.toast_requested.emit("缺失值处理完成")
            return True
        except (DataError, DataValidationError, ValueError) as exc:
            self.toast_requested.emit(f"处理失败：{exc}")
            return False

    def select_time_range(self, t_start: float | None = None, t_end: float | None = None) -> bool:
        experiment = self._current_experiment()
        if experiment is None:
            self.toast_requested.emit("请先导入并应用字段映射")
            return False
        if t_start is None:
            value, ok = QInputDialog.getDouble(self, "选择时间范围", "起始时间", float(experiment.time.min()), -1e12, 1e12, 6)
            if not ok:
                return False
            t_start = value
        if t_end is None:
            value, ok = QInputDialog.getDouble(self, "选择时间范围", "结束时间", float(experiment.time.max()), -1e12, 1e12, 6)
            if not ok:
                return False
            t_end = value
        if t_start > t_end:
            self.toast_requested.emit("时间范围无效：起始时间不能大于结束时间")
            return False
        history = list(getattr(getattr(_window_app(self), "project", None), "preprocess_log", []) or [])
        try:
            from data.preprocessing import select_time_range

            new = select_time_range(experiment, t_start, t_end, history)
            self._set_processed_experiment(new, history)
            self.toast_requested.emit(f"已选择时间区间 [{t_start:g}, {t_end:g}]")
            return True
        except (DataError, DataValidationError, ValueError) as exc:
            self.toast_requested.emit(f"选择范围失败：{exc}")
            return False

    def _set_processed_experiment(self, experiment, history: list[str]) -> None:
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is not None:
            if hasattr(app, "clear_results"):
                app.clear_results()
            project.experiment = experiment
            project.preprocess_log = history
            project.mark_dirty()
        self._experiment = experiment
        self._update_summary(experiment=experiment)
        self._set_plot_series(experiment)
        refresh = getattr(self.window(), "_after_project_change", None)
        if callable(refresh):
            refresh()

    def reset_data(self) -> bool:
        if self._raw_experiment is not None:
            restored = _clone_experiment(self._raw_experiment)
            app = _window_app(self)
            project = getattr(app, "project", None) if app is not None else None
            if project is not None:
                if hasattr(app, "clear_results"):
                    app.clear_results()
                project.experiment = restored
                project.preprocess_log = []
                project.mark_dirty()
            self._experiment = restored
            if self._raw_df is not None:
                self._set_dataframe(self._raw_df)
            self._set_plot_series(restored)
            refresh = getattr(self.window(), "_after_project_change", None)
            if callable(refresh):
                refresh()
            self.toast_requested.emit("数据处理已重置")
            return True
        app = _window_app(self)
        if app is not None and getattr(app, "project", None) is not None:
            self.data_model.headers = ["time"]
            self.data_model.replace_rows([])
            self.mapping_model.replace_rows([])
            self._update_summary()
            self.series_selector.clear()
            self.series_selector.addItem("暂无数据")
            self.data_plot.clear()
            refresh = getattr(self.window(), "_after_project_change", None)
            if callable(refresh):
                refresh()
            self.toast_requested.emit("当前项目暂无数据")
            return True
        self.data_model.headers = ["time", "u", "position", "velocity"]
        self.data_model.replace_rows(DATA_ROWS)
        self.mapping_model.replace_rows([["time", "时间"], ["u", "输入"], ["position", "输出"], ["velocity", "状态"]])
        self._update_summary()
        self._update_plot()
        self.toast_requested.emit("数据视图已重置")
        return True

    # ------------------------------------------------------------------ #
    # Preview and project synchronisation
    # ------------------------------------------------------------------
    def _update_summary(self, df: pd.DataFrame | None = None, experiment=None) -> None:
        if experiment is None and df is None:
            self.summary_labels[0].setText("4,860 行")
            self.summary_labels[2].setText("4 列")
            self.summary_labels[4].setText("0 个缺失值")
            self.summary_labels[6].setText("时长 81 分钟")
            return
        if df is not None:
            n, m = df.shape
            missing = int(df.isna().sum().sum())
            self.summary_labels[0].setText(f"{n:,} 行")
            self.summary_labels[2].setText(f"{m} 列")
            self.summary_labels[4].setText(f"{missing} 个缺失值")
            numeric_time = pd.to_numeric(df.iloc[:, 0], errors="coerce")
            span = float(numeric_time.max() - numeric_time.min()) if numeric_time.notna().any() else 0.0
        else:
            n = experiment.n_points
            m = 1 + experiment.n_inputs + experiment.n_outputs
            bad = sum(int(np.count_nonzero(~np.isfinite(arr))) for arr in [experiment.time, *experiment.inputs.values(), *experiment.outputs.values()])
            self.summary_labels[0].setText(f"{n:,} 行")
            self.summary_labels[2].setText(f"{m} 列")
            self.summary_labels[4].setText(f"{bad} 个缺失值")
            span = float(experiment.time[-1] - experiment.time[0]) if n else 0.0
        self.summary_labels[6].setText(f"时长 {span:g} 秒")

    def _set_plot_series(self, experiment) -> None:
        self.series_selector.blockSignals(True)
        self.series_selector.clear()
        if experiment is None:
            self.series_selector.addItem("输出 · position", ("output", "position"))
            self.series_selector.addItem("状态 · velocity", ("output", "velocity"))
        else:
            for name in experiment.outputs:
                self.series_selector.addItem(f"输出 · {name}", ("output", name))
            for name in experiment.inputs:
                self.series_selector.addItem(f"输入 · {name}", ("input", name))
        self.series_selector.blockSignals(False)
        if self.series_selector.count():
            self.series_selector.setCurrentIndex(0)
        self._update_plot()

    def _update_plot(self):
        self.data_plot.clear()
        experiment = self._current_experiment()
        if experiment is None:
            app = _window_app(self)
            if app is not None and getattr(app, "project", None) is not None:
                return
            xs = [row[0] for row in DATA_ROWS]
            self.data_plot.line(xs, [row[1] for row in DATA_ROWS], t.ACCENT, "输入 (u)")
            value_index = 2 if self.series_selector.currentIndex() == 0 else 3
            label = "position" if value_index == 2 else "velocity"
            self.data_plot.line(xs, [row[value_index] for row in DATA_ROWS], t.CHART_SIMULATED, label)
            return
        xs = experiment.time.tolist()
        for name, values in experiment.inputs.items():
            self.data_plot.line(xs, values.tolist(), t.ACCENT, f"输入 · {name}")
        data = self.series_selector.currentData()
        if not data:
            return
        role, name = data
        values = experiment.outputs.get(name) if role == "output" else experiment.inputs.get(name)
        if values is not None:
            self.data_plot.line(xs, values.tolist(), t.CHART_SIMULATED, name)

    def on_project_changed(self) -> None:
        """Refresh the page after MainWindow creates/opens a project."""

        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            self._update_plot()
            return
        if project.experiment is None:
            # Keep the initial reference mock for the standalone page, but
            # show an explicit empty state once a real project is selected.
            self._bound_project = project
            self._source_path = project.data_source
            self._raw_df = None
            self._raw_experiment = None
            self._experiment = None
            self.data_model.headers = []
            self.data_model.replace_rows([])
            self.mapping_model.replace_rows([])
            self.summary_labels[0].setText("0 行")
            self.summary_labels[2].setText("0 列")
            self.summary_labels[4].setText("0 个缺失值")
            self.summary_labels[6].setText("时长 0 秒")
            self.series_selector.clear()
            self.series_selector.addItem("暂无数据")
            self.data_plot.clear()
            return
        # Keep the imported snapshot across preprocessing refreshes so the
        # Reset action can genuinely restore the preprocessed data.  A new
        # project (or an opened project) starts a fresh snapshot.
        if project is not self._bound_project:
            self._bound_project = project
            self._source_path = project.data_source
            self._raw_df = None
            self._raw_experiment = _clone_experiment(project.experiment)
        elif self._raw_experiment is None:
            self._raw_experiment = _clone_experiment(project.experiment)
        self._experiment = project.experiment
        self._source_path = self._source_path or project.data_source
        self._update_summary(experiment=project.experiment)
        self._set_plot_series(project.experiment)
        if self._raw_df is None:
            columns = [project.mapping.get("time", "time")]
            columns += list(project.mapping.get("inputs", {}).keys())
            columns += list(project.mapping.get("outputs", {}).keys())
            frame = {name: values for name, values in [(columns[0], project.experiment.time)]}
            frame.update(project.experiment.inputs)
            frame.update(project.experiment.outputs)
            self._raw_df = pd.DataFrame(frame)
            self._set_dataframe(self._raw_df)
        self.show_project_mapping(project)

    def show_project_mapping(self, project) -> None:
        mapping = project.mapping or {}
        time_col = mapping.get("time")
        inputs = mapping.get("inputs", {})
        outputs = mapping.get("outputs", {})
        columns = list(self._raw_df.columns) if self._raw_df is not None else [time_col, *inputs.keys(), *outputs.keys()]
        self._set_mapping_rows(columns, time_col, inputs.keys(), outputs.keys(), [c for c in columns if c not in {time_col, *inputs.keys(), *outputs.keys()}])


class ModelPage(BasePage):
    """Built-in and user-defined DynamicModel editor.

    The editor deliberately uses a small, readable text format so a model can
    be copied into a project file.  SymPy validation remains in
    :class:`core.model_definition.DynamicModel`; this page only translates the
    text into that safe domain object and displays its compiled structure.
    """

    model_changed = Signal()
    _HELP = """states:
x1
x2

inputs:
u

parameters:
k
c
m

equations:
dx1/dt = x2
dx2/dt = (-k*x1 - c*x2 + u)/m

outputs:
x1

output equations:
x1 = x1
"""

    def __init__(self):
        super().__init__()
        self._model: DynamicModel | None = None
        self._valid = False
        validate = button("验证模型", "primary", "check")
        validate.setToolTip("解析并校验当前模型，然后写入项目")
        validate.clicked.connect(self.validate_model)
        self.validate_button = validate
        self.add_header("模型定义", "定义状态方程、输入、参数以及观测输出。", validate)

        columns = QHBoxLayout()
        structure = Card()
        structure.layout().addWidget(section_title("模型结构"))
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("来源", objectName="BodySecondary"))
        self.source_combo = QComboBox()
        self.source_combo.addItem("内置模型", "builtin")
        self.source_combo.addItem("用户自定义", "user")
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        source_row.addWidget(self.source_combo, 1)
        structure.layout().addLayout(source_row)
        self.builtin_combo = QComboBox()
        for key in builtin_model_keys():
            self.builtin_combo.addItem(builtin_model_labels()[key], key)
        self.builtin_combo.currentIndexChanged.connect(self._on_builtin_changed)
        structure.layout().addWidget(self.builtin_combo)
        self.builtin_desc = QLabel("", objectName="Muted")
        self.builtin_desc.setWordWrap(True)
        structure.layout().addWidget(self.builtin_desc)
        self.structure_body = QWidget()
        self.structure_layout = QVBoxLayout(self.structure_body)
        self.structure_layout.setContentsMargins(0, 8, 0, 0)
        self.structure_layout.setSpacing(5)
        structure.layout().addWidget(self.structure_body)
        structure.layout().addStretch(1)
        self.structure_card = structure
        columns.addWidget(structure, 1)

        editor = Card()
        editor.layout().addWidget(section_title("方程编辑"))
        code = QPlainTextEdit()
        code.setFont(QFont("Microsoft YaHei UI", 10))
        code.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        code.setPlaceholderText(self._HELP)
        code.setPlainText(self._HELP)
        self.code = code
        self.editor = code  # compatibility with the original editor naming
        editor.layout().addWidget(code, 1)
        self.status_badge = badge("未验证", "neutral")
        editor.layout().addWidget(self.status_badge, 0, Qt.AlignmentFlag.AlignLeft)
        self.error_label = QLabel("", objectName="BodySecondary")
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet(f"color:{t.DANGER};")
        self.error_label.hide()
        editor.layout().addWidget(self.error_label)
        columns.addWidget(editor, 1)
        self.root.addLayout(columns, 1)

        # Match the frozen Mock's second-order example on first launch.
        second_order_index = self.builtin_combo.findData("second_order")
        if second_order_index >= 0:
            self.builtin_combo.setCurrentIndex(second_order_index)
        self._model = DynamicModel.from_builtin("second_order")
        self._render_model(self._model)
        self._on_source_changed()

    def _on_source_changed(self, *_args):
        is_user = self.source_combo.currentData() == "user"
        self.builtin_combo.setVisible(not is_user)
        self.builtin_desc.setVisible(not is_user)
        if not is_user:
            self._on_builtin_changed()

    def _on_builtin_changed(self, *_args):
        key = self.builtin_combo.currentData()
        model = get_builtin_model(key) if key else None
        self.builtin_desc.setText(model.description if model else "")
        if model and self.source_combo.currentData() == "builtin":
            dynamic = DynamicModel.from_builtin(key)
            self._model = dynamic
            self._render_model(dynamic)

    @staticmethod
    def _split_names(value: str) -> list[str]:
        return [item.strip() for item in value.replace(",", " ").replace(";", " ").split() if item.strip()]

    def _parse_user_model(self) -> DynamicModel:
        sections: dict[str, list[str]] = {}
        current: str | None = None
        equations: list[tuple[str, str | None]] = []
        for raw_line in self.code.toPlainText().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            # Accept both ``states:`` and a heading followed by one name per
            # line.  A colon with inline names is also convenient for short
            # definitions.
            head = line.rstrip(":").strip().lower()
            aliases = {
                "states": "states", "状态": "states", "state": "states",
                "inputs": "inputs", "输入": "inputs", "input": "inputs",
                "parameters": "parameters", "参数": "parameters", "params": "parameters",
                "outputs": "outputs", "输出": "outputs", "output": "outputs",
                "equations": "equations", "equation": "equations", "方程": "equations", "dynamics": "equations",
                "output equations": "output_equations", "输出方程": "output_equations",
                "initial": "initial", "initial conditions": "initial", "初始条件": "initial",
            }
            if head in aliases:
                current = aliases[head]
                continue
            if ":" in line and line.split(":", 1)[0].strip().lower() in aliases:
                key, inline = line.split(":", 1)
                current = aliases[key.strip().lower()]
                if inline.strip():
                    sections.setdefault(current, []).extend(self._split_names(inline))
                continue
            if "=" in line:
                equations.append((line, current))
                continue
            if current in ("states", "inputs", "parameters", "outputs", "initial"):
                sections.setdefault(current, []).extend(self._split_names(line))

        states = sections.get("states", [])
        inputs = sections.get("inputs", [])
        parameters = sections.get("parameters", [])
        outputs = sections.get("outputs") or list(states)
        if not states:
            raise ModelError("请定义至少一个状态变量")
        if not parameters:
            raise ModelError("请定义至少一个参数")

        dynamics: dict[str, str] = {}
        output_equations: dict[str, str] = {}
        initial_conditions: dict[str, float] = {}
        for equation, equation_section in equations:
            lhs, rhs = equation.split("=", 1)
            lhs, rhs = lhs.strip(), rhs.strip()
            if "/dt" in lhs:
                dynamics[lhs] = rhs
            elif equation_section == "initial" and lhs in states:
                try:
                    initial_conditions[lhs] = float(rhs)
                except ValueError as exc:
                    raise ModelError(f"初始条件 {lhs} 不是数值") from exc
            elif equation_section == "initial":
                # ``x = 0`` may have been collected as an equation while the
                # current section is initial.
                try:
                    initial_conditions[lhs] = float(rhs)
                except ValueError:
                    pass
            elif lhs in outputs:
                output_equations[lhs] = rhs
        # Parse initial values written as ``x 0`` under the initial section.
        for item in sections.get("initial", []):
            if len(item.split()) == 2:
                name, value = item.split()
                try:
                    initial_conditions[name] = float(value)
                except ValueError:
                    pass
        initial_conditions = {name: initial_conditions.get(name, 0.0) for name in states}
        if not output_equations:
            output_equations = {name: name for name in outputs}
        return DynamicModel.from_user_definition(
            states=states,
            inputs=inputs,
            parameters=parameters,
            dynamics=dynamics,
            outputs=outputs,
            output_equations=output_equations,
            initial_conditions=initial_conditions,
            description="用户自定义模型",
        )

    def validate_model(self) -> bool:
        try:
            if self.source_combo.currentData() == "builtin":
                key = self.builtin_combo.currentData()
                if not key:
                    raise ModelError("请选择内置模型")
                model = DynamicModel.from_builtin(key)
            else:
                model = self._parse_user_model()
            app = _window_app(self)
            if app is not None:
                if getattr(app, "project", None) is None:
                    app.new_project("未命名项目")
                app.set_model(model)
            self._model = model
            self._valid = True
            self._render_model(model)
            self.status_badge.setText("✓ 模型有效")
            self.status_badge.setProperty("badge", "success")
            self._polish_badge()
            self.error_label.hide()
            self.model_changed.emit()
            self.toast_requested.emit("模型验证通过")
            return True
        except (ModelError, NDMCError, ValueError, TypeError) as exc:
            self._valid = False
            self.status_badge.setText("模型无效")
            self.status_badge.setProperty("badge", "danger")
            self._polish_badge()
            self.error_label.setText(str(exc))
            self.error_label.show()
            self.toast_requested.emit(f"模型校验失败：{exc}")
            return False

    def _polish_badge(self):
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

    def _render_model(self, model: DynamicModel | None):
        self._clear_structure_layout(self.structure_layout)
        if model is None:
            return
        groups = (
            ("状态变量", model.states),
            ("输入", model.inputs),
            ("参数", model.parameters),
            ("输出", model.outputs),
        )
        for group, names in groups:
            self.structure_layout.addWidget(QLabel(group, objectName="Muted"))
            for name in names:
                row = QHBoxLayout()
                row.addWidget(QLabel(name))
                row.addStretch(1)
                row.addWidget(QLabel("已定义", objectName="Muted"))
                self.structure_layout.addLayout(row)

    @staticmethod
    def _clear_structure_layout(layout: QVBoxLayout) -> None:
        """Remove widgets and nested row layouts from a model preview."""

        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            if child_layout is not None:
                ModelPage._clear_structure_layout(child_layout)  # type: ignore[arg-type]
                child_layout.deleteLater()
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def on_project_changed(self) -> None:
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        if project.model is None:
            self._model = None
            self._valid = False
            self._render_model(None)
            self.code.clear()
            self.status_badge.setText("未定义")
            self.status_badge.setProperty("badge", "neutral")
            self._polish_badge()
            self.error_label.clear()
            self.error_label.hide()
            return
        self._model = project.model
        if project.model.builtin_key:
            source_index = self.source_combo.findData("builtin")
            if source_index >= 0 and self.source_combo.currentData() != "builtin":
                self.source_combo.blockSignals(True)
                self.source_combo.setCurrentIndex(source_index)
                self.source_combo.blockSignals(False)
            model_index = self.builtin_combo.findData(project.model.builtin_key)
            if model_index >= 0 and self.builtin_combo.currentIndex() != model_index:
                self.builtin_combo.blockSignals(True)
                self.builtin_combo.setCurrentIndex(model_index)
                self.builtin_combo.blockSignals(False)
            builtin = get_builtin_model(project.model.builtin_key)
            self.builtin_desc.setText(builtin.description if builtin else project.model.description)
        else:
            source_index = self.source_combo.findData("user")
            if source_index >= 0 and self.source_combo.currentData() != "user":
                self.source_combo.blockSignals(True)
                self.source_combo.setCurrentIndex(source_index)
                self.source_combo.blockSignals(False)
        self._on_source_changed()
        self._render_model(project.model)
        model = project.model
        text_lines = [
            "states:", *model.states, "",
            "inputs:", *model.inputs, "",
            "parameters:", *model.parameters, "",
            "equations:", *(f"d{state}/dt = {expr}" for state, expr in zip(model.states, model.rhs_exprs)), "",
            "outputs:", *model.outputs, "",
            "output equations:", *(f"{name} = {expr}" for name, expr in zip(model.outputs, model.output_exprs)),
        ]
        self.code.setPlainText("\n".join(text_lines))
        self.status_badge.setText("✓ 模型有效")
        self.status_badge.setProperty("badge", "success")
        self._polish_badge()


class _ProjectParameterModel(ParameterTableModel):
    """ParameterTableModel with the sixth, display-only unit column.

    The legacy Mock model exposed a ``rows`` list and string-formatted values;
    those conveniences are retained while the underlying values now remain
    real :class:`core.parameter.Parameter` instances.
    """

    HEADERS = ["参数", "初值", "下限", "上限", "状态", "单位"]

    def __init__(self, table: ParameterTable, units: dict[str, str] | None = None, parent=None):
        self.units = dict(units or {})
        self.decimals = 3
        super().__init__(table, parent)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def _format_number(self, value: float) -> str:
        return f"{float(value):.{self.decimals}f}"

    def set_decimals(self, decimals: int) -> None:
        self.decimals = max(0, min(12, int(decimals)))
        # Formatting is a presentation-only change.  ``dataChanged`` is
        # reserved for edits because ParametersPage treats it as a request to
        # persist the table, which would otherwise recurse during refresh.
        self.layoutChanged.emit()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        param = self._parameter_at(index.row())
        col = index.column()
        if col == 5:
            return self.units.get(param.name, "-") if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.ToolTipRole) else None
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.ToolTipRole):
            if col == 0:
                return param.name
            if col == 1:
                return self._format_number(param.initial)
            if col == 2:
                return self._format_number(param.lower)
            if col == 3:
                return self._format_number(param.upper)
            if col == 4:
                return "待辨识" if param.free else "固定"
        if role == Qt.ItemDataRole.ForegroundRole and col == 0:
            return QColor(t.TEXT_SECONDARY)
        if role == Qt.ItemDataRole.TextAlignmentRole and col > 0:
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        col = index.column()
        if col == 4:
            param = self._parameter_at(index.row())
            text = str(value)
            if text not in ("待辨识", "固定"):
                return False
            param.free = text == "待辨识"
            self.dataChanged.emit(index, index)
            self.validate_all()
            return True
        if col == 5 or col == 0:
            return False
        return super().setData(index, value, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() in (0, 5):
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    @property
    def rows(self) -> list[list[str]]:
        return [[
            p.name,
            self._format_number(p.initial),
            self._format_number(p.lower),
            self._format_number(p.upper),
            "待辨识" if p.free else "固定",
            self.units.get(p.name, "-"),
        ] for p in self._table]

    def append_row(self, row: Iterable[object]) -> int:
        values = list(row)
        name = str(values[0]) if values else "p"
        initial = _float_or_default(values[1] if len(values) > 1 else None, 1.0)
        lower = _float_or_default(values[2] if len(values) > 2 else None, 0.001)
        upper = _float_or_default(values[3] if len(values) > 3 else None, 10.0)
        free = str(values[4] if len(values) > 4 else "待辨识") != "固定"
        if len(values) > 5:
            self.units[name] = str(values[5])
        self.add_parameter(name)
        parameter = self._table.get(name)
        if parameter is not None:
            parameter.initial, parameter.lower, parameter.upper, parameter.free = initial, lower, upper, free
        self.layoutChanged.emit()
        return self.rowCount() - 1

    def remove_row(self, row: int) -> bool:
        if not 0 <= row < self.rowCount():
            return False
        name = self._parameter_at(row).name
        self._table.remove(name)
        self.units.pop(name, None)
        self.layoutChanged.emit()
        self.validate_all()
        return True

    def replace_rows(self, rows: Iterable[Iterable[object]]) -> None:
        table = ParameterTable()
        units: dict[str, str] = {}
        for row in rows:
            values = list(row)
            if not values:
                continue
            name = str(values[0])
            parameter = Parameter(
                name=name,
                initial=_float_or_default(values[1] if len(values) > 1 else None, 1.0),
                lower=_float_or_default(values[2] if len(values) > 2 else None, 0.001),
                upper=_float_or_default(values[3] if len(values) > 3 else None, 10.0),
                free=str(values[4] if len(values) > 4 else "待辨识") != "固定",
            )
            table.add(parameter)
            if len(values) > 5:
                units[name] = str(values[5])
        self.units = units
        self.set_parameters(table)


def _float_or_default(value: object, default: float) -> float:
    try:
        parsed = float(value)
        return parsed if np.isfinite(parsed) else default
    except (TypeError, ValueError):
        return default


def _mock_parameter_table() -> tuple[ParameterTable, dict[str, str]]:
    table = ParameterTable()
    units: dict[str, str] = {}
    for row in PARAMETERS:
        name = str(row[0])
        table.add(Parameter(name=name, initial=_float_or_default(row[1], 1.0), lower=_float_or_default(row[2], 0.001), upper=_float_or_default(row[3], 10.0), free=str(row[4]) != "固定"))
        if len(row) > 5:
            units[name] = str(row[5])
    return table, units


class ParametersPage(BasePage):
    def __init__(self):
        super().__init__()
        validate = button("验证参数", "secondary", "check")
        validate.clicked.connect(self.validate_parameters)
        self.validate_button = validate
        self.add_header("参数配置", "设置参数初值、搜索边界和参数状态。", validate)
        toolbar = QHBoxLayout()
        self.add_button = button("添加", "secondary", "plus")
        self.delete_button = button("删除", "secondary", "trash")
        self.reset_button = button("重置", "secondary", "reset")
        self.delete_button.setEnabled(False)
        self.add_button.clicked.connect(self.add_parameter)
        self.delete_button.clicked.connect(self.remove_selected)
        self.reset_button.clicked.connect(self.reset_parameters)
        toolbar.addWidget(self.add_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addWidget(self.reset_button)
        toolbar.addStretch(1)
        self.root.addLayout(toolbar)

        table, units = _mock_parameter_table()
        self.model = _ProjectParameterModel(table, units, self)
        self.table = table_view(self.model, 38, [100, 110, 110, 110, 130, 100])
        self.table.setFixedHeight(164)
        for column in (1, 2, 3):
            self.table.setItemDelegateForColumn(column, DoubleSpinBoxDelegate(parent=self.table))
        self.table.setItemDelegateForColumn(4, ComboBoxDelegate(["待辨识", "固定"], self.table))
        self.table.selectionModel().selectionChanged.connect(self._selection_changed)
        self.model.dataChanged.connect(self._parameters_changed)
        self.model.error_changed.connect(lambda *_: None)
        self.root.addWidget(self.table)
        self.validation_panel = QFrame(objectName="Card")
        self.validation_panel.setMaximumHeight(42)
        valid_layout = QHBoxLayout(self.validation_panel)
        valid_layout.setContentsMargins(12, 8, 12, 8)
        self.validation_badge = badge("✓ 参数配置有效", "success")
        valid_layout.addWidget(self.validation_badge)
        valid_layout.addStretch(1)
        self.root.addWidget(self.validation_panel)
        self.root.addStretch(1)

    def set_decimal_places(self, decimals: int) -> None:
        self.model.set_decimals(decimals)
        self.table.resizeRowsToContents()

    def _selection_changed(self, *_):
        self.delete_button.setEnabled(bool(self.table.selectionModel().selectedRows()))

    def _parameters_changed(self, *_args):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is not None:
            # Route edits through the application facade so every analysis
            # artifact derived from the previous parameter table is removed.
            if hasattr(app, "set_parameter_table"):
                app.set_parameter_table(self.model.table())
            else:
                project.parameters = self.model.table()
                project.mark_dirty()
            refresh = getattr(self.window(), "_after_project_change", None)
            if callable(refresh):
                refresh()

    def _set_project_table(self, table: ParameterTable, units: dict[str, str] | None = None):
        self.model.units = dict(units or self.model.units)
        self.model.set_parameters(table)
        self.table.clearSelection()
        self.delete_button.setEnabled(False)
        self.validate_parameters(emit_toast=False)

    def add_parameter(self):
        existing = set(self.model.table().names)
        suffix = 1
        while f"p{suffix}" in existing:
            suffix += 1
        name = f"p{suffix}"
        row = self.model.append_row([name, "1.000", "0.000", "10.000", "待辨识", "-"])
        self._parameters_changed()
        self.table.selectRow(row)
        self.toast_requested.emit(f"已添加参数 {name}")

    def remove_selected(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return
        row = selected[0].row()
        name = str(self.model.data(self.model.index(row, 0)))
        if not ConfirmDialog.ask(self, "删除参数", f"确认删除参数 {name}？", "删除", True):
            return
        self.model.remove_row(row)
        self._parameters_changed()
        self.delete_button.setEnabled(False)
        self.toast_requested.emit(f"已删除参数 {name}")

    def _default_table_from_model(self, model: DynamicModel | None) -> tuple[ParameterTable, dict[str, str]]:
        if model is None:
            return _mock_parameter_table()
        table = ParameterTable()
        units: dict[str, str] = {}
        builtin = None
        app = _window_app(self)
        if app is not None:
            model_page = getattr(getattr(self.window(), "pages", {}), "get", lambda *_: None)("model")
            key = model_page.builtin_combo.currentData() if model_page is not None and hasattr(model_page, "builtin_combo") else None
            builtin = get_builtin_model(key) if key else None
        for name in model.parameters:
            defaults = builtin.parameter_defaults.get(name, {}) if builtin is not None else {}
            table.add(Parameter(name=name, initial=float(defaults.get("initial", 1.0)), lower=float(defaults.get("lower", 0.001)), upper=float(defaults.get("upper", 10.0)), free=bool(defaults.get("free", True))))
        return table, units

    def reset_parameters(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        model = getattr(project, "model", None) if project is not None else None
        table, units = self._default_table_from_model(model)
        self._set_project_table(table, units)
        self._parameters_changed()
        self.toast_requested.emit("参数配置已重置")

    def validate_parameters(self, emit_toast: bool = True):
        errors = []
        for row, parameter in enumerate(self.model.table()):
            if not parameter.free:
                continue
            try:
                parameter.validate()
            except (ValueError, TypeError, OverflowError):
                errors.append(row)
        if errors:
            self.validation_badge.setText("参数边界无效")
            self.validation_badge.setProperty("badge", "danger")
            message = "参数配置无效，请检查初值和边界"
        else:
            self.validation_badge.setText("✓ 参数配置有效")
            self.validation_badge.setProperty("badge", "success")
            message = "参数配置有效"
        self.validation_badge.style().unpolish(self.validation_badge)
        self.validation_badge.style().polish(self.validation_badge)
        if emit_toast:
            self.toast_requested.emit(message)
        return not errors

    def on_project_changed(self) -> None:
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        settings = getattr(self.window(), "_settings", None)
        if settings is not None:
            try:
                self.set_decimal_places(int(settings.value("decimals", 3)))
            except (TypeError, ValueError):
                self.set_decimal_places(3)
        self._set_project_table(project.parameters)


class IdentificationPage(BasePage):
    def __init__(self):
        super().__init__()
        self.run_state = "ready"
        self.timer = QTimer(self)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self._tick)
        self.step = 0
        self.action = button("开始辨识", "primary", "play")
        self.action.clicked.connect(self.toggle_run)
        self.add_header("参数辨识", "选择求解算法并运行模型参数估计。", self.action)

        body = QHBoxLayout()
        body.setSpacing(20)
        left = QVBoxLayout()
        algo_card = Card()
        algo_card.layout().addWidget(section_title("算法选择"))
        algo_grid = QGridLayout()
        algorithms = [
            ("least_squares", "最小二乘", "TRF / Dogbox"),
            ("nelder_mead", "Nelder-Mead", "无梯度局部搜索"),
            ("differential_evolution", "差分进化", "全局搜索"),
            ("multistart", "多起点", "多起点局部搜索"),
        ]
        self.algo_buttons = []
        for i, (key, name, detail) in enumerate(algorithms):
            choice = QPushButton(f"{name}\n{detail}")
            choice.setProperty("algo", True)
            choice.setProperty("algorithm_key", key)
            choice.setCheckable(True)
            choice.setChecked(i == 0)
            choice.clicked.connect(partial(self._select_algo, choice))
            algo_grid.addWidget(choice, i // 2, i % 2)
            self.algo_buttons.append(choice)
        algo_card.layout().addLayout(algo_grid)
        left.addWidget(algo_card)
        settings = Card()
        settings.layout().addWidget(section_title("算法设置"))
        form = QFormLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItem("TRF", "trf")
        self.method_combo.addItem("Dogbox", "dogbox")
        form.addRow(QLabel("方法", objectName="BodySecondary"), self.method_combo)
        self.max_iterations_spin = QSpinBox()
        self.max_iterations_spin.setRange(1, 100000)
        self.max_iterations_spin.setValue(2000)
        form.addRow(QLabel("最大迭代次数", objectName="BodySecondary"), self.max_iterations_spin)
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setDecimals(10)
        self.tolerance_spin.setRange(1e-12, 1.0)
        self.tolerance_spin.setValue(1e-8)
        self.tolerance_spin.setSingleStep(1e-8)
        form.addRow(QLabel("容差", objectName="BodySecondary"), self.tolerance_spin)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2**31 - 1)
        self.seed_spin.setValue(42)
        self.seed_spin.setSpecialValueText("随机")
        form.addRow(QLabel("随机种子", objectName="BodySecondary"), self.seed_spin)
        settings.layout().addLayout(form)
        self.advanced_toggle = button("高级设置", "secondary")
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.clicked.connect(self.toggle_advanced)
        settings.layout().addWidget(self.advanced_toggle)
        self.advanced_panel = QWidget()
        advanced_form = QFormLayout(self.advanced_panel)
        advanced_form.setContentsMargins(0, 4, 0, 0)
        self.rtol_spin = QDoubleSpinBox()
        self.rtol_spin.setDecimals(10); self.rtol_spin.setRange(1e-12, 1.0); self.rtol_spin.setValue(1e-6)
        self.atol_spin = QDoubleSpinBox()
        self.atol_spin.setDecimals(10); self.atol_spin.setRange(1e-12, 1.0); self.atol_spin.setValue(1e-9)
        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItem("线性", "linear")
        self.interpolation_combo.addItem("零阶保持", "zero_order_hold")
        advanced_form.addRow(QLabel("rtol", objectName="Muted"), self.rtol_spin)
        advanced_form.addRow(QLabel("atol", objectName="Muted"), self.atol_spin)
        advanced_form.addRow(QLabel("输入插值", objectName="Muted"), self.interpolation_combo)
        self.advanced_panel.hide()
        settings.layout().addWidget(self.advanced_panel)
        left.addWidget(settings)
        left.addStretch(1)
        body.addLayout(left, 2)

        right = QVBoxLayout()
        status = Card()
        status_head = QHBoxLayout()
        status_head.addWidget(section_title("运行状态"))
        status_head.addStretch(1)
        self.status_badge = badge("就绪", "neutral")
        status_head.addWidget(self.status_badge)
        status.layout().addLayout(status_head)
        metric_row = QHBoxLayout()
        self.eval_card = MetricCard("评估次数", "0 / 2,000")
        self.obj_card = MetricCard("最佳目标函数", "0.2480")
        self.time_card = MetricCard("运行时间", "0.00 s")
        for card in (self.eval_card, self.obj_card, self.time_card):
            card.setStyleSheet("border:0;")
            metric_row.addWidget(card, 1)
        status.layout().addLayout(metric_row)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()
        status.layout().addWidget(self.progress)
        right.addWidget(status)

        convergence = Card()
        convergence.layout().addWidget(section_title("目标函数与评估次数"))
        self.plot = EngineeringPlot("评估次数", "目标函数", 220)
        self.plot.setMaximumHeight(292)
        self.plot.plot.setLogMode(y=True)
        convergence.layout().addWidget(self.plot)
        right.addWidget(convergence)
        self.result = Card()
        result_row = QHBoxLayout()
        result_row.addWidget(badge("✓ 已完成", "success"))
        result_row.addWidget(QLabel("最佳参数:  k = 2.514   c = 0.176"))
        result_row.addStretch(1)
        self.result.layout().addLayout(result_row)
        self.result.hide()
        right.addWidget(self.result)
        right.addStretch(1)
        body.addLayout(right, 3)
        self.root.addLayout(body, 1)

    def _select_algo(self, selected):
        for choice in self.algo_buttons:
            choice.setChecked(choice is selected)

    def current_algorithm(self) -> str:
        for choice in self.algo_buttons:
            if choice.isChecked():
                return str(choice.property("algorithm_key") or "least_squares")
        return "least_squares"

    def _collect_real_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {
            "seed": None if self.seed_spin.value() == 0 else self.seed_spin.value(),
            "max_iterations": self.max_iterations_spin.value(),
            "tolerance": self.tolerance_spin.value(),
            "rtol": self.rtol_spin.value(),
            "atol": self.atol_spin.value(),
            "input_interpolation": self.interpolation_combo.currentData(),
        }
        if self.current_algorithm() == "least_squares":
            options["method"] = self.method_combo.currentData()
        elif self.current_algorithm() == "differential_evolution":
            options.update({"population": 15, "mutation": (0.5, 1.0), "recombination": 0.7, "tolerance": self.tolerance_spin.value()})
        elif self.current_algorithm() == "multistart":
            options["n_starts"] = 10
        return options

    def toggle_advanced(self, checked: bool):
        self.advanced_panel.setVisible(checked)
        self.advanced_toggle.setText("收起高级设置" if checked else "高级设置")

    def toggle_run(self):
        if self.run_state == "running":
            app = _window_app(self)
            if app is not None and getattr(app, "project", None) is not None:
                window = self.window()
                cancel = getattr(window, "cancel_worker", None)
                if cancel:
                    cancel()
            else:
                self.cancel_mock()
        else:
            app = _window_app(self)
            project = getattr(app, "project", None) if app is not None else None
            if project is not None and project.model is not None and project.experiment is not None:
                self.start_real()
            else:
                self.start_mock()

    def start_real(self):
        window = self.window()
        try:
            worker = window.run_identification_async(self.current_algorithm(), self._collect_real_options())
        except Exception as exc:
            self.on_identification_error(str(exc))
            return False
        self._real_worker = worker
        self.run_state = "running"
        self.result.hide()
        self.progress.setRange(0, 0)
        self.progress.show()
        self.action.setText("取消辨识")
        self.action.setProperty("variant", "danger")
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)
        self.status_badge.setText("运行中")
        self.status_badge.setProperty("badge", "info")
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.toast_requested.emit("已开始参数辨识")
        return True

    def on_identification_done(self, result: dict[str, Any] | None = None, emit: bool = True):
        self._real_worker = None
        self.run_state = "completed"
        self.progress.hide()
        self.status_badge.setText("已完成")
        self.status_badge.setProperty("badge", "success")
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.action.setText("开始辨识")
        self.action.setProperty("variant", "primary")
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)
        if result:
            objective = result.get("objective_value", result.get("objective", 0.0))
            evaluations = result.get("n_evaluations", result.get("nfev", 0))
            runtime = result.get("runtime_seconds", 0.0)
            self.eval_card.set_value(f"{evaluations:,}")
            self.obj_card.set_value(f"{float(objective):.6g}")
            self.time_card.set_value(f"{float(runtime):.2f} s")
            params = result.get("parameters", {})
            label = "最佳参数: " + "   ".join(f"{name} = {float(value):.6g}" for name, value in params.items())
            self.result.layout().itemAt(1).widget().setText(label) if self.result.layout().count() > 1 else None
        self.result.show()
        if emit:
            self.toast_requested.emit("参数辨识已完成")

    def on_identification_error(self, message: str):
        self._real_worker = None
        if "取消" in str(message):
            self.run_state = "cancelled"
            text, prop = "已取消", "warning"
        else:
            self.run_state = "error"
            text, prop = "运行失败", "danger"
        self.progress.hide()
        self.status_badge.setText(text)
        self.status_badge.setProperty("badge", prop)
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.action.setText("开始辨识")
        self.action.setProperty("variant", "primary")
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)
        if text == "运行失败":
            self.toast_requested.emit(f"参数辨识运行失败：{message}")

    def start_mock(self):
        self.run_state = "running"
        self.step = 0
        self.result.hide()
        self.plot.clear()
        self.progress.setValue(0)
        self.progress.show()
        self.action.setText("取消辨识")
        self.action.setProperty("variant", "danger")
        self.action.setIcon(self.action.icon())
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)
        self.status_badge.setText("运行中")
        self.status_badge.setProperty("badge", "info")
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.timer.start()

    def _tick(self):
        self.step += 1
        count = min(len(CONVERGENCE), self.step)
        values = CONVERGENCE[:count]
        self.plot.clear()
        self.plot.line([p[0] for p in values], [p[1] for p in values], t.ACCENT)
        evaluation, objective = values[-1]
        self.eval_card.set_value(f"{evaluation} / 2,000")
        self.obj_card.set_value(f"{objective:.4f}")
        self.time_card.set_value(f"{1.72 * count / len(CONVERGENCE):.2f} s")
        self.progress.setValue(int(100 * count / len(CONVERGENCE)))
        if count == len(CONVERGENCE):
            self.complete_mock()

    def complete_mock(self):
        self.timer.stop()
        self.run_state = "completed"
        self.plot.clear()
        self.plot.line([p[0] for p in CONVERGENCE], [p[1] for p in CONVERGENCE], t.ACCENT)
        self.eval_card.set_value("318 / 2,000")
        self.obj_card.set_value("0.0031")
        self.time_card.set_value("1.72 s")
        self.progress.hide()
        self.status_badge.setText("已完成")
        self.status_badge.setProperty("badge", "success")
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.action.setText("开始辨识")
        self.action.setProperty("variant", "primary")
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)
        self.result.show()
        self.toast_requested.emit("参数辨识已完成")

    def show_running_snapshot(self, steps: int = 3):
        self.start_mock()
        self.timer.stop()
        for _ in range(max(1, min(steps, len(CONVERGENCE) - 1))):
            self._tick()

    def cancel_mock(self):
        self.timer.stop()
        self.run_state = "cancelled"
        self.progress.hide()
        self.status_badge.setText("已取消")
        self.status_badge.setProperty("badge", "warning")
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.action.setText("开始辨识")
        self.action.setProperty("variant", "primary")
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)

    def error_mock(self):
        self.timer.stop()
        self.run_state = "error"
        self.progress.hide()
        self.status_badge.setText("运行失败")
        self.status_badge.setProperty("badge", "danger")
        self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)
        self.action.setText("开始辨识")
        self.action.setProperty("variant", "primary")
        self.action.style().unpolish(self.action); self.action.style().polish(self.action)
        self.toast_requested.emit("参数辨识运行失败")

    def on_project_changed(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        entry = project.results.get("identification", {})
        result = entry.get("result", {}) if isinstance(entry, dict) else {}
        if result and self.run_state not in ("cancelled", "error"):
            self.on_identification_done(result, emit=False)
        elif self.run_state not in ("running", "cancelled", "error"):
            # A new project has no fit yet; clear the reference project's
            # values instead of presenting them as current results.
            self.run_state = "ready"
            self.progress.hide()
            self.result.hide()
            self.plot.clear()
            self.eval_card.set_value("0")
            self.obj_card.set_value("—")
            self.time_card.set_value("—")
            self.status_badge.setText("就绪")
            self.status_badge.setProperty("badge", "neutral")
            self.status_badge.style().unpolish(self.status_badge); self.status_badge.style().polish(self.status_badge)

    on_result_changed = on_project_changed


class CalibrationPage(BasePage):
    def __init__(self):
        super().__init__()
        self.add_header("模型校准", "比较实验观测与当前辨识模型的拟合结果。")
        metrics = QHBoxLayout()
        self.metric_cards = {}
        for label, value in (("RMSE", "0.0418"), ("MAE", "0.0312"), ("R²", "0.9871"), ("运行时间", "3.21 s")):
            card = MetricCard(label, value)
            self.metric_cards[label] = card
            metrics.addWidget(card, 1)
        self.root.addLayout(metrics)
        plot_card = Card()
        plot_toolbar = QHBoxLayout()
        plot_toolbar.addWidget(section_title("实测 vs 模拟"))
        plot_toolbar.addStretch(1)
        reset_view = button("", "secondary", "reset")
        reset_view.setFixedSize(34, 34)
        reset_view.setToolTip("复位图表视图")
        reset_view.setAccessibleName("复位图表视图")
        plot_toolbar.addWidget(reset_view)
        plot_card.layout().addLayout(plot_toolbar)
        plot = EngineeringPlot("时间 (s)", "position (m)", 380)
        self.calibration_plot = plot
        xs = [r[0] for r in TIME_SERIES]
        plot.line(xs, [r[1] for r in TIME_SERIES], t.ACCENT, "实测值")
        plot.line(xs, [r[2] for r in TIME_SERIES], t.CHART_SIMULATED, "模拟值", 2)
        plot.set_default_x_range(0, 50)
        reset_view.clicked.connect(plot.reset_view)
        plot_card.layout().addWidget(plot)
        self.root.addWidget(plot_card, 1)
        self.root.addWidget(section_title("参数结果"))
        self.result_model = SimpleTableModel(
            ["参数", "估计值", "初值", "变化"],
            [["k", "2.514", "2.000", "+25.7%"], ["c", "0.176", "0.200", "-12.0%"], ["m", "1.000", "1.000", "固定"]],
        )
        result_table = table_view(
            self.result_model,
            34,
            [120, 145, 145, 150],
        )
        self.result_table = result_table
        result_table.setMaximumHeight(140)
        self.root.addWidget(result_table)

    @staticmethod
    def _number(value: object, default: str = "—") -> str:
        try:
            value = float(value)
            return f"{value:.6g}" if np.isfinite(value) else default
        except (TypeError, ValueError):
            return default

    def on_project_changed(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        cal = project.results.get("calibration", {})
        summary = cal.get("metrics", {}).get("summary", {}) if isinstance(cal, dict) else {}
        ident = project.results.get("identification", {}).get("result", {})
        self.metric_cards["RMSE"].set_value(self._number(summary.get("RMSE")))
        self.metric_cards["MAE"].set_value(self._number(summary.get("MAE")))
        self.metric_cards["R²"].set_value(self._number(summary.get("R2")))
        self.metric_cards["运行时间"].set_value(f"{float(ident.get('runtime_seconds', 0.0) or 0.0):.2f} s" if ident else "—")

        if project.experiment is not None:
            self.calibration_plot.clear()
            x = np.asarray(project.experiment.time, dtype=float)
            predicted = cal.get("predicted", {}) if isinstance(cal, dict) else {}
            if not predicted:
                try:
                    from .backend import current_prediction

                    predicted = current_prediction(project)
                except Exception:
                    predicted = {}
            for name, measured in project.experiment.outputs.items():
                self.calibration_plot.line(x, np.asarray(measured, dtype=float), t.ACCENT, f"实测 · {name}")
                values = predicted.get(name) if isinstance(predicted, dict) else None
                if values is not None:
                    self.calibration_plot.line(x, np.asarray(values, dtype=float), t.CHART_SIMULATED, f"模拟 · {name}", 2)
            if x.size:
                self.calibration_plot.set_default_x_range(float(x[0]), float(x[-1]))
        else:
            self.calibration_plot.clear()

        params = project.parameters
        estimates = ident.get("parameters", {}) if isinstance(ident, dict) else {}
        rows = []
        for parameter in params:
            if parameter.name in estimates:
                estimate = float(estimates[parameter.name])
                delta = "—" if parameter.initial == 0 else f"{(estimate - parameter.initial) / abs(parameter.initial) * 100:+.3g}%"
            else:
                estimate = parameter.initial
                delta = "固定" if not parameter.free else "—"
            rows.append([parameter.name, self._number(estimate), self._number(parameter.initial), delta])
        self.result_model.replace_rows(rows)

    on_result_changed = on_project_changed


class DiagnosticsPage(BasePage):
    def __init__(self):
        super().__init__()
        self.add_header("诊断分析", "残差分析、参数敏感度与可辨识性诊断。")
        self.tabs = QTabWidget()
        self.tabs.addTab(self._residuals(), "残差")
        self.tabs.addTab(self._sensitivity(), "敏感度")
        self.tabs.addTab(self._identifiability(), "可辨识性")
        self.tabs.addTab(self._correlation(), "相关性")
        self.tabs.tabBar().setUsesScrollButtons(True)
        self.tabs.tabBar().setElideMode(Qt.TextElideMode.ElideNone)
        self.root.addWidget(self.tabs, 1)

    def _residuals(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 16, 0, 0); layout.setSpacing(18)
        metrics = QHBoxLayout()
        self.residual_metric_cards = {}
        for label, value in (("均值", "0.0012"), ("标准差", "0.0417"), ("最大绝对值", "0.129"), ("ACF 峰值", "0.087")):
            card = MetricCard(label, value)
            self.residual_metric_cards[label] = card
            metrics.addWidget(card, 1)
        layout.addLayout(metrics)
        line_card = Card(); line_card.layout().addWidget(section_title("残差时间序列"))
        plot = EngineeringPlot("时间 (s)", "残差", 205)
        self.residual_plot = plot
        plot.line([r[0] for r in RESIDUALS], [r[1] for r in RESIDUALS], t.CHART_RESIDUAL)
        line_card.layout().addWidget(plot); layout.addWidget(line_card)
        hist_card = Card(); hist_card.layout().addWidget(section_title("残差分布"))
        hist = EngineeringPlot("残差", "频数", 180)
        self.residual_histogram = hist
        hist.bars([r[0] for r in HISTOGRAM], [r[1] for r in HISTOGRAM], t.BORDER_STRONG, .025)
        hist_card.layout().addWidget(hist); layout.addWidget(hist_card)
        return page

    def _sensitivity(self):
        page = QWidget(); layout = QHBoxLayout(page); layout.setContentsMargins(0, 16, 0, 0)
        plot_card = Card(); plot_card.layout().addWidget(section_title("归一化敏感度"))
        plot = EngineeringPlot("RMS 敏感度", "", 260)
        self.sensitivity_plot = plot
        plot.horizontal_bars([1, 2], [2.31, 1.14], t.TEXT_SECONDARY, .55)
        plot.plot.getAxis("left").setTicks([[(1, "k"), (2, "c")]])
        plot.plot.setXRange(0, 2.6, padding=0)
        plot_card.layout().addWidget(plot); layout.addWidget(plot_card, 1)
        self.sensitivity_model = SimpleTableModel(["参数", "敏感度", "排名"], [["k", "2.31", "1"], ["c", "1.14", "2"]])
        self.sensitivity_table = table_view(self.sensitivity_model, 36, [100, 120, 100])
        layout.addWidget(self.sensitivity_table, 1)
        return page

    def _identifiability(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 16, 0, 0)
        row = QHBoxLayout()
        self.ident_metric_cards = {}
        for label, value, sub in (("条件数", "31.7", ""), ("秩", "2 / 2", "良好"), ("最小奇异值", "0.184", "")):
            card = MetricCard(label, value, sub)
            self.ident_metric_cards[label] = card
            row.addWidget(card, 1)
        layout.addLayout(row)
        card = Card(); card.layout().addWidget(section_title("奇异值"))
        plot = EngineeringPlot("索引", "奇异值", 230); plot.bars([1, 2], [5.84, .184], t.ACCENT, .55)
        self.singular_plot = plot
        card.layout().addWidget(plot); layout.addWidget(card)
        self.ident_badge = badge("良好 · 当前示例未检测到明显的局部可辨识性问题。", "success")
        self.ident_badge.setWordWrap(True)
        layout.addWidget(self.ident_badge, 0, Qt.AlignmentFlag.AlignLeft)
        return page

    def _correlation(self):
        page = QWidget(); layout = QHBoxLayout(page); layout.setContentsMargins(0, 16, 0, 0)
        card = Card(); card.layout().addWidget(section_title("参数相关性"))
        grid = QGridLayout()
        self.correlation_grid = grid
        values = [[1.0, .73], [.73, 1.0]]
        for idx, name in enumerate(("k", "c")):
            grid.addWidget(QLabel(name), 0, idx + 1, Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(QLabel(name), idx + 1, 0, Qt.AlignmentFlag.AlignCenter)
        for i in range(2):
            for j in range(2):
                cell = QLabel(f"{values[i][j]:.2f}")
                cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setFixedSize(82, 62)
                cell.setStyleSheet(f"background:{t.ACCENT_SUBTLE if i == j else t.SURFACE_HOVER}; color:{t.ACCENT if i == j else t.TEXT_PRIMARY}; border-radius:6px;")
                grid.addWidget(cell, i + 1, j + 1)
        card.layout().addLayout(grid); card.layout().addStretch(1); layout.addWidget(card, 1)
        high = Card(); high.layout().addWidget(section_title("最高参数相关性")); self.high_corr_pair = QLabel("k ↔ c", objectName="BodySecondary"); self.high_corr_value = QLabel("0.73", objectName="MetricValue"); high.layout().addWidget(self.high_corr_pair); high.layout().addWidget(self.high_corr_value); high.layout().addStretch(1); layout.addWidget(high, 1)
        return page

    @staticmethod
    def _finite_values(values):
        try:
            return np.asarray(values, dtype=float)
        except (TypeError, ValueError):
            return np.asarray([], dtype=float)

    def on_project_changed(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        cal = project.results.get("calibration", {})
        if not isinstance(cal, dict):
            return
        if not cal:
            for label in self.residual_metric_cards:
                self.residual_metric_cards[label].set_value("—")
            self.residual_plot.clear()
            self.residual_histogram.clear()
            self.sensitivity_plot.clear()
            self.sensitivity_model.replace_rows([])
            self.ident_metric_cards["条件数"].set_value("—")
            self.ident_metric_cards["秩"].set_value("—")
            self.ident_metric_cards["最小奇异值"].set_value("—")
            self.singular_plot.clear()
            self.ident_badge.setText("暂无校准结果，请先运行参数辨识。")
            self.ident_badge.setProperty("badge", "neutral")
            self.ident_badge.style().unpolish(self.ident_badge); self.ident_badge.style().polish(self.ident_badge)
            while self.correlation_grid.count():
                item = self.correlation_grid.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.high_corr_pair.setText("暂无")
            self.high_corr_value.setText("—")
            return
        outputs = list(cal.get("residuals", {}).keys())
        output = outputs[0] if outputs else (project.model.outputs[0] if project.model and project.model.outputs else None)
        residuals = self._finite_values(cal.get("residuals", {}).get(output, [])) if output else np.asarray([])
        stats = cal.get("residual_stats", {}).get(output, {}) if output else {}
        diagnosis = cal.get("residual_diagnosis", {}).get(output, {}) if output else {}
        if residuals.size:
            mean = stats.get("mean", float(np.mean(residuals)))
            std = stats.get("std", float(np.std(residuals)))
            maximum = max(abs(float(stats.get("min", np.min(residuals)))), abs(float(stats.get("max", np.max(residuals)))))
            acf = np.asarray(diagnosis.get("acf", []), dtype=float)
            acf_peak = float(np.max(np.abs(acf))) if acf.size else 0.0
            for label, value in (("均值", mean), ("标准差", std), ("最大绝对值", maximum), ("ACF 峰值", acf_peak)):
                self.residual_metric_cards[label].set_value(f"{float(value):.6g}")
            self.residual_plot.clear()
            time_values = np.asarray(project.experiment.time, dtype=float) if project.experiment is not None else np.arange(residuals.size)
            if time_values.size == residuals.size:
                self.residual_plot.line(time_values, residuals, t.CHART_RESIDUAL, output or "残差")
            self.residual_histogram.clear()
            hist, edges = np.histogram(residuals, bins=min(20, max(5, int(np.sqrt(residuals.size)))))
            centers = (edges[:-1] + edges[1:]) / 2
            width = float(np.diff(edges).mean() * .8) if len(edges) > 1 else .025
            self.residual_histogram.bars(centers, hist, t.BORDER_STRONG, width)

        sensitivity = cal.get("sensitivity", {}).get("summary", {})
        if sensitivity:
            ordered = sorted(sensitivity.items(), key=lambda item: float(item[1].get("rms", 0.0)), reverse=True)
            self.sensitivity_plot.clear()
            y = list(range(1, len(ordered) + 1))
            vals = [float(item[1].get("rms", 0.0)) for item in ordered]
            self.sensitivity_plot.horizontal_bars(y, vals, t.TEXT_SECONDARY, .55)
            self.sensitivity_plot.plot.getAxis("left").setTicks([[(idx, name) for idx, (name, _) in zip(y, ordered)]])
            self.sensitivity_plot.plot.setXRange(0, max(vals + [1.0]) * 1.15, padding=0)
            self.sensitivity_model.replace_rows([[name, f"{float(info.get('rms', 0.0)):.6g}", str(rank + 1)] for rank, (name, info) in enumerate(ordered)])

        ident = cal.get("identifiability", {})
        if ident:
            singular = self._finite_values(ident.get("singular_values", []))
            cond = ident.get("condition_number")
            rank = ident.get("rank")
            n_params = ident.get("n_parameters", len(singular))
            minimum = float(np.min(singular)) if singular.size else float("nan")
            self.ident_metric_cards["条件数"].set_value(f"{float(cond):.6g}" if cond is not None and np.isfinite(cond) else "∞")
            self.ident_metric_cards["秩"].set_value(f"{rank} / {n_params}")
            self.ident_metric_cards["最小奇异值"].set_value(f"{minimum:.6g}" if np.isfinite(minimum) else "—")
            self.singular_plot.clear()
            if singular.size:
                self.singular_plot.bars(list(range(1, singular.size + 1)), singular, t.ACCENT, .55)
            warnings = ident.get("warnings", []) or []
            self.ident_badge.setText(("；".join(str(item) for item in warnings[:2])) if warnings else "良好 · 未检测到明显的局部可辨识性问题。")
            self.ident_badge.setProperty("badge", "warning" if warnings else "success")
            self.ident_badge.style().unpolish(self.ident_badge); self.ident_badge.style().polish(self.ident_badge)

            corr = ident.get("correlation")
            names = ident.get("parameter_names", [])
            if corr is not None and names:
                while self.correlation_grid.count():
                    item = self.correlation_grid.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                matrix = np.asarray(corr, dtype=float)
                for idx, name in enumerate(names):
                    self.correlation_grid.addWidget(QLabel(str(name)), 0, idx + 1, Qt.AlignmentFlag.AlignCenter)
                    self.correlation_grid.addWidget(QLabel(str(name)), idx + 1, 0, Qt.AlignmentFlag.AlignCenter)
                highest = (None, None, 0.0)
                for i in range(min(len(names), matrix.shape[0])):
                    for j in range(min(len(names), matrix.shape[1])):
                        value = float(matrix[i, j])
                        cell = QLabel(f"{value:.2f}")
                        cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        cell.setFixedSize(82, 62)
                        cell.setStyleSheet(f"background:{t.ACCENT_SUBTLE if i == j else t.SURFACE_HOVER}; color:{t.ACCENT if i == j else t.TEXT_PRIMARY}; border-radius:6px;")
                        self.correlation_grid.addWidget(cell, i + 1, j + 1)
                        if i < j and abs(value) > abs(highest[2]):
                            highest = (names[i], names[j], value)
                if highest[0] is not None:
                    self.high_corr_pair.setText(f"{highest[0]} ↔ {highest[1]}")
                    self.high_corr_value.setText(f"{highest[2]:.4g}")

    on_result_changed = on_project_changed


class UncertaintyPage(BasePage):
    def __init__(self):
        super().__init__()
        self.add_header("可信度分析", "多起点稳定性与 Bootstrap 参数可信度区间。")
        tabs = QTabWidget()
        tabs.addTab(self._multi(), "多起点分析")
        tabs.addTab(self._bootstrap(), "Bootstrap")
        tabs.tabBar().setUsesScrollButtons(True)
        tabs.tabBar().setElideMode(Qt.TextElideMode.ElideNone)
        tabs.setCurrentIndex(0)
        self.tabs = tabs
        self.root.addWidget(tabs, 1)

    def _multi(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 16, 0, 0)
        row = QHBoxLayout()
        self.multi_cards = {}
        for label, value in (("起点数", "20"), ("成功次数", "20"), ("成功率", "100%"), ("最佳 RMSE", "0.0418")):
            card = MetricCard(label, value)
            self.multi_cards[label] = card
            row.addWidget(card, 1)
        layout.addLayout(row)
        self.multi_model = SimpleTableModel(["起点", "k", "c"], [[i + 1, f"{2.48 + (i % 5) * .01:.3f}", f"{.17 + (i % 4) * .003:.3f}"] for i in range(10)])
        self.multi_table = table_view(self.multi_model, 30, [105, 115, 115])
        layout.addWidget(self.multi_table)
        self.multi_run_button = button("运行多起点", "secondary", "play")
        self.multi_run_button.clicked.connect(self.run_stability)
        layout.addWidget(self.multi_run_button, 0, Qt.AlignmentFlag.AlignLeft)
        return page

    def _bootstrap(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(0, 16, 0, 0); layout.setSpacing(16)
        row = QHBoxLayout()
        self.bootstrap_cards = {}
        for label, value in (("Bootstrap 样本数", "100"), ("随机种子", "42"), ("状态", "已完成")):
            card = MetricCard(label, value)
            self.bootstrap_cards[label] = card
            row.addWidget(card, 1)
        row.addStretch(1); layout.addLayout(row)
        self.bootstrap_model = SimpleTableModel(["参数", "估计值", "中位数", "P2.5", "P97.5"], BOOTSTRAP)
        table = table_view(self.bootstrap_model, 34, [100, 115, 115, 115, 115])
        self.bootstrap_table = table
        table.setMaximumHeight(150); layout.addWidget(table)
        select_row = QHBoxLayout(); select_row.addWidget(QLabel("参数:", objectName="BodySecondary")); select = QComboBox(); select.addItems(["k", "c"]); self.bootstrap_parameter = select; select.currentTextChanged.connect(self._update_bootstrap_plot); select_row.addWidget(select)
        self.bootstrap_b_spin = QSpinBox(); self.bootstrap_b_spin.setRange(1, 1000); self.bootstrap_b_spin.setValue(100); self.bootstrap_b_spin.setPrefix("B="); select_row.addWidget(self.bootstrap_b_spin)
        self.bootstrap_seed_spin = QSpinBox(); self.bootstrap_seed_spin.setRange(0, 2**31 - 1); self.bootstrap_seed_spin.setValue(42); self.bootstrap_seed_spin.setPrefix("seed="); select_row.addWidget(self.bootstrap_seed_spin)
        rerun = button("重新运行", "secondary", "play")
        rerun.clicked.connect(self.run_bootstrap)
        self.bootstrap_run_button = rerun
        select_row.addWidget(rerun); select_row.addStretch(1); layout.addLayout(select_row)
        card = Card()
        chart_header = QHBoxLayout()
        self.bootstrap_chart_title = section_title("Bootstrap 参数分布 · k")
        chart_header.addWidget(self.bootstrap_chart_title)
        chart_header.addStretch(1)
        self.bootstrap_chart_summary = QLabel("中位数 2.509  [2.41, 2.62]", objectName="Muted")
        chart_header.addWidget(self.bootstrap_chart_summary)
        chart_header.addWidget(badge("95% 百分位区间", "info"))
        card.layout().addLayout(chart_header)
        plot = EngineeringPlot("参数值", "频数", 240); plot.bars([2.40, 2.44, 2.48, 2.52, 2.56, 2.60], [2, 8, 22, 34, 24, 10], t.SUCCESS, .032)
        self.bootstrap_plot = plot
        card.layout().addWidget(plot); layout.addWidget(card)
        return page

    @staticmethod
    def _parameter_rows(result: dict[str, Any]) -> list[list[str]]:
        rows = []
        for name, info in (result.get("parameters", {}) or {}).items():
            rows.append([
                str(name),
                f"{float(info.get('mean', float('nan'))):.6g}",
                f"{float(info.get('median', float('nan'))):.6g}",
                f"{float(info.get('p2_5', float('nan'))):.6g}",
                f"{float(info.get('p97_5', float('nan'))):.6g}",
            ])
        return rows

    def run_bootstrap(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            self.toast_requested.emit("Bootstrap 已重新运行")
            return False
        try:
            window = self.window()
            worker = window.run_bootstrap_async({"B": self.bootstrap_b_spin.value(), "seed": self.bootstrap_seed_spin.value(), "algorithm": "least_squares"}, self.on_bootstrap_done)
            self.bootstrap_run_button.setEnabled(False)
            self.bootstrap_cards["状态"].set_value("运行中")
            self._bootstrap_worker = worker
            return True
        except Exception as exc:
            self.on_analysis_error("bootstrap", str(exc))
            return False

    def on_bootstrap_done(self, result: dict[str, Any] | None = None, emit: bool = True):
        self.bootstrap_run_button.setEnabled(True)
        result = result or {}
        self.bootstrap_cards["Bootstrap 样本数"].set_value(str(result.get("B", 0)))
        self.bootstrap_cards["随机种子"].set_value(str(result.get("seed", "—")))
        self.bootstrap_cards["状态"].set_value("已完成")
        rows = self._parameter_rows(result)
        if rows:
            self.bootstrap_model.replace_rows(rows)
            self.bootstrap_parameter.blockSignals(True)
            self.bootstrap_parameter.clear()
            self.bootstrap_parameter.addItems([row[0] for row in rows])
            self.bootstrap_parameter.blockSignals(False)
            self._update_bootstrap_plot()
        if emit:
            self.toast_requested.emit("Bootstrap 已完成")

    def _update_bootstrap_plot(self):
        name = self.bootstrap_parameter.currentText()
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        result = project.results.get("bootstrap", {}) if project is not None else {}
        info = result.get("parameters", {}).get(name, {}) if isinstance(result, dict) else {}
        samples = np.asarray(info.get("samples", []), dtype=float)
        self.bootstrap_plot.clear()
        if samples.size:
            hist, edges = np.histogram(samples, bins=min(20, max(5, int(np.sqrt(samples.size)))))
            centers = (edges[:-1] + edges[1:]) / 2
            width = float(np.diff(edges).mean() * .8) if len(edges) > 1 else .03
            self.bootstrap_plot.bars(centers, hist, t.SUCCESS, width)
            median = float(info.get("median", np.median(samples)))
            lo = float(info.get("p2_5", np.percentile(samples, 2.5)))
            hi = float(info.get("p97_5", np.percentile(samples, 97.5)))
            self.bootstrap_chart_title.setText(f"Bootstrap 参数分布 · {name}")
            self.bootstrap_chart_summary.setText(f"中位数 {median:.6g}  [{lo:.6g}, {hi:.6g}]")

    def run_stability(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            self.toast_requested.emit("多起点分析已完成")
            return False
        try:
            worker = self.window().run_stability_async({"n_starts": 10, "seed": 42}, self.on_stability_done)
            self.multi_run_button.setEnabled(False)
            self.multi_cards["成功率"].set_value("运行中")
            self._stability_worker = worker
            return True
        except Exception as exc:
            self.on_analysis_error("stability", str(exc))
            return False

    def on_stability_done(self, result: dict[str, Any] | None = None, emit: bool = True):
        self.multi_run_button.setEnabled(True)
        result = result or {}
        n_starts = int(result.get("n_starts", 0) or 0)
        n_success = int(result.get("n_success", result.get("n_feasible", 0)) or 0)
        rate = float(result.get("success_rate", n_success / n_starts if n_starts else 0.0))
        self.multi_cards["起点数"].set_value(str(n_starts))
        self.multi_cards["成功次数"].set_value(str(n_success))
        self.multi_cards["成功率"].set_value(f"{rate * 100:.1f}%")
        self.multi_cards["最佳 RMSE"].set_value(f"{float(result.get('best_objective', float('nan'))):.6g}")
        project = getattr(_window_app(self), "project", None)
        names = [p.name for p in project.parameters.free_parameters()] if project is not None else []
        samples = result.get("parameters", {}) or {}
        if names and samples:
            count = max((len(info.get("samples", [])) for info in samples.values()), default=0)
            rows = []
            for i in range(count):
                rows.append([i + 1] + [f"{float(samples.get(name, {}).get('samples', [float('nan')] * count)[i]):.6g}" for name in names])
            self.multi_model.headers = ["起点", *names]
            self.multi_model.replace_rows(rows)
        if emit:
            self.toast_requested.emit("多起点分析已完成")

    def on_analysis_error(self, kind: str, message: str):
        if kind == "bootstrap":
            self.bootstrap_run_button.setEnabled(True)
            self.bootstrap_cards["状态"].set_value("失败")
        else:
            self.multi_run_button.setEnabled(True)
            self.multi_cards["成功率"].set_value("失败")

    def on_project_changed(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            return
        stability = project.results.get("stability")
        if isinstance(stability, dict) and stability.get("parameters"):
            self.on_stability_done(stability, emit=False)
        else:
            self.multi_cards["起点数"].set_value("—")
            self.multi_cards["成功次数"].set_value("—")
            self.multi_cards["成功率"].set_value("—")
            self.multi_cards["最佳 RMSE"].set_value("—")
            self.multi_model.replace_rows([])
        bootstrap = project.results.get("bootstrap")
        if isinstance(bootstrap, dict) and bootstrap.get("parameters"):
            self.on_bootstrap_done(bootstrap, emit=False)
        else:
            self.bootstrap_cards["Bootstrap 样本数"].set_value("—")
            self.bootstrap_cards["随机种子"].set_value("—")
            self.bootstrap_cards["状态"].set_value("未运行")
            self.bootstrap_model.replace_rows([])
            self.bootstrap_plot.clear()

    on_result_changed = on_project_changed


class ExportPage(BasePage):
    def __init__(self):
        super().__init__()
        self.add_header("结果导出", "选择需要包含的分析内容和导出格式。")
        body = QHBoxLayout()
        content = Card(); content.layout().addWidget(section_title("导出内容"))
        options = QGridLayout()
        self.checkboxes: dict[str, QCheckBox] = {}
        check_items = (("summary", "项目概要"), ("parameters", "参数结果"), ("metrics", "评估指标"), ("simulation", "仿真结果"), ("residuals", "残差结果"), ("diagnostics", "诊断结果"), ("bootstrap", "Bootstrap 结果"))
        for i, (key, text) in enumerate(check_items):
            check = QCheckBox(text); check.setChecked(True); self.checkboxes[key] = check; options.addWidget(check, i // 2, i % 2)
        content.layout().addLayout(options); content.layout().addStretch(1); body.addWidget(content, 1)
        settings = QVBoxLayout()
        format_card = Card(); format_card.layout().addWidget(section_title("格式")); combo = QComboBox(); combo.addItem("Excel", "excel"); combo.addItem("CSV", "csv"); combo.addItem("HTML 报告", "html"); combo.addItem("PNG 图像", "png"); self.format_combo = combo; format_card.layout().addWidget(combo); settings.addWidget(format_card)
        dest_card = Card(); dest_card.layout().addWidget(section_title("导出位置")); dest_row = QHBoxLayout(); self.destination = QLineEdit(str(Path.cwd() / "export")); self.destination.setToolTip("导出的文件夹"); dest_row.addWidget(self.destination, 1)
        browse = button("浏览…", "secondary")
        browse.clicked.connect(self.browse_destination)
        self.browse_button = browse
        dest_row.addWidget(browse); dest_card.layout().addLayout(dest_row); settings.addWidget(dest_card)
        export = button("导出结果", "primary", "export"); export.clicked.connect(self.run_export); settings.addWidget(export)
        self.export_button = export
        self.export_result = QLabel("导出完成 · 已生成 6 个文件")
        self.export_result.setProperty("badge", "success")
        self.export_result.setWordWrap(True)
        self.export_result.hide()
        settings.addWidget(self.export_result)
        settings.addStretch(1); body.addLayout(settings, 1)
        self.root.addLayout(body, 1)

    def browse_destination(self):
        path = QFileDialog.getExistingDirectory(self, "选择导出位置", self.destination.text())
        if path:
            self.destination.setText(path)

    def _checks(self) -> dict[str, bool]:
        return {key: checkbox.isChecked() for key, checkbox in self.checkboxes.items()}

    def run_export(self):
        app = _window_app(self)
        project = getattr(app, "project", None) if app is not None else None
        if project is None:
            # Keep the standalone reference surface useful in visual tests.
            self.export_result.setText("导出完成 · 已生成 6 个文件")
            self.export_result.show()
            self.toast_requested.emit("导出完成")
            return True
        if not any(self._checks().values()):
            self.export_result.setText("请至少选择一项导出内容")
            self.export_result.setProperty("badge", "warning")
            self.export_result.show()
            self.toast_requested.emit("请至少选择一项导出内容")
            return False
        try:
            fmt = self.format_combo.currentData()
            output = self.window().export_results(self.destination.text().strip(), fmt, self._checks())
            paths = [line for line in str(output).splitlines() if line.strip()]
            self.export_result.setText(f"导出完成 · 已生成 {len(paths)} 个文件" if paths else "导出完成 · 没有可导出的结果")
            self.export_result.setProperty("badge", "success" if paths else "warning")
            self.export_result.show()
            self.toast_requested.emit("导出完成" if paths else "没有生成文件")
            return bool(paths)
        except Exception as exc:
            self.export_result.setText(f"导出失败：{exc}")
            self.export_result.setProperty("badge", "danger")
            self.export_result.show()
            self.toast_requested.emit(f"导出失败：{exc}")
            return False

    def on_project_changed(self):
        project = getattr(_window_app(self), "project", None)
        if project is None:
            return
        self.export_button.setEnabled(True)

    on_result_changed = on_project_changed


class SettingsPage(BasePage):
    def __init__(self):
        super().__init__(); self.add_header("设置", "外观、界面与应用偏好。")
        row = QHBoxLayout()
        appearance = Card(); appearance.layout().addWidget(section_title("外观")); self.theme_badge = badge("浅色", "success"); appearance.layout().addWidget(self.theme_badge, 0, Qt.AlignmentFlag.AlignLeft); appearance.layout().addWidget(QLabel("当前迁移版本仅提供浅色主题", objectName="Muted")); appearance.layout().addStretch(1); row.addWidget(appearance, 1)
        ui = Card(); ui.layout().addWidget(section_title("界面")); form = QFormLayout()
        self.sidebar_combo = QComboBox(); self.sidebar_combo.addItems(["展开", "折叠"]); self.sidebar_combo.currentTextChanged.connect(self._sidebar_changed); form.addRow("侧边栏", self.sidebar_combo)
        self.grid_combo = QComboBox(); self.grid_combo.addItems(["开启", "关闭"]); self.grid_combo.currentTextChanged.connect(self._grid_changed); form.addRow("图表网格", self.grid_combo)
        self.decimals_combo = QComboBox(); self.decimals_combo.addItems(["2", "3", "4", "6"]); self.decimals_combo.currentTextChanged.connect(self._decimals_changed); form.addRow("小数位数", self.decimals_combo)
        ui.layout().addLayout(form); ui.layout().addStretch(1); row.addWidget(ui, 1); row.addStretch(1); self.root.addLayout(row, 1)
        self._load_settings()

    def _settings(self):
        app_window = self.window()
        settings = getattr(app_window, "_settings", None)
        # During MainWindow construction pages are instantiated before they
        # are reparented, so ``window()`` can still be this page itself.
        return settings if hasattr(settings, "value") else None

    def _load_settings(self):
        settings = self._settings()
        # Sidebar collapse is intentionally session-local.  Reading the live
        # widget keeps this page synchronized with the shell without allowing
        # a stale preference from a previous process to change the next
        # launch's geometry.
        sidebar = getattr(self.window(), "sidebar", None)
        collapsed = bool(getattr(sidebar, "collapsed", False))
        self.sidebar_combo.blockSignals(True); self.sidebar_combo.setCurrentText("折叠" if collapsed else "展开"); self.sidebar_combo.blockSignals(False)
        if settings is None:
            return
        grid = settings.value("plot_grid", True)
        grid = grid not in (False, 0, "0", "false", "False")
        self.grid_combo.blockSignals(True); self.grid_combo.setCurrentText("开启" if grid else "关闭"); self.grid_combo.blockSignals(False)
        decimals = str(settings.value("decimals", "3"))
        if decimals not in ("2", "3", "4", "6"):
            decimals = "3"
        self.decimals_combo.blockSignals(True); self.decimals_combo.setCurrentText(decimals); self.decimals_combo.blockSignals(False)
        self._apply_grid(grid)

    def _sidebar_changed(self, value: str):
        settings = self._settings()
        collapsed = value == "折叠"
        sidebar = getattr(self.window(), "sidebar", None)
        if sidebar is not None and bool(getattr(sidebar, "collapsed", False)) != collapsed:
            sidebar.toggle()

    def _grid_changed(self, value: str):
        enabled = value == "开启"
        settings = self._settings()
        if settings is not None:
            settings.setValue("plot_grid", enabled)
        self._apply_grid(enabled)

    def _apply_grid(self, enabled: bool):
        for page in getattr(self.window(), "pages", {}).values():
            for plot in page.findChildren(EngineeringPlot):
                plot.plot.showGrid(x=enabled, y=enabled, alpha=.14)

    def _decimals_changed(self, value: str):
        settings = self._settings()
        if settings is not None:
            settings.setValue("decimals", value)
        parameters = getattr(self.window(), "pages", {}).get("parameters")
        if parameters is not None and hasattr(parameters, "set_decimal_places"):
            parameters.set_decimal_places(int(value))

    def on_project_changed(self):
        self._load_settings()

    on_result_changed = on_project_changed


class AboutPage(BasePage):
    def __init__(self):
        super().__init__(); self.add_header("关于", "软件信息与技术栈。")
        card = Card(); card.setMaximumWidth(620); card.layout().addWidget(QLabel("NDM Calibrator", objectName="MetricValue")); card.layout().addWidget(QLabel("非线性动态模型参数辨识与校准软件", objectName="BodySecondary")); card.layout().addWidget(QLabel("PySide6 桌面版 · 版本 1.0", objectName="Muted")); card.layout().addSpacing(10); card.layout().addWidget(section_title("技术栈")); card.layout().addWidget(QLabel("Python   PySide6   PyQtGraph", objectName="BodySecondary")); card.layout().addWidget(QLabel("支持项目管理、动态模型辨识、诊断分析与结果导出。", objectName="Muted")); self.root.addWidget(card); self.root.addStretch(1)


PAGE_CLASSES = {
    "dashboard": DashboardPage, "data": DataPage, "model": ModelPage,
    "parameters": ParametersPage, "identification": IdentificationPage,
    "calibration": CalibrationPage, "diagnostics": DiagnosticsPage,
    "uncertainty": UncertaintyPage, "export": ExportPage,
    "settings": SettingsPage, "about": AboutPage,
}
