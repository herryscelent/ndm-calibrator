"""Project model and .ndmc persistence.

A project bundles data mapping, experiment, model, parameters, algorithm
settings and results into a single ZIP archive with a versioned JSON manifest
inside, so a saved project can be reopened and fully restored.
"""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from app.constants import PROJECT_SCHEMA_VERSION
from core.exceptions import CorruptedProjectError, ProjectError
from core.model_definition import DynamicModel
from core.parameter import Parameter, ParameterTable

MANIFEST_NAME = "manifest.json"
PROJECT_JSON = "project.json"
MODEL_JSON = "model.json"
PARAMETERS_JSON = "parameters.json"
SETTINGS_JSON = "settings.json"
DATA_DIR = "data/"
RESULTS_DIR = "results/"


@dataclass
class Project:
    """In-memory representation of a calibration project."""

    name: str = "未命名项目"
    description: str = ""
    created_at: str = ""
    modified_at: str = ""
    file_path: Optional[Path] = None
    dirty: bool = False

    # Data mapping: original dataframe is not stored in memory; we keep the
    # mapped arrays in the Experiment object.
    data_source: Optional[str] = None  # original file name
    column_types: Dict[str, str] = field(default_factory=dict)
    mapping: Dict[str, str] = field(default_factory=dict)  # role -> column name
    preprocess_log: list[str] = field(default_factory=list)

    experiment: Optional[Any] = None  # core.experiment.Experiment
    model: Optional[DynamicModel] = None
    parameters: ParameterTable = field(default_factory=ParameterTable)

    settings: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _now_iso()

    # ------------------------------------------------------------------ #
    # Dirty tracking
    # ------------------------------------------------------------------ #
    def mark_dirty(self) -> None:
        self.dirty = True
        self.modified_at = _now_iso()

    def mark_saved(self) -> None:
        self.dirty = False

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def save(self, path: Path | str) -> None:
        path = Path(path)
        try:
            if path.suffix.lower() != ".ndmc":
                path = path.with_suffix(".ndmc")
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(PROJECT_JSON, json.dumps(self._project_dict(), ensure_ascii=False, indent=2))
                zf.writestr(MODEL_JSON, json.dumps(self.model.to_dict() if self.model else {}, ensure_ascii=False, indent=2))
                zf.writestr(PARAMETERS_JSON, json.dumps(self.parameters.to_dict(), ensure_ascii=False, indent=2))
                zf.writestr(SETTINGS_JSON, json.dumps(self.settings, ensure_ascii=False, indent=2))
                zf.writestr(MANIFEST_NAME, json.dumps(self._manifest_dict(), ensure_ascii=False, indent=2))
                if self.experiment is not None:
                    zf.writestr(DATA_DIR + "experiment.json", json.dumps(self._experiment_dict(), ensure_ascii=False, indent=2))
                zf.writestr(RESULTS_DIR + "results.json", json.dumps(self.results, ensure_ascii=False, indent=2))
        except (OSError, zipfile.BadZipFile) as exc:
            raise ProjectError(f"保存项目失败: {exc}") from exc
        self.file_path = path
        self.mark_saved()

    def _project_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "data_source": self.data_source,
            "column_types": self.column_types,
            "mapping": self.mapping,
            "preprocess_log": self.preprocess_log,
        }

    def _manifest_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": PROJECT_SCHEMA_VERSION,
            "app_name": "NDM-Calibrator",
            "app_version": "V1.0",
            "entries": [
                PROJECT_JSON,
                MODEL_JSON,
                PARAMETERS_JSON,
                SETTINGS_JSON,
                MANIFEST_NAME,
                RESULTS_DIR + "results.json",
            ],
        }

    def _experiment_dict(self) -> Dict[str, Any]:
        exp = self.experiment
        return {
            "time": exp.time.tolist(),
            "inputs": {k: v.tolist() for k, v in exp.inputs.items()},
            "outputs": {k: v.tolist() for k, v in exp.outputs.items()},
            "ignored": exp.ignored,
        }

    @classmethod
    def open(cls, path: Path | str) -> "Project":
        path = Path(path)
        if not path.exists():
            raise ProjectError(f"项目文件不存在: {path}")
        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = set(zf.namelist())
                if MANIFEST_NAME not in names or PROJECT_JSON not in names:
                    raise CorruptedProjectError("项目文件缺少必要成员 (manifest/project.json)")
                try:
                    manifest = json.loads(zf.read(MANIFEST_NAME))
                except json.JSONDecodeError as exc:
                    raise CorruptedProjectError("项目 manifest 损坏") from exc
                schema = manifest.get("schema_version")
                if schema != PROJECT_SCHEMA_VERSION:
                    raise CorruptedProjectError(
                        f"项目 schema 版本不兼容: 文件为 {schema}, 软件要求 {PROJECT_SCHEMA_VERSION}"
                    )
                project_data = json.loads(zf.read(PROJECT_JSON))
                model_data = json.loads(zf.read(MODEL_JSON))
                params_data = json.loads(zf.read(PARAMETERS_JSON))
                settings_data = json.loads(zf.read(SETTINGS_JSON))
                exp_data = None
                if DATA_DIR + "experiment.json" in names:
                    exp_data = json.loads(zf.read(DATA_DIR + "experiment.json"))
                results_data = {}
                if RESULTS_DIR + "results.json" in names:
                    results_data = json.loads(zf.read(RESULTS_DIR + "results.json"))
        except zipfile.BadZipFile as exc:
            raise CorruptedProjectError(f"项目文件不是有效的 ZIP: {exc}") from exc
        except KeyError as exc:
            raise CorruptedProjectError(f"项目文件缺少内容: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise CorruptedProjectError(f"项目 JSON 内容损坏: {exc}") from exc
        except OSError as exc:
            raise ProjectError(f"读取项目文件失败: {exc}") from exc

        try:
            project = cls(
                name=project_data.get("name", "未命名项目"),
                description=project_data.get("description", ""),
                created_at=project_data.get("created_at", _now_iso()),
                modified_at=project_data.get("modified_at", _now_iso()),
                file_path=path,
                data_source=project_data.get("data_source"),
                column_types=project_data.get("column_types", {}),
                mapping=project_data.get("mapping", {}),
                preprocess_log=project_data.get("preprocess_log", []),
                settings=settings_data,
                results=results_data,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise CorruptedProjectError(f"项目内容不完整: {exc}") from exc

        if model_data:
            try:
                project.model = DynamicModel.from_dict(model_data)
            except Exception as exc:
                raise CorruptedProjectError(f"模型内容无法解析: {exc}") from exc
        try:
            project.parameters = ParameterTable.from_dict(params_data)
        except (KeyError, TypeError, ValueError) as exc:
            raise CorruptedProjectError(f"参数配置损坏: {exc}") from exc

        if exp_data is not None:
            project.experiment = _build_experiment_from_dict(exp_data)

        project.mark_saved()
        return project

    def summary(self) -> Dict[str, Any]:
        exp = self.experiment
        return {
            "name": self.name,
            "description": self.description,
            "n_points": exp.n_points if exp else 0,
            "n_inputs": exp.n_inputs if exp else 0,
            "n_outputs": exp.n_outputs if exp else 0,
            "n_parameters": len(self.parameters),
            "n_free_parameters": len(self.parameters.free_parameters()),
            "model_states": self.model.states if self.model else [],
            "data_source": self.data_source,
            "file_path": str(self.file_path) if self.file_path else None,
        }


def _build_experiment_from_dict(exp_data: Dict[str, Any]):
    from core.experiment import Experiment

    return Experiment(
        time=np.array(exp_data["time"], dtype=float),
        inputs={k: np.array(v, dtype=float) for k, v in exp_data.get("inputs", {}).items()},
        outputs={k: np.array(v, dtype=float) for k, v in exp_data.get("outputs", {}).items()},
        ignored=exp_data.get("ignored", []),
    )


def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
