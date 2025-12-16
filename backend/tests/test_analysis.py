"""
Integration Tests for Analysis Module
Tests analysis endpoints: technical, fundamental, sentiment, signals, backtest
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestAnalysisEndpoints:
    """Test suite for analysis endpoints"""
    
    def test_get_technical_analysis(self):
        """Test get technical analysis endpoint"""
        response = client.get("/api/analysis/technical/BTCUSDT")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get technical analysis endpoint exists")
    
    def test_get_fundamental_analysis(self):
        """Test get fundamental analysis endpoint"""
        response = client.get("/api/analysis/fundamental/BTCUSDT")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get fundamental analysis endpoint exists")
    
    def test_get_sentiment(self):
        """Test get sentiment endpoint"""
        response = client.get("/api/analysis/sentiment")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get sentiment endpoint exists")
    
    def test_get_signals(self):
        """Test get trading signals endpoint"""
        response = client.get("/api/analysis/signals")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get signals endpoint exists")
    
    def test_run_backtest(self):
        """Test run backtest endpoint"""
        from datetime import datetime, timedelta
        response = client.post(
            "/api/analysis/backtest",
            json={
                "symbol": "BTCUSDT",
                "strategy": "simple_momentum",
                "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "initial_balance": 10000.0
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422, 400]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Run backtest endpoint exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

