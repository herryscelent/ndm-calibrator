# Qt Migration Code Audit

> Scope note (2026-08-27): the visual migration remains Mock-data based for
> screenshots and layout evidence, while the current repository `ui_v2` window
> is an integrated build that can call the existing Application/domain services.
> This records the delivered workspace state without rewriting or rolling back
> those backend changes.

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| TODO/FIXME in migration code | PASS | No matches under `ui_v2/`, `tests_v2/` or Qt scripts. |
| Bare `except` | PASS | No bare exception handlers in migration code. |
| Direct SciPy/ODE/optimizer import | WARN | No direct optimizer imports in page code; integrated `Application`/domain imports remain available through `ui_v2.backend` and `main_window.py`. |
| Random mock generation | PASS | No `random` or `np.random` use; mock data is deterministic. |
| Hard-coded random data inside pages | PASS | Page values come from `ui_v2/mock_data.py`. |
| Main entry point | PASS | `python -m ui_v2`. |
| Page navigation | PASS | 11 routes in `QStackedWidget`, plus Topbar Settings/About actions. |
| Empty/unused required page | PASS | Every required page is instantiated and reachable. |
| Button handlers | PASS | Navigation, new/open/import, filtering, selectors, validation, add/delete/reset, identification states, browse, export and Toast are wired. |
| ConfirmDialog | PASS | QSS-styled reusable `ConfirmDialog` is used for parameter deletion. |
| Parameter validation | PASS | Frontend `lower < initial < upper` check implemented. |
| Identification states | PASS | Ready, running, completed, cancelled and error Mock states are tested. |
| Plot interactions | PASS | Pan/zoom remain enabled; calibration reset and crosshair tooltip are available. |
| Table overflow/tooltips | PASS | Local horizontal scrolling, fixed minimum column widths and `ToolTipRole` for elided values. |
| Duplicated color literals | WARN | Semantic colors use tokens; a few derived badge/cell colors remain local by design. |
| Duplicated spacing literals | WARN | Layout tokens are centralized, while small widget-specific margins remain local. |
| Raw default Qt controls | PASS | Buttons, inputs, combos, checkboxes, tables, tabs, progress, splitter and scrollbars are QSS styled. |
| Accessibility basics | PASS | Keyboard focus remains visible; navigation and icon buttons expose tooltips/accessible names. |
| Legacy UI preservation | PASS | Existing `ui/` was not replaced or removed. |

## Tests

- Qt migration suite: **21 passed** (`tests_v2/`).
- Layout/interaction audit: **PASS** at 1100×700, 1366×768, 1440×900 and 1920×1080.
- DPI audit: **PASS** at 100%, 125% and 150% (`docs/QT_LAYOUT_AUDIT_*.json`).
- Existing project suite: **96 passed**; one expected numerical overflow warning
  from the divergence test is recorded without changing the Mock frontend scope.

Real backend connected: **YES** (repository integrated run; screenshot states use Mock data)

Mock frontend: **YES** (deterministic visual/audit states)

This package supersedes the previous migration baseline ZIP. The final ZIP hash
is recorded in `README_QT_MIGRATION.md` and `MANIFEST.json` after packaging.
