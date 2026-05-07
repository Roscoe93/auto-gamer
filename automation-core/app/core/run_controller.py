from __future__ import annotations

import asyncio
import uuid
from typing import Callable

from app.core.session_service import SessionService


class RunController:
    def __init__(self, session_service: SessionService, on_state_changed: Callable[[], None] | None = None) -> None:
        self._session_service = session_service
        self._on_state_changed = on_state_changed
        self._run_task: asyncio.Task | None = None

    def start(self) -> None:
        summary = self._session_service.get_summary()
        if summary.status != "idle":
            raise ValueError(f"Cannot start from state: {summary.status}")
        if not summary.windowId:
            raise ValueError("Cannot start: No target window selected")

        summary.runId = str(uuid.uuid4())
        summary.status = "running"
        summary.metrics.durationSeconds = 0
        summary.metrics.actionCount = 0
        summary.metrics.resumeCount = 0

        self._notify()

        if self._run_task and not self._run_task.done():
            self._run_task.cancel()
        self._run_task = asyncio.create_task(self._simulation_loop())

    def pause(self) -> None:
        summary = self._session_service.get_summary()
        if summary.status != "running":
            raise ValueError(f"Cannot pause from state: {summary.status}")
        
        summary.status = "paused"
        self._notify()

    def resume(self) -> None:
        summary = self._session_service.get_summary()
        if summary.status != "paused":
            raise ValueError(f"Cannot resume from state: {summary.status}")
        
        summary.status = "running"
        summary.metrics.resumeCount += 1
        self._notify()

    def stop(self) -> None:
        summary = self._session_service.get_summary()
        if summary.status == "idle":
            return
            
        summary.status = "idle"
        summary.runId = None
        self._notify()
        
        if self._run_task and not self._run_task.done():
            self._run_task.cancel()

    def _notify(self) -> None:
        if self._on_state_changed:
            self._on_state_changed()

    async def _simulation_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(1.0)
                summary = self._session_service.get_summary()
                if summary.status == "running":
                    summary.metrics.durationSeconds += 1
                    # Simulate some actions being performed
                    if summary.metrics.durationSeconds % 3 == 0:
                        summary.metrics.actionCount += 1
                    self._notify()
                elif summary.status == "idle":
                    break
        except asyncio.CancelledError:
            pass
