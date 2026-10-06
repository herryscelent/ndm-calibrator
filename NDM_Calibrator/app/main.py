"""Application entry point.

Usage: python -m app.main
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.constants import APP_NAME_EN, APP_NAME_CN, APP_VERSION

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def _setup_logging() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(_LOG_DIR / "app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
    )


def main() -> int:
    _setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("%s %s (%s) 启动", APP_NAME_CN, APP_VERSION, APP_NAME_EN)

    try:
        from ui_v2.main_window import MainWindow
        from ui_v2.theme import apply_theme
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:
        logger.error("GUI 依赖缺失: %s", exc)
        print(f"缺少 PySide6, 请先执行: pip install -r requirements.txt ({exc})")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME_EN)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("NDM-Calibrator")
    apply_theme(app)

    window = MainWindow()
    window.show()
    exit_code = app.exec()
    logger.info("软件退出, code=%s", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
