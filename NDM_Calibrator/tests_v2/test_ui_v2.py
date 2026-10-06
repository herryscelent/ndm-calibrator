from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

from ui_v2.components import AlertDialog, ComboBoxDelegate, ConfirmDialog, DoubleSpinBoxDelegate, UnsavedChangesDialog
from ui_v2.main_window import MainWindow
from ui_v2.mock_data import DATA_ROWS, PARAMETERS, TIME_SERIES


def test_main_window_create(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.pages.keys() >= {"dashboard", "data", "identification", "about"}


def test_initial_conditions_are_inferred_from_imported_data(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.app.new_project("initial-condition regression")
    csv = Path(__file__).resolve().parents[1] / "examples" / "exponential_decay" / "data.csv"
    window.app.import_data(str(csv), "time", [], ["x"])

    from core.model_definition import DynamicModel

    window.app.set_model(DynamicModel.from_builtin("exponential_decay"))
    project = window.app.project
    assert project.settings["initial_conditions"]["x"] == pytest.approx(4.976849007057598)

    result = window.app.run_identification("least_squares", {
        "method": "trf",
        "max_iterations": 2000,
        "tolerance": 1e-8,
        "rtol": 1e-6,
        "atol": 1e-9,
        "input_interpolation": "linear",
    })
    assert result["parameters"]["k"] == pytest.approx(0.35, abs=0.01)

    window.app.close_project()
    window.close()


def test_mock_chart_domains_and_data_rows():
    assert TIME_SERIES[0][0] == 0.0
    assert TIME_SERIES[-1][0] == 50.0
    assert len(DATA_ROWS) == 24
    assert DATA_ROWS[:5] == [
        (0.0, 0, 0.0, 0),
        (0.5, 0, 0.654, 1.306),
        (1.0, 0, 2.002, 3.998),
        (1.5, 0, 2.003, 3.994),
        (2.0, 1, 2.004, 3.988),
    ]


def test_navigation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.navigate("parameters")
    assert window.stack.currentWidget() is window.scrolls["parameters"]
    assert window.sidebar.buttons["parameters"].isChecked()


def test_sidebar_collapse(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    before = window.sidebar.width()
    window.sidebar.toggle()
    assert window.sidebar.width() < before


def test_parameter_edit(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["parameters"]
    index = page.model.index(0, 1)
    assert page.model.setData(index, "2.100")
    assert page.model.data(index) == "2.100"
    assert isinstance(page.table.itemDelegateForColumn(1), DoubleSpinBoxDelegate)
    assert isinstance(page.table.itemDelegateForColumn(4), ComboBoxDelegate)


def test_parameter_validation(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["parameters"]
    assert page.validate_parameters() is True
    page.model.setData(page.model.index(0, 1), "20")
    assert page.validate_parameters() is False
    assert page.validation_badge.text() == "参数边界无效"


def test_identification_states(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["identification"]
    page.start_mock()
    assert page.run_state == "running"
    assert page.action.text() == "取消辨识"
    page.complete_mock()
    assert page.run_state == "completed"
    assert page.status_badge.text() == "已完成"
    assert not page.result.isHidden()


def test_data_mapping_delegate(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["data"]
    delegate = page.mapping_table.itemDelegateForColumn(1)
    assert isinstance(delegate, ComboBoxDelegate)
    editor = delegate.createEditor(page.mapping_table, None, page.mapping_table.model().index(0, 1))
    assert isinstance(editor, QComboBox)
    assert editor.findText("忽略") >= 0


def test_identification_cancel_and_error(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["identification"]
    page.start_mock()
    page.cancel_mock()
    assert page.run_state == "cancelled"
    assert page.status_badge.text() == "已取消"
    page.error_mock()
    assert page.run_state == "error"
    assert page.status_badge.text() == "运行失败"


def test_diagnostics_tabs(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["diagnostics"]
    page.tabs.setCurrentIndex(3)
    assert page.tabs.tabText(page.tabs.currentIndex()) == "相关性"


def test_toast(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    window.show_toast("测试消息")
    assert window.toast.label.text() == "测试消息"


def test_toast_avoids_page_content(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    window.navigate("calibration")
    window.show_toast("参数辨识已完成")
    qtbot.wait(10)
    toast = window.toast.geometry()
    topbar = window.topbar
    for action in topbar.action_buttons.values():
        action_rect = action.geometry().translated(topbar.pos())
        assert not toast.intersects(action_rect)
    for content in (window.pages["calibration"].calibration_plot, window.pages["calibration"].result_table):
        content_rect = content.geometry()
        content_rect.moveTopLeft(content.mapTo(window.centralWidget(), content_rect.topLeft()))
        assert not toast.intersects(content_rect)


def test_themed_alert_dialogs(qtbot):
    alert = AlertDialog(None, "错误", "测试错误")
    qtbot.addWidget(alert)
    assert alert.objectName() == "AlertDialog"
    unsaved = UnsavedChangesDialog(None, "未保存的修改", "是否保存？")
    qtbot.addWidget(unsaved)
    assert unsaved.objectName() == "UnsavedChangesDialog"
    unsaved.discard_button.click()
    assert unsaved.choice == "discard"


def test_export_page_exists(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["export"]
    page.run_export()
    assert not page.export_result.isHidden()
    assert "6 个文件" in page.export_result.text()


def test_confirm_dialog_is_styled(qtbot):
    dialog = ConfirmDialog(None, "删除参数", "确认删除参数 k？", "删除", True)
    qtbot.addWidget(dialog)
    assert dialog.objectName() == "ConfirmDialog"
    assert dialog.confirm_button.property("variant") == "dangerFilled"
    assert dialog.cancel_button.text() == "取消"


def test_parameter_toolbar_actions(qtbot, monkeypatch):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["parameters"]
    original_count = page.model.rowCount()
    page.add_parameter()
    assert page.model.rowCount() == original_count + 1
    page.table.selectRow(original_count)
    monkeypatch.setattr(ConfirmDialog, "ask", lambda *args, **kwargs: True)
    page.remove_selected()
    assert page.model.rowCount() == original_count
    page.add_parameter()
    page.reset_parameters()
    assert page.model.rowCount() == len(page.model.rows) == len(PARAMETERS)


def test_data_filter_series_and_tooltip(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    page = window.pages["data"]
    page.search.setText("3.998")
    qtbot.wait(10)
    assert page.data_proxy.rowCount() >= 1
    page.series_selector.setCurrentIndex(1)
    assert len(page.data_plot.plot.listDataItems()) == 2
    index = page.data_model.index(2, 3)
    assert page.data_model.data(index, Qt.ItemDataRole.ToolTipRole) == "3.998"


def test_interaction_states_and_tab_overflow_controls(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    identification = window.pages["identification"]
    identification.toggle_advanced(True)
    assert not identification.advanced_panel.isHidden()
    identification.show_running_snapshot(3)
    assert identification.run_state == "running"
    assert identification.eval_card.value_label.toolTip() == "60 / 2,000"

    diagnostics = window.pages["diagnostics"]
    uncertainty = window.pages["uncertainty"]
    assert diagnostics.tabs.tabBar().usesScrollButtons()
    assert uncertainty.tabs.tabBar().usesScrollButtons()
    assert uncertainty.tabs.currentIndex() == 0


def test_minimum_desktop_layout_and_long_text(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(1100, 700)
    window.show()
    qtbot.wait(30)
    long_name = "二阶机械系统参数校准 · 超长项目名称 · 工况数据集 A-001"
    window.topbar.project_context.setText(long_name)
    qtbot.wait(10)
    assert window.topbar.project_context.width() >= 160
    assert window.topbar.project_context.toolTip() == long_name

    for route, scroll in window.scrolls.items():
        window.navigate(route)
        qtbot.wait(5)
        assert scroll.horizontalScrollBar().maximum() == 0, route

    window.navigate("data")
    assert window.pages["data"].data_table.horizontalScrollBar().maximum() > 0


def test_topbar_navigation_actions(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.mouseClick(window.topbar.action_buttons["settings"], Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is window.scrolls["settings"]
    qtbot.mouseClick(window.topbar.action_buttons["about"], Qt.MouseButton.LeftButton)
    assert window.stack.currentWidget() is window.scrolls["about"]


def test_application_close(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    window.close()
    assert window.isVisible() is False
