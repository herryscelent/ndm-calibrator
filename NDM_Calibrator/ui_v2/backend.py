"""Small backend-facing helpers shared by the high-fidelity Qt pages.

The visual migration keeps its widgets in ``ui_v2`` while the domain and
numerical services live in the existing application packages.  This module
contains the boring conversions needed at that boundary so individual pages
do not need to know about pandas, NumPy or result storage details.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.application import Application
from core.exceptions import NDMCError
from data.loader import load_dataframe
from data.mapping import map_columns
from data.validator import describe_dataframe, validate_series


def auto_mapping(df: pd.DataFrame) -> tuple[str, list[str], list[str]]:
    """Choose a conservative time/input/output mapping for an imported frame."""

    if df is None or df.empty:
        raise NDMCError("数据为空, 无法自动映射")
    columns = [str(c) for c in df.columns]
    numeric = [c for c in columns if pd.to_numeric(df[c], errors="coerce").notna().any()]
    time_col = next(
        (candidate for candidate in ("time", "t", "时间", "Time") if candidate in columns),
        numeric[0] if numeric else columns[0],
    )
    numeric = [c for c in numeric if c != time_col]
    if not numeric:
        raise NDMCError("没有可用的数值列作为输入或输出")
    output_cols = [numeric[-1]]
    input_cols = numeric[:-1]
    return time_col, input_cols, output_cols


def import_frame(
    application: Application,
    path: str | Path,
    time_col: str | None = None,
    input_cols: list[str] | None = None,
    output_cols: list[str] | None = None,
    ignored_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and map a frame into the current project.

    Returns the raw frame and a display summary.  The application facade owns
    project mutation; this helper only provides the column choices and quality
    report needed by the page.
    """

    if application.project is None:
        raise NDMCError("请先新建项目")
    df, source = load_dataframe(path)
    detected_time, detected_inputs, detected_outputs = auto_mapping(df)
    time_col = time_col or detected_time
    input_cols = list(input_cols if input_cols is not None else detected_inputs)
    output_cols = list(output_cols if output_cols is not None else detected_outputs)
    ignored_cols = list(ignored_cols or [str(c) for c in df.columns if str(c) not in {time_col, *input_cols, *output_cols}])
    experiment = map_columns(df, time_col, input_cols, output_cols, ignored_cols)
    quality = validate_series(experiment.time, experiment.inputs, experiment.outputs)
    application.project.data_source = source
    application.project.mapping = {
        "time": time_col,
        "inputs": {name: name for name in input_cols},
        "outputs": {name: name for name in output_cols},
        "ignored": ignored_cols,
    }
    application.project.column_types = {str(col): str(dtype) for col, dtype in df.dtypes.items()}
    application.project.experiment = experiment
    application.project.settings.setdefault("data", {})["quality_warnings"] = quality
    application.project.settings["data"]["summary"] = describe_dataframe(df)
    application.project.mark_dirty()
    return df, {
        "source": source,
        "time": time_col,
        "inputs": input_cols,
        "outputs": output_cols,
        "ignored": ignored_cols,
        "quality_warnings": quality,
    }


def experiment_frame(project) -> pd.DataFrame:
    """Return the mapped experiment as a table suitable for a Qt model."""

    if project is None or project.experiment is None:
        return pd.DataFrame()
    exp = project.experiment
    data: dict[str, Any] = {"time": np.asarray(exp.time, dtype=float)}
    data.update({name: np.asarray(values, dtype=float) for name, values in exp.inputs.items()})
    data.update({name: np.asarray(values, dtype=float) for name, values in exp.outputs.items()})
    return pd.DataFrame(data)


def current_prediction(project) -> dict[str, np.ndarray]:
    """Calculate current fitted outputs from stored identification results."""

    if project is None or project.model is None or project.experiment is None:
        return {}
    entry = project.results.get("identification", {})
    params = entry.get("result", {}).get("parameters", {})
    if not params:
        return {}
    from identification.base import build_context

    context = build_context(project)
    theta = np.array([params[name] for name in context.free_names], dtype=float)
    return context.predict_outputs(theta)


def parameter_rows(project) -> list[list[object]]:
    """Convert the domain parameter table to the page's row shape."""

    if project is None:
        return []
    return [
        [p.name, f"{p.initial:.6g}", f"{p.lower:.6g}", f"{p.upper:.6g}", "待辨识" if p.free else "固定", ""]
        for p in project.parameters
    ]
