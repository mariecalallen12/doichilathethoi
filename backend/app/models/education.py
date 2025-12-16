"""
Education Models
Digital Utopia Platform

Models cho Education module: Videos, Ebooks, Economic Calendar, Market Reports, Progress
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, DECIMAL, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base, TimestampMixin


class EducationVideo(Base, TimestampMixin):
    """
    Bảng education_videos - Video tutorials
    
    Lưu trữ thông tin video hướng dẫn trading
    """
    __tablename__ = "education_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)  # beginner, intermediate, advanced
    tags = Column(JSONB, default=[])  # Array of tags
    language = Column(String(10), default="en", index=True)
    
    # Metadata
    author = Column(String(255), nullable=True)
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), nullable=True)  # 0.00 to 5.00
    
    # Status
    is_published = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships - removed to avoid FK issues with polymorphic progress
    # Progress can be queried separately using item_type and item_id
    
    def __repr__(self):
        return f"<EducationVideo(id={self.id}, title={self.title})>"


class EducationEbook(Base, TimestampMixin):
    """
    Bảng education_ebooks - Ebooks
    
    Lưu trữ thông tin sách điện tử về trading
    """
    __tablename__ = "education_ebooks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    page_count = Column(Integer, nullable=True)
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSONB, default=[])
    language = Column(String(10), default="en", index=True)
    
    # Metadata
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    isbn = Column(String(50), nullable=True)
    download_count = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), nullable=True)  # 0.00 to 5.00
    
    # Status
    is_published = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships - removed to avoid FK issues with polymorphic progress
    # Progress can be queried separately using item_type and item_id
    
    def __repr__(self):
        return f"<EducationEbook(id={self.id}, title={self.title})>"


class EconomicCalendar(Base, TimestampMixin):
    """
    Bảng economic_calendar - Economic calendar events
    
    Lưu trữ các sự kiện kinh tế quan trọng
    """
    __tablename__ = "economic_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    country = Column(String(100), nullable=False, index=True)
    currency = Column(String(10), nullable=True, index=True)
    
    # Timing
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    timezone = Column(String(50), default="UTC")
    
    # Impact
    impact = Column(String(20), nullable=True, index=True)  # low, medium, high
    previous_value = Column(String(100), nullable=True)
    forecast_value = Column(String(100), nullable=True)
    actual_value = Column(String(100), nullable=True)
    
    # Category
    category = Column(String(100), nullable=True, index=True)  # employment, inflation, gdp, etc.
    
    # Status
    is_published = Column(Boolean, default=True, index=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_economic_calendar_date_country', 'event_date', 'country'),
    )
    
    def __repr__(self):
        return f"<EconomicCalendar(id={self.id}, title={self.title}, date={self.event_date})>"


class MarketReport(Base, TimestampMixin):
    """
    Bảng market_reports - Market analysis reports
    
    Lưu trữ các báo cáo phân tích thị trường
    """
    __tablename__ = "market_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)
    file_url = Column(String(500), nullable=True)
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)  # daily, weekly, monthly, special
    tags = Column(JSONB, default=[])
    language = Column(String(10), default="en", index=True)
    
    # Report period
    report_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    author = Column(String(255), nullable=True)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    
    # Status
    is_published = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    sort_order = Column(Integer, default=0, index=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships - removed to avoid FK issues with polymorphic progress
    # Progress can be queried separately using item_type and item_id
    
    def __repr__(self):
        return f"<MarketReport(id={self.id}, title={self.title})>"


class EducationProgress(Base, TimestampMixin):
    """
    Bảng education_progress - User progress tracking
    
    Theo dõi tiến độ học tập của người dùng
    """
    __tablename__ = "education_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Item reference (polymorphic)
    item_type = Column(String(50), nullable=False, index=True)  # video, ebook, report
    item_id = Column(Integer, nullable=False, index=True)
    
    # Progress tracking
    progress_percent = Column(DECIMAL(5, 2), default=0.0)  # 0.00 to 100.00
    time_spent = Column(Integer, default=0)  # Time spent in seconds
    last_position = Column(String(100), nullable=True)  # Last position (for videos: timestamp, for ebooks: page)
    is_completed = Column(Boolean, default=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Ratings and feedback
    rating = Column(Integer, nullable=True)  # 1 to 5
    feedback = Column(Text, nullable=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", backref="education_progress")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_education_progress_user_item', 'user_id', 'item_type', 'item_id'),
    )
    
    def __repr__(self):
        return f"<EducationProgress(id={self.id}, user_id={self.user_id}, item_type={self.item_type}, progress={self.progress_percent}%)>"

