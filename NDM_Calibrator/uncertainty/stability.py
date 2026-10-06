"""Multi-start stability analysis.

Uses the local-solution cloud produced by multi-start identification (or by
running it on demand) to compute statistics about how stable the optimal
parameter estimate is across starting points.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from core.exceptions import NDMCError
from identification.base import build_context, bounds_and_initial, check_cancelled
from identification.multistart import generate_initial_guesses, run_multistart
from app.constants import STABILITY_CV_HIGH_THRESHOLD


class StabilityError(NDMCError):
    """Raised when stability analysis cannot be performed."""


def run_multistart_stability(project, options: Dict[str, Any]) -> Dict[str, Any]:
    """Run multi-start and compute per-parameter stability statistics.

    Reuses the stored multistart run when available and compatible; otherwise
    runs it fresh.
    """
    check_cancelled(options)
    free_names = [p.name for p in project.parameters.free_parameters()]

    stored = project.results.get("identification_history", [])
    ms_runs = [r for r in stored if r.get("algorithm") == "multistart"]
    result = None
    if ms_runs:
        last = ms_runs[-1]["result"]
        if last.get("extra", {}).get("all_solutions"):
            result = last

    if result is None:
        # Run it on demand.
        ctx = build_context(project)
        lower, upper, x0 = bounds_and_initial(project)
        try:
            n_starts = int(options.get("n_starts", 10))
        except (TypeError, ValueError) as exc:
            raise StabilityError("多起点数量必须是正整数") from exc
        if n_starts < 1:
            raise StabilityError("多起点数量必须 >= 1")
        seed = options.get("seed", 0)
        from identification.manager import run_algorithm
        run_options = {"n_starts": n_starts, "seed": seed}
        if options.get("_cancel_token") is not None:
            run_options["_cancel_token"] = options["_cancel_token"]
        r = run_algorithm(project, "multistart", run_options)
        result = r.to_dict() if hasattr(r, "to_dict") else r

    all_solutions = result.get("extra", {}).get("all_solutions", [])
    check_cancelled(options)
    feasible = [s for s in all_solutions if s.get("theta") is not None and np.isfinite(s.get("objective", np.inf))]
    if not feasible:
        raise StabilityError("没有可用的多起点结果")

    objectives = np.array([s["objective"] for s in feasible], dtype=float)
    theta_matrix = np.array([s["theta"] for s in feasible], dtype=float)

    best_obj = float(np.min(objectives))
    success_count = sum(1 for s in feasible if s.get("success"))
    per_param = {}
    for j, name in enumerate(free_names):
        col = theta_matrix[:, j]
        mean = float(np.mean(col))
        std = float(np.std(col))
        cv = float(std / abs(mean)) if abs(mean) > 1e-12 else float("inf")
        per_param[name] = {
            "mean": mean,
            "std": std,
            "min": float(np.min(col)),
            "max": float(np.max(col)),
            "cv": cv,
            "best": float(theta_matrix[np.argmin(objectives), j]),
            "samples": [float(v) for v in col],
            "high_variability": cv > STABILITY_CV_HIGH_THRESHOLD,
        }

    return {
        "n_starts": int(len(all_solutions)),
        "n_feasible": int(len(feasible)),
        "n_success": success_count,
        "success_rate": float(success_count / len(all_solutions)) if all_solutions else 0.0,
        "best_objective": best_obj,
        "objective_mean": float(np.mean(objectives)),
        "objective_std": float(np.std(objectives)),
        "parameters": per_param,
        "seed": result.get("seed"),
    }
