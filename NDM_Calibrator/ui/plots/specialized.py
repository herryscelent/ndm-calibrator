"""Specific plot widgets built on BasePlot."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pyqtgraph as pg

from ui.design.colors import palette_for
from ui.plots.base_plot import BasePlot


class TimeSeriesPlot(BasePlot):
    """Simple line plot of one or more series (data preview)."""

    def __init__(self, title: str = "数据曲线", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "值")
        self.plot.setLabel("bottom", "时间")
        self._curves: list[pg.PlotDataItem] = []

    def plot_series(self, time: np.ndarray, series: Dict[str, np.ndarray]) -> None:
        self.clear()
        self._curves = []
        pal = self._pal()
        colors = [pal.plot_primary, pal.plot_secondary, pal.plot_residual, pal.success, pal.warning, pal.info]
        legend = self.plot.addLegend()
        for i, (name, y) in enumerate(series.items()):
            color = colors[i % len(colors)]
            pen = pg.mkPen(color, width=1.5)
            curve = self.plot.plot(time, y, pen=pen, name=name)
            self._curves.append(curve)
            legend.addItem(curve, name)
        self.plot.enableAutoRange(axis="xy", enable=True)
        self.plot.autoRange()


class MeasuredSimulatedPlot(BasePlot):
    """Measured vs simulated time series with a toggleable legend."""

    def __init__(self, title: str = "实测 vs 模拟", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "输出")
        self.plot.setLabel("bottom", "时间")

    def plot_fit(self, time, measured, simulated) -> None:
        self.clear()
        pal = self._pal()
        legend = self.plot.addLegend(offset=(10, 10))
        m = self.plot.plot(time, measured, pen=None, symbol="o", symbolSize=5,
                           symbolBrush=pg.mkBrush(pal.plot_measured), name="实测")
        s = self.plot.plot(time, simulated, pen=pg.mkPen(pal.plot_simulated, width=2), name="模拟")
        legend.addItem(m, "实测")
        legend.addItem(s, "模拟")
        self.plot.enableAutoRange(axis="xy", enable=True)
        self.plot.autoRange()


class ResidualPlot(BasePlot):
    """Residual time series (optionally with histogram)."""

    def __init__(self, title: str = "残差", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "残差")
        self.plot.setLabel("bottom", "时间")

    def plot_residuals(self, time, residual) -> None:
        self.clear()
        pal = self._pal()
        pen = pg.mkPen(pal.plot_residual, width=1.5)
        self.plot.plot(time, residual, pen=pen)
        # zero reference line
        zero = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen(pal.border_strong, style=pg.QtCore.Qt.PenStyle.DashLine))
        self.plot.addItem(zero)
        self.plot.enableAutoRange(axis="xy", enable=True)
        self.plot.autoRange()


class ConvergencePlot(BasePlot):
    """Convergence history (best objective over iterations)."""

    def __init__(self, title: str = "收敛过程", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "目标函数值")
        self.plot.setLabel("bottom", "迭代")

    def plot_history(self, history: List[float]) -> None:
        self.clear()
        if not history:
            return
        pal = self._pal()
        self.plot.plot(np.arange(len(history)), history, pen=pg.mkPen(pal.plot_primary, width=1.8))
        self.plot.enableAutoRange(axis="xy", enable=True)
        self.plot.autoRange()


class SensitivityPlot(BasePlot):
    """Horizontal bar chart of normalised sensitivity (PyQtGraph)."""

    def __init__(self, title: str = "参数敏感度", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "")
        self.plot.setLabel("bottom", "归一化敏感度 (RMS)")

    def plot_sensitivity(self, names: List[str], rms_values: List[float]) -> None:
        self.clear()
        pal = self._pal()
        y = np.arange(len(names))
        # Horizontal bar chart: each bar spans x in [0, rms] at row y.
        bars = pg.BarGraphItem(x0=0, x1=rms_values, y0=y, height=0.6, brush=pal.plot_primary)
        self.plot.addItem(bars)
        self.plot.getAxis("left").setTicks([[(i, n) for i, n in zip(y, names)]])
        self.plot.enableAutoRange(axis="xy", enable=True)
        self.plot.autoRange()


class CorrelationHeatmap(BasePlot):
    """Parameter correlation heatmap using an ImageItem."""

    def __init__(self, title: str = "参数相关性", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "")
        self.plot.setLabel("bottom", "")
        self.plot.getPlotItem().hideButtons()

    def plot_correlation(self, correlation: np.ndarray, names: List[str]) -> None:
        self.clear()
        # Build a diverging colormap: blue -> white -> red.
        colors = [
            (0.0, pg.mkColor("#3B6FB6")),
            (0.5, pg.mkColor("#FFFFFF")),
            (1.0, pg.mkColor("#C8593E")),
        ]
        cmap = pg.ColorMap(pos=[c[0] for c in colors], color=[c[1] for c in colors])
        lut = cmap.getLookupTable(0.0, 1.0, 256)
        img = pg.ImageItem()
        data = np.clip(correlation, -1, 1)
        img.setImage(data, autoLevels=False, levels=(-1, 1), lut=lut)
        img.setRect(pg.QtCore.QRectF(0, 0, len(names), len(names)))
        self.plot.addItem(img)
        self.plot.setXRange(0, len(names))
        self.plot.setYRange(0, len(names))
        self.plot.invertY(False)
        self.plot.getAxis("bottom").setTicks([[(i + 0.5, n) for i, n in enumerate(names)]])
        self.plot.getAxis("left").setTicks([[(i + 0.5, n) for i, n in enumerate(names)]])
        # Value labels
        for i in range(len(names)):
            for j in range(len(names)):
                txt = pg.TextItem(f"{data[i, j]:.2f}", color="#1F2328", anchor=(0.5, 0.5))
                txt.setPos(j + 0.5, i + 0.5)
                self.plot.addItem(txt)


class HistogramPlot(BasePlot):
    """Histogram of a distribution (bootstrap samples / stability)."""

    def __init__(self, title: str = "分布", theme_manager=None, parent=None):
        super().__init__(title, theme_manager, parent)
        self.plot.setLabel("left", "频数")
        self.plot.setLabel("bottom", "参数值")

    def plot_samples(self, samples, point_estimate: Optional[float] = None, interval=None) -> None:
        self.clear()
        pal = self._pal()
        arr = np.asarray(samples, dtype=float)
        if arr.size == 0:
            return
        hist, edges = np.histogram(arr, bins=min(30, max(10, arr.size // 4)))
        bars = pg.BarGraphItem(x=edges[:-1] + np.diff(edges) / 2, height=hist, width=np.diff(edges) * 0.9,
                               brush=pal.plot_primary)
        self.plot.addItem(bars)
        if point_estimate is not None:
            vline = pg.InfiniteLine(pos=point_estimate, angle=90, pen=pg.mkPen(pal.danger, width=2))
            self.plot.addItem(vline)
        if interval is not None:
            lo, hi = interval
            span = pg.LinearRegionItem(values=(lo, hi), brush=pg.mkBrush(255, 165, 0, 40), movable=False)
            self.plot.addItem(span)
        self.plot.enableAutoRange(axis="xy", enable=True)
        self.plot.autoRange()
