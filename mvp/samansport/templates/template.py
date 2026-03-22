"""Page template wrapper — sidebar + main content layout."""

import reflex as rx

from samansport.state import AppState
from samansport.styles import COLORS, TRANSITION, SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH
from samansport.components.sidebar import sidebar
from samansport.components.controls import controls


def template(page_fn=None, *, on_date_change=None):
    """Decorator that wraps a page function with the standard layout.

    Usage::

        @template
        def simple_page() -> rx.Component:
            return rx.text("Hello")

        @template(on_date_change=MyState.reload_data)
        def data_page() -> rx.Component:
            return rx.text("Data")
    """

    def decorator(fn):
        def wrapper() -> rx.Component:
            return rx.box(
                sidebar(),
                rx.box(
                    controls(on_date_change=on_date_change),
                    fn(),
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
        wrapper.__name__ = fn.__name__
        wrapper.__module__ = fn.__module__
        return wrapper

    # Support both @template and @template(on_date_change=...)
    if page_fn is not None:
        return decorator(page_fn)
    return decorator
