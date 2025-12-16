"""
Notifications Models
Digital Utopia Platform

Models cho Notifications System
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base, TimestampMixin


class Notification(Base, TimestampMixin):
    """
    Model cho Notifications
    
    Attributes:
        id: Primary key
        user_id: ID của user nhận notification
        type: Loại notification (alert, info, warning)
        category: Category (diagnostic, trading, system, etc.)
        severity: Mức độ nghiêm trọng (low, medium, high, critical)
        title: Tiêu đề notification
        message: Nội dung notification
        data: Dữ liệu bổ sung (JSONB)
        read_at: Thời gian đọc (nullable)
        dismissed_at: Thời gian dismiss (nullable)
        expires_at: Thời gian hết hạn (nullable)
        link_url: URL để navigate khi click (optional)
    """
    
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    type = Column(String(50), nullable=False, index=True)  # alert, info, warning, success
    category = Column(String(50), nullable=False, index=True)  # diagnostic, trading, system, financial
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB, nullable=True)  # Additional data (alert_rule_id, diagnostic_report_id, etc.)
    
    read_at = Column(DateTime(timezone=True), nullable=True, index=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    link_url = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, read={self.read_at is not None})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'category': self.category,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'link_url': self.link_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def is_read(self):
        """Check if notification is read"""
        return self.read_at is not None
    
    @property
    def is_dismissed(self):
        """Check if notification is dismissed"""
        return self.dismissed_at is not None
    
    @property
    def is_expired(self):
        """Check if notification is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class NotificationPreference(Base, TimestampMixin):
    """
    Model cho Notification Preferences của user
    
    Attributes:
        id: Primary key
        user_id: ID của user
        category: Category của notification
        email_enabled: Cho phép email notifications
        in_app_enabled: Cho phép in-app notifications
        push_enabled: Cho phép push notifications (future)
        webhook_url: Webhook URL (optional)
    """
    
    __tablename__ = 'notification_preferences'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    
    email_enabled = Column(Boolean, nullable=False, server_default='true')
    in_app_enabled = Column(Boolean, nullable=False, server_default='true')
    push_enabled = Column(Boolean, nullable=False, server_default='false')
    webhook_url = Column(String(500), nullable=True)
    
    # Unique constraint on user_id + category
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id}, category={self.category})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'email_enabled': self.email_enabled,
            'in_app_enabled': self.in_app_enabled,
            'push_enabled': self.push_enabled,
            'webhook_url': self.webhook_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

