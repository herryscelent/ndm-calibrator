"""Reusable UI components shared across pages."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design.colors import palette_for
from ui.design.icons import icon


class StatusBadge(QLabel):
    """Coloured status pill (● Label). Used only for status indication."""

    STATUS_COLORS = {
        "success": "success",
        "warning": "warning",
        "error": "danger",
        "info": "info",
        "neutral": "text_secondary",
        "running": "info",
    }

    def __init__(self, text: str, status: str = "neutral", parent=None):
        super().__init__(parent)
        self._status = status
        self.setText(f"● {text}")
        self.apply_theme()

    def set_status(self, status: str, text: Optional[str] = None) -> None:
        self._status = status
        if text is not None:
            self.setText(f"● {text}")
        self.apply_theme()

    def apply_theme(self) -> None:
        color_name = self.STATUS_COLORS.get(self._status, "text_secondary")
        color = getattr(palette_for("light"), color_name, "#57606A")
        self.setStyleSheet(f"color: {color}; font-size: 12px;")


class MetricCard(QFrame):
    """Compact KPI card: label + value."""

    def __init__(self, label: str, value: str = "Not available", parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)
        self.label = QLabel(label)
        self.label.setObjectName("MetricLabel")
        self.value = QLabel(value)
        self.value.setObjectName("MetricValue")
        lay.addWidget(self.label)
        lay.addWidget(self.value)

    def set_value(self, value: str) -> None:
        self.value.setText(value)


class EmptyState(QWidget):
    """Empty state with icon, title, description and a primary action."""

    def __init__(self, title: str, description: str, action_text: str = "", action_icon: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(10)

        ic = QLabel()
        ic.setPixmap(icon("search", palette_for("light").text_disabled).pixmap(48, 48))
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ic)

        self.title = QLabel(title)
        self.title.setObjectName("EmptyTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.title)

        self.desc = QLabel(description)
        self.desc.setObjectName("EmptyDesc")
        self.desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc.setWordWrap(True)
        lay.addWidget(self.desc)

        if action_text:
            self.action = QPushButton(action_text)
            self.action.setObjectName("PrimaryButton")
            if action_icon:
                self.action.setIcon(icon(action_icon, palette_for("light").accent_text))
            lay.addWidget(self.action)
            lay.addSpacing(4)

    def set_action_visible(self, visible: bool) -> None:
        btn = getattr(self, "action", None)
        if btn is not None:
            btn.setVisible(visible)


class PageHeader(QWidget):
    """Standard page header: title + subtitle (+ optional primary action)."""

    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self.title = QLabel(title)
        self.title.setObjectName("PageTitle")
        self.subtitle = QLabel(subtitle)
        self.subtitle.setObjectName("PageSubtitle")
        self.subtitle.setWordWrap(True)
        text_col.addWidget(self.title)
        text_col.addWidget(self.subtitle)
        lay.addLayout(text_col, 1)

        self._actions = QHBoxLayout()
        self._actions.setSpacing(8)
        lay.addLayout(self._actions)

    def add_action(self, button: QPushButton) -> None:
        self._actions.addWidget(button)


class SectionPanel(QFrame):
    """A titled panel container."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SectionPanel")
        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(16, 12, 16, 16)
        self.outer.setSpacing(10)
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("SectionTitle")
            self.outer.addWidget(self.title_label)

    def add_widget(self, widget: QWidget) -> None:
        self.outer.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.outer.addLayout(layout)


class Toast(QWidget):
    """Lightweight transient toast notification (appears bottom-right)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.hide()

    def show_message(self, text: str) -> None:
        from PySide6.QtCore import QTimer

        self.setStyleSheet(
            "background: rgba(31,35,40,0.92); color: white; border-radius: 6px; padding: 10px 16px;"
        )
        self.label = QLabel(text, self)
        self.label.setStyleSheet("color: white; background: transparent;")
        self.resize(self.label.sizeHint().width() + 32, self.label.sizeHint().height() + 20)
        self.label.move(16, 10)
        self.adjustSize()
        self.show()
        parent_rect = self.parentWidget().rect() if self.parentWidget() else None
        if parent_rect:
            self.move(parent_rect.right() - self.width() - 20, parent_rect.bottom() - self.height() - 20)
        QTimer.singleShot(2600, self.hide)
