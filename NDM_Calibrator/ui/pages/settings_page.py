"""Settings page and About page."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from ui.components.common import SectionPanel
from ui.pages.base_page import BasePage


class SettingsPage(BasePage):
    """Application settings (appearance, UI, application)."""

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("设置", "外观、界面与应用偏好设置 (即时生效)。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        app_panel = SectionPanel("外观")
        form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色 (Light)", "light")
        self.theme_combo.addItem("深色 (Dark)", "dark")
        self.theme_combo.addItem("跟随系统 (System)", "system")
        self.theme_combo.setCurrentText(
            {"light": "浅色 (Light)", "dark": "深色 (Dark)", "system": "跟随系统 (System)"}.get(self._theme.theme, "浅色 (Light)")
        )
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        form.addRow("主题", self.theme_combo)
        app_panel.add_layout(form)
        body.addWidget(app_panel)

        ui_panel = SectionPanel("界面")
        ui_form = QFormLayout()
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(0, 10)
        self.decimal_spin.setValue(6)
        ui_form.addRow("数字精度 (小数位)", self.decimal_spin)
        ui_panel.add_layout(ui_form)
        body.addWidget(ui_panel)

        about = QLabel("设置即时生效。主题选择会保存并在下次启动时恢复。")
        about.setStyleSheet("color: #57606A;")
        body.addWidget(about)
        body.addStretch(1)

    def _on_theme_changed(self) -> None:
        theme = self.theme_combo.currentData()
        self._theme.set_theme(theme)

    def on_project_changed(self) -> None:
        self.show_content()


class AboutPage(BasePage):
    """About / version information."""

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("关于", "软件版本、构建与依赖信息。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()
        panel = SectionPanel("非线性动态模型参数辨识与校准软件")
        text = QLabel(
            "<h3>V1.0</h3>"
            "<p><b>NDM-Calibrator</b></p>"
            "<p>基于已有实验/观测时序数据, 对用户定义的非线性动态模型中的未知参数进行辨识、校准和可信度分析。</p>"
            "<p><b>技术栈:</b> Python · PySide6 · NumPy · SciPy · SymPy · PyQtGraph · Matplotlib</p>"
            "<p><b>许可:</b> 内部工具软件</p>"
        )
        text.setTextInteractionFlags(text.textInteractionFlags())
        text.setWordWrap(True)
        panel.add_widget(text)
        body.addWidget(panel)
        body.addStretch(1)

    def on_project_changed(self) -> None:
        self.show_content()
