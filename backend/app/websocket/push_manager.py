"""
WebSocket Real-time Push Notification System
Handles real-time updates for Admin and Client apps
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set, List, Any
import json
import logging
from datetime import datetime
import redis.asyncio as redis
from ..core.config import settings
from ..dependencies import get_current_user_ws

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections with Redis pub/sub"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "market": set(),
            "trading": set(),
            "admin": set(),
            "notifications": set(),
            "alerts": set()
        }
        self.user_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.redis_client: redis.Redis = None
        self.pubsub = None
    
    async def connect(self, websocket: WebSocket, channel: str, user_id: str = None):
        """Connect client to specific channel"""
        await websocket.accept()
        
        if channel in self.active_connections:
            self.active_connections[channel].add(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = {}
            self.user_connections[user_id][channel] = websocket
        
        # Initialize Redis if not already
        if not self.redis_client:
            await self._init_redis()
        
        # Add to Redis set for tracking
        await self.redis_client.sadd(f"ws:{channel}:connections", user_id or "anonymous")
        
        logger.info(f"Client connected to {channel} channel. User: {user_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "channel": channel,
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
    
    async def disconnect(self, websocket: WebSocket, channel: str, user_id: str = None):
        """Disconnect client from channel"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].pop(channel, None)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from Redis
        if self.redis_client:
            await self.redis_client.srem(f"ws:{channel}:connections", user_id or "anonymous")
        
        logger.info(f"Client disconnected from {channel} channel. User: {user_id}")
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            logger.info("Redis connection initialized for WebSocket manager")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast message to all connections in a channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {channel}: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        self.active_connections[channel] -= disconnected
    
    async def send_to_user(self, user_id: str, message: dict, channel: str = None):
        """Send message to specific user across channels or specific channel"""
        if user_id not in self.user_connections:
            return
        
        connections = self.user_connections[user_id]
        
        if channel and channel in connections:
            await self.send_personal_message(message, connections[channel])
        else:
            # Send to all user's connections
            for conn in connections.values():
                await self.send_personal_message(message, conn)
    
    async def publish_to_redis(self, channel: str, message: dict):
        """Publish message to Redis channel for cross-instance sync"""
        if not self.redis_client:
            await self._init_redis()
        
        try:
            await self.redis_client.publish(
                f"ws:broadcast:{channel}",
                json.dumps(message)
            )
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")
    
    async def subscribe_to_redis(self, channel: str):
        """Subscribe to Redis channel for receiving broadcasts"""
        if not self.pubsub:
            await self._init_redis()
        
        try:
            await self.pubsub.subscribe(f"ws:broadcast:{channel}")
            
            # Listen for messages
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await self.broadcast_to_channel(channel, data)
        except Exception as e:
            logger.error(f"Error in Redis subscription: {e}")
    
    def get_channel_stats(self) -> Dict[str, int]:
        """Get connection statistics for all channels"""
        return {
            channel: len(connections)
            for channel, connections in self.active_connections.items()
        }

# Global connection manager instance
manager = ConnectionManager()

# WebSocket endpoint handlers
async def handle_market_stream(websocket: WebSocket, user_id: str = None):
    """Handle market data real-time stream"""
    await manager.connect(websocket, "market", user_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client requests (subscribe to symbols, etc.)
            if message.get("action") == "subscribe":
                symbols = message.get("symbols", [])
                await manager.send_personal_message({
                    "type": "subscription",
                    "status": "subscribed",
                    "symbols": symbols
                }, websocket)
            
            elif message.get("action") == "unsubscribe":
                symbols = message.get("symbols", [])
                await manager.send_personal_message({
                    "type": "subscription",
                    "status": "unsubscribed",
                    "symbols": symbols
                }, websocket)
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "market", user_id)
    except Exception as e:
        logger.error(f"Error in market stream: {e}")
        await manager.disconnect(websocket, "market", user_id)

async def handle_trading_stream(websocket: WebSocket, user_id: str):
    """Handle trading signals and order updates"""
    await manager.connect(websocket, "trading", user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle trading actions
            if message.get("action") == "place_order":
                # Process order (integrate with trading system)
                await manager.send_personal_message({
                    "type": "order",
                    "status": "processing",
                    "order_id": message.get("order_id")
                }, websocket)
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "trading", user_id)
    except Exception as e:
        logger.error(f"Error in trading stream: {e}")
        await manager.disconnect(websocket, "trading", user_id)

async def handle_admin_stream(websocket: WebSocket, user_id: str):
    """Handle admin real-time updates"""
    await manager.connect(websocket, "admin", user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle admin actions
            if message.get("action") == "broadcast":
                # Admin broadcasting to all users
                await manager.broadcast_to_channel(
                    message.get("target_channel", "notifications"),
                    {
                        "type": "admin_message",
                        "message": message.get("message"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "admin", user_id)
    except Exception as e:
        logger.error(f"Error in admin stream: {e}")
        await manager.disconnect(websocket, "admin", user_id)

async def handle_notification_stream(websocket: WebSocket, user_id: str):
    """Handle user notifications"""
    await manager.connect(websocket, "notifications", user_id)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "mark_read":
                notification_id = message.get("notification_id")
                # Mark notification as read in database
                await manager.send_personal_message({
                    "type": "notification",
                    "status": "marked_read",
                    "notification_id": notification_id
                }, websocket)
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "notifications", user_id)
    except Exception as e:
        logger.error(f"Error in notification stream: {e}")
        await manager.disconnect(websocket, "notifications", user_id)

async def handle_alert_stream(websocket: WebSocket, user_id: str):
    """Handle system alerts for admin"""
    await manager.connect(websocket, "alerts", user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process alert acknowledgments
            message = json.loads(data)
            
            if message.get("action") == "acknowledge":
                alert_id = message.get("alert_id")
                await manager.send_personal_message({
                    "type": "alert",
                    "status": "acknowledged",
                    "alert_id": alert_id
                }, websocket)
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket, "alerts", user_id)
    except Exception as e:
        logger.error(f"Error in alert stream: {e}")
        await manager.disconnect(websocket, "alerts", user_id)

# Helper functions for external use
async def push_market_update(symbol: str, data: dict):
    """Push market data update to all subscribed clients"""
    await manager.broadcast_to_channel("market", {
        "type": "market_update",
        "symbol": symbol,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def push_trade_signal(signal: dict):
    """Push trading signal to trading channel"""
    await manager.broadcast_to_channel("trading", {
        "type": "signal",
        "data": signal,
        "timestamp": datetime.utcnow().isoformat()
    })

async def push_notification(user_id: str, notification: dict):
    """Push notification to specific user"""
    await manager.send_to_user(user_id, {
        "type": "notification",
        "data": notification,
        "timestamp": datetime.utcnow().isoformat()
    }, "notifications")

async def push_alert(alert: dict, admin_only: bool = True):
    """Push system alert"""
    channel = "alerts" if admin_only else "notifications"
    await manager.broadcast_to_channel(channel, {
        "type": "alert",
        "data": alert,
        "timestamp": datetime.utcnow().isoformat()
    })

async def push_admin_broadcast(message: str, level: str = "info"):
    """Broadcast message from admin to all users"""
    await manager.broadcast_to_channel("notifications", {
        "type": "admin_broadcast",
        "message": message,
        "level": level,
        "timestamp": datetime.utcnow().isoformat()
    })
