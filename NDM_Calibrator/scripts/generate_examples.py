"""Generate all synthetic example datasets used by the software and tests.

Every example is generated from the true model with a fixed seed and slight
noise, so results are reproducible. Metadata with true parameters is written
alongside each dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from core.model_definition import DynamicModel
from simulation.simulator import Simulator

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def _write_dataset(name: str, df: pd.DataFrame, metadata: Dict) -> Path:
    csv_path = EXAMPLES_DIR / name / "data.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    (EXAMPLES_DIR / name / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return csv_path


def generate_exponential_decay(seed: int = 100) -> Path:
    """Example 1: exponential decay, true k=0.35."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 20, 401)
    m = DynamicModel.from_builtin("exponential_decay")
    exp = _simulate(m, {"k": 0.35}, t, {}, x0={"x": 5.0})
    noise = rng.normal(0, 0.02, t.size)
    df = pd.DataFrame({"time": t, "x": exp.outputs["x"] + noise})
    meta = {
        "name": "exponential_decay",
        "model": "exponential_decay",
        "true_parameters": {"k": 0.35},
        "noise_std": 0.02,
        "seed": seed,
        "recommended_algorithm": "least_squares",
        "expected_range": {"k": [0.3, 0.4]},
    }
    return _write_dataset("exponential_decay", df, meta)


def generate_first_order(seed: int = 101) -> Path:
    """Example 2: first-order system, true K=2.5, tau=6.0."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 30, 601)
    u = np.where(t < 12, 0.0, 1.0)
    m = DynamicModel.from_builtin("first_order")
    exp = _simulate(m, {"K": 2.5, "tau": 6.0}, t, {"u": u}, x0={"x": 0.0})
    noise = rng.normal(0, 0.02, t.size)
    df = pd.DataFrame({"time": t, "u": u, "x": exp.outputs["x"] + noise})
    meta = {
        "name": "first_order",
        "model": "first_order",
        "true_parameters": {"K": 2.5, "tau": 6.0},
        "noise_std": 0.02,
        "seed": seed,
        "recommended_algorithm": "least_squares",
        "expected_range": {"K": [2.2, 2.8], "tau": [5.0, 7.0]},
    }
    return _write_dataset("first_order", df, meta)


def generate_second_order(seed: int = 102) -> Path:
    """Example 3: mass-spring-damper, true k=30, c=2.0 (m fixed)."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 20, 501)
    u = np.where(t < 2, 0.0, 1.0)
    m = DynamicModel.from_builtin("second_order")
    exp = _simulate(m, {"k": 30.0, "c": 2.0, "m": 1.0}, t, {"u": u}, x0={"x1": 0.0, "x2": 0.0})
    noise = rng.normal(0, 0.03, t.size)
    df = pd.DataFrame({"time": t, "u": u, "x1": exp.outputs["x1"] + noise})
    meta = {
        "name": "second_order",
        "model": "second_order",
        "true_parameters": {"k": 30.0, "c": 2.0},
        "fixed_parameters": {"m": 1.0},
        "noise_std": 0.03,
        "seed": seed,
        "recommended_algorithm": "least_squares",
        "expected_range": {"k": [25, 35], "c": [1.2, 2.8]},
    }
    return _write_dataset("second_order", df, meta)


def generate_cubic_nonlinear(seed: int = 103) -> Path:
    """Example 4: cubic nonlinear, true a=0.5, b=0.8, c=1.2."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 25, 501)
    u = np.where(t < 8, 0.5, 1.5)
    m = DynamicModel.from_builtin("cubic_nonlinear")
    exp = _simulate(m, {"a": 0.5, "b": 0.8, "c": 1.2}, t, {"u": u}, x0={"x": 0.0})
    noise = rng.normal(0, 0.02, t.size)
    df = pd.DataFrame({"time": t, "u": u, "x": exp.outputs["x"] + noise})
    meta = {
        "name": "cubic_nonlinear",
        "model": "cubic_nonlinear",
        "true_parameters": {"a": 0.5, "b": 0.8, "c": 1.2},
        "noise_std": 0.02,
        "seed": seed,
        "recommended_algorithm": "differential_evolution",
        "expected_range": {"a": [0.3, 0.7], "b": [0.5, 1.1], "c": [0.9, 1.5]},
    }
    return _write_dataset("cubic_nonlinear", df, meta)


def _simulate(m, params, t, inputs, x0):
    from core.experiment import Experiment

    exp = Experiment(time=t, inputs=inputs, outputs={o: np.zeros(t.size) for o in m.outputs})
    return Simulator(m).simulate(params, exp, initial_conditions=x0)


def generate_all() -> None:
    paths = [
        generate_exponential_decay(),
        generate_first_order(),
        generate_second_order(),
        generate_cubic_nonlinear(),
    ]
    for p in paths:
        print(f"generated: {p}")
    print(f"total: {len(paths)} examples")


if __name__ == "__main__":
    generate_all()
