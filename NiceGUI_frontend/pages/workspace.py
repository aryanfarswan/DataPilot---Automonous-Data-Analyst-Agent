from __future__ import annotations

import asyncio
import logging
import time
from typing import Any
from nicegui import events, ui

from api.client import api
from state.app_state import (
    AppState,
    Column,
    UploadResponse,
    ReportSection,
    ExecutiveSummary,
    TableResult,
    ChartSpec,
    Insight,
    Recommendation,
    DebugInfo,
    ChatMessage,
)
from components.header import render_header
from components.left_sidebar import render_left_sidebar
from components.right_sidebar import render_right_sidebar
from components.upload import render_upload_hero
from components.chat import render_chat_feed, render_chat_composer
from pages.metrics import render_analytics_page

logger = logging.getLogger(__name__)


def parse_report_payload(raw_report: dict[str, Any]) -> ReportSection:
    """Safely convert backend JSON report dict into typed ReportSection model."""
    exec_data = raw_report.get("executive_summary") or {}
    exec_summary = ExecutiveSummary(
        headline=exec_data.get("headline", "Executive Summary"),
        summary=exec_data.get("summary", ""),
        confidence=exec_data.get("confidence", "Medium"),
    )

    tables = []
    for t in raw_report.get("tables", []):
        tables.append(
            TableResult(
                title=t.get("title", "Results Table"),
                columns=t.get("columns", []),
                rows=t.get("rows", []),
            )
        )

    charts = []
    for c in raw_report.get("charts", []):
        charts.append(
            ChartSpec(
                title=c.get("title", "Chart"),
                type=c.get("type", "other"),
                plotly_json=c.get("plotly_json"),
            )
        )

    insights = []
    for i in raw_report.get("insights", []):
        insights.append(
            Insight(
                title=i.get("title", "Insight"),
                body=i.get("body", ""),
            )
        )

    recommendations = []
    for r in raw_report.get("recommendations", []):
        recommendations.append(
            Recommendation(
                title=r.get("title", "Action"),
                body=r.get("body", ""),
            )
        )

    return ReportSection(
        title=raw_report.get("title", "Data Analysis"),
        executive_summary=exec_summary,
        tables=tables,
        charts=charts,
        insights=insights,
        recommendations=recommendations,
        report_type=raw_report.get("report_type"),
    )


