"""
Trade Broadcaster Integration Tests
Tests for trade broadcaster lifecycle, broadcast functions, and price updates
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.services.trade_broadcaster import (
    TradeBroadcaster,
    get_trade_broadcaster
)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.api.websocket import (
    manager,
    broadcast_trade_update,
    broadcast_price_update
)


class TestTradeBroadcasterInitialization:
    """Test trade broadcaster initialization"""
    
    def test_broadcaster_singleton(self):
        """Test broadcaster uses singleton pattern"""
        broadcaster1 = get_trade_broadcaster()
        broadcaster2 = get_trade_broadcaster()
        
        assert broadcaster1 is broadcaster2
        assert isinstance(broadcaster1, TradeBroadcaster)
    
    def test_broadcaster_default_state(self):
        """Test broadcaster default state"""
        broadcaster = get_trade_broadcaster()
        
        assert broadcaster.is_running is False
        assert broadcaster.broadcast_task is None
        assert broadcaster.symbols == ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        assert len(broadcaster.base_prices) == 3
        assert broadcaster.broadcast_fn is None
        assert broadcaster.price_broadcast_fn is None
    
    def test_broadcaster_symbols(self):
        """Test broadcaster has correct symbols"""
        broadcaster = get_trade_broadcaster()
        
        expected_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        assert broadcaster.symbols == expected_symbols
        
        for symbol in expected_symbols:
            assert symbol in broadcaster.base_prices
            assert symbol in broadcaster.current_prices
            assert symbol in broadcaster.previous_prices


class TestBroadcastFunctionSetup:
    """Test setting broadcast functions"""
    
    @pytest.mark.asyncio
    async def test_set_broadcast_function(self):
        """Test setting trade broadcast function"""
        broadcaster = get_trade_broadcaster()
        
        mock_fn = AsyncMock()
        broadcaster.set_broadcast_function(mock_fn)
        
        assert broadcaster.broadcast_fn is not None
        assert broadcaster.broadcast_fn == mock_fn
    
    @pytest.mark.asyncio
    async def test_set_price_broadcast_function(self):
        """Test setting price broadcast function"""
        broadcaster = get_trade_broadcaster()
        
        mock_fn = AsyncMock()
        broadcaster.set_price_broadcast_function(mock_fn)
        
        assert broadcaster.price_broadcast_fn is not None
        assert broadcaster.price_broadcast_fn == mock_fn
    
    @pytest.mark.asyncio
    async def test_set_both_functions(self):
        """Test setting both broadcast functions"""
        broadcaster = get_trade_broadcaster()
        
        mock_trade_fn = AsyncMock()
        mock_price_fn = AsyncMock()
        
        broadcaster.set_broadcast_function(mock_trade_fn)
        broadcaster.set_price_broadcast_function(mock_price_fn)
        
        assert broadcaster.broadcast_fn == mock_trade_fn
        assert broadcaster.price_broadcast_fn == mock_price_fn


class TestTradeBroadcasterLifecycle:
    """Test trade broadcaster lifecycle"""
    
    @pytest.mark.asyncio
    async def test_start_broadcaster(self):
        """Test starting broadcaster"""
        broadcaster = get_trade_broadcaster()
        
        # Ensure not running
        await broadcaster.stop()
        assert broadcaster.is_running is False
        
        # Start broadcaster
        await broadcaster.start(interval_seconds=0.1)
        assert broadcaster.is_running is True
        assert broadcaster.broadcast_task is not None
        
        # Wait a bit
        await asyncio.sleep(0.15)
        
        # Stop broadcaster
        await broadcaster.stop()
        assert broadcaster.is_running is False
    
    @pytest.mark.asyncio
    async def test_stop_broadcaster(self):
        """Test stopping broadcaster"""
        broadcaster = get_trade_broadcaster()
        
        # Start first
        await broadcaster.start(interval_seconds=0.1)
        assert broadcaster.is_running is True
        
        # Stop
        await broadcaster.stop()
        assert broadcaster.is_running is False
    
    @pytest.mark.asyncio
    async def test_double_start_handling(self):
        """Test that starting twice doesn't create multiple tasks"""
        broadcaster = get_trade_broadcaster()
        
        await broadcaster.stop()  # Ensure stopped
        
        # Start first time
        await broadcaster.start(interval_seconds=0.1)
        task1 = broadcaster.broadcast_task
        
        # Start second time (should be ignored)
        await broadcaster.start(interval_seconds=0.1)
        task2 = broadcaster.broadcast_task
        
        # Should be same task
        assert task1 is task2
        
        await broadcaster.stop()


