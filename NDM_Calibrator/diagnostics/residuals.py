"""Residual diagnostics: statistics, autocorrelation and structure hints."""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from app.constants import RESIDUAL_ACF_MAX_LAG_DEFAULT, RESIDUAL_STRUCTURE_MESSAGE
from core.exceptions import NDMCError


class ResidualDiagnosticsError(NDMCError):
    """Raised when residual diagnostics cannot be computed."""


def compute_residual_stats(residuals: np.ndarray) -> Dict[str, float]:
    residuals = np.asarray(residuals, dtype=float)
    if residuals.size == 0:
        raise ResidualDiagnosticsError("残差为空")
    if not np.all(np.isfinite(residuals)):
        raise ResidualDiagnosticsError("残差包含非有限值")
    return {
        "mean": float(np.mean(residuals)),
        "std": float(np.std(residuals)),
        "min": float(np.min(residuals)),
        "max": float(np.max(residuals)),
        "count": int(residuals.size),
    }


def autocorrelation(residuals: np.ndarray, max_lag: int) -> np.ndarray:
    """Sample autocorrelation for lags 1..max_lag (mean-removed)."""
    residuals = np.asarray(residuals, dtype=float)
    n = residuals.size
    if n < 2:
        raise ResidualDiagnosticsError("样本过少, 无法计算自相关")
    max_lag = min(int(max_lag), n - 1)
    r = residuals - np.mean(residuals)
    denom = np.sum(r**2)
    if denom == 0:
        return np.zeros(max_lag)
    acf = np.empty(max_lag)
    for lag in range(1, max_lag + 1):
        acf[lag - 1] = np.sum(r[lag:] * r[:-lag]) / denom
    return acf


def residual_structure_diagnosis(residuals: np.ndarray, max_lag: int = RESIDUAL_ACF_MAX_LAG_DEFAULT) -> Dict[str, object]:
    """Return a diagnosis dict for residuals of one output.

    Uses the Ljung-Box style rule-of-thumb: if any of the first few ACF lags
    exceed ~1.96/sqrt(n) in magnitude, there is evidence of structure. The
    message is worded as a statistical hint, not an absolute claim.
    """
    residuals = np.asarray(residuals, dtype=float)
    n = residuals.size
    if n < 4:
        return {"has_structure": False, "message": "样本过少, 无法进行残差结构诊断", "acf": []}
    max_lag = min(int(max_lag), min(n - 1, 20))
    acf = autocorrelation(residuals, max_lag)
    threshold = 1.96 / np.sqrt(n)
    exceeding = [int(lag) for lag in range(1, max_lag + 1) if abs(acf[lag - 1]) > threshold]
    # Persistent correlation across several lags is evidence of structure;
    # a single lag exceeding the threshold is common even for white noise.
    has_structure = len(exceeding) >= 3
    return {
        "has_structure": has_structure,
        "message": RESIDUAL_STRUCTURE_MESSAGE if has_structure else "未检测到明显残差结构",
        "acf": acf.tolist(),
        "lags_exceeding_threshold": exceeding,
        "threshold": float(threshold),
    }
