"""
SQLAlchemy Models Module
Digital Utopia Platform

Tất cả các model database theo schema thiết kế
"""

from .base import Base, TimestampMixin
from .user import User, UserProfile, Role, Permission, RolePermission, RefreshToken
from .financial import Transaction, WalletBalance, ExchangeRate, Invoice, Payment
from .compliance import KYCDocument, ComplianceEvent, RiskAssessment, AMLScreening
from .portfolio import TradingBot, Watchlist
from .referral import ReferralCode, ReferralRegistration
from .audit import AuditLog, AnalyticsEvent
from .market import MarketDataHistory, MarketPrice, MarketAnalysis
from .system import SystemSetting, ScheduledReport, TradingAdjustment
from .diagnostics import TradingDiagnosticReport
from .alert_rules import AlertRule, AlertHistory
from .notifications import Notification, NotificationPreference
from .education import EducationVideo, EducationEbook, EconomicCalendar, MarketReport, EducationProgress
from .support import (
    SupportArticle, SupportCategory, SupportContact, SupportOffice, 
    SupportChannel, FAQ, Conversation, ChatMessage
)
from .legal import TermsOfService, PrivacyPolicy, RiskWarning, Complaint

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    
    # User
    "User",
    "UserProfile", 
    "Role",
    "Permission",
    "RolePermission",
    "RefreshToken",
    
    # Financial
    "Transaction",
    "WalletBalance",
    "ExchangeRate",
    "Invoice",
    "Payment",
    
    # Compliance
    "KYCDocument",
    "ComplianceEvent",
    "RiskAssessment",
    "AMLScreening",
    
    # Portfolio
    "TradingBot",
    "Watchlist",
    
    # Referral
    "ReferralCode",
    "ReferralRegistration",
    
    # Audit
    "AuditLog",
    "AnalyticsEvent",
    
    # Market Data
    "MarketDataHistory",
    "MarketPrice",
    "MarketAnalysis",
    
    # System
    "SystemSetting",
    "ScheduledReport",
    "TradingAdjustment",
    
    # Diagnostics
    "TradingDiagnosticReport",
    
    # Alert Rules
    "AlertRule",
    "AlertHistory",
    
    # Notifications
    "Notification",
    "NotificationPreference",
    
    # Education
    "EducationVideo",
    "EducationEbook",
    "EconomicCalendar",
    "MarketReport",
    "EducationProgress",
    
    # Support
    "SupportArticle",
    "SupportCategory",
    "SupportContact",
    "SupportOffice",
    "SupportChannel",
    "FAQ",
    "Conversation",
    "ChatMessage",

    # Legal
    "TermsOfService",
    "PrivacyPolicy",
    "RiskWarning",
    "Complaint"
]

