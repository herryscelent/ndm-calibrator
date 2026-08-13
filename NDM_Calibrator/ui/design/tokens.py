"""Design tokens: spacing, radius, elevation, typography scales.

All geometry-related scales live here; UI code must reference these instead
of hard-coding pixel values.
"""

# Spacing scale (px)
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
    "2xl": 24,
    "3xl": 32,
    "4xl": 40,
}

# Radius scale (px)
RADIUS = {
    "input": 6,
    "button": 6,
    "card": 8,
    "panel": 8,
    "large": 12,
}

# Elevation (box-shadow-like, applied via QSS border/highlight)
ELEVATION = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 4,
}

# Typography hierarchy (px). Keep <= 6 sizes.
TYPE = {
    "display": 26,
    "page_title": 20,
    "section": 15,
    "body": 13,
    "secondary": 12,
    "caption": 11,
    "metric_value": 24,
    "mono": 12,
}

FONT_FAMILY = {
    "sans": "Segoe UI",
    "mono": "Consolas",
}

FIELD_HEIGHT = 32
SIDEBAR_WIDTH_EXPANDED = 220
SIDEBAR_WIDTH_COLLAPSED = 68
TOPBAR_HEIGHT = 48
