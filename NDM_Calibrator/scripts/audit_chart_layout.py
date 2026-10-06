from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6 import __version__ as PYSIDE_VERSION
from PySide6.QtCore import Qt, qVersion
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton,
    QTableView, QWidget,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source" if (ROOT / "source" / "ui_v2").exists() else ROOT
sys.path.insert(0, str(SOURCE_ROOT))

from ui_v2.main_window import MainWindow
from ui_v2.theme import apply_theme


VIEWPORTS = [(1100, 700), (1366, 768), (1440, 900), (1920, 1080)]
EXPECTED_X = {
    "dashboard": (0.0, 50.0),
    "calibration": (0.0, 50.0),
    "residual": (0.0, 29.5),
    "histogram": (-0.15, 0.12),
    "bootstrap": (2.40, 2.60),
}


def settle(app: QApplication, delay: float = 0.08) -> None:
    deadline = time.time() + delay
    while time.time() < deadline:
        app.processEvents()
        time.sleep(0.005)


def data_x_bounds(plot) -> tuple[float, float]:
    bounds = []
    for item in plot.plot.listDataItems():
        x, _ = item.getData()
        if x is not None and len(x):
            bounds.extend((float(min(x)), float(max(x))))
    for item in plot.plot.getPlotItem().items:
        opts = getattr(item, "opts", None)
        if not opts or "x" not in opts:
            continue
        x = opts["x"]
        if x is not None and len(x):
            bounds.extend((float(min(x)), float(max(x))))
    if not bounds:
        raise AssertionError("plot has no x data")
    return min(bounds), max(bounds)


def plot_geometry(plot) -> dict[str, float | int]:
    width = plot.plot.width()
    height = plot.plot.height()
    return {
        "width": width,
        "height": height,
        "aspect": round(width / height, 3),
    }


def text_and_overlap_audit(page: QWidget) -> dict[str, object]:
    clipped = []
    for widget in page.findChildren(QWidget):
        if not isinstance(widget, (QLabel, QPushButton, QComboBox, QCheckBox)):
            continue
        if not widget.isVisibleTo(page) or widget.width() <= 0:
            continue
        if isinstance(widget, QComboBox):
            text = widget.currentText()
            required = widget.fontMetrics().horizontalAdvance(text) + 38
        else:
            raw_text = widget.text().strip()
            text = raw_text.replace("\n", " ")
            if not text or (isinstance(widget, QLabel) and widget.wordWrap()):
                continue
            icon_space = 24 if isinstance(widget, QPushButton) and not widget.icon().isNull() else 0
            required = max(widget.fontMetrics().horizontalAdvance(line) for line in raw_text.splitlines()) + icon_space
            if isinstance(widget, QPushButton):
                required += 28
        if required > widget.width() + 2:
            clipped.append({
                "type": type(widget).__name__,
                "text": text,
                "required": required,
                "available": widget.width(),
            })

    overlaps = []
    for parent in page.findChildren(QWidget) + [page]:
        children = [
            child for child in parent.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly)
            if child.isVisibleTo(page) and not child.geometry().isEmpty()
        ]
        for index, first in enumerate(children):
            for second in children[index + 1:]:
                intersection = first.geometry().intersected(second.geometry())
                if intersection.width() > 2 and intersection.height() > 2:
                    overlaps.append({
                        "parent": type(parent).__name__,
                        "first": type(first).__name__,
                        "second": type(second).__name__,
                        "intersection": [intersection.width(), intersection.height()],
                    })
    return {"clipped": clipped, "overlaps": overlaps}


