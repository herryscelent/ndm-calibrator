"""Export page: choose formats and destination, run exports."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from core.exceptions import NDMCError
from ui.components.common import SectionPanel
from ui.pages.base_page import BasePage


class ExportPage(BasePage):
    """Export results to Excel / CSV / images / HTML report."""

    def __init__(self, theme_manager, parent=None):
        self._theme = theme_manager
        super().__init__("结果导出", "导出参数、指标、诊断与 Bootstrap 结果。")
        self._build_content()

    def _build_content(self) -> None:
        body = self.body()

        panel = SectionPanel("导出内容")
        form = QFormLayout()
        self.chk_summary = QCheckBox("项目信息")
        self.chk_params = QCheckBox("参数结果")
        self.chk_metrics = QCheckBox("拟合指标")
        self.chk_simulation = QCheckBox("模拟序列")
        self.chk_residuals = QCheckBox("残差")
        self.chk_diagnostics = QCheckBox("诊断分析")
        self.chk_bootstrap = QCheckBox("Bootstrap 结果")
        for chk in (self.chk_summary, self.chk_params, self.chk_metrics, self.chk_simulation,
                    self.chk_residuals, self.chk_diagnostics, self.chk_bootstrap):
            chk.setChecked(True)
            form.addRow(chk)
        panel.add_layout(form)
        body.addWidget(panel)

        fmt_panel = SectionPanel("导出格式")
        fmt_form = QFormLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItem("Excel 工作簿 (.xlsx)", "excel")
        self.format_combo.addItem("HTML 分析报告", "report")
        fmt_form.addRow("格式", self.format_combo)
        fmt_panel.add_layout(fmt_form)
        body.addWidget(fmt_panel)

        dest_panel = SectionPanel("导出位置")
        dest_form = QFormLayout()
        self.dest_edit = QLineEdit()
        browse_btn = QPushButton("浏览…")
        browse_btn.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.dest_edit)
        row.addWidget(browse_btn)
        dest_form.addRow("目标目录", row)
        dest_panel.add_layout(dest_form)
        body.addWidget(dest_panel)

        run_row = QHBoxLayout()
        self.export_btn = QPushButton("导出")
        self.export_btn.setObjectName("PrimaryButton")
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #57606A;")
        run_row.addWidget(self.export_btn)
        run_row.addWidget(self.status_label)
        run_row.addStretch(1)
        body.addLayout(run_row)

        self.export_btn.clicked.connect(self._export)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if path:
            self.dest_edit.setText(path)

    def _export(self) -> None:
        app = self.window().app
        if app is None:
            return
        dest = self.dest_edit.text().strip()
        if not dest:
            self.status_label.setText("请选择导出目录")
            return
        fmt = self.format_combo.currentData()
        checks = {
            "summary": self.chk_summary.isChecked(),
            "parameters": self.chk_params.isChecked(),
            "metrics": self.chk_metrics.isChecked(),
            "simulation": self.chk_simulation.isChecked(),
            "residuals": self.chk_residuals.isChecked(),
            "diagnostics": self.chk_diagnostics.isChecked(),
            "bootstrap": self.chk_bootstrap.isChecked(),
        }
        try:
            result = app.export_results(dest, fmt, checks)
            self.status_label.setText(result)
        except NDMCError as exc:
            self.status_label.setText(f"导出失败: {exc}")

    def on_project_changed(self) -> None:
        app = self.window().app
        project = app.project if app else None
        if project is None:
            self.set_empty_state("新建或打开一个项目", "完成辨识后, 在此导出分析结果。", "", "")
            self.set_empty()
            return
        self.show_content()
