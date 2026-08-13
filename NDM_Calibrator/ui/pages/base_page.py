"""Base page and page-state helpers."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QWidget

from ui.components.common import EmptyState, PageHeader, SectionPanel


class PageState(str, Enum):
    EMPTY = "empty"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class BasePage(QWidget):
    """Common plumbing for all pages: header + a stacked state container."""

    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QStackedWidget, QVBoxLayout

        self._state = PageState.EMPTY
        self.page_title = title
        self.page_subtitle = subtitle

        self.outer = QVBoxLayout(self)
        self.outer.setContentsMargins(24, 20, 24, 20)
        self.outer.setSpacing(16)

        self.header = PageHeader(title, subtitle)
        self.outer.addWidget(self.header)

        self.stack = QStackedWidget(self)
        self.outer.addWidget(self.stack, 1)

        # Empty-state page (shown by default until a page fills its content).
        self.empty_widget = self.make_empty_state()
        self.stack.addWidget(self.empty_widget)
        self.content_widget = QWidget(self)
        self.stack.addWidget(self.content_widget)
        self._content_lay = QVBoxLayout(self.content_widget)
        self._content_lay.setContentsMargins(0, 0, 0, 0)
        self._content_lay.setSpacing(16)
        self._build_content()

        self.stack.setCurrentWidget(self.empty_widget)

    # ------------------------------------------------------------------ #
    def make_empty_state(self) -> EmptyState:
        return EmptyState(
            "尚未就绪",
            "完成前置步骤后, 此页面将显示可用内容。",
            "",
        )

    def _build_content(self) -> None:
        """Hook for subclasses to populate self.body()."""

    def body(self) -> QVBoxLayout:
        return self._content_lay

    def set_empty(self) -> None:
        self._state = PageState.EMPTY
        self.stack.setCurrentWidget(self.empty_widget)

    def show_content(self) -> None:
        self._state = PageState.READY
        self.stack.setCurrentWidget(self.content_widget)

    def set_empty_state(self, title: str, description: str, action_text: str = "", action_icon: str = "") -> None:
        """Replace the empty-state text (call before set_empty)."""
        self.empty_widget.title.setText(title)
        self.empty_widget.desc.setText(description)
        self.empty_widget.set_action_visible(bool(action_text))

    # ------------------------------------------------------------------ #
    def refresh(self) -> None:
        """Called by MainWindow when the project changes; pages override."""
        self.on_project_changed()

    def on_project_changed(self) -> None:
        pass

    def on_result_changed(self) -> None:
        pass
