"""
Integration tests for Diagnostics API endpoints
Tests: POST /api/diagnostics/trading-report, GET endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.models.base import Base
from app.models.user import User
from app.models.diagnostics import TradingDiagnosticReport
from app.core.security import get_password_hash
from main import app
from app.db.session import get_db

# Create test database (use SQLite to avoid external dependencies)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_diagnostics.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database tables"""
    Base.metadata.create_all(
        bind=engine,
        tables=[
            User.__table__,
            TradingDiagnosticReport.__table__,
        ],
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(
            bind=engine,
            tables=[
                User.__table__,
                TradingDiagnosticReport.__table__,
            ],
        )


@pytest.fixture(scope="function")
def client(db):
    """Create test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """Get auth token for test user"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    if response.status_code == 200:
        return response.json().get("access_token") or response.json().get("token")
    return None


def test_create_diagnostic_report_anonymous(client, db):
    """Test creating diagnostic report without authentication"""
    report_data = {
        "report": {
            "diagnostics": {
                "url": "https://example.com/trading",
                "userAgent": "Mozilla/5.0",
                "auth": {"hasToken": False},
                "api": {"overallHealth": "healthy"},
                "websocket": {"connected": True},
                "components": {},
                "recommendations": [],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    }
    
    response = client.post("/api/diagnostics/trading-report", json=report_data)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://example.com/trading"
    assert data["user_id"] is None  # Anonymous user
    assert data["overall_health"] == "healthy"


def test_create_diagnostic_report_authenticated(client, db, test_user, auth_token):
    """Test creating diagnostic report with authentication"""
    if not auth_token:
        pytest.skip("Auth token not available")
    
    report_data = {
        "report": {
            "diagnostics": {
                "url": "https://example.com/trading",
                "userAgent": "Mozilla/5.0",
                "auth": {"hasToken": True, "userId": test_user.id},
                "api": {"overallHealth": "degraded"},
                "websocket": {"connected": False},
                "components": {"chart": {"isEmpty": True}},
                "recommendations": [
                    {"severity": "high", "issue": "Test issue", "solution": "Test solution"}
                ],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    }
    
    response = client.post(
        "/api/diagnostics/trading-report",
        json=report_data,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["overall_health"] == "degraded"


def test_get_diagnostic_reports_list(client, db, test_user, auth_token):
    """Test getting list of diagnostic reports"""
    # Create some test reports
    report1 = TradingDiagnosticReport(
        url="https://example.com/trading1",
        overall_health="healthy",
        user_id=test_user.id,
    )
    report2 = TradingDiagnosticReport(
        url="https://example.com/trading2",
        overall_health="unhealthy",
        user_id=None,  # Anonymous
    )
    db.add_all([report1, report2])
    db.commit()
    
    # Test without auth - should only see anonymous reports
    response = client.get("/api/diagnostics/trading-reports")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should only see anonymous report
    assert all(r["user_id"] is None for r in data)
    
    # Test with auth - should see own reports
    if auth_token:
        response = client.get(
            "/api/diagnostics/trading-reports",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should see own reports
        user_reports = [r for r in data if r["user_id"] == test_user.id]
        assert len(user_reports) > 0


def test_get_diagnostic_reports_with_filters(client, db, test_user, auth_token):
    """Test getting reports with filters"""
    # Create test reports with different health statuses
    report1 = TradingDiagnosticReport(
        url="https://example.com/trading1",
        overall_health="healthy",
        user_id=test_user.id,
    )
    report2 = TradingDiagnosticReport(
        url="https://example.com/trading2",
        overall_health="unhealthy",
        user_id=test_user.id,
    )
    db.add_all([report1, report2])
    db.commit()
    
    if not auth_token:
        pytest.skip("Auth token not available")
    
    # Filter by health
    response = client.get(
        "/api/diagnostics/trading-reports?health=healthy",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(r["overall_health"] == "healthy" for r in data)
    
    # Filter by user_id
    response = client.get(
        f"/api/diagnostics/trading-reports?user_id={test_user.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(r["user_id"] == test_user.id for r in data)


def test_get_diagnostic_report_by_id(client, db, test_user, auth_token):
    """Test getting a specific diagnostic report by ID"""
    report = TradingDiagnosticReport(
        url="https://example.com/trading",
        overall_health="healthy",
        user_id=test_user.id,
        auth_status={"hasToken": True},
        api_status={"overallHealth": "healthy"},
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Test without auth - should fail if report belongs to user
    response = client.get(f"/api/diagnostics/trading-reports/{report.id}")
    assert response.status_code == 403  # Forbidden
    
    # Test with auth - should succeed
    if auth_token:
        response = client.get(
            f"/api/diagnostics/trading-reports/{report.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report.id
        assert data["url"] == "https://example.com/trading"
        assert data["auth_status"] == {"hasToken": True}


def test_get_diagnostic_report_not_found(client, db):
    """Test getting non-existent report"""
    response = client.get("/api/diagnostics/trading-reports/99999")
    assert response.status_code == 404


def test_create_report_with_complex_data(client, db):
    """Test creating report with complex JSONB data"""
    report_data = {
        "report": {
            "diagnostics": {
                "url": "https://example.com/trading",
                "userAgent": "Mozilla/5.0",
                "auth": {
                    "hasToken": True,
                    "tokenType": "auth_token",
                    "isExpired": False,
                    "userId": 123,
                },
                "api": {
                    "overallHealth": "degraded",
                    "endpoints": {
                        "/api/trading/orders": {"status": 200, "ok": True},
                        "/api/trading/positions": {"status": 500, "ok": False},
                    },
                    "errors": [
                        {"endpoint": "/api/trading/positions", "status": 500}
                    ],
                },
                "websocket": {
                    "connected": False,
                    "error": "Connection timeout",
                    "reconnectAttempts": 3,
                },
                "components": {
                    "chart": {"isEmpty": True, "hasContent": False},
                    "orderBook": {"isEmpty": False, "hasContent": True},
                },
                "recommendations": [
                    {
                        "severity": "high",
                        "category": "api",
                        "issue": "API endpoint failed",
                        "solution": "Check backend server",
                    },
                    {
                        "severity": "medium",
                        "category": "websocket",
                        "issue": "WebSocket disconnected",
                        "solution": "Check WebSocket server",
                    },
                ],
                "collectionDuration": 150,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    }
    
    response = client.post("/api/diagnostics/trading-report", json=report_data)
    assert response.status_code == 201
    data = response.json()
    assert data["overall_health"] == "degraded"
    
    # Verify complex data is stored correctly
    report = db.query(TradingDiagnosticReport).filter_by(id=data["id"]).first()
    assert report is not None
    assert report.api_status["overallHealth"] == "degraded"
    assert len(report.recommendations) == 2
    assert report.recommendations[0]["severity"] == "high"


def test_pagination(client, db, test_user, auth_token):
    """Test pagination parameters"""
    # Create multiple reports
    for i in range(15):
        report = TradingDiagnosticReport(
            url=f"https://example.com/trading{i}",
            overall_health="healthy",
            user_id=test_user.id,
        )
        db.add(report)
    db.commit()
    
    if not auth_token:
        pytest.skip("Auth token not available")
    
    # Test pagination
    response = client.get(
        "/api/diagnostics/trading-reports?skip=0&limit=10",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10
    
    # Test skip
    response = client.get(
        "/api/diagnostics/trading-reports?skip=10&limit=10",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10

