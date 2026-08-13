"""Experiment data model.

Holds the imported time series after field mapping: time vector, one or more
input series and one or more output series, all stored as plain NumPy arrays.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np

from core.exceptions import DataValidationError


@dataclass
class Experiment:
    """A mapped experiment dataset."""

    time: np.ndarray
    inputs: Dict[str, np.ndarray] = field(default_factory=dict)
    outputs: Dict[str, np.ndarray] = field(default_factory=dict)
    ignored: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    @property
    def n_points(self) -> int:
        return int(self.time.size)

    @property
    def n_inputs(self) -> int:
        return len(self.inputs)

    @property
    def n_outputs(self) -> int:
        return len(self.outputs)

    def validate(self) -> None:
        n = self.time.size
        if n == 0:
            raise DataValidationError("实验数据为空")
        if not np.all(np.isfinite(self.time)):
            raise DataValidationError("时间列包含非有限值")
        for name, arr in self.inputs.items():
            if arr.size != n:
                raise DataValidationError(
                    f"输入 {name} 长度({arr.size})与时间长度({n})不一致"
                )
        for name, arr in self.outputs.items():
            if arr.size != n:
                raise DataValidationError(
                    f"输出 {name} 长度({arr.size})与时间长度({n})不一致"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_points": self.n_points,
            "inputs": list(self.inputs.keys()),
            "outputs": list(self.outputs.keys()),
            "ignored": self.ignored,
        }
