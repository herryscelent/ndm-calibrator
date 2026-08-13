"""Algorithm dispatch and run-history management."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.exceptions import OptimizationError
from identification.base import build_context, bounds_and_initial
from identification.differential_evolution import run_differential_evolution
from identification.least_squares import run_least_squares
from identification.multistart import run_multistart
from identification.nelder_mead import run_nelder_mead
from identification.result import IdentificationResult

ALGORITHMS = {
    "least_squares": "非线性最小二乘 (TRF/Dogbox)",
    "nelder_mead": "Nelder-Mead",
    "differential_evolution": "Differential Evolution",
    "multistart": "Multi-start 最小二乘",
}


def algorithm_keys() -> List[str]:
    return list(ALGORITHMS.keys())


def algorithm_labels() -> Dict[str, str]:
    return dict(ALGORITHMS)


def run_algorithm(project, algorithm: str, options: Dict[str, Any]) -> IdentificationResult:
    """Run an identification algorithm and return its result."""
    ctx = build_context(project)
    seed = options.get("seed")

    if algorithm == "least_squares":
        return run_least_squares(ctx, project, options, seed=seed)
    if algorithm == "nelder_mead":
        return run_nelder_mead(ctx, project, options, seed=seed)
    if algorithm == "differential_evolution":
        return run_differential_evolution(ctx, project, options, seed=seed)
    if algorithm == "multistart":
        return run_multistart(ctx, project, options, seed=seed)
    raise OptimizationError(f"未知算法: {algorithm}")


def summarize(project) -> Dict[str, Any]:
    """Return a table-ready summary of all stored identification results."""
    rows = []
    for run in project.results.get("identification_history", []):
        result = run["result"]
        rows.append({
            "algorithm": result["algorithm"],
            "objective": result["objective_value"],
            "runtime": result["runtime_seconds"],
            "evaluations": result["n_evaluations"],
            "success": result["success"],
            "seed": result.get("seed"),
            "parameters": result["parameters"],
        })
    return {"rows": rows}
