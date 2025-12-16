"""
Services Module
Digital Utopia Platform

Business logic services sử dụng database
"""

from .user_service import UserService
# from .trading_service import TradingService  # Removed - service doesn't exist
from .financial_service import FinancialService
from .cache_service import CacheService
from .compliance_service import ComplianceService
from .admin_service import AdminService
from .portfolio_service import PortfolioService
from .referral_service import ReferralService

__all__ = [
    "UserService",
    # "TradingService",  # Removed - service doesn't exist
    "FinancialService",
    "CacheService",
    "ComplianceService",
    "AdminService",
    "PortfolioService",
    "ReferralService"
]
