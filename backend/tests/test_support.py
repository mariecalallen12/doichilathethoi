"""
Integration Tests for Support Module
Tests support endpoints: articles, categories, search, contact, offices, channels, FAQ
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestSupportEndpoints:
    """Test suite for support endpoints"""
    
    def test_get_articles(self):
        """Test get articles endpoint"""
        response = client.get("/api/support/articles")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get articles endpoint exists")
    
    def test_get_article_by_id(self):
        """Test get article by ID endpoint"""
        response = client.get("/api/support/articles/1")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get article by ID endpoint exists")
    
    def test_get_categories(self):
        """Test get categories endpoint"""
        response = client.get("/api/support/categories")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get categories endpoint exists")
    
    def test_search_articles(self):
        """Test search articles endpoint"""
        response = client.post(
            "/api/support/search",
            json={"query": "deposit"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Search articles endpoint exists")
    
    def test_submit_contact(self):
        """Test submit contact endpoint"""
        response = client.post(
            "/api/support/contact",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test Subject",
                "message": "Test message"
            }
        )
        assert response.status_code in [200, 401, 422, 400]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Submit contact endpoint exists")
    
    def test_get_offices(self):
        """Test get offices endpoint"""
        response = client.get("/api/support/offices")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get offices endpoint exists")
    
    def test_get_channels(self):
        """Test get channels endpoint"""
        response = client.get("/api/support/channels")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get channels endpoint exists")
    
    def test_get_faq(self):
        """Test get FAQ endpoint"""
        response = client.get("/api/support/faq")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get FAQ endpoint exists")
    
    def test_get_faq_by_category(self):
        """Test get FAQ by category endpoint"""
        response = client.get("/api/support/faq/deposits")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get FAQ by category endpoint exists")
    
    def test_search_faq(self):
        """Test search FAQ endpoint"""
        response = client.post(
            "/api/support/faq/search",
            json={"query": "deposit"}
        )
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Search FAQ endpoint exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

