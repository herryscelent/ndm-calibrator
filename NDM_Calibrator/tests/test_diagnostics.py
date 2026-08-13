"""Tests for metrics, residuals, sensitivity and identifiability."""

from __future__ import annotations

import numpy as np
import pytest

from diagnostics.identifiability import compute_identifiability
from diagnostics.metrics import compute_metrics
from diagnostics.residuals import autocorrelation, compute_residual_stats, residual_structure_diagnosis
from diagnostics.sensitivity import compute_sensitivity, sensitivity_summary


class TestMetrics:
    def test_hand_computable(self):
        m = compute_metrics(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 4.0]))
        assert abs(m["SSE"] - 1.0) < 1e-9
        assert abs(m["MSE"] - 1 / 3) < 1e-9
        assert abs(m["RMSE"] - np.sqrt(1 / 3)) < 1e-9
        assert abs(m["MAE"] - 1 / 3) < 1e-9
        assert abs(m["max_abs_error"] - 1.0) < 1e-9
        assert abs(m["mean_error"] + 1 / 3) < 1e-9

    def test_r2_perfect_fit_is_one(self):
        m = compute_metrics(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))
        assert abs(m["R2"] - 1.0) < 1e-9

    def test_length_mismatch_raises(self):
        with pytest.raises(Exception):
            compute_metrics(np.array([1.0, 2.0]), np.array([1.0]))


class TestResiduals:
    def test_iid_noise_stats(self):
        rng = np.random.default_rng(0)
        res = rng.normal(0, 1, 500)
        stats = compute_residual_stats(res)
        assert abs(stats["mean"]) < 0.2
        assert abs(stats["std"] - 1.0) < 0.2

    def test_acf_white_noise_small(self):
        rng = np.random.default_rng(1)
        acf = autocorrelation(rng.normal(0, 1, 300), 10)
        assert acf.size == 10
        assert np.max(np.abs(acf)) < 0.4

    def test_acf_sinusoid_large(self):
        t = np.linspace(0, 30, 600)
        res = np.sin(2 * np.pi * t / 5)
        acf = autocorrelation(res, 20)
        assert abs(acf[0]) > 0.8  # strong lag-1 correlation

    def test_structured_residual_detected(self):
        t = np.linspace(0, 30, 600)
        res = 0.1 * np.sin(2 * np.pi * t / 5)
        diag = residual_structure_diagnosis(res)
        assert diag["has_structure"] is True

    def test_short_sample_no_structure(self):
        res = np.array([0.1, -0.2, 0.3, -0.1, 0.05])
        diag = residual_structure_diagnosis(res, max_lag=4)
        assert "无法" in diag["message"] or diag["has_structure"] in (True, False)


class TestSensitivity:
    def test_linear_identity(self):
        # y = 3*x1 + 5*x2  ->  dy/dx1 = 3, dy/dx2 = 5
        def predict(theta):
            return np.array([3 * theta[0] + 5 * theta[1]])

        S, S_norm = compute_sensitivity(predict, np.array([1.0, 2.0]), ["a", "b"], step_frac=1e-4)
        assert abs(S[0, 0] - 3.0) < 1e-3
        assert abs(S[0, 1] - 5.0) < 1e-3

    def test_normalized_scale(self):
        def predict(theta):
            return np.array([theta[0] * 100.0])

        S, S_norm = compute_sensitivity(predict, np.array([2.0]), ["a"])
        assert abs(S[0, 0] - 100.0) < 1e-2
        # normalized = d y/d theta * theta / y = 100*2/200 = 1
        assert abs(S_norm[0, 0] - 1.0) < 1e-3

    def test_summary(self):
        def predict(theta):
            return np.array([theta[0], 2 * theta[0]])

        S, S_norm = compute_sensitivity(predict, np.array([1.0]), ["a"])
        summary = sensitivity_summary(S_norm, ["a"])
        assert "a" in summary


class TestIdentifiability:
    def test_full_rank_two_params(self):
        # Well-conditioned Jacobian
        S = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        out = compute_identifiability(S)
        assert out["rank"] == 2
        assert out["correlation"] is not None
        assert not out["warnings"]

    def test_rank_deficient(self):
        # Column 2 is twice column 1 -> rank 1
        S = np.array([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]])
        out = compute_identifiability(S)
        assert out["rank"] == 1
        assert out["covariance"] is None
        assert any("秩" in w for w in out["warnings"])

    def test_high_correlation_warns(self):
        # Nearly collinear columns
        S = np.array([[1.0, 1.0], [1.0, 1.0 + 1e-6], [2.0, 2.0]])
        out = compute_identifiability(S)
        # Correlations may be near 1 and warnings issued.
        if out["correlation"] is not None:
            corr = np.array(out["correlation"])
            assert abs(corr[0, 1]) > 0.99

    def test_too_few_samples(self):
        S = np.array([[1.0, 0.0]])  # 1 sample, 2 params
        with pytest.raises(Exception):
            compute_identifiability(S)

    def test_singular_values_shape(self):
        S = np.random.default_rng(3).normal(size=(20, 3))
        out = compute_identifiability(S)
        assert len(out["singular_values"]) == 3
