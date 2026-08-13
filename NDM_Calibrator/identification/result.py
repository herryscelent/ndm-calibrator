"""Result data structure returned by every identification algorithm."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class IdentificationResult:
    algorithm: str
    parameters: Dict[str, float]          # free parameter name -> estimated value
    objective_value: float
    success: bool
    message: str = ""
    n_evaluations: int = 0
    runtime_seconds: float = 0.0
    seed: Optional[int] = None
    # Extra per-algorithm payload (local optima, history, ...).
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def names(self) -> List[str]:
        return list(self.parameters.keys())

    @property
    def values(self) -> np.ndarray:
        return np.array(list(self.parameters.values()), dtype=float)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "parameters": self.parameters,
            "objective_value": float(self.objective_value),
            "success": self.success,
            "message": self.message,
            "n_evaluations": self.n_evaluations,
            "runtime_seconds": float(self.runtime_seconds),
            "seed": self.seed,
            "extra": self.extra,
        }
