"""Theme manager: applies Light/Dark palettes, QSS, icons and plot themes.

Switching themes is immediate (no restart). The theme choice is persisted via
QSettings.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget

from ui.design.colors import ColorPalette, palette_for

logger = logging.getLogger(__name__)


class ThemeManager:
    """Centralised theme state and application."""

    def __init__(self, app: QApplication, default_theme: str = "light"):
        self._app = app
        self._theme = default_theme
        self._qss = self._load_qss()
        self._settings = QSettings("NDM-Calibrator", "NDM-Calibrator")
        restored = self._settings.value("theme", default_theme)
        if restored in ("light", "dark", "system"):
            self._theme = restored
        self._current: str = "light"

    @property
    def theme(self) -> str:
        return self._current

    @property
    def palette(self) -> ColorPalette:
        return palette_for(self._current)

    def is_dark(self) -> bool:
        return self._current == "dark"

    def _load_qss(self) -> str:
        parts = []
        qss_dir = Path(__file__).resolve().parent.parent / "styles"
        for fname in ("base.qss", "light.qss", "dark.qss", "tables.qss", "forms.qss", "navigation.qss"):
            path = qss_dir / fname
            if path.exists():
                parts.append(path.read_text(encoding="utf-8"))
        return "\n".join(parts)

    def _resolve_theme(self) -> str:
        if self._theme == "system":
            return "dark" if self._app.styleHints().colorScheme() == Qt.ColorScheme.Dark else "light"
        return self._theme

    def apply(self) -> None:
        self._current = self._resolve_theme()
        pal = palette_for(self._current)
        self._apply_palette(pal)
        qss = self._qss.replace("__TOKENS__", self._token_css(pal))
        self._app.setStyleSheet(qss)
        # Qt style hint for scrollbars / focus.
        self._app.setStyle("Fusion")
        self._app.style().unpolish(self._app)
        self._app.style().polish(self._app)
        logger.info("Theme applied: %s", self._current)

    def _token_css(self, pal: ColorPalette) -> str:
        return (
            f"@bg={pal.background};@surface={pal.surface};@surface2={pal.surface_secondary};"
            f"@hover={pal.surface_hover};@border={pal.border};@border_strong={pal.border_strong};"
            f"@text={pal.text_primary};@text2={pal.text_secondary};@disabled={pal.text_disabled};"
            f"@accent={pal.accent};@accent_hover={pal.accent_hover};@accent_pressed={pal.accent_pressed};"
            f"@accent_text={pal.accent_text};@success={pal.success};@warning={pal.warning};"
            f"@danger={pal.danger};@info={pal.info};@input_bg={pal.input_bg};"
            f"@focus={pal.input_focus_border};@selection={pal.selection_bg};@tooltip={pal.tooltip_bg};"
        )

    def _apply_palette(self, pal: ColorPalette) -> None:
        qp = QPalette()
        qp.setColor(QPalette.ColorRole.Window, QColor(pal.background))
        qp.setColor(QPalette.ColorRole.WindowText, QColor(pal.text_primary))
        qp.setColor(QPalette.ColorRole.Base, QColor(pal.surface))
        qp.setColor(QPalette.ColorRole.AlternateBase, QColor(pal.table_alt_row))
        qp.setColor(QPalette.ColorRole.Text, QColor(pal.text_primary))
        qp.setColor(QPalette.ColorRole.Button, QColor(pal.surface_secondary))
        qp.setColor(QPalette.ColorRole.ButtonText, QColor(pal.text_primary))
        qp.setColor(QPalette.ColorRole.Highlight, QColor(pal.accent))
        qp.setColor(QPalette.ColorRole.HighlightedText, QColor(pal.accent_text))
        qp.setColor(QPalette.ColorRole.ToolTipBase, QColor(pal.tooltip_bg))
        qp.setColor(QPalette.ColorRole.ToolTipText, QColor(pal.background))
        qp.setColor(QPalette.ColorRole.PlaceholderText, QColor(pal.text_disabled))
        self._app.setPalette(qp)

    def set_theme(self, theme: str) -> None:
        if theme not in ("light", "dark", "system"):
            raise ValueError(f"未知主题: {theme}")
        self._theme = theme
        self._settings.setValue("theme", theme)
        self.apply()

    def toggle(self) -> str:
        nxt = "dark" if self._current == "light" else "light"
        self.set_theme(nxt)
        return self._current
