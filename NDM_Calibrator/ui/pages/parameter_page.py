"""Parameter configuration page."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QHBoxLayout

from core.exceptions import NDMCError
from ui.components.common import StatusBadge
from ui.components.parameter_table import ParameterTableWidget
from ui.pages.base_page import BasePage


class ParameterPage(BasePage):
    """Edit free/fixed parameters, bounds and initial values."""

    parameters_changed = Signal()

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("参数配置", "设置待辨识参数的初值、约束范围及固定状态。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        row = QHBoxLayout()
        self.sync_btn = QPushButton("从模型同步参数")
        self.validate_btn = QPushButton("验证")
        self.validate_btn.setObjectName("PrimaryButton")
        self.badge = StatusBadge("未验证", "neutral")
        row.addWidget(self.sync_btn)
        row.addWidget(self.validate_btn)
        row.addWidget(self.badge)
        row.addStretch(1)
        body.addLayout(row)

        self.table_widget = ParameterTableWidget()
        body.addWidget(self.table_widget, 1)

        self.sync_btn.clicked.connect(self._sync_from_model)
        self.validate_btn.clicked.connect(self._validate)
        self.table_widget.changed.connect(self.parameters_changed)

    def _sync_from_model(self) -> None:
        app = self.window().app
        if app is None:
            return
        try:
            app.sync_parameters_from_model()
            self.table_widget.set_parameters(app.project.parameters)
            self.badge.set_status("info", "已同步")
        except NDMCError as exc:
            self.badge.set_status("error", str(exc))

    def _validate(self) -> None:
        app = self.window().app
        if app is None:
            return
        try:
            errors = app.validate_parameters()
            if errors:
                self.badge.set_status("error", "参数无效")
            else:
                self.badge.set_status("success", "参数有效")
        except NDMCError as exc:
            self.badge.set_status("error", str(exc))

    def on_project_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            self.set_empty_state("新建或打开一个项目", "配置参数前请先创建项目并定义模型。", "", "")
            self.set_empty()
            return
        self.show_content()
        self.table_widget.set_parameters(project.parameters)
