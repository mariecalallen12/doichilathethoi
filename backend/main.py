"""
CMEETRADING - FastAPI Backend
Main Application Entry Point

Migration from: Next.js 14.2.18 + React 18.2.0
Migration to: FastAPI + Vue.js 3 + TypeScript

Principle: Maintain 100% of existing functionality and content
Only change the implementation language and framework.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 CMEETRADING FastAPI Backend Starting...")
    
    # Initialize Redis connection
    try:
        from app.db.redis_client import init_redis
        redis_connected = init_redis()
        if redis_connected:
            logger.info("✅ Redis connection initialized successfully")
        else:
            logger.warning("⚠️  Redis connection failed, running without Redis cache")
    except Exception as e:
        logger.error(f"❌ Redis initialization error: {e}")
    
    # Initialize database connections
    try:
        from app.db.session import check_db_connection
        if check_db_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.warning("⚠️  Database connection check failed")
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")

    # Setup authentication
    # Load configuration
    
    yield
    
    # Shutdown
    logger.info("🛑 CMEETRADING FastAPI Backend Shutting Down...")
    
    # Close Redis connection
    try:
        from app.db.redis_client import redis_client
        redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")

    # Stop simulator
    try:
        sim = getattr(app.state, "trading_data_simulator", None)
        if sim:
            await sim.stop()
            logger.info("Trading data simulator stopped")
    except Exception as e:
        logger.error(f"Error stopping trading data simulator: {e}")

# Create FastAPI application
app = FastAPI(
    title="CMEETRADING API",
    description="""
    ## CMEETRADING - FastAPI Backend
    
    High-performance API backend migrated from Next.js to FastAPI.
    
    ### Features:
    - 🔐 **Authentication & Authorization**: JWT-based auth with role-based access control
    - 💰 **Financial Operations**: Deposits, withdrawals, currency exchange
    - 📊 **Market Data**: Real-time prices, historical data, market analysis
    - 💼 **Portfolio Management**: Portfolio tracking, analytics, rebalancing
    - 🛡️ **Compliance & Risk**: KYC/AML, risk assessment, compliance monitoring
    - 👥 **User Management**: Profile management, settings, preferences
    - 📱 **Admin Dashboard**: User management, analytics, system configuration
    
    ### API Modules:
    1. **Authentication** (`/api/auth`) - Login, register, token management
    2. **Client** (`/api/client`) - Dashboard, wallet, profile, settings
    3. **Admin** (`/api/admin`) - User management, approvals, analytics
    4. **Financial** (`/api/financial`) - Deposits, withdrawals, exchange, reports
    5. **Market Data** (`/api/market`) - Prices, historical data, analysis
    6. **Portfolio** (`/api/portfolio`) - Portfolio management, analytics
    7. **Compliance** (`/api/compliance`) - KYC, AML, audit trails
    8. **Risk Management** (`/api/risk-management`) - Risk assessment, limits
    9. **Staff Referrals** (`/api/staff`) - Referral management
    10. **User Management** (`/api/users`) - User CRUD operations
    11. **Education** (`/api/education`) - Videos, ebooks, calendar, reports, progress tracking
    12. **Analysis** (`/api/analysis`) - Technical analysis, fundamental analysis, sentiment, signals, backtesting
    13. **Support** (`/api/support`) - Articles, categories, contact, offices, channels, FAQ
    14. **Legal** (`/api/legal`) - Terms of service, privacy policy, risk warning, complaints
    
    ### Authentication:
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    ### WebSocket:
    Real-time updates available at `/ws` endpoint for:
    - Order updates
    - Position updates
    - Price updates
    
    ### Rate Limiting:
    API requests are rate-limited to prevent abuse. Standard limits:
    - 60 requests per minute
    - 1000 requests per hour
    
    ### Error Responses:
    All errors follow a consistent format:
    ```json
    {
        "error": true,
        "message": "Error description",
        "status_code": 400,
        "timestamp": "2025-12-05T15:14:49Z"
    }
    ```
    """,
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "CMEETRADING Support",
        "email": "support@digitalutopia.com"
    },
    license_info={
        "name": "MIT License"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.digitalutopia.com",
            "description": "Production server"
        }
    ]
)

# CORS Middleware
from app.core.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("✅ Prometheus metrics enabled at /metrics")
except ImportError:
    logger.warning("⚠️  prometheus-fastapi-instrumentator not installed, metrics disabled")

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# GZip Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Logging Middleware
from app.middleware.logging import LoggingMiddleware
app.add_middleware(LoggingMiddleware)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint - maintains Next.js API structure"""
    return {
        "message": "CMEETRADING - FastAPI Backend",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint working", "status": "ok"}

@app.get("/api/health")
async def health_check():
    """
    Health Check Endpoint
    Migrated from: Next.js /api/health
    Maintains exact same response structure and functionality
    
    Returns 200 OK even in degraded mode to allow nginx to start.
    Health check tools can check the status field to determine actual health.
    """
    import time
    import psutil
    from fastapi import status
    from fastapi.responses import JSONResponse
    
    # Check database connection
    db_status = "unknown"
    db_connected = False
    try:
        from app.db.session import check_db_connection
        db_connected = check_db_connection()
        db_status = "connected" if db_connected else "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        db_connected = False
    
    # Check Redis connection
    redis_status = "unknown"
    redis_connected = False
    try:
        from app.db.redis_client import redis_client
        redis_connected = redis_client.is_connected
        redis_status = "connected" if redis_connected else "disconnected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
        redis_connected = False
    
    # Determine overall status
    # Return "ok" if at least database is connected (Redis is optional)
    overall_status = "ok" if db_connected else "degraded"
    
    # Always return 200 OK so health checks pass even in degraded mode
    # This allows nginx and other services to start
    response_data = {
        "status": overall_status,
        "service": "backend",
        "version": "2.0.0",
        "uptime": f"{time.time() - psutil.boot_time():.3f}s",
        "memory": {
            "rss": f"{psutil.virtual_memory().percent}%",
            "available": f"{psutil.virtual_memory().available / 1024 / 1024:.1f} MB"
        },
        "database": db_status,
        "redis": redis_status,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    }
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data
    )

