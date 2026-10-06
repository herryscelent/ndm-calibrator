from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QWidget

from . import tokens as t

pg.setConfigOptions(antialias=True, background=t.SURFACE, foreground=t.TEXT_SECONDARY)


class EngineeringPlot(QWidget):
    def __init__(self, x_label: str = "", y_label: str = "", minimum_height: int = 220):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.plot = pg.PlotWidget()
        self.plot.setMinimumHeight(minimum_height)
        self.plot.setBackground(t.SURFACE)
        self.plot.showGrid(x=True, y=True, alpha=.14)
        self.plot.setMenuEnabled(False)
        self.plot.setMouseEnabled(x=True, y=True)
        self.plot.getPlotItem().setContentsMargins(4, 4, 4, 4)
        self.plot.setLabel("bottom", x_label)
        self.plot.setLabel("left", y_label)
        axis_font = QFont("Microsoft YaHei UI", 8)
        for axis_name in ("left", "bottom"):
            axis = self.plot.getAxis(axis_name)
            axis.setTickFont(axis_font)
            axis.setPen(pg.mkPen(t.BORDER_STRONG))
            axis.setTextPen(pg.mkPen(t.TEXT_SECONDARY))
        self._data_items = []
        self._default_x_range: tuple[float, float] | None = None
        crosshair_pen = pg.mkPen(t.BORDER_STRONG, width=1, style=Qt.PenStyle.DashLine)
        self._crosshair_x = pg.InfiniteLine(angle=90, movable=False, pen=crosshair_pen)
        self._crosshair_y = pg.InfiniteLine(angle=0, movable=False, pen=crosshair_pen)
        for overlay in (self._crosshair_x, self._crosshair_y):
            overlay.hide()
            self.plot.addItem(overlay, ignoreBounds=True)
        self.plot.scene().sigMouseMoved.connect(self._mouse_moved)
        layout.addWidget(self.plot)

    def line(self, x, y, color: str, name: str = "", width: float = 1.8):
        if name and self.plot.plotItem.legend is None:
            self.plot.addLegend(
                offset=(10, 10),
                labelTextColor=t.TEXT_SECONDARY,
                brush=pg.mkBrush(255, 255, 255, 220),
                pen=pg.mkPen(t.BORDER),
            )
        item = self.plot.plot(x, y, pen=pg.mkPen(color, width=width), name=name or None)
        self._data_items.append(item)
        return item

    def bars(self, x, height, color: str, width: float = .7):
        item = pg.BarGraphItem(x=x, height=height, width=width, brush=color, pen=pg.mkPen(color))
        self.plot.addItem(item)
        self._data_items.append(item)
        return item

    def horizontal_bars(self, y, width, color: str, height: float = .55):
        item = pg.BarGraphItem(x0=0, y=y, width=width, height=height, brush=color, pen=pg.mkPen(color))
        self.plot.addItem(item)
        self._data_items.append(item)
        return item

    def set_default_x_range(self, minimum: float, maximum: float) -> None:
        self._default_x_range = (minimum, maximum)
        self.plot.setXRange(minimum, maximum, padding=0)

    def reset_view(self) -> None:
        self.plot.enableAutoRange()
        self.plot.autoRange()
        if self._default_x_range:
            self.plot.setXRange(*self._default_x_range, padding=0)

    def _mouse_moved(self, scene_position) -> None:
        if not self.plot.sceneBoundingRect().contains(scene_position):
            for overlay in (self._crosshair_x, self._crosshair_y):
                overlay.hide()
            return
        point = self.plot.plotItem.vb.mapSceneToView(scene_position)
        self._crosshair_x.setPos(point.x())
        self._crosshair_y.setPos(point.y())
        self.plot.setToolTip(f"x {point.x():.3g}   y {point.y():.3g}")
        for overlay in (self._crosshair_x, self._crosshair_y):
            overlay.show()

    def clear(self):
        for item in self._data_items:
            self.plot.removeItem(item)
        self._data_items.clear()
        legend = self.plot.plotItem.legend
        if legend is not None:
            legend.clear()
