from __future__ import annotations

import os

# Backend API URL (FastAPI server)
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# NiceGUI Server Settings
APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT: int = int(os.getenv("APP_PORT", "8501"))

# Application Metadata
APP_TITLE: str = "DataPilot — Autonomous Data Analyst"
APP_FAVICON: str = "✨"

