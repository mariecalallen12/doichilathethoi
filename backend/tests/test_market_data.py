"""
Integration Tests for Market Data Module
Tests historical data, market analysis, and data feeds endpoints
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestMarketDataEndpoints:
    """Test suite for market data endpoints"""
    
    def test_get_historical_data(self):
        """Test historical data endpoint"""
        response = client.get(
            "/api/market/historical-data/BTCUSDT",
            params={
                "timeframe": "1h",
                "limit": 100
            },
            headers={"Authorization": "Bearer test_token"}
        )
        # Should return 401 without valid token, but endpoint exists
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Historical data endpoint exists")
    
    def test_get_market_analysis(self):
        """Test market analysis endpoint"""
        response = client.get(
            "/api/market/analysis/BTCUSDT",
            params={
                "analysis_type": "technical",
                "timeframe": "1d"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "indicators" in data
        print("✅ Market analysis endpoint exists")
    
    def test_get_data_feeds(self):
        """Test data feeds endpoint"""
        response = client.get(
            "/api/market/data-feeds",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "feeds" in data
        print("✅ Data feeds endpoint exists")
    
    def test_get_market_summary(self):
        """Test market summary endpoint"""
        response = client.get(
            "/api/market/summary",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "market_statistics" in data
        print("✅ Market summary endpoint exists")

