from __future__ import annotations

import json
import logging
from typing import Any
import plotly.graph_objects as go
from nicegui import ui

from state.app_state import ChartSpec

logger = logging.getLogger(__name__)


def apply_theme_to_layout(layout: dict[str, Any], is_dark: bool = False) -> dict[str, Any]:
    """Apply consistent styling to Plotly layout."""
    layout = dict(layout)
    text_color = "#f4f4f5" if is_dark else "#0f172a"
    grid_color = "rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.06)"

    layout["paper_bgcolor"] = "rgba(0,0,0,0)"
    layout["plot_bgcolor"] = "rgba(0,0,0,0)"
    layout["font"] = {
        "family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        "color": text_color,
        "size": 11,
    }
    layout["margin"] = dict(t=40, r=20, l=50, b=40)

    # Configure axes styling
    for axis_name in ("xaxis", "yaxis"):
        axis = dict(layout.get(axis_name, {}))
        axis["gridcolor"] = grid_color
        axis["linecolor"] = grid_color
        axis["zerolinecolor"] = grid_color
        axis["tickfont"] = {"color": text_color, "size": 10}
        layout[axis_name] = axis

    return layout


def render_chart_card(chart: ChartSpec | dict[str, Any], is_dark: bool = False) -> None:
    """Render a single chart inside a stylized card container."""
    title = chart.title if isinstance(chart, ChartSpec) else chart.get("title", "Visualization")
    raw_data = chart.plotly_json if isinstance(chart, ChartSpec) else chart.get("plotly_json")

    with ui.card().classes("w-full rounded-2xl p-5 border border-slate-200/80 bg-white shadow-sm"):
        with ui.row().classes("w-full items-center justify-between pb-2 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("bar_chart", size="18px").classes("text-blue-600")
                ui.label(title).classes("text-sm font-bold text-slate-800")

        if not raw_data:
            ui.label("No chart data available").classes("text-xs text-slate-400 py-8 text-center w-full")
            return

        try:
            chart_dict = raw_data
            if isinstance(raw_data, str):
                chart_dict = json.loads(raw_data)

            if isinstance(chart_dict, dict):
                data = chart_dict.get("data", [])
                layout = apply_theme_to_layout(chart_dict.get("layout", {}), is_dark=is_dark)
                fig = go.Figure(data=data, layout=layout)
                chart_ui = ui.plotly(fig).classes("w-full h-[420px] rounded-xl overflow-hidden")
                chart_ui.props('config="{responsive: true, displayModeBar: false}"')
            else:
                ui.label("Unsupported chart format").classes("text-xs text-slate-400 py-4")
        except Exception as e:
            logger.error("Failed to render Plotly chart: %s", e)
            with ui.row().classes("items-center gap-2 text-rose-500 text-xs py-4"):
                ui.icon("error", size="16px")
                ui.label(f"Could not render chart: {e}")
