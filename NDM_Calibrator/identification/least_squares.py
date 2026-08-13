"""Nonlinear least-squares identification via scipy.optimize.least_squares."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
from scipy.optimize import least_squares

from core.exceptions import OptimizationError
from core.objective import ObjectiveConfig, residuals_for_objective
from identification.base import IdentificationContext, bounds_and_initial
from identification.result import IdentificationResult


def run_least_squares(
    ctx: IdentificationContext,
    project,
    options: Dict[str, Any],
    seed: Optional[int] = None,
) -> IdentificationResult:
    """Run scipy least_squares (TRF / Dogbox) on the residual vector.

    The residual vector is built per output so multi-output models fit
    simultaneously. NaN/Inf residuals are mapped to a large penalty so the
    optimiser is nudged away from diverging regions instead of crashing.
    """
    method = options.get("method", "trf")
    if method not in ("trf", "dogbox", "lm"):
        raise OptimizationError(f"不支持的 least_squares 方法: {method}")

    lower, upper, x0 = bounds_and_initial(project)
    for name, val in zip(ctx.free_names, x0):
        lo = project.parameters.get(name).lower
        hi = project.parameters.get(name).upper
        if not lo < val < hi:
            raise OptimizationError(
                f"参数 {name} 初值 {val} 超出范围 ({lo}, {hi})"
            )

    # Residual builder: weights per output scale the residual so the
    # weighted least-squares objective is optimised.
    def residuals(theta: np.ndarray) -> np.ndarray:
        params = ctx.build_parameter_dict(theta)
        sim = ctx.simulator.simulate(
            params, ctx.experiment,
            initial_conditions=ctx.initial_conditions,
            input_interpolation=ctx.input_interpolation,
        )
        if not sim.success:
            # Penalty proportional to divergence magnitude keeps gradient info.
            pen = 1e6 * (1.0 + np.linalg.norm(theta))
            return np.full(
                sum(o.size for o in ctx.measured_outputs().values()), pen, dtype=float
            )
        pieces = []
        for name in ctx.model.outputs:
            measured = ctx.measured_outputs()[name]
            predicted = sim.outputs[name]
            w = ctx.objective_config.weight_for(name)
            pieces.append(residuals_for_objective(measured, predicted, ctx.objective_config, w))
        return np.concatenate(pieces)

    start = time.time()
    try:
        ls = least_squares(
            residuals,
            x0,
            bounds=(lower, upper),
            method=method if method != "lm" else "trf",  # lm ignores bounds
        )
    except Exception as exc:
        raise OptimizationError(f"least_squares 失败: {exc}") from exc
    runtime = time.time() - start

    obj = ctx.evaluate(ls.x)
    return IdentificationResult(
        algorithm="least_squares",
        parameters={name: float(v) for name, v in zip(ctx.free_names, ls.x)},
        objective_value=obj,
        success=bool(ls.success),
        message=ls.message if ls.message else ("成功" if ls.success else "未收敛"),
        n_evaluations=int(ls.nfev),
        runtime_seconds=runtime,
        seed=seed,
        extra={"method": method},
    )
