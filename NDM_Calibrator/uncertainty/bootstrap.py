"""Residual bootstrap for parameter uncertainty estimation."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import numpy as np

from app.constants import BOOTSTRAP_DEFAULT_B
from core.exceptions import NDMCError
from identification.base import build_context, bounds_and_initial
from identification.differential_evolution import run_differential_evolution
from identification.least_squares import run_least_squares
from identification.nelder_mead import run_nelder_mead


class BootstrapError(NDMCError):
    """Raised when bootstrap cannot be performed."""


def _sample_algos():
    from identification.manager import algorithm_keys
    return {k: k for k in algorithm_keys()}


def run_bootstrap(project, options: Dict[str, Any]) -> Dict[str, Any]:
    """Residual bootstrap.

    Workflow:
      1. Fit with the stored optimal parameters (or re-run the given algorithm
         if no result is stored) to get residuals.
      2. Resample residuals with replacement, add to the fitted response to
         build B synthetic datasets, and re-identify each.
      3. Report per-parameter mean/std/median/2.5/97.5 percentiles.

    ``options``: B (int), seed (int), algorithm (str).
    """
    B = int(options.get("B", BOOTSTRAP_DEFAULT_B))
    seed = options.get("seed")
    algorithm = options.get("algorithm", "least_squares")
    if B < 1:
        raise BootstrapError("B 必须 >= 1")
    if B > 1000:
        raise BootstrapError("B 过大 (上限 1000), 桌面上会非常慢")

    ctx = build_context(project)
    lower, upper, x0 = bounds_and_initial(project)
    free_names = ctx.free_names

    # 1. Optimal parameters from stored current identification, if any.
    current = project.results.get("identification")
    if current is not None and current.get("result", {}).get("parameters"):
        theta_opt = np.array(
            [current["result"]["parameters"][n] for n in free_names], dtype=float
        )
    else:
        # Fall back to re-running the requested algorithm once.
        result = _run_algo(project, algorithm, seed)
        theta_opt = np.array([result.parameters[n] for n in free_names], dtype=float)

    predicted = ctx.predict_outputs(theta_opt)
    residuals = {
        name: ctx.measured_outputs()[name] - predicted[name] for name in ctx.model.outputs
    }
    n = ctx.experiment.n_points

    rng = np.random.default_rng(seed)
    samples: Dict[str, List[float]] = {name: [] for name in free_names}
    successes = 0
    failures: List[str] = []

    start = time.time()
    for b in range(B):
        try:
            # 2-4. Bootstrap data and re-identify.
            boot_residuals = {
                name: residuals[name][rng.integers(0, n, size=n)] for name in residuals
            }
            boot_measured = {
                name: predicted[name] + boot_residuals[name] for name in residuals
            }
            boot_project = _make_boot_project(project, boot_measured)
            result = _run_algo(boot_project, algorithm, seed=seed + b if seed is not None else None)
            for i, name in enumerate(free_names):
                samples[name].append(result.parameters[name])
            successes += 1
        except Exception as exc:
            failures.append(f"bootstrap 第 {b} 次失败: {exc}")
            if len(failures) > max(1, B // 2):
                raise BootstrapError(
                    f"Bootstrap 失败过多 ({len(failures)}/{B}): {failures[0]}"
                )
    runtime = time.time() - start

    if successes == 0:
        raise BootstrapError("所有 bootstrap 重辨识均失败")

    per_param = {}
    for name in free_names:
        arr = np.array(samples[name])
        mean = float(np.mean(arr))
        std = float(np.std(arr))
        median = float(np.median(arr))
        lo = float(np.percentile(arr, 2.5))
        hi = float(np.percentile(arr, 97.5))
        per_param[name] = {
            "mean": mean,
            "std": std,
            "median": median,
            "p2_5": lo,
            "p97_5": hi,
            "samples": [float(v) for v in arr],
            "n_success": int(arr.size),
        }

    return {
        "method": "residual bootstrap",
        "B": B,
        "n_success": successes,
        "n_failures": len(failures),
        "seed": seed,
        "algorithm": algorithm,
        "runtime_seconds": float(runtime),
        "parameters": per_param,
        "failures": failures,
        "optimal_parameters": {n: float(theta_opt[i]) for i, n in enumerate(free_names)},
    }


def _make_boot_project(project, boot_measured: Dict[str, np.ndarray]):
    from core.experiment import Experiment

    exp = project.experiment
    new_exp = Experiment(
        time=exp.time,
        inputs=dict(exp.inputs),
        outputs=boot_measured,
        ignored=list(exp.ignored),
    )
    new_project = type(project)(
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        modified_at=project.modified_at,
        file_path=project.file_path,
        data_source=project.data_source,
        column_types=dict(project.column_types),
        mapping=dict(project.mapping),
        preprocess_log=list(project.preprocess_log),
        settings=dict(project.settings),
        results={},
    )
    new_project.experiment = new_exp
    new_project.model = project.model
    new_project.parameters = project.parameters
    return new_project


def _run_algo(project, algorithm: str, seed: Optional[int]):
    ctx = build_context(project)
    from identification.manager import run_algorithm
    return run_algorithm(project, algorithm, {"seed": seed} if seed is not None else {})
