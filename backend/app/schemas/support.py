"""
Support module schemas for FastAPI endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========== Article Schemas ==========

class ArticleResponse(BaseModel):
    """Support article response model"""
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    tags: List[str] = []
    language: str = "en"
    author: Optional[str] = None
    view_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    is_published: bool = True
    is_featured: bool = False
    is_pinned: bool = False
    related_article_ids: List[int] = []
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class ArticleListRequest(BaseModel):
    """Request model for listing articles"""
    category_id: Optional[int] = None
    language: Optional[str] = None
    is_featured: Optional[bool] = None
    is_pinned: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    search: Optional[str] = None


class ArticleListResponse(BaseModel):
    """Article list response wrapper"""
    success: bool
    data: List[ArticleResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


# ========== Category Schemas ==========

class CategoryResponse(BaseModel):
    """Support category response model"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0
    article_count: Optional[int] = None

    class Config:
        from_attributes = True
        orm_mode = True


class CategoryListResponse(BaseModel):
    """Category list response wrapper"""
    success: bool
    data: List[CategoryResponse]
    metadata: Dict[str, Any] = {}


# ========== Search Schemas ==========

class ArticleSearchRequest(BaseModel):
    """Request model for searching articles"""
    query: str = Field(..., min_length=1, description="Search query")
    category_id: Optional[int] = None
    language: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ArticleSearchResponse(BaseModel):
    """Article search response wrapper"""
    success: bool
    data: List[ArticleResponse]
    total: int
    query: str
    metadata: Dict[str, Any] = {}


# ========== Contact Schemas ==========

class ContactSubmitRequest(BaseModel):
    """Request model for submitting contact form"""
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., description="Email address")
    phone: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    contact_type: Optional[str] = None  # general, technical, billing, etc.
    priority: str = Field(default="normal")  # low, normal, high, urgent


class ContactResponse(BaseModel):
    """Contact submission response model"""
    id: int
    name: str
    email: str
    subject: str
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


# ========== Office Schemas ==========

class OfficeResponse(BaseModel):
    """Support office response model"""
    id: int
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    business_hours: Dict[str, Any] = {}
    timezone: str = "UTC"
    is_active: bool = True
    is_headquarters: bool = False

    class Config:
        from_attributes = True
        orm_mode = True


class OfficeListResponse(BaseModel):
    """Office list response wrapper"""
    success: bool
    data: List[OfficeResponse]
    metadata: Dict[str, Any] = {}


# ========== Channel Schemas ==========

class ChannelResponse(BaseModel):
    """Support channel response model"""
    id: int
    name: str
    type: str  # email, phone, chat, ticket, social
    description: Optional[str] = None
    icon: Optional[str] = None
    value: str  # email address, phone number, URL, etc.
    availability: Optional[str] = None
    is_active: bool = True
    is_primary: bool = False
    average_response_time: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True


class ChannelListResponse(BaseModel):
    """Channel list response wrapper"""
    success: bool
    data: List[ChannelResponse]
    metadata: Dict[str, Any] = {}


# ========== FAQ Schemas ==========

class FAQResponse(BaseModel):
    """FAQ response model"""
    id: int
    question: str
    answer: str
    category: Optional[str] = None
    tags: List[str] = []
    language: str = "en"
    view_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    is_published: bool = True
    is_featured: bool = False
    related_faq_ids: List[int] = []
    meta_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class FAQListRequest(BaseModel):
    """Request model for listing FAQ"""
    category: Optional[str] = None
    language: Optional[str] = None
    is_featured: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class FAQListResponse(BaseModel):
    """FAQ list response wrapper"""
    success: bool
    data: List[FAQResponse]
    total: int
    limit: int
    offset: int
    metadata: Dict[str, Any] = {}


class FAQSearchRequest(BaseModel):
    """Request model for searching FAQ"""
    query: str = Field(..., min_length=1, description="Search query")
    category: Optional[str] = None
    language: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class FAQSearchResponse(BaseModel):
    """FAQ search response wrapper"""
    success: bool
    data: List[FAQResponse]
    total: int
    query: str
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

