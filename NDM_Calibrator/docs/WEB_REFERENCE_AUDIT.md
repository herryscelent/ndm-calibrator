# Web Reference Audit

## Reference Identity

- Immutable baseline: `web-ui/NDM_CALIBRATOR_WEB_UI_V1_0_FREEZE.zip`
- Baseline version: V1.0 Freeze
- Baseline ZIP SHA256: `7FBB10D605442C38C60637229CF25FE2636B18BCC3AD3F5CE012A20A05F9734D`
- Current screenshot sync: 2026-08-26 responsive/occlusion pass
- Current Web captures: 32 PNG files (16 desktop, 16 mobile/state)
- Qt reference copy: 11 desktop screenshots plus 5 interaction-state screenshots
- Audited inputs: screenshots, source, mock data, `UI_DESIGN_SYSTEM.md`, `QT_MAPPING.md`, `UI_AUDIT.md`, manifest and hashes

## Extracted Tokens

| Token | Value |
| --- | --- |
| background | `#F5F7FA` |
| surface/topbar | `#FFFFFF` |
| sidebar | `#F1F4F8` |
| border | `#DDE3EA` |
| text primary | `#20252B` |
| text secondary | `#5F6B78` |
| accent | `#356FE5` |
| accent hover | `#285FCB` |
| accent subtle | `#E7F0FF` |
| success | `#27875A` |
| warning | `#B7791F` |
| danger | `#C94A4A` |

- Web font: Segoe UI → system-ui → sans-serif. Qt uses Microsoft YaHei UI as a
  Windows-compatible substitution; the rasterization difference is recorded as
  a known visual WARN.
- Sidebar: 220 px expanded, 68 px collapsed.
- Topbar: 48 px.
- Page padding: 28 px.
- Radius: 6 px small, 8 px medium.
- Tables: compact engineering rows, 30-38 px depending on page context.
- Charts: full-width analytical plots using the frozen deterministic data.

## Screenshot Synchronization

- The immutable V1.0 ZIP remains the provenance baseline; it is not overwritten.
- The current Web screenshot script waits for fonts, chart marks, clip-path
  geometry and a continuous stable visual signature. This prevents an animated
  line chart from being frozen with only a partial 0–50 s domain.
- `uncertainty_bootstrap.png` explicitly selects the Bootstrap tab.
- Mobile captures cover sidebar/topbar compaction, local table scrolling and
  long-content checks. Qt comparison intentionally remains on the prompt's
  desktop acceptance viewports.

## Reference Result

| Check | Result | Evidence |
| --- | --- | --- |
| Desktop screenshot count | PASS | 11 reference images, all 1440×900 |
| Interaction-state references | PASS | 5 state images, all 1440×900 |
| Chart animation stability | PASS | 1.8 s settle floor plus stable geometry signature |
| Mobile layout assertions | PASS | document width, interactive bounds, overlap and chart-size checks |
| Font identity | WARN | Web Segoe/system; Qt Microsoft YaHei UI substitution |