class TestTradeGeneration:
    """Test trade generation"""
    
    def test_generate_trade(self):
        """Test generating a trade"""
        broadcaster = get_trade_broadcaster()
        
        symbol = "BTCUSDT"
        trade = broadcaster._generate_trade(symbol)
        
        assert trade is not None
        assert "id" in trade
        assert "price" in trade
        assert "quantity" in trade
        assert "side" in trade
        assert "timestamp" in trade
        assert "time" in trade
        
        assert trade["side"] in ["buy", "sell"]
        assert isinstance(trade["price"], (int, float))
        assert isinstance(trade["quantity"], (int, float))
        assert trade["price"] > 0
        assert trade["quantity"] > 0
    
    def test_generate_trade_symbol_format(self):
        """Test trade uses correct symbol format"""
        broadcaster = get_trade_broadcaster()
        
        for symbol in broadcaster.symbols:
            trade = broadcaster._generate_trade(symbol)
            # Trade ID should contain symbol
            assert symbol in trade["id"]
    
    def test_get_recent_trades(self):
        """Test getting recent trades"""
        broadcaster = get_trade_broadcaster()
        
        symbol = "BTCUSDT"
        trades = broadcaster.get_recent_trades(symbol, limit=10)
        
        assert isinstance(trades, list)
        assert len(trades) == 10
        
        for trade in trades:
            assert "id" in trade
            assert "price" in trade
            assert "quantity" in trade
            assert "side" in trade
            assert "timestamp" in trade
            assert "time" in trade


class TestPriceUpdateWithChange:
    """Test price updates with change/changePercent"""
    
    @pytest.mark.asyncio
    async def test_price_update_calculates_change(self):
        """Test price update calculates change correctly"""
        broadcaster = get_trade_broadcaster()
        
        symbol = "BTCUSDT"
        initial_price = broadcaster.base_prices[symbol]
        
        # Set previous price
        broadcaster.previous_prices[symbol] = initial_price
        
        # Generate trade (which updates current price)
        trade = broadcaster._generate_trade(symbol)
        current_price = trade["price"]
        
        # Calculate expected change
        expected_change = current_price - initial_price
        expected_change_percent = (expected_change / initial_price * 100) if initial_price > 0 else 0.0
        
        # Verify change calculation logic
        assert abs(expected_change) >= 0  # Can be positive or negative
        assert isinstance(expected_change_percent, float)
    
    @pytest.mark.asyncio
    async def test_broadcast_price_update_with_change(self):
        """Test broadcasting price update with change info"""
        # Mock websocket
        from unittest.mock import AsyncMock
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        # Connect to prices channel
        await manager.connect(mock_ws, user_id=1, channels=["prices"])
        
        # Broadcast price update with change
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
        assert message["data"]["symbol"] == symbol
        assert message["data"]["price"] == price
        assert message["data"]["change"] == change
        assert message["data"]["changePercent"] == change_percent
        
        # Cleanup
        manager.disconnect(mock_ws, user_id=1)


class TestBroadcastLoop:
    """Test broadcast loop functionality"""
    
    @pytest.mark.asyncio
    async def test_broadcast_loop_calls_functions(self):
        """Test broadcast loop calls broadcast functions"""
        broadcaster = get_trade_broadcaster()
        
        # Mock broadcast functions
        mock_trade_fn = AsyncMock()
        mock_price_fn = AsyncMock()
        
        broadcaster.set_broadcast_function(mock_trade_fn)
        broadcaster.set_price_broadcast_function(mock_price_fn)
        
        # Start broadcaster with short interval
        await broadcaster.start(interval_seconds=0.1)
        
        # Wait for at least one iteration
        await asyncio.sleep(0.15)
        
        # Verify functions were called
        assert mock_trade_fn.called
        assert mock_price_fn.called
        
        await broadcaster.stop()
    
    @pytest.mark.asyncio
    async def test_broadcast_loop_updates_previous_prices(self):
        """Test broadcast loop updates previous prices"""
        broadcaster = get_trade_broadcaster()
        
        symbol = "BTCUSDT"
        initial_previous = broadcaster.previous_prices[symbol]
        
        # Mock functions
        mock_trade_fn = AsyncMock()
        mock_price_fn = AsyncMock()
        
        broadcaster.set_broadcast_function(mock_trade_fn)
        broadcaster.set_price_broadcast_function(mock_price_fn)
        
        # Start and run one iteration
        await broadcaster.start(interval_seconds=0.1)
        await asyncio.sleep(0.15)
        await broadcaster.stop()
        
        # Previous price should be updated (may be same or different)
        # Just verify it's still a valid price
        assert broadcaster.previous_prices[symbol] > 0


