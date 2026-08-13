"""Semantic color tokens for Light and Dark themes.

UI code must reference these semantic names (via theme_manager), never raw
hex codes, so a single theme switch restyles the whole application including
plots.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    background: str
    surface: str
    surface_secondary: str
    surface_hover: str
    border: str
    border_strong: str
    text_primary: str
    text_secondary: str
    text_disabled: str

    accent: str
    accent_hover: str
    accent_pressed: str
    accent_text: str

    success: str
    warning: str
    danger: str
    info: str

    plot_primary: str
    plot_secondary: str
    plot_measured: str
    plot_simulated: str
    plot_residual: str

    table_header: str
    table_alt_row: str
    input_bg: str
    input_focus_border: str
    selection_bg: str
    tooltip_bg: str
    scrollbar_bg: str


LIGHT = ColorPalette(
    background="#F3F4F6",
    surface="#FFFFFF",
    surface_secondary="#F9FAFB",
    surface_hover="#F0F1F3",
    border="#E2E5EA",
    border_strong="#C9CDD4",
    text_primary="#1F2328",
    text_secondary="#57606A",
    text_disabled="#9CA3AB",
    accent="#0F6CBD",
    accent_hover="#0B5CA8",
    accent_pressed="#084D8F",
    accent_text="#FFFFFF",
    success="#1A7F37",
    warning="#9A6700",
    danger="#CF222E",
    info="#0969DA",
    plot_primary="#0F6CBD",
    plot_secondary="#C8593E",
    plot_measured="#0F6CBD",
    plot_simulated="#C8593E",
    plot_residual="#9A6700",
    table_header="#F0F1F3",
    table_alt_row="#F7F8FA",
    input_bg="#FFFFFF",
    input_focus_border="#0F6CBD",
    selection_bg="#CEE3F8",
    tooltip_bg="#1F2328",
    scrollbar_bg="#D7DBE0",
)

DARK = ColorPalette(
    background="#1B1D21",
    surface="#23252B",
    surface_secondary="#2A2D34",
    surface_hover="#32353D",
    border="#3A3E46",
    border_strong="#4A4F58",
    text_primary="#E6E8EB",
    text_secondary="#A8ADB5",
    text_disabled="#6B7280",
    accent="#4DA3E8",
    accent_hover="#5FB0F0",
    accent_pressed="#3D8FCC",
    accent_text="#0B1220",
    success="#3FB950",
    warning="#D29922",
    danger="#F85149",
    info="#58A6FF",
    plot_primary="#4DA3E8",
    plot_secondary="#F0907B",
    plot_measured="#4DA3E8",
    plot_simulated="#F0907B",
    plot_residual="#D29922",
    table_header="#2A2D34",
    table_alt_row="#26292F",
    input_bg="#1E2025",
    input_focus_border="#4DA3E8",
    selection_bg="#2B4A6B",
    tooltip_bg="#E6E8EB",
    scrollbar_bg="#3A3E46",
)


def palette_for(theme: str) -> ColorPalette:
    return DARK if theme == "dark" else LIGHT
