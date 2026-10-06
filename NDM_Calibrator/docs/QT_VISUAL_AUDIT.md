# Qt Visual Audit

Scope: the captured Qt states and all layout assertions use deterministic Mock
data. The repository's current `ui_v2` shell is also wired to the existing
Application/domain services for integrated runs; this does not change the Web
reference baseline or the visual comparison inputs.

审计脚本：`scripts/audit_chart_layout.py`。它检查页面是否超出
`QScrollArea` viewport、交互控件中心是否被遮挡、同层控件是否相交、表格
省略值是否有完整 Tooltip、图表是否有非空数据，以及 Toast/Sidebar/Topbar
的边界。运行态、完成态、取消态、错误态、诊断四个 Tabs、可信度两个 Tabs
和导出结果均纳入审计。

| Area | Result | Notes |
| --- | --- | --- |
| Reference integrity | PASS | Immutable Web ZIP hash retained; current 11 desktop + 5 state references synced on 2026-08-26. |
| Main window geometry | PASS | 1100×700, 1366×768, 1440×900 and 1920×1080 all audited. |
| Sidebar | PASS | 220/68 px states, active icon color, tooltip and bottom action present. |
| Topbar | PASS | Product, bounded project text, saved status, four tooltips and navigation handlers. |
| Dashboard | PASS | 40:60 workflow/plot balance; new/open actions provide Mock feedback. |
| Data | PASS | Split layout, filtering, series selector and editable role delegate; local table scroll at minimum width. |
| Model | PASS | Structure/editor/validation hierarchy retained; validation action wired. |
| Parameters | PASS | Typed delegates, add/delete/reset actions, confirmation dialog and boundary validation. |
| Identification | WARN | All five Mock states are visible and non-overlapping; PyQtGraph logarithmic labels differ from Web. |
| Calibration | PASS | Metrics, reset control, crosshair tooltip and full 0–50 s domain retained. |
| Diagnostics | WARN | Four Tabs and sensitivity ranking pass layout checks; PyQtGraph axis scaling differs from Recharts. |
| Uncertainty | PASS | Default is multi-start; Bootstrap includes selector, rerun action, interval summary and chart. |
| Export | PASS | Content selection, format, path, browse feedback and completed result are wired. |
| Settings | PASS | Page exists and is navigable from Topbar and Sidebar. |
| About | PASS | Page exists and is navigable from Topbar and Sidebar. |
| Color tokens | PASS | Central tokens match synchronized Web semantic values. |
| Typography | WARN | Web uses Segoe/system; Qt uses Microsoft YaHei UI substitution and different rasterization. |
| Spacing/radius | PASS | Shared QSS and token values; no broad absolute-position layout. |
| Tables/forms/buttons/tabs/badges | PASS | QSS covers tables, forms, checkbox, splitter, tabs, focus and horizontal scrollbars. |
| Plots | WARN | PyQtGraph axes/legends differ from Recharts; data domains and non-empty marks are asserted. |
| Mock data consistency | PASS | Deterministic data; corrected cumulative velocity and calibration spans 0–50 s. |
| 1100x700 | PASS | Minimum Qt desktop size; all pages fit outer viewport and data table scrolls locally. |
| 1366x768 | PASS | No clipped text or overlapping controls. |
| 1440x900 | PASS | Primary screenshot and comparison viewport. |
| 1920x1080 | PASS | Stretch policies preserve hierarchy without new overlap. |
| 100% DPI | PASS | `QT_LAYOUT_AUDIT_100.json`, DPR 1.0. |
| 125% DPI | PASS | `QT_LAYOUT_AUDIT_125.json`; no clipping/overlap under scale factor 1.25. |
| 150% DPI | PASS | `QT_LAYOUT_AUDIT_150.json`; no clipping/overlap under scale factor 1.5. |

Summary: PASS 24, WARN 4, FAIL 0.

Environment records (OS, Python, Qt/PySide6 version, platform plugin, requested
scale and device-pixel ratio) are stored in each JSON report. No visual FAIL
blocks the Qt Mock migration package.
