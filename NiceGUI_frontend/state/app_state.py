from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


# ──────────────────────────────────────────────
# Data Models (mirrors frontend/src/types/*)
# ──────────────────────────────────────────────

@dataclass
class Column:
    name: str
    dtype: str


@dataclass
class UploadResponse:
    session_id: str
    dataset_id: str
    row_count: int
    columns: list[Column] = field(default_factory=list)


@dataclass
class ExecutiveSummary:
    headline: str
    summary: str
    confidence: str = "High"  # "High" | "Medium" | "Low"


@dataclass
class TableResult:
    title: str
    columns: list[str] = field(default_factory=list)
    rows: list[list[Any]] = field(default_factory=list)


@dataclass
class ChartSpec:
    title: str
    type: str
    plotly_json: Any = None


@dataclass
class Insight:
    title: str
    body: str


@dataclass
class Recommendation:
    title: str
    body: str


@dataclass
class DebugInfo:
    generated_code: str | None = None
    execution_mode: str | None = None  # "SQL" | "PYTHON" | "DETERMINISTIC"
    execution_plan: str | None = None
    llm_reasoning: str | None = None


@dataclass
class ReportSection:
    title: str
    executive_summary: ExecutiveSummary
    tables: list[TableResult] = field(default_factory=list)
    charts: list[ChartSpec] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    report_type: str | None = None


@dataclass
class ChatMessage:
    id: str
    role: str  # "user" | "assistant"
    content: str | None = None
    report: ReportSection | None = None
    debug: DebugInfo | None = None
    success: bool | None = None
    execution_id: int | None = None
    execution_time: int | None = None
    retry_count: int | None = None
    model: str | None = None
    provider: str | None = None


@dataclass
class ComputedMetrics:
    total_executions: int = 0
    first_try_success: int = 0
    retry_success: int = 0
    failed: int = 0
    success_rate: float = 0.0
    first_try_rate: float = 0.0
    recovery_rate: float = 0.0
    failure_aggregates: dict[str, int] = field(default_factory=dict)


# ──────────────────────────────────────────────
# Per-Client Application State
# ──────────────────────────────────────────────

@dataclass
class AppState:
    """State container for a single connected client session."""
    # Navigation & View
    active_tab: str = "analysis"  # "analysis" | "metrics"
    is_dark: bool = False
    is_left_sidebar_collapsed: bool = False
    is_right_sidebar_collapsed: bool = False

    # Dataset & Upload
    session: UploadResponse | None = None
    is_uploading: bool = False
    upload_error: str | None = None

    # Analysis & Chat
    question: str = ""
    chat_history: list[ChatMessage] = field(default_factory=list)
    is_analyzing: bool = False
    trace_history: list[dict[str, Any]] = field(default_factory=list)

    # Session History
    session_queries: list[dict[str, Any]] = field(default_factory=list)
    selected_history_id: str | None = None

    # UI Refresh Listeners
    _listeners: list[Callable[[], None]] = field(default_factory=list)

    def on_change(self, callback: Callable[[], None]) -> None:
        """Register a callback invoked when state changes."""
        self._listeners.append(callback)

    def notify_change(self) -> None:
        """Notify all listeners to refresh UI elements."""
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    @property
    def has_dataset(self) -> bool:
        return self.session is not None

    @property
    def dataset_name(self) -> str:
        return self.session.dataset_id if self.session else "dataset.csv"

    @property
    def row_count(self) -> int:
        return self.session.row_count if self.session else 0

    @property
    def columns(self) -> list[Column]:
        return self.session.columns if self.session else []

    def get_latest_assistant_message(self) -> ChatMessage | None:
        for msg in reversed(self.chat_history):
            if msg.role == "assistant":
                return msg
        return None

    def reset_on_upload(self, session: UploadResponse) -> None:
        """Reset chat, trace, and history when a new dataset is uploaded (mirrors App.tsx L56-60)."""
        self.session = session
        self.chat_history.clear()
        self.trace_history.clear()
        self.session_queries.clear()
        self.upload_error = None
        self.is_uploading = False
        self.selected_history_id = None
        self.notify_change()

    def reset_to_start_workspace(self) -> None:
        """Reset state back to the initial start workspace landing page."""
        self.session = None
        self.active_tab = "analysis"
        self.chat_history.clear()
        self.trace_history.clear()
        self.session_queries.clear()
        self.upload_error = None
        self.is_analyzing = False
        self.is_uploading = False
        self.selected_history_id = None
        self.notify_change()

