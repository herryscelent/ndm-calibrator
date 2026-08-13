"""Tests for simulation: analytic comparisons and interpolation."""

from __future__ import annotations

import numpy as np
import pytest

from core.experiment import Experiment
from core.model_definition import DynamicModel
from simulation.discrete_solver import step_map
from simulation.interpolation import linear_interpolation, zero_order_hold
from simulation.ode_solver import ODESolverConfig, solve_ode
from simulation.simulator import Simulator


class TestExponentialDecay:
    def test_matches_analytic(self):
        m = DynamicModel.from_builtin("exponential_decay")
        t = np.linspace(0, 10, 201)
        exp = Experiment(time=t, inputs={}, outputs={"x": 0 * t})
        sim = Simulator(m)
        res = sim.simulate({"k": 0.35}, exp, initial_conditions={"x": 2.0})
        assert res.success
        analytic = 2.0 * np.exp(-0.35 * t)
        assert np.max(np.abs(res.outputs["x"] - analytic)) < 1e-4

    def test_zero_decay_constant(self):
        m = DynamicModel.from_builtin("exponential_decay")
        t = np.linspace(0, 5, 101)
        exp = Experiment(time=t, inputs={}, outputs={"x": 0 * t})
        res = Simulator(m).simulate({"k": 0.0}, exp, initial_conditions={"x": 3.0})
        assert res.success
        assert np.allclose(res.outputs["x"], 3.0, atol=1e-6)


class TestFirstOrder:
    def test_steady_state_approaches_ku(self):
        m = DynamicModel.from_builtin("first_order")
        t = np.linspace(0, 40, 401)
        u = np.ones_like(t)
        exp = Experiment(time=t, inputs={"u": u}, outputs={"x": 0 * t})
        res = Simulator(m).simulate({"K": 2.5, "tau": 6.0}, exp)
        assert res.success
        assert abs(res.outputs["x"][-1] - 2.5) < 0.05

    def test_step_response_rise_time(self):
        """tau determines the 63% rise time."""
        m = DynamicModel.from_builtin("first_order")
        t = np.linspace(0, 30, 3001)
        u = np.where(t >= 1, 1.0, 0.0)
        exp = Experiment(time=t, inputs={"u": u}, outputs={"x": 0 * t})
        res = Simulator(m).simulate({"K": 1.0, "tau": 3.0}, exp)
        assert res.success
        x = res.outputs["x"]
        idx = np.argmin(np.abs(x - 0.63))
        assert abs(t[idx] - 1.0 - 3.0) < 0.5


class TestSolverConfig:
    def test_invalid_method_raises(self):
        with pytest.raises(Exception):
            ODESolverConfig(method="Bogus")

    @pytest.mark.parametrize("method", ["RK45", "DOP853", "Radau", "BDF"])
    def test_all_methods_run(self, method):
        def rhs(t, x):
            return np.array([-0.5 * x[0]])

        t, y, ok, _ = solve_ode(rhs, np.array([1.0]), (0.0, 5.0),
                                t_eval=np.linspace(0, 5, 51),
                                config=ODESolverConfig(method=method))
        assert ok
        assert y.shape[0] == 51

    def test_divergence_reported_not_crashed(self):
        def rhs(t, x):
            return np.array([10.0 * x[0]])

        t, y, ok, msg = solve_ode(rhs, np.array([1.0]), (0.0, 10.0),
                                  t_eval=np.linspace(0, 10, 101))
        assert ok is False or not np.all(np.isfinite(y))


class TestInterpolation:
    def test_zero_order_hold(self):
        t = np.array([0, 1, 2, 3])
        u = np.array([0, 5, 10, 15])
        q = np.array([0.3, 1.9, 3.0, 4.0])
        out = zero_order_hold(t, u, q)
        assert np.allclose(out, [0, 5, 15, 15])

    def test_linear(self):
        t = np.array([0, 1, 2])
        u = np.array([0, 10, 20])
        q = np.array([0.5, 1.5])
        out = linear_interpolation(t, u, q)
        assert np.allclose(out, [5, 15])

    def test_linear_clamps_outside(self):
        t = np.array([0, 1])
        u = np.array([0, 10])
        out = linear_interpolation(t, u, np.array([-1, 5]))
        assert np.allclose(out, [0, 10])


class TestDiscreteSolver:
    def test_linear_map(self):
        def f(x, u, params):
            return params["a"] * x + u["u"]

        traj, ok, msg = step_map(f, np.array([1.0]), {"u": np.array([0.0])}, 5, {"a": 2.0})
        assert ok
        assert traj[-1, 0] == 32.0  # 1 * 2^5

    def test_divergence_reported(self):
        def f(x, u, params):
            return np.array([1e6 * x[0]])

        traj, ok, msg = step_map(f, np.array([1.0]), {}, 100, {})
        assert ok is False or not np.all(np.isfinite(traj))
