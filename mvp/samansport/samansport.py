"""SamanSport ERP Dashboard — Reflex app entry point."""

import reflex as rx

# Import pages so their @rx.page decorators register routes
from samansport.pages import dashboard, analytics  # noqa: F401
from samansport.styles import BASE_STYLE

app = rx.App(style=BASE_STYLE)
