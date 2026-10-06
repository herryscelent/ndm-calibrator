from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "reference" / "web_screenshots"
STATE_WEB = ROOT / "reference" / "web_screenshots_states"
QT = ROOT / "screenshots_qt"
OUT = ROOT / "comparison"
OUT.mkdir(exist_ok=True)
STATE_OUT = OUT / "states"
STATE_OUT.mkdir(exist_ok=True)

PAIRS = [
    ("dashboard.png", "01_dashboard.png", "01_dashboard_compare.png"),
    ("data.png", "02_data.png", "02_data_compare.png"),
    ("model.png", "03_model.png", "03_model_compare.png"),
    ("parameters.png", "04_parameters.png", "04_parameters_compare.png"),
    ("identification.png", "05_identification_ready.png", "05_identification_ready_compare.png"),
    ("identification_completed.png", "07_identification_completed.png", "07_identification_completed_compare.png"),
    ("calibration.png", "08_calibration.png", "08_calibration_compare.png"),
    ("diagnostics_residuals.png", "09_diagnostics_residuals.png", "09_diagnostics_residuals_compare.png"),
    ("diagnostics_correlation.png", "10_diagnostics_correlation.png", "10_diagnostics_correlation_compare.png"),
    ("uncertainty_bootstrap.png", "11_uncertainty_bootstrap.png", "11_uncertainty_bootstrap_compare.png"),
    ("export.png", "12_export.png", "12_export_compare.png"),
]

STATE_PAIRS = [
    ("identification_advanced.png", "states/identification_advanced.png", "identification_advanced_compare.png"),
    ("identification_running.png", "06_identification_running.png", "identification_running_compare.png"),
    ("diagnostics_sensitivity.png", "states/diagnostics_sensitivity.png", "diagnostics_sensitivity_compare.png"),
    ("uncertainty.png", "states/uncertainty_multistart.png", "uncertainty_multistart_compare.png"),
    ("export_result.png", "states/export_completed.png", "export_completed_compare.png"),
]


def build_pair(web_dir: Path, web_name: str, qt_name: str, out_name: str, out_dir: Path) -> None:
    web = Image.open(web_dir / web_name).convert("RGB")
    qt = Image.open(QT / qt_name).convert("RGB")
    target_h = min(web.height, qt.height)
    web = web.resize((round(web.width * target_h / web.height), target_h))
    qt = qt.resize((round(qt.width * target_h / qt.height), target_h))
    header = 34
    canvas = Image.new("RGB", (web.width + qt.width, target_h + header), "white")
    canvas.paste(web, (0, header))
    canvas.paste(qt, (web.width, header))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 9), "Web Reference", fill="#20252B")
    draw.text((web.width + 12, 9), "PySide6", fill="#20252B")
    draw.line((web.width, 0, web.width, canvas.height), fill="#C9D2DC", width=2)
    canvas.save(out_dir / out_name)
    print(f"saved: {out_name}")


def main():
    for web_name, qt_name, out_name in PAIRS:
        build_pair(WEB, web_name, qt_name, out_name, OUT)
    for web_name, qt_name, out_name in STATE_PAIRS:
        build_pair(STATE_WEB, web_name, qt_name, out_name, STATE_OUT)


if __name__ == "__main__":
    main()
