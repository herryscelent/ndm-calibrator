"""CSV export for individual result tables."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from core.exceptions import NDMCError
from core.project import Project


def export_csv(project: Project, dest_dir: Path | str) -> list[str]:
    """Export parameters, simulated series, residuals and bootstrap samples
    as separate CSV files. Returns list of written paths."""
    dest_dir = Path(dest_dir)
    if not dest_dir.exists():
        raise NDMCError(f"目标目录不存在: {dest_dir}")
    out = []
    result = project.results

    # Parameters
    if project.parameters:
        rows = [{"参数": p.name, "初值": p.initial, "下限": p.lower, "上限": p.upper,
                 "状态": "待辨识" if p.free else "固定"} for p in project.parameters]
        p = dest_dir / "parameters.csv"
        pd.DataFrame(rows).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    # Simulation
    sim_path = dest_dir / "simulation.csv"
    if project.experiment is not None:
        df = pd.DataFrame({"time": project.experiment.time})
        for name, arr in project.experiment.inputs.items():
            df[f"{name}"] = arr
        for name, arr in project.experiment.outputs.items():
            df[f"{name}_measured"] = arr
        entry = project.results.get("identification", {})
        params = entry.get("result", {}).get("parameters")
        if params:
            try:
                from identification.base import build_context

                ctx = build_context(project)
                theta = __import__("numpy").array([params[n] for n in ctx.free_names], dtype=float)
                predicted = ctx.predict_outputs(theta)
                for o in project.model.outputs:
                    df[f"{o}_simulated"] = predicted[o]
            except Exception:
                pass
        df.to_csv(sim_path, index=False, encoding="utf-8")
        out.append(str(sim_path))

    # Residuals
    cal = result.get("calibration", {})
    for o, res in cal.get("residuals", {}).items():
        p = dest_dir / f"residuals_{o}.csv"
        pd.DataFrame({"residual": res}).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    # Bootstrap samples
    boot = result.get("bootstrap", {})
    for name, info in boot.get("parameters", {}).items():
        p = dest_dir / f"bootstrap_{name}.csv"
        pd.DataFrame({"sample": info.get("samples", [])}).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    return out
