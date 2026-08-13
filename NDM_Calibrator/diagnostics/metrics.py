"""Model calibration metrics (goodness of fit)."""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from core.exceptions import NDMCError


class MetricsError(NDMCError):
    """Raised when metrics cannot be computed from given arrays."""


def compute_metrics(measured: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """Compute standard fit metrics for one output series.

    Returns a dict with SSE, MSE, RMSE, MAE, R2, max_abs_error, mean_error.
    """
    measured = np.asarray(measured, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if measured.size != predicted.size:
        raise MetricsError("measured 与 predicted 长度不一致")
    if measured.size == 0:
        raise MetricsError("指标输入为空")
    if not np.all(np.isfinite(measured)) or not np.all(np.isfinite(predicted)):
        raise MetricsError("指标输入包含非有限值")

    diff = measured - predicted
    sse = float(np.sum(diff**2))
    mse = float(np.mean(diff**2))
    rmse = float(np.sqrt(mse))
    mae = float(np.mean(np.abs(diff)))
    max_abs_error = float(np.max(np.abs(diff)))
    mean_error = float(np.mean(diff))

    var = float(np.var(measured))
    if var > 0:
        r2 = float(1.0 - sse / (measured.size * var))
    else:
        r2 = float("nan")

    return {
        "SSE": sse,
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "R2": r2,
        "max_abs_error": max_abs_error,
        "mean_error": mean_error,
    }


def compute_all_metrics(
    measured_by_output: Dict[str, np.ndarray],
    predicted_by_output: Dict[str, np.ndarray],
) -> Dict[str, Dict[str, float]]:
    """Per-output metrics plus a 'summary' aggregate (mean of each metric)."""
    result: Dict[str, Dict[str, float]] = {}
    for name in measured_by_output:
        result[name] = compute_metrics(
            measured_by_output[name], predicted_by_output[name]
        )
    # Aggregate summary: mean across outputs per metric.
    metrics_names = list(result.values())[0].keys() if result else []
    summary = {}
    for m in metrics_names:
        values = [result[name][m] for name in result if np.isfinite(result[name][m])]
        summary[m] = float(np.mean(values)) if values else float("nan")
    result["summary"] = summary
    return result
