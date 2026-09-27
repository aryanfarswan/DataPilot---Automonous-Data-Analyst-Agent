from __future__ import annotations

import logging
from typing import Any
import plotly.graph_objects as go
from nicegui import ui

from api.client import api
from state.app_state import AppState
from components.charts import apply_theme_to_layout

logger = logging.getLogger(__name__)


def compute_metrics_summary(metric_days: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregated analytics metrics matching analytics.ts."""
    total = sum(m.get("total_executions", 0) for m in metric_days)
    first_try = sum(m.get("first_try_success_count", 0) for m in metric_days)
    retry_succ = sum(m.get("retry_success_count", 0) for m in metric_days)
    failed = sum(m.get("failed_count", 0) for m in metric_days)

    succ_total = first_try + retry_succ
    success_rate = (succ_total / total * 100.0) if total > 0 else 0.0
    first_try_rate = (first_try / total * 100.0) if total > 0 else 0.0
    recovery_rate = (retry_succ / succ_total * 100.0) if succ_total > 0 else 0.0

    failure_aggs: dict[str, int] = {}
    for m in metric_days:
        types = m.get("common_failure_types") or {}
        if isinstance(types, dict):
            for k, v in types.items():
                failure_aggs[k] = failure_aggs.get(k, 0) + int(v)

    return {
        "total": total,
        "first_try": first_try,
        "retry_success": retry_succ,
        "failed": failed,
        "success_rate": success_rate,
        "first_try_rate": first_try_rate,
        "recovery_rate": recovery_rate,
        "failure_aggregates": failure_aggs,
    }


def render_kpi_card(icon_name: str, label: str, value: str, delta: str, positive: bool = True) -> None:
    """Render a single KPI summary card."""
    with ui.card().classes("rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm flex-col justify-between"):
        with ui.row().classes("w-full items-center justify-between mb-3"):
            ui.label(label).classes("text-xs font-bold text-slate-400 uppercase tracking-wider")
            with ui.element("div").classes("h-8 w-8 grid place-items-center rounded-lg bg-blue-50 text-blue-600"):
                ui.icon(icon_name, size="18px")
        ui.label(value).classes("text-2xl font-bold text-slate-900 tracking-tight")
        ui.label(delta).classes(
            f"text-[11px] font-medium mt-1.5 {'text-emerald-600' if positive else 'text-rose-500'}"
        )


def render_analytics_page(state: AppState) -> None:
    """Render the full analytics dashboard."""
    container = ui.column().classes("w-full flex-1 overflow-y-auto px-4 sm:px-8 py-6 gap-6 max-w-6xl mx-auto")

    async def load_and_render() -> None:
        container.clear()
        with container:
            with ui.row().classes("w-full items-center justify-center py-12"):
                ui.spinner("dots", size="lg", color="blue")
                ui.label("Fetching workspace analytics...").classes("text-sm text-slate-400 ml-3")

        try:
            metrics_data = await api.get_metrics()
            metric_days = metrics_data if isinstance(metrics_data, list) else metrics_data.get("metrics", [])
        except Exception as e:
            logger.error("Failed to load metrics: %s", e)
            metric_days = []

        summary = compute_metrics_summary(metric_days)

        container.clear()
        with container:
            # 1. Page Header
            with ui.row().classes("w-full items-center justify-between pb-4 border-b border-slate-200/80"):
                with ui.column().classes("gap-1"):
                    ui.label("WORKSPACE").classes("text-[10px] font-bold uppercase tracking-widest text-blue-600")
                    with ui.row().classes("items-center gap-3"):
                        ui.label("Analytics").classes("text-2xl font-bold text-slate-900")
                        with ui.button(on_click=load_and_render).props("flat dense round").classes("text-slate-500 hover:text-slate-900"):
                            ui.icon("refresh", size="18px")
                with ui.element("div").classes(
                    "items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 hidden sm:flex"
                ):
                    ui.icon("auto_awesome", size="14px").classes("text-blue-600")
                    ui.label("Last 30 days")

            # Description
            with ui.column().classes("gap-1"):
                ui.label("A live pulse of query volume, latency, and success rates across your DataPilot workspace.").classes(
                    "text-xs text-slate-500"
                )

            # 2. KPI Cards
            with ui.grid().classes("grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 w-full"):
                render_kpi_card("analytics", "Total Queries", f"{summary['total']:,}", "Lifetime", positive=True)
                render_kpi_card("trending_up", "Success Rate", f"{summary['success_rate']:.1f}%", "First Try + Retries", positive=summary['success_rate'] >= 80)
                render_kpi_card("bolt", "First-Try Rate", f"{summary['first_try_rate']:.1f}%", "Zero retries", positive=summary['first_try_rate'] >= 70)
                render_kpi_card("warning", "Failed Queries", f"{summary['failed']:,}", "Unrecoverable", positive=summary['failed'] == 0)

            # 3. Execution Stats Section
            with ui.card().classes("w-full rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm"):
                ui.label("Execution Stats").classes("text-sm font-bold text-slate-900 mb-1")
                ui.label("Aggregated performance breakdown.").classes("text-xs text-slate-500 mb-4")

                with ui.grid().classes("grid grid-cols-2 sm:grid-cols-4 gap-3 w-full text-center"):
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50 border border-slate-200/60"):
                        ui.label("Total Recovered").classes("text-[10px] text-slate-400 uppercase tracking-wider")
                        ui.label(f"{summary['retry_success']}").classes("text-sm font-bold text-slate-800 mt-1")
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50 border border-slate-200/60"):
                        ui.label("Recovery Rate").classes("text-[10px] text-slate-400 uppercase tracking-wider")
                        ui.label(f"{summary['recovery_rate']:.1f}%").classes("text-sm font-bold text-slate-800 mt-1")
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50 border border-slate-200/60"):
                        ui.label("First Try Success").classes("text-[10px] text-slate-400 uppercase tracking-wider")
                        ui.label(f"{summary['first_try']}").classes("text-sm font-bold text-slate-800 mt-1")
                    with ui.element("div").classes("p-3 rounded-xl bg-slate-50 border border-slate-200/60"):
                        ui.label("Unrecoverable").classes("text-[10px] text-slate-400 uppercase tracking-wider")
                        ui.label(f"{summary['failed']}").classes("text-sm font-bold text-slate-800 mt-1")

            # 4. Analytics Visualizations (Plotly charts)
            if metric_days:
                sorted_days = sorted(metric_days, key=lambda x: str(x.get("execution_date", "")))
                dates = [str(d.get("execution_date", ""))[:10] for d in sorted_days]
                totals = [d.get("total_executions", 0) for d in sorted_days]
                successes = [d.get("first_try_success_count", 0) + d.get("retry_success_count", 0) for d in sorted_days]
                fails = [d.get("failed_count", 0) for d in sorted_days]

                with ui.grid().classes("grid grid-cols-1 lg:grid-cols-2 gap-4 w-full"):
                    # Volume Area Chart
                    with ui.card().classes("w-full rounded-2xl p-4 border border-slate-200/80 bg-white shadow-sm"):
                        ui.label("Query Volume").classes("text-sm font-bold text-slate-900 mb-2")
                        fig_vol = go.Figure()
                        fig_vol.add_trace(go.Scatter(
                            x=dates, y=totals, fill="tozeroy",
                            line=dict(color="#2563eb", width=2),
                            fillcolor="rgba(37, 99, 235, 0.12)",
                            name="Queries",
                        ))
                        apply_theme_to_layout(fig_vol.layout, is_dark=state.is_dark)
                        ui.plotly(fig_vol).classes("w-full h-64")

                    # Success vs Failure Line Chart
                    with ui.card().classes("w-full rounded-2xl p-4 border border-slate-200/80 bg-white shadow-sm"):
                        ui.label("Success vs Failure Trend").classes("text-sm font-bold text-slate-900 mb-2")
                        fig_trend = go.Figure()
                        fig_trend.add_trace(go.Scatter(
                            x=dates, y=successes, mode="lines+markers",
                            line=dict(color="#10b981", width=2),
                            name="Success",
                        ))
                        fig_trend.add_trace(go.Scatter(
                            x=dates, y=fails, mode="lines+markers",
                            line=dict(color="#ef4444", width=2),
                            name="Failed",
                        ))
                        apply_theme_to_layout(fig_trend.layout, is_dark=state.is_dark)
                        ui.plotly(fig_trend).classes("w-full h-64")

            # 5. Recent Execution Logs (from current session history)
            if state.session_queries:
                with ui.card().classes("w-full rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm"):
                    ui.label("Recent Execution Logs").classes("text-sm font-bold text-slate-900 mb-3")
                    log_cols = [
                        {"name": "id", "label": "ID", "field": "id", "align": "center"},
                        {"name": "question", "label": "Question", "field": "question", "align": "left"},
                        {"name": "status", "label": "Status", "field": "status", "align": "center"},
                        {"name": "latency", "label": "Latency", "field": "latency", "align": "right"},
                        {"name": "time", "label": "Time", "field": "time", "align": "right"},
                    ]
                    log_rows = [
                        {
                            "id": f"#{q.get('id', '')}",
                            "question": q.get("question", ""),
                            "status": "Succeeded" if q.get("success") else "Failed",
                            "latency": f"{q.get('execution_time_ms', 0):.0f}ms",
                            "time": str(q.get("created_at", ""))[-8:-3] if q.get("created_at") else "--",
                        }
                        for q in reversed(state.session_queries[-10:])
                    ]
                    ui.table(columns=log_cols, rows=log_rows, pagination={"rowsPerPage": 5}).props(
                        "flat dense bordered"
                    ).classes("w-full bg-transparent text-xs")

    ui.timer(0.01, load_and_render, once=True)
