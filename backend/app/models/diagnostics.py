"""
Diagnostics Models
Digital Utopia Platform

Models cho Trading Dashboard Diagnostic Reports
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base, TimestampMixin


class TradingDiagnosticReport(Base, TimestampMixin):
    """
    Model lưu trữ diagnostic reports từ Trading Dashboard
    
    Attributes:
        id: Primary key
        user_id: ID của user tạo report (nullable nếu chưa đăng nhập)
        url: URL của trang khi tạo report
        user_agent: User agent string
        auth_status: Trạng thái authentication (JSONB)
        api_status: Trạng thái API health (JSONB)
        ws_status: Trạng thái WebSocket (JSONB)
        component_status: Trạng thái các components (JSONB)
        errors: Danh sách errors (JSONB)
        warnings: Danh sách warnings (JSONB)
        recommendations: Khuyến nghị (JSONB)
        raw_data: Raw diagnostic data (JSONB)
        overall_health: Trạng thái tổng thể (healthy/degraded/unhealthy)
        sent_at: Thời gian gửi report (nullable)
    """
    
    __tablename__ = 'trading_diagnostic_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    url = Column(String(500), nullable=False)
    user_agent = Column(String(500), nullable=True)
    
    # Status fields (stored as JSONB for flexibility)
    auth_status = Column(JSONB, nullable=True)
    api_status = Column(JSONB, nullable=True)
    ws_status = Column(JSONB, nullable=True)
    component_status = Column(JSONB, nullable=True)
    
    # Errors and recommendations
    errors = Column(JSONB, nullable=True)
    warnings = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    
    # Raw diagnostic data
    raw_data = Column(JSONB, nullable=True)
    
    # Overall health status
    overall_health = Column(String(20), nullable=True, index=True)  # healthy, degraded, unhealthy
    
    # Metadata
    sent_at = Column(DateTime(timezone=True), nullable=True)
    collection_duration_ms = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<TradingDiagnosticReport(id={self.id}, user_id={self.user_id}, health={self.overall_health}, created_at={self.created_at})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'url': self.url,
            'user_agent': self.user_agent,
            'auth_status': self.auth_status,
            'api_status': self.api_status,
            'ws_status': self.ws_status,
            'component_status': self.component_status,
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'overall_health': self.overall_health,
            'collection_duration_ms': self.collection_duration_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
        }

