from __future__ import annotations

from typing import Callable
from nicegui import ui

from state.app_state import AppState


def render_header(
    state: AppState,
    on_toggle_left_sidebar: Callable[[], None],
    on_toggle_right_sidebar: Callable[[], None],
) -> None:
    """Render top header bar matching the modern light theme."""
    latest_msg = state.get_latest_assistant_message()
    report_title = (
        latest_msg.report.title
        if latest_msg and latest_msg.report and latest_msg.report.title
        else ("Data Analysis" if latest_msg else "Ready for questions")
    )
    model_name = latest_msg.model if latest_msg and latest_msg.model else "llama-3.3-70b-versatile"

    with ui.element("header").classes(
        "sticky top-0 z-20 flex items-center justify-between border-b border-slate-100 bg-white px-4 sm:px-6 py-2.5 shrink-0 w-full"
    ):
        # Left side: sidebar toggle + breadcrumbs
        with ui.row().classes("items-center gap-3 min-w-0"):
            with ui.button(on_click=on_toggle_left_sidebar).props("flat dense round").classes(
                "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            ):
                ui.icon("menu", size="20px")

            with ui.column().classes("gap-0 min-w-0"):
                if state.has_dataset:
                    ui.label(f"{state.dataset_name} · {state.row_count:,} rows").classes(
                        "text-[10px] font-medium uppercase tracking-wider text-slate-400"
                    )
                ui.label(report_title).classes("text-sm font-bold text-slate-900 truncate")

        # Right side: badges, toggles, right sidebar toggle
        with ui.row().classes("items-center gap-2 sm:gap-3"):
            if state.has_dataset:
                # Live status pill
                with ui.element("div").classes(
                    "hidden sm:flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] text-slate-600"
                ):
                    ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse")
                    ui.label("Live")

                # Model chip
                with ui.element("div").classes(
                    "hidden md:flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[11px] font-medium text-blue-700"
                ):
                    ui.icon("auto_awesome", size="12px").classes("text-blue-600")
                    ui.label(model_name)

            # Dark/Light theme toggle
            def toggle_theme() -> None:
                state.is_dark = not state.is_dark
                ui.dark_mode().set_value(state.is_dark)
                state.notify_change()

            with ui.button(on_click=toggle_theme).props("flat dense round").classes(
                "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            ):
                ui.icon("dark_mode" if state.is_dark else "light_mode", size="18px")

            # Right sidebar toggle (only in analysis tab with dataset)
            if state.has_dataset and state.active_tab == "analysis":
                with ui.button(on_click=on_toggle_right_sidebar).props("flat dense round").classes(
                    "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                ):
                    ui.icon("tune", size="20px")
