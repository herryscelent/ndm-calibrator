"""Figure export using Matplotlib (publication-friendly, white background)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Segoe UI"]
plt.rcParams["axes.unicode_minus"] = False

from core.exceptions import NDMCError
from core.project import Project


def export_figures(project: Project, dest_dir: Path | str, checks: Dict[str, bool] | None = None) -> list[str]:
    """Export fit, residual, sensitivity, correlation and bootstrap figures
    as PNG files. Returns list of written paths."""
    dest_dir = Path(dest_dir)
    if not dest_dir.exists():
        raise NDMCError(f"目标目录不存在: {dest_dir}")
    out = []

    def enabled(key: str) -> bool:
        return checks is None or checks.get(key, True)

    if project.experiment is None or project.model is None:
        return out

    entry = project.results.get("identification", {})
    params = entry.get("result", {}).get("parameters")
    cal = project.results.get("calibration", {})

    # Fit figure
    if params and enabled("simulation"):
        try:
            from identification.base import build_context

            ctx = build_context(project)
            theta = np.array([params[n] for n in ctx.free_names], dtype=float)
            predicted = ctx.predict_outputs(theta)
            fig, ax = plt.subplots(figsize=(8, 4))
            for i, o in enumerate(project.model.outputs):
                measured = ctx.measured_outputs()[o]
                ax.plot(project.experiment.time, measured, "o", ms=3, label=f"{o} 实测")
                ax.plot(project.experiment.time, predicted[o], "-", lw=1.5, label=f"{o} 模拟")
            ax.set_xlabel("时间")
            ax.set_ylabel("输出")
            ax.legend()
            ax.grid(alpha=0.3)
            fig.tight_layout()
            p = dest_dir / "fit.png"
            fig.savefig(p, dpi=150)
            plt.close(fig)
            out.append(str(p))
        except Exception:
            pass

    # Residual figure
    if cal.get("residuals") and project.model.outputs and enabled("residuals"):
        fig, ax = plt.subplots(figsize=(8, 3))
        o = project.model.outputs[0]
        ax.plot(project.experiment.time, cal["residuals"][o], lw=1)
        ax.axhline(0, color="gray", ls="--", lw=0.8)
        ax.set_xlabel("时间")
        ax.set_ylabel("残差")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        p = dest_dir / "residual.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        out.append(str(p))

    # Correlation heatmap
    corr = cal.get("identifiability", {}).get("correlation")
    names = cal.get("identifiability", {}).get("parameter_names", [])
    if corr and names and enabled("diagnostics"):
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(names)), names)
        ax.set_yticks(range(len(names)), names)
        for i in range(len(names)):
            for j in range(len(names)):
                ax.text(j, i, f"{corr[i][j]:.2f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        p = dest_dir / "correlation.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        out.append(str(p))

    if enabled("diagnostics"):
        sensitivity = cal.get("sensitivity", {}).get("summary", {})
        if sensitivity:
            ordered = sorted(
                sensitivity.items(),
                key=lambda item: float(item[1].get("rms", 0.0)) if isinstance(item[1], dict) else float(item[1]),
                reverse=True,
            )
            fig, ax = plt.subplots(figsize=(7, 4))
            labels = [name for name, _ in ordered]
            values = [float(info.get("rms", 0.0)) if isinstance(info, dict) else float(info) for _, info in ordered]
            ax.barh(labels[::-1], values[::-1], color="#5F6B78")
            ax.set_xlabel("RMS sensitivity")
            fig.tight_layout()
            p = dest_dir / "sensitivity.png"
            fig.savefig(p, dpi=150)
            plt.close(fig)
            out.append(str(p))

        singular = cal.get("identifiability", {}).get("singular_values", [])
        if singular:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(np.arange(1, len(singular) + 1), singular, color="#356FE5")
            ax.set_xlabel("Index")
            ax.set_ylabel("Singular value")
            fig.tight_layout()
            p = dest_dir / "identifiability.png"
            fig.savefig(p, dpi=150)
            plt.close(fig)
            out.append(str(p))

    return out
