"""Left navigation sidebar."""

from __future__ import annotations

from typing import List, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QPushButton, QVBoxLayout, QWidget

from ui.design.icons import icon
from ui.design.tokens import SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_WIDTH_EXPANDED


class Sidebar(QWidget):
    """Vertical navigation with expanded/collapsed modes."""

    navigation_requested = Signal(str)

    # (key, label, icon_name)
    NAV_ITEMS: List[Tuple[str, str, str]] = [
        ("dashboard", "项目首页", "dashboard"),
        ("data", "数据管理", "data"),
        ("model", "模型定义", "model"),
        ("parameters", "参数配置", "parameters"),
        ("identification", "参数辨识", "identify"),
        ("calibration", "模型校准", "calibrate"),
        ("diagnostics", "诊断分析", "diagnostics"),
        ("uncertainty", "可信度分析", "uncertainty"),
        ("export", "结果导出", "export"),
    ]

    FOOTER_ITEMS: List[Tuple[str, str, str]] = [
        ("settings", "设置", "settings"),
        ("about", "关于", "about"),
    ]

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self._theme = theme_manager
        self._collapsed = False
        self.setObjectName("Sidebar")
        self._buttons = {}

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 8, 0, 8)
        self._layout.setSpacing(2)

        self._add_section_label("工作流")
        for key, label, ico in self.NAV_ITEMS:
            self._add_button(key, label, ico)

        self._layout.addStretch(1)

        self._add_section_label("应用")
        for key, label, ico in self.FOOTER_ITEMS:
            self._add_button(key, label, ico)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for btn in self._buttons.values():
            self._group.addButton(btn)

        self.setFixedWidth(SIDEBAR_WIDTH_EXPANDED)

    def _add_section_label(self, text: str) -> None:
        from PySide6.QtWidgets import QLabel

        self._layout.addWidget(QLabel(text, self, objectName="SidebarSectionLabel"))

    def _add_button(self, key: str, label: str, icon_name: str) -> None:
        btn = QPushButton(label, self)
        btn.setObjectName("SidebarNavButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        color = self._theme.palette.text_secondary
        btn.setIcon(icon(icon_name, color))
        btn.setIconSize(btn.iconSize().expandedTo(btn.iconSize()))
        btn.clicked.connect(lambda: self.navigation_requested.emit(key))
        btn.setProperty("navKey", key)
        self._buttons[key] = btn
        self._layout.addWidget(btn)

    def set_collapsed(self, collapsed: bool) -> None:
        self._collapsed = collapsed
        width = SIDEBAR_WIDTH_COLLAPSED if collapsed else SIDEBAR_WIDTH_EXPANDED
        self.setFixedWidth(width)
        lookup = {k: label for k, label, _ in self.NAV_ITEMS + self.FOOTER_ITEMS}
        for key, btn in self._buttons.items():
            if collapsed:
                btn.setText("")
            else:
                btn.setText(lookup[key])
        self.update()

    def is_collapsed(self) -> bool:
        return self._collapsed

    def select(self, key: str) -> None:
        btn = self._buttons.get(key)
        if btn is not None:
            btn.setChecked(True)
