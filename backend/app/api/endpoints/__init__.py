"""
API Endpoints Package
Migration from Next.js API routes to FastAPI routers
"""

from .auth import router as auth_router
from .client import router as client_router
from .admin import router as admin_router
from .financial import router as financial_router
from .market import router as market_router
from .portfolio import router as portfolio_router
from .compliance import router as compliance_router
from .risk_management import router as risk_management_router
from .staff_referrals import router as staff_referrals_router
from .users import router as users_router
from .diagnostics import router as diagnostics_router
from .alert_rules import router as alert_rules_router
from .notifications import router as notifications_router
from .audit import router as audit_router
from .performance import router as performance_router
from .education import router as education_router
from .analysis import router as analysis_router
from .support import router as support_router
from .legal import router as legal_router

__all__ = [
    "auth_router",
    "client_router", 
    "admin_router",
    "financial_router",
    "market_router",
    "portfolio_router",
    "compliance_router",
    "risk_management_router",
    "staff_referrals_router",
    "users_router",
    "diagnostics_router",
    "alert_rules_router",
    "notifications_router",
    "audit_router",
    "performance_router",
    "education_router",
    "analysis_router",
    "support_router",
    "legal_router"
]
