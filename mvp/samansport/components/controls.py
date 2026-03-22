"""Header date controls for SamanSport ERP Dashboard."""

import reflex as rx

from samansport.state import AppState
from samansport.styles import COLORS, TRANSITION

PRESETS = ["Ma", "7 nap", "30 nap", "Idén", "Tavaly"]


def _preset_pill(label: str, on_date_change=None) -> rx.Component:
    """Single date-range preset pill button."""
    is_active = AppState.active_preset == label
    # Chain: first update dates, then reload data
    if on_date_change is not None:
        on_click = [AppState.set_preset(label), on_date_change]
    else:
        on_click = AppState.set_preset(label)
    return rx.button(
        label,
        on_click=on_click,
        background=rx.cond(is_active, COLORS["accent"], COLORS["white"]),
        color=rx.cond(is_active, COLORS["white"], COLORS["700"]),
        border=rx.cond(
            is_active,
            f"1px solid {COLORS['accent']}",
            f"1px solid {COLORS['300']}",
        ),
        border_radius="9999px",
        padding="0.25rem 0.875rem",
        font_size="0.8rem",
        cursor="pointer",
        transition=TRANSITION,
        _hover={
            "border_color": COLORS["accent"],
            "opacity": "0.85",
        },
        variant="ghost",
    )


def _date_input(label: str, value: rx.Var[str], on_change, on_date_change=None) -> rx.Component:
    """Labelled date input field."""
    if on_date_change is not None:
        handler = [on_change, on_date_change]
    else:
        handler = on_change
    return rx.box(
        rx.text(
            label,
            font_size="0.75rem",
            font_weight="500",
            color=COLORS["700"],
            margin_bottom="0.25rem",
        ),
        rx.input(
            type="date",
            value=value,
            on_change=handler,
            border=f"1px solid {COLORS['300']}",
            border_radius="8px",
            padding="0.35rem 0.5rem",
            font_size="0.8rem",
            color=COLORS["900"],
            width="160px",
        ),
    )


def controls(on_date_change=None) -> rx.Component:
    """Header area: greeting, date presets, date pickers, refresh.

    Args:
        on_date_change: Optional event handler to fire after any date/preset change.
    """
    return rx.box(
        # Top row — greeting + date
        rx.hstack(
            rx.box(
                rx.heading(
                    AppState.greeting + "! \U0001f44b",
                    font_size="1.35rem",
                    font_weight="700",
                    color=COLORS["900"],
                    line_height="1.3",
                ),
                rx.text(
                    "Itt találod az üzleti áttekintést és elemzéseket.",
                    font_size="0.85rem",
                    color=COLORS["400"],
                    margin_top="0.15rem",
                ),
            ),
            rx.hstack(
                rx.icon(tag="calendar", size=15, color=COLORS["text_secondary"]),
                rx.text(
                    AppState.formatted_date,
                    font_size="0.85rem",
                    color=COLORS["text_secondary"],
                ),
                spacing="1",
                align_items="center",
            ),
            justify_content="space-between",
            align_items="flex-start",
            width="100%",
            margin_bottom="1rem",
        ),
        # Preset pills + date pickers row
        rx.hstack(
            # Preset pills
            rx.hstack(
                *[_preset_pill(p, on_date_change=on_date_change) for p in PRESETS],
                spacing="2",
                align_items="center",
                flex_wrap="wrap",
            ),
            # Spacer
            rx.spacer(),
            # Date pickers
            rx.hstack(
                _date_input("Kezdő dátum", AppState.date_start, AppState.set_date_start, on_date_change),
                _date_input("Záró dátum", AppState.date_end, AppState.set_date_end, on_date_change),
                spacing="3",
                align_items="flex-end",
            ),
            width="100%",
            align_items="flex-end",
            flex_wrap="wrap",
            spacing="4",
        ),
        # Bottom border
        border_bottom=f"1px solid {COLORS['100']}",
        padding_bottom="1.25rem",
        margin_bottom="1.25rem",
    )
