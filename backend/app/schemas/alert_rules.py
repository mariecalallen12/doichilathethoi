"""
Alert Rules Schemas
Digital Utopia Platform

Pydantic schemas cho Alert Rules API endpoints
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class AlertSeverity(str, Enum):
    """Mức độ nghiêm trọng của alert"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    """Loại notification"""
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"


class AlertRuleBase(BaseModel):
    """Base schema cho Alert Rule"""
    name: str = Field(..., min_length=1, max_length=200, description="Tên của alert rule")
    description: Optional[str] = Field(None, description="Mô tả rule")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Điều kiện để trigger alert")
    thresholds: Dict[str, Any] = Field(default_factory=dict, description="Ngưỡng để trigger alert")
    actions: Dict[str, Any] = Field(default_factory=dict, description="Actions khi alert được trigger")
    enabled: bool = Field(default=True, description="Rule có được bật không")
    priority: int = Field(default=5, ge=1, le=10, description="Độ ưu tiên (1-10)")


class AlertRuleCreate(AlertRuleBase):
    """Schema để tạo alert rule mới"""
    user_id: Optional[int] = Field(None, description="ID của user (None cho system-wide rule)")


class AlertRuleUpdate(BaseModel):
    """Schema để update alert rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    thresholds: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)


class AlertRuleResponse(AlertRuleBase):
    """Schema response cho Alert Rule"""
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    """Schema response cho Alert History"""
    id: int
    alert_rule_id: int
    user_id: Optional[int]
    triggered_at: datetime
    conditions_met: Dict[str, Any]
    actions_taken: Optional[Dict[str, Any]]
    resolved_at: Optional[datetime]
    acknowledged_by: Optional[int]
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlertRuleListResponse(BaseModel):
    """Schema response cho list of alert rules"""
    rules: List[AlertRuleResponse]
    total: int
    page: int
    page_size: int


class AlertHistoryListResponse(BaseModel):
    """Schema response cho list of alert history"""
    alerts: List[AlertHistoryResponse]
    total: int
    page: int
    page_size: int

