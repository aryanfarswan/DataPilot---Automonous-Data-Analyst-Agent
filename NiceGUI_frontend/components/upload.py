"""
DataPilot — CSV Drag-and-Drop Upload Component
===================================================
Handles CSV file uploads via NiceGUI's ui.upload element.
Visually matches the reference light design with soft blue dropzone,
circular icon badge, drag-and-drop support, and 100MB validation.
"""

from __future__ import annotations

import logging
from typing import Callable, Coroutine, Any
from nicegui import events, ui

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


def render_upload_hero(
    on_upload: Callable[[str, bytes], Coroutine[Any, Any, None]],
    is_uploading: bool = False,
    error_message: str | None = None,
    on_error: Callable[[str], None] | None = None,
) -> ui.upload | None:
    """
    Render full hero upload section matching the reference design.
    Returns the ui.upload element so external buttons (like left sidebar's '+ New analysis')
    can trigger file selection via uploader.run_method('pickFiles').
    """
    with ui.column().classes("w-full max-w-[660px] mx-auto items-center text-center py-12 px-4 gap-6"):
        # 1. Top Glowing Icon badge
        with ui.element("div").classes(
            "w-14 h-14 grid place-items-center rounded-2xl bg-blue-100/70 border border-blue-200/80 shadow-[0_0_20px_rgba(59,130,246,0.18)] mb-1"
        ):
            ui.icon("auto_awesome", size="28px").classes("text-blue-600")

        # 2. Headings
        with ui.column().classes("gap-1.5 items-center"):
            ui.label("Autonomous Data Analyst").classes("text-3xl font-bold tracking-tight text-slate-900")
            ui.label(
                "Upload a CSV and ask questions in plain English. The AI agent queries, visualizes, and explains your data instantly."
            ).classes("text-sm text-slate-500 max-w-md leading-relaxed")

        # 3. Error Banner (if error occurred)
        if error_message:
            with ui.row().classes(
                "w-full items-center gap-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-600 text-xs animate-fade-in"
            ):
                ui.icon("error", size="18px").classes("shrink-0")
                ui.label(error_message).classes("font-medium text-left flex-1")

        # 4. Upload Drop Zone or Loading State
        uploader_elem: ui.upload | None = None

        if is_uploading:
            # Loading State while backend processes CSV
            with ui.element("div").classes("custom-dropzone flex flex-col items-center justify-center py-12 gap-3 select-none"):
                with ui.element("div").classes(
                    "h-16 w-16 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center mb-1"
                ):
                    ui.spinner("dots", size="36px", color="blue")
                ui.label("Uploading dataset...").classes("text-base font-semibold text-slate-900")
                ui.label("Normalizing encoding and registering DuckDB table...").classes(
                    "text-xs text-blue-600 animate-pulse font-medium"
                )
        else:
            # Relative container card
            with ui.element("div").classes("custom-dropzone group"):
                # A. Visible Presentation Layer (pure NiceGUI / Tailwind, always visible!)
                with ui.column().classes("w-full items-center justify-center text-center gap-2.5 select-none pointer-events-none relative z-10 py-1"):
                    # Top circular badge with soft blue ring
                    with ui.element("div").classes(
                        "h-20 w-20 rounded-full bg-blue-100/70 border border-blue-200/80 flex items-center justify-center shadow-sm mb-1 ring-4 ring-blue-50 transition-transform duration-300 group-hover:scale-105"
                    ):
                        ui.icon("cloud_upload", size="38px").classes("text-blue-600")

                    # Main title
                    ui.label("Click to upload your CSV file").classes("text-lg font-bold text-slate-900 tracking-tight")

                    # Subtitle
                    ui.label("or drag and drop it here").classes("text-xs text-slate-500")

                    # Max size & format
                    ui.label("Maximum file size: 100MB • CSV files only").classes("text-[11px] text-slate-400")

                    # Browse button
                    with ui.element("div").classes(
                        "bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl px-5 py-2.5 shadow-md shadow-blue-500/20 flex items-center gap-2 mt-2 transition-transform duration-200 group-hover:scale-105"
                    ):
                        ui.icon("folder", size="16px")
                        ui.label("Browse CSV File")

                # B. Active Quasar Uploader (covers card with opacity 0 at z-index 20)
                async def handle_upload_event(e: events.UploadEventArguments) -> None:
                    try:
                        file_obj = getattr(e, "file", None)
                        if file_obj is not None:
                            filename = getattr(file_obj, "name", "dataset.csv")
                            content = await file_obj.read()
                        elif hasattr(e, "content"):
                            filename = getattr(e, "name", "dataset.csv")
                            content = await e.content.read()
                        else:
                            raise ValueError("Could not access uploaded file content.")

                        # Validate CSV extension
                        if not filename.lower().endswith(".csv"):
                            err = "Only CSV files are accepted. Please select a file ending in .csv"
                            logger.warning(err)
                            ui.notify(err, type="negative", position="bottom-right")
                            if on_error:
                                on_error(err)
                            return

                        # Validate file size (100 MB)
                        if len(content) > MAX_FILE_SIZE_BYTES:
                            size_mb = len(content) / (1024 * 1024)
                            err = f"File exceeds 100MB limit ({size_mb:.1f}MB)."
                            logger.warning(err)
                            ui.notify(err, type="negative", position="bottom-right")
                            if on_error:
                                on_error(err)
                            return

                        await on_upload(filename, content)
                    except Exception as exc:
                        logger.error("Upload error: %s", exc)
                        err = f"Upload failed: {exc}"
                        ui.notify(err, type="negative", position="bottom-right")
                        if on_error:
                            on_error(err)

                uploader_elem = (
                    ui.upload(
                        on_upload=handle_upload_event,
                        max_files=1,
                        auto_upload=True,
                    )
                    .props('accept=".csv" flat')
                )

        # 5. Features checklist row below drop zone
        with ui.row().classes("gap-6 text-xs text-slate-600 items-center justify-center mt-2 flex-wrap"):
            with ui.row().classes("items-center gap-1.5"):
                ui.icon("check_circle", size="16px").classes("text-emerald-500")
                ui.label("Automatic schema discovery").classes("font-medium")
            with ui.row().classes("items-center gap-1.5"):
                ui.icon("check_circle", size="16px").classes("text-emerald-500")
                ui.label("Local DuckDB engine").classes("font-medium")
            with ui.row().classes("items-center gap-1.5"):
                ui.icon("check_circle", size="16px").classes("text-emerald-500")
                ui.label("Plotly visualizations").classes("font-medium")

        return uploader_elem
