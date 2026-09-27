"""
DataPilot— Left Sidebar Component
=======================================
Renders the left navigation sidebar including brand, new analysis trigger,
dataset card, searchable schema viewer, query history list, and footer navigation
in a clean, professional light theme matching the reference design.
"""

from __future__ import annotations

from typing import Any, Callable
from nicegui import ui

from state.app_state import AppState
from components.history import render_history_item


def get_column_icon(dtype: str) -> str:
    """Return appropriate Material icon name for column dtype."""
    d = dtype.lower()
    if any(k in d for k in ("int", "float", "double", "decimal", "numeric", "number")):
        return "tag"
    if any(k in d for k in ("date", "time", "timestamp")):
        return "calendar_today"
    return "title"


def render_left_sidebar(
    state: AppState,
    on_new_analysis: Callable[[], None],
    on_select_history: Callable[[dict[str, Any]], None],
    on_toggle_collapse: Callable[[], None],
    on_switch_tab: Callable[[str], None],
) -> None:
    """Render full left sidebar content inside a white rounded card."""
    with ui.column().classes("h-full w-full flex-col justify-between bg-white rounded-2xl border border-slate-200/80 shadow-sm p-4 gap-3 select-none"):
        # Top + Middle scrollable area
        with ui.column().classes("w-full flex-1 min-h-0 gap-3 overflow-hidden"):
            # 1. Brand Header
            with ui.row().classes("w-full items-center justify-between px-0.5 pt-0.5"):
                with ui.row().classes("items-center gap-2.5"):
                    with ui.element("div").classes(
                        "h-8 w-8 grid place-items-center rounded-lg bg-blue-600 shadow-sm"
                    ):
                        ui.icon("auto_awesome", size="16px").classes("text-white")
                    with ui.column().classes("gap-0"):
                        ui.label("DataPilot").classes("text-sm font-bold text-slate-900 tracking-tight leading-none")
                        ui.label("Autonomous Analyst").classes("text-[10px] text-slate-400 mt-1")

                with ui.button(on_click=on_toggle_collapse).props("flat dense round").classes(
                    "text-slate-400 hover:text-slate-700"
                ):
                    ui.icon("chevron_right", size="20px")

            # 2. New Analysis Button
            with ui.button(on_click=on_new_analysis).classes(
                "w-full bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-2 px-3 font-semibold text-xs shadow-sm flex items-center justify-between transition-transform active:scale-98"
            ):
                with ui.row().classes("items-center justify-between w-full"):
                    with ui.row().classes("items-center gap-1.5"):
                        ui.icon("add", size="16px")
                        ui.label("NEW ANALYSIS")
                    with ui.element("kbd").classes("bg-white/20 rounded px-1.5 py-0.5 text-[9px] font-mono text-white"):
                        ui.label("⌘K")

            # 3. Connected Dataset Card (if loaded)
            if state.has_dataset:
                with ui.card().classes("w-full rounded-xl p-3 border border-slate-200/80 bg-slate-50/60 shadow-none"):
                    with ui.row().classes("items-center gap-2 mb-2"):
                        with ui.element("div").classes("h-7 w-7 grid place-items-center rounded-lg bg-blue-100/80 text-blue-600"):
                            ui.icon("storage", size="16px")
                        with ui.column().classes("gap-0 flex-1 min-w-0"):
                            ui.label(state.dataset_name).classes("text-xs font-semibold text-slate-800 truncate")
                            with ui.row().classes("items-center gap-1"):
                                ui.element("div").classes("h-1.5 w-1.5 rounded-full bg-emerald-500")
                                ui.label("Connected").classes("text-[10px] text-emerald-600 font-medium")

                    with ui.row().classes("w-full grid grid-cols-2 gap-2 text-center"):
                        with ui.element("div").classes("rounded-lg bg-white p-1.5 border border-slate-200/60"):
                            ui.label("Rows").classes("text-[9px] text-slate-400 uppercase tracking-wider")
                            ui.label(f"{state.row_count:,}").classes("text-xs font-bold text-slate-800 mt-0.5")
                        with ui.element("div").classes("rounded-lg bg-white p-1.5 border border-slate-200/60"):
                            ui.label("Columns").classes("text-[9px] text-slate-400 uppercase tracking-wider")
                            ui.label(f"{len(state.columns)}").classes("text-xs font-bold text-slate-800 mt-0.5")

            # 4. Middle Scrollable: Schema & Recent History
            with ui.column().classes("w-full flex-1 min-h-0 overflow-y-auto pr-1 gap-3 scrollbar-custom"):
                # Schema Section
                if state.has_dataset and state.columns:
                    with ui.expansion(f"SCHEMA ({len(state.columns)})", icon="schema", value=True).classes(
                        "w-full text-slate-700 text-xs font-bold"
                    ):
                        schema_search = (
                            ui.input(placeholder="Search columns…")
                            .props("dense outlined rounded")
                            .classes("w-full text-xs mb-2")
                        )
                        columns_container = ui.column().classes("w-full gap-1")

                        def update_columns(search_term: str = "") -> None:
                            columns_container.clear()
                            term = search_term.lower()
                            filtered = [c for c in state.columns if term in c.name.lower()]
                            with columns_container:
                                for col in filtered:
                                    with ui.row().classes(
                                        "w-full items-center justify-between px-2 py-1 rounded hover:bg-slate-100 text-slate-700 text-xs font-mono"
                                    ):
                                        with ui.row().classes("items-center gap-2 min-w-0"):
                                            ui.icon(get_column_icon(col.dtype), size="14px").classes("text-blue-500")
                                            ui.label(col.name).classes("truncate")
                                        ui.label(col.dtype).classes("text-[10px] text-slate-400 font-sans")
                                if not filtered:
                                    ui.label("No matching columns").classes("text-[11px] text-slate-400 py-2 text-center w-full")

                        schema_search.on_value_change(lambda e: update_columns(e.value))
                        update_columns()

                # History Section
                with ui.expansion(f"RECENT ({len(state.session_queries)})", icon="history", value=True).classes(
                    "w-full text-slate-700 text-xs font-bold"
                ):
                    if not state.session_queries:
                        ui.label("No queries yet").classes("text-xs text-slate-400 py-6 text-center w-full")
                    else:
                        with ui.column().classes("w-full gap-1"):
                            for item in reversed(state.session_queries):
                                is_sel = str(item.get("id")) == str(state.selected_history_id)
                                render_history_item(item, is_sel, on_select_history)

        # 5. Footer Navigation (Workspace / Analytics)
        with ui.column().classes("w-full border-t border-slate-200/80 pt-2 gap-1.5"):
            def go_workspace() -> None:
                on_switch_tab("analysis")

            def go_analytics() -> None:
                on_switch_tab("metrics")

            ws_active = state.active_tab == "analysis"
            ws_classes = (
                "w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-colors "
                + ("bg-blue-50 text-blue-600 border border-blue-200" if ws_active else "text-slate-600 hover:text-slate-900 hover:bg-slate-100")
            )
            with ui.button(on_click=go_workspace).classes(ws_classes).props("flat"):
                ui.icon("auto_awesome", size="16px")
                ui.label("WORKSPACE")

            an_active = state.active_tab == "metrics"
            an_classes = (
                "w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold transition-colors "
                + ("bg-blue-50 text-blue-600 border border-blue-200" if an_active else "text-slate-600 hover:text-slate-900 hover:bg-slate-100")
            )
            with ui.button(on_click=go_analytics).classes(an_classes).props("flat"):
                ui.icon("bar_chart", size="16px")
                ui.label("ANALYTICS")
