"""Top application bar: app title, project name, dirty indicator and actions."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QToolButton, QWidget

from ui.design.icons import icon


class TopBar(QWidget):
    save_requested = Signal()
    save_as_requested = Signal()
    open_requested = Signal()
    new_requested = Signal()
    theme_toggle_requested = Signal()
    settings_requested = Signal()

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self._theme = theme_manager
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(10)

        self.app_title = QLabel("非线性动态模型参数辨识与校准软件")
        self.app_title.setObjectName("AppTitle")
        lay.addWidget(self.app_title)

        self.project_name = QLabel("未命名项目")
        self.project_name.setObjectName("ProjectName")
        self.project_name.setToolTip("未命名项目")
        lay.addWidget(self.project_name)

        self.dirty = QLabel("● 未保存")
        self.dirty.setObjectName("DirtyIndicator")
        self.dirty.hide()
        lay.addWidget(self.dirty)

        lay.addStretch(1)

        for name, tip, slot in (
            ("folder", "打开项目 (Ctrl+O)", self.open_requested),
            ("save", "保存项目 (Ctrl+S)", self.save_requested),
        ):
            btn = QToolButton(self)
            btn.setObjectName("IconButton")
            btn.setIcon(icon(name, theme_manager.palette.text_secondary))
            btn.setToolTip(tip)
            btn.setAccessibleName(tip)
            btn.clicked.connect(slot)
            lay.addWidget(btn)

        theme_btn = QToolButton(self)
        theme_btn.setObjectName("IconButton")
        theme_btn.setIcon(icon("moon", theme_manager.palette.text_secondary))
        theme_btn.setToolTip("切换主题 (Light/Dark)")
        theme_btn.setAccessibleName("切换主题")
        theme_btn.clicked.connect(self.theme_toggle_requested)
        lay.addWidget(theme_btn)

    def set_project(self, name: str, dirty: bool = False) -> None:
        self.project_name.setText(name)
        self.project_name.setToolTip(name)
        self.dirty.setVisible(dirty)