def table_content_audit(page: QWidget) -> dict[str, int]:
    missing_tooltips = []
    elided_cells = 0
    scrollable_tables = 0
    for table in page.findChildren(QTableView):
        if not table.isVisibleTo(page):
            continue
        if table.horizontalScrollBar().maximum() > 0:
            scrollable_tables += 1
        model = table.model()
        for row in range(min(model.rowCount(), 24)):
            for column in range(model.columnCount()):
                index = model.index(row, column)
                text = str(model.data(index, Qt.ItemDataRole.DisplayRole) or "")
                available = max(0, table.columnWidth(column) - 20)
                if table.fontMetrics().horizontalAdvance(text) <= available:
                    continue
                elided_cells += 1
                if str(model.data(index, Qt.ItemDataRole.ToolTipRole) or "") != text:
                    missing_tooltips.append((row, column, text))
    assert not missing_tooltips, f"elided table values missing tooltips: {missing_tooltips}"
    return {"tables": len(page.findChildren(QTableView)), "scrollable": scrollable_tables, "elided": elided_cells}


def assert_page_fits(window: MainWindow, route: str) -> None:
    scroll = window.scrolls[route]
    page = window.pages[route]
    assert scroll.horizontalScrollBar().maximum() == 0, f"{route}: outer horizontal overflow"
    assert page.width() <= scroll.viewport().width() + 2, (
        f"{route}: page width {page.width()} > viewport {scroll.viewport().width()}"
    )


def interaction_state_audit(window: MainWindow, app: QApplication) -> dict[str, int]:
    checked = 0
    identification = window.pages["identification"]
    window.navigate("identification")
    states = []
    identification.advanced_toggle.setChecked(True)
    identification.toggle_advanced(True)
    states.append(("advanced", identification.advanced_panel.isVisibleTo(identification)))
    identification.advanced_toggle.setChecked(False)
    identification.toggle_advanced(False)
    identification.show_running_snapshot(3)
    states.append(("running", identification.status_badge.text() == "运行中"))
    identification.complete_mock()
    states.append(("completed", identification.result.isVisibleTo(identification)))
    identification.start_mock()
    identification.cancel_mock()
    states.append(("cancelled", identification.status_badge.text() == "已取消"))
    identification.error_mock()
    states.append(("error", identification.status_badge.text() == "运行失败"))
    for name, condition in states:
        settle(app)
        assert condition, f"identification {name} state not visible"
        result = text_and_overlap_audit(identification)
        assert not result["clipped"], f"identification {name} clipped: {result['clipped']}"
        assert not result["overlaps"], f"identification {name} overlaps: {result['overlaps']}"
        checked += 1

    diagnostics = window.pages["diagnostics"]
    window.navigate("diagnostics")
    for index in range(diagnostics.tabs.count()):
        diagnostics.tabs.setCurrentIndex(index)
        settle(app)
        result = text_and_overlap_audit(diagnostics)
        assert not result["clipped"] and not result["overlaps"], f"diagnostics tab {index}: {result}"
        checked += 1

    uncertainty = window.pages["uncertainty"]
    window.navigate("uncertainty")
    for index in range(uncertainty.tabs.count()):
        uncertainty.tabs.setCurrentIndex(index)
        settle(app)
        result = text_and_overlap_audit(uncertainty)
        assert not result["clipped"] and not result["overlaps"], f"uncertainty tab {index}: {result}"
        checked += 1

    export = window.pages["export"]
    window.navigate("export")
    export.run_export()
    settle(app)
    assert export.export_result.isVisibleTo(export)
    checked += 1

    # Toast feedback must remain visible without covering a table/plot or a
    # topbar action.  The shell positions it in the topbar stretch area.
    window.show_toast("参数辨识已完成")
    settle(app)
    toast = window.toast.geometry()
    for action in window.topbar.action_buttons.values():
        action_rect = action.geometry().translated(window.topbar.pos())
        assert not toast.intersects(action_rect), f"toast covers topbar action {action.toolTip()}"
    for route in ("calibration", "diagnostics", "uncertainty", "export"):
        page = window.pages[route]
        for widget in page.findChildren(QWidget):
            if widget is page or not widget.isVisibleTo(page):
                continue
            if not isinstance(widget, QTableView) and type(widget).__name__ != "PlotWidget":
                continue
            top_left = widget.mapTo(window.centralWidget(), widget.rect().topLeft())
            rect = widget.rect()
            rect.moveTopLeft(top_left)
            assert not toast.intersects(rect), f"toast covers {route} content"
    window.toast.hide()
    return {"states_checked": checked}


