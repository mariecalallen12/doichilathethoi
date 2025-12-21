#!/usr/bin/env python3
"""
Trading System API - Main Server
================================

Main server that runs both MarketData and TradingFeatures APIs
"""

import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import API modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MarketData.api import market_app
from TradingFeatures.api import trading_app
from Shared.models import ApiResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Main API application
main_app = FastAPI(
    title="Trading System API",
    description="Comprehensive trading system with market data and trading features",
    version="1.0.0"
)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
main_app.include_router(market_app, prefix="/market", tags=["Market Data"])
main_app.include_router(trading_app, prefix="/trading", tags=["Trading Features"])

@main_app.get("/", response_model=ApiResponse)
async def root():
    """Main API information"""
    return ApiResponse(
        success=True,
        data={
            "service": "Trading System API",
            "version": "1.0.0",
            "description": "Dual-stream trading system API",
            "architecture": {
                "stream_1": "Market Data - Real-time market information display",
                "stream_2": "Trading Features - Binary signals and trading recommendations"
            },
            "modules": {
                "Market Data API": "/market",
                "Trading Features API": "/trading"
            },
            "endpoints": {
                "Market Data": {
                    "base": "/market",
                    "endpoints": ["/prices", "/overview", "/summary", "/health"]
                },
                "Trading Features": {
                    "base": "/trading", 
                    "endpoints": ["/signals", "/binary", "/analysis", "/health"]
                }
            },
            "features": {
                "real_time_data": "Live market data from Binance, Forex, Metals APIs",
                "binary_signals": "1=BULLISH, 0=BEARISH trading signals",
                "multi_asset": "Crypto, Forex, Metals coverage",
                "free_tier": "100% free APIs with no authentication required"
            }
        },
        message="Trading System API is operational",
        timestamp=datetime.now().isoformat()
    )

@main_app.get("/health", response_model=ApiResponse)
async def main_health_check():
    """Main health check"""
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "Trading System API",
            "timestamp": datetime.now().isoformat(),
            "modules": {
                "market_data": "operational",
                "trading_features": "operational"
            },
            "architecture": "dual-stream",
            "version": "1.0.0"
        },
        message="Trading System API is healthy",
        timestamp=datetime.now().isoformat()
    )

@main_app.get("/docs")
async def api_docs():
    """Redirect to API documentation"""
    return {
        "message": "API Documentation available at:",
        "market_data_docs": "/market/docs",
        "trading_features_docs": "/trading/docs",
        "swagger_ui": "/market/docs or /trading/docs"
    }

@main_app.get("/status")
async def system_status():
    """Detailed system status"""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": "Trading System API",
        "status": "operational",
        "streams": {
            "stream_1_market_data": {
                "name": "Market Data Display",
                "path": "/market",
                "status": "active",
                "description": "Real-time market information and price display",
                "endpoints": {
                    "all_prices": "/market/prices",
                    "market_overview": "/market/overview", 
                    "market_summary": "/market/summary",
                    "supported_symbols": "/market/supported-symbols"
                }
            },
            "stream_2_trading_features": {
                "name": "Trading Features",
                "path": "/trading",
                "status": "active", 
                "description": "Binary trading signals and analysis",
                "endpoints": {
                    "trading_signals": "/trading/signals",
                    "binary_array": "/trading/binary",
                    "market_analysis": "/trading/analysis",
                    "recommendations": "/trading/recommendations"
                }
            }
        },
        "data_sources": {
            "binance": "https://data-api.binance.vision",
            "forex": "https://api.exchangerate-api.com",
            "metals": "https://api.metals-api.com"
        },
        "architecture": {
            "dual_stream": "Market Data (Display) + Trading Features (Signals)",
            "real_time": "Live data updates < 1 second",
            "free_tier": "No authentication required",
            "binary_format": "1=BULLISH, 0=BEARISH"
        }
    }

if __name__ == "__main__":
    print("🚀 Trading System API - Dual Stream Architecture")
    print("=" * 60)
    print("📊 Stream 1: Market Data API - /market")
    print("🎯 Stream 2: Trading Features API - /trading")
    print("=" * 60)
    print("🌐 Main API: http://0.0.0.0:8000")
    print("📊 Market Docs: http://0.0.0.0:8000/market/docs")
    print("🎯 Trading Docs: http://0.0.0.0:8000/trading/docs")
    print("🔗 Status: http://0.0.0.0:8000/status")
    print("=" * 60)
    print("✅ Architecture: Dual Stream Ready")
    print("📡 Data Sources: Binance + Forex + Metals")
    print("🔢 Binary Signals: 1=BULLISH, 0=BEARISH")
    print("💰 Cost: 100% FREE")
    print("=" * 60)
    
    uvicorn.run(
        main_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )