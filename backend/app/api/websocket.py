"""
WebSocket Server for Real-time Updates
Digital Utopia Platform

Channels:
- orders: Order updates
- positions: Position updates  
- prices: Market price updates (with change/changePercent)
- orderbook: Order book updates
- trades: Trade execution updates
- candles: Candlestick updates
- market_data: Market data updates
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict, List, Set, Optional
import json
import asyncio
from datetime import datetime
import logging

from ..core.security import verify_access_token
from ..models.user import User
from ..db.session import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Store connections by user_id and channel
        # Format: {user_id: {channel: [websocket1, websocket2, ...]}}
        self.active_connections: Dict[int, Dict[str, List[WebSocket]]] = {}
        # Store all connections for broadcasting
        self.all_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, user_id: int, channels: List[str]):
        """Connect a WebSocket and subscribe to channels"""
        await websocket.accept()
        self.all_connections.append(websocket)
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        for channel in channels:
            if channel not in self.active_connections[user_id]:
                self.active_connections[user_id][channel] = []
            self.active_connections[user_id][channel].append(websocket)
        
        logger.info(f"WebSocket connected: user_id={user_id}, channels={channels}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket"""
        if websocket in self.all_connections:
            self.all_connections.remove(websocket)
        
        if user_id in self.active_connections:
            for channel in self.active_connections[user_id]:
                if websocket in self.active_connections[user_id][channel]:
                    self.active_connections[user_id][channel].remove(websocket)
            
            # Clean up empty channels
            self.active_connections[user_id] = {
                k: v for k, v in self.active_connections[user_id].items() if v
            }
            
            # Clean up empty user entries
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int, channel: str):
        """Send message to specific user on specific channel"""
        if user_id not in self.active_connections:
            return
        
        if channel not in self.active_connections[user_id]:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections[user_id][channel]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict, channel: str = None):
        """
        Broadcast message to all connections (or specific channel).
        
        If channel is provided, only sends to connections subscribed to that channel.
        Otherwise, broadcasts to all connections.
        """
        message_json = json.dumps(message)
        disconnected = []
        
        if channel:
            # Filter by channel - send only to connections subscribed to this channel
            connections_to_send = set()
            for user_id, user_channels in self.active_connections.items():
                if channel in user_channels:
                    connections_to_send.update(user_channels[channel])
            
            for connection in connections_to_send:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting to channel {channel}: {e}")
                    disconnected.append(connection)
        else:
            # Broadcast to all connections
            for connection in self.all_connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")
                    disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            # Find and remove from active_connections
            for user_id in list(self.active_connections.keys()):
                user_channels = self.active_connections[user_id]
                for ch in list(user_channels.keys()):
                    if conn in user_channels[ch]:
                        user_channels[ch].remove(conn)
                # Clean up empty channels
                self.active_connections[user_id] = {
                    k: v for k, v in user_channels.items() if v
                }
                # Clean up empty user entries
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from all_connections
            if conn in self.all_connections:
                self.all_connections.remove(conn)


# Global connection manager
manager = ConnectionManager()


