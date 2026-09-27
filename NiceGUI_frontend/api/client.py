from __future__ import annotations

import logging
from typing import Any
import httpx

from config import BACKEND_URL

logger = logging.getLogger(__name__)


class ApiClient:
    """Asynchronous client for DataPilot FastAPI backend."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or BACKEND_URL).rstrip("/")

    async def upload_csv(self, filename: str, content: bytes) -> dict[str, Any]:
        """
        Upload a CSV file to the backend.
        Returns UploadResponse dict with session_id, dataset_id, row_count, columns.
        """
        url = f"{self.base_url}/upload"
        files = {"file": (filename, content, "text/csv")}
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(url, files=files)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                detail = "Upload failed."
                try:
                    detail = e.response.json().get("detail", str(e))
                except Exception:
                    detail = e.response.text or str(e)
                logger.error("Upload failed: %s", detail)
                raise RuntimeError(detail) from e
            except Exception as e:
                logger.error("Unexpected error during upload: %s", e)
                raise RuntimeError(f"Network error during upload: {e}") from e

    async def analyze(self, session_id: str, question: str) -> dict[str, Any]:
        """
        Send a natural language data analysis query to the backend.
        Returns complete analysis payload with report, debug, and query info.
        """
        url = f"{self.base_url}/analyze"
        payload = {"session_id": session_id, "question": question}
        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                detail = "Analysis failed."
                try:
                    detail = e.response.json().get("detail", str(e))
                except Exception:
                    detail = e.response.text or str(e)
                logger.error("Analysis failed: %s", detail)
                raise RuntimeError(detail) from e
            except Exception as e:
                logger.error("Unexpected error during analysis: %s", e)
                raise RuntimeError(f"Network error during analysis: {e}") from e

    async def get_trace(self, session_id: str) -> list[dict[str, Any]]:
        """
        Fetch execution trace steps from the backend for a given session.
        """
        url = f"{self.base_url}/execution/{session_id}/trace"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("trace", [])
                return []
            except Exception as e:
                logger.warning("Failed to poll trace: %s", e)
                return []

    async def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """
        Retrieve query history for the specified session.
        """
        url = f"{self.base_url}/history/{session_id}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("history", [])
                return []
            except Exception as e:
                logger.warning("Failed to fetch history: %s", e)
                return []

    async def get_metrics(self) -> dict[str, Any]:
        """
        Fetch lifetime execution metrics for analytics dashboard.
        """
        url = f"{self.base_url}/metrics"
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("metrics", {})
                return {}
            except Exception as e:
                logger.warning("Failed to fetch metrics: %s", e)
                return {}

    def get_pdf_download_url(self, execution_id: int | str) -> str:
        """
        Returns direct backend URL to download the generated PDF report.
        """
        return f"{self.base_url}/report/{execution_id}/pdf"


# Shared singleton instance
api = ApiClient()

