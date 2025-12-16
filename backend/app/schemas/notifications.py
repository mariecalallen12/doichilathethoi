"""
Notifications Schemas
Digital Utopia Platform

Pydantic schemas cho Notifications API endpoints
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    """Base schema cho Notification"""
    type: str = Field(..., description="Loại notification (alert, info, warning, success)")
    category: str = Field(..., description="Category (diagnostic, trading, system, etc.)")
    severity: str = Field(..., description="Mức độ nghiêm trọng (low, medium, high, critical)")
    title: str = Field(..., min_length=1, max_length=200, description="Tiêu đề notification")
    message: str = Field(..., description="Nội dung notification")
    data: Optional[Dict[str, Any]] = Field(None, description="Dữ liệu bổ sung")
    link_url: Optional[str] = Field(None, max_length=500, description="URL để navigate khi click")
    expires_in_hours: Optional[int] = Field(None, ge=1, description="Số giờ để expire")


class NotificationCreate(NotificationBase):
    """Schema để tạo notification mới"""
    user_id: int = Field(..., description="ID của user nhận notification")


class NotificationResponse(NotificationBase):
    """Schema response cho Notification"""
    id: int
    user_id: int
    read_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    is_read: bool
    is_dismissed: bool
    is_expired: bool

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema response cho list of notifications"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationPreferenceBase(BaseModel):
    """Base schema cho Notification Preference"""
    category: str = Field(..., description="Category của notification")
    email_enabled: bool = Field(default=True, description="Cho phép email notifications")
    in_app_enabled: bool = Field(default=True, description="Cho phép in-app notifications")
    push_enabled: bool = Field(default=False, description="Cho phép push notifications")
    webhook_url: Optional[str] = Field(None, max_length=500, description="Webhook URL")


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema response cho Notification Preference"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema để update notification preference"""
    email_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    webhook_url: Optional[str] = Field(None, max_length=500)

