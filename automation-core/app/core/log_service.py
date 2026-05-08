import logging
from typing import Callable, List
from datetime import datetime, timezone

class WebSocketLogHandler(logging.Handler):
    def __init__(self, callback: Callable[[dict], None]):
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord):
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname.lower(),
                "source": record.name,
                "message": record.getMessage()
            }
            self.callback(log_entry)
        except Exception:
            self.handleError(record)

from collections import deque

class LogService:
    def __init__(self):
        self._listeners: List[Callable[[dict], None]] = []
        self._recent_logs = deque(maxlen=100)
        self._setup_logger()

    def _setup_logger(self):
        # We use a specific logger for our application
        logger = logging.getLogger("kuroneko")
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers
        if not any(isinstance(h, WebSocketLogHandler) for h in logger.handlers):
            handler = WebSocketLogHandler(self._on_log)
            logger.addHandler(handler)

    def add_listener(self, listener: Callable[[dict], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[dict], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def get_recent_logs(self) -> List[dict]:
        return list(self._recent_logs)

    def _on_log(self, log_entry: dict) -> None:
        self._recent_logs.append(log_entry)
        for listener in self._listeners:
            listener(log_entry)
