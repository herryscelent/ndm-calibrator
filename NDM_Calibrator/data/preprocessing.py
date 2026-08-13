"""Preprocessing operations on mapped experiment data.

All operations return a NEW Experiment and append a log entry, so the full
history of preprocessing is recorded in the project configuration.
"""

from __future__ import annotations

import numpy as np

from core.experiment import Experiment


def _log(history: list[str], message: str) -> None:
    history.append(message)


def drop_nan_rows(exp: Experiment, history: list[str]) -> Experiment:
    """Drop rows where any mapped column is NaN/Inf."""
    n_before = exp.n_points
    mask = np.ones(exp.n_points, dtype=bool)
    for name, arr in {**exp.inputs, **exp.outputs}.items():
        mask &= np.isfinite(arr)
    mask &= np.isfinite(exp.time)

    new = Experiment(
        time=exp.time[mask],
        inputs={k: v[mask] for k, v in exp.inputs.items()},
        outputs={k: v[mask] for k, v in exp.outputs.items()},
        ignored=list(exp.ignored),
    )
    _log(history, f"删除缺失行: {n_before} -> {new.n_points}")
    return new


def interpolate_nan(exp: Experiment, history: list[str]) -> Experiment:
    """Linearly interpolate NaN/Inf in each mapped series."""
    time = exp.time
    new_inputs = {}
    new_outputs = {}
    for name, arr in exp.inputs.items():
        new_inputs[name] = _interp_series(time, arr)
    for name, arr in exp.outputs.items():
        new_outputs[name] = _interp_series(time, arr)
    _log(history, "对缺失值执行线性插值")
    return Experiment(time=time, inputs=new_inputs, outputs=new_outputs, ignored=list(exp.ignored))


def _interp_series(time: np.ndarray, arr: np.ndarray) -> np.ndarray:
    out = arr.astype(float, copy=True)
    bad = ~np.isfinite(out)
    if not bad.any():
        return out
    good_idx = np.flatnonzero(~bad)
    if good_idx.size == 0:
        out[:] = 0.0
        return out
    out[bad] = np.interp(time[bad], time[good_idx], out[good_idx])
    # Interior NaN get interpolated; leading/trailing NaN (outside the
    # good samples) are replaced by their nearest valid neighbour.
    if not np.all(np.isfinite(out)):
        nearest = np.interp(np.arange(out.size), good_idx, out[good_idx])
        out[~np.isfinite(out)] = nearest[~np.isfinite(out)]
    return out


def select_time_range(exp: Experiment, t_start: float | None, t_end: float | None, history: list[str]) -> Experiment:
    """Keep only samples inside [t_start, t_end]."""
    mask = np.ones(exp.n_points, dtype=bool)
    if t_start is not None:
        mask &= exp.time >= t_start
    if t_end is not None:
        mask &= exp.time <= t_end

    new = Experiment(
        time=exp.time[mask],
        inputs={k: v[mask] for k, v in exp.inputs.items()},
        outputs={k: v[mask] for k, v in exp.outputs.items()},
        ignored=list(exp.ignored),
    )
    _log(history, f"选择时间区间 [{t_start}, {t_end}]: 保留 {new.n_points} 点")
    return new
