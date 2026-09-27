from __future__ import annotations

from typing import Callable, Coroutine, Any
from nicegui import ui

from state.app_state import AppState, ChatMessage
from components.report import render_report
from components.trace import resolve_trace_steps


def render_user_message(content: str) -> None:
    """Render a user prompt bubble."""
    with ui.row().classes("w-full justify-end my-2"):
        with ui.element("div").classes(
            "max-w-xl rounded-2xl rounded-tr-sm px-4 py-2.5 bg-blue-600 text-white text-sm shadow-sm font-medium"
        ):
            ui.label(content)


def render_empty_chat_state() -> None:
    """Render placeholder state when no questions have been asked."""
    with ui.column().classes("w-full items-center justify-center py-20 px-4 text-center gap-4"):
        with ui.element("div").classes("p-4 rounded-2xl bg-blue-50 border border-blue-200 shadow-sm"):
            ui.icon("auto_awesome", size="36px").classes("text-blue-600")
        with ui.column().classes("gap-1 items-center"):
            ui.label("Start exploring your data").classes("text-lg font-bold text-slate-900")
            ui.label("Ask questions in natural language to discover trends, anomalies, and insights.").classes(
                "text-xs text-slate-500 max-w-sm"
            )


def render_analyzing_state(state: AppState) -> None:
    """Render live analyzing card showing active pipeline stage."""
    resolved = resolve_trace_steps(state.trace_history, is_analyzing=True, active_status=None)
    running_step = next((s for s in resolved if s["status"] == "running"), None)
    stage_text = "Preparing analysis..."
    if running_step:
        step_name = running_step.get("step", "")
        if "Understanding" in step_name:
            stage_text = "Understanding your dataset..."
        elif "Planning" in step_name:
            stage_text = "Planning the analysis strategy..."
        elif "Generating" in step_name:
            stage_text = "Synthesizing DuckDB SQL..."
        elif "Executing" in step_name:
            stage_text = "Executing in isolated sandbox..."
        elif "Validating" in step_name:
            stage_text = "Validating data integrity..."
        elif "report" in step_name.lower():
            stage_text = "Generating comprehensive report..."
        else:
            stage_text = f"{step_name}..."

    with ui.card().classes(
        "w-full rounded-2xl p-5 border border-blue-200 bg-blue-50/40 animate-pulse my-4 shadow-sm"
    ):
        with ui.row().classes("items-center gap-4"):
            with ui.element("div").classes(
                "h-10 w-10 grid place-items-center rounded-xl bg-blue-100 text-blue-600 shrink-0"
            ):
                ui.spinner("dots", size="md", color="blue")
            with ui.column().classes("gap-0.5"):
                ui.label("Agent is analyzing...").classes("text-sm font-semibold text-slate-900")
                ui.label(stage_text).classes("text-xs text-blue-600 font-medium")


def render_chat_feed(state: AppState) -> None:
    """Render the full sequence of messages in chat history."""
    if not state.chat_history and not state.is_analyzing:
        render_empty_chat_state()
        return

    with ui.column().classes("w-full max-w-4xl mx-auto gap-6 px-2 sm:px-4 py-6"):
        for msg in state.chat_history:
            if msg.role == "user" and msg.content:
                render_user_message(msg.content)
            elif msg.role == "assistant" and msg.report:
                render_report(msg)

        if state.is_analyzing:
            render_analyzing_state(state)


def render_chat_composer(
    state: AppState,
    on_submit: Callable[[str], Coroutine[Any, Any, None]],
) -> None:
    """Render sticky bottom query composer with model badge and shortcut."""
    with ui.element("footer").classes(
        "sticky bottom-0 z-10 w-full border-t border-slate-200/80 bg-white/95 p-3 sm:p-4 backdrop-blur-xl shrink-0"
    ):
        with ui.column().classes("w-full max-w-4xl mx-auto gap-1.5 items-center"):
            # Text area + send button wrapper
            with ui.card().classes(
                "w-full rounded-2xl p-1.5 border border-slate-200 focus-within:border-blue-500 shadow-sm bg-slate-50 flex-row items-center transition-colors"
            ):
                async def trigger_submit() -> None:
                    text = query_input.value.strip()
                    if not text or state.is_analyzing:
                        return
                    query_input.value = ""
                    await on_submit(text)

                query_input = (
                    ui.input(placeholder="Ask anything about your data… (e.g. 'Show monthly revenue trend')")
                    .props("borderless dense autogrow")
                    .classes("flex-1 text-sm text-slate-900 px-3 py-1")
                )
                query_input.on("keydown.enter.prevent", trigger_submit)

                with ui.button(on_click=trigger_submit).props("round flat").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:scale-105 transition-transform"
                ):
                    ui.icon("arrow_upward", size="18px")

            ui.label("DataAgent Pro can make mistakes. Always verify critical decisions.").classes(
                "text-[10px] text-slate-400 text-center"
            )
