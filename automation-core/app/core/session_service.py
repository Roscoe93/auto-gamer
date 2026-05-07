from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class SessionMetrics:
    durationSeconds: int = 0
    actionCount: int = 0
    resumeCount: int = 0

@dataclass
class SessionSummary:
    runId: str | None = None
    status: str = "idle"
    platform: str = "unknown"
    windowId: str | None = None
    windowTitle: str | None = None
    windowMode: str | None = None
    profileId: str | None = None
    profileName: str | None = None
    metrics: SessionMetrics = field(default_factory=SessionMetrics)

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


class SessionService:
    def __init__(self) -> None:
        self._summary = SessionSummary()

    def get_summary(self) -> SessionSummary:
        return self._summary

    def update_window(self, window_id: str | None, window_title: str | None) -> None:
        self._summary.windowId = window_id
        self._summary.windowTitle = window_title