def create_workspace_view(state: AppState) -> None:
    """Build and wire the complete NiceGUI Workspace."""
    uploader_ref: list[ui.upload] = []

    # ── Left Drawer ──────────────────────────────────────────────
    left_drawer = ui.left_drawer(value=True).classes(
        "bg-[#f4f6fb] p-2 sm:p-3 overflow-hidden w-76 sm:w-80 border-none"
    )

    # ── Right Drawer ─────────────────────────────────────────────
    right_drawer = ui.right_drawer(value=True).classes(
        "bg-[#f4f6fb] p-2 sm:p-3 overflow-hidden w-80 sm:w-88 border-none"
    )

    # ── Actions ──────────────────────────────────────────────────
    async def handle_upload(filename: str, content: bytes) -> None:
        state.is_uploading = True
        state.upload_error = None
        state.notify_change()

        try:
            raw_data = await api.upload_csv(filename, content)
            cols = [
                Column(name=c.get("name", ""), dtype=c.get("dtype", ""))
                for c in raw_data.get("columns", [])
            ]
            upload_resp = UploadResponse(
                session_id=raw_data.get("session_id", ""),
                dataset_id=raw_data.get("dataset_id", filename),
                row_count=raw_data.get("row_count", 0),
                columns=cols,
            )
            state.reset_on_upload(upload_resp)
            # Ensure right sidebar is open and workspace tab is active
            state.active_tab = "analysis"
            right_drawer.value = True
            ui.notify(
                f"Dataset loaded — {upload_resp.row_count:,} rows",
                type="positive",
                position="bottom-right",
            )
        except Exception as e:
            state.upload_error = str(e)
            ui.notify(f"Upload failed: {e}", type="negative", position="bottom-right")
        finally:
            state.is_uploading = False
            state.notify_change()

    def trigger_new_analysis() -> None:
        state.reset_to_start_workspace()
        ui.notify("Redirected to start workspace", type="info", position="bottom-right")

    def handle_keyboard(e: events.KeyEventArguments) -> None:
        if e.key and e.key.lower() == "k" and (e.modifiers.ctrl or e.modifiers.meta) and e.action.keydown:
            trigger_new_analysis()

    ui.keyboard(on_key=handle_keyboard)

    def select_history_report(history_row: dict[str, Any]) -> None:
        state.selected_history_id = str(history_row.get("id"))
        q = history_row.get("question", "")
        summary = history_row.get("narrative_summary", "")
        succ = history_row.get("success", True)
        chart_json = history_row.get("chart_plotly_json")

        charts = [ChartSpec(title="Chart", type="other", plotly_json=chart_json)] if chart_json else []
        hist_report = ReportSection(
            title=q,
            executive_summary=ExecutiveSummary(
                headline=q,
                summary=summary,
                confidence="High" if succ else "Low",
            ),
            tables=[],
            charts=charts,
            insights=[],
            recommendations=[],
        )

        state.chat_history = [
            ChatMessage(id="usr-hist", role="user", content=q),
            ChatMessage(
                id="ast-hist",
                role="assistant",
                report=hist_report,
                success=succ,
                execution_id=history_row.get("id"),
                execution_time=history_row.get("execution_time_ms"),
                retry_count=0,
            ),
        ]
        state.active_tab = "analysis"
        state.notify_change()

    async def handle_analyze_query(user_question: str) -> None:
        if not state.session or not user_question.strip() or state.is_analyzing:
            return

        session_id = state.session.session_id
        start_time = time.time()
        state.is_analyzing = True
        state.trace_history = []
        right_drawer.value = True

        # Optimistic user message bubble
        state.chat_history.append(
            ChatMessage(id=str(time.time()), role="user", content=user_question)
        )
        state.notify_change()

        # Background trace polling task
        stop_polling = asyncio.Event()

        async def poll_trace_loop() -> None:
            while not stop_polling.is_set():
                try:
                    trace_data = await api.get_trace(session_id)
                    if trace_data:
                        state.trace_history = trace_data
                        refresh_right_sidebar()
                except Exception:
                    pass
                await asyncio.sleep(1.2)

        poll_task = asyncio.create_task(poll_trace_loop())

        try:
            data = await api.analyze(session_id, user_question)
            duration_ms = int((time.time() - start_time) * 1000)

            # Stop polling & fetch final trace
            stop_polling.set()
            await poll_task
            state.trace_history = await api.get_trace(session_id)

            report_obj = parse_report_payload(data.get("report") or {})
            raw_debug = data.get("debug") or {}
            debug_obj = DebugInfo(
                generated_code=raw_debug.get("generated_code"),
                execution_mode=raw_debug.get("execution_mode"),
                execution_plan=raw_debug.get("execution_plan"),
                llm_reasoning=raw_debug.get("llm_reasoning"),
            )

            q_info = data.get("query") or {}
            asst_msg = ChatMessage(
                id=str(time.time()),
                role="assistant",
                report=report_obj,
                debug=debug_obj,
                success=data.get("success", True),
                execution_id=q_info.get("execution_id"),
                execution_time=duration_ms,
                retry_count=q_info.get("retry_count", 0),
                model=q_info.get("model"),
                provider=q_info.get("provider"),
            )
            state.chat_history.append(asst_msg)

            # Refresh history queries
            hist = await api.get_history(session_id)
            state.session_queries = hist

        except Exception as e:
            logger.error("Analysis failed: %s", e)
            stop_polling.set()
            try:
                await poll_task
            except Exception:
                pass

            err_report = ReportSection(
                title="Analysis Error",
                executive_summary=ExecutiveSummary(
                    headline="An error occurred while running the analysis.",
                    summary=str(e),
                    confidence="Low",
                ),
            )
            state.chat_history.append(
                ChatMessage(
                    id=str(time.time()),
                    role="assistant",
                    report=err_report,
                    success=False,
                )
            )
        finally:
            state.is_analyzing = False
            state.notify_change()

    # ── Refreshable Views ────────────────────────────────────────

    @ui.refreshable
    def refresh_header() -> None:
        render_header(
            state,
            on_toggle_left_sidebar=lambda: left_drawer.toggle(),
            on_toggle_right_sidebar=lambda: right_drawer.toggle(),
        )

    @ui.refreshable
    def refresh_left_sidebar() -> None:
        render_left_sidebar(
            state,
            on_new_analysis=trigger_new_analysis,
            on_select_history=select_history_report,
            on_toggle_collapse=lambda: left_drawer.toggle(),
            on_switch_tab=lambda tab: setattr(state, "active_tab", tab) or state.notify_change(),
        )

    @ui.refreshable
    def refresh_right_sidebar() -> None:
        render_right_sidebar(
            state,
            on_toggle_collapse=lambda: right_drawer.toggle(),
        )

    @ui.refreshable
    def refresh_main_content() -> None:
        if state.active_tab == "metrics":
            render_analytics_page(state)
        elif not state.has_dataset:
            uploader = render_upload_hero(
                handle_upload,
                is_uploading=state.is_uploading,
                error_message=state.upload_error,
                on_error=lambda err: setattr(state, "upload_error", err) or state.notify_change(),
            )
            uploader_ref.clear()
            if uploader is not None:
                uploader_ref.append(uploader)
        else:
            with ui.column().classes("w-full flex-1 overflow-y-auto min-h-0"):
                render_chat_feed(state)
            render_chat_composer(state, handle_analyze_query)

    # Mount drawers content
    with left_drawer:
        refresh_left_sidebar()

    with right_drawer:
        refresh_right_sidebar()

    # Mount main body container
    with ui.column().classes("w-full h-screen overflow-hidden flex-col bg-[#f4f6fb] text-slate-900 flex-1 p-2 sm:p-3 m-0 relative"):
        # Central white card
        with ui.column().classes("w-full h-full bg-white rounded-2xl border border-slate-200/80 shadow-sm flex flex-col overflow-hidden relative"):
            refresh_header()

            # Floating Left Sidebar Re-open button (visible when left drawer is closed)
            with ui.button(on_click=lambda: left_drawer.toggle()).props("flat dense").classes(
                "fixed left-3 top-1/2 -translate-y-1/2 z-30 h-10 w-6 p-0 rounded-r-lg bg-white text-slate-600 hover:text-slate-900 border border-l-0 border-slate-200 shadow-md items-center justify-center flex"
            ):
                ui.icon("chevron_right", size="18px")

            # Central view
            with ui.column().classes("w-full flex-1 min-h-0 overflow-hidden p-0 relative"):
                refresh_main_content()

    # Register reactive refresh listener
    def on_state_updated() -> None:
        refresh_header.refresh()
        refresh_left_sidebar.refresh()
        refresh_right_sidebar.refresh()
        refresh_main_content.refresh()

    state.on_change(on_state_updated)

