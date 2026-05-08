from __future__ import annotations

import asyncio
import os
import logging

from app.api.websocket_server import BridgeWebSocketServer

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("kuroneko")

async def run() -> None:
    host = os.getenv("KURONEKO_STUDIO_BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("KURONEKO_STUDIO_BRIDGE_PORT", "8765"))
    server = BridgeWebSocketServer(host=host, port=port)
    await server.start()
    
    print(f"KuroNeko Studio bridge listening on ws://{host}:{server.port}")
    logger.info(f"KuroNeko Studio bridge listening on ws://{host}:{server.port}")
    logger.debug("Debug log test")
    logger.warning("Warning log test")
    logger.error("Error log test")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run())
