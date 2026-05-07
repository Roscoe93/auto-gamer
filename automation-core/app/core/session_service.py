from __future__ import annotations

from dataclasses import asdict, dataclass


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

    def to_payload(self) -> dict[str, object]:
        return asdict(self)


class SessionService:
    def __init__(self) -> None:
        self._summary = SessionSummary()

    def get_summary(self) -> SessionSummary:
        return self._summary
