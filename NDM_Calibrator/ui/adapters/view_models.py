"""Adapters mapping backend results to UI-displayable data.

Pages read from these adapters instead of reaching into raw scipy/simulation
internals, so the UI stays decoupled from backend details.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np


class IdentificationAdapter:
    """Wrap an identification result dict for display."""

    def __init__(self, entry: Dict[str, Any] | None):
        self.entry = entry or {}
        self.result = self.entry.get("result", {})

    @property
    def algorithm(self) -> str:
        return self.entry.get("algorithm", "")

    @property
    def parameters(self) -> Dict[str, float]:
        return self.result.get("parameters", {})

    @property
    def objective_value(self) -> Optional[float]:
        v = self.result.get("objective_value")
        return float(v) if v is not None else None

    @property
    def success(self) -> bool:
        return bool(self.result.get("success", False))

    @property
    def message(self) -> str:
        return self.result.get("message", "")

    @property
    def runtime(self) -> Optional[float]:
        v = self.result.get("runtime_seconds")
        return float(v) if v is not None else None

    @property
    def seed(self) -> Optional[int]:
        return self.result.get("seed")

    @property
    def is_empty(self) -> bool:
        return not self.entry


class CalibrationAdapter:
    """Wrap the calibration/diagnostics result for display."""

    def __init__(self, data: Dict[str, Any] | None):
        self.data = data or {}

    @property
    def is_empty(self) -> bool:
        return not self.data

    def metric(self, name: str) -> Optional[float]:
        metrics = self.data.get("metrics", {})
        summary = metrics.get("summary", {})
        v = summary.get(name)
        return float(v) if v is not None else None

    def per_output_metric(self, output: str, name: str) -> Optional[float]:
        metrics = self.data.get("metrics", {})
        v = metrics.get(output, {}).get(name)
        return float(v) if v is not None else None

    def residual_stats(self, output: str) -> Dict[str, Any]:
        return self.data.get("residual_stats", {}).get(output, {})

    def residual_diagnosis(self, output: str) -> Dict[str, Any]:
        return self.data.get("residual_diagnosis", {}).get(output, {})

    def sensitivity_summary(self) -> Dict[str, Dict[str, float]]:
        return self.data.get("sensitivity", {}).get("summary", {})

    def identifiability(self) -> Dict[str, Any]:
        return self.data.get("identifiability", {})

    def correlation_matrix(self) -> Optional[np.ndarray]:
        corr = self.data.get("identifiability", {}).get("correlation")
        return np.array(corr, dtype=float) if corr else None

    def residual_series(self, output: str) -> Optional[np.ndarray]:
        res = self.data.get("residuals", {}).get(output)
        return np.array(res, dtype=float) if res else None


class DiagnosticsAdapter(CalibrationAdapter):
    """Alias for CalibrationAdapter (diagnostics page shows the same data)."""


class BootstrapAdapter:
    """Wrap bootstrap result for display."""

    def __init__(self, data: Dict[str, Any] | None):
        self.data = data or {}

    @property
    def is_empty(self) -> bool:
        return not self.data

    @property
    def parameters(self) -> Dict[str, Dict[str, float]]:
        return self.data.get("parameters", {})

    @property
    def n_success(self) -> int:
        return int(self.data.get("n_success", 0))

    @property
    def B(self) -> int:
        return int(self.data.get("B", 0))

    def samples(self, name: str) -> List[float]:
        return self.data.get("parameters", {}).get(name, {}).get("samples", [])


class StabilityAdapter:
    """Wrap multi-start stability result for display."""

    def __init__(self, data: Dict[str, Any] | None):
        self.data = data or {}

    @property
    def is_empty(self) -> bool:
        return not self.data

    @property
    def success_rate(self) -> float:
        return float(self.data.get("success_rate", 0.0))

    @property
    def best_objective(self) -> Optional[float]:
        v = self.data.get("best_objective")
        return float(v) if v is not None else None

    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return self.data.get("parameters", {})
