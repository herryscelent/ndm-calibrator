"""Capture GUI screenshots for visual review (gui_prompt requirement).

Runs the real application offscreen with a fully identified example project,
renders each major page in Light and Dark, and saves PNGs to screenshots/.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

OUT = ROOT / "screenshots"


def _grab(app, window, path: Path) -> None:
    window.resize(1440, 900)
    app.processEvents()
    window.grab().save(str(path))
    print(f"saved: {path.name}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication([])

    from ui.main_window import MainWindow
    from core.model_definition import DynamicModel
    from core.parameter import ParameterTable
    from app.application import run_identification_for_project
    from diagnostics.orchestrator import run_calibration_and_diagnostics
    from uncertainty.bootstrap import run_bootstrap

    window = MainWindow()
    window.show()
    app.processEvents()

    # Build a fully identified project from Example 2.
    window.app.new_project("示例项目: 一阶惯性系统")
    csv = ROOT / "examples" / "first_order" / "data.csv"
    if csv.exists():
        window.app.import_data(str(csv), "time", ["u"], ["x"])
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

    run_identification_for_project(window.app.project, "least_squares", {})
    run_calibration_and_diagnostics(window.app.project, window.app.project.results["identification"]["result"]["parameters"])
    run_bootstrap(window.app.project, {"B": 40, "seed": 7})
    window._after_project_change()
    app.processEvents()

    # Light theme screenshots
    window.theme.set_theme("light")
    for key, name in (
        ("dashboard", "01_dashboard_light"),
        ("data", "02_data_light"),
        ("model", "03_model_light"),
        ("parameters", "04_parameters_light"),
        ("identification", "05_identification_light"),
        ("calibration", "06_calibration_light"),
        ("diagnostics", "07_diagnostics_light"),
        ("uncertainty", "08_uncertainty_light"),
    ):
        window.navigate(key)
        window.resize(1440, 900)
        app.processEvents()
        _grab(app, window, OUT / f"{name}.png")

    # Dark theme screenshots
    window.theme.set_theme("dark")
    window.navigate("dashboard")
    app.processEvents()
    _grab(app, window, OUT / "09_dashboard_dark.png")
    window.navigate("calibration")
    app.processEvents()
    _grab(app, window, OUT / "10_calibration_dark.png")

    window.close()
    print("done")


if __name__ == "__main__":
    main()
