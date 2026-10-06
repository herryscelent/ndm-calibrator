from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .main_window import MainWindow
from .theme import apply_theme


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("NDM Calibrator")
    apply_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
