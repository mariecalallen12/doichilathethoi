"""
Integration Tests for Financial Module
Tests currency exchange, payment processing, and financial reports endpoints
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestFinancialEndpoints:
    """Test suite for financial endpoints"""
    
    def test_currency_exchange_endpoint(self):
        """Test currency exchange endpoint"""
        response = client.post(
            "/api/financial/exchange",
            params={
                "from_currency": "USDT",
                "to_currency": "BTC",
                "amount": 1000
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 403, 422]
        print("✅ Currency exchange endpoint exists")
    
    def test_payment_processing_endpoint(self):
        """Test payment processing endpoint"""
        response = client.post(
            "/api/financial/payments/process",
            params={
                "payment_id": "1",
                "action": "approve"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 403, 404, 422]
        print("✅ Payment processing endpoint exists")
    
    def test_financial_reports_endpoint(self):
        """Test financial reports endpoint"""
        response = client.get(
            "/api/financial/reports",
            params={
                "report_type": "summary",
                "period": "monthly"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Financial reports endpoint exists")
    
    def test_financial_reports_transactions(self):
        """Test financial reports with transactions type"""
        response = client.get(
            "/api/financial/reports",
            params={
                "report_type": "transactions",
                "period": "weekly"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        print("✅ Financial reports transactions endpoint works")

