#!/usr/bin/env python3
"""
Market Data API Endpoints
========================

FastAPI endpoints for market data display (Luồng 1)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Shared.models import AssetClass, ApiResponse, PriceData
from Shared.utils import data_formatter
from MarketData.providers import MarketDataAggregator

logger = logging.getLogger(__name__)

# Pydantic models for API
class PriceResponse(BaseModel):
    symbol: str
    asset_class: str
    current_price: str
    price_change_24h: str
    volume: Optional[str] = None
    high_24h: Optional[str] = None
    low_24h: Optional[str] = None
    timestamp: str
    source: str

class MarketOverviewResponse(BaseModel):
    timestamp: str
    total_instruments: int
    by_asset_class: Dict[str, int]
    market_stats: Dict[str, float]
    top_performers: Dict[str, Any]

class MarketSummaryResponse(BaseModel):
    timestamp: str
    market_data: Dict[str, PriceResponse]
    overview: MarketOverviewResponse

# Initialize APIRouter
market_app = APIRouter()

# Global aggregator instance
market_aggregator = MarketDataAggregator()

def format_price_response(price_data: PriceData) -> PriceResponse:
    """Format PriceData for API response"""
    return PriceResponse(
        symbol=price_data.symbol,
        asset_class=price_data.asset_class.value,
        current_price=data_formatter.format_price(price_data.price, price_data.symbol),
        price_change_24h=data_formatter.format_change(price_data.change_24h or 0),
        volume=f"{price_data.volume:,.0f}" if price_data.volume else None,
        high_24h=data_formatter.format_price(price_data.high_24h, price_data.symbol) if price_data.high_24h else None,
        low_24h=data_formatter.format_price(price_data.low_24h, price_data.symbol) if price_data.low_24h else None,
        timestamp=price_data.timestamp,
        source=price_data.source
    )

@market_app.get("/", response_model=ApiResponse)
async def market_data_info():
    """Market data API information"""
    return ApiResponse(
        success=True,
        data={
            "service": "Market Data API",
            "version": "1.0.0",
            "description": "Real-time market data and price information",
            "endpoints": {
                "/prices": "Get all current prices",
                "/prices/{symbol}": "Get price for specific symbol",
                "/prices/asset/{asset_class}": "Get prices by asset class",
                "/overview": "Get market overview",
                "/summary": "Get complete market summary",
                "/health": "Health check"
            },
            "asset_classes": [cls.value for cls in AssetClass],
            "supported_symbols": "Crypto, Forex, Metals"
        },
        message="Market Data API is operational",
        timestamp=datetime.now().isoformat()
    )

@market_app.get("/health", response_model=ApiResponse)
async def market_health_check():
    """Health check for market data service"""
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "Market Data API",
            "timestamp": datetime.now().isoformat(),
            "providers": {
                "binance": "connected",
                "forex": "connected", 
                "metals": "connected"
            }
        },
        message="Market Data API is healthy",
        timestamp=datetime.now().isoformat()
    )

@market_app.get("/prices", response_model=Dict[str, PriceResponse])
async def get_all_prices():
    """Get all current prices"""
    try:
        prices = await market_aggregator.get_all_prices()
        
        if not prices:
            raise HTTPException(status_code=503, detail="No market data available")
        
        return {symbol: format_price_response(price_data) for symbol, price_data in prices.items()}
    
    except Exception as e:
        logger.error(f"Error getting all prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@market_app.get("/prices/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str):
    """Get price for specific symbol"""
    try:
        symbol = symbol.upper().strip()
        
        # Try all providers
        all_prices = await market_aggregator.get_all_prices()
        
        if symbol not in all_prices:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return format_price_response(all_prices[symbol])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@market_app.get("/prices/asset/{asset_class}", response_model=Dict[str, PriceResponse])
async def get_prices_by_asset_class(asset_class: AssetClass):
    """Get prices filtered by asset class"""
    try:
        prices = await market_aggregator.get_prices_by_asset_class(asset_class)
        
        return {symbol: format_price_response(price_data) for symbol, price_data in prices.items()}
    
    except Exception as e:
        logger.error(f"Error getting prices for {asset_class}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@market_app.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    """Get market overview statistics"""
    try:
        summary = await market_aggregator.get_market_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=503, detail=summary["error"])
        
        return MarketOverviewResponse(
            timestamp=summary["timestamp"],
            total_instruments=summary["total_instruments"],
            by_asset_class=summary["by_asset_class"],
            market_stats=summary["market_stats"],
            top_performers=summary["top_performers"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@market_app.get("/summary", response_model=MarketSummaryResponse)
async def get_market_summary():
    """Get complete market summary with all prices and overview"""
    try:
        # Get both prices and overview
        prices_task = market_aggregator.get_all_prices()
        overview_task = market_aggregator.get_market_summary()
        
        prices, overview = await asyncio.gather(prices_task, overview_task)
        
        if "error" in overview:
            raise HTTPException(status_code=503, detail=overview["error"])
        
        # Format prices for response
        formatted_prices = {symbol: format_price_response(price_data) 
                          for symbol, price_data in prices.items()}
        
        return MarketSummaryResponse(
            timestamp=datetime.now().isoformat(),
            market_data=formatted_prices,
            overview=MarketOverviewResponse(
                timestamp=overview["timestamp"],
                total_instruments=overview["total_instruments"],
                by_asset_class=overview["by_asset_class"],
                market_stats=overview["market_stats"],
                top_performers=overview["top_performers"]
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@market_app.get("/supported-symbols")
async def get_supported_symbols():
    """Get list of supported symbols"""
    try:
        all_prices = await market_aggregator.get_all_prices()
        
        symbols_by_class = {
            "crypto": [],
            "forex": [],
            "metals": []
        }
        
        for symbol, price_data in all_prices.items():
            if price_data.asset_class == AssetClass.CRYPTO:
                symbols_by_class["crypto"].append(symbol)
            elif price_data.asset_class == AssetClass.FOREX:
                symbols_by_class["forex"].append(symbol)
            elif price_data.asset_class == AssetClass.METALS:
                symbols_by_class["metals"].append(symbol)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "supported_symbols": symbols_by_class,
            "total_count": len(all_prices)
        }
    
    except Exception as e:
        logger.error(f"Error getting supported symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@market_app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    from ..Shared.utils import cache_manager
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cache_size": cache_manager.size(),
        "cache_ttl": cache_manager.ttl,
        "status": "operational"
    }