"""Objective functions used during parameter identification.

Each objective is a pure function returning a scalar loss given predicted and
measured output arrays. The residual-style objectives (SSE, MSE, RMSE, MAE)
are used directly with scipy least_squares as residuals; the others reduce to
a scalar used by Nelder-Mead / DE / multi-start.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from core.exceptions import NDMCError


class ObjectiveError(NDMCError):
    """Raised when an objective configuration is invalid."""


@dataclass(frozen=True)
class ObjectiveConfig:
    """Configuration of the objective (loss) type.

    ``type`` is one of: sse, mse, rmse, mae, huber.
    ``weights`` optionally maps output-name -> scalar weight (default all 1).
    """

    type: str = "sse"
    weights: dict[str, float] | None = None
    huber_delta: float = 1.0

    def __post_init__(self):
        allowed = {"sse", "mse", "rmse", "mae", "huber"}
        if self.type not in allowed:
            raise ObjectiveError(
                f"未知目标函数类型 '{self.type}', 允许: {sorted(allowed)}"
            )
        if self.huber_delta <= 0:
            raise ObjectiveError("Huber delta 必须大于 0")

    def weight_for(self, output_name: str) -> float:
        if self.weights is None:
            return 1.0
        return float(self.weights.get(output_name, 1.0))


def _residual_vector(measured: np.ndarray, predicted: np.ndarray, weight: float) -> np.ndarray:
    diff = measured - predicted
    if np.any(~np.isfinite(diff)):
        raise ObjectiveError("预测或实测包含非有限值")
    return np.sqrt(weight) * diff


def residuals_for_objective(
    measured: np.ndarray,
    predicted: np.ndarray,
    config: ObjectiveConfig,
    weight: float = 1.0,
) -> np.ndarray:
    """Return a per-point residual vector for least_squares.

    SSE and MSE use sqrt-weighted residuals (so that sum-of-squares of the
    residuals equals the objective). RMSE/MAE/Huber use direct residual so the
    optimiser drives the same quantity the user sees.
    """
    if config.type in {"sse", "mse"}:
        return _residual_vector(measured, predicted, weight)
    return _residual_vector(measured, predicted, 1.0)


def evaluate_objective(
    measured: np.ndarray, predicted: np.ndarray, config: ObjectiveConfig
) -> float:
    """Evaluate the scalar objective value for a single output series.

    NaN-free requirement is enforced here; the caller is expected to pass
    clean arrays (missing points handled upstream by interpolation).
    """
    if measured.size != predicted.size:
        raise ObjectiveError("measured 与 predicted 长度不一致")
    if measured.size == 0:
        raise ObjectiveError("目标函数输入为空")
    diff = measured - predicted
    valid = np.isfinite(diff)
    if not np.all(valid):
        raise ObjectiveError("目标函数包含非有限值")

    if config.type == "sse":
        return float(np.sum(diff**2))
    if config.type == "mse":
        return float(np.mean(diff**2))
    if config.type == "rmse":
        return float(np.sqrt(np.mean(diff**2)))
    if config.type == "mae":
        return float(np.mean(np.abs(diff)))
    if config.type == "huber":
        delta = config.huber_delta
        abs_diff = np.abs(diff)
        quadratic = abs_diff <= delta
        return float(
            np.mean(
                np.where(quadratic, 0.5 * diff**2, delta * (abs_diff - 0.5 * delta))
            )
        )
    raise ObjectiveError(f"未知目标函数类型 '{config.type}'")


def make_scalar_objective(
    measured: np.ndarray, predicted: np.ndarray, config: ObjectiveConfig
) -> Callable[[], float]:
    """Factory for a zero-argument scalar objective (handy for reports)."""
    return lambda: evaluate_objective(measured, predicted, config)


def aggregate_objectives(
    per_output: dict[str, float], config: ObjectiveConfig
) -> float:
    """Combine per-output objective values into one scalar.

    The multi-output scalar objective is a weighted mean of per-output
    objectives so outputs are comparable.
    """
    if not per_output:
        raise ObjectiveError("没有可聚合的输出目标值")
    weights = config.weights or {}
    total = sum(weights.get(name, 1.0) for name in per_output)
    return sum(per_output[name] * weights.get(name, 1.0) for name in per_output) / total
