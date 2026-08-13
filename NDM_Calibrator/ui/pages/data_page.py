"""Data management page: import, summary, table, mapping and preview plot."""

from __future__ import annotations

from typing import Optional

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ui.components.common import SectionPanel
from ui.plots.specialized import TimeSeriesPlot
from ui.pages.base_page import BasePage


class DataFrameModel(QAbstractTableModel):
    """Read-only model over a pandas DataFrame."""

    def __init__(self, df: Optional[pd.DataFrame] = None, parent=None):
        super().__init__(parent)
        self._df = df if df is not None else pd.DataFrame()

    def set_dataframe(self, df: pd.DataFrame) -> None:
        self.beginResetModel()
        self._df = df
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return self._df.shape[0] if not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()) -> int:
        return self._df.shape[1] if not parent.isValid() else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        val = self._df.iat[index.row(), index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            if pd.isna(val):
                return ""
            if isinstance(val, float):
                return f"{val:.6g}"
            return str(val)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if isinstance(val, (int, float)):
                return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._df.columns[section])
            return section + 1
        return None


class DataPage(BasePage):
    """Handles CSV/XLSX import, mapping and preprocessing."""

    import_requested = Signal(str)
    data_changed = Signal()

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("数据管理", "导入实验时序数据, 映射字段并检查数据质量。")
        self._df: Optional[pd.DataFrame] = None
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        toolbar = QHBoxLayout()
        self.import_btn = QPushButton("导入 CSV / XLSX")
        self.import_btn.setObjectName("PrimaryButton")
        self.reset_btn = QPushButton("重置")
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.reset_btn)
        toolbar.addStretch(1)
        body.addLayout(toolbar)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #57606A;")
        body.addWidget(self.summary_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left: table
        table_panel = SectionPanel("数据预览")
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_model = DataFrameModel()
        self.table_view.setModel(self.table_model)
        self.table_view.setSortingEnabled(True)
        table_panel.add_widget(self.table_view)
        splitter.addWidget(table_panel)

        # Right: mapping + plot
        right = QVBoxLayout()
        right.setSpacing(12)
        mapping_panel = SectionPanel("字段映射")
        self.mapping_box = QComboBox()
        self.mapping_box.currentIndexChanged.connect(self._apply_mapping)
        mapping_panel.add_widget(self.mapping_box)
        self.mapping_help = QLabel("字段映射由模型自动推断。导入数据后选择映射方案。")
        self.mapping_help.setWordWrap(True)
        mapping_panel.add_widget(self.mapping_help)
        right.addWidget(mapping_panel)

        plot_panel = SectionPanel("数据曲线")
        self.preview_plot = TimeSeriesPlot(theme_manager=self._theme)
        plot_panel.add_widget(self.preview_plot)
        right.addWidget(plot_panel, 1)

        right_widget = QWidget()
        right_widget.setLayout(right)
        splitter.addWidget(right_widget)
        splitter.setSizes([500, 380])
        body.addWidget(splitter, 1)

        self.import_btn.clicked.connect(self._on_import_clicked)
        self.reset_btn.clicked.connect(self._on_reset)

    # ------------------------------------------------------------------ #
    def _on_import_clicked(self) -> None:
        app = self.window().app
        if app is None:
            return
        app.show_import_dialog()

    def _on_reset(self) -> None:
        app = self.window().app
        if app is not None:
            app.reset_data()

    def _apply_mapping(self) -> None:
        app = self.window().app
        if app is None or self._df is None:
            return
        scheme = self.mapping_box.currentData()
        if scheme is None:
            return
        app.apply_mapping_scheme(scheme)

    # ------------------------------------------------------------------ #
    def set_dataframe(self, df: pd.DataFrame) -> None:
        self._df = df
        self.table_model.set_dataframe(df)
        n, m = df.shape
        missing = int(df.isna().sum().sum())
        self.summary_label.setText(f"{n} 行 × {m} 列 | 缺失值 {missing}")

    def set_mapping_options(self, options) -> None:
        self.mapping_box.blockSignals(True)
        self.mapping_box.clear()
        for label, scheme in options:
            self.mapping_box.addItem(label, scheme)
        self.mapping_box.blockSignals(False)

    def on_project_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None or project.experiment is None:
            self.set_empty_state(
                "尚未导入实验数据",
                "导入 CSV 或 XLSX 文件以开始参数辨识。",
                "导入数据",
                "data",
            )
            self.import_btn.setText("导入数据")
            self.set_empty()
            return
        self.show_content()
        self.import_btn.setText("导入 CSV / XLSX")
        # Rebuild mapping options from project column info.
        if project.data_source:
            from data.loader import load_dataframe

            try:
                df, _ = load_dataframe(project.data_source)
                self.set_dataframe(df)
                options = [(c, {"role": "input", "column": c}) for c in df.columns if c not in project.mapping.get("outputs", {})]
            except Exception:
                self.set_dataframe(self._df if self._df is not None else pd.DataFrame())
