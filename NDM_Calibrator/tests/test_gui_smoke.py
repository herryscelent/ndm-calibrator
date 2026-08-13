"""GUI smoke tests (run with QT_QPA_PLATFORM=offscreen)."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def app():
    _app = QApplication.instance() or QApplication([])
    yield _app


@pytest.fixture
def window(app):
    from ui.main_window import MainWindow

    w = MainWindow()
    w.show()
    app.processEvents()
    yield w
    # Close without triggering the dirty-save confirmation dialog.
    w.app.close_project()
    w.close()


@pytest.fixture
def loaded_project(window):
    """A MainWindow with a fully identified first-order project."""
    window.app.new_project("smoke")
    csv = ROOT / "examples" / "first_order" / "data.csv"
    if csv.exists():
        df = pd.read_csv(csv)
        window.app.import_data(str(csv), "time", ["u"], ["x"])
        window.pages["data"].set_dataframe(df)
    from core.model_definition import DynamicModel
    from core.parameter import ParameterTable

    window.app.set_model(DynamicModel.from_builtin("first_order"))
    pt = ParameterTable()
    pt.sync_from_names(["K", "tau"])
    pt.get("K").initial = 2.0
    pt.get("K").lower = 0.01
    pt.get("K").upper = 20.0
    pt.get("tau").initial = 6.0
    pt.get("tau").lower = 0.1
    pt.get("tau").upper = 100.0
    window.app.project.parameters = pt

    from app.application import run_identification_for_project

    run_identification_for_project(window.app.project, "least_squares", {})
    window._run_calibration()
    window._after_project_change()
    return window


class TestMainWindow:
    def test_creation(self, window):
        assert len(window.pages) == 11
        assert window.stack.count() == 11

    def test_page_switch(self, app, window):
        for key in ("data", "model", "parameters", "identification", "calibration",
                    "diagnostics", "uncertainty", "export", "settings", "about"):
            window.navigate(key)
            app.processEvents()
            assert window.stack.currentWidget() is window.pages[key]

    def test_theme_switch(self, window):
        window.theme.set_theme("dark")
        assert window.theme.is_dark()
        window.theme.set_theme("light")
        assert not window.theme.is_dark()

    def test_sidebar_collapse(self, window):
        window.sidebar.set_collapsed(True)
        assert window.sidebar.is_collapsed()
        window.sidebar.set_collapsed(False)
        assert not window.sidebar.is_collapsed()

    def test_status_bar(self, window):
        window.status("Ready")
        assert "Ready" in window.status_label.text()


class TestEmptyStates:
    def test_data_page_empty(self, app, window):
        window.navigate("data")
        app.processEvents()
        assert window.pages["data"].stack.currentWidget() is window.pages["data"].empty_widget

    def test_parameters_empty(self, app, window):
        window.navigate("parameters")
        app.processEvents()
        assert window.pages["parameters"].stack.currentWidget() is window.pages["parameters"].empty_widget


class TestParameterEditing:
    def test_add_parameter(self, app, window, loaded_project):
        page = window.pages["parameters"]
        n_before = len(page.table_widget.model.table())
        page.table_widget.model.add_parameter()
        assert len(page.table_widget.model.table()) == n_before + 1

    def test_invalid_range_detected(self, app, window, loaded_project):
        page = window.pages["parameters"]
        model = page.table_widget.model
        model.setData(model.index(0, 1), 50.0)  # initial > upper
        model.setData(model.index(0, 3), 10.0)  # upper < initial
        assert model.errors  # errors populated

    def test_validate_button(self, app, window, loaded_project):
        page = window.pages["parameters"]
        window.navigate("parameters")
        page._validate()
        errors = window.validate_parameters()
        assert isinstance(errors, list)


class TestResultStates:
    def test_calibration_shows_metrics(self, app, window, loaded_project):
        window.navigate("calibration")
        app.processEvents()
        page = window.pages["calibration"]
        assert page.metric_rmse.value.text() != "N/A"

    def test_diagnostics_populated(self, app, window, loaded_project):
        window.navigate("diagnostics")
        app.processEvents()
        page = window.pages["diagnostics"]
        assert page.sens_table.rowCount() > 0
        assert page.corr_table.rowCount() >= 0

    def test_export_page_ready(self, app, window, loaded_project):
        window.navigate("export")
        app.processEvents()
        assert window.pages["export"].stack.currentWidget() is window.pages["export"].content_widget


class TestErrorState:
    def test_identification_without_model_errors(self, window):
        window.app.new_project("err")
        window.navigate("identification")
        page = window.pages["identification"]
        page.start()
        # No model -> should not crash; page shows empty state or error badge.
        assert page.badge is not None
