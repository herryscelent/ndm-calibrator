"""Nelder-Mead downhill simplex identification."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
from scipy.optimize import minimize

from core.exceptions import OptimizationError
from core.objective import aggregate_objectives, evaluate_objective
from identification.base import IdentificationContext, bounds_and_initial
from identification.result import IdentificationResult


def run_nelder_mead(
    ctx: IdentificationContext,
    project,
    options: Dict[str, Any],
    seed: Optional[int] = None,
) -> IdentificationResult:
    """Run scipy.optimize.minimize(method='Nelder-Mead') on the scalar objective.

    Nelder-Mead does not support hard bounds natively; we fold the bounds in
    with a soft penalty so solutions stay inside the feasible box.
    """
    lower, upper, x0 = bounds_and_initial(project)
    max_iter = int(options.get("max_iterations", 10000))
    penalty = options.get("bounds_penalty", 1e3)

    def scalar_objective(theta: np.ndarray) -> float:
        obj = ctx.evaluate(theta)
        if not np.isfinite(obj):
            return 1e9
        # Soft bounds penalty.
        below = np.maximum(lower - theta, 0.0)
        above = np.maximum(theta - upper, 0.0)
        return float(obj + penalty * (np.sum(below**2) + np.sum(above**2)))

    start = time.time()
    try:
        res = minimize(
            scalar_objective,
            x0,
            method="Nelder-Mead",
            options={"maxiter": max_iter, "xatol": 1e-8, "fatol": 1e-8},
        )
    except Exception as exc:
        raise OptimizationError(f"Nelder-Mead 失败: {exc}") from exc
    runtime = time.time() - start

    theta = np.clip(res.x, lower, upper)
    obj = ctx.evaluate(theta)
    return IdentificationResult(
        algorithm="nelder_mead",
        parameters={name: float(v) for name, v in zip(ctx.free_names, theta)},
        objective_value=obj,
        success=bool(res.success),
        message=res.message if res.message else ("成功" if res.success else "未收敛"),
        n_evaluations=int(res.nfev),
        runtime_seconds=runtime,
        seed=seed,
    )