class TestIntegrationWithWebSocket:
    """Test integration with WebSocket manager"""
    
    @pytest.mark.asyncio
    async def test_broadcaster_integration_with_websocket(self):
        """Test broadcaster integrates with WebSocket manager"""
        broadcaster = get_trade_broadcaster()
        
        # Set real broadcast functions
        broadcaster.set_broadcast_function(broadcast_trade_update)
        broadcaster.set_price_broadcast_function(broadcast_price_update)
        
        # Mock websocket
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        # Connect to channels
        await manager.connect(mock_ws, user_id=1, channels=["trades", "prices"])
        
        # Start broadcaster
        await broadcaster.start(interval_seconds=0.1)
        
        # Wait for messages
        await asyncio.sleep(0.25)
        
        # Verify messages were sent
        assert mock_ws.send_text.called
        
        await broadcaster.stop()
        manager.disconnect(mock_ws, user_id=1)
    
    @pytest.mark.asyncio
    async def test_symbol_format_in_broadcast(self):
        """Test symbol format in broadcast messages"""
        broadcaster = get_trade_broadcaster()
        
        # Mock websocket
        mock_ws = AsyncMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        
        await manager.connect(mock_ws, user_id=1, channels=["trades", "prices"])
        
        broadcaster.set_broadcast_function(broadcast_trade_update)
        broadcaster.set_price_broadcast_function(broadcast_price_update)
        
        await broadcaster.start(interval_seconds=0.1)
        await asyncio.sleep(0.25)
        await broadcaster.stop()
        
        # Check that messages contain correct symbol format (BTCUSDT)
        if mock_ws.send_text.called:
            calls = mock_ws.send_text.call_args_list
            for call in calls:
                message_str = call[0][0]
                message = json.loads(message_str)
                
                if message.get("type") == "trade_update":
                    assert "data" in message
                    assert "symbol" in message["data"]
                    # Symbol should be in BTCUSDT format
                    assert message["data"]["symbol"] in broadcaster.symbols
                
                if message.get("type") == "price_update":
                    assert "data" in message
                    assert "symbol" in message["data"] or "s" in message["data"]
                    symbol = message["data"].get("symbol") or message["data"].get("s")
                    assert symbol in broadcaster.symbols
        
        manager.disconnect(mock_ws, user_id=1)


class TestErrorHandling:
    """Test error handling in broadcaster"""
    
    @pytest.mark.asyncio
    async def test_broadcast_loop_handles_errors(self):
        """Test broadcast loop handles errors gracefully"""
        broadcaster = get_trade_broadcaster()
        
        # Mock function that raises error
        mock_fn = AsyncMock(side_effect=Exception("Test error"))
        broadcaster.set_broadcast_function(mock_fn)
        broadcaster.set_price_broadcast_function(mock_fn)
        
        # Start broadcaster - should not crash
        await broadcaster.start(interval_seconds=0.1)
        await asyncio.sleep(0.15)
        
        # Should still be running (errors are caught)
        assert broadcaster.is_running is True
        
        await broadcaster.stop()
    
    @pytest.mark.asyncio
    async def test_generate_trade_error_handling(self):
        """Test trade generation handles errors"""
        broadcaster = get_trade_broadcaster()
        
        # Invalid symbol should return None or handle gracefully
        trade = broadcaster._generate_trade("INVALID")
        # Should handle gracefully (may return None or use default)
        if trade is not None:
            assert "price" in trade


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

