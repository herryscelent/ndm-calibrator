"""Multi-start least-squares identification.

Generates M initial guesses inside the parameter box, runs local least-squares
from each, sorts by objective, and returns the best while keeping all local
solutions for stability analysis.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares

from core.exceptions import OptimizationError
from identification.base import IdentificationContext, bounds_and_initial
from identification.result import IdentificationResult


def generate_initial_guesses(lower, upper, n_starts: int, seed: int | None) -> np.ndarray:
    """Latin-hypercube style spread of initial guesses inside the box."""
    rng = np.random.default_rng(seed)
    n_params = lower.size
    guesses = np.empty((n_starts, n_params), dtype=float)
    for j in range(n_params):
        lo, hi = lower[j], upper[j]
        # Stratified sampling along each dimension.
        edges = np.linspace(lo, hi, n_starts + 1)
        cells = [edges[i:i + 2] for i in range(n_starts)]
        for i in range(n_starts):
            a, b = cells[i]
            guesses[i, j] = rng.uniform(a, b)
    # Shuffle so stratification doesn't correlate columns.
    if n_params > 1:
        for j in range(n_params):
            guesses[:, j] = rng.permutation(guesses[:, j])
    return guesses


def run_multistart(
    ctx: IdentificationContext,
    project,
    options: Dict[str, Any],
    seed: Optional[int] = None,
) -> IdentificationResult:
    """Run least-squares from multiple starts, return best solution."""
    lower, upper, x0 = bounds_and_initial(project)
    n_starts = int(options.get("n_starts", 10))
    seed = int(seed) if seed is not None else int(options.get("seed", 0))
    method = options.get("method", "trf")

    guesses = generate_initial_guesses(lower, upper, n_starts, seed)

    all_solutions: List[Dict[str, Any]] = []

    def residuals(theta: np.ndarray) -> np.ndarray:
        params = ctx.build_parameter_dict(theta)
        sim = ctx.simulator.simulate(
            params, ctx.experiment,
            initial_conditions=ctx.initial_conditions,
            input_interpolation=ctx.input_interpolation,
        )
        if not sim.success:
            pen = 1e6 * (1.0 + np.linalg.norm(theta))
            return np.full(
                sum(o.size for o in ctx.measured_outputs().values()), pen, dtype=float
            )
        from core.objective import residuals_for_objective

        pieces = []
        for name in ctx.model.outputs:
            measured = ctx.measured_outputs()[name]
            predicted = sim.outputs[name]
            w = ctx.objective_config.weight_for(name)
            pieces.append(residuals_for_objective(measured, predicted, ctx.objective_config, w))
        return np.concatenate(pieces)

    start = time.time()
    for i, g in enumerate(guesses):
        try:
            ls = least_squares(
                residuals, g, bounds=(lower, upper), method=method,
            )
            theta = ls.x
            obj = ctx.evaluate(theta)
        except Exception as exc:
            all_solutions.append({"start": g.tolist(), "theta": None, "objective": np.inf, "success": False, "message": str(exc)})
            continue
        all_solutions.append({
            "start": g.tolist(),
            "theta": theta.tolist(),
            "objective": float(obj),
            "success": bool(ls.success),
            "nfev": int(ls.nfev),
        })
    runtime = time.time() - start

    feasible = [s for s in all_solutions if s["theta"] is not None and np.isfinite(s["objective"])]
    if not feasible:
        raise OptimizationError("所有多起点优化均失败")

    best = min(feasible, key=lambda s: s["objective"])
    n_success = sum(1 for s in feasible if s["success"])
    return IdentificationResult(
        algorithm="multistart",
        parameters={name: float(v) for name, v in zip(ctx.free_names, best["theta"])},
        objective_value=best["objective"],
        success=best["success"],
        message=f"多起点优化完成: {len(all_solutions)} 起点, {n_success} 成功",
        n_evaluations=sum(s.get("nfev", 0) for s in all_solutions),
        runtime_seconds=runtime,
        seed=seed,
        extra={
            "n_starts": n_starts,
            "n_success": n_success,
            "all_solutions": all_solutions,
        },
    )
