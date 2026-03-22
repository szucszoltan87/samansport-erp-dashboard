"""SamanSport ERP Dashboard — Reflex style definitions.

Grey-blue palette and component styles matching the existing Streamlit theme.
"""

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
COLORS = {
    # Neutral scale (lightest → darkest)
    "25": "#FCFCFD",
    "50": "#F8F9FC",
    "100": "#EAECF5",
    "200": "#D5D9EB",
    "300": "#B3B8DB",
    "400": "#717BBC",
    "500": "#4E5BA6",
    "600": "#3E4784",
    "700": "#363F72",
    "800": "#293056",
    "900": "#101323",
    "950": "#0D0F1C",
    # Semantic aliases
    "blue": "#4E5BA6",
    "teal": "#4E5BA6",
    "indigo": "#3E4784",
    "green": "#10b981",
    "red": "#ef4444",
    "amber": "#f59e0b",
    "purple": "#717BBC",
    "slate": "#B3B8DB",
    "accent": "#4E5BA6",
    "charcoal": "#293056",
    # Sidebar
    "sidebar_bg": "#363F72",
    "sidebar_text": "#B3B8DB",
    "sidebar_active_bg": "rgba(78,91,166,0.18)",
}

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
SIDEBAR_WIDTH = "240px"
SIDEBAR_COLLAPSED_WIDTH = "60px"
TRANSITION = "all 0.3s ease"

# ---------------------------------------------------------------------------
# Base style — passed to rx.App(style=…)
# ---------------------------------------------------------------------------
BASE_STYLE = {
    "font_family": "Inter, sans-serif",
    "background": COLORS["50"],
    "color": COLORS["900"],
    "::selection": {
        "background": COLORS["accent"],
        "color": "#ffffff",
    },
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
SIDEBAR_STYLE = {
    "width": SIDEBAR_WIDTH,
    "min_width": SIDEBAR_WIDTH,
    "height": "100vh",
    "position": "fixed",
    "left": "0",
    "top": "0",
    "background": COLORS["sidebar_bg"],
    "color": COLORS["sidebar_text"],
    "padding": "1rem 0.75rem",
    "overflow_y": "auto",
    "transition": TRANSITION,
    "z_index": "100",
}

SIDEBAR_COLLAPSED_STYLE = {
    **SIDEBAR_STYLE,
    "width": SIDEBAR_COLLAPSED_WIDTH,
    "min_width": SIDEBAR_COLLAPSED_WIDTH,
}

# ---------------------------------------------------------------------------
# Main content area
# ---------------------------------------------------------------------------
MAIN_CONTENT_STYLE = {
    "margin_left": SIDEBAR_WIDTH,
    "padding": "1.5rem 2rem",
    "transition": TRANSITION,
    "min_height": "100vh",
}

MAIN_CONTENT_COLLAPSED_STYLE = {
    **MAIN_CONTENT_STYLE,
    "margin_left": SIDEBAR_COLLAPSED_WIDTH,
}

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
KPI_CARD_STYLE = {
    "background": "#ffffff",
    "border_radius": "10px",
    "box_shadow": "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)",
    "border_top": f"3px solid {COLORS['accent']}",
    "padding": "1.25rem 1.5rem",
    "width": "100%",
}

# ---------------------------------------------------------------------------
# Preset date-range pills
# ---------------------------------------------------------------------------
PRESET_PILL_STYLE = {
    "background": "#ffffff",
    "border": f"1px solid {COLORS['300']}",
    "border_radius": "9999px",
    "padding": "0.25rem 0.875rem",
    "font_size": "0.8rem",
    "color": COLORS["700"],
    "cursor": "pointer",
    "transition": TRANSITION,
    "_hover": {
        "border_color": COLORS["accent"],
        "color": COLORS["accent"],
    },
}

PRESET_PILL_ACTIVE_STYLE = {
    **PRESET_PILL_STYLE,
    "background": COLORS["accent"],
    "color": "#ffffff",
    "border_color": COLORS["accent"],
    "_hover": {
        "background": COLORS["600"],
        "border_color": COLORS["600"],
        "color": "#ffffff",
    },
}
