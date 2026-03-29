import reflex as rx
from datetime import datetime, date, timedelta


class AppState(rx.State):
    """Global application state."""

    # Sidebar
    sidebar_collapsed: bool = False

    # Date range (defaults set via _default_start / _default_end)
    date_start: str = (date.today() - timedelta(days=30)).isoformat()
    date_end: str = date.today().isoformat()
    active_preset: str = "30 nap"

    # Period toggle
    period: str = "Havi"

    # Sync info
    last_synced: str = ""
    connection_ok: bool = True
    connection_mode: str = ""

    # Current page
    current_page: str = "dashboard"

    def check_connection_and_sync(self):
        """Fetch connection health and last sync timestamp from the API."""
        try:
            import sys
            import os

            _mvp_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
            if _mvp_dir not in sys.path:
                sys.path.insert(0, _mvp_dir)
            import tharanis_client as api

            health = api.check_connection()
            self.connection_ok = health.get("ok", False)
            self.connection_mode = health.get("mode", "")

            raw_ts = api.get_last_sync_time()
            if raw_ts:
                from datetime import datetime as _dt

                try:
                    parsed = _dt.fromisoformat(raw_ts.replace("Z", "+00:00"))
                    self.last_synced = parsed.strftime("%Y.%m.%d %H:%M")
                except Exception:
                    self.last_synced = ""
            else:
                self.last_synced = ""
        except Exception:
            self.connection_ok = False
            self.last_synced = ""

    def _init_dates(self):
        """Initialize dates if empty."""
        if not self.date_start or not self.date_end:
            today = date.today()
            self.date_start = (today - timedelta(days=30)).isoformat()
            self.date_end = today.isoformat()

    @rx.var
    def greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Jó reggelt"
        elif hour < 18:
            return "Jó napot"
        return "Jó estét"

    @rx.var
    def formatted_date(self) -> str:
        today = date.today()
        hu_months = {
            1: "jan.",
            2: "febr.",
            3: "márc.",
            4: "ápr.",
            5: "máj.",
            6: "jún.",
            7: "júl.",
            8: "aug.",
            9: "szept.",
            10: "okt.",
            11: "nov.",
            12: "dec.",
        }
        return f"{today.year}. {hu_months[today.month]} {today.day}."

    def toggle_sidebar(self):
        self.sidebar_collapsed = not self.sidebar_collapsed

    def set_preset(self, preset: str):
        today = date.today()
        ranges = {
            "Ma": (today, today),
            "7 nap": (today - timedelta(days=7), today),
            "30 nap": (today - timedelta(days=30), today),
            "Idén": (today.replace(month=1, day=1), today),
            "Tavaly": (
                today.replace(year=today.year - 1, month=1, day=1),
                today.replace(year=today.year - 1, month=12, day=31),
            ),
        }
        if preset in ranges:
            start, end = ranges[preset]
            self.date_start = start.isoformat()
            self.date_end = end.isoformat()
            self.active_preset = preset

    def set_period(self, period: str):
        self.period = period

    def set_date_start(self, value: str):
        self.date_start = value
        self.active_preset = ""

    def set_date_end(self, value: str):
        self.date_end = value
        self.active_preset = ""

    def navigate_to(self, page: str):
        self.current_page = page
        return rx.redirect(f"/{page}" if page != "dashboard" else "/")
