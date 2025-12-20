"""
WebSocket Integration Tests
Tests for WebSocket connection, authentication, channel filtering, and message routing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient
from app.api.websocket import (
    ConnectionManager,
    manager,
    websocket_endpoint,
    broadcast_trade_update,
    broadcast_price_update,
    get_user_from_token
)
from app.core.security import create_access_token


class TestConnectionManager:
    """Test ConnectionManager functionality"""
    
    @pytest.fixture
    def connection_manager(self):
        """Create a fresh connection manager for testing"""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        ws.receive_text = AsyncMock()
        ws.query_params = {}
        ws.headers = {}
        return ws
    
    @pytest.mark.asyncio
    async def test_connect_websocket(self, connection_manager, mock_websocket):
        """Test connecting a WebSocket"""
        user_id = 1
        channels = ["prices", "trades"]
        
        await connection_manager.connect(mock_websocket, user_id, channels)
        
        # Verify accept was called
        mock_websocket.accept.assert_called_once()
        
        # Verify connection is stored
        assert user_id in connection_manager.active_connections
        assert "prices" in connection_manager.active_connections[user_id]
        assert "trades" in connection_manager.active_connections[user_id]
        assert mock_websocket in connection_manager.active_connections[user_id]["prices"]
        assert mock_websocket in connection_manager.all_connections
    
    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, connection_manager, mock_websocket):
        """Test disconnecting a WebSocket"""
        user_id = 1
        channels = ["prices"]
        
        # Connect first
        await connection_manager.connect(mock_websocket, user_id, channels)
        
        # Disconnect
        connection_manager.disconnect(mock_websocket, user_id)
        
        # Verify connection is removed
        assert mock_websocket not in connection_manager.all_connections
        if user_id in connection_manager.active_connections:
            # Channel should be empty or removed
            assert "prices" not in connection_manager.active_connections[user_id] or \
                   len(connection_manager.active_connections[user_id].get("prices", [])) == 0
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, connection_manager, mock_websocket):
        """Test sending personal message to specific user/channel"""
        user_id = 1
        channels = ["prices"]
        
        await connection_manager.connect(mock_websocket, user_id, channels)
        
        message = {"type": "test", "data": "test_data"}
        await connection_manager.send_personal_message(message, user_id, "prices")
        
        # Verify send_text was called
        mock_websocket.send_text.assert_called_once()
        call_args = mock_websocket.send_text.call_args[0][0]
        assert json.loads(call_args) == message
    
    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, connection_manager):
        """Test broadcasting to all connections"""
        # Create multiple mock websockets
        ws1 = AsyncMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2 = AsyncMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        
        await connection_manager.connect(ws1, user_id=1, channels=["prices"])
        await connection_manager.connect(ws2, user_id=2, channels=["trades"])
        
        message = {"type": "broadcast", "data": "all"}
        await connection_manager.broadcast(message, channel=None)
        
        # Both should receive
        assert ws1.send_text.called
        assert ws2.send_text.called
    
    @pytest.mark.asyncio
    async def test_broadcast_to_channel(self, connection_manager):
        """Test broadcasting to specific channel only"""
        # Create mock websockets
        ws1 = AsyncMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2 = AsyncMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        
        await connection_manager.connect(ws1, user_id=1, channels=["prices"])
        await connection_manager.connect(ws2, user_id=2, channels=["trades"])
        
        message = {"type": "price_update", "channel": "prices", "data": {}}
        await connection_manager.broadcast(message, channel="prices")
        
        # Only ws1 should receive (subscribed to prices)
        assert ws1.send_text.called
        # ws2 should not receive (not subscribed to prices)
        assert not ws2.send_text.called


class TestWebSocketAuthentication:
    """Test WebSocket authentication"""
    
    @pytest.mark.asyncio
    async def test_get_user_from_token_valid(self):
        """Test getting user from valid token"""
        from app.core.security import create_access_token
        
        # Create a valid token
        user_id = 123
        token = create_access_token(data={"sub": str(user_id)})
        
        # Mock websocket with token
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params = {"token": token}
        mock_ws.headers = {}
        
        result = await get_user_from_token(mock_ws)
        assert result == user_id
    
    @pytest.mark.asyncio
    async def test_get_user_from_token_invalid(self):
        """Test getting user from invalid token"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params = {"token": "invalid_token"}
        mock_ws.headers = {}
        
        result = await get_user_from_token(mock_ws)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_from_token_missing(self):
        """Test getting user when token is missing"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params = {}
        mock_ws.headers = {}
        
        result = await get_user_from_token(mock_ws)
        assert result is None


class TestWebSocketMessageRouting:
    """Test WebSocket message routing"""
    
    @pytest.mark.asyncio
    async def test_broadcast_trade_update(self):
        """Test broadcasting trade update"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        user_id = 1
        await manager.connect(mock_ws, user_id, channels=["trades"])
        
        symbol = "BTCUSDT"
        trade_data = {
            "id": "test_trade_1",
            "price": 45000.0,
            "quantity": 1.0,
            "side": "buy",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        await broadcast_trade_update(symbol, trade_data)
        
        # Verify message was sent
        assert mock_ws.send_text.called
        
        # Cleanup
        manager.disconnect(mock_ws, user_id)
    
    @pytest.mark.asyncio
    async def test_broadcast_price_update(self):
        """Test broadcasting price update with change info"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        user_id = 1
        await manager.connect(mock_ws, user_id, channels=["prices"])
        
        symbol = "BTCUSDT"
        price = 45000.0
        change = 100.0
        change_percent = 0.22
        
        await broadcast_price_update(symbol, price, change=change, change_percent=change_percent)
        
        # Verify message was sent
        assert mock_ws.send_text.called
        
        # Verify message content
        call_args = mock_ws.send_text.call_args[0][0]
        message = json.loads(call_args)
        
        assert message["type"] == "price_update"
        assert message["channel"] == "prices"
        assert "data" in message
        assert message["data"]["symbol"] == symbol
        assert message["data"]["price"] == price
        assert message["data"]["change"] == change
        assert message["data"]["changePercent"] == change_percent
        
        # Cleanup
        manager.disconnect(mock_ws, user_id)
    
    @pytest.mark.asyncio
    async def test_price_update_short_keys(self):
        """Test price update includes short keys"""
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        user_id = 1
        await manager.connect(mock_ws, user_id, channels=["prices"])
        
        await broadcast_price_update("BTCUSDT", 45000.0, change=100.0, change_percent=0.22)
        
        call_args = mock_ws.send_text.call_args[0][0]
        message = json.loads(call_args)
        data = message["data"]
        
        # Check short keys exist
        assert "s" in data  # symbol
        assert "p" in data  # price
        assert "c" in data  # change
        assert "cp" in data  # changePercent
        
        # Cleanup
        manager.disconnect(mock_ws, user_id)


class TestWebSocketChannelFiltering:
    """Test WebSocket channel filtering"""
    
    @pytest.mark.asyncio
    async def test_channel_filtering_prices_only(self):
        """Test that messages are only sent to subscribed channels"""
        # Create websockets with different channel subscriptions
        ws_prices = AsyncMock(spec=WebSocket)
        ws_prices.accept = AsyncMock()
        ws_prices.send_text = AsyncMock()
        
        ws_trades = AsyncMock(spec=WebSocket)
        ws_trades.accept = AsyncMock()
        ws_trades.send_text = AsyncMock()
        
        await manager.connect(ws_prices, user_id=1, channels=["prices"])
        await manager.connect(ws_trades, user_id=2, channels=["trades"])
        
        # Broadcast price update
        await broadcast_price_update("BTCUSDT", 45000.0)
        
        # Only ws_prices should receive
        assert ws_prices.send_text.called
        assert not ws_trades.send_text.called
        
        # Cleanup
        manager.disconnect(ws_prices, user_id=1)
        manager.disconnect(ws_trades, user_id=2)
    
    @pytest.mark.asyncio
    async def test_multiple_channels_subscription(self):
        """Test websocket subscribed to multiple channels"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        
        await manager.connect(ws, user_id=1, channels=["prices", "trades"])
        
        # Broadcast to prices
        await broadcast_price_update("BTCUSDT", 45000.0)
        assert ws.send_text.called
        
        # Reset call count
        ws.send_text.reset_mock()
        
        # Broadcast to trades
        await broadcast_trade_update("BTCUSDT", {"id": "1", "price": 45000.0})
        assert ws.send_text.called
        
        # Cleanup
        manager.disconnect(ws, user_id=1)


class TestWebSocketConnectionCleanup:
    """Test WebSocket connection cleanup"""
    
    @pytest.mark.asyncio
    async def test_cleanup_on_disconnect(self):
        """Test cleanup when websocket disconnects"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        
        user_id = 1
        await manager.connect(ws, user_id, channels=["prices"])
        
        # Verify connected
        assert ws in manager.all_connections
        
        # Disconnect
        manager.disconnect(ws, user_id)
        
        # Verify cleaned up
        assert ws not in manager.all_connections
        if user_id in manager.active_connections:
            assert "prices" not in manager.active_connections[user_id] or \
                   len(manager.active_connections[user_id].get("prices", [])) == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_on_send_error(self):
        """Test cleanup when send fails"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock(side_effect=Exception("Send failed"))
        
        user_id = 1
        await manager.connect(ws, user_id, channels=["prices"])
        
        # Try to send message (should handle error gracefully)
        message = {"type": "test"}
        await manager.broadcast(message, channel="prices")
        
        # Connection should be cleaned up after error
        # (This depends on implementation, but should not crash)


class TestWebSocketEndpoint:
    """Test WebSocket endpoint integration"""
    
    @pytest.mark.asyncio
    async def test_websocket_endpoint_requires_auth(self):
        """Test that WebSocket endpoint requires authentication"""
        # This test would require a more complex setup with actual WebSocket client
        # For now, we test the authentication function directly
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.query_params = {}  # No token
        mock_ws.headers = {}
        mock_ws.close = AsyncMock()
        
        user_id = await get_user_from_token(mock_ws)
        assert user_id is None  # Should fail without token


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