def verify_images() -> dict[str, object]:
    web_dir = ROOT / "reference" / "web_screenshots"
    qt_dir = ROOT / "screenshots_qt"
    comparison_dir = ROOT / "comparison"
    web_sizes = {p.name: Image.open(p).size for p in web_dir.glob("*.png")}
    state_web_sizes = {p.name: Image.open(p).size for p in (ROOT / "reference" / "web_screenshots_states").glob("*.png")}
    # Ignore explicitly named debug grabs so a developer's temporary image
    # cannot make the formal 12-screen audit fail.
    qt_sizes = {p.name: Image.open(p).size for p in qt_dir.glob("*.png") if not p.name.startswith("debug_")}
    comparison_sizes = {p.name: Image.open(p).size for p in comparison_dir.glob("*.png")}
    state_sizes = {p.name: Image.open(p).size for p in (qt_dir / "states").glob("*.png")}
    state_comparison_sizes = {p.name: Image.open(p).size for p in (comparison_dir / "states").glob("*.png")}
    assert len(web_sizes) == 11
    assert len(qt_sizes) == 12
    assert len(comparison_sizes) == 11
    assert len(state_web_sizes) == 5
    assert len(state_sizes) == 4
    assert len(state_comparison_sizes) == 5
    assert set(web_sizes.values()) == {(1440, 900)}
    assert set(qt_sizes.values()) == {(1440, 900)}
    assert set(comparison_sizes.values()) == {(2880, 934)}
    return {
        "web": {"count": len(web_sizes), "size": [1440, 900], "aspect": 1.6},
        "qt": {"count": len(qt_sizes), "size": [1440, 900], "aspect": 1.6},
        "comparison": {"count": len(comparison_sizes), "size": [2880, 934]},
        "reference_states": {"count": len(state_web_sizes), "size": [1440, 900]},
        "interaction_states": {"count": len(state_sizes), "size": [1440, 900]},
        "state_comparison": {"count": len(state_comparison_sizes), "size": [2880, 934]},
    }


