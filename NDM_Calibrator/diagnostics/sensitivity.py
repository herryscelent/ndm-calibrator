"""Local parameter sensitivity via finite differences at the optimal point."""

from __future__ import annotations

from typing import Dict

import numpy as np

from core.exceptions import NDMCError


class SensitivityError(NDMCError):
    """Raised when sensitivity cannot be computed."""


def compute_sensitivity(
    predict: callable,
    theta: np.ndarray,
    names: list[str],
    step_frac: float = 1e-3,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate the Jacobian d(predicted)/d(theta) by central finite differences.

    ``predict(theta)`` returns a 1-D array of predicted outputs (flattened
    across all outputs). ``step_frac`` is the relative perturbation used to
    scale the step per parameter, handling parameter-scale differences.

    Returns (S, S_norm) where S is shape (n_samples, n_params) raw sensitivity
    and S_norm is normalised by parameter magnitude.
    """
    theta = np.asarray(theta, dtype=float)
    if theta.ndim != 1:
        raise SensitivityError("参数向量必须是一维")
    base = np.asarray(predict(theta), dtype=float)

    n_params = theta.size
    S = np.empty((base.size, n_params), dtype=float)
    for j in range(n_params):
        scale = max(abs(theta[j]), 1e-8)
        step = step_frac * scale
        tp = theta.copy(); tp[j] += step
        tm = theta.copy(); tm[j] -= step
        yp = np.asarray(predict(tp), dtype=float)
        ym = np.asarray(predict(tm), dtype=float)
        S[:, j] = (yp - ym) / (2 * step)

    if not np.all(np.isfinite(S)):
        raise SensitivityError("灵敏度计算出现非有限值(参数过小或边界附近)")

    # Normalised sensitivity: (d y / d theta) * (theta / |y|) for comparability.
    y_norm = np.abs(base)
    y_safe = np.where(y_norm < 1e-12, 1.0, y_norm)
    S_norm = S * theta[np.newaxis, :] / y_safe[:, np.newaxis]
    return S, S_norm


def sensitivity_summary(S_norm: np.ndarray, names: list[str]) -> Dict[str, Dict[str, float]]:
    """Per-parameter RMS of normalised sensitivity (relative influence)."""
    result = {}
    for j, name in enumerate(names):
        col = S_norm[:, j]
        result[name] = {
            "rms": float(np.sqrt(np.mean(col**2))) if col.size else 0.0,
            "max": float(np.max(np.abs(col))) if col.size else 0.0,
        }
    return result
