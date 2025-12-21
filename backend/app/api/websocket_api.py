"""
WebSocket API Endpoints
Manages WebSocket connections and real-time streams
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from ..websocket.push_manager import (
    manager,
    handle_market_stream,
    handle_trading_stream,
    handle_admin_stream,
    handle_notification_stream,
    handle_alert_stream,
    push_market_update,
    push_trade_signal,
    push_notification,
    push_alert,
    push_admin_broadcast
)
from ..dependencies import get_current_user, get_current_user_ws
import logging

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = logging.getLogger(__name__)

@router.websocket("/market")
async def websocket_market(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for market data stream"""
    user_id = None
    if token:
        try:
            # Verify token and get user
            user = await get_current_user_ws(token)
            user_id = user.get("id")
        except:
            pass
    
    await handle_market_stream(websocket, user_id)

@router.websocket("/trading/{user_id}")
async def websocket_trading(websocket: WebSocket, user_id: str, token: str):
    """WebSocket endpoint for trading signals and orders"""
    try:
        # Verify token
        user = await get_current_user_ws(token)
        if user.get("id") != user_id:
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await handle_trading_stream(websocket, user_id)

@router.websocket("/admin/{user_id}")
async def websocket_admin(websocket: WebSocket, user_id: str, token: str):
    """WebSocket endpoint for admin real-time updates"""
    try:
        user = await get_current_user_ws(token)
        if user.get("id") != user_id or not user.get("is_admin"):
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await handle_admin_stream(websocket, user_id)

@router.websocket("/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str, token: str):
    """WebSocket endpoint for user notifications"""
    try:
        user = await get_current_user_ws(token)
        if user.get("id") != user_id:
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await handle_notification_stream(websocket, user_id)

@router.websocket("/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: str, token: str):
    """WebSocket endpoint for system alerts (admin only)"""
    try:
        user = await get_current_user_ws(token)
        if user.get("id") != user_id or not user.get("is_admin"):
            await websocket.close(code=1008, reason="Unauthorized")
            return
    except Exception as e:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    await handle_alert_stream(websocket, user_id)

@router.get("/stats")
async def get_websocket_stats(current_user: dict = Depends(get_current_user)):
    """Get WebSocket connection statistics"""
    return manager.get_channel_stats()

# HTTP endpoints for triggering WebSocket pushes
@router.post("/push/market")
async def trigger_market_push(
    symbol: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger market data push"""
    await push_market_update(symbol, data)
    return {"status": "pushed", "symbol": symbol}

@router.post("/push/signal")
async def trigger_signal_push(
    signal: dict,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger trading signal push"""
    await push_trade_signal(signal)
    return {"status": "pushed", "signal": signal}

@router.post("/push/notification")
async def trigger_notification_push(
    user_id: str,
    notification: dict,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger notification push to specific user"""
    await push_notification(user_id, notification)
    return {"status": "pushed", "user_id": user_id}

@router.post("/push/alert")
async def trigger_alert_push(
    alert: dict,
    admin_only: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger system alert push"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    await push_alert(alert, admin_only)
    return {"status": "pushed", "admin_only": admin_only}

@router.post("/push/broadcast")
async def trigger_broadcast(
    message: str,
    level: str = "info",
    current_user: dict = Depends(get_current_user)
):
    """Broadcast message from admin to all users"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    await push_admin_broadcast(message, level)
    return {"status": "broadcast", "message": message, "level": level}
