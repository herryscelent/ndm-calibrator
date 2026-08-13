"""Field mapping from a raw DataFrame into an Experiment."""

from __future__ import annotations

from typing import List, Sequence

import numpy as np
import pandas as pd

from core.exceptions import DataValidationError
from core.experiment import Experiment


def _as_float_series(df: pd.DataFrame, column: str, role: str) -> pd.Series:
    if column not in df.columns:
        raise DataValidationError(f"列 '{column}' 不存在于数据中")
    raw = df[column]
    # Try numeric coercion; if the column is entirely non-numeric we will
    # surface a clear error.
    coerced = pd.to_numeric(raw, errors="coerce")
    if coerced.isna().all():
        raise DataValidationError(
            f"{role}列 '{column}' 无法转换为数值(可能全部为字符串/缺失)"
        )
    return coerced


def map_columns(
    df: pd.DataFrame,
    time_col: str,
    input_cols: Sequence[str],
    output_cols: Sequence[str],
    ignored_cols: Sequence[str] = (),
) -> Experiment:
    """Build an Experiment by mapping DataFrame columns to roles.

    Raises DataValidationError for missing columns or invalid time series.
    """
    if df is None or df.empty:
        raise DataValidationError("数据为空, 无法映射")

    time_series = _as_float_series(df, time_col, "时间")
    time = time_series.to_numpy(dtype=float)
    if not np.all(np.isfinite(time)):
        raise DataValidationError("时间列包含非有限值 (NaN/Inf)")

    inputs = {col: _as_float_series(df, col, "输入").to_numpy(dtype=float) for col in input_cols}
    outputs = {col: _as_float_series(df, col, "输出").to_numpy(dtype=float) for col in output_cols}

    exp = Experiment(
        time=time,
        inputs=inputs,
        outputs=outputs,
        ignored=list(ignored_cols),
    )
    return exp