# Import and register API routers
from app.api.endpoints import (
    auth,
    client,
    admin,
    financial,
    market,
    portfolio,
    compliance,
    risk_management,
    staff_referrals,
    users,
    diagnostics,
    alert_rules,
    notifications,
    audit,
    performance,
    education,
    analysis,
    support,
    legal,
)
from app.api.endpoints import admin_trading
from app.api.endpoints import opex_trading
from app.api.endpoints import opex_market
from app.api.websocket import websocket_endpoint

# Phase 1: Authentication endpoints (migrated from Next.js)
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

# Phase 1: Client endpoints (migrated from Next.js)
app.include_router(client.router, prefix="/api/client", tags=["client"])

# Phase 1: Admin endpoints (migrated from Next.js)
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Admin Trading endpoints (OPEX)
app.include_router(admin_trading.router, prefix="/api/admin", tags=["admin-trading"])

# Phase 1: Financial endpoints (migrated from Next.js)
app.include_router(financial.router, prefix="/api/financial", tags=["financial"])

# OPEX Market Data endpoints (register first to handle orderbook, trades, ticker)
app.include_router(opex_market.router, prefix="/api/market", tags=["market"])

# Phase 1: Market data endpoints (migrated from Next.js) - non-conflicting routes only
app.include_router(market.router, prefix="/api/market", tags=["market"])

# OPEX Trading endpoints
app.include_router(opex_trading.router, prefix="/api/trading", tags=["trading"])

# Phase 1: Portfolio endpoints (migrated from Next.js)
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])

# Phase 1: Compliance endpoints (migrated from Next.js)
app.include_router(compliance.router, prefix="/api/compliance", tags=["compliance"])

# Phase 1: Risk Management endpoints (migrated from Next.js)
app.include_router(risk_management.router, prefix="/api/risk-management", tags=["risk-management"])

# Phase 1: Staff Referral Management endpoints (migrated from Next.js)
app.include_router(staff_referrals.router, prefix="/api/staff", tags=["staff"])

# Phase 1: User Management endpoints (migrated from Next.js)
app.include_router(users.router, prefix="/api", tags=["users"])

# Diagnostics endpoints
app.include_router(diagnostics.router, prefix="/api/diagnostics", tags=["diagnostics"])

# Alert Rules endpoints
app.include_router(alert_rules.router, prefix="/api", tags=["alert-rules"])

# Notifications endpoints
app.include_router(notifications.router, prefix="/api", tags=["notifications"])

# Audit Log endpoints
app.include_router(audit.router, prefix="/api", tags=["audit"])

# Performance monitoring endpoints
app.include_router(performance.router, prefix="/api", tags=["performance"])

# Education endpoints
app.include_router(education.router, prefix="/api/education", tags=["education"])

# Analysis endpoints
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

# Support endpoints
app.include_router(support.router, prefix="/api/support", tags=["support"])

# Legal endpoints
app.include_router(legal.router, prefix="/api/legal", tags=["legal"])

# WebSocket endpoint for real-time updates
app.websocket("/ws")(websocket_endpoint)

# OPEX WebSocket endpoint
from app.api.websocket_opex import router as opex_websocket_router
app.include_router(opex_websocket_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global exception handler"""
    # Translate common English error messages to Vietnamese
    detail = exc.detail
    if detail == "Not Found" or detail == "Not found" or detail == "not found":
        detail = "Không tìm thấy tài nguyên yêu cầu"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": detail,
            "detail": detail,  # Keep detail field for frontend compatibility
            "status_code": exc.status_code,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
    )


from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler_starlette(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions (including 404)"""
    if exc.status_code == 404:
        # Custom 404 handler to return Vietnamese message
        return JSONResponse(
            status_code=404,
            content={
                "error": True,
                "message": f"Không tìm thấy tài nguyên: {request.url.path}",
                "detail": f"Không tìm thấy tài nguyên: {request.url.path}",
                "status_code": 404,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
        )
    # For other Starlette HTTP exceptions, translate and format
    detail = exc.detail
    if detail == "Not Found" or detail == "Not found" or detail == "not found":
        detail = "Không tìm thấy tài nguyên yêu cầu"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": detail,
            "detail": detail,
            "status_code": exc.status_code,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )