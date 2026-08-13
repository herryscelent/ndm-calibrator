"""Parameter identifiability diagnostics based on the local Jacobian.

Computes F = J^T J (Fisher-information-like matrix), its singular values,
condition number, approximate covariance and the parameter correlation matrix.
Warnings are issued for high correlation / rank deficiency / poor conditioning.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from app.constants import (
    CONDITION_NUMBER_HIGH,
    CORRELATION_HIGH_THRESHOLD,
    CORRELATION_WARNING_MESSAGE,
    IDENTIFIABILITY_MAX_SINGULAR_VALUES,
)
from core.exceptions import NDMCError


class IdentifiabilityError(NDMCError):
    """Raised when identifiability cannot be computed."""


def compute_identifiability(S: np.ndarray, sigma2: float = 1.0) -> Dict[str, object]:
    """Analyse the Jacobian J (S) for identifiability.

    ``S`` has shape (n_samples, n_params). ``sigma2`` is the residual variance
    used to scale the approximate covariance (J^T J)^{-1} * sigma2.

    Returns singular values, condition number, covariance (may be None when
    rank deficient), correlation matrix (may be None), and warning messages.
    """
    S = np.asarray(S, dtype=float)
    if S.ndim != 2 or S.shape[1] == 0:
        raise IdentifiabilityError("Jacobian 形状非法")
    n_samples, n_params = S.shape
    if n_samples < n_params:
        raise IdentifiabilityError(
            f"样本数({n_samples})少于参数数({n_params}), 无法计算可辨识性"
        )

    JtJ = S.T @ S
    try:
        singular_values = np.linalg.svd(S, compute_uv=False)
    except np.linalg.LinAlgError as exc:
        raise IdentifiabilityError(f"SVD 失败: {exc}") from exc

    positive = singular_values[singular_values > 1e-12]
    cond = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float("inf")
    rank = int(len(positive))

    covariance = None
    correlation = None
    warnings: List[str] = []

    if rank < n_params:
        warnings.append(
            f"Jacobian 秩亏(rank={rank} < 参数数 {n_params}), 部分参数不可辨识"
        )
    else:
        try:
            inv = np.linalg.inv(JtJ)
            covariance = inv * sigma2
            corr = np.empty_like(inv)
            for i in range(n_params):
                for j in range(n_params):
                    denom = np.sqrt(inv[i, i] * inv[j, j])
                    corr[i, j] = inv[i, j] / denom if denom > 0 else 0.0
            correlation = corr
            # Flag strongly correlated pairs.
            pairs = []
            for i in range(n_params):
                for j in range(i + 1, n_params):
                    if abs(corr[i, j]) > CORRELATION_HIGH_THRESHOLD:
                        pairs.append((i, j, float(corr[i, j])))
            for i, j, rho in pairs:
                warnings.append(
                    f"参数 {i} 与 {j} 相关系数 |rho|={rho:.3f} > {CORRELATION_HIGH_THRESHOLD}: {CORRELATION_WARNING_MESSAGE}"
                )
        except np.linalg.LinAlgError:
            warnings.append("协方差矩阵奇异, 无法计算参数相关矩阵")

    if cond > CONDITION_NUMBER_HIGH:
        warnings.append(f"条件数过大 ({cond:.3e}), 结果可能对数据噪声高度敏感")

    return {
        "singular_values": singular_values.tolist(),
        "condition_number": cond,
        "rank": rank,
        "covariance": covariance.tolist() if covariance is not None else None,
        "correlation": correlation.tolist() if correlation is not None else None,
        "warnings": warnings,
        "n_samples": n_samples,
        "n_parameters": n_params,
    }
