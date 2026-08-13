"""Editable parameter table (Model/View) with validation."""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.parameter import Parameter, ParameterTable
from ui.design.colors import palette_for


class ParameterTableModel(QAbstractTableModel):
    """Table model exposing Parameter objects as editable rows.

    Columns: Parameter | Initial | Lower | Upper | Status
    """

    HEADERS = ["参数", "初值", "下限", "上限", "状态"]

    def __init__(self, table: Optional[ParameterTable] = None, parent=None):
        super().__init__(parent)
        self._table = table if table is not None else ParameterTable()
        self.errors: dict[str, str] = {}

    # ------------------------------------------------------------------ #
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._table) if not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.HEADERS[section]
            return section + 1
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        param = self._parameter_at(index.row())
        col = index.column()
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if col == 0:
                return param.name
            if col == 1:
                return param.initial
            if col == 2:
                return param.lower
            if col == 3:
                return param.upper
            if col == 4:
                return "待辨识" if param.free else "固定"
        if role == Qt.ItemDataRole.ForegroundRole and col == 0:
            return QColor(palette_for("light").text_secondary)
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False
        param = self._parameter_at(index.row())
        col = index.column()
        try:
            if col == 1:
                param.initial = float(value)
            elif col == 2:
                param.lower = float(value)
            elif col == 3:
                param.upper = float(value)
        except (TypeError, ValueError):
            return False
        self.dataChanged.emit(index, index)
        self.validate_all()
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    def _parameter_at(self, row: int) -> Parameter:
        return list(self._table)[row]

    # ------------------------------------------------------------------ #
    def set_parameters(self, table: ParameterTable) -> None:
        self.beginResetModel()
        self._table = table
        self.errors.clear()
        self.endResetModel()
        self.validate_all()

    def add_parameter(self, name: str = "") -> None:
        import re

        base = name or "p"
        candidate = base
        idx = 1
        while candidate in self._table:
            candidate = f"{base}{idx}"
            idx += 1
        self.beginInsertRows(QModelIndex(), len(self._table), len(self._table))
        self._table.add(Parameter(name=candidate))
        self.endInsertRows()
        self.validate_all()

    def remove_selected(self, rows: List[int]) -> None:
        for row in sorted(rows, reverse=True):
            param = self._parameter_at(row)
            self.beginRemoveRows(QModelIndex(), row, row)
            try:
                self._table.remove(param.name)
            except KeyError:
                pass
            self.endRemoveRows()
        self.validate_all()

    def reset_defaults(self) -> None:
        for p in self._table:
            p.initial = 1.0
            p.lower = 0.001
            p.upper = 1000.0
            p.free = True
        self.layoutChanged.emit()
        self.validate_all()

    def validate_all(self) -> None:
        self.errors.clear()
        for p in self._table:
            if not p.lower < p.initial < p.upper:
                self.errors[p.name] = f"需要 lower < initial < upper (当前: {p.lower} < {p.initial} < {p.upper})"
        self.error_changed.emit(dict(self.errors))

    error_changed = Signal(dict)

    def table(self) -> ParameterTable:
        return self._table


class ParameterTableWidget(QWidget):
    """Composite widget: table + toolbar (Add/Remove/Reset) + error panel."""

    changed = Signal()

    def __init__(self, table: Optional[ParameterTable] = None, parent=None):
        super().__init__(parent)
        self.model = ParameterTableModel(table, self)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("新增参数")
        self.remove_btn = QPushButton("删除参数")
        self.reset_btn = QPushButton("恢复默认")
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.remove_btn)
        toolbar.addWidget(self.reset_btn)
        toolbar.addStretch(1)
        lay.addLayout(toolbar)

        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setAlternatingRowColors(True)
        self.view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setSortingEnabled(False)
        for col, width in enumerate((90, 100, 100, 100, 80)):
            self.view.setColumnWidth(col, width)
        lay.addWidget(self.view, 1)

        self.error_label = QLabel(self)
        self.error_label.setObjectName("InlineError")
        self.error_label.setStyleSheet("color: #CF222E;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        lay.addWidget(self.error_label)

        self.add_btn.clicked.connect(self._add)
        self.remove_btn.clicked.connect(self._remove)
        self.reset_btn.clicked.connect(self._reset)
        self.model.error_changed.connect(self._show_errors)
        self.model.dataChanged.connect(lambda *_: self.changed.emit())

    def _add(self) -> None:
        self.model.add_parameter()
        self.changed.emit()

    def _remove(self) -> None:
        rows = sorted({i.row() for i in self.view.selectionModel().selectedRows()})
        if not rows:
            return
        self.model.remove_selected(rows)
        self.changed.emit()

    def _reset(self) -> None:
        self.model.reset_defaults()
        self.changed.emit()

    def _show_errors(self, errors: dict) -> None:
        if errors:
            first = next(iter(errors.values()))
            self.error_label.setText(f"参数范围错误: {first}")
            self.error_label.show()
        else:
            self.error_label.hide()

    def set_parameters(self, table: ParameterTable) -> None:
        self.model.set_parameters(table)

    def get_parameters(self) -> ParameterTable:
        return self.model.table()
