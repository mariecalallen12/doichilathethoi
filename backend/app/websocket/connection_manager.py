"""
WebSocket Connection Manager for Chat
"""
from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Each room (conversation_id) has a list of active connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        """Accept and store a new connection."""
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        """Remove a connection."""
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a personal message to a single websocket."""
        await websocket.send_text(message)

    async def broadcast_to_room(self, message: str, room_id: int):
        """Broadcast a message to all clients in a specific room."""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

    async def broadcast_to_room_except(self, message: str, room_id: int, websocket: WebSocket):
        """Broadcast a message to all clients in a room except the sender."""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != websocket:
                    await connection.send_text(message)

# Create a single instance of the manager
manager = ConnectionManager()
