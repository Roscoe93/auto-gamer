from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from websockets.asyncio.server import ServerConnection, serve

from app.core.session_service import SessionService
from app.core.run_controller import RunController
from app.core.capture_service import CaptureService
from app.windows.window_service import WindowService
from app.scripts.registry import ScriptRegistry
from app.scripts.profile_manager import ProfileManager

from app.api.message_router import MessageRouter
from app.api.handlers.session_handler import create_session_router
from app.api.handlers.run_handler import create_run_router
from app.api.handlers.script_handler import create_script_router


class BridgeWebSocketServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, heartbeat_interval: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval

        # Initialize Core Services
        self._session_service = SessionService()
        self._window_service = WindowService()
        self._run_controller = RunController(self._session_service, self._on_state_changed)
        self._script_registry = ScriptRegistry()
        self._profile_manager = ProfileManager()
        self._capture_service = CaptureService(self._session_service, self._window_service)
        self._capture_service.add_listener(self._on_preview_frame)

        # Setup Router
        self._router = MessageRouter()
        self._router.include_router(create_session_router(self._session_service, self._window_service, self._on_state_changed))
        self._router.include_router(create_run_router(self._run_controller))
        self._router.include_router(create_script_router(self._script_registry, self._profile_manager))

        self._server = None
        self._active_connections: set[ServerConnection] = set()

    def _on_preview_frame(self, payload: dict) -> None:
        raw_payload = json.dumps(payload)
        for conn in self._active_connections:
            asyncio.create_task(conn.send(raw_payload))

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
        self._capture_service.start()
        self._server = await serve(self._handle_connection, self.host, self.port)
        sockets = self._server.sockets or []
        if sockets:
            self.port = sockets[0].getsockname()[1]

    async def stop(self) -> None:
        self._capture_service.stop()
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
        try:
            message = json.loads(raw_message)
            # Delegate to the router
            await self._router.dispatch(connection, message)
        except json.JSONDecodeError:
            await connection.send(json.dumps({"type": "error", "payload": {"code": "INVALID_JSON", "message": "Failed to parse JSON message"}}))
        except Exception as e:
            # Catch unexpected errors to prevent the connection from crashing silently
            print(f"Error handling message: {e}")
            await connection.send(json.dumps({"type": "error", "payload": {"code": "INTERNAL_ERROR", "message": str(e)}}))

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