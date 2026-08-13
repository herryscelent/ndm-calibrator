"""Base PyQtGraph plot panel with theme support and a standard toolbar.

Interactive plots in the app use PyQtGraph; Matplotlib is reserved for
report/export figures.
"""

from __future__ import annotations

from typing import Optional

import pyqtgraph as pg
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QVBoxLayout, QWidget

from ui.design.colors import palette_for
from ui.design.icons import icon

pg.setConfigOptions(antialias=True)


class BasePlot(QWidget):
    """A themed PlotWidget with a compact toolbar (reset/auto-range/export)."""

    def __init__(self, title: str = "", theme_manager=None, parent=None):
        super().__init__(parent)
        self._theme_manager = theme_manager
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.plot = pg.PlotWidget(self)
        self.plot.setBackground("transparent")
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.plot.setMenuEnabled(False)
        self._default_title = title
        if title:
            self.plot.setTitle(title, size="11pt")
        self.plot.setLabel("left", "值")
        self.plot.setLabel("bottom", "时间")

        self._legend = None
        self._crosshair = None
        lay.addWidget(self.plot, 1)

        self._build_toolbar(lay)

    def _build_toolbar(self, parent_lay) -> None:
        bar = QHBoxLayout()
        bar.setSpacing(4)
        self.actions = {}
        for key, ico, tip in (
            ("reset", "reset", "重置视图"),
            ("auto", "eye", "自动范围"),
            ("crosshair", "search", "十字线"),
            ("export", "export_image", "导出 PNG"),
        ):
            btn = QToolButton(self)
            btn.setObjectName("IconButton")
            btn.setToolTip(tip)
            btn.setAccessibleName(tip)
            btn.clicked.connect(lambda _, k=key: self._action(k))
            self.actions[key] = btn
            bar.addWidget(btn)
        bar.addStretch(1)
        parent_lay.addLayout(bar)

    def _action(self, key: str) -> None:
        if key == "reset":
            self.plot.enableAutoRange(axis="xy", enable=True)
            self.plot.autoRange()
        elif key == "auto":
            self.plot.enableAutoRange(axis="xy", enable=True)
            self.plot.autoRange()
        elif key == "crosshair":
            self._toggle_crosshair()
        elif key == "export":
            self.export_png()

    def _toggle_crosshair(self) -> None:
        if self._crosshair is None:
            self._crosshair = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(self._pal().border_strong, width=1, style=Qt.PenStyle.DashLine))
            self.plot.addItem(self._crosshair)
        else:
            self.plot.removeItem(self._crosshair)
            self._crosshair = None

    def _pal(self):
        return palette_for(self._theme_manager.theme if self._theme_manager else "light")

    def export_png(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(self, "导出图片", "plot.png", "PNG 图片 (*.png);;SVG (*.svg)")
        if path:
            if path.lower().endswith(".svg"):
                self.plot.show()
            self.plot.grab().save(path)

    def set_labels(self, x: str, y: str) -> None:
        self.plot.setLabel("bottom", x)
        self.plot.setLabel("left", y)

    def clear(self) -> None:
        self.plot.clear()
        if self._default_title:
            self.plot.setTitle(self._default_title, size="11pt")

    def apply_theme(self) -> None:
        pal = self._pal()
        self.plot.getAxis("left").setPen(pg.mkPen(pal.text_secondary))
        self.plot.getAxis("bottom").setPen(pg.mkPen(pal.text_secondary))
        self.plot.getAxis("left").setTextPen(pg.mkPen(pal.text_secondary))
        self.plot.getAxis("bottom").setTextPen(pg.mkPen(pal.text_secondary))
