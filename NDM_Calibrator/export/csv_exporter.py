"""CSV export for individual result tables."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from core.exceptions import NDMCError
from core.project import Project


def export_csv(project: Project, dest_dir: Path | str, checks: Dict[str, bool] | None = None) -> list[str]:
    """Export parameters, simulated series, residuals and bootstrap samples
    as separate CSV files.  ``checks`` mirrors the export page's content
    toggles; omitted values default to enabled for backwards compatibility.
    Returns list of written paths."""
    dest_dir = Path(dest_dir)
    if not dest_dir.exists():
        raise NDMCError(f"目标目录不存在: {dest_dir}")
    out = []
    result = project.results

    def enabled(key: str) -> bool:
        return checks is None or checks.get(key, True)

    if enabled("summary"):
        summary = [{
            "项目名称": project.name,
            "描述": project.description,
            "数据来源": project.data_source or "",
            "样本数": project.experiment.n_points if project.experiment is not None else 0,
            "输入数": project.experiment.n_inputs if project.experiment is not None else 0,
            "输出数": project.experiment.n_outputs if project.experiment is not None else 0,
            "参数数": len(project.parameters),
        }]
        p = dest_dir / "summary.csv"
        pd.DataFrame(summary).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    # Parameters
    if enabled("parameters") and project.parameters:
        rows = [{"参数": p.name, "初值": p.initial, "下限": p.lower, "上限": p.upper,
                 "状态": "待辨识" if p.free else "固定"} for p in project.parameters]
        p = dest_dir / "parameters.csv"
        pd.DataFrame(rows).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    if enabled("metrics"):
        metrics = project.results.get("calibration", {}).get("metrics", {})
        rows = []
        for output, values in metrics.items():
            if isinstance(values, dict):
                rows.extend({"输出": output, "指标": key, "值": value} for key, value in values.items())
        if rows:
            p = dest_dir / "metrics.csv"
            pd.DataFrame(rows).to_csv(p, index=False, encoding="utf-8")
            out.append(str(p))

    # Simulation
    sim_path = dest_dir / "simulation.csv"
    if enabled("simulation") and project.experiment is not None:
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
    if enabled("residuals"):
        residual_items = cal.get("residuals", {}).items()
    else:
        residual_items = ()
    for o, res in residual_items:
        p = dest_dir / f"residuals_{o}.csv"
        pd.DataFrame({"residual": res}).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    if enabled("diagnostics"):
        ident = cal.get("identifiability", {}) if isinstance(cal, dict) else {}
        rows = [{"类别": "identifiability", "指标": key, "值": value}
                for key, value in ident.items() if key not in ("correlation", "singular_values")]
        for index, value in enumerate(ident.get("singular_values", []) if isinstance(ident, dict) else []):
            rows.append({"类别": "singular_value", "指标": str(index + 1), "值": value})
        for name, info in (cal.get("sensitivity", {}).get("summary", {}) if isinstance(cal, dict) else {}).items():
            rows.append({"类别": "sensitivity", "指标": name, "值": info.get("rms") if isinstance(info, dict) else info})
        if rows:
            p = dest_dir / "diagnostics.csv"
            pd.DataFrame(rows).to_csv(p, index=False, encoding="utf-8")
            out.append(str(p))

    # Bootstrap samples
    boot = result.get("bootstrap", {})
    for name, info in (boot.get("parameters", {}).items() if enabled("bootstrap") else ()):
        p = dest_dir / f"bootstrap_{name}.csv"
        pd.DataFrame({"sample": info.get("samples", [])}).to_csv(p, index=False, encoding="utf-8")
        out.append(str(p))

    return out
