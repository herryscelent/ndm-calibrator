"""Data validation checks on imported series.

All checks are non-fatal at the application level: they return a list of
warnings that the UI can display, rather than crashing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.exceptions import DataValidationError


def validate_series(time: np.ndarray, inputs: dict, outputs: dict) -> list[str]:
    """Run all checks and return a list of human-readable warnings.

    Hard structural errors (empty data, time not finite) raise
    DataValidationError; softer issues are returned as warnings.
    """
    warnings: list[str] = []

    if time.size == 0:
        raise DataValidationError("数据为空")
    if not np.all(np.isfinite(time)):
        raise DataValidationError("时间列包含非有限值 (NaN/Inf)")

    n = time.size

    # Monotonicity
    diff = np.diff(time)
    if np.any(diff < 0):
        warnings.append("时间并非单调递增(存在回退)")
    elif np.any(diff == 0):
        warnings.append("存在重复时间戳")

    # Interval statistics
    if diff.size > 0:
        intervals = np.abs(diff)
        warnings.append(
            f"时间间隔: 最小={intervals.min():.6g}, 最大={intervals.max():.6g}, "
            f"均值={intervals.mean():.6g}"
        )

    for name, arr in {**inputs, **outputs}.items():
        nan_count = int(np.isnan(arr).sum())
        inf_count = int(np.isinf(arr).sum())
        non_finite = nan_count + inf_count
        if non_finite > 0:
            warnings.append(f"列 '{name}': NaN={nan_count}, Inf={inf_count}")
        if arr.size != n:
            warnings.append(f"列 '{name}': 长度({arr.size})与时间长度({n})不一致")

    if n < 2:
        warnings.append("数据点过少(<2), 难以进行参数辨识")

    return warnings


def describe_dataframe(df: pd.DataFrame) -> dict:
    """Compute summary statistics shown in the data management page."""
    stats = {}
    for col in df.columns:
        series = df[col]
        numeric = pd.to_numeric(series, errors="coerce")
        nan_count = int(numeric.isna().sum())
        if nan_count == len(numeric):
            stats[col] = {
                "dtype": str(series.dtype),
                "nan": nan_count,
                "min": None,
                "max": None,
                "mean": None,
                "std": None,
            }
        else:
            stats[col] = {
                "dtype": str(series.dtype),
                "nan": nan_count,
                "min": float(numeric.min()),
                "max": float(numeric.max()),
                "mean": float(numeric.mean()),
                "std": float(numeric.std()),
            }
    return stats
