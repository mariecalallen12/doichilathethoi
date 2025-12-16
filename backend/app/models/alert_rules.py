"""
Alert Rules Models
Digital Utopia Platform

Models cho Alert Rules Configuration
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import enum

from .base import Base, TimestampMixin


class AlertSeverity(enum.Enum):
    """Mức độ nghiêm trọng của alert"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(enum.Enum):
    """Loại notification"""
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"  # Future


class AlertRule(Base, TimestampMixin):
    """
    Model cho Alert Rules Configuration
    
    Attributes:
        id: Primary key
        name: Tên của alert rule
        description: Mô tả rule
        user_id: ID của user tạo rule (nullable nếu là system-wide rule)
        conditions: Điều kiện để trigger alert (JSONB)
        thresholds: Ngưỡng để trigger alert (JSONB)
        actions: Actions khi alert được trigger (JSONB)
        enabled: Rule có được bật không
        priority: Độ ưu tiên (1-10)
    """
    
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    # Conditions (JSONB): health_status, api_errors, ws_disconnects, component_empty
    conditions = Column(JSONB, nullable=False, server_default='{}')
    
    # Thresholds (JSONB): error_count, duration_seconds, severity_level
    thresholds = Column(JSONB, nullable=False, server_default='{}')
    
    # Actions (JSONB): notification_types (array), webhook_url (optional)
    actions = Column(JSONB, nullable=False, server_default='{}')
    
    # Settings
    enabled = Column(Boolean, nullable=False, server_default='true', index=True)
    priority = Column(Integer, nullable=False, server_default='5')  # 1-10
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name={self.name}, enabled={self.enabled})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'conditions': self.conditions,
            'thresholds': self.thresholds,
            'actions': self.actions,
            'enabled': self.enabled,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AlertHistory(Base, TimestampMixin):
    """
    Model lưu lịch sử alerts đã được trigger
    
    Attributes:
        id: Primary key
        alert_rule_id: ID của alert rule đã trigger
        user_id: ID của user liên quan (nullable)
        triggered_at: Thời gian trigger
        conditions_met: Điều kiện đã được thỏa mãn (JSONB)
        actions_taken: Actions đã thực hiện (JSONB)
        resolved_at: Thời gian resolve (nullable)
        acknowledged_by: User ID đã acknowledge (nullable)
        severity: Mức độ nghiêm trọng
    """
    
    __tablename__ = 'alert_history'
    
    id = Column(Integer, primary_key=True, index=True)
    alert_rule_id = Column(Integer, ForeignKey('alert_rules.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    conditions_met = Column(JSONB, nullable=False)
    actions_taken = Column(JSONB, nullable=True)
    
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    
    def __repr__(self):
        return f"<AlertHistory(id={self.id}, rule_id={self.alert_rule_id}, triggered_at={self.triggered_at})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'alert_rule_id': self.alert_rule_id,
            'user_id': self.user_id,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'conditions_met': self.conditions_met,
            'actions_taken': self.actions_taken,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'acknowledged_by': self.acknowledged_by,
            'severity': self.severity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

