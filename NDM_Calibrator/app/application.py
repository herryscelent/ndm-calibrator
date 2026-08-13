"""Application controller layer.

Coordinates domain objects (project, model, parameters, experiment) with the
services (simulation, identification, diagnostics, uncertainty, export).
The GUI talks to this layer, never directly to the domain internals.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.exceptions import NDMCError
from core.model_definition import DynamicModel
from core.objective import ObjectiveConfig
from core.parameter import Parameter, ParameterTable
from core.project import Project

logger = logging.getLogger(__name__)


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
        if keep_parameter_defaults:
            self.project.parameters.sync_from_names(model.parameters)
        self.project.mark_dirty()
        logger.info("设置模型: 状态=%s 参数=%s", model.states, model.parameters)

    def set_parameter_table(self, table: ParameterTable) -> None:
        if self.project is None:
            raise NDMCError("请先新建或打开项目")
        self.project.parameters = table
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
    history = project.results.setdefault("identification_history", [])
    entry = {
        "algorithm": algorithm,
        "options": options,
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
