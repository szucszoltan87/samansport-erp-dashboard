"""Page template wrapper — sidebar + main content layout."""

import reflex as rx

from samansport.state import AppState
from samansport.styles import COLORS, TRANSITION, SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH
from samansport.components.sidebar import sidebar
from samansport.components.controls import controls


def template(page_fn):
    """Decorator that wraps a page function with the standard layout.

    Usage::

        @template
        def dashboard_page() -> rx.Component:
            return rx.text("Hello")
    """

    def wrapper() -> rx.Component:
        return rx.box(
            sidebar(),
            rx.box(
                controls(),
                page_fn(),
                margin_left=rx.cond(
                    AppState.sidebar_collapsed,
                    SIDEBAR_COLLAPSED_WIDTH,
                    SIDEBAR_WIDTH,
                ),
                transition=TRANSITION,
                padding="1.5rem 2rem",
                min_height="100vh",
                background=COLORS["50"],
            ),
        )

    # Preserve function metadata so Reflex page routing works correctly.
    wrapper.__name__ = page_fn.__name__
    wrapper.__module__ = page_fn.__module__
    return wrapper
