"""
Integration Tests for Client Profile Module
Tests profile, settings, preferences, and onboarding endpoints
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestClientProfileEndpoints:
    """Test suite for client profile endpoints"""
    
    def test_get_client_profile(self):
        """Test get client profile endpoint"""
        response = client.get(
            "/api/client/profile",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get client profile endpoint exists")
    
    def test_update_client_profile(self):
        """Test update client profile endpoint"""
        response = client.put(
            "/api/client/profile",
            params={
                "full_name": "Test User",
                "phone": "+1234567890"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        print("✅ Update client profile endpoint exists")
    
    def test_get_client_settings(self):
        """Test get client settings endpoint"""
        response = client.get(
            "/api/client/settings",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get client settings endpoint exists")
    
    def test_update_client_settings(self):
        """Test update client settings endpoint"""
        response = client.put(
            "/api/client/settings",
            params={
                "language": "en",
                "timezone": "UTC"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        print("✅ Update client settings endpoint exists")
    
    def test_get_client_preferences(self):
        """Test get client preferences endpoint"""
        response = client.get(
            "/api/client/preferences",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get client preferences endpoint exists")
    
    def test_update_client_preferences(self):
        """Test update client preferences endpoint"""
        response = client.put(
            "/api/client/preferences",
            params={
                "trading_style": "conservative",
                "risk_tolerance": "medium"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        print("✅ Update client preferences endpoint exists")
    
    def test_get_onboarding_status(self):
        """Test get onboarding status endpoint"""
        response = client.get(
            "/api/client/onboarding/status",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get onboarding status endpoint exists")
    
    def test_complete_onboarding_step(self):
        """Test complete onboarding step endpoint"""
        response = client.post(
            "/api/client/onboarding/complete",
            params={
                "step": "profile_completion"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        print("✅ Complete onboarding step endpoint exists")

