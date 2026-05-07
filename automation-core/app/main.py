from __future__ import annotations

import asyncio
import os

from app.api.websocket_server import BridgeWebSocketServer


async def run() -> None:
    host = os.getenv("QUIET_STUDIO_BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("QUIET_STUDIO_BRIDGE_PORT", "8765"))
    server = BridgeWebSocketServer(host=host, port=port)
    await server.start()
    print(f"Quiet Studio bridge listening on ws://{host}:{server.port}")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run())
