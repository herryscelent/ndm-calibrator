"""Typography helpers (font construction from tokens)."""

from __future__ import annotations

from PySide6.QtGui import QFont

from ui.design.tokens import FONT_FAMILY, TYPE


def font(size: str = "body", bold: bool = False, mono: bool = False) -> QFont:
    f = QFont(FONT_MONO if mono else FONT_SANS)
    f.setPixelSize(TYPE[size])
    f.setWeight(QFont.Weight.DemiBold if bold else QFont.Weight.Normal)
    return f


FONT_SANS = FONT_FAMILY["sans"]
FONT_MONO = FONT_FAMILY["mono"]
