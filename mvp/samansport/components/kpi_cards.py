"""KPI card components for SamanSport ERP Dashboard."""

import reflex as rx

from samansport.styles import KPI_CARD_STYLE, COLORS


def kpi_card(
    label: str,
    value: rx.Var | str,
    sub: rx.Var | str = "",
    icon_name: str = "",
    icon_bg: str = COLORS["blue_light"],
    icon_color: str = COLORS["accent"],
) -> rx.Component:
    """Single KPI card with label, value, optional subtitle, and icon."""
    icon_box = rx.box(
        rx.icon(tag=icon_name, size=16, color=icon_color) if icon_name else rx.fragment(),
        width="36px",
        height="36px",
        border_radius="8px",
        background=icon_bg,
        display="flex",
        align_items="center",
        justify_content="center",
    )

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(
                    label,
                    font_size="0.75rem",
                    font_weight="500",
                    color=COLORS["text_secondary"],
                ),
                rx.text(
                    value,
                    font_size="1.25rem",
                    font_weight="800",
                    color=COLORS["text_dark"],
                    letter_spacing="-0.03em",
                ),
                rx.cond(
                    sub != "",
                    rx.text(sub, font_size="0.7rem", color=COLORS["muted"]),
                    rx.fragment(),
                ),
                spacing="1",
                align_items="flex-start",
            ),
            icon_box,
            justify="between",
            width="100%",
        ),
        **KPI_CARD_STYLE,
    )


def kpi_grid(*cards: rx.Component) -> rx.Component:
    """Responsive grid wrapper for KPI cards."""
    return rx.grid(
        *cards,
        columns=rx.breakpoints(initial="1", sm="2", lg="4"),
        spacing="3",
        width="100%",
        margin_bottom="1rem",
    )
