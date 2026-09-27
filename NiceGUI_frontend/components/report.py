"""
DataPilot — Full Report Component
======================================
Renders complete, multi-section analysis reports including Executive Summary,
Interactive Tables, Plotly Charts, Insights, Recommendations, SQL/Python viewer,
Debug panel, and Action bar in clean light styling.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any
from nicegui import ui

from config import BACKEND_URL
from state.app_state import ChatMessage, ReportSection, DebugInfo
from components.tables import render_table_card
from components.charts import render_chart_card

INSIGHT_ICONS = ["lightbulb", "trending_up", "warning", "public", "bolt"]


def render_executive_summary(report: ReportSection) -> None:
    """Render the executive summary with confidence badge and headline."""
    summary = report.executive_summary
    confidence = summary.confidence or "High"

    with ui.card().classes(
        "w-full rounded-3xl p-6 sm:p-8 bg-white border border-slate-200/80 shadow-sm relative overflow-hidden"
    ):
        # Top badges
        with ui.row().classes("items-center gap-2 mb-4"):
            with ui.row().classes(
                "items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-blue-700"
            ):
                ui.icon("auto_awesome", size="12px")
                ui.label("Executive Summary")

            is_high = confidence.lower() == "high"
            badge_color = "emerald" if is_high else "amber"
            with ui.row().classes(
                f"items-center gap-1.5 rounded-full border border-{badge_color}-200 bg-{badge_color}-50 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-{badge_color}-700"
            ):
                ui.icon("verified_user", size="12px")
                ui.label(f"{confidence} confidence")

        # Headline
        ui.label(summary.headline).classes(
            "text-2xl font-bold leading-tight tracking-tight sm:text-3xl text-slate-900 mb-4"
        )

        # Body paragraphs
        with ui.column().classes("gap-3 text-sm leading-relaxed text-slate-600 font-normal max-w-3xl"):
            for para in summary.summary.split("\n"):
                clean = para.strip()
                if clean:
                    ui.label(clean)


def render_insights(report: ReportSection) -> None:
    """Render 2-column key insights cards with light hover effects."""
    insights = report.insights
    if not insights:
        return

    with ui.card().classes("w-full rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm"):
        with ui.row().classes("items-center gap-2 mb-3"):
            ui.icon("insights", size="18px").classes("text-blue-600")
            ui.label("Key Insights").classes("text-sm font-bold text-slate-800")

        with ui.grid().classes("grid grid-cols-1 sm:grid-cols-2 gap-3 w-full"):
            for idx, item in enumerate(insights):
                icon_name = INSIGHT_ICONS[idx % len(INSIGHT_ICONS)]
                with ui.element("div").classes(
                    "rounded-xl border border-slate-200/80 bg-slate-50/50 p-4 hover:border-blue-300 hover:bg-blue-50/20 transition-all duration-200"
                ):
                    with ui.row().classes("items-center gap-2 mb-2"):
                        with ui.element("div").classes(
                            "h-7 w-7 grid place-items-center rounded-lg bg-blue-100/80 text-blue-600"
                        ):
                            ui.icon(icon_name, size="16px")
                        ui.label(item.title).classes("text-sm font-semibold text-slate-900")
                    ui.label(item.body).classes("text-xs text-slate-500 leading-relaxed")


def render_recommendations(report: ReportSection) -> None:
    """Render actionable recommendations with green emphasis."""
    recs = report.recommendations
    if not recs:
        return

    with ui.card().classes("w-full rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm"):
        with ui.row().classes("items-center gap-2 mb-3"):
            ui.icon("check_circle", size="18px").classes("text-emerald-500")
            ui.label("Recommended Actions").classes("text-sm font-bold text-slate-800")

        with ui.column().classes("w-full gap-2.5"):
            for item in recs:
                with ui.row().classes(
                    "w-full items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50/40 p-4 hover:border-emerald-300 hover:bg-emerald-50/70 transition-all duration-200"
                ):
                    with ui.element("div").classes(
                        "h-7 w-7 grid place-items-center rounded-lg bg-emerald-100 text-emerald-600 shrink-0 mt-0.5"
                    ):
                        ui.icon("task_alt", size="16px")
                    with ui.column().classes("flex-1 min-w-0 gap-1"):
                        ui.label(item.title).classes("text-sm font-semibold text-slate-900")
                        ui.label(item.body).classes("text-xs text-slate-600 leading-relaxed")
                    ui.icon("arrow_forward", size="16px").classes("text-emerald-500 shrink-0 mt-1")


def render_code_viewer(debug: DebugInfo | None) -> None:
    """Render collapsible executed SQL or Python code viewer."""
    if not debug or not debug.generated_code:
        return

    is_python = debug.execution_mode == "PYTHON"
    title = "Executed Python Code" if is_python else "Executed SQL Query"
    filename = "script.py" if is_python else "query.sql"
    code = debug.generated_code

    with ui.expansion(title, icon="terminal").classes(
        "w-full rounded-2xl border border-slate-200/80 bg-white shadow-sm text-slate-800"
    ):
        with ui.row().classes("w-full items-center justify-between pb-2 border-b border-slate-100"):
            ui.label(filename).classes("text-xs font-mono text-slate-400")

            def copy_code() -> None:
                ui.run_javascript(f"navigator.clipboard.writeText({json.dumps(code)})")
                ui.notify("Code copied to clipboard", type="positive", position="bottom-right")

            ui.button("Copy", on_click=copy_code).props("dense outline").classes(
                "text-[11px] rounded px-2 text-slate-600 hover:text-slate-900 border-slate-300"
            )

        with ui.element("pre").classes(
            "w-full overflow-x-auto p-3 text-xs font-mono text-slate-100 bg-slate-900 rounded-lg mt-2 leading-relaxed"
        ):
            ui.label(code)


def render_debug_panel(debug: DebugInfo | None) -> None:
    """Render collapsible debug reasoning and execution plan."""
    if not debug:
        return

    has_content = bool(debug.llm_reasoning or debug.execution_plan)
    if not has_content:
        return

    with ui.expansion("Debug Information & Reasoning", icon="bug_report").classes(
        "w-full rounded-2xl border border-slate-200/80 bg-white shadow-sm text-slate-800"
    ):
        with ui.column().classes("w-full gap-3 pt-2"):
            if debug.llm_reasoning:
                with ui.element("div").classes("w-full rounded-xl border border-slate-200/80 bg-slate-50 p-3.5"):
                    ui.label("AGENT REASONING").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1")
                    ui.label(debug.llm_reasoning).classes("text-xs text-slate-700 leading-relaxed")

            if debug.execution_plan:
                with ui.element("div").classes("w-full rounded-xl border border-slate-200/80 bg-slate-50 p-3.5"):
                    ui.label("EXECUTION PLAN").classes("text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1")
                    ui.label(debug.execution_plan).classes("text-xs text-slate-700 font-mono leading-relaxed")


def render_report_actions(msg: ChatMessage) -> None:
    """Render per-report action buttons: PDF, CSV, Copy Markdown."""
    report = msg.report
    if not report:
        return

    has_table = bool(report.tables)
    execution_id = msg.execution_id

    # PDF Action
    def handle_pdf() -> None:
        if execution_id:
            # Backend generated PDF
            pdf_url = f"{BACKEND_URL}/report/{execution_id}/pdf"
            ui.run_javascript(f"window.open('{pdf_url}', '_blank')")
        else:
            ui.run_javascript("window.print()")

    # CSV Action
    def handle_csv() -> None:
        if not has_table:
            return
        tbl = report.tables[0]
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(tbl.columns)
        for r in tbl.rows:
            writer.writerow([str(c) if c is not None else "" for c in r])
        csv_bytes = buf.getvalue().encode("utf-8")
        clean_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in report.title)
        ui.download(csv_bytes, f"{clean_title or 'data'}.csv")
        ui.notify("CSV downloaded", type="positive", position="bottom-right")

    # Copy Markdown Action
    def handle_copy_md() -> None:
        lines = [f"# {report.title}", ""]
        if report.executive_summary:
            lines.extend([
                "## Summary",
                report.executive_summary.headline,
                report.executive_summary.summary,
                "",
            ])
        if report.insights:
            lines.append("## Key Insights")
            for i in report.insights:
                lines.append(f"- **{i.title}**: {i.body}")
            lines.append("")
        if report.recommendations:
            lines.append("## Recommendations")
            for r in report.recommendations:
                lines.append(f"- **{r.title}**: {r.body}")
            lines.append("")
        if msg.debug and msg.debug.generated_code:
            lang = "python" if msg.debug.execution_mode == "PYTHON" else "sql"
            lines.extend([f"## Executed Code ({lang})", f"```{lang}", msg.debug.generated_code, "```"])

        full_md = "\n".join(lines)
        ui.run_javascript(f"navigator.clipboard.writeText({json.dumps(full_md)})")
        ui.notify("Report copied as Markdown", type="positive", position="bottom-right")

    with ui.row().classes("w-full items-center gap-2 pt-2 flex-wrap"):
        with ui.button(on_click=handle_pdf).props("dense outline").classes(
            "rounded-lg px-3 py-1.5 text-xs text-slate-700 hover:text-slate-900 border-slate-300 bg-white hover:bg-slate-50 shadow-sm"
        ):
            with ui.row().classes("items-center gap-1.5"):
                ui.icon("picture_as_pdf", size="14px").classes("text-blue-600")
                ui.label("PDF Report")

        if has_table:
            with ui.button(on_click=handle_csv).props("dense outline").classes(
                "rounded-lg px-3 py-1.5 text-xs text-slate-700 hover:text-slate-900 border-slate-300 bg-white hover:bg-slate-50 shadow-sm"
            ):
                with ui.row().classes("items-center gap-1.5"):
                    ui.icon("download", size="14px").classes("text-blue-600")
                    ui.label("Download CSV")

        with ui.button(on_click=handle_copy_md).props("dense outline").classes(
            "rounded-lg px-3 py-1.5 text-xs text-slate-700 hover:text-slate-900 border-slate-300 bg-white hover:bg-slate-50 shadow-sm"
        ):
            with ui.row().classes("items-center gap-1.5"):
                ui.icon("content_copy", size="14px").classes("text-blue-600")
                ui.label("Copy Markdown")


def render_report(msg: ChatMessage) -> None:
    """Orchestrate and render all sections of an analysis report."""
    report = msg.report
    if not report:
        return

    with ui.column().classes("w-full gap-5 animate-fade-in"):
        # 1. Executive Summary
        render_executive_summary(report)

        # 2. Data Tables
        for table in report.tables:
            render_table_card(table)

        # 3. Plotly Charts
        if report.charts:
            with ui.grid().classes(
                f"w-full gap-4 {'grid-cols-1' if len(report.charts) == 1 else 'grid-cols-1 lg:grid-cols-2'}"
            ):
                for chart in report.charts:
                    render_chart_card(chart)

        # 4. Insights
        render_insights(report)

        # 5. Recommendations
        render_recommendations(report)

        # 6. SQL / Python viewer
        render_code_viewer(msg.debug)

        # 7. Debug Panel
        render_debug_panel(msg.debug)

        # 8. Action Bar
        render_report_actions(msg)
