"""Differential Evolution global optimisation identification."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
from scipy.optimize import differential_evolution

from core.exceptions import OptimizationError
from identification.base import IdentificationContext, bounds_and_initial, check_cancelled
from identification.result import IdentificationResult


def run_differential_evolution(
    ctx: IdentificationContext,
    project,
    options: Dict[str, Any],
    seed: Optional[int] = None,
) -> IdentificationResult:
    """Run scipy differential_evolution with a seeded, reproducible RNG."""
    lower, upper, x0 = bounds_and_initial(project)

    try:
        population = int(options.get("population", 15))
        maxiter = int(options.get("max_iterations", 1000))
    except (TypeError, ValueError) as exc:
        raise OptimizationError("DE 种群规模和最大迭代次数必须是整数") from exc
    if population < 1:
        raise OptimizationError("DE 种群规模必须 >= 1")
    if maxiter < 1:
        raise OptimizationError("DE 最大迭代次数必须 >= 1")
    mutation = options.get("mutation", (0.5, 1.0))
    try:
        recombination = float(options.get("recombination", 0.7))
    except (TypeError, ValueError) as exc:
        raise OptimizationError("DE 重组概率必须在 [0, 1] 内") from exc
    if not np.isfinite(recombination) or not 0 <= recombination <= 1:
        raise OptimizationError("DE 重组概率必须在 [0, 1] 内")
    tolerance = options.get("tolerance", 0.01)
    try:
        tolerance = float(tolerance)
    except (TypeError, ValueError) as exc:
        raise OptimizationError("DE 收敛容差必须是正数") from exc
    if not np.isfinite(tolerance) or tolerance <= 0:
        raise OptimizationError("DE 收敛容差必须是正的有限数")
    raw_seed = seed if seed is not None else (options["seed"] if "seed" in options else 0)
    seed = int(raw_seed) if raw_seed is not None else None

    # DE with a fixed seed must be reproducible.
    rng = np.random.default_rng(seed)

    def scalar_objective(theta: np.ndarray) -> float:
        check_cancelled(options)
        obj = ctx.evaluate(theta)
        if not np.isfinite(obj):
            return 1e12
        return float(obj)

    start = time.time()
    try:
        def callback(_xk, _convergence):
            return bool(options.get("_cancel_token") and options["_cancel_token"].cancelled())

        res = differential_evolution(
            scalar_objective,
            list(zip(lower, upper)),
            seed=rng.integers(0, 2**32 - 1) if seed is not None else None,
            popsize=population,
            maxiter=maxiter,
            mutation=mutation,
            recombination=recombination,
            tol=tolerance,
            polish=True,
            updating="immediate",
            callback=callback,
        )
    except Exception as exc:
        raise OptimizationError(f"Differential Evolution 失败: {exc}") from exc
    runtime = time.time() - start
    check_cancelled(options)

    theta = res.x
    obj = ctx.evaluate(theta)
    return IdentificationResult(
        algorithm="differential_evolution",
        parameters={name: float(v) for name, v in zip(ctx.free_names, theta)},
        objective_value=obj,
        success=bool(res.success),
        message=res.message if res.message else ("成功" if res.success else "未收敛"),
        n_evaluations=int(getattr(res, "nfev", res.nit)),
        runtime_seconds=runtime,
        seed=seed,
    )
