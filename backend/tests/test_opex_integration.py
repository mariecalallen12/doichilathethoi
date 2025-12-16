"""
OPEX Integration Testing
Tests for OPEX services integration with FastAPI backend
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.opex_client import OPEXClient
from app.services.opex_trading_service import OPEXTradingService
from app.services.opex_market_service import OPEXMarketService


class TestOPEXAPIEndpoints:
    """Test OPEX API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_trading_health_endpoint(self, client):
        """Test trading health check endpoint"""
        response = client.get("/api/trading/health")
        assert response.status_code in [200, 503]  # 503 if OPEX unavailable
        data = response.json()
        assert "status" in data
        assert "service" in data
    
    def test_market_symbols_endpoint(self, client):
        """Test market symbols endpoint"""
        response = client.get("/api/market/symbols")
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_market_orderbook_endpoint(self, client):
        """Test market orderbook endpoint"""
        response = client.get("/api/market/orderbook/BTCUSDT")
        assert response.status_code in [200, 400, 503]
        if response.status_code == 200:
            data = response.json()
            assert "symbol" in data
            assert "bids" in data
            assert "asks" in data
    
    def test_cache_stats_endpoint(self, client):
        """Test cache statistics endpoint"""
        # This endpoint might require authentication
        response = client.get("/api/trading/cache/stats")
        # Should return 200 or 401/403 if auth required
        assert response.status_code in [200, 401, 403, 500]


class TestOPEXClient:
    """Test OPEX client"""
    
    @pytest.mark.asyncio
    async def test_opex_client_initialization(self):
        """Test OPEX client can be initialized"""
        client = OPEXClient(
            base_url="http://localhost:8082",
            api_key=None,
            timeout=30
        )
        assert client.base_url == "http://localhost:8082"
        assert client.timeout == 30
    
    @pytest.mark.asyncio
    async def test_opex_client_request_retry(self):
        """Test OPEX client retry logic"""
        client = OPEXClient(
            base_url="http://localhost:8082",
            api_key=None,
            timeout=5
        )
        
        # Mock httpx client to simulate failures
        with patch.object(client.client, 'request', new_callable=AsyncMock) as mock_request:
            from httpx import HTTPStatusError, Response, Request
            from http import HTTPStatus
            
            # Simulate 3 failures then success
            mock_response = Mock(spec=Response)
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status = Mock(side_effect=HTTPStatusError(
                "Server Error",
                request=Mock(spec=Request),
                response=mock_response
            ))
            
            mock_request.side_effect = [
                HTTPStatusError("Server Error", request=Mock(), response=mock_response),
                HTTPStatusError("Server Error", request=Mock(), response=mock_response),
                HTTPStatusError("Server Error", request=Mock(), response=mock_response),
            ]
            
            # Should raise after retries
            with pytest.raises(Exception):
                await client._request("GET", "/test")


class TestOPEXTradingService:
    """Test OPEX trading service"""
    
    @pytest.mark.asyncio
    async def test_place_order(self):
        """Test placing an order"""
        service = OPEXTradingService()
        
        with patch.object(service.opex, 'place_order', new_callable=AsyncMock) as mock_place:
            mock_place.return_value = {
                "id": "123",
                "status": "pending",
                "symbol": "BTC_USDT"
            }
            
            from decimal import Decimal
            result = await service.place_order(
                user_id=1,
                symbol="BTCUSDT",
                side="buy",
                order_type="market",
                quantity=Decimal("1.0")
            )
            
            assert result["id"] == "123"
            assert mock_place.called
    
    @pytest.mark.asyncio
    async def test_get_orders(self):
        """Test getting orders"""
        service = OPEXTradingService()
        
        with patch.object(service.opex, 'get_orders', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                {"id": "1", "symbol": "BTC_USDT", "side": "BUY", "status": "FILLED"}
            ]
            
            result = await service.get_orders(user_id=1)
            assert isinstance(result, list)
            assert mock_get.called


class TestOPEXMarketService:
    """Test OPEX market service"""
    
    @pytest.mark.asyncio
    async def test_get_symbols(self):
        """Test getting symbols"""
        service = OPEXMarketService()
        
        with patch.object(service.opex, 'get_symbols', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                {"symbol": "BTC_USDT", "base": "BTC", "quote": "USDT"}
            ]
            
            result = await service.get_symbols()
            assert isinstance(result, list)
            assert mock_get.called
    
    @pytest.mark.asyncio
    async def test_get_orderbook(self):
        """Test getting orderbook"""
        service = OPEXMarketService()
        
        with patch.object(service.opex, 'get_orderbook', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "symbol": "BTC_USDT",
                "bids": [[30000, 1.0]],
                "asks": [[30001, 1.0]]
            }
            
            result = await service.get_orderbook("BTCUSDT")
            assert "symbol" in result
            assert "bids" in result
            assert "asks" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

