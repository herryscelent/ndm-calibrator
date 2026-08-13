"""Interpolation of input signals onto an arbitrary simulation grid.

Supports zero-order hold and linear interpolation, both monotonicity-safe and
NaN-defensive.
"""

from __future__ import annotations

import numpy as np

from core.exceptions import SimulationError


def zero_order_hold(t_source: np.ndarray, u_source: np.ndarray, t_query: np.ndarray) -> np.ndarray:
    """Piecewise-constant interpolation (backward fill)."""
    _validate_inputs(t_source, u_source)
    if t_source.size == 0:
        raise SimulationError("输入信号为空")
    idx = np.searchsorted(t_source, t_query, side="right") - 1
    idx = np.clip(idx, 0, t_source.size - 1)
    return np.asarray(u_source, dtype=float)[idx]


def linear_interpolation(t_source: np.ndarray, u_source: np.ndarray, t_query: np.ndarray) -> np.ndarray:
    """Linear interpolation; clamps to the endpoints outside the source range."""
    _validate_inputs(t_source, u_source)
    if t_source.size < 2:
        return np.full(t_query.shape, float(np.asarray(u_source, dtype=float)[0]))
    u = np.asarray(u_source, dtype=float)
    return np.interp(t_query, t_source, u)


def _validate_inputs(t_source: np.ndarray, u_source: np.ndarray) -> None:
    if t_source.shape != u_source.shape:
        raise SimulationError("插值: 时间与数值长度不一致")
    if t_source.size == 0:
        raise SimulationError("插值: 空输入")
    if not np.all(np.isfinite(t_source)):
        raise SimulationError("插值: 源时间包含非有限值")
