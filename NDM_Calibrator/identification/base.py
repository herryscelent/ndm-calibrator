"""Base machinery for parameter identification.

Provides the scalar objective used by all algorithms. The objective builds a
parameter dict (fixed parameters keep their table values, free parameters get
the candidate values), runs a simulation and evaluates the loss on the mapped
experiment outputs.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from app.constants import ODE_DEFAULT_METHOD
from core.experiment import Experiment
from core.model_definition import DynamicModel
from core.objective import ObjectiveConfig, aggregate_objectives, evaluate_objective
from core.parameter import Parameter
from simulation.ode_solver import ODESolverConfig
from simulation.simulator import Simulator


def check_cancelled(options: Dict[str, Any] | None) -> None:
    """Raise a domain error when a UI worker requested cancellation.

    The token is intentionally carried in the transient options dict instead
    of the persisted project settings.  Keeping this helper in the domain
    layer avoids importing Qt worker classes into numerical code.
    """

    token = options.get("_cancel_token") if options else None
    if token is not None and token.cancelled():
        from core.exceptions import OptimizationError

        raise OptimizationError("操作已取消")


class IdentificationContext:
    """Encapsulates everything an objective function needs from the project."""

    def __init__(
        self,
        model: DynamicModel,
        experiment: Experiment,
        fixed_parameters: Dict[str, float],
        free_names: List[str],
        objective_config: ObjectiveConfig | None = None,
        solver_config: ODESolverConfig | None = None,
        input_interpolation: str = "linear",
        initial_conditions: Optional[Dict[str, float]] = None,
    ):
        self.model = model
        self.experiment = experiment
        self.fixed_parameters = dict(fixed_parameters)
        self.free_names = list(free_names)
        self.objective_config = objective_config or ObjectiveConfig()
        self.solver_config = solver_config or ODESolverConfig()
        self.input_interpolation = input_interpolation
        self.initial_conditions = initial_conditions
        self.simulator = Simulator(model, solver_config)
        # Precompute per-output scalar (measured) slices.
        self._measured = {name: experiment.outputs[name] for name in model.outputs}

    def build_parameter_dict(self, free_values: np.ndarray) -> Dict[str, float]:
        params = dict(self.fixed_parameters)
        params.update({name: float(v) for name, v in zip(self.free_names, free_values)})
        return params

    def evaluate(self, free_values: np.ndarray) -> float:
        """Return the scalar objective for a candidate free-parameter vector."""
        params = self.build_parameter_dict(free_values)
        sim_result = self.simulator.simulate(
            params,
            self.experiment,
            initial_conditions=self.initial_conditions,
            input_interpolation=self.input_interpolation,
        )
        if not sim_result.success:
            return np.inf
        # Compute weighted aggregate over outputs.
        per_output = {}
        for name in self.model.outputs:
            measured = self._measured[name]
            predicted = sim_result.outputs[name]
            per_output[name] = evaluate_objective(
                measured, predicted, self.objective_config
            )
        return aggregate_objectives(per_output, self.objective_config)

    def predict_outputs(self, free_values: np.ndarray) -> Dict[str, np.ndarray]:
        """Run a simulation and return predicted outputs (for plots)."""
        params = self.build_parameter_dict(free_values)
        sim_result = self.simulator.simulate(
            params,
            self.experiment,
            initial_conditions=self.initial_conditions,
            input_interpolation=self.input_interpolation,
        )
        if not sim_result.success:
            raise RuntimeError(f"模拟失败: {sim_result.message}")
        return sim_result.outputs

    def measured_outputs(self) -> Dict[str, np.ndarray]:
        return dict(self._measured)


def build_context(project) -> IdentificationContext:
    """Construct an IdentificationContext from a Project (with stored settings)."""
    model = project.model
    free_params: List[Parameter] = project.parameters.free_parameters()
    fixed = {
        p.name: p.initial for p in project.parameters
        if not p.free
    }
    settings = project.settings.get("identification", {})
    objective_config = ObjectiveConfig(
        type=settings.get("objective", "sse"),
        huber_delta=settings.get("huber_delta", 1.0),
    )
    solver_config = ODESolverConfig(
        method=settings.get("solver_method", ODE_DEFAULT_METHOD),
        rtol=settings.get("rtol", 1e-6),
        atol=settings.get("atol", 1e-9),
        max_step=settings.get("max_step"),
    )
    ctx = IdentificationContext(
        model=model,
        experiment=project.experiment,
        fixed_parameters=fixed,
        free_names=[p.name for p in free_params],
        objective_config=objective_config,
        solver_config=solver_config,
        input_interpolation=settings.get("input_interpolation", "linear"),
        initial_conditions=project.settings.get("initial_conditions"),
    )
    return ctx


def bounds_and_initial(project) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (lower, upper, x0) arrays for free parameters in table order."""
    free_params = project.parameters.free_parameters()
    lower = np.array([p.lower for p in free_params], dtype=float)
    upper = np.array([p.upper for p in free_params], dtype=float)
    x0 = np.array([p.initial for p in free_params], dtype=float)
    return lower, upper, x0
