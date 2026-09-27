"""
DataPilot — Execution Trace Stage Resolver & Components
============================================================
Translates raw LangGraph Pregel trace steps into structured, user-facing
pipeline stages matching the light theme reference design.
"""

from __future__ import annotations

from typing import Any
from nicegui import ui

FRIENDLY_LABELS: dict[str, str] = {
    "schema_profiler": "Understanding dataset",
    "planner": "Planning analysis",
    "sql_generator": "Generating",
    "sandbox_executor": "Executing query",
    "validator": "Validating results",
    "report_agent": "Generating report",
}

DEFAULT_STEPS: list[str] = [
    "Understanding dataset",
    "Planning analysis",
    "Generating",
    "Executing query",
    "Validating results",
    "Generating report",
]


def resolve_trace_steps(
    trace: list[dict[str, Any]],
    is_analyzing: bool,
    active_status: bool | None,
) -> list[dict[str, Any]]:
    """
    Resolve sequential pipeline steps into status and metadata.
    """
    has_trace = bool(trace)
    next_running_idx = -1
    last_executed_idx = -1

    if has_trace:
        last_node_name = trace[-1].get("metadata", {}).get("source") or trace[-1].get("step", "")
        last_label = FRIENDLY_LABELS.get(last_node_name, last_node_name)
        try:
            last_executed_idx = DEFAULT_STEPS.index(last_label)
        except ValueError:
            last_executed_idx = -1

        if is_analyzing:
            next_running_idx = min(len(DEFAULT_STEPS) - 1, last_executed_idx + 1)
    elif is_analyzing:
        next_running_idx = 0

    resolved = []
    for idx, label in enumerate(DEFAULT_STEPS):
        status = "pending"
        duration_ms = None
        details = None

        # Find matching trace step
        for t in trace:
            node_name = t.get("metadata", {}).get("source") or t.get("step", "")
            if FRIENDLY_LABELS.get(node_name, node_name) == label:
                duration_ms = t.get("metadata", {}).get("writes", {}).get("duration_ms") or t.get("duration_ms")
                details = t.get("values", {}).get("retry_target") or t.get("details")
                if details and not str(details).startswith("Routing:"):
                    details = f"Routing: {details}"
                break

        if active_status is True:
            status = "success"
        else:
            if next_running_idx != -1:
                if idx < next_running_idx:
                    status = "success"
                elif idx == next_running_idx:
                    status = "running"
                else:
                    status = "pending"
            else:
                # Finished analysis
                if idx < last_executed_idx:
                    status = "success"
                elif idx == last_executed_idx:
                    status = "failed" if active_status is False else "success"
                else:
                    status = "pending"

        resolved.append({
            "step": label,
            "status": status,
            "duration_ms": duration_ms,
            "details": details,
        })

    return resolved


def render_trace_stage(
    step: dict[str, Any],
    is_expanded: bool = False,
) -> None:
    """Render a single pipeline execution step card."""
    status = step.get("status", "pending")
    label = step.get("step", "")
    duration_ms = step.get("duration_ms")
    details = step.get("details")

    is_running = status == "running"
    is_done = status == "success"
    is_failed = status == "failed"
    is_pending = status == "pending"

    # Container classes
    box_classes = (
        "flex w-full items-center justify-between gap-2.5 rounded-xl px-2.5 py-1.5 text-left border transition-all duration-200 "
    )
    if is_running:
        box_classes += "bg-blue-50/60 border-blue-200 shadow-sm"
    elif is_pending:
        box_classes += "border-transparent opacity-60"
    else:
        box_classes += "border-transparent hover:bg-slate-50"

    with ui.column().classes("w-full gap-0.5"):
        with ui.row().classes(box_classes):
            with ui.row().classes("items-center gap-2.5 min-w-0 flex-1"):
                # Left circular icon indicator
                icon_box = "grid h-6 w-6 shrink-0 place-items-center rounded-full border transition-all "
                if is_done:
                    icon_box += "bg-emerald-50 text-emerald-600 border-emerald-200"
                    with ui.element("div").classes(icon_box):
                        ui.icon("check", size="14px")
                elif is_failed:
                    icon_box += "bg-rose-50 text-rose-600 border-rose-200"
                    with ui.element("div").classes(icon_box):
                        ui.icon("close", size="14px")
                elif is_running:
                    icon_box += "bg-blue-50 text-blue-600 border-blue-300 ring-2 ring-blue-100"
                    with ui.element("div").classes(icon_box):
                        ui.spinner("dots", size="sm", color="blue")
                else:
                    icon_box += "bg-slate-100 text-slate-400 border-slate-200"
                    with ui.element("div").classes(icon_box):
                        ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-slate-400")

                # Title and subtext
                with ui.column().classes("min-w-0 flex-1 gap-0"):
                    title_classes = "text-xs transition-colors "
                    if is_running:
                        title_classes += "text-blue-600 font-semibold"
                    elif is_done:
                        title_classes += "text-slate-700 font-medium"
                    elif is_failed:
                        title_classes += "text-rose-600 font-medium"
                    else:
                        title_classes += "text-slate-500 font-medium"
                    ui.label(label).classes(title_classes)

                    if is_running:
                        ui.label("Processing…").classes("text-[10px] text-blue-500 animate-pulse")
                    elif duration_ms:
                        ui.label(f"{duration_ms}ms").classes("text-[10px] text-slate-400")

            # Right trailing status dot
            if is_done:
                ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0")
            elif is_running:
                ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse shrink-0")
            elif is_failed:
                ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-rose-500 shrink-0")
            else:
                ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-slate-300 shrink-0")

        # Routing or retry details if present
        if details:
            with ui.row().classes("w-full pl-9 pr-2 py-0.5 text-[10px] text-blue-600 font-mono items-center gap-1"):
                ui.icon("subdirectory_arrow_right", size="12px")
                ui.label(str(details)).classes("truncate")
