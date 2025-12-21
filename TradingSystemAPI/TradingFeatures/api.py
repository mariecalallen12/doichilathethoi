#!/usr/bin/env python3
"""
Trading Features API Endpoints
=============================

FastAPI endpoints for trading features and signals (Luồng 2)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Shared.models import AssetClass, ApiResponse, SignalType
from Shared.utils import data_formatter
from TradingFeatures.signals import TradingSignalsGenerator, BinarySignalsGenerator, TradingAnalysis

logger = logging.getLogger(__name__)

# Pydantic models for API
class TradingSignalResponse(BaseModel):
    symbol: str
    asset_class: str
    current_price: str
    price_change_24h: str
    signal: str
    signal_emoji: str
    signal_strength: str
    confidence: str
    entry_price: str
    target_price: str
    stop_loss: str
    recommendation: str
    timeframe: str
    timestamp: str

class BinarySignalResponse(BaseModel):
    symbol: str
    binary_code: str
    signal: str
    current_price: str
    price_change_24h: str
    recommendation: str
    signal_strength: str
    confidence: str
    timestamp: str

class BinaryArrayResponse(BaseModel):
    timestamp: str
    total_signals: int
    bullish_signals: int
    bearish_signals: int
    market_sentiment: str
    binary_array: List[str]
    binary_string: str
    symbols: List[str]

class MarketAnalysisResponse(BaseModel):
    timestamp: str
    asset_class_analysis: Dict[str, Any]
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    high_confidence_signals: List[Dict[str, Any]]

# Initialize FastAPI app
trading_app = FastAPI(
    title="Trading System API - Trading Features",
    description="Binary trading signals and analysis",
    version="1.0.0"
)

trading_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
signals_generator = TradingSignalsGenerator()
binary_generator = BinarySignalsGenerator()
analysis = TradingAnalysis()

def format_signal_response(signal) -> TradingSignalResponse:
    """Format TradingSignal for API response"""
    return TradingSignalResponse(
        symbol=signal.symbol,
        asset_class=signal.asset_class.value,
        current_price=data_formatter.format_price(signal.current_price, signal.symbol),
        price_change_24h=data_formatter.format_change(signal.price_change_24h),
        signal=signal.signal.value,
        signal_emoji=data_formatter.get_signal_emoji(signal.signal),
        signal_strength=f"{signal.signal_strength:.0f}%",
        confidence=f"{signal.confidence:.0f}%",
        entry_price=data_formatter.format_price(signal.entry_price, signal.symbol),
        target_price=data_formatter.format_price(signal.target_price, signal.symbol),
        stop_loss=data_formatter.format_price(signal.stop_loss, signal.symbol),
        recommendation="",  # Will be filled by binary generator
        timeframe=signal.timeframe,
        timestamp=signal.timestamp
    )

@trading_app.get("/", response_model=ApiResponse)
async def trading_features_info():
    """Trading features API information"""
    return ApiResponse(
        success=True,
        data={
            "service": "Trading Features API",
            "version": "1.0.0",
            "description": "Binary trading signals and analysis",
            "endpoints": {
                "/signals": "Get all trading signals",
                "/binary": "Get binary signals array",
                "/binary/{symbol}": "Get binary signal for symbol",
                "/analysis": "Get market analysis",
                "/analysis/trends": "Get trend analysis",
                "/health": "Health check"
            },
            "binary_meaning": {
                "1": "BULLISH - UP/BUY signal",
                "0": "BEARISH - DOWN/SELL signal"
            },
            "signal_types": [signal.value for signal in SignalType]
        },
        message="Trading Features API is operational",
        timestamp=datetime.now().isoformat()
    )

@trading_app.get("/health", response_model=ApiResponse)
async def trading_health_check():
    """Health check for trading features service"""
    return ApiResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "Trading Features API",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "signals": "operational",
                "binary": "operational",
                "analysis": "operational"
            }
        },
        message="Trading Features API is healthy",
        timestamp=datetime.now().isoformat()
    )

@trading_app.get("/signals", response_model=Dict[str, TradingSignalResponse])
async def get_all_trading_signals():
    """Get all trading signals"""
    try:
        signals = await signals_generator.generate_all_signals()
        
        if not signals:
            raise HTTPException(status_code=503, detail="No trading signals available")
        
        return {symbol: format_signal_response(signal) for symbol, signal in signals.items()}
    
    except Exception as e:
        logger.error(f"Error getting trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/signals/{symbol}", response_model=TradingSignalResponse)
async def get_trading_signal(symbol: str):
    """Get trading signal for specific symbol"""
    try:
        symbol = symbol.upper().strip()
        signals = await signals_generator.generate_all_signals()
        
        if symbol not in signals:
            raise HTTPException(status_code=404, detail=f"No signal found for {symbol}")
        
        return format_signal_response(signals[symbol])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trading signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/signals/asset/{asset_class}", response_model=Dict[str, TradingSignalResponse])
async def get_signals_by_asset_class(asset_class: AssetClass):
    """Get trading signals filtered by asset class"""
    try:
        signals = await signals_generator.generate_signals_by_asset_class(asset_class)
        
        return {symbol: format_signal_response(signal) for symbol, signal in signals.items()}
    
    except Exception as e:
        logger.error(f"Error getting signals for {asset_class}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/binary", response_model=BinaryArrayResponse)
async def get_binary_signals():
    """Get binary signals array for all instruments"""
    try:
        binary_data = await binary_generator.generate_binary_signals()
        
        if "error" in binary_data:
            raise HTTPException(status_code=503, detail=binary_data["error"])
        
        return BinaryArrayResponse(
            timestamp=binary_data["timestamp"],
            total_signals=binary_data["total_signals"],
            bullish_signals=binary_data["summary"]["bullish_signals"],
            bearish_signals=binary_data["summary"]["bearish_signals"],
            market_sentiment=binary_data["summary"]["market_sentiment"],
            binary_array=binary_data["binary_array"],
            binary_string=binary_data["binary_string"],
            symbols=binary_data["symbols"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting binary signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/binary/{symbol}", response_model=BinarySignalResponse)
async def get_binary_signal(symbol: str):
    """Get binary signal for specific symbol"""
    try:
        symbol = symbol.upper().strip()
        binary_signal = await binary_generator.get_binary_for_symbol(symbol)
        
        if not binary_signal:
            raise HTTPException(status_code=404, detail=f"No binary signal found for {symbol}")
        
        return BinarySignalResponse(**binary_signal)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting binary signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/binary/stream")
async def get_binary_stream():
    """Get binary signals stream for real-time updates"""
    try:
        binary_data = await binary_generator.generate_binary_signals()
        
        if "error" in binary_data:
            raise HTTPException(status_code=503, detail=binary_data["error"])
        
        # Create simplified stream data
        stream_data = []
        for signal_data in binary_data["signals"]:
            stream_data.append({
                "symbol": signal_data["symbol"],
                "binary": signal_data["binary_code"],
                "price": signal_data["current_price"],
                "change": signal_data["price_change_24h"],
                "signal": signal_data["signal"],
                "confidence": signal_data["confidence"]
            })
        
        return {
            "timestamp": binary_data["timestamp"],
            "stream": stream_data,
            "market_binary": binary_data["binary_string"],
            "market_sentiment": binary_data["summary"]["market_sentiment"],
            "total_signals": binary_data["total_signals"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating binary stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis():
    """Get comprehensive market analysis"""
    try:
        analysis_data = await analysis.analyze_market_trends()
        
        if "error" in analysis_data:
            raise HTTPException(status_code=503, detail=analysis_data["error"])
        
        return MarketAnalysisResponse(**analysis_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/analysis/trends")
async def get_trend_analysis():
    """Get trend analysis data"""
    try:
        analysis_data = await analysis.analyze_market_trends()
        
        if "error" in analysis_data:
            raise HTTPException(status_code=503, detail=analysis_data["error"])
        
        return {
            "timestamp": analysis_data["timestamp"],
            "market_sentiment": "Based on current binary signals",
            "trend_summary": analysis_data["asset_class_analysis"],
            "top_movers": {
                "gainers": analysis_data["top_gainers"],
                "losers": analysis_data["top_losers"]
            },
            "confidence_analysis": analysis_data["high_confidence_signals"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/recommendations")
async def get_trading_recommendations():
    """Get current trading recommendations"""
    try:
        signals = await signals_generator.generate_all_signals()
        
        if not signals:
            raise HTTPException(status_code=503, detail="No signals available for recommendations")
        
        # Categorize recommendations
        strong_buy = []
        buy = []
        sell = []
        strong_sell = []
        
        for signal in signals.values():
            rec = {
                "symbol": signal.symbol,
                "asset_class": signal.asset_class.value,
                "current_price": data_formatter.format_price(signal.current_price, signal.symbol),
                "confidence": f"{signal.confidence:.0f}%",
                "target": data_formatter.format_price(signal.target_price, signal.symbol),
                "stop_loss": data_formatter.format_price(signal.stop_loss, signal.symbol)
            }
            
            if signal.signal == SignalType.STRONG_BUY:
                strong_buy.append(rec)
            elif signal.signal == SignalType.BUY:
                buy.append(rec)
            elif signal.signal == SignalType.SELL:
                sell.append(rec)
            elif signal.signal == SignalType.STRONG_SELL:
                strong_sell.append(rec)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "recommendations": {
                "strong_buy": strong_buy,
                "buy": buy,
                "sell": sell,
                "strong_sell": strong_sell
            },
            "summary": {
                "total_signals": len(signals),
                "bullish_count": len(strong_buy) + len(buy),
                "bearish_count": len(sell) + len(strong_sell)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trading recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trading_app.get("/performance")
async def get_signal_performance():
    """Get signal performance metrics"""
    try:
        signals = await signals_generator.generate_all_signals()
        
        if not signals:
            raise HTTPException(status_code=503, detail="No signals available for performance analysis")
        
        # Analyze signal distribution
        signal_distribution = {}
        confidence_distribution = {
            "high": 0,    # > 70%
            "medium": 0,  # 40-70%
            "low": 0      # < 40%
        }
        
        for signal in signals.values():
            # Count signal types
            signal_type = signal.signal.value
            signal_distribution[signal_type] = signal_distribution.get(signal_type, 0) + 1
            
            # Count confidence levels
            if signal.confidence > 70:
                confidence_distribution["high"] += 1
            elif signal.confidence > 40:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(signals),
            "signal_distribution": signal_distribution,
            "confidence_distribution": confidence_distribution,
            "average_confidence": sum(s.confidence for s in signals.values()) / len(signals),
            "average_strength": sum(s.signal_strength for s in signals.values()) / len(signals)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signal performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))