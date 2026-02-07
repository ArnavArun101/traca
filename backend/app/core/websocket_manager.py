import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Map session_id to WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"New connection: {session_id}. Total connections: {len(self.active_connections)}")

<<<<<<< HEAD
    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            del self.active_connections[session_id]
            await websocket.close()
=======
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51
            logger.info(f"Disconnected: {session_id}. Remaining connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast(self, message: dict):
<<<<<<< HEAD
        disconnected_sessions = []
        for session_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except RuntimeError as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                disconnected_sessions.append(session_id)
            except Exception as e:
                logger.error(f"Unexpected error sending message to {session_id}: {e}")
                disconnected_sessions.append(session_id)
        for session_id in disconnected_sessions:
            await self.disconnect(session_id)
=======
        for connection in self.active_connections.values():
            await connection.send_json(message)
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

manager = ConnectionManager()
