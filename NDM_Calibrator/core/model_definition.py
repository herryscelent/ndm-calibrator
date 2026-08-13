"""Dynamic model definition and safe SymPy parsing.

Two model sources are supported:
  * built-in templates (exponential decay, first-order, second-order,
    logistic, cubic nonlinear)
  * user-defined models described by states/inputs/parameters and a set of
    ODE expressions written in a simple math notation.

Parsing NEVER uses ``eval``. Expressions are parsed with SymPy using an
explicit whitelist of allowed functions and symbols, and validated before a
model can be used for simulation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np
import sympy as sp

from core.exceptions import ModelError, ModelParseError

# Symbols used for differentiation with respect to time.
_TIME_SYMBOL = sp.Symbol("t", real=True)

# Functions allowed inside user expressions. Mapping: name -> sympy function.
_ALLOWED_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
    "sign": sp.sign,
    "tanh": sp.tanh,
}

# Simple regex to find candidate tokens for blacklist checking.
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

_DX_PREFIX = "dx"


@dataclass
class BuiltinModel:
    """Description of a built-in model template."""

    key: str
    label_cn: str
    states: List[str]
    inputs: List[str]
    parameters: List[str]
    rhs_exprs: List[str]  # RHS of each dx_i/dt, in order of `states`
    output_exprs: List[str]  # output equations, keyed by output name below
    outputs: List[str]
    initial_defaults: Dict[str, float]
    parameter_defaults: Dict[str, Dict[str, float]]
    description: str = ""


_BUILTIN_MODELS: Dict[str, BuiltinModel] = {}


def _register(model: BuiltinModel) -> None:
    _BUILTIN_MODELS[model.key] = model


_register(BuiltinModel(
    key="exponential_decay",
    label_cn="指数衰减模型 (dx/dt = -k*x)",
    states=["x"],
    inputs=[],
    parameters=["k"],
    rhs_exprs=["-k*x"],
    outputs=["x"],
    output_exprs=["x"],
    initial_defaults={"x": 1.0},
    parameter_defaults={"k": {"initial": 0.5, "lower": 0.001, "upper": 10.0}},
    description="指数衰减: dx/dt = -k*x, 输出 y = x",
))

_register(BuiltinModel(
    key="first_order",
    label_cn="一阶惯性系统 (dx/dt = -(x + K*u)/tau)",
    states=["x"],
    inputs=["u"],
    parameters=["K", "tau"],
    rhs_exprs=["(-x + K*u)/tau"],
    outputs=["x"],
    output_exprs=["x"],
    initial_defaults={"x": 0.0},
    parameter_defaults={
        "K": {"initial": 1.0, "lower": 0.01, "upper": 20.0},
        "tau": {"initial": 5.0, "lower": 0.01, "upper": 100.0},
    },
    description="一阶惯性系统: dx/dt = (-x + K*u)/tau",
))

_register(BuiltinModel(
    key="second_order",
    label_cn="二阶质量-弹簧-阻尼模型",
    states=["x1", "x2"],
    inputs=["u"],
    parameters=["k", "c", "m"],
    rhs_exprs=["x2", "(-k*x1 - c*x2 + u)/m"],
    outputs=["x1"],
    output_exprs=["x1"],
    initial_defaults={"x1": 0.0, "x2": 0.0},
    parameter_defaults={
        "k": {"initial": 10.0, "lower": 0.1, "upper": 200.0},
        "c": {"initial": 1.0, "lower": 0.01, "upper": 50.0},
        "m": {"initial": 1.0, "lower": 0.01, "upper": 20.0, "free": False},
    },
    description="二阶质量-弹簧-阻尼: dx1/dt=x2, dx2/dt=(-k*x1 - c*x2 + u)/m",
))

_register(BuiltinModel(
    key="logistic",
    label_cn="Logistic 动态模型 (dx/dt = r*x*(1 - x/K))",
    states=["x"],
    inputs=[],
    parameters=["r", "K"],
    rhs_exprs=["r*x*(1 - x/K)"],
    outputs=["x"],
    output_exprs=["x"],
    initial_defaults={"x": 0.1},
    parameter_defaults={
        "r": {"initial": 0.5, "lower": 0.001, "upper": 5.0},
        "K": {"initial": 10.0, "lower": 0.1, "upper": 100.0},
    },
    description="Logistic: dx/dt = r*x*(1 - x/K)",
))

_register(BuiltinModel(
    key="cubic_nonlinear",
    label_cn="非线性动态模型 (dx/dt = -a*x - b*x^3 + c*u)",
    states=["x"],
    inputs=["u"],
    parameters=["a", "b", "c"],
    rhs_exprs=["-a*x - b*x**3 + c*u"],
    outputs=["x"],
    output_exprs=["x"],
    initial_defaults={"x": 0.0},
    parameter_defaults={
        "a": {"initial": 0.5, "lower": 0.001, "upper": 10.0},
        "b": {"initial": 0.5, "lower": 0.001, "upper": 10.0},
        "c": {"initial": 1.0, "lower": 0.001, "upper": 20.0},
    },
    description="非线性: dx/dt = -a*x - b*x^3 + c*u",
))


def builtin_model_keys() -> List[str]:
    return list(_BUILTIN_MODELS.keys())


def builtin_model_labels() -> Dict[str, str]:
    return {key: m.label_cn for key, m in _BUILTIN_MODELS.items()}


def get_builtin_model(key: str) -> BuiltinModel | None:
    return _BUILTIN_MODELS.get(key)


class DynamicModel:
    """A validated continuous-time dynamic model ready for simulation."""

    def __init__(
        self,
        states: List[str],
        inputs: List[str],
        parameters: List[str],
        rhs_exprs: List[str],
        outputs: List[str],
        output_exprs: List[str],
        initial_conditions: Dict[str, float],
        description: str = "",
    ):
        self.states = list(states)
        self.inputs = list(inputs)
        self.parameters = list(parameters)
        self.rhs_exprs = list(rhs_exprs)
        self.outputs = list(outputs)
        self.output_exprs = list(output_exprs)
        self.initial_conditions = dict(initial_conditions)
        self.description = description

        # Compile the symbolic model.
        self._symbols = {
            "states": {name: sp.Symbol(name, real=True) for name in self.states},
            "inputs": {name: sp.Symbol(name, real=True) for name in self.inputs},
            "parameters": {name: sp.Symbol(name, real=True) for name in self.parameters},
        }
        self._parsed_rhs: List[sp.Expr] = []
        self._parsed_outputs: Dict[str, sp.Expr] = {}
        self._compile()

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #
    @classmethod
    def from_builtin(cls, key: str) -> "DynamicModel":
        model = get_builtin_model(key)
        if model is None:
            raise ModelError(f"未知内置模型: {key}")
        return cls(
            states=model.states,
            inputs=model.inputs,
            parameters=model.parameters,
            rhs_exprs=model.rhs_exprs,
            outputs=model.outputs,
            output_exprs=model.output_exprs,
            initial_conditions=model.initial_defaults,
            description=model.description,
        )

    @classmethod
    def from_user_definition(
        cls,
        states: List[str],
        inputs: List[str],
        parameters: List[str],
        dynamics: Dict[str, str],
        outputs: List[str] | None = None,
        output_equations: Dict[str, str] | None = None,
        initial_conditions: Dict[str, float] | None = None,
        description: str = "",
    ) -> "DynamicModel":
        """Build a model from a user-friendly dict definition.

        ``dynamics`` maps "dx1/dt" -> "expr". Outputs default to all states;
        ``output_equations`` maps output-name -> expression in terms of states
        (and optionally inputs/parameters/time).
        """
        states = [s.strip() for s in states]
        inputs = [s.strip() for s in inputs]
        parameters = [s.strip() for s in parameters]
        _check_no_duplicates(states, inputs, parameters)

        rhs_exprs: List[str] = []
        for st in states:
            key = f"{_DX_PREFIX}{st}/dt"
            if key not in dynamics:
                raise ModelParseError(f"缺少状态 {st} 的动态方程 {key}")
            rhs_exprs.append(dynamics[key])

        if outputs is None:
            outputs = list(states)
        if output_equations is None:
            output_equations = {out: out for out in outputs}

        if initial_conditions is None:
            initial_conditions = {st: 0.0 for st in states}

        model = cls(
            states=states,
            inputs=inputs,
            parameters=parameters,
            rhs_exprs=rhs_exprs,
            outputs=list(outputs),
            output_exprs=[output_equations[o] for o in outputs],
            initial_conditions=initial_conditions,
            description=description,
        )
        return model

    # ------------------------------------------------------------------ #
    # Symbolic compilation & validation
    # ------------------------------------------------------------------ #
    def _compile(self) -> None:
        state_syms = self._symbols["states"]
        input_syms = self._symbols["inputs"]
        param_syms = self._symbols["parameters"]

        if len(self.states) != len(self.rhs_exprs):
            raise ModelError(
                f"状态数量({len(self.states)})与方程数量({len(self.rhs_exprs)})不匹配"
            )

        def _parse(expr_str: str, context: str) -> sp.Expr:
            expr_str = expr_str.strip()
            if not expr_str:
                raise ModelParseError(f"{context}: 表达式为空")
            tokens = set(_TOKEN_RE.findall(expr_str))
            blacklist = tokens - set(state_syms) - set(input_syms) - set(param_syms) - set(_ALLOWED_FUNCTIONS)
            # Allow the differential placeholder token "dt" inside "dx/dt" keys
            # is not present here since we only parse RHS expressions.
            if blacklist:
                raise ModelParseError(
                    f"{context}: 使用了未定义符号 {sorted(blacklist)}"
                )
            try:
                parsed = sp.sympify(
                    expr_str,
                    locals={**_ALLOWED_FUNCTIONS, **state_syms, **input_syms, **param_syms},
                    evaluate=True,
                )
            except (sp.SympifyError, TypeError, ValueError, SyntaxError) as exc:
                raise ModelParseError(f"{context}: 表达式无法解析: {exc}") from exc
            if not isinstance(parsed, sp.Expr):
                raise ModelParseError(f"{context}: 表达式未产生有效数学表达式")
            return parsed

        # Parse all RHS equations.
        parsed_rhs = []
        for i, (st, expr) in enumerate(zip(self.states, self.rhs_exprs)):
            parsed = _parse(expr, f"dx{st}/dt")
            parsed_rhs.append(parsed)

        # Validate the RHS does not contain time derivative symbols (dt) misuse.
        for i, (st, expr) in enumerate(zip(self.states, self.rhs_exprs)):
            free = set(parsed_rhs[i].free_symbols)
            illegal = free - set(state_syms.values()) - set(input_syms.values()) - set(param_syms.values())
            illegal = illegal - {_TIME_SYMBOL}
            if illegal:
                raise ModelParseError(
                    f"dx{st}/dt: 表达式中含有非法符号 {[str(s) for s in illegal]}"
                )

        # Parse output equations.
        parsed_outputs = {}
        for out, expr in zip(self.outputs, self.output_exprs):
            parsed = _parse(expr, f"输出 {out}")
            parsed_outputs[out] = parsed

        self._parsed_rhs = parsed_rhs
        self._parsed_outputs = parsed_outputs
        self._validate_initial_conditions()

    def _validate_initial_conditions(self) -> None:
        missing = [st for st in self.states if st not in self.initial_conditions]
        if missing:
            raise ModelError(f"缺少初始条件: {missing}")
        for st in self.states:
            val = self.initial_conditions[st]
            if not np.isfinite(float(val)):
                raise ModelError(f"状态 {st} 初始条件不是有限数值: {val}")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    @property
    def n_states(self) -> int:
        return len(self.states)

    @property
    def n_inputs(self) -> int:
        return len(self.inputs)

    @property
    def n_parameters(self) -> int:
        return len(self.parameters)

    @property
    def n_outputs(self) -> int:
        return len(self.outputs)

    @property
    def is_autonomous(self) -> bool:
        return self.n_inputs == 0

    def requires_input(self, name: str) -> bool:
        return name in self.inputs

    def rhs_lambdified(self, parameter_values: Dict[str, float]):
        """Return a callable rhs(t, x) for a given parameter dict."""
        state_vec = sp.Matrix(self._parsed_rhs)
        state_vec = state_vec.xreplace(
            {self._symbols["parameters"][name]: sp.Float(float(value)) for name, value in parameter_values.items()}
        )
        func = sp.lambdify(
            (_TIME_SYMBOL, sp.Matrix(list(self._symbols["states"].values()))),
            state_vec,
            modules="numpy",
        )
        return func

    def output_lambdified(self, parameter_values: Dict[str, float]):
        """Return a callable output(x, u_by_name) -> dict output_name -> value."""
        x_syms = list(self._symbols["states"].values())
        u_syms = list(self._symbols["inputs"].values())
        outputs = {
            name: expr.xreplace(
                {self._symbols["parameters"][p]: sp.Float(float(parameter_values[p])) for p in parameter_values}
            )
            for name, expr in self._parsed_outputs.items()
        }
        func = sp.lambdify(
            (sp.Matrix(x_syms), sp.Matrix(u_syms)),
            [outputs[name] for name in self.outputs],
            modules="numpy",
        )

        def _call(x: np.ndarray, u_by_name: Dict[str, float]) -> Dict[str, float]:
            u_vals = np.array([u_by_name[name] for name in self.inputs], dtype=float) if self.inputs else np.array([])
            result = func(x, u_vals)
            if not isinstance(result, (list, tuple)):
                result = [result]
            return {name: float(v) for name, v in zip(self.outputs, result)}

        return _call

    def initial_state_vector(self) -> np.ndarray:
        return np.array([float(self.initial_conditions[st]) for st in self.states], dtype=float)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": "user",
            "description": self.description,
            "states": self.states,
            "inputs": self.inputs,
            "parameters": self.parameters,
            "dynamics": {f"dx{st}/dt": expr for st, expr in zip(self.states, self.rhs_exprs)},
            "outputs": self.outputs,
            "output_equations": dict(zip(self.outputs, self.output_exprs)),
            "initial_conditions": {k: float(v) for k, v in self.initial_conditions.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DynamicModel":
        if data.get("kind") == "builtin":
            return cls.from_builtin(data["builtin_key"])
        return cls.from_user_definition(
            states=data["states"],
            inputs=data["inputs"],
            parameters=data["parameters"],
            dynamics=data["dynamics"],
            outputs=data["outputs"],
            output_equations=data["output_equations"],
            initial_conditions={k: float(v) for k, v in data["initial_conditions"].items()},
            description=data.get("description", ""),
        )


def _check_no_duplicates(states: List[str], inputs: List[str], parameters: List[str]) -> None:
    seen: Dict[str, str] = {}
    for category, names in (("状态", states), ("输入", inputs), ("参数", parameters)):
        for name in names:
            if not name:
                raise ModelParseError(f"{category}名不能为空")
            if name in seen:
                raise ModelParseError(f"符号 '{name}' 重名 (已作为{seen[name]})")
            seen[name] = category
