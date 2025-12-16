"""
System Models
Digital Utopia Platform

Models cho system settings và configuration
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class SystemSetting(Base, TimestampMixin):
    """
    Bảng system_settings - Cài đặt hệ thống
    
    Lưu trữ các cấu hình hệ thống dưới dạng key-value
    """
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)  # Cho phép client access không cần auth
    
    def __repr__(self):
        return f"<SystemSetting(key='{self.key}')>"


class ScheduledReport(Base, TimestampMixin):
    """
    Bảng scheduled_reports - Báo cáo đã lên lịch
    
    Lưu trữ các báo cáo được lên lịch tự động
    """
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Report details
    report_type = Column(String(100), nullable=False, index=True)  # daily_summary, weekly_analytics, monthly_report, financial_report, trading_report
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly
    
    # Status
    status = Column(String(50), default="pending", index=True)  # active, pending, paused
    
    # Schedule
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    config = Column(JSONB, default={})  # Email recipients, format, etc.
    
    def __repr__(self):
        return f"<ScheduledReport(id={self.id}, report_type={self.report_type}, status={self.status})>"


class TradingAdjustment(Base, TimestampMixin):
    """
    Bảng trading_adjustments - Điều chỉnh giao dịch
    
    Lưu trữ lịch sử các điều chỉnh giao dịch của admin
    """
    __tablename__ = "trading_adjustments"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    position_id = Column(Integer, ForeignKey("portfolio_positions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Adjustment details
    adjustment_type = Column(String(100), nullable=False, index=True)  # win_rate, position_override, reset_win_rate
    target_value = Column(String(255), nullable=True)  # JSON string or value
    previous_value = Column(String(255), nullable=True)
    
    # Result
    result = Column(Text, nullable=True)
    
    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id], backref="admin_adjustments")
    user = relationship("User", foreign_keys=[user_id], backref="user_adjustments")
    
    def __repr__(self):
        return f"<TradingAdjustment(id={self.id}, type={self.adjustment_type})>"

