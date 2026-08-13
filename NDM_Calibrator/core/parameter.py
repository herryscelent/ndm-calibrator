"""Parameter domain object.

A model parameter has a name, an initial guess, a lower/upper bound and a
status (free to be identified, or fixed at its initial value).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from app.constants import PARAMETER_BOUND_DEFAULT_LOWER, PARAMETER_BOUND_DEFAULT_UPPER, PARAMETER_INITIAL_DEFAULT


@dataclass
class Parameter:
    """A single model parameter with bounds and identification status."""

    name: str
    initial: float = PARAMETER_INITIAL_DEFAULT
    lower: float = PARAMETER_BOUND_DEFAULT_LOWER
    upper: float = PARAMETER_BOUND_DEFAULT_UPPER
    free: bool = True

    @property
    def is_free(self) -> bool:
        return self.free

    def validate(self) -> None:
        """Validate bounds ordering. Raises ValueError on failure."""
        if not self.lower < self.initial < self.upper:
            raise ValueError(
                f"参数 {self.name} 范围非法: 要求 lower < initial < upper, "
                f"实际为 lower={self.lower}, initial={self.initial}, upper={self.upper}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initial": self.initial,
            "lower": self.lower,
            "upper": self.upper,
            "free": self.free,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parameter":
        return cls(
            name=data["name"],
            initial=float(data.get("initial", PARAMETER_INITIAL_DEFAULT)),
            lower=float(data.get("lower", PARAMETER_BOUND_DEFAULT_LOWER)),
            upper=float(data.get("upper", PARAMETER_BOUND_DEFAULT_UPPER)),
            free=bool(data.get("free", True)),
        )


class ParameterTable:
    """Ordered collection of Parameters."""

    def __init__(self, parameters: Dict[str, Parameter] | None = None):
        self._parameters: Dict[str, Parameter] = dict(parameters or {})

    def __len__(self) -> int:
        return len(self._parameters)

    def __iter__(self):
        return iter(self._parameters.values())

    def __contains__(self, name: str) -> bool:
        return name in self._parameters

    def get(self, name: str) -> Parameter | None:
        return self._parameters.get(name)

    def add(self, parameter: Parameter) -> None:
        if not parameter.name:
            raise ValueError("参数名不能为空")
        if parameter.name in self._parameters:
            raise ValueError(f"参数 {parameter.name} 已存在")
        self._parameters[parameter.name] = parameter

    def remove(self, name: str) -> None:
        if name not in self._parameters:
            raise KeyError(f"参数 {name} 不存在")
        del self._parameters[name]

    def update(self, parameter: Parameter) -> None:
        if parameter.name not in self._parameters:
            raise KeyError(f"参数 {parameter.name} 不存在")
        self._parameters[parameter.name] = parameter

    @property
    def names(self) -> list[str]:
        return list(self._parameters.keys())

    def free_names(self) -> list[str]:
        return [name for name, p in self._parameters.items() if p.free]

    def free_parameters(self) -> list[Parameter]:
        return [p for p in self._parameters.values() if p.free]

    def to_dict(self) -> Dict[str, Any]:
        return {name: p.to_dict() for name, p in self._parameters.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParameterTable":
        table = cls()
        for name, p in data.items():
            table.add(Parameter.from_dict({**p, "name": p.get("name", name)}))
        return table

    def sync_from_names(self, names: list[str], keep_existing: bool = True) -> list[str]:
        """Add missing parameters with defaults. Returns names that were added."""
        added = []
        for name in names:
            if name not in self._parameters:
                self._parameters[name] = Parameter(name=name)
                added.append(name)
        if not keep_existing:
            for name in list(self._parameters.keys()):
                if name not in names:
                    del self._parameters[name]
        return added
