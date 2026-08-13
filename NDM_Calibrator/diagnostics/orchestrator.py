"""Orchestration of post-identification calibration and diagnostics."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from core.exceptions import NDMCError
from core.objective import ObjectiveConfig
from diagnostics.identifiability import compute_identifiability
from diagnostics.metrics import compute_all_metrics
from diagnostics.residuals import (
    compute_residual_stats,
    residual_structure_diagnosis,
)
from diagnostics.sensitivity import compute_sensitivity, sensitivity_summary
from identification.base import build_context


def run_calibration_and_diagnostics(project, parameter_values: Dict[str, float]) -> Dict[str, Any]:
    """Compute metrics, residuals, sensitivity and identifiability for the
    given parameter values, and store results on the project."""
    ctx = build_context(project)
    free_names = ctx.free_names
    theta = np.array([parameter_values[name] for name in free_names], dtype=float)

    # Predicted vs measured
    predicted = ctx.predict_outputs(theta)
    measured = ctx.measured_outputs()

    metrics = compute_all_metrics(measured, predicted)

    residuals = {}
    residual_stats = {}
    residual_diagnosis = {}
    for name in ctx.model.outputs:
        res = measured[name] - predicted[name]
        residuals[name] = res
        residual_stats[name] = compute_residual_stats(res)
        residual_diagnosis[name] = residual_structure_diagnosis(res)

    # Sensitivity
    predict_flat = lambda th: np.concatenate(
        [ctx.predict_outputs(th)[n] for n in ctx.model.outputs]
    )
    S, S_norm = compute_sensitivity(predict_flat, theta, free_names)
    sens_summary = sensitivity_summary(S_norm, free_names)

    # Identifiability (using residual variance as sigma2 estimate)
    sigma2 = max(residual_stats[ctx.model.outputs[0]]["std"], 1e-12) ** 2
    ident = compute_identifiability(S, sigma2=sigma2)
    ident["parameter_names"] = free_names

    result = {
        "parameter_values": {k: float(v) for k, v in parameter_values.items()},
        "metrics": metrics,
        "residuals": {k: v.tolist() for k, v in residuals.items()},
        "residual_stats": residual_stats,
        "residual_diagnosis": residual_diagnosis,
        "sensitivity": {"S": S.tolist(), "S_norm": S_norm.tolist(), "summary": sens_summary, "names": free_names},
        "identifiability": ident,
    }
    project.results["calibration"] = result
    project.mark_dirty()
    return result
