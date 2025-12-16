"""
OPEX WebSocket Integration
WebSocket proxy for real-time data from OPEX Core
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.routing import APIRouter

from app.services.opex_client import get_opex_client, OPEXClient

logger = logging.getLogger(__name__)
router = APIRouter()


class OPEXWebSocketManager:
    """Manages WebSocket connections and proxies messages from OPEX"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.opex_client: OPEXClient = get_opex_client()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def handle_opex_message(self, message: Dict[str, Any]):
        """Handle message from OPEX WebSocket and forward to clients"""
        # Forward OPEX messages to all connected clients
        await self.broadcast({
            "type": "opex_update",
            "data": message
        })


# Global WebSocket manager instance
websocket_manager = OPEXWebSocketManager()


@router.websocket("/ws/opex")
async def websocket_opex_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for OPEX real-time data
    
    Clients connect to this endpoint to receive:
    - Order updates
    - Position updates
    - Price updates
    - Trade updates
    """
    import uuid
    client_id = str(uuid.uuid4())
    
    try:
        await websocket_manager.connect(websocket, client_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to OPEX WebSocket"
        })
        
        # Keep connection alive and forward messages
        while True:
            try:
                # Receive message from client (subscriptions, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client subscriptions
                if message.get("type") == "subscribe":
                    # Subscribe to specific channels
                    channels = message.get("channels", [])
                    await websocket.send_json({
                        "type": "subscribed",
                        "channels": channels
                    })
                elif message.get("type") == "unsubscribe":
                    # Unsubscribe from channels
                    channels = message.get("channels", [])
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "channels": channels
                    })
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        websocket_manager.disconnect(client_id)


# Function to broadcast OPEX updates (called from other services)
async def broadcast_opex_update(update_type: str, data: Dict[str, Any]):
    """
    Broadcast OPEX update to all connected WebSocket clients
    
    Args:
        update_type: Type of update (order, position, price, trade)
        data: Update data
    """
    await websocket_manager.broadcast({
        "type": update_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })

