"""Continuous-time ODE solver built on scipy.integrate.solve_ivp.

Supports RK45, DOP853, Radau, BDF with configurable tolerances. Input signals
are provided as callables u(t) and interpolated to whatever time points the
integrator needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

import numpy as np
from scipy.integrate import solve_ivp

from app.constants import (
    ODE_DEFAULT_ATOL,
    ODE_DEFAULT_METHOD,
    ODE_DEFAULT_RTOL,
)
from core.exceptions import SimulationError

_METHODS = ("RK45", "DOP853", "Radau", "BDF")

# States above this magnitude are treated as diverged (explosion). Chosen well
# above any physically meaningful signal level but far below float overflow.
_DIVERGENCE_LIMIT = 1e20


@dataclass
class ODESolverConfig:
    method: str = ODE_DEFAULT_METHOD
    rtol: float = ODE_DEFAULT_RTOL
    atol: float = ODE_DEFAULT_ATOL
    max_step: Optional[float] = None

    def __post_init__(self):
        if self.method not in _METHODS:
            raise SimulationError(f"不支持的求解方法: {self.method} (允许: {_METHODS})")
        if self.rtol <= 0 or self.atol <= 0:
            raise SimulationError("rtol/atol 必须为正")


def solve_ode(
    rhs: Callable[[float, np.ndarray], np.ndarray],
    x0: np.ndarray,
    t_span: tuple[float, float],
    t_eval: Optional[np.ndarray] = None,
    config: ODESolverConfig | None = None,
) -> tuple[np.ndarray, np.ndarray, bool, str]:
    """Integrate an ODE system.

    Returns (t, X, success, message). ``X`` has shape (len(t), n_states).
    On failure ``success`` is False and ``message`` explains why; the caller
    must not let this crash the GUI.
    """
    config = config or ODESolverConfig()
    x0 = np.asarray(x0, dtype=float)
    kwargs = {}
    if config.max_step is not None:
        kwargs["max_step"] = config.max_step
    try:
        result = solve_ivp(
            rhs,
            (t_span[0], t_span[1]),
            x0,
            method=config.method,
            rtol=config.rtol,
            atol=config.atol,
            t_eval=t_eval,
            **kwargs,
        )
    except Exception as exc:  # solve_ivp raises on hard failures
        return np.asarray(t_eval if t_eval is not None else [t_span[0]], dtype=float), \
               np.full((t_eval.size if t_eval is not None else 1, x0.size), np.nan), False, f"积分失败: {exc}"

    t = result.t
    y = result.y.T  # (n_t, n_states)
    if t.size == 0 or y.size == 0:
        return t, y, False, "积分返回空结果"

    # Guard against divergence: NaN/Inf, or values exploding to an enormous
    # but still finite magnitude that would destroy the fit objective.
    if np.any(~np.isfinite(y)) or np.any(np.abs(y) > _DIVERGENCE_LIMIT):
        return t, y, False, "状态发散(NaN/Inf/爆炸), 请检查参数与模型"

    if not result.success:
        return t, y, False, f"积分器提前终止: {result.message}"

    return t, y, True, "OK"
