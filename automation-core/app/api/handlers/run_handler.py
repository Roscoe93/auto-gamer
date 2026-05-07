import json
from typing import Any, Dict
from websockets.asyncio.server import ServerConnection

from app.api.message_router import MessageRouter
from app.core.run_controller import RunController

def create_run_router(run_controller: RunController) -> MessageRouter:
    router = MessageRouter()

    async def handle_start(connection: ServerConnection, message: Dict[str, Any]) -> None:
        try:
            run_controller.start()
        except ValueError as e:
            await connection.send(json.dumps({"type": "error", "payload": {"code": "START_FAILED", "message": str(e)}}))

    async def handle_pause(connection: ServerConnection, message: Dict[str, Any]) -> None:
        try:
            run_controller.pause()
        except ValueError as e:
            await connection.send(json.dumps({"type": "error", "payload": {"code": "PAUSE_FAILED", "message": str(e)}}))

    async def handle_resume(connection: ServerConnection, message: Dict[str, Any]) -> None:
        try:
            run_controller.resume()
        except ValueError as e:
            await connection.send(json.dumps({"type": "error", "payload": {"code": "RESUME_FAILED", "message": str(e)}}))

    async def handle_stop(connection: ServerConnection, message: Dict[str, Any]) -> None:
        run_controller.stop()

    router.register("run/start", handle_start)
    router.register("run/pause", handle_pause)
    router.register("run/resume", handle_resume)
    router.register("run/stop", handle_stop)
    
    return router
