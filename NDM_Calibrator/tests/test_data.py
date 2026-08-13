"""Tests for data loading, mapping and preprocessing."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.experiment import Experiment
from data.loader import load_dataframe
from data.mapping import map_columns
from data.preprocessing import drop_nan_rows, interpolate_nan, select_time_range
from data.validator import validate_series


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"time": [0.0, 1.0, 2.0, 3.0], "u": [1.0, 2.0, 3.0, 4.0], "x": [0.0, 1.0, 4.0, 9.0]}
    )


class TestLoader:
    def test_load_csv(self, tmp_path):
        path = tmp_path / "data.csv"
        pd.DataFrame({"a": [1, 2], "b": [3, 4]}).to_csv(path, index=False)
        df, name = load_dataframe(path)
        assert df.shape == (2, 2)
        assert name == "data.csv"

    def test_load_xlsx(self, tmp_path):
        path = tmp_path / "data.xlsx"
        pd.DataFrame({"a": [1, 2]}).to_excel(path, index=False)
        df, _ = load_dataframe(path)
        assert df.shape == (1, 1) or df.shape == (2, 1)

    def test_missing_file_raises(self):
        with pytest.raises(Exception):
            load_dataframe("nonexistent.csv")

    def test_bad_extension_raises(self, tmp_path):
        path = tmp_path / "data.txt"
        path.write_text("hello")
        with pytest.raises(Exception):
            load_dataframe(path)


class TestMapping:
    def test_map_valid(self, sample_df):
        exp = map_columns(sample_df, "time", ["u"], ["x"])
        assert exp.n_points == 4
        assert exp.n_inputs == 1
        assert exp.n_outputs == 1

    def test_missing_column_raises(self, sample_df):
        with pytest.raises(Exception):
            map_columns(sample_df, "nope", [], [])

    def test_non_numeric_column_raises(self):
        df = pd.DataFrame({"time": [0, 1], "u": ["a", "b"]})
        with pytest.raises(Exception):
            map_columns(df, "time", ["u"], [])


class TestValidation:
    def test_monotonic_time(self, sample_df):
        exp = map_columns(sample_df, "time", ["u"], ["x"])
        warnings = validate_series(exp.time, exp.inputs, exp.outputs)
        assert not any("单调" in w for w in warnings)

    def test_non_monotonic_warns(self):
        exp = Experiment(time=np.array([0, 2, 1]), inputs={}, outputs={"x": np.array([0, 1, 2])})
        warnings = validate_series(exp.time, exp.inputs, exp.outputs)
        assert any("单调" in w for w in warnings)

    def test_nan_warns(self):
        exp = Experiment(time=np.array([0, 1, 2]), inputs={}, outputs={"x": np.array([0, np.nan, 2])})
        warnings = validate_series(exp.time, exp.inputs, exp.outputs)
        assert any("NaN" in w for w in warnings)


class TestPreprocessing:
    def test_drop_nan_rows(self):
        exp = Experiment(
            time=np.array([0, 1, 2, 3]),
            inputs={},
            outputs={"x": np.array([0.0, np.nan, 2.0, 3.0])},
        )
        log = []
        new = drop_nan_rows(exp, log)
        assert new.n_points == 3
        assert log

    def test_interpolate_nan(self):
        exp = Experiment(
            time=np.array([0.0, 1.0, 2.0, 3.0]),
            inputs={},
            outputs={"x": np.array([0.0, np.nan, 2.0, 3.0])},
        )
        log = []
        new = interpolate_nan(exp, log)
        assert abs(new.outputs["x"][1] - 1.0) < 1e-9

    def test_select_time_range(self):
        exp = Experiment(
            time=np.array([0, 1, 2, 3, 4]),
            inputs={},
            outputs={"x": np.arange(5, dtype=float)},
        )
        log = []
        new = select_time_range(exp, 1.0, 3.0, log)
        assert new.n_points == 3
        assert np.allclose(new.time, [1, 2, 3])