def main() -> int:
    app = QApplication.instance() or QApplication([])
    apply_theme(app)
    window = MainWindow()
    window.show()
    scale = float(os.environ.get("QT_SCALE_FACTOR", "1"))
    report = {
        "environment": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "qt": qVersion(),
            "pyside6": PYSIDE_VERSION,
            "requested_scale": scale,
            "device_pixel_ratio": window.devicePixelRatioF(),
            "platform_plugin": os.environ.get("QT_QPA_PLATFORM", "default"),
        },
        "images": verify_images(),
        "viewports": {},
    }

    for width, height in VIEWPORTS:
        window.resize(width, height)
        settle(app)
        viewport_report = {
            "window_size": [window.width(), window.height()],
            "client_size": [window.centralWidget().width(), window.centralWidget().height()],
        }

        dashboard = window.pages["dashboard"]
        window.navigate("dashboard")
        settle(app)
        flow_width = dashboard.workflow_panel.width()
        plot_width = dashboard.dashboard_plot.width()
        ratio = flow_width / (flow_width + plot_width)
        assert 0.37 <= ratio <= 0.43
        assert dashboard.dashboard_plot.plot.height() <= 260
        viewport_report["dashboard"] = {
            "workflow_share": round(ratio, 3),
            "plot": plot_geometry(dashboard.dashboard_plot),
        }

        data = window.pages["data"]
        window.navigate("data")
        settle(app)
        splitter_sizes = data.data_splitter.sizes()
        splitter_ratio = splitter_sizes[0] / sum(splitter_sizes)
        assert 0.56 <= splitter_ratio <= 0.64
        viewport_report["data"] = {
            "left_share": round(splitter_ratio, 3),
            "plot": plot_geometry(data.data_plot),
        }

        identification = window.pages["identification"]
        window.navigate("identification")
        settle(app)
        assert identification.plot.plot.height() <= 292
        viewport_report["identification"] = {"plot": plot_geometry(identification.plot)}

        calibration = window.pages["calibration"]
        window.navigate("calibration")
        settle(app)
        viewport_report["calibration"] = {"plot": plot_geometry(calibration.calibration_plot)}

        diagnostics = window.pages["diagnostics"]
        window.navigate("diagnostics")
        diagnostics.tabs.setCurrentIndex(0)
        settle(app)
        viewport_report["residual"] = {"plot": plot_geometry(diagnostics.residual_plot)}
        viewport_report["histogram"] = {"plot": plot_geometry(diagnostics.residual_histogram)}

        uncertainty = window.pages["uncertainty"]
        window.navigate("uncertainty")
        uncertainty.tabs.setCurrentIndex(1)
        settle(app)
        viewport_report["bootstrap"] = {"plot": plot_geometry(uncertainty.bootstrap_plot)}

        table_report = {}
        for route in ("dashboard", "data", "model", "parameters", "identification", "calibration", "diagnostics", "uncertainty", "export", "settings", "about"):
            window.navigate(route)
            settle(app, 0.02)
            assert_page_fits(window, route)
            text_layout = text_and_overlap_audit(window.pages[route])
            assert not text_layout["clipped"], f"{route} clipped text: {text_layout['clipped']}"
            assert not text_layout["overlaps"], f"{route} overlaps: {text_layout['overlaps']}"
            table_report[route] = table_content_audit(window.pages[route])
        viewport_report["text_layout"] = {"clipped": 0, "overlaps": 0}
        viewport_report["tables"] = table_report

        for shell_part in (window.topbar, window.sidebar):
            shell_layout = text_and_overlap_audit(shell_part)
            assert not shell_layout["clipped"], f"shell clipped text: {shell_layout['clipped']}"
            assert not shell_layout["overlaps"], f"shell overlaps: {shell_layout['overlaps']}"

        original_context = window.topbar.project_context.fullText()
        long_context = "二阶机械系统参数校准 · 超长项目名称 · 批次 2026-08-26 · 工况数据集 A-001"
        window.topbar.project_context.setText(long_context)
        settle(app)
        assert window.topbar.project_context.toolTip() == long_context
        assert window.topbar.project_context.width() > 0
        window.topbar.project_context.setText(original_context)

        window.show_toast("导出完成 · 已生成 6 个文件 · 内容较长时仍保持在窗口内")
        settle(app)
        toast = window.toast.geometry()
        shell = window.centralWidget().rect()
        assert shell.contains(toast), f"toast escapes client area: {toast} vs {shell}"
        window.toast.hide()
        viewport_report["interaction_states"] = interaction_state_audit(window, app)

        if width == 1100:
            window.navigate("data")
            settle(app)
            assert data.data_table.horizontalScrollBar().maximum() > 0, (
                "data table must use local horizontal scrolling at minimum desktop width"
            )

        actual_bounds = {
            "dashboard": data_x_bounds(dashboard.dashboard_plot),
            "calibration": data_x_bounds(calibration.calibration_plot),
            "residual": data_x_bounds(diagnostics.residual_plot),
            "histogram": data_x_bounds(diagnostics.residual_histogram),
            "bootstrap": data_x_bounds(uncertainty.bootstrap_plot),
        }
        for name, expected in EXPECTED_X.items():
            actual = actual_bounds[name]
            assert actual == expected, f"{name}: expected {expected}, got {actual}"
            viewport_report[name]["data_x"] = list(actual)

        report["viewports"][f"{width}x{height}"] = viewport_report

    window.close()
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    scale_key = int(round(scale * 100))
    report_path = ROOT / "docs" / f"QT_LAYOUT_AUDIT_{scale_key}.json"
    report_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    print(f"saved: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
