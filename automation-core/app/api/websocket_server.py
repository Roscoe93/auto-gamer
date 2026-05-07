from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from websockets.asyncio.server import ServerConnection, serve

from app.core.session_service import SessionService


class BridgeWebSocketServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, heartbeat_interval: float = 5.0) -> None:
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self._session_service = SessionService()
        self._server = None

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
        heartbeat_task = asyncio.create_task(self._heartbeat_loop(connection))
        await connection.send(json.dumps({"type": "connection/status", "payload": {"state": "connected"}}))

        try:
            async for raw_message in connection:
                await self._handle_message(connection, raw_message)
        finally:
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
