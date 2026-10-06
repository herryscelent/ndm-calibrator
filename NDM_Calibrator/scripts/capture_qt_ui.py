from __future__ import annotations

import os
import hashlib
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source" if (ROOT / "source" / "ui_v2").exists() else ROOT
sys.path.insert(0, str(SOURCE_ROOT))

from ui_v2.main_window import MainWindow
from ui_v2.theme import apply_theme


OUT = ROOT / "screenshots_qt"
OUT.mkdir(exist_ok=True)
STATE_OUT = OUT / "states"
STATE_OUT.mkdir(exist_ok=True)


def render_png(window: MainWindow) -> bytes:
    pixmap = window.grab()
    if pixmap.isNull() or pixmap.width() < 100 or pixmap.height() < 100:
        raise RuntimeError("Qt 窗口截图为空或尺寸异常")
    image = pixmap.toImage()
    samples = [
        image.pixelColor(x, y).rgba()
        for x in range(0, image.width(), max(1, image.width() // 24))
        for y in range(0, image.height(), max(1, image.height() // 16))
    ]
    # A valid page can legitimately use only a handful of colors (for
    # example, a text-heavy model page).  Counting distinct colors therefore
    # produces false positives.  A genuinely blank grab is nearly uniform;
    # compare samples with the corner background instead.
    background = samples[0]
    if len(set(samples)) < 2 or sum(color != background for color in samples) < 8:
        raise RuntimeError("Qt 窗口截图近似空白")
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not pixmap.save(buffer, "PNG"):
        raise RuntimeError("Qt 截图编码失败")
    return bytes(buffer.data())


def stable_frame(
    window: MainWindow,
    app: QApplication,
    timeout: float = 4.0,
    stable_frames: int = 3,
) -> bytes:
    deadline = time.monotonic() + timeout
    previous = None
    matched = 0
    last_frame = b""
    while time.monotonic() < deadline:
        app.processEvents()
        last_frame = render_png(window)
        digest = hashlib.sha256(last_frame).digest()
        if digest == previous:
            matched += 1
            if matched >= stable_frames:
                return last_frame
        else:
            previous = digest
            matched = 0
        time.sleep(.04)
    raise TimeoutError("Qt 页面在截图超时前未达到连续稳定帧")


def capture(window: MainWindow, app: QApplication, route: str, filename: str, out_dir: Path = OUT):
    window.navigate(route)
    frame = stable_frame(window, app)
    path = out_dir / filename
    path.write_bytes(frame)
    print(f"saved: {path.name}")


def main():
    app = QApplication.instance() or QApplication([])
    apply_theme(app)
    window = MainWindow()
    window.resize(1440, 900)
    window.show()
    stable_frame(window, app)

    capture(window, app, "dashboard", "01_dashboard.png")
    capture(window, app, "data", "02_data.png")
    capture(window, app, "model", "03_model.png")
    capture(window, app, "parameters", "04_parameters.png")
    capture(window, app, "identification", "05_identification_ready.png")

    identification = window.pages["identification"]
    identification.advanced_toggle.setChecked(True)
    identification.toggle_advanced(True)
    capture(window, app, "identification", "identification_advanced.png", STATE_OUT)
    identification.advanced_toggle.setChecked(False)
    identification.toggle_advanced(False)
    identification.show_running_snapshot(3)
    capture(window, app, "identification", "06_identification_running.png")
    identification.complete_mock()
    capture(window, app, "identification", "07_identification_completed.png")

    capture(window, app, "calibration", "08_calibration.png")
    capture(window, app, "diagnostics", "09_diagnostics_residuals.png")
    window.pages["diagnostics"].tabs.setCurrentIndex(1)
    capture(window, app, "diagnostics", "diagnostics_sensitivity.png", STATE_OUT)
    window.pages["diagnostics"].tabs.setCurrentIndex(3)
    capture(window, app, "diagnostics", "10_diagnostics_correlation.png")
    window.pages["uncertainty"].tabs.setCurrentIndex(0)
    capture(window, app, "uncertainty", "uncertainty_multistart.png", STATE_OUT)
    window.pages["uncertainty"].tabs.setCurrentIndex(1)
    capture(window, app, "uncertainty", "11_uncertainty_bootstrap.png")
    capture(window, app, "export", "12_export.png")
    window.pages["export"].run_export()
    capture(window, app, "export", "export_completed.png", STATE_OUT)
    window.close()


if __name__ == "__main__":
    main()
