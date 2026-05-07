import asyncio
import json
import pathlib
import sys
import unittest

import websockets


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api.websocket_server import BridgeWebSocketServer


class BridgeWebSocketServerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.server = BridgeWebSocketServer(host="127.0.0.1", port=0, heartbeat_interval=0.05)
        await self.server.start()
        self.url = f"ws://127.0.0.1:{self.server.port}"

    async def asyncTearDown(self) -> None:
        await self.server.stop()

    async def test_client_receives_status_and_can_fetch_session(self) -> None:
        async with websockets.connect(self.url) as socket:
            status_message = json.loads(await asyncio.wait_for(socket.recv(), timeout=1))
            self.assertEqual(status_message["type"], "connection/status")
            self.assertEqual(status_message["payload"]["state"], "connected")

            await socket.send(json.dumps({"type": "session/get"}))
            session_message = json.loads(await asyncio.wait_for(socket.recv(), timeout=1))

            self.assertEqual(session_message["type"], "session/updated")
            self.assertEqual(session_message["payload"]["status"], "idle")
            self.assertIsNone(session_message["payload"]["runId"])

    async def test_client_receives_heartbeat_event(self) -> None:
        async with websockets.connect(self.url) as socket:
            await asyncio.wait_for(socket.recv(), timeout=1)

            heartbeat_message = json.loads(await asyncio.wait_for(socket.recv(), timeout=1))
            self.assertEqual(heartbeat_message["type"], "connection/heartbeat")
            self.assertIn("ts", heartbeat_message["payload"])


if __name__ == "__main__":
    unittest.main()
