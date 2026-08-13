"""Tests for core domain objects."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

from core.experiment import Experiment
from core.model_definition import DynamicModel
from core.parameter import Parameter, ParameterTable
from core.project import Project


# ------------------------------------------------------------------ #
# Parameter validation
# ------------------------------------------------------------------ #
class TestParameter:
    def test_valid_bounds(self):
        p = Parameter(name="k", initial=1.0, lower=0.1, upper=10.0)
        p.validate()  # should not raise

    def test_invalid_bounds_raise(self):
        p = Parameter(name="k", initial=5.0, lower=1.0, upper=2.0)
        with pytest.raises(ValueError):
            p.validate()

    def test_equality_bounds_invalid(self):
        p = Parameter(name="k", initial=1.0, lower=1.0, upper=2.0)
        with pytest.raises(ValueError):
            p.validate()

    def test_roundtrip_dict(self):
        p = Parameter(name="K", initial=2.5, lower=0.1, upper=20.0, free=True)
        p2 = Parameter.from_dict(p.to_dict())
        assert p2.name == "K"
        assert p2.initial == 2.5
        assert p2.free is True


class TestParameterTable:
    def test_add_duplicate_raises(self):
        pt = ParameterTable()
        pt.add(Parameter(name="k"))
        with pytest.raises(ValueError):
            pt.add(Parameter(name="k"))

    def test_sync_from_names(self):
        pt = ParameterTable()
        added = pt.sync_from_names(["a", "b"])
        assert added == ["a", "b"]
        assert pt.free_names() == ["a", "b"]

    def test_sync_keeps_existing_values(self):
        pt = ParameterTable()
        pt.sync_from_names(["a"])
        pt.get("a").initial = 42.0
        pt.sync_from_names(["a", "b"])
        assert pt.get("a").initial == 42.0


# ------------------------------------------------------------------ #
# Model parsing
# ------------------------------------------------------------------ #
class TestModelParsing:
    def test_builtin_first_order(self):
        m = DynamicModel.from_builtin("first_order")
        assert m.states == ["x"]
        assert set(m.parameters) == {"K", "tau"}
        assert m.outputs == ["x"]

    def test_user_definition_valid(self):
        m = DynamicModel.from_user_definition(
            states=["x1", "x2"],
            inputs=["u"],
            parameters=["k", "c", "b"],
            dynamics={"dx1/dt": "x2", "dx2/dt": "-k*x1 - c*x2 + b*u"},
            outputs=["x1"],
            output_equations={"x1": "x1"},
            initial_conditions={"x1": 0.0, "x2": 0.0},
        )
        assert m.n_states == 2
        assert m.n_parameters == 3

    def test_undefined_symbol_rejected(self):
        with pytest.raises(Exception):
            DynamicModel.from_user_definition(
                states=["x"],
                inputs=[],
                parameters=["a"],
                dynamics={"dx/dt": "a*x + unknown_symbol"},
                outputs=["x"],
                output_equations={"x": "x"},
                initial_conditions={"x": 1.0},
            )

    def test_missing_equation_rejected(self):
        with pytest.raises(Exception):
            DynamicModel.from_user_definition(
                states=["x1", "x2"],
                inputs=[],
                parameters=["a"],
                dynamics={"dx1/dt": "a*x1"},
                outputs=["x1"],
                output_equations={"x1": "x1"},
                initial_conditions={"x1": 1.0, "x2": 1.0},
            )

    def test_injection_rejected(self):
        with pytest.raises(Exception):
            DynamicModel.from_user_definition(
                states=["x"],
                inputs=[],
                parameters=["a"],
                dynamics={"dx/dt": "__import__('os').system('x')"},
                outputs=["x"],
                output_equations={"x": "x"},
                initial_conditions={"x": 1.0},
            )

    def test_duplicate_symbols_rejected(self):
        with pytest.raises(Exception):
            DynamicModel.from_user_definition(
                states=["x"],
                inputs=["x"],
                parameters=["a"],
                dynamics={"dx/dt": "a*x"},
                outputs=["x"],
                output_equations={"x": "x"},
                initial_conditions={"x": 1.0},
            )

    def test_roundtrip_dict(self):
        m = DynamicModel.from_builtin("second_order")
        m2 = DynamicModel.from_dict(m.to_dict())
        assert m2.states == m.states
        assert m2.rhs_exprs == m.rhs_exprs


# ------------------------------------------------------------------ #
# Experiment validation
# ------------------------------------------------------------------ #
class TestExperiment:
    def test_length_mismatch_raises(self):
        with pytest.raises(Exception):
            Experiment(
                time=np.array([0, 1, 2]),
                inputs={"u": np.array([0, 1])},
                outputs={},
            )

    def test_empty_raises(self):
        with pytest.raises(Exception):
            Experiment(time=np.array([]), inputs={}, outputs={})


# ------------------------------------------------------------------ #
# Project persistence
# ------------------------------------------------------------------ #
class TestProjectPersistence:
    def test_save_reopen_roundtrip(self, first_order_project, tmp_path):
        path = tmp_path / "proj.ndmc"
        first_order_project.save(path)
        p2 = Project.open(path)
        assert p2.name == first_order_project.name
        assert p2.parameters.get("K").initial == 1.0
        assert p2.model.states == ["x"]
        assert p2.experiment.n_points == 301
        assert p2.model.rhs_exprs == first_order_project.model.rhs_exprs

    def test_save_results_persist(self, first_order_project, tmp_path):
        first_order_project.results["identification"] = {
            "algorithm": "least_squares",
            "result": {"parameters": {"K": 2.5, "tau": 6.0}},
        }
        path = tmp_path / "proj.ndmc"
        first_order_project.save(path)
        p2 = Project.open(path)
        assert p2.results["identification"]["result"]["parameters"]["K"] == 2.5

    def test_corrupted_file_raises_friendly(self, tmp_path):
        bad = tmp_path / "bad.ndmc"
        bad.write_bytes(b"not a zip file at all")
        with pytest.raises(Exception) as exc:
            Project.open(bad)
        assert "损坏" in str(exc.value) or "ZIP" in str(exc.value)

    def test_wrong_schema_rejected(self, tmp_path):
        import json, zipfile

        path = tmp_path / "schema.ndmc"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("manifest.json", json.dumps({"schema_version": "99.9"}))
            zf.writestr("project.json", json.dumps({"name": "x"}))
        with pytest.raises(Exception) as exc:
            Project.open(path)
        assert "schema" in str(exc.value).lower()

    def test_missing_member_rejected(self, tmp_path):
        import json, zipfile

        path = tmp_path / "incomplete.ndmc"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("project.json", json.dumps({"name": "x"}))
        with pytest.raises(Exception):
            Project.open(path)
