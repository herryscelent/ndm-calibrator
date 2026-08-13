"""Simulator: run a DynamicModel against an Experiment to produce predicted
output series.

For a given parameter set, the symbolic RHS and output equations are
substituted once and lambdified, then used throughout the integration. Inputs
u(t) are interpolated onto whatever time grid the integrator requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
from sympy import Matrix, lambdify

from core.exceptions import SimulationError
from core.experiment import Experiment
from core.model_definition import DynamicModel
from simulation.interpolation import linear_interpolation, zero_order_hold
from simulation.ode_solver import ODESolverConfig, solve_ode


@dataclass
class SimulationResult:
    t: np.ndarray
    states: np.ndarray                 # (n_t, n_states)
    outputs: Dict[str, np.ndarray]     # output name -> (n_t,)
    success: bool
    message: str


class Simulator:
    """Simulate a model for given parameters, initial conditions and input."""

    def __init__(self, model: DynamicModel, solver_config: ODESolverConfig | None = None):
        self.model = model
        self.solver_config = solver_config or ODESolverConfig()

    def simulate(
        self,
        parameters: Dict[str, float],
        experiment: Experiment,
        initial_conditions: Optional[Dict[str, float]] = None,
        input_interpolation: str = "linear",
    ) -> SimulationResult:
        """Simulate the model and return outputs on the experiment grid.

        ``parameters`` must contain a value for every model parameter.
        """
        _check_parameter_completeness(self.model, parameters)

        x0 = self._initial_state(initial_conditions)
        u_interp = self._build_input_callables(experiment, input_interpolation)
        rhs = _compile_rhs(self.model, parameters)

        def _rhs(t: float, x: np.ndarray) -> np.ndarray:
            u_vals = np.array(
                [u_interp[name](t) for name in self.model.inputs], dtype=float
            ) if self.model.inputs else np.array([])
            return rhs(x, u_vals)

        t_eval = experiment.time
        t_span = (float(t_eval[0]), float(t_eval[-1]))
        t, X, success, message = solve_ode(_rhs, x0, t_span, t_eval=t_eval, config=self.solver_config)
        if not success:
            return SimulationResult(t=t, states=X, outputs={}, success=False, message=message)

        outputs = self._evaluate_outputs(X, parameters, experiment)
        return SimulationResult(t=t, states=X, outputs=outputs, success=True, message=message)

    # ------------------------------------------------------------------ #
    def _initial_state(self, initial_conditions: Optional[Dict[str, float]]) -> np.ndarray:
        x0 = self.model.initial_state_vector()
        if initial_conditions:
            for st, val in initial_conditions.items():
                if st not in self.model.states:
                    raise SimulationError(f"未知状态初始条件: {st}")
                x0[self.model.states.index(st)] = float(val)
        return x0

    def _build_input_callables(self, experiment: Experiment, interpolation: str):
        if interpolation not in ("linear", "zero_order_hold"):
            raise SimulationError(f"未知输入插值方式: {interpolation}")
        callables = {}
        for name in self.model.inputs:
            if name not in experiment.inputs:
                raise SimulationError(f"模型需要输入 '{name}', 但数据中没有该输入")
            t_src = experiment.time
            u_src = experiment.inputs[name]

            def _make(ts, us, mode):
                if mode == "zero_order_hold":
                    def _interp(t):
                        v = zero_order_hold(ts, us, np.atleast_1d(t))
                        return float(v[0])
                    return _interp
                def _interp(t):
                    v = linear_interpolation(ts, us, np.atleast_1d(t))
                    return float(v[0])
                return _interp

            callables[name] = _make(t_src, u_src, interpolation)
        return callables

    def _evaluate_outputs(self, X, parameters, experiment) -> Dict[str, np.ndarray]:
        u_interp = self._build_input_callables(experiment, "linear")
        output_func = _compile_outputs(self.model, parameters)
        n = X.shape[0]
        result: Dict[str, np.ndarray] = {
            name: np.empty(n, dtype=float) for name in self.model.outputs
        }
        for i, t in enumerate(experiment.time):
            u_vals = {
                name: interp(t) for name, interp in u_interp.items()
            } if self.model.inputs else {}
            values = output_func(X[i], u_vals)
            for name in self.model.outputs:
                result[name][i] = values[name]
        return result


def _compile_rhs(model: DynamicModel, parameters: Dict[str, float]):
    """Return callable rhs(x, u) with parameters already substituted."""
    state_syms = [model._symbols["states"][s] for s in model.states]
    u_syms = [model._symbols["inputs"][s] for s in model.inputs]
    param_syms = model._symbols["parameters"]
    substituted = Matrix(model._parsed_rhs).xreplace(
        {param_syms[p]: float(parameters[p]) for p in model.parameters}
    )
    func = lambdify((state_syms, u_syms), substituted, modules="numpy")

    def rhs(x: np.ndarray, u_vals: np.ndarray) -> np.ndarray:
        return np.asarray(func(x, u_vals), dtype=float).reshape(-1)

    return rhs


def _compile_outputs(model: DynamicModel, parameters: Dict[str, float]):
    """Return callable output(x, u_by_name) -> {output_name: float}."""
    state_syms = [model._symbols["states"][s] for s in model.states]
    u_syms = [model._symbols["inputs"][s] for s in model.inputs]
    param_syms = model._symbols["parameters"]
    funcs = {}
    for name in model.outputs:
        expr = model._parsed_outputs[name].xreplace(
            {param_syms[p]: float(parameters[p]) for p in model.parameters}
        )
        funcs[name] = lambdify((state_syms, u_syms), expr, modules="numpy")

    def _call(x: np.ndarray, u_by_name: Dict[str, float]) -> Dict[str, float]:
        u_vals = np.array(
            [u_by_name[name] for name in model.inputs], dtype=float
        ) if model.inputs else np.array([])
        out = {}
        for name in model.outputs:
            out[name] = float(np.asarray(funcs[name](x, u_vals), dtype=float).item())
        return out

    return _call


def _check_parameter_completeness(model: DynamicModel, parameters: Dict[str, float]) -> None:
    missing = [p for p in model.parameters if p not in parameters]
    if missing:
        raise SimulationError(f"缺少模型参数值: {missing}")
