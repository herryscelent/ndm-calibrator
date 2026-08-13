"""Shared fixtures for the test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.experiment import Experiment  # noqa: E402
from core.model_definition import DynamicModel  # noqa: E402
from core.parameter import Parameter, ParameterTable  # noqa: E402
from core.project import Project  # noqa: E402
from simulation.simulator import Simulator  # noqa: E402


@pytest.fixture
def first_order_data():
    """Synthetic first-order data with known truth (K=2.5, tau=6.0)."""
    rng = np.random.default_rng(42)
    m = DynamicModel.from_builtin("first_order")
    t = np.linspace(0, 30, 301)
    u = np.where(t < 15, 0.0, 1.0)
    exp = Experiment(time=t, inputs={"u": u}, outputs={"x": 0 * t})
    sim = Simulator(m)
    y = sim.simulate({"K": 2.5, "tau": 6.0}, exp).outputs["x"]
    y_noisy = y + rng.normal(0, 0.02, y.size)
    return {
        "model": m,
        "experiment": Experiment(time=t, inputs={"u": u}, outputs={"x": y_noisy}),
        "time": t,
        "u": u,
        "x": y_noisy,
        "true": {"K": 2.5, "tau": 6.0},
    }


@pytest.fixture
def first_order_project(first_order_data):
    """A project configured for first-order identification."""
    project = Project(name="test")
    project.model = first_order_data["model"]
    project.experiment = first_order_data["experiment"]
    pt = ParameterTable()
    pt.sync_from_names(["K", "tau"])
    pt.get("K").initial = 1.0
    pt.get("K").lower = 0.01
    pt.get("K").upper = 20.0
    pt.get("tau").initial = 5.0
    pt.get("tau").lower = 0.1
    pt.get("tau").upper = 100.0
    project.parameters = pt
    return project
