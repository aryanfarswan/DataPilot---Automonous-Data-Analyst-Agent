"""
DataPilot — Right Sidebar Component (Pipeline & Observability)
===================================================================
Renders the execution trace monitor, sequential stage badges, live runtime
metadata, and execution statistics in a clean light theme matching the reference design.
"""

from __future__ import annotations

from typing import Any, Callable
from nicegui import ui

from state.app_state import AppState
from components.trace import resolve_trace_steps, render_trace_stage


def render_stat_box(icon_name: str, label: str, value: str) -> None:
    """Render a single key-value run metric box."""
    with ui.element("div").classes("rounded-xl border border-slate-200/80 bg-white p-3 flex flex-col gap-1 hover:border-blue-200 transition-colors"):
        with ui.row().classes("items-center gap-1.5 text-xs text-slate-500 font-medium"):
            ui.icon(icon_name, size="15px").classes("text-blue-600")
            ui.label(label)
        ui.label(value).classes("text-sm font-bold text-slate-800 truncate")


def render_right_sidebar(
    state: AppState,
    on_toggle_collapse: Callable[[], None],
) -> None:
    """Render full right sidebar execution trace and statistics."""
    latest_msg = state.get_latest_assistant_message()
    has_trace = bool(state.trace_history)

    # Determine overall pipeline status
    if state.is_analyzing:
        pipeline_status = "Running"
        status_badge_style = "bg-blue-50 text-blue-600 border-blue-200"
    elif latest_msg and latest_msg.success is False:
        pipeline_status = "Failed"
        status_badge_style = "bg-rose-50 text-rose-600 border-rose-200"
    elif has_trace:
        pipeline_status = "Completed"
        status_badge_style = "bg-emerald-50 text-emerald-600 border-emerald-200"
    else:
        pipeline_status = "Idle"
        status_badge_style = "bg-slate-100 text-slate-500 border-slate-200"

    resolved_steps = resolve_trace_steps(
        state.trace_history,
        is_analyzing=state.is_analyzing,
        active_status=latest_msg.success if latest_msg else None,
    )

    with ui.column().classes(
        "h-full w-full flex-col bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 gap-4 overflow-y-auto scrollbar-custom select-none"
    ):
        # Header with collapse button
        with ui.row().classes("w-full items-center justify-between pb-1"):
            with ui.row().classes("items-center gap-2 text-sm font-bold text-slate-800"):
                ui.icon("terminal", size="18px").classes("text-blue-600")
                ui.label("Execution Trace")
            with ui.button(on_click=on_toggle_collapse).props("flat dense round").classes(
                "text-blue-600 hover:text-blue-800"
            ):
                ui.icon("chevron_right", size="20px")

        # 1. Pipeline Status Card
        with ui.card().classes("w-full rounded-xl p-3.5 border border-slate-200/80 bg-white shadow-none"):
            with ui.row().classes("w-full items-center justify-between mb-3"):
                with ui.row().classes("items-center gap-1.5 text-xs font-bold text-slate-800"):
                    ui.icon("apps", size="16px").classes("text-blue-600")
                    ui.label("Pipeline")
                with ui.element("div").classes(
                    f"rounded-full px-2.5 py-0.5 text-[10px] font-medium border {status_badge_style}"
                ):
                    ui.label(pipeline_status)

            # Trace steps list
            with ui.column().classes("w-full gap-1"):
                for s in resolved_steps:
                    render_trace_stage(s)

        # 2. Run Statistics Section
        with ui.column().classes("w-full gap-2.5"):
            with ui.row().classes("items-center gap-2 text-xs font-bold text-slate-800"):
                ui.icon("bar_chart", size="18px").classes("text-blue-600")
                ui.label("Run Statistics")

            exec_time = latest_msg.execution_time if latest_msg and latest_msg.execution_time else None
            latency_str = f"{(exec_time / 1000):.2f}s" if exec_time else "--"
            retries_str = str(latest_msg.retry_count) if latest_msg and latest_msg.retry_count is not None else "--"
            provider_str = latest_msg.provider or "Groq" if latest_msg else "--"
            model_str = latest_msg.model or "llama-3.3-70b-versatile" if latest_msg else "--"

            rows_returned = None
            charts_count = 0
            confidence = None
            if latest_msg and latest_msg.report:
                if latest_msg.report.tables and latest_msg.report.tables[0].rows:
                    rows_returned = len(latest_msg.report.tables[0].rows)
                charts_count = len(latest_msg.report.charts)
                if latest_msg.report.executive_summary:
                    confidence = latest_msg.report.executive_summary.confidence

            with ui.grid().classes("grid grid-cols-2 gap-2 w-full"):
                render_stat_box("schedule", "Latency", latency_str)
                render_stat_box("sync", "Retries", retries_str)
                render_stat_box("cloud", "Provider", provider_str)
                render_stat_box("psychology", "Model", model_str)

                if rows_returned is not None:
                    render_stat_box("table_rows", "Rows", f"{rows_returned:,}")
                if charts_count > 0:
                    render_stat_box("bar_chart", "Charts", str(charts_count))
                if confidence:
                    render_stat_box("verified_user", "Confidence", confidence)
                if latest_msg:
                    status_text = "Success" if latest_msg.success else "Failed"
                    render_stat_box("info", "Status", status_text)
