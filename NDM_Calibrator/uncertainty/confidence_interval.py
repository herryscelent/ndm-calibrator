"""Confidence-interval helpers.

The bootstrap result is reported as a *percentile interval* (2.5%–97.5%),
which is explicitly labelled in the UI and reports so it is not confused with
a strict statistical confidence interval.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np


def percentile_interval(samples: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Return the (1-alpha) percentile interval of a sample."""
    arr = np.asarray(samples, dtype=float)
    lo = 100 * alpha / 2
    hi = 100 * (1 - alpha / 2)
    return {
        "lower": float(np.percentile(arr, lo)),
        "upper": float(np.percentile(arr, hi)),
        "median": float(np.median(arr)),
    }


def summarize_samples(samples: List[float]) -> Dict[str, float]:
    arr = np.asarray(samples, dtype=float)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }
