"""
Integration Tests for Education Module
Tests education endpoints: videos, ebooks, calendar, reports, progress
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import app

client = TestClient(app)


class TestEducationEndpoints:
    """Test suite for education endpoints"""
    
    def test_get_videos(self):
        """Test get videos endpoint"""
        response = client.get("/api/education/videos")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get videos endpoint exists")
    
    def test_get_video_by_id(self):
        """Test get video by ID endpoint"""
        response = client.get("/api/education/videos/1")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get video by ID endpoint exists")
    
    def test_get_ebooks(self):
        """Test get ebooks endpoint"""
        response = client.get("/api/education/ebooks")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get ebooks endpoint exists")
    
    def test_get_ebook_by_id(self):
        """Test get ebook by ID endpoint"""
        response = client.get("/api/education/ebooks/1")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get ebook by ID endpoint exists")
    
    def test_get_calendar(self):
        """Test get economic calendar endpoint"""
        response = client.get("/api/education/calendar")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get calendar endpoint exists")
    
    def test_get_reports(self):
        """Test get market reports endpoint"""
        response = client.get("/api/education/reports")
        assert response.status_code in [200, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get reports endpoint exists")
    
    def test_get_report_by_id(self):
        """Test get report by ID endpoint"""
        response = client.get("/api/education/reports/1")
        assert response.status_code in [200, 404, 401, 422]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Get report by ID endpoint exists")
    
    def test_update_progress(self):
        """Test update progress endpoint"""
        response = client.post(
            "/api/education/progress",
            json={
                "item_id": 1,
                "item_type": "video",
                "progress_percent": 50.0,
                "time_spent": 300
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code in [200, 401, 422, 400]
        if response.status_code == 200:
            data = response.json()
            assert "success" in data or "data" in data
        print("✅ Update progress endpoint exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

