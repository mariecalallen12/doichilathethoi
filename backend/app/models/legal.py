"""
Legal Models
Digital Utopia Platform

Models cho Legal module: Terms of Service, Privacy Policy, Risk Warning, Complaints
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base, TimestampMixin


class TermsOfService(Base, TimestampMixin):
    """
    Bảng terms_of_service - Terms of Service versions
    
    Lưu trữ các phiên bản Terms of Service
    """
    __tablename__ = "terms_of_service"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Version info
    version = Column(String(50), nullable=False, unique=True, index=True)  # e.g., "1.0", "2.0", "2024-01-01"
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Effective dates
    effective_date = Column(DateTime(timezone=True), nullable=False, index=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_current = Column(Boolean, default=False, index=True)  # Only one should be current
    
    # Metadata
    changes_summary = Column(Text, nullable=True)  # Summary of changes from previous version
    meta_data = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<TermsOfService(id={self.id}, version={self.version}, is_current={self.is_current})>"


class PrivacyPolicy(Base, TimestampMixin):
    """
    Bảng privacy_policy - Privacy Policy versions
    
    Lưu trữ các phiên bản Privacy Policy
    """
    __tablename__ = "privacy_policy"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Version info
    version = Column(String(50), nullable=False, unique=True, index=True)  # e.g., "1.0", "2.0", "2024-01-01"
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Effective dates
    effective_date = Column(DateTime(timezone=True), nullable=False, index=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_current = Column(Boolean, default=False, index=True)  # Only one should be current
    
    # Metadata
    changes_summary = Column(Text, nullable=True)  # Summary of changes from previous version
    meta_data = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<PrivacyPolicy(id={self.id}, version={self.version}, is_current={self.is_current})>"


class RiskWarning(Base, TimestampMixin):
    """
    Bảng risk_warning - Risk Warning content
    
    Lưu trữ nội dung cảnh báo rủi ro
    """
    __tablename__ = "risk_warning"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Categorization
    category = Column(String(100), nullable=True, index=True)  # general, trading, investment, etc.
    severity = Column(String(20), default="high", index=True)  # low, medium, high, critical
    
    # Language
    language = Column(String(10), default="en", index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_current = Column(Boolean, default=False, index=True)  # Only one should be current per language
    
    # Display settings
    show_on_registration = Column(Boolean, default=True)
    show_on_trading = Column(Boolean, default=False)
    require_acknowledgment = Column(Boolean, default=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    def __repr__(self):
        return f"<RiskWarning(id={self.id}, title={self.title}, severity={self.severity})>"


class Complaint(Base, TimestampMixin):
    """
    Bảng complaints - User complaints
    
    Lưu trữ các khiếu nại từ người dùng
    """
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Complaint info
    complaint_type = Column(String(50), nullable=False, index=True)  # service, trading, financial, technical, other
    subject = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Related transaction/order (if applicable)
    related_transaction_id = Column(Integer, nullable=True)
    related_order_id = Column(Integer, nullable=True)
    related_reference = Column(String(255), nullable=True)
    
    # Priority
    priority = Column(String(20), default="normal", index=True)  # low, normal, high, urgent
    
    # Status
    status = Column(String(50), default="submitted", index=True)  # submitted, under_review, in_progress, resolved, closed, rejected
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # User feedback
    user_satisfaction = Column(String(20), nullable=True)  # satisfied, unsatisfied, neutral
    user_feedback = Column(Text, nullable=True)
    
    # Attachments
    attachments = Column(JSONB, default=[])  # Array of file URLs/paths
    
    # Internal notes
    internal_notes = Column(Text, nullable=True)
    
    # Additional data
    meta_data = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="complaints")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_complaints_user_status', 'user_id', 'status'),
        Index('idx_complaints_type_status', 'complaint_type', 'status'),
    )
    
    def __repr__(self):
        return f"<Complaint(id={self.id}, user_id={self.user_id}, subject={self.subject}, status={self.status})>"

