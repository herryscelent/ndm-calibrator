"""Model definition page."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
)

from core.exceptions import ModelError, NDMCError
from core.model_definition import DynamicModel, builtin_model_labels, builtin_model_keys
from ui.components.common import SectionPanel, StatusBadge
from ui.pages.base_page import BasePage

_HELP = """使用以下格式定义状态空间模型:

状态 states:
x1
x2

输入 inputs:
u

参数 parameters:
k
c
b

方程 (每行一个):
dx1/dt = x2
dx2/dt = -k*x1 - c*x2 + b*u

输出 outputs:
y

输出方程:
y = x1
"""


class ModelPage(BasePage):
    """Built-in template selection and user-defined model editor."""

    model_changed = Signal()

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("模型定义", "选择内置模型模板或定义自定义非线性动态模型。")
        self._model: DynamicModel | None = None
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        top = QHBoxLayout()
        top.addWidget(QLabel("模型来源:"))
        self.source_combo = QComboBox()
        self.source_combo.addItem("内置模型模板", "builtin")
        self.source_combo.addItem("用户自定义模型", "user")
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        top.addWidget(self.source_combo)
        top.addStretch(1)
        body.addLayout(top)

        self.builtin_panel = SectionPanel("内置模型模板")
        self.builtin_combo = QComboBox()
        self.builtin_combo.currentIndexChanged.connect(self._on_builtin_changed)
        self.builtin_panel.add_widget(self.builtin_combo)
        self.builtin_desc = QLabel("")
        self.builtin_desc.setWordWrap(True)
        self.builtin_panel.add_widget(self.builtin_desc)
        body.addWidget(self.builtin_panel)

        self.user_panel = SectionPanel("自定义模型编辑")
        self.editor = QPlainTextEdit()
        self.editor.setFont(__import__("PySide6.QtGui", fromlist=["QFont"]).QFont("Consolas", 11))
        self.editor.setPlaceholderText(_HELP)
        self.editor.setPlainText(_HELP)
        self.user_panel.add_widget(self.editor)
        body.addWidget(self.user_panel)

        validate_row = QHBoxLayout()
        self.validate_btn = QPushButton("验证模型")
        self.validate_btn.setObjectName("PrimaryButton")
        self.badge = StatusBadge("未验证", "neutral")
        validate_row.addWidget(self.validate_btn)
        validate_row.addWidget(self.badge)
        validate_row.addStretch(1)
        body.addLayout(validate_row)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #CF222E;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        body.addWidget(self.error_label)

        self.validate_btn.clicked.connect(self._validate)
        self._load_builtin_list()
        self._on_source_changed()

    def _load_builtin_list(self) -> None:
        self.builtin_combo.clear()
        for key in builtin_model_keys():
            self.builtin_combo.addItem(builtin_model_labels()[key], key)
        if self.builtin_combo.count():
            self._on_builtin_changed()

    def _on_source_changed(self) -> None:
        is_user = self.source_combo.currentData() == "user"
        self.builtin_panel.setVisible(not is_user)
        self.user_panel.setVisible(is_user)

    def _on_builtin_changed(self) -> None:
        key = self.builtin_combo.currentData()
        if key:
            from core.model_definition import get_builtin_model

            m = get_builtin_model(key)
            self.builtin_desc.setText(m.description if m else "")

    def _validate(self) -> None:
        app = self.window().app
        if app is None:
            return
        try:
            if self.source_combo.currentData() == "builtin":
                key = self.builtin_combo.currentData()
                model = DynamicModel.from_builtin(key)
            else:
                model = self._parse_user_model()
            app.set_model(model)
            self._model = model
            self.badge.set_status("success", "模型有效")
            self.error_label.hide()
            self.model_changed.emit()
        except (ModelError, NDMCError) as exc:
            self.badge.set_status("error", "模型无效")
            self.error_label.setText(str(exc))
            self.error_label.show()

    def _parse_user_model(self) -> DynamicModel:
        text = self.editor.toPlainText()
        sections = {}
        current = None
        eqs = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            low = line.lower()
            if low.startswith(("states", "状态")):
                current = "states"; continue
            if low.startswith(("inputs", "输入")):
                current = "inputs"; continue
            if low.startswith(("parameters", "参数")):
                current = "parameters"; continue
            if low.startswith(("outputs", "输出")):
                current = "outputs"; continue
            if low.startswith(("dynamics", "方程")) or low.startswith(("equations",)):
                current = "equations"; continue
            if "=" in line and ("/dt" in line or current == "equations"):
                eqs.append(line)
                continue
            if current in ("states", "inputs", "parameters", "outputs"):
                sections.setdefault(current, []).append(line.strip())

        states = sections.get("states") or []
        inputs = sections.get("inputs") or []
        params = sections.get("parameters") or []
        outputs = sections.get("outputs") or states

        # Separate dynamic equations and output equations.
        dynamics = {}
        output_eqs = {}
        for eq in eqs:
            lhs, rhs = eq.split("=", 1)
            lhs = lhs.strip()
            if "/dt" in lhs:
                dynamics[lhs] = rhs.strip()
            else:
                output_eqs[lhs] = rhs.strip()

        if not states or not params:
            raise ModelError("请定义状态和参数")

        # Output equations default to identity on states.
        if not output_eqs:
            output_eqs = {out: out for out in outputs}

        return DynamicModel.from_user_definition(
            states=states,
            inputs=inputs,
            parameters=params,
            dynamics=dynamics,
            outputs=outputs,
            output_equations=output_eqs,
            description="用户自定义模型",
        )

    def on_project_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            self.set_empty_state("新建或打开一个项目", "定义模型前请先创建项目。", "", "")
            self.set_empty()
            return
        self.show_content()
