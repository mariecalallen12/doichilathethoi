"""
Education module schemas for FastAPI endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========== Video Schemas ==========

class VideoResponse(BaseModel):
    """Video response model"""
    id: int
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: str
    duration: Optional[int] = None
    category: Optional[str] = None
    tags: List[str] = []
    language: str = "en"
    author: Optional[str] = None
    views_count: int = 0
    likes_count: int = 0
    rating: Optional[float] = None
    is_published: bool = True
    is_featured: bool = False
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class VideoListRequest(BaseModel):
    """Request model for listing videos"""
    category: Optional[str] = None
    language: Optional[str] = None
    is_featured: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    search: Optional[str] = None


class VideoListResponse(BaseModel):
    """Video list response wrapper"""
    success: bool
    data: List[VideoResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


# ========== Ebook Schemas ==========

class EbookResponse(BaseModel):
    """Ebook response model"""
    id: int
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    file_url: str
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    category: Optional[str] = None
    tags: List[str] = []
    language: str = "en"
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    download_count: int = 0
    rating: Optional[float] = None
    is_published: bool = True
    is_featured: bool = False
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class EbookListRequest(BaseModel):
    """Request model for listing ebooks"""
    category: Optional[str] = None
    language: Optional[str] = None
    is_featured: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    search: Optional[str] = None


class EbookListResponse(BaseModel):
    """Ebook list response wrapper"""
    success: bool
    data: List[EbookResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


# ========== Calendar Schemas ==========

class CalendarEventResponse(BaseModel):
    """Economic calendar event response model"""
    id: int
    title: str
    description: Optional[str] = None
    country: str
    currency: Optional[str] = None
    event_date: datetime
    timezone: str = "UTC"
    impact: Optional[str] = None
    previous_value: Optional[str] = None
    forecast_value: Optional[str] = None
    actual_value: Optional[str] = None
    category: Optional[str] = None
    is_published: bool = True
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class CalendarRequest(BaseModel):
    """Request model for economic calendar"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class CalendarResponse(BaseModel):
    """Calendar response wrapper"""
    success: bool
    data: List[CalendarEventResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


# ========== Report Schemas ==========

class ReportResponse(BaseModel):
    """Market report response model"""
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_url: Optional[str] = None
    file_url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    language: str = "en"
    report_date: datetime
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    author: Optional[str] = None
    view_count: int = 0
    download_count: int = 0
    is_published: bool = True
    is_featured: bool = False
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class ReportListRequest(BaseModel):
    """Request model for listing reports"""
    category: Optional[str] = None
    language: Optional[str] = None
    is_featured: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    search: Optional[str] = None


class ReportListResponse(BaseModel):
    """Report list response wrapper"""
    success: bool
    data: List[ReportResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


# ========== Progress Schemas ==========

class ProgressUpdateRequest(BaseModel):
    """Request model for updating progress"""
    item_id: int = Field(..., description="ID of the item (video, ebook, or report)")
    item_type: str = Field(..., description="Type of item: video, ebook, or report")
    progress_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent: Optional[int] = Field(None, ge=0, description="Time spent in seconds")
    last_position: Optional[str] = None
    is_completed: Optional[bool] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None
    meta_data: Dict[str, Any] = {}


class ProgressResponse(BaseModel):
    """Progress response model"""
    id: int
    user_id: int
    item_type: str
    item_id: int
    progress_percent: float
    time_spent: int
    last_position: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


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

