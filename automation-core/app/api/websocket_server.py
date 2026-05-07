from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from websockets.asyncio.server import ServerConnection, serve

from app.core.session_service import SessionService
from app.core.run_controller import RunController
from app.windows.window_service import WindowService


class BridgeWebSocketServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, heartbeat_interval: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self._session_service = SessionService()
        self._window_service = WindowService()
        self._run_controller = RunController(self._session_service, self._on_state_changed)
        self._server = None
        self._active_connections: set[ServerConnection] = set()

    def _on_state_changed(self) -> None:
        # Broadcast state change to all active connections
        payload = json.dumps(
            {
                "type": "session/updated",
                "payload": self._session_service.get_summary().to_payload(),
            }
        )
        for conn in self._active_connections:
            asyncio.create_task(conn.send(payload))

    async def start(self) -> None:
        self._server = await serve(self._handle_connection, self.host, self.port)
        sockets = self._server.sockets or []
        if sockets:
            self.port = sockets[0].getsockname()[1]

    async def stop(self) -> None:
        if self._server is None:
            return

        self._server.close()
        await self._server.wait_closed()
        self._server = None

    async def _handle_connection(self, connection: ServerConnection) -> None:
        self._active_connections.add(connection)
        heartbeat_task = asyncio.create_task(self._heartbeat_loop(connection))
        await connection.send(json.dumps({"type": "connection/status", "payload": {"state": "connected"}}))

        try:
            async for raw_message in connection:
                await self._handle_message(connection, raw_message)
        finally:
            self._active_connections.remove(connection)
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

    async def _handle_message(self, connection: ServerConnection, raw_message: str) -> None:
        message = json.loads(raw_message)
        message_type = message.get("type")

        if message_type == "session/get":
            await connection.send(
                json.dumps(
                    {
                        "type": "session/updated",
                        "payload": self._session_service.get_summary().to_payload(),
                    }
                )
            )
            return

        if message_type == "session/list-windows":
            windows = self._window_service.list_windows()
            await connection.send(
                json.dumps(
                    {
                        "type": "session/windows-listed",
                        "payload": [{"id": w.id, "title": w.title} for w in windows],
                    }
                )
            )
            return

        if message_type == "session/select-window":
            payload = message.get("payload", {})
            self._session_service.update_window(payload.get("windowId"), payload.get("windowTitle"))
            self._on_state_changed()
            return

        if message_type == "run/start":
            try:
                self._run_controller.start()
            except ValueError as e:
                await connection.send(json.dumps({"type": "error", "payload": {"code": "START_FAILED", "message": str(e)}}))
            return

        if message_type == "run/pause":
            try:
                self._run_controller.pause()
            except ValueError as e:
                await connection.send(json.dumps({"type": "error", "payload": {"code": "PAUSE_FAILED", "message": str(e)}}))
            return

        if message_type == "run/resume":
            try:
                self._run_controller.resume()
            except ValueError as e:
                await connection.send(json.dumps({"type": "error", "payload": {"code": "RESUME_FAILED", "message": str(e)}}))
            return

        if message_type == "run/stop":
            self._run_controller.stop()
            return

        await connection.send(
            json.dumps(
                {
                    "type": "error",
                    "payload": {
                        "code": "UNKNOWN_COMMAND",
                        "message": f"Unsupported command: {message_type}",
                    },
                }
            )
        )

    async def _heartbeat_loop(self, connection: ServerConnection) -> None:
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            await connection.send(
                json.dumps(
                    {
                        "type": "connection/heartbeat",
                        "payload": {"ts": datetime.now(timezone.utc).isoformat()},
                    }
                )
            )


import contextlib  # noqa: E402
