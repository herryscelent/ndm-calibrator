from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QStyledItemDelegate, QTableView, QVBoxLayout,
    QWidget,
)

from ui.design.icons import icon

from . import tokens as t


def button(text: str = "", variant: str = "secondary", icon_name: str | None = None) -> QPushButton:
    widget = QPushButton(text)
    widget.setProperty("variant", variant)
    if icon_name:
        color = "#FFFFFF" if variant == "primary" else t.DANGER if variant == "danger" else t.TEXT_SECONDARY
        widget.setIcon(icon(icon_name, color))
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    return widget


def badge(text: str, variant: str = "neutral") -> QLabel:
    label = QLabel(text)
    label.setProperty("badge", variant)
    label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return label


def section_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("SectionTitle")
    return label


class ElidedLabel(QLabel):
    """Single-line label that preserves its full value in a tooltip."""

    def __init__(self, text: str = "", object_name: str | None = None):
        super().__init__()
        if object_name:
            self.setObjectName(object_name)
        self._full_text = text
        self.setToolTip(text)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self._apply_elision()

    def setText(self, text: str) -> None:
        self._full_text = text
        self.setToolTip(text)
        self._apply_elision()

    def fullText(self) -> str:
        return self._full_text

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_elision()

    def _apply_elision(self) -> None:
        available = max(0, self.width() - 2)
        visible = self.fontMetrics().elidedText(self._full_text, Qt.TextElideMode.ElideRight, available)
        QLabel.setText(self, visible)


class PageHeader(QWidget):
    def __init__(self, title: str, description: str, action: QWidget | None = None):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        texts = QVBoxLayout()
        texts.setSpacing(3)
        title_label = QLabel(title, objectName="PageTitle")
        description_label = ElidedLabel(description, "PageDescription")
        description_label.setMinimumWidth(220)
        texts.addWidget(title_label)
        texts.addWidget(description_label)
        row.addLayout(texts, 1)
        row.addStretch(1)
        if action:
            row.addWidget(action, 0, Qt.AlignmentFlag.AlignTop)


class Card(QFrame):
    def __init__(self, layout=None, object_name: str = "Card"):
        super().__init__()
        self.setObjectName(object_name)
        if layout is None:
            layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)
        self.setLayout(layout)


