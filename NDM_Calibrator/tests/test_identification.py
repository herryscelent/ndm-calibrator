"""Tests for identification: parameter recovery and reproducibility."""

from __future__ import annotations

import numpy as np
import pytest

from identification.manager import algorithm_keys, run_algorithm


class TestIdentificationRecovery:
    def test_least_squares_recovers_first_order(self, first_order_project):
        r = run_algorithm(first_order_project, "least_squares", {})
        assert r.success
        assert abs(r.parameters["K"] - 2.5) < 0.1
        assert abs(r.parameters["tau"] - 6.0) < 0.3

    def test_nelder_mead_recovers(self, first_order_project):
        r = run_algorithm(first_order_project, "nelder_mead", {"max_iterations": 2000})
        assert r.success
        assert abs(r.parameters["K"] - 2.5) < 0.15
        assert abs(r.parameters["tau"] - 6.0) < 0.4

    def test_differential_evolution_recovers(self, first_order_project):
        r = run_algorithm(first_order_project, "differential_evolution", {"seed": 42, "max_iterations": 300})
        assert abs(r.parameters["K"] - 2.5) < 0.1
        assert abs(r.parameters["tau"] - 6.0) < 0.3

    def test_multistart_recovers(self, first_order_project):
        r = run_algorithm(first_order_project, "multistart", {"seed": 42, "n_starts": 12})
        assert r.success
        assert abs(r.parameters["K"] - 2.5) < 0.15
        assert abs(r.parameters["tau"] - 6.0) < 0.3
        assert len(r.extra["all_solutions"]) == 12

    def test_exponential_decay_noiseless_exact(self):
        from core.experiment import Experiment
        from core.model_definition import DynamicModel
        from core.parameter import ParameterTable
        from core.project import Project
        from simulation.simulator import Simulator

        m = DynamicModel.from_builtin("exponential_decay")
        t = np.linspace(0, 10, 201)
        exp = Experiment(time=t, inputs={}, outputs={"x": 0 * t})
        y = Simulator(m).simulate({"k": 0.35}, exp, initial_conditions={"x": 1.0}).outputs["x"]
        project = Project(name="t")
        project.model = m
        project.experiment = Experiment(time=t, inputs={}, outputs={"x": y})
        pt = ParameterTable()
        pt.sync_from_names(["k"])
        pt.get("k").initial = 0.1
        pt.get("k").lower = 0.001
        pt.get("k").upper = 5.0
        project.parameters = pt
        r = run_algorithm(project, "least_squares", {})
        assert abs(r.parameters["k"] - 0.35) < 1e-4


class TestReproducibility:
    def test_de_same_seed_same_result(self, first_order_project):
        r1 = run_algorithm(first_order_project, "differential_evolution", {"seed": 7})
        r2 = run_algorithm(first_order_project, "differential_evolution", {"seed": 7})
        assert r1.parameters == r2.parameters

    def test_multistart_same_seed_same_result(self, first_order_project):
        r1 = run_algorithm(first_order_project, "multistart", {"seed": 3, "n_starts": 8})
        r2 = run_algorithm(first_order_project, "multistart", {"seed": 3, "n_starts": 8})
        assert r1.parameters == r2.parameters

    def test_seed_recorded(self, first_order_project):
        r = run_algorithm(first_order_project, "differential_evolution", {"seed": 9})
        assert r.seed == 9


class TestObjective:
    def test_exponential_recovery_uses_sse(self, first_order_project):
        first_order_project.settings["identification"] = {"objective": "mse"}
        r = run_algorithm(first_order_project, "least_squares", {})
        assert abs(r.parameters["K"] - 2.5) < 0.15


def test_algorithm_keys_available():
    keys = algorithm_keys()
    assert set(keys) == {"least_squares", "nelder_mead", "differential_evolution", "multistart"}