async def get_user_from_token(websocket: WebSocket) -> Optional[int]:
    """Get user_id from WebSocket token"""
    try:
        # Get token from query params or headers
        token = websocket.query_params.get("token") or websocket.headers.get("authorization", "").replace("Bearer ", "")
        
        if not token:
            logger.warning("WebSocket connection attempt without token")
            return None
        
        payload = verify_access_token(token)
        if not payload:
            logger.warning("WebSocket connection attempt with invalid token")
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("WebSocket token missing user_id in payload")
            return None
        
        return int(user_id)
    except ValueError as e:
        logger.error(f"Invalid user_id format in token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting user from token: {e}", exc_info=True)
        return None


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint"""
    user_id = None
    channels = []
    
    try:
        # Authenticate
        user_id = await get_user_from_token(websocket)
        if not user_id:
            logger.warning("WebSocket connection rejected: authentication failed")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return
        
        logger.info(f"WebSocket authentication successful for user_id={user_id}")
        
        # Get channels from query params
        channels_param = websocket.query_params.get("channels", "orders,positions,prices,orderbook,trades,candles,market_data")
        channels = [ch.strip() for ch in channels_param.split(",")]
        
        # Connect
        await manager.connect(websocket, user_id, channels)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "channels": channels,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages (with timeout to allow ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                try:
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    if message_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    elif message_type == "subscribe":
                        # Handle channel subscription changes
                        new_channels = message.get("channels", [])
                        channels = new_channels
                        await websocket.send_json({
                            "type": "subscribed",
                            "channels": channels
                        })
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {data}")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except:
                    break
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: user_id={user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user_id={user_id}: {e}", exc_info=True)
    finally:
        if user_id:
            manager.disconnect(websocket, user_id)


# ========== HELPER FUNCTIONS FOR BROADCASTING ==========

async def broadcast_order_update(order_data: dict, user_id: int):
    """Broadcast order update to user"""
    await manager.send_personal_message({
        "type": "order_update",
        "channel": "orders",
        "data": order_data,
        "timestamp": datetime.utcnow().isoformat()
    }, user_id, "orders")


async def broadcast_position_update(position_data: dict, user_id: int):
    """Broadcast position update to user"""
    await manager.send_personal_message({
        "type": "position_update",
        "channel": "positions",
        "data": position_data,
        "timestamp": datetime.utcnow().isoformat()
    }, user_id, "positions")


async def broadcast_price_update(symbol: str, price: float, change: float = None, change_percent: float = None):
    """
    Broadcast price update to all subscribers.
    
    Args:
        symbol: Trading symbol
        price: Current price
        change: Price change (optional)
        change_percent: Price change percentage (optional)
    """
    data = {
        "symbol": symbol,  # Full key for compatibility
        "s": symbol,  # Short key for optimization
        "price": round(price, 4),
        "p": round(price, 4),  # Short key
        "t": int(datetime.utcnow().timestamp()),  # Unix timestamp
    }
    
    # Add change information if provided
    if change is not None:
        data["change"] = round(change, 4)
        data["c"] = round(change, 4)  # Short key
    if change_percent is not None:
        data["changePercent"] = round(change_percent, 4)
        data["cp"] = round(change_percent, 4)  # Short key
    
    await manager.broadcast({
        "type": "price_update",
        "channel": "prices",
        "data": data
    }, "prices")


async def broadcast_sim_event(event_type: str, channel: str, data: dict):
    """Broadcast generic simulator event to all subscribers."""
    await manager.broadcast(
        {
            "type": event_type,
            "channel": channel,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        },
        channel,
    )


async def broadcast_health_update(health_status: dict, user_id: int = None):
    """Broadcast diagnostic health update to user or all subscribers"""
    message = {
        "type": "health_update",
        "channel": "diagnostics",
        "data": health_status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if user_id:
        await manager.send_personal_message(message, user_id, "diagnostics")
    else:
        await manager.broadcast(message, "diagnostics")


async def broadcast_candle_update(symbol: str, candle_data: dict):
    """Broadcast candle update to all subscribers"""
    await manager.broadcast({
        "type": "candle_update",
        "channel": "candles",
        "data": {
            "symbol": symbol,
            "candle": candle_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, "candles")


async def broadcast_market_data_update(symbol: str, market_data: dict):
    """Broadcast market data update to all subscribers"""
    await manager.broadcast({
        "type": "market_data_update",
        "channel": "market_data",
        "data": {
            "symbol": symbol,
            "market_data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, "market_data")


async def broadcast_trade_update(symbol: str, trade_data: dict):
    """
    Broadcast trade update to all subscribers.
    
    Args:
        symbol: Trading symbol (e.g., "BTCUSDT")
        trade_data: Trade data dict with keys like:
            - price: float
            - quantity: float
            - side: str ("buy" or "sell")
            - timestamp: str (ISO format)
            - id: str (optional trade ID)
    """
    await manager.broadcast({
        "type": "trade_update",
        "channel": "trades",
        "data": {
            "symbol": symbol,
            "trade": trade_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    }, "trades")


async def broadcast_alert(alert_data: dict, user_id: int = None):
    """Broadcast alert notification to user or all subscribers"""
    message = {
        "type": "alert",
        "channel": "diagnostics",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if user_id:
        await manager.send_personal_message(message, user_id, "diagnostics")
    else:
        await manager.broadcast(message, "diagnostics")