class MetricCard(Card):
    def __init__(self, label: str, value: str, sub: str = ""):
        layout = QVBoxLayout()
        super().__init__(layout)
        layout.setSpacing(2)
        layout.addWidget(QLabel(label, objectName="MetricLabel"))
        self.value_label = ElidedLabel(value, "MetricValue")
        layout.addWidget(self.value_label)
        if sub:
            layout.addWidget(QLabel(sub, objectName="Muted"))
        self.setMinimumWidth(124)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class SimpleTableModel(QAbstractTableModel):
    def __init__(self, headers: Sequence[str], rows: Sequence[Sequence[object]], editable_columns: set[int] | None = None):
        super().__init__()
        self.headers = list(headers)
        self.rows = [list(row) for row in rows]
        self.editable_columns = editable_columns or set()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        value = self.rows[index.row()][index.column()]
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return str(value)
        if role == Qt.ItemDataRole.ToolTipRole:
            return str(value)
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() > 0:
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if role == Qt.ItemDataRole.ForegroundRole:
            if str(value) == "待辨识":
                return QColor(t.ACCENT)
            if str(value) == "固定":
                return QColor(t.TEXT_SECONDARY)
        return None

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section] if orientation == Qt.Orientation.Horizontal else str(section + 1)
        return None

    def flags(self, index: QModelIndex):
        flags = super().flags(index)
        if index.column() in self.editable_columns:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole and index.column() in self.editable_columns:
            self.rows[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def append_row(self, row: Sequence[object]) -> int:
        position = len(self.rows)
        self.beginInsertRows(QModelIndex(), position, position)
        self.rows.append(list(row))
        self.endInsertRows()
        return position

    def remove_row(self, row: int) -> bool:
        if not 0 <= row < len(self.rows):
            return False
        self.beginRemoveRows(QModelIndex(), row, row)
        del self.rows[row]
        self.endRemoveRows()
        return True

    def replace_rows(self, rows: Sequence[Sequence[object]]) -> None:
        self.beginResetModel()
        self.rows = [list(row) for row in rows]
        self.endResetModel()


def table_view(
    model: QAbstractTableModel,
    row_height: int = 31,
    column_widths: Sequence[int] | None = None,
) -> QTableView:
    view = QTableView()
    view.setModel(model)
    view.verticalHeader().setVisible(False)
    view.verticalHeader().setDefaultSectionSize(row_height)
    view.horizontalHeader().setStretchLastSection(True)
    view.setAlternatingRowColors(False)
    view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    view.setShowGrid(True)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    if column_widths:
        header = view.horizontalHeader()
        header.setStretchLastSection(True)
        header.setMinimumSectionSize(56)
        for column, width in enumerate(column_widths):
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            view.setColumnWidth(column, width)
    return view


class ConfirmDialog(QDialog):
    """QSS-styled confirmation dialog used by destructive mock actions."""

    def __init__(
        self,
        parent: QWidget | None,
        title: str,
        message: str,
        confirm_text: str = "确认",
        dangerous: bool = False,
    ):
        super().__init__(parent)
        self.setObjectName("ConfirmDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        layout.addWidget(QLabel(title, objectName="DialogTitle"))
        message_label = QLabel(message, objectName="BodySecondary")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = button("取消", "secondary")
        confirm = button(confirm_text, "dangerFilled" if dangerous else "primary")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self.accept)
        actions.addWidget(cancel)
        actions.addWidget(confirm)
        layout.addLayout(actions)
        self.cancel_button = cancel
        self.confirm_button = confirm

    @classmethod
    def ask(
        cls,
        parent: QWidget | None,
        title: str,
        message: str,
        confirm_text: str = "确认",
        dangerous: bool = False,
    ) -> bool:
        dialog = cls(parent, title, message, confirm_text, dangerous)
        return dialog.exec() == QDialog.DialogCode.Accepted


class AlertDialog(QDialog):
    """Small themed informational/error dialog for application failures."""

    def __init__(self, parent: QWidget | None, title: str, message: str, confirm_text: str = "确定"):
        super().__init__(parent)
        self.setObjectName("AlertDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        layout.addWidget(QLabel(title, objectName="DialogTitle"))
        body = QLabel(str(message), objectName="BodySecondary")
        body.setWordWrap(True)
        layout.addWidget(body)
        actions = QHBoxLayout()
        actions.addStretch(1)
        confirm = button(confirm_text, "primary")
        confirm.clicked.connect(self.accept)
        actions.addWidget(confirm)
        layout.addLayout(actions)
        self.confirm_button = confirm

    @classmethod
    def show_message(cls, parent: QWidget | None, title: str, message: str) -> None:
        cls(parent, title, message).exec()


class UnsavedChangesDialog(QDialog):
    """Themed three-way choice used when leaving a dirty project."""

    def __init__(self, parent: QWidget | None, title: str, message: str):
        super().__init__(parent)
        self.setObjectName("UnsavedChangesDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(440)
        self.choice = "cancel"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        layout.addWidget(QLabel(title, objectName="DialogTitle"))
        body = QLabel(str(message), objectName="BodySecondary")
        body.setWordWrap(True)
        layout.addWidget(body)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = button("取消", "secondary")
        discard = button("放弃修改", "danger")
        save = button("保存", "primary")
        cancel.clicked.connect(self.reject)
        discard.clicked.connect(lambda: self._finish("discard"))
        save.clicked.connect(lambda: self._finish("save"))
        actions.addWidget(cancel)
        actions.addWidget(discard)
        actions.addWidget(save)
        layout.addLayout(actions)
        self.cancel_button = cancel
        self.discard_button = discard
        self.save_button = save

    def _finish(self, choice: str) -> None:
        self.choice = choice
        self.accept()

    @classmethod
    def ask(cls, parent: QWidget | None, title: str, message: str) -> str:
        dialog = cls(parent, title, message)
        dialog.exec()
        return dialog.choice


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, options: Sequence[str], parent=None):
        super().__init__(parent)
        self.options = list(options)

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.options)
        return editor

    def setEditorData(self, editor, index):
        editor.setCurrentText(str(index.data(Qt.ItemDataRole.EditRole)))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)


class DoubleSpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, minimum: float = -1e12, maximum: float = 1e12, parent=None):
        super().__init__(parent)
        self.minimum = minimum
        self.maximum = maximum

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(6)
        editor.setRange(self.minimum, self.maximum)
        editor.setSingleStep(0.01)
        return editor

    def setEditorData(self, editor, index):
        try:
            editor.setValue(float(index.data(Qt.ItemDataRole.EditRole)))
        except (TypeError, ValueError):
            editor.setValue(0.0)

    def setModelData(self, editor, model, index):
        value = f"{editor.value():.6f}".rstrip("0").rstrip(".")
        model.setData(index, value, Qt.ItemDataRole.EditRole)


class Toast(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setStyleSheet(f"background:{t.TEXT_PRIMARY}; border-radius:8px;")
        self.setMaximumWidth(440)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        self.label = QLabel()
        self.label.setStyleSheet("color:white;")
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(400)
        layout.addWidget(self.label)
        self.hide()

    def show_message(self, message: str, duration: int = 2200):
        self.label.setText(message)
        self.label.setToolTip(message)
        self.adjustSize()
        self.reposition()
        self.raise_()
        self.show()
        QTimer.singleShot(duration, self.hide)

    def reposition(self) -> None:
        """Place the toast in the shell without covering page content.

        The main window has a generous empty stretch between the project
        context and the icon actions in its topbar.  Using that space keeps
        transient feedback visible while leaving plots and tables unobscured.
        Standalone pages/tests do not have a topbar, so they retain the
        conventional bottom-right placement as a fallback.
        """
        parent = self.parentWidget()
        if parent is None:
            return
        topbar = parent.findChild(QWidget, "Topbar")
        if topbar is not None and topbar.width() > 0:
            project_context = topbar.findChild(QWidget, "ProjectContext")
            action_buttons = topbar.findChildren(QPushButton)
            left = project_context.geometry().right() + 10 if project_context is not None else 180
            right = min((button.geometry().left() for button in action_buttons), default=topbar.width() - 16) - 10
            width = self.width()
            if right - left >= width:
                x = topbar.geometry().x() + left + (right - left - width) // 2
                y = topbar.geometry().y() + max(2, (topbar.height() - self.height()) // 2)
                self.move(max(0, x), max(0, y))
                return
            # At unusually narrow widths keep the message in the topbar and
            # clamp it away from the window edges; page data remains clear.
            x = topbar.geometry().x() + max(8, (topbar.width() - width) // 2)
            y = topbar.geometry().y() + max(2, (topbar.height() - self.height()) // 2)
            self.move(max(0, x), max(0, y))
            return
        self.move(parent.width() - self.width() - 24, parent.height() - self.height() - 24)


class Sidebar(QWidget):
    navigation_requested = Signal(str)
    collapse_requested = Signal()

    ITEMS = [
        ("dashboard", "项目首页", "dashboard"), ("data", "数据管理", "data"),
        ("model", "模型定义", "model"), ("parameters", "参数配置", "parameters"),
        ("identification", "参数辨识", "identify"), ("calibration", "模型校准", "calibrate"),
        ("diagnostics", "诊断分析", "diagnostics"), ("uncertainty", "可信度分析", "uncertainty"),
        ("export", "结果导出", "export"),
    ]
    FOOTER = [("settings", "设置", "settings"), ("about", "关于", "about")]

    def __init__(self):
        super().__init__(objectName="Sidebar")
        self.buttons: dict[str, QPushButton] = {}
        self.icon_names: dict[str, str] = {}
        self.collapsed = False
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(1)
        self._section("工作流")
        for item in self.ITEMS:
            self._add(*item)
        self.layout.addStretch(1)
        self._section("应用")
        for item in self.FOOTER:
            self._add(*item)
        collapse = button("折叠", "secondary", "reset")
        collapse.setToolTip("折叠侧边栏")
        collapse.setAccessibleName("折叠侧边栏")
        collapse.clicked.connect(self.collapse_requested)
        self.layout.addWidget(collapse)
        self.collapse_button = collapse
        self.setFixedWidth(t.SIDEBAR_WIDTH)

    def _section(self, text: str):
        self.layout.addWidget(QLabel(text, objectName="SidebarSection"))

    def _add(self, key: str, label: str, icon_name: str):
        nav = QPushButton(label)
        nav.setProperty("nav", True)
        nav.setCheckable(True)
        nav.setIcon(icon(icon_name, t.TEXT_MUTED))
        nav.setToolTip(label)
        nav.setAccessibleName(label)
        nav.clicked.connect(lambda _, k=key: self.navigation_requested.emit(k))
        self.buttons[key] = nav
        self.icon_names[key] = icon_name
        self.layout.addWidget(nav)

    def select(self, key: str):
        for item_key, nav in self.buttons.items():
            selected = item_key == key
            nav.setChecked(selected)
            nav.setIcon(icon(self.icon_names[item_key], t.ACCENT if selected else t.TEXT_MUTED))

    def toggle(self):
        self.collapsed = not self.collapsed
        self.setFixedWidth(t.SIDEBAR_COLLAPSED if self.collapsed else t.SIDEBAR_WIDTH)
        labels = {key: label for key, label, _ in self.ITEMS + self.FOOTER}
        for key, nav in self.buttons.items():
            nav.setText("" if self.collapsed else labels[key])
        self.collapse_button.setText("" if self.collapsed else "折叠")
        self.collapse_button.setToolTip("展开侧边栏" if self.collapsed else "折叠侧边栏")
        self.collapse_button.setAccessibleName(self.collapse_button.toolTip())


class Topbar(QWidget):
    open_requested = Signal()
    new_requested = Signal()
    save_requested = Signal()
    theme_requested = Signal()
    settings_requested = Signal()
    about_requested = Signal()

    def __init__(self):
        super().__init__(objectName="Topbar")
        self.setFixedHeight(t.TOPBAR_HEIGHT)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        layout.addWidget(QLabel("NDM Calibrator", objectName="ProductName"))
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet(f"color:{t.BORDER};")
        layout.addWidget(divider)
        self.project_context = ElidedLabel("二阶机械系统参数校准", "ProjectContext")
        self.project_context.setMinimumWidth(160)
        self.project_context.setMaximumWidth(360)
        self.project_context.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.project_context)
        self.saved_badge = badge("已保存", "success")
        layout.addWidget(self.saved_badge)
        layout.addStretch(1)
        actions = (
            ("folder", "打开项目", self.open_requested),
            ("plus", "新建项目", self.new_requested),
            ("save", "保存项目", self.save_requested),
            ("moon", "主题", self.theme_requested),
            ("settings", "设置", self.settings_requested),
            ("about", "帮助", self.about_requested),
        )
        self.action_buttons = {}
        for icon_name, tip, signal in actions:
            action = QPushButton()
            action.setFixedSize(34, 34)
            action.setIcon(icon(icon_name, t.TEXT_SECONDARY))
            action.setToolTip(tip)
            action.setAccessibleName(tip)
            action.clicked.connect(signal.emit)
            self.action_buttons[icon_name] = action
            layout.addWidget(action)
