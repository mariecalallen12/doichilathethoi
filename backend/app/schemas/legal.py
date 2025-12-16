"""
Legal module schemas for FastAPI endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========== Terms of Service Schemas ==========

class TermsRequest(BaseModel):
    """Request model for terms of service"""
    version: Optional[str] = None


class TermsResponse(BaseModel):
    """Terms of service response model"""
    id: int
    version: str
    title: str
    content: str
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    is_current: bool = False
    changes_summary: Optional[str] = None
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class TermsListResponse(BaseModel):
    """Terms list response wrapper"""
    success: bool
    data: List[TermsResponse]
    current_version: Optional[str] = None
    metadata: Dict[str, Any] = {}


# ========== Privacy Policy Schemas ==========

class PrivacyRequest(BaseModel):
    """Request model for privacy policy"""
    version: Optional[str] = None


class PrivacyResponse(BaseModel):
    """Privacy policy response model"""
    id: int
    version: str
    title: str
    content: str
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    is_active: bool = True
    is_current: bool = False
    changes_summary: Optional[str] = None
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class PrivacyListResponse(BaseModel):
    """Privacy list response wrapper"""
    success: bool
    data: List[PrivacyResponse]
    current_version: Optional[str] = None
    metadata: Dict[str, Any] = {}


# ========== Risk Warning Schemas ==========

class RiskWarningResponse(BaseModel):
    """Risk warning response model"""
    id: int
    title: str
    content: str
    category: Optional[str] = None
    severity: str = "high"
    language: str = "en"
    is_active: bool = True
    is_current: bool = False
    show_on_registration: bool = True
    show_on_trading: bool = False
    require_acknowledgment: bool = True
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class RiskWarningListResponse(BaseModel):
    """Risk warning list response wrapper"""
    success: bool
    data: List[RiskWarningResponse]
    metadata: Dict[str, Any] = {}


# ========== Complaint Schemas ==========

class ComplaintSubmitRequest(BaseModel):
    """Request model for submitting complaint"""
    complaint_type: str = Field(..., description="Type: service, trading, financial, technical, other")
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    related_transaction_id: Optional[int] = None
    related_order_id: Optional[int] = None
    related_reference: Optional[str] = None
    priority: str = Field(default="normal")  # low, normal, high, urgent
    attachments: List[str] = []  # URLs or file paths


class ComplaintUpdateRequest(BaseModel):
    """Request model for updating complaint"""
    status: Optional[str] = None  # submitted, under_review, in_progress, resolved, closed, rejected
    resolution: Optional[str] = None
    user_satisfaction: Optional[str] = None  # satisfied, unsatisfied, neutral
    user_feedback: Optional[str] = None


class ComplaintResponse(BaseModel):
    """Complaint response model"""
    id: int
    user_id: int
    complaint_type: str
    subject: str
    description: str
    related_transaction_id: Optional[int] = None
    related_order_id: Optional[int] = None
    related_reference: Optional[str] = None
    priority: str
    status: str
    submitted_at: datetime
    assigned_to: Optional[int] = None
    assigned_at: Optional[datetime] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    user_satisfaction: Optional[str] = None
    user_feedback: Optional[str] = None
    attachments: List[str] = []
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class ComplaintListRequest(BaseModel):
    """Request model for listing complaints"""
    status: Optional[str] = None
    complaint_type: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ComplaintListResponse(BaseModel):
    """Complaint list response wrapper"""
    success: bool
    data: List[ComplaintResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


# ========== Generic Response Schemas ==========

class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool
    data: Any
    metadata: Dict[str, Any] = {}


class ApiError(BaseModel):
    """Generic API error response"""
    error: bool = True
    message: str
    status_code: int
    timestamp: str

