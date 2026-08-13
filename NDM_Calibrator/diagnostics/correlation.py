"""Parameter correlation helpers (thin wrapper over identifiability output)."""

from __future__ import annotations

import numpy as np


def correlation_matrix(covariance: np.ndarray) -> np.ndarray | None:
    """Convert a covariance matrix into a Pearson correlation matrix.

    Returns None when the covariance is singular or off-diagonal zero.
    """
    cov = np.asarray(covariance, dtype=float)
    n = cov.shape[0]
    if cov.shape != (n, n):
        return None
    corr = np.zeros((n, n))
    diag = np.sqrt(np.diag(cov))
    if np.any(diag <= 0):
        return None
    for i in range(n):
        for j in range(n):
            corr[i, j] = cov[i, j] / (diag[i] * diag[j])
    return corr
