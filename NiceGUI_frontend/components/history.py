from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable
from nicegui import ui


def format_relative_time(date_str: str | None) -> str:
    """Format an ISO timestamp or date string into human-friendly relative time."""
    if not date_str:
        return ""
    try:
        # Handle ISO strings with Z or timezone offsets
        clean_str = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(timezone.utc)
        diff = now - dt
        diff_sec = int(diff.total_seconds())

        if diff_sec < 60:
            return "Just now"
        diff_min = diff_sec // 60
        if diff_min < 60:
            return f"{diff_min}m ago"
        diff_hr = diff_min // 60
        if diff_hr < 24:
            return f"{diff_hr}h ago"
        diff_day = diff_hr // 24
        if diff_day < 7:
            return f"{diff_day}d ago"
        return dt.strftime("%b %d")
    except Exception:
        return ""


def render_history_item(
    item: dict[str, Any],
    is_selected: bool,
    on_select: Callable[[dict[str, Any]], None],
) -> None:
    """Render a single historical query item with status dot and relative time."""
    question = item.get("question", "Untitled query")
    success = item.get("success")
    created_at = item.get("created_at")
    rel_time = format_relative_time(created_at)

    item_classes = (
        "w-full text-left p-2.5 rounded-lg transition-colors cursor-pointer block border "
        + (
            "bg-blue-50 border-blue-200 text-blue-700 font-semibold"
            if is_selected
            else "border-transparent hover:bg-slate-100 text-slate-700"
        )
    )

    with ui.element("button").classes(item_classes).on("click", lambda: on_select(item)):
        with ui.row().classes("w-full items-start justify-between no-wrap gap-2"):
            ui.label(question).classes("text-xs font-medium truncate flex-1 text-slate-800")
            if success is not None:
                dot_color = "bg-emerald-500" if success else "bg-rose-500"
                ui.element("div").classes(f"h-2 w-2 rounded-full {dot_color} shrink-0 mt-1")
        if rel_time:
            ui.label(rel_time).classes("text-[10px] text-slate-400 mt-1")
