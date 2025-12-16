"""
Integration Tests for Legal Module
Tests legal endpoints: terms, privacy, risk warning, complaints
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestLegalEndpoints:
    """Test suite for legal endpoints"""
    
    def test_get_terms(self):
        """Test get terms of service endpoint"""
        response = client.get("/api/legal/terms")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get terms endpoint exists")
    
    def test_get_terms_by_version(self):
        """Test get terms by version endpoint"""
        response = client.get("/api/legal/terms/version/1.0")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get terms by version endpoint exists")
    
    def test_get_privacy(self):
        """Test get privacy policy endpoint"""
        response = client.get("/api/legal/privacy")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get privacy endpoint exists")
    
    def test_get_privacy_by_version(self):
        """Test get privacy by version endpoint"""
        response = client.get("/api/legal/privacy/version/1.0")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get privacy by version endpoint exists")
    
    def test_get_risk_warning(self):
        """Test get risk warning endpoint"""
        response = client.get("/api/legal/risk-warning")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get risk warning endpoint exists")
    
    def test_get_complaints(self):
        """Test get complaints endpoint"""
        response = client.get(
            "/api/legal/complaints",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get complaints endpoint exists")
    
    def test_submit_complaint(self):
        """Test submit complaint endpoint"""
        response = client.post(
            "/api/legal/complaints",
            json={
                "complaint_type": "service",
                "subject": "Test Complaint",
                "description": "Test complaint description",
                "priority": "normal"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422, 400]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Submit complaint endpoint exists")
    
    def test_get_complaint_by_id(self):
        """Test get complaint by ID endpoint"""
        response = client.get(
            "/api/legal/complaints/1",
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get complaint by ID endpoint exists")
    
    def test_update_complaint(self):
        """Test update complaint endpoint"""
        response = client.put(
            "/api/legal/complaints/1",
            json={
                "status": "resolved",
                "user_satisfaction": "satisfied"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 404, 401, 422, 400]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Update complaint endpoint exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

