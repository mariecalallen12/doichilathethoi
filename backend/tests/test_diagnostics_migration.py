"""
Test Diagnostics Migration
Verify that the migration creates the correct table structure
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.diagnostics import TradingDiagnosticReport


def test_table_exists(db: Session):
    """Test that trading_diagnostic_reports table exists"""
    inspector = inspect(db.bind)
    tables = inspector.get_table_names()
    assert 'trading_diagnostic_reports' in tables, "Table trading_diagnostic_reports should exist"


def test_table_columns(db: Session):
    """Test that all required columns exist"""
    inspector = inspect(db.bind)
    columns = [col['name'] for col in inspector.get_columns('trading_diagnostic_reports')]
    
    required_columns = [
        'id', 'user_id', 'url', 'user_agent',
        'auth_status', 'api_status', 'ws_status', 'component_status',
        'errors', 'warnings', 'recommendations', 'raw_data',
        'overall_health', 'sent_at', 'collection_duration_ms',
        'created_at', 'updated_at'
    ]
    
    for col in required_columns:
        assert col in columns, f"Column {col} should exist"


def test_table_indexes(db: Session):
    """Test that indexes are created"""
    inspector = inspect(db.bind)
    indexes = inspector.get_indexes('trading_diagnostic_reports')
    index_names = [idx['name'] for idx in indexes]
    
    # Check for important indexes
    assert any('user_id' in idx['name'] for idx in indexes), "Index on user_id should exist"
    assert any('overall_health' in idx['name'] for idx in indexes), "Index on overall_health should exist"
    assert any('created_at' in idx['name'] for idx in indexes), "Index on created_at should exist"


def test_foreign_key_constraint(db: Session):
    """Test that foreign key constraint exists"""
    inspector = inspect(db.bind)
    foreign_keys = inspector.get_foreign_keys('trading_diagnostic_reports')
    
    # Check for user_id foreign key
    user_fk = [fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']]
    assert len(user_fk) > 0, "Foreign key constraint on user_id should exist"
    assert user_fk[0]['referred_table'] == 'users', "Foreign key should reference users table"


def test_model_creation(db: Session):
    """Test that we can create a TradingDiagnosticReport instance"""
    report = TradingDiagnosticReport(
        url='https://example.com/trading',
        user_agent='Mozilla/5.0',
        overall_health='healthy',
        collection_duration_ms=100
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    assert report.id is not None, "Report should have an ID after creation"
    assert report.url == 'https://example.com/trading', "URL should be saved correctly"
    assert report.overall_health == 'healthy', "Overall health should be saved correctly"
    
    # Cleanup
    db.delete(report)
    db.commit()


def test_jsonb_columns(db: Session):
    """Test that JSONB columns can store complex data"""
    report = TradingDiagnosticReport(
        url='https://example.com/trading',
        auth_status={'hasToken': True, 'isExpired': False},
        api_status={'overallHealth': 'healthy', 'endpoints': {}},
        recommendations=[{'severity': 'high', 'issue': 'Test issue'}],
        raw_data={'test': 'data'}
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    assert report.auth_status == {'hasToken': True, 'isExpired': False}, "Auth status should be saved correctly"
    assert report.recommendations[0]['severity'] == 'high', "Recommendations should be saved correctly"
    
    # Cleanup
    db.delete(report)
    db.commit()


@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

