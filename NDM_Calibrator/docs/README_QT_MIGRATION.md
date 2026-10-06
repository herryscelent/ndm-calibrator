# PySide6 Qt Migration

This package is the V1.0 Freeze Web UI translated to a PySide6 Qt Widgets mock
frontend, synchronized with the Web responsive/occlusion pass completed on
2026-08-26. The screenshot and visual-audit states use deterministic Mock data;
the current repository run also exposes the project's Application facade for
data import, model/parameter edits, identification, uncertainty and export.

This is the current integrated workspace build. It intentionally preserves the
backend changes already present in the repository, so it is an extension of the
prompt's Phase 1 Mock UI rather than a strict Mock-only package. The immutable
Web reference ZIP and reference screenshots remain unchanged.

## Run

From the repository root:

```powershell
cd E:\software_auth\NDM_Calibrator
conda run -n ndm-calibrator python -m ui_v2
```

When using the extracted `deliverable_qt_mock` package, run from its
`source` directory instead:

```powershell
cd <extracted-package>\source
conda run -n ndm-calibrator python -m ui_v2
```

## Capture And Compare

```powershell
conda run -n ndm-calibrator python scripts\capture_qt_ui.py
conda run -n ndm-calibrator python scripts\build_ui_comparison.py
```

`capture_qt_ui.py` waits for a continuous stable PNG signature and captures the
12 required desktop images plus deterministic advanced/sensitivity/multi-start/
export-completed states. `audit_chart_layout.py` additionally checks page
viewport bounds, interactive occlusion, table tooltips, plot data domains and
Toast/shell containment. `run_dpi_audits.py` repeats the audit at 100%, 125% and
150% scaling.

## Tests

From the repository root:

```powershell
conda run -n ndm-calibrator python -m pytest tests_v2 -q
```

From an extracted package:

```powershell
cd <extracted-package>\source
conda run -n ndm-calibrator python -m pytest ..\tests -q
```

All commands must use the `ndm-calibrator` environment. On restricted Windows
setups, point `TEMP` and `TMP` to a writable workspace directory.

## Structure

- `source/`: `ui_v2/` shell/pages plus the domain packages used by the current
  integrated run (`app/`, `core/`, `data/`, `simulation/`, `identification/`,
  `diagnostics/`, `uncertainty/`, `export/` and the shared `ui/` components).
- `tests/`: the Qt migration tests and the existing numerical/domain suite.
- `screenshots_qt/`: 12 automated 1440×900 Qt captures plus four state captures.
- `comparison/`: 11 required and five state side-by-side Web/Qt comparisons.
- `reference/`: immutable V1.0 provenance plus synchronized 2026-08-26 desktop/state screenshots.
- `docs/QT_LAYOUT_AUDIT_100.json`, `_125.json`, `_150.json`: machine-readable DPI/layout evidence.

Real backend connected: YES (repository integrated run; Mock data remains the
visual baseline)

Mock frontend: YES (deterministic screenshot/audit states)

Final ZIP SHA256: recorded in the package `MANIFEST.json`/`SHA256SUMS.txt` and
in the final packaging note after the current tree is rebuilt.

The standalone `source/` tree is intended to be used with the repository's
domain packages for the integrated actions. Keep the Web reference and the
deterministic Mock states as the visual regression baseline when continuing
backend work.
