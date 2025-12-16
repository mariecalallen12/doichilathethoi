"""
Support Models
Digital Utopia Platform

Models cho Support module: Articles, Categories, Contact, Offices, Channels, FAQ
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base, TimestampMixin


class SupportCategory(Base, TimestampMixin):
    """
    Bảng support_categories - Article categories
    
    Phân loại các bài viết hỗ trợ
    """
    __tablename__ = "support_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey("support_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Relationships
    parent = relationship("SupportCategory", remote_side=[id], backref="children")
    articles = relationship("SupportArticle", back_populates="category")
    
    def __repr__(self):
        return f"<SupportCategory(id={self.id}, name={self.name})>"


class SupportArticle(Base, TimestampMixin):
    """
    Bảng support_articles - Help articles
    
    Lưu trữ các bài viết hướng dẫn và hỗ trợ
    """
    __tablename__ = "support_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    
    # Categorization
    category_id = Column(Integer, ForeignKey("support_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    tags = Column(JSONB, default=[])
    language = Column(String(10), default="en", index=True)
    
    # Metadata
    author = Column(String(255), nullable=True)
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(JSONB, default=[])
    
    # Status
    is_published = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    is_pinned = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Related articles
    related_article_ids = Column(JSONB, default=[])
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships
    category = relationship("SupportCategory", back_populates="articles")
    
    # Indexes for full-text search
    __table_args__ = (
        Index('idx_support_articles_title_content', 'title', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<SupportArticle(id={self.id}, title={self.title})>"


class SupportContact(Base, TimestampMixin):
    """
    Bảng support_contacts - Contact form submissions
    
    Lưu trữ các yêu cầu liên hệ từ người dùng
    """
    __tablename__ = "support_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User reference (optional for anonymous contacts)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Contact info
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    subject = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Category
    contact_type = Column(String(50), nullable=True, index=True)  # general, technical, billing, etc.
    priority = Column(String(20), default="normal", index=True)  # low, normal, high, urgent
    
    # Status
    status = Column(String(50), default="pending", index=True)  # pending, in_progress, resolved, closed
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Response
    response = Column(Text, nullable=True)
    responded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="support_contacts")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    responder = relationship("User", foreign_keys=[responded_by])
    
    def __repr__(self):
        return f"<SupportContact(id={self.id}, email={self.email}, subject={self.subject})>"


class SupportOffice(Base, TimestampMixin):
    """
    Bảng support_offices - Office locations
    
    Lưu trữ thông tin các văn phòng hỗ trợ
    """
    __tablename__ = "support_offices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    postal_code = Column(String(20), nullable=True)
    
    # Contact info
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Location
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    
    # Business hours
    business_hours = Column(JSONB, default={})  # {monday: {open: "09:00", close: "17:00"}, ...}
    timezone = Column(String(50), default="UTC")
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_headquarters = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<SupportOffice(id={self.id}, name={self.name}, city={self.city})>"


class SupportChannel(Base, TimestampMixin):
    """
    Bảng support_channels - Support channels
    
    Lưu trữ thông tin các kênh hỗ trợ
    """
    __tablename__ = "support_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    name = Column(String(100), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False, index=True)  # email, phone, chat, ticket, social
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    
    # Contact info
    value = Column(String(255), nullable=False)  # email address, phone number, URL, etc.
    availability = Column(String(100), nullable=True)  # 24/7, business_hours, etc.
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_primary = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Response time
    average_response_time = Column(String(50), nullable=True)  # "1 hour", "24 hours", etc.
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<SupportChannel(id={self.id}, name={self.name}, type={self.type})>"


class FAQ(Base, TimestampMixin):
    """
    Bảng faq - Frequently Asked Questions
    
    Lưu trữ các câu hỏi thường gặp
    """
    __tablename__ = "faq"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    question = Column(String(500), nullable=False, index=True)
    answer = Column(Text, nullable=False)
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSONB, default=[])
    language = Column(String(10), default="en", index=True)
    
    # Metadata
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # Status
    is_published = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Related FAQs
    related_faq_ids = Column(JSONB, default=[])
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Indexes for search
    __table_args__ = (
        Index('idx_faq_question_answer', 'question', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, question={self.question[:50]}...)>"

