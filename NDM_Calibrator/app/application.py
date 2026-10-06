"""Application controller layer.

Coordinates domain objects (project, model, parameters, experiment) with the
services (simulation, identification, diagnostics, uncertainty, export).
The GUI talks to this layer, never directly to the domain internals.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.exceptions import NDMCError
from core.model_definition import DynamicModel, get_builtin_model
from core.objective import ObjectiveConfig
from core.parameter import Parameter, ParameterTable
from core.project import Project
from app.constants import PARAMETER_BOUND_DEFAULT_LOWER, PARAMETER_BOUND_DEFAULT_UPPER, PARAMETER_INITIAL_DEFAULT

logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    """Convert transient/numeric option values into JSON-safe primitives."""

    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    # NumPy scalar/array values expose ``item``/``tolist`` without requiring
    # the application layer to import NumPy just for serialization.
    to_list = getattr(value, "tolist", None)
    if callable(to_list):
        try:
            return _json_safe(to_list())
        except (TypeError, ValueError):
            pass
    to_item = getattr(value, "item", None)
    if callable(to_item):
        try:
            return _json_safe(to_item())
        except (TypeError, ValueError):
            pass
    if isinstance(value, Path):
        return str(value)
    return value


class Application:
    """Facade for the whole desktop application."""

    def __init__(self):
        self.project: Optional[Project] = None
        self._recent_projects: List[Path] = []

    # ------------------------------------------------------------------ #
    # Project management
    # ------------------------------------------------------------------ #
    def new_project(self, name: str = "未命名项目", description: str = "") -> Project:
        self.project = Project(name=name, description=description)
        logger.info("新建项目: %s", name)
        return self.project

    def open_project(self, path: Path | str) -> Project:
        self.project = Project.open(path)
        self._push_recent(path)
        logger.info("打开项目: %s", path)
        return self.project

    def save_project(self, path: Optional[Path | str] = None) -> Optional[Path]:
        if self.project is None:
            raise NDMCError("当前没有项目")
        target = path if path is not None else self.project.file_path
        if target is None:
            raise NDMCError("请指定项目保存路径")
        self.project.save(target)
        self._push_recent(self.project.file_path)
        logger.info("保存项目: %s", target)
        return self.project.file_path

    def close_project(self) -> None:
        if self.project is not None:
            logger.info("关闭项目: %s", self.project.name)
        self.project = None

    def _push_recent(self, path: Path | str) -> None:
        p = Path(path)
        if p in self._recent_projects:
            self._recent_projects.remove(p)
        self._recent_projects.insert(0, p)
        self._recent_projects = self._recent_projects[:8]

    @property
    def recent_projects(self) -> List[Path]:
        return list(self._recent_projects)

    # ------------------------------------------------------------------ #
    # Data
    # ------------------------------------------------------------------ #
    def import_data(self, path: Path | str, time_col: str, input_cols: List[str],
                    output_cols: List[str], ignored_cols: Optional[List[str]] = None) -> None:
        """Load a CSV/XLSX file and map columns into the project experiment."""
        if self.project is None:
            raise NDMCError("请先新建或打开项目")
        from data.loader import load_dataframe
        from data.mapping import map_columns

        df, source = load_dataframe(path)
        mapping = {
            "time": time_col,
            "inputs": {c: c for c in input_cols},
            "outputs": {c: c for c in output_cols},
        }
        experiment = map_columns(df, time_col, input_cols, output_cols, ignored_cols or [])
        self.project.data_source = source
        self.project.mapping = mapping
        self.project.column_types = {str(col): str(dtype) for col, dtype in df.dtypes.items()}
        self.project.experiment = experiment
        # A fitted trajectory is extremely sensitive to x0.  When a state is
        # observed directly, seed it from the first measured sample so the
        # optimizer does not compare data starting at, for example, x=5 with a
        # model forced to start at the template default x=1.
        self._sync_initial_conditions_from_experiment(replace=True)
        self._clear_analysis_results()
        self.project.mark_dirty()
        logger.info("导入数据: %s (行数=%d)", source, experiment.n_points)

    def set_preprocess_log(self, log: List[str]) -> None:
        if self.project is not None:
            self.project.preprocess_log = log
            self.project.mark_dirty()

    # ------------------------------------------------------------------ #
    # Model & parameters
    # ------------------------------------------------------------------ #
    def set_model(self, model: DynamicModel, keep_parameter_defaults: bool = True) -> None:
        if self.project is None:
            raise NDMCError("请先新建或打开项目")
        self.project.model = model
        # Synchronize the table to the model while retaining user-edited
        # values for parameters that still exist.  Built-in templates carry
        # calibrated-friendly defaults; generic Parameter defaults are used
        # for custom models.
        existing = {p.name: p for p in self.project.parameters}
        defaults = {}
        builtin = get_builtin_model(getattr(model, "builtin_key", ""))
        if builtin is not None:
            defaults = builtin.parameter_defaults
        from core.parameter import ParameterTable

        synced = ParameterTable()
        for name in model.parameters:
            if keep_parameter_defaults and name in existing:
                synced.add(existing[name])
                continue
            spec = defaults.get(name, {})
            synced.add(Parameter(
                name=name,
                initial=float(spec.get("initial", PARAMETER_INITIAL_DEFAULT)),
                lower=float(spec.get("lower", PARAMETER_BOUND_DEFAULT_LOWER)),
                upper=float(spec.get("upper", PARAMETER_BOUND_DEFAULT_UPPER)),
                free=bool(spec.get("free", True)),
            ))
        self.project.parameters = synced
        self._sync_initial_conditions_from_experiment()
        self._clear_analysis_results()
        self.project.mark_dirty()
        logger.info("设置模型: 状态=%s 参数=%s", model.states, model.parameters)

    def _sync_initial_conditions_from_experiment(self, replace: bool = False) -> None:
        """Seed directly observed states from the first measured sample.

        Only state/output pairs whose output equation is exactly the state are
        inferred.  This covers the built-in templates without guessing values
        for transformed outputs or unobserved derivative states such as x2 in
        the second-order model.  Existing user-provided values are preserved
        unless the experiment itself has just been replaced.
        """
        project = self.project
        if project is None or project.model is None or project.experiment is None:
            return
        model = project.model
        experiment = project.experiment
        current = dict(project.settings.get("initial_conditions") or {})
        changed = False
        # Models can be changed after a previous run.  Drop stale state names
        # so the simulator never receives an initial condition for a state
        # that no longer exists.
        valid_current = {state: current[state] for state in model.states if state in current}
        if valid_current != current:
            current = valid_current
            changed = True
        for state in model.states:
            directly_observed = (
                state in model.outputs
                and state in experiment.outputs
                and str(dict(zip(model.outputs, model.output_exprs)).get(state, "")).strip() == state
            )
            if not directly_observed:
                continue
            if not replace and state in current:
                continue
            values = experiment.outputs[state]
            if len(values) == 0:
                continue
            try:
                value = float(values[0])
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                continue
            if current.get(state) != value:
                current[state] = value
                changed = True
        if changed:
            project.settings["initial_conditions"] = current

    def set_parameter_table(self, table: ParameterTable) -> None:
        if self.project is None:
            raise NDMCError("请先新建或打开项目")
        self.project.parameters = table
        self._clear_analysis_results()
        self.project.mark_dirty()

    def _clear_analysis_results(self) -> None:
        """Discard analysis artifacts invalidated by model/data changes."""
        if self.project is not None:
            self.project.results.clear()

    def clear_results(self) -> None:
        """Public explicit reset used by the UI before a fresh analysis."""
        self._clear_analysis_results()
        if self.project is not None:
            self.project.mark_dirty()

    # ------------------------------------------------------------------ #
    # Identification & analysis (wired to services; GUI runs these in
    # worker threads via ui.workers)
    # ------------------------------------------------------------------ #
    def run_identification(self, algorithm: str, options: Dict[str, Any]) -> Dict[str, Any]:
        if self.project is None or self.project.model is None:
            raise NDMCError("请先定义模型")
        if self.project.experiment is None:
            raise NDMCError("请先导入数据")
        free_params = self.project.parameters.free_parameters()
        if not free_params:
            raise NDMCError("没有待辨识参数")
        return run_identification_for_project(self.project, algorithm, options)

    def run_bootstrap(self, options: Dict[str, Any]) -> Dict[str, Any]:
        if self.project is None:
            raise NDMCError("请先新建或打开项目")
        return run_bootstrap_for_project(self.project, options)

    def run_multistart_stability(self, options: Dict[str, Any]) -> Dict[str, Any]:
        if self.project is None:
            raise NDMCError("请先新建或打开项目")
        return run_stability_for_project(self.project, options)


def _require_project_state(project: Project):
    if project.model is None:
        raise NDMCError("请先定义模型")
    if project.experiment is None:
        raise NDMCError("请先导入数据")
    free_params = project.parameters.free_parameters()
    if not free_params:
        raise NDMCError("没有待辨识参数")
    return free_params


def run_identification_for_project(project: Project, algorithm: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Run identification, store the run in history and set it as current."""
    from identification.manager import run_algorithm

    free_params = _require_project_state(project)
    result = run_algorithm(project, algorithm, options)
    # A new fit supersedes downstream analyses based on the previous fit,
    # while preserving the identification history for auditability.
    for key in ("bootstrap", "stability", "calibration", "diagnostics"):
        project.results.pop(key, None)
    history = project.results.setdefault("identification_history", [])
    # ``_cancel_token`` is a transient worker-only value.  Never persist it in
    # the JSON project history because thread/event objects are not serializable.
    persisted_options = _json_safe({key: value for key, value in options.items() if key != "_cancel_token"})
    entry = {
        "algorithm": algorithm,
        "options": persisted_options,
        "result": result.to_dict(),
    }
    history.append(entry)
    project.results["identification"] = entry  # current scheme
    project.mark_dirty()
    return result.to_dict()


def run_bootstrap_for_project(project: Project, options: Dict[str, Any]) -> Dict[str, Any]:
    from uncertainty.bootstrap import run_bootstrap

    free_params = _require_project_state(project)
    result = run_bootstrap(project, options)
    project.results["bootstrap"] = result
    project.mark_dirty()
    return result


def run_stability_for_project(project: Project, options: Dict[str, Any]) -> Dict[str, Any]:
    from uncertainty.stability import run_multistart_stability

    free_params = _require_project_state(project)
    result = run_multistart_stability(project, options)
    project.results["stability"] = result
    project.mark_dirty()
    return result
