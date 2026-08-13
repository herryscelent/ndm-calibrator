"""Tests for uncertainty: bootstrap and stability."""

from __future__ import annotations

import numpy as np
import pytest

from identification.manager import run_algorithm
from uncertainty.bootstrap import run_bootstrap
from uncertainty.stability import run_multistart_stability


@pytest.fixture
def fitted_project(first_order_project):
    """A project with a completed identification result."""
    r = run_algorithm(first_order_project, "least_squares", {})
    first_order_project.results["identification"] = {
        "algorithm": "least_squares",
        "result": r.to_dict(),
    }
    return first_order_project


class TestBootstrap:
    def test_output_dimensions(self, fitted_project):
        result = run_bootstrap(fitted_project, {"B": 10, "seed": 1})
        assert result["n_success"] == 10
        assert set(result["parameters"].keys()) == {"K", "tau"}
        for name, info in result["parameters"].items():
            assert len(info["samples"]) == 10
            assert info["p2_5"] < info["median"] < info["p97_5"]

    def test_seed_reproducibility(self, fitted_project):
        r1 = run_bootstrap(fitted_project, {"B": 8, "seed": 11})
        r2 = run_bootstrap(fitted_project, {"B": 8, "seed": 11})
        for name in r1["parameters"]:
            assert r1["parameters"][name]["samples"] == r2["parameters"][name]["samples"]

    def test_interval_covers_estimate(self, fitted_project):
        result = run_bootstrap(fitted_project, {"B": 20, "seed": 3})
        for name, info in result["parameters"].items():
            assert info["p2_5"] <= info["mean"] <= info["p97_5"]

    def test_invalid_b_raises(self, fitted_project):
        with pytest.raises(Exception):
            run_bootstrap(fitted_project, {"B": 0})


class TestStability:
    def test_success_rate(self, fitted_project):
        result = run_multistart_stability(fitted_project, {"n_starts": 8, "seed": 2})
        assert result["n_starts"] == 8
        assert 0.0 <= result["success_rate"] <= 1.0
        assert set(result["parameters"].keys()) == {"K", "tau"}

    def test_per_parameter_stats(self, fitted_project):
        result = run_multistart_stability(fitted_project, {"n_starts": 6, "seed": 5})
        for name, info in result["parameters"].items():
            assert "mean" in info
            assert "std" in info
            assert "cv" in info
            assert "best" in info

    def test_best_matches_global(self, fitted_project):
        result = run_multistart_stability(fitted_project, {"n_starts": 10, "seed": 8})
        assert abs(result["parameters"]["K"]["best"] - 2.5) < 0.2
        assert abs(result["parameters"]["tau"]["best"] - 6.0) < 0.4
