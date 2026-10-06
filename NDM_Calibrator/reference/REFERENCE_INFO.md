# Web Reference Identity

- Immutable baseline package: `web-ui/NDM_CALIBRATOR_WEB_UI_V1_0_FREEZE.zip`
- Baseline version: V1.0 Freeze
- Baseline ZIP SHA256: `7FBB10D605442C38C60637229CF25FE2636B18BCC3AD3F5CE012A20A05F9734D`
- Synchronized screenshot set: 2026-08-26 responsive/occlusion pass
- Desktop reference screenshots: 11 PNG files in `web_screenshots/`
- State reference screenshots: 5 PNG files in `web_screenshots_states/`
- The Web working tree contains 32 captures: 16 desktop and 16 mobile/state captures.

## Screenshot Sync

The baseline ZIP is kept immutable for provenance. The current Web source was
recaptured after the mobile overflow, long-content, control-occlusion and
chart-animation fixes. The capture script now waits for fonts, chart marks,
clip-path geometry and a continuous stable visual signature before saving.

The 11 desktop images and 5 state images copied here are the current Qt visual
reference. Mobile captures remain in `web-ui/screenshots/` as responsive Web
evidence; Qt acceptance remains the desktop viewports required by the prompt.
