from typing import Any, Callable, Coroutine, Dict
import json
from websockets.asyncio.server import ServerConnection

MessageHandler = Callable[[ServerConnection, Dict[str, Any]], Coroutine[Any, Any, None]]

class MessageRouter:
    def __init__(self):
        self._handlers: Dict[str, MessageHandler] = {}

    def register(self, message_type: str, handler: MessageHandler) -> None:
        """Register a handler for a specific message type."""
        self._handlers[message_type] = handler

    def include_router(self, router: "MessageRouter") -> None:
        """Include handlers from another router."""
        self._handlers.update(router._handlers)

    async def dispatch(self, connection: ServerConnection, message: Dict[str, Any]) -> None:
        """Dispatch a message to the appropriate handler."""
        message_type = message.get("type")
        handler = self._handlers.get(message_type)
        
        if handler:
            await handler(connection, message)
        else:
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
