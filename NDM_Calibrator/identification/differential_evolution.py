"""Differential Evolution global optimisation identification."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
from scipy.optimize import differential_evolution

from core.exceptions import OptimizationError
from identification.base import IdentificationContext, bounds_and_initial
from identification.result import IdentificationResult


def run_differential_evolution(
    ctx: IdentificationContext,
    project,
    options: Dict[str, Any],
    seed: Optional[int] = None,
) -> IdentificationResult:
    """Run scipy differential_evolution with a seeded, reproducible RNG."""
    lower, upper, x0 = bounds_and_initial(project)

    population = int(options.get("population", 15))
    maxiter = int(options.get("max_iterations", 1000))
    mutation = options.get("mutation", (0.5, 1.0))
    recombination = float(options.get("recombination", 0.7))
    seed = int(seed) if seed is not None else int(options.get("seed", 0))

    # DE with a fixed seed must be reproducible.
    rng = np.random.default_rng(seed)

    def scalar_objective(theta: np.ndarray) -> float:
        obj = ctx.evaluate(theta)
        if not np.isfinite(obj):
            return 1e12
        return float(obj)

    start = time.time()
    try:
        res = differential_evolution(
            scalar_objective,
            list(zip(lower, upper)),
            seed=rng.integers(0, 2**32 - 1),
            popsize=population,
            maxiter=maxiter,
            mutation=mutation,
            recombination=recombination,
            polish=True,
            updating="immediate",
        )
    except Exception as exc:
        raise OptimizationError(f"Differential Evolution 失败: {exc}") from exc
    runtime = time.time() - start

    theta = res.x
    obj = ctx.evaluate(theta)
    return IdentificationResult(
        algorithm="differential_evolution",
        parameters={name: float(v) for name, v in zip(ctx.free_names, theta)},
        objective_value=obj,
        success=bool(res.success),
        message=res.message if res.message else ("成功" if res.success else "未收敛"),
        n_evaluations=int(res.nit),
        runtime_seconds=runtime,
        seed=seed,
    )
