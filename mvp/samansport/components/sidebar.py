"""Collapsible sidebar component for SamanSport ERP Dashboard."""

import reflex as rx

from samansport.state import AppState
from samansport.styles import COLORS, TRANSITION


def _nav_item(label: str, icon_tag: str, href: str, page_key: str) -> rx.Component:
    """Single navigation link with active highlight."""
    is_active = AppState.current_page == page_key
    return rx.link(
        rx.box(
            rx.icon(tag=icon_tag, size=18, color="inherit"),
            rx.cond(
                AppState.sidebar_collapsed,
                rx.fragment(),
                rx.text(
                    label,
                    margin_left="0.75rem",
                    font_size="0.875rem",
                    font_weight="500",
                    white_space="nowrap",
                    overflow="hidden",
                ),
            ),
            display="flex",
            align_items="center",
            padding="0.5rem 0.75rem",
            border_radius="8px",
            color=rx.cond(is_active, "#FCFCFD", COLORS["sidebar_text"]),
            background=rx.cond(is_active, COLORS["sidebar_active_bg"], "transparent"),
            _hover={"background": COLORS["sidebar_active_bg"], "color": "#FCFCFD"},
            transition=TRANSITION,
            cursor="pointer",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def _brand_header() -> rx.Component:
    """Brand block: accent square + title + subtitle."""
    return rx.box(
        rx.hstack(
            rx.box(
                width="28px",
                height="28px",
                border_radius="6px",
                background=COLORS["accent"],
                flex_shrink="0",
            ),
            rx.cond(
                AppState.sidebar_collapsed,
                rx.fragment(),
                rx.box(
                    rx.text(
                        "SamanSport",
                        font_size="1.05rem",
                        font_weight="700",
                        color=COLORS["200"],
                        line_height="1.2",
                        white_space="nowrap",
                    ),
                    rx.text(
                        "ERP Elemzések",
                        font_size="0.7rem",
                        color="rgba(179,184,219,0.6)",
                        white_space="nowrap",
                    ),
                ),
            ),
            align_items="center",
            spacing="3",
        ),
        padding_bottom="1.25rem",
        border_bottom=f"1px solid rgba(179,184,219,0.15)",
        margin_bottom="0.75rem",
    )


def _toggle_button() -> rx.Component:
    """Collapse / expand chevron button."""
    return rx.box(
        rx.icon(
            tag=rx.cond(
                AppState.sidebar_collapsed,
                "chevron-right",
                "chevron-left",
            ),
            size=16,
            color=COLORS["sidebar_text"],
        ),
        on_click=AppState.toggle_sidebar,
        cursor="pointer",
        display="flex",
        align_items="center",
        justify_content="center",
        width="28px",
        height="28px",
        border_radius="6px",
        _hover={"background": COLORS["sidebar_active_bg"]},
        margin_bottom="1rem",
        align_self=rx.cond(AppState.sidebar_collapsed, "center", "flex-end"),
    )


def _bottom_section() -> rx.Component:
    """Bottom area with settings link and user avatar."""
    return rx.box(
        # Settings
        rx.box(
            rx.icon(tag="settings", size=18, color=COLORS["sidebar_text"]),
            rx.cond(
                AppState.sidebar_collapsed,
                rx.fragment(),
                rx.text(
                    "Beállítások",
                    margin_left="0.75rem",
                    font_size="0.875rem",
                    font_weight="500",
                    color=COLORS["sidebar_text"],
                    white_space="nowrap",
                    overflow="hidden",
                ),
            ),
            display="flex",
            align_items="center",
            padding="0.5rem 0.75rem",
            border_radius="8px",
            _hover={"background": COLORS["sidebar_active_bg"], "color": "#FCFCFD"},
            cursor="pointer",
            transition=TRANSITION,
        ),
        # Divider
        rx.box(
            height="1px",
            background="rgba(179,184,219,0.15)",
            margin_y="0.75rem",
        ),
        # User profile row
        rx.hstack(
            rx.box(
                rx.text(
                    "SS",
                    font_size="0.75rem",
                    font_weight="700",
                    color="#FCFCFD",
                ),
                display="flex",
                align_items="center",
                justify_content="center",
                width="32px",
                height="32px",
                border_radius="50%",
                background=COLORS["accent"],
                flex_shrink="0",
            ),
            rx.cond(
                AppState.sidebar_collapsed,
                rx.fragment(),
                rx.text(
                    "SamanSport",
                    font_size="0.8rem",
                    color=COLORS["sidebar_text"],
                    white_space="nowrap",
                    overflow="hidden",
                ),
            ),
            align_items="center",
            spacing="3",
            padding="0.25rem 0.5rem",
        ),
        margin_top="auto",
        padding_top="0.75rem",
        border_top=f"1px solid rgba(179,184,219,0.15)",
    )


def sidebar() -> rx.Component:
    """Collapsible sidebar — fixed left panel."""
    return rx.box(
        _brand_header(),
        _toggle_button(),
        # Navigation links
        rx.box(
            _nav_item("Dashboard", "layout-dashboard", "/", "dashboard"),
            rx.box(height="0.25rem"),
            _nav_item("Analitika", "chart-column", "/analytics", "analytics"),
            flex="1",
        ),
        _bottom_section(),
        # Outer box styling
        position="fixed",
        left="0",
        top="0",
        height="100vh",
        width=rx.cond(AppState.sidebar_collapsed, "60px", "240px"),
        min_width=rx.cond(AppState.sidebar_collapsed, "60px", "240px"),
        background=COLORS["sidebar_bg"],
        color=COLORS["sidebar_text"],
        padding="1rem 0.75rem",
        overflow="hidden",
        display="flex",
        flex_direction="column",
        transition=TRANSITION,
        z_index="100",
    )
