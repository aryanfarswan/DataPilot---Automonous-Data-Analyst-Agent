from __future__ import annotations

import os
import sys
from pathlib import Path

# Add current directory to Python path for seamless imports
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from nicegui import app, ui

from config import APP_FAVICON, APP_HOST, APP_PORT, APP_TITLE
from pages.workspace import create_workspace_view
from state.app_state import AppState

# Preload custom CSS styles
CSS_FILE = CURRENT_DIR / "styles" / "app.css"
CUSTOM_CSS = CSS_FILE.read_text(encoding="utf-8") if CSS_FILE.exists() else ""


@ui.page("/")
def index_page() -> None:
    """Main application landing page with client-scoped state."""
    # Inject styling
    if CUSTOM_CSS:
        ui.add_head_html(f"<style>{CUSTOM_CSS}</style>")

    # Initialize Quasar dark mode (default light)
    ui.dark_mode(False)

    # Client-scoped reactive application state
    client_state = AppState(is_dark=False)

    # Render workspace view
    create_workspace_view(client_state)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host=APP_HOST,
        port=APP_PORT,
        title=APP_TITLE,
        favicon=APP_FAVICON,
        dark=False,
        reload=False,
    )

