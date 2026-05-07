import json
from typing import Any, Dict, Callable
from websockets.asyncio.server import ServerConnection

from app.api.message_router import MessageRouter
from app.core.session_service import SessionService
from app.windows.window_service import WindowService

def create_session_router(
    session_service: SessionService, 
    window_service: WindowService,
    on_state_changed: Callable[[], None]
) -> MessageRouter:
    router = MessageRouter()

    async def handle_get(connection: ServerConnection, message: Dict[str, Any]) -> None:
        await connection.send(
            json.dumps(
                {
                    "type": "session/updated",
                    "payload": session_service.get_summary().to_payload(),
                }
            )
        )

    async def handle_list_windows(connection: ServerConnection, message: Dict[str, Any]) -> None:
        windows = window_service.list_windows()
        await connection.send(
            json.dumps(
                {
                    "type": "session/windows-listed",
                    "payload": [{"id": w.id, "title": w.title} for w in windows],
                }
            )
        )

    async def handle_select_window(connection: ServerConnection, message: Dict[str, Any]) -> None:
        payload = message.get("payload", {})
        window_id = payload.get("windowId")
        session_service.update_window(window_id, payload.get("windowTitle"))
        
        # 选中窗口后，尝试将其拉到前台以便截图
        if window_id:
            window_service.bring_to_front(window_id)
            
        on_state_changed()

    router.register("session/get", handle_get)
    router.register("session/list-windows", handle_list_windows)
    router.register("session/select-window", handle_select_window)
    
    return router
