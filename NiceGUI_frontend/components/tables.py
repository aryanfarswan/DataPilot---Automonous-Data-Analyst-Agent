"""
DataPilot — Interactive Data Table Component
=================================================
Renders interactive, paginated, searchable data tables with smart value
formatting (currencies, percentages, integers) and CSV export matching
the clean light theme design.
"""

from __future__ import annotations

import csv
import io
import math
from typing import Any
from nicegui import ui

from state.app_state import TableResult


def format_table_cell(value: Any, col_name: str, table_title: str = "") -> tuple[str, str]:
    """
    Format a value based on column name and table context.
    Returns (formatted_str, alignment: 'left' | 'center' | 'right').
    """
    if value is None:
        return ("—", "left")

    str_val = str(value).strip()
    if str_val == "":
        return ("", "left")

    try:
        num = float(str_val)
    except (ValueError, TypeError):
        return (str_val, "left")

    col_lower = col_name.lower()
    title_lower = table_title.lower()

    if "correlation" in title_lower:
        return (f"{num:.5f}", "right")

    if any(k in col_lower for k in ("id", "year", "month", "day", "date")):
        return (str_val, "center")

    currency_keys = ("price", "revenue", "sales", "amount", "cost", "fee", "profit", "value")
    if any(k in col_lower for k in currency_keys):
        return (f"${num:,.2f}", "right")

    pct_keys = ("pct", "percent", "margin", "rate", "share")
    if any(k in col_lower for k in pct_keys):
        pct_val = num if num > 1.0 else num * 100.0
        return (f"{pct_val:.1f}%", "right")

    if num.is_integer():
        return (f"{int(num):,}", "right")

    return (f"{num:,.2f}", "right")


def render_table_card(table: TableResult | dict[str, Any]) -> None:
    """Render a styled data table with search, sorting, pagination, and CSV download."""
    title = table.title if isinstance(table, TableResult) else table.get("title", "Results Table")
    columns = table.columns if isinstance(table, TableResult) else table.get("columns", [])
    rows = table.rows if isinstance(table, TableResult) else table.get("rows", [])

    if not columns or not rows:
        return

    # Infer alignment for each column from first non-null row
    alignments = {}
    for col_idx, col_name in enumerate(columns):
        col_align = "left"
        for r in rows:
            if col_idx < len(r) and r[col_idx] is not None and str(r[col_idx]).strip() != "":
                _, col_align = format_table_cell(r[col_idx], col_name, title)
                break
        alignments[col_name] = col_align

    # Prepare Quasar table columns definition
    table_columns = [
        {
            "name": col_name,
            "label": col_name,
            "field": col_name,
            "align": alignments[col_name],
            "sortable": True,
        }
        for col_name in columns
    ]

    # Prepare formatted table rows
    formatted_rows = []
    for row_idx, r in enumerate(rows):
        row_dict: dict[str, Any] = {"_id": row_idx}
        for col_idx, col_name in enumerate(columns):
            raw_val = r[col_idx] if col_idx < len(r) else None
            formatted_val, _ = format_table_cell(raw_val, col_name, title)
            row_dict[col_name] = formatted_val
        formatted_rows.append(row_dict)

    # Function to export CSV
    def export_csv() -> None:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(columns)
        for r in rows:
            writer.writerow([str(c) if c is not None else "" for c in r])
        csv_bytes = buf.getvalue().encode("utf-8")
        clean_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title)
        ui.download(csv_bytes, f"{clean_title or 'data'}.csv")
        ui.notify("CSV downloaded", type="positive", position="bottom-right")

    with ui.card().classes("w-full rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm"):
        # Header with title and controls
        with ui.row().classes("w-full items-center justify-between gap-3 pb-3 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("table_chart", size="18px").classes("text-blue-600")
                ui.label(title).classes("text-sm font-bold text-slate-800")
                ui.label(f"({len(rows):,} rows)").classes("text-xs text-slate-400")

            with ui.row().classes("items-center gap-2"):
                # Search input
                search_input = (
                    ui.input(placeholder="Search table…")
                    .props("dense outlined rounded")
                    .classes("text-xs w-48")
                )
                search_input.add_slot(
                    "prepend",
                    '<q-icon name="search" size="16px" class="text-slate-400" />',
                )

                # Export CSV button
                with ui.button(on_click=export_csv).props("dense outline").classes(
                    "rounded-lg px-2.5 py-1 text-xs text-slate-700 hover:text-slate-900 border-slate-300 bg-white hover:bg-slate-50 shadow-sm"
                ):
                    with ui.row().classes("items-center gap-1.5 no-wrap"):
                        ui.icon("download", size="14px").classes("text-blue-600")
                        ui.label("CSV")

        # Quasar Table
        qtable = ui.table(
            columns=table_columns,
            rows=formatted_rows,
            pagination={"rowsPerPage": 10},
        ).classes("w-full bg-transparent text-xs")
        qtable.props("flat bordered dense")

        # Connect search filter to table
        search_input.bind_value_to(qtable, "filter")
