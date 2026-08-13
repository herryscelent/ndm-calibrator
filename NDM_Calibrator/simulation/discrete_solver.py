"""Discrete-time solver for discrete dynamic models.

V1.0's primary focus is continuous-time ODE models; this module provides the
state-map machinery so a discrete model (x_{k+1} = f(x_k, u_k, theta, k))
can be stepped forward. It is exercised by tests and available for future
discrete templates.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

import numpy as np

from core.exceptions import SimulationError


def step_map(
    f: Callable[[np.ndarray, np.ndarray, dict], np.ndarray],
    x0: np.ndarray,
    u_series: Dict[str, np.ndarray],
    n_steps: int,
    parameters: Dict[str, float],
) -> tuple[np.ndarray, bool, str]:
    """Iterate a discrete state map.

    ``f(x, u, theta)`` returns x_{k+1}. Returns (trajectory (n_steps+1, nx),
    success, message).
    """
    x = np.asarray(x0, dtype=float).reshape(-1)
    nx = x.size
    traj = np.empty((n_steps + 1, nx), dtype=float)
    traj[0] = x

    for k in range(n_steps):
        u = {
            name: float(np.asarray(series, dtype=float)[min(k, series.size - 1)])
            for name, series in u_series.items()
        }
        try:
            x_next = np.asarray(f(x, u, parameters), dtype=float).reshape(-1)
        except Exception as exc:
            return traj[: k + 1], False, f"离散步进失败(第 {k} 步): {exc}"
        if x_next.size != nx:
            return traj[: k + 1], False, "状态维度变化"
        if not np.all(np.isfinite(x_next)):
            return traj[: k + 1], False, f"状态发散(第 {k} 步)"
        traj[k + 1] = x_next
        x = x_next

    return traj, True, "OK"
