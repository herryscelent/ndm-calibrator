"""Line icon set rendered with QPainter (no external assets, no emoji).

Icons follow a single visual language: 1.5px strokes, rounded caps/joins,
24x24 grid. Each icon is drawn programmatically so it adapts to theme color.
"""

from __future__ import annotations

import math
from typing import Callable, Dict

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

_ICON_SIZE = 24
_STROKE = 1.5


def _path_icon(draw: Callable[[QPainter], None]) -> QIcon:
    """Build an icon by invoking `draw` on a painter for a single pixmap."""

    def _render(color: QColor) -> QIcon:
        pm = QPixmap(_ICON_SIZE, _ICON_SIZE)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(color, _STROKE, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(QBrush())
        draw(p)
        p.end()
        return QIcon(pm)

    return _render


def _make_icon(name: str, draw: Callable[[QPainter], None]) -> None:
    _ICONS[name] = _path_icon(draw)


_ICONS: Dict[str, Callable[[QColor], QIcon]] = {}


def _line(p: QPainter, x1, y1, x2, y2):
    p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


# --- Icon definitions ------------------------------------------------ #
def _dashboard(p):
    p.drawRect(QRectF(4, 4, 16, 16))
    _line(p, 4, 12, 12, 12)
    _line(p, 12, 4, 12, 20)
    p.drawRect(QRectF(15, 15, 5, 5))


def _data(p):
    p.drawRect(QRectF(4, 4, 16, 16))
    for y in (9.5, 15):
        _line(p, 5, y, 19, y)


def _model(p):
    # graph nodes
    for cx, cy in ((7, 17), (17, 17), (7, 7), (17, 7)):
        p.drawEllipse(QRectF(cx - 1.5, cy - 1.5, 3, 3))
    _line(p, 8.5, 16, 15.5, 8.5)
    _line(p, 8.5, 8.5, 15.5, 15.5)


def _parameters(p):
    p.drawEllipse(QRectF(4.5, 4.5, 6, 6))
    _line(p, 9.5, 12, 20, 12)
    p.drawEllipse(QRectF(14, 15, 6, 6))
    _line(p, 4, 15, 13, 15)


def _identify(p):
    # target + magnifier
    p.drawEllipse(QRectF(5, 5, 10, 10))
    p.drawEllipse(QRectF(8, 8, 4, 4))
    _line(p, 13.5, 13.5, 20, 20)


def _calibrate(p):
    # gauge
    p.drawArc(QRectF(4, 4, 16, 16), 20 * 16, 140 * 16)
    _line(p, 12, 12, 16, 8)
    _line(p, 8, 12, 8, 20)
    _line(p, 16, 12, 16, 20)


def _diagnostics(p):
    # activity pulse
    _line(p, 2, 12, 7, 12)
    _line(p, 7, 12, 9, 7)
    _line(p, 9, 7, 11, 17)
    _line(p, 11, 17, 13, 12)
    _line(p, 13, 12, 22, 12)


def _uncertainty(p):
    # bell curve
    path = QPainterPath()
    path.moveTo(3, 17)
    path.cubicTo(8, 8, 16, 8, 21, 17)
    p.drawPath(path)
    _line(p, 3, 20, 21, 20)


def _export(p):
    # arrow out of tray
    _line(p, 12, 4, 12, 13)
    _line(p, 8, 8, 12, 4)
    _line(p, 16, 8, 12, 4)
    p.drawRect(QRectF(4, 14, 16, 6))


def _settings(p):
    # gear approximation: circle + spokes
    p.drawEllipse(QRectF(8, 8, 8, 8))
    for ang in range(0, 360, 60):
        rad = math.radians(ang)
        x1, y1 = 12 + 4.5 * math.cos(rad), 12 + 4.5 * math.sin(rad)
        x2, y2 = 12 + 6.5 * math.cos(rad), 12 + 6.5 * math.sin(rad)
        _line(p, x1, y1, x2, y2)


def _about(p):
    # info circle
    p.drawEllipse(QRectF(4, 4, 16, 16))
    _line(p, 12, 11, 12, 16)
    p.drawEllipse(QRectF(11.5, 7.5, 1, 1))


def _folder(p):
    p.drawRect(QRectF(4, 6, 16, 13))
    _line(p, 4, 9, 20, 9)


def _save(p):
    p.drawRect(QRectF(4, 4, 16, 16))
    _line(p, 8, 4, 8, 10)
    _line(p, 8, 10, 16, 10)
    _line(p, 16, 10, 16, 20)
    _line(p, 8, 14, 16, 14)


def _sun(p):
    p.drawEllipse(QRectF(9, 9, 6, 6))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1, y1 = 12 + 6.5 * math.cos(rad), 12 + 6.5 * math.sin(rad)
        x2, y2 = 12 + 9 * math.cos(rad), 12 + 9 * math.sin(rad)
        _line(p, x1, y1, x2, y2)


def _moon(p):
    path = QPainterPath()
    path.moveTo(15, 5)
    path.arcTo(QRectF(6, 5, 13, 13), 0, 180)
    p.drawPath(path)


def _check(p):
    _line(p, 5, 13, 10, 18)
    _line(p, 10, 18, 19, 6)


def _check_circle(p):
    p.drawEllipse(QRectF(4, 4, 16, 16))
    _line(p, 7, 12, 10.5, 15.5)
    _line(p, 10.5, 15.5, 17, 8.5)


def _warn(p):
    # triangle
    path = QPainterPath()
    path.moveTo(12, 4)
    path.lineTo(21, 20)
    path.lineTo(3, 20)
    path.closeSubpath()
    p.drawPath(path)
    _line(p, 12, 10, 12, 15)


def _error(p):
    p.drawEllipse(QRectF(5, 5, 14, 14))
    _line(p, 9.5, 9.5, 14.5, 14.5)
    _line(p, 14.5, 9.5, 9.5, 14.5)


def _play(p):
    path = QPainterPath()
    path.moveTo(8, 5)
    path.lineTo(19, 12)
    path.lineTo(8, 19)
    path.closeSubpath()
    p.drawPath(path)


def _stop(p):
    p.drawRect(QRectF(7, 7, 10, 10))


def _search(p):
    p.drawEllipse(QRectF(5, 5, 10, 10))
    _line(p, 13, 13, 20, 20)


def _reset(p):
    # circular arrow
    p.drawArc(QRectF(5, 5, 14, 14), 30 * 16, 280 * 16)
    path = QPainterPath()
    path.moveTo(18, 6)
    path.lineTo(20, 10)
    path.lineTo(16, 11)
    path.closeSubpath()
    p.drawPath(path)


def _export_image(p):
    p.drawRect(QRectF(4, 5, 16, 14))
    _line(p, 4, 13, 8, 9)
    _line(p, 8, 9, 13, 14)
    _line(p, 13, 14, 16, 11)
    _line(p, 16, 11, 20, 15)


def _eye(p):
    # crosshair / view
    _line(p, 12, 3, 12, 6)
    _line(p, 12, 18, 12, 21)
    _line(p, 3, 12, 6, 12)
    _line(p, 18, 12, 21, 12)
    p.drawEllipse(QRectF(8, 8, 8, 8))


def _plus(p):
    _line(p, 12, 5, 12, 19)
    _line(p, 5, 12, 19, 12)


def _trash(p):
    p.drawRect(QRectF(6, 8, 12, 12))
    _line(p, 4, 8, 20, 8)
    _line(p, 9, 4, 15, 4)
    _line(p, 10, 12, 10, 17)
    _line(p, 14, 12, 14, 17)


for _name, _fn in {
    "dashboard": _dashboard,
    "data": _data,
    "model": _model,
    "parameters": _parameters,
    "identify": _identify,
    "calibrate": _calibrate,
    "diagnostics": _diagnostics,
    "uncertainty": _uncertainty,
    "export": _export,
    "settings": _settings,
    "about": _about,
    "folder": _folder,
    "save": _save,
    "sun": _sun,
    "moon": _moon,
    "check": _check,
    "check_circle": _check_circle,
    "warn": _warn,
    "error": _error,
    "play": _play,
    "stop": _stop,
    "search": _search,
    "reset": _reset,
    "export_image": _export_image,
    "eye": _eye,
    "plus": _plus,
    "trash": _trash,
}.items():
    _make_icon(_name, _fn)


def icon(name: str, color: str | None = None) -> QIcon:
    """Return a themed line icon.

    ``color`` is a hex string; when None a default neutral color is used
    (callers should pass a theme-aware color).
    """
    factory = _ICONS.get(name)
    if factory is None:
        raise KeyError(f"未知图标: {name}")
    base = QColor(color or "#57606A")
    return factory(base)
