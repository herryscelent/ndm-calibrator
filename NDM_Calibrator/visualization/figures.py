"""Static figure generation with Matplotlib (publication-friendly, white bg).

Application-interactive plots use PyQtGraph (ui/plots); this module produces
Matplotlib figures for report/export. It is kept decoupled from the Qt UI.
"""

from __future__ import annotations

from typing import Dict, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Segoe UI"]
plt.rcParams["axes.unicode_minus"] = False


def fit_figure(time, measured: Dict[str, np.ndarray], simulated: Dict[str, np.ndarray]) -> plt.Figure:
    """Measured vs simulated time series figure."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for name in measured:
        ax.plot(time, measured[name], "o", ms=3, label=f"{name} 实测")
        ax.plot(time, simulated[name], "-", lw=1.5, label=f"{name} 模拟")
    ax.set_xlabel("时间")
    ax.set_ylabel("输出")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def residual_figure(time, residual: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(time, residual, lw=1)
    ax.axhline(0, color="gray", ls="--", lw=0.8)
    ax.set_xlabel("时间")
    ax.set_ylabel("残差")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def correlation_heatmap_figure(correlation: np.ndarray, names) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(correlation, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(names)), names)
    ax.set_yticks(range(len(names)), names)
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, f"{correlation[i][j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    return fig


def histogram_figure(samples: np.ndarray, title: str = "分布") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(samples, bins=min(30, max(10, len(samples) // 4)), color="#4DA3E8", alpha=0.85)
    ax.set_xlabel("参数值")
    ax.set_ylabel("频数")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig
