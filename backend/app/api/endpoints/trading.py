"""
Trading Features Endpoints
Implements all trading signals, binary signals, analysis, and recommendations
Based on TradingSystemAPI/TradingFeatures
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.middleware.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.customization_engine import customization_engine
from app.services.trading_signals_service import (
    TradingSignalsService,
    BinarySignalsService,
    TradingAnalysisService
)

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Response Models
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
    volume: Optional[str] = None
    market_cap: Optional[str] = None

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

class RecommendationsResponse(BaseModel):
    timestamp: str
    recommendations: Dict[str, List[Dict[str, Any]]]
    summary: Dict[str, int]

# Service instances
signals_service = TradingSignalsService()
binary_service = BinarySignalsService()
analysis_service = TradingAnalysisService()

@router.get("/")
async def trading_info():
    """Trading API information"""
    return {
        "service": "Trading Features API",
        "version": "1.0.0",
        "description": "Binary trading signals, analysis, and recommendations",
        "endpoints": {
            "/signals": "Get all trading signals",
            "/signals/{symbol}": "Get signal for specific symbol",
            "/signals/asset/{asset_class}": "Get signals by asset class",
            "/binary": "Get binary signals array",
            "/binary/{symbol}": "Get binary signal for symbol",
            "/binary/stream": "Get binary stream for real-time",
            "/analysis": "Get comprehensive market analysis",
            "/analysis/trends": "Get trend analysis",
            "/recommendations": "Get trading recommendations",
            "/performance": "Get signal performance metrics",
            "/health": "Health check"
        },
        "binary_meaning": {
            "1": "BULLISH - UP/BUY signal",
            "0": "BEARISH - DOWN/SELL signal"
        },
        "signal_types": ["STRONG_BUY", "BUY", "UP", "DOWN", "SELL", "STRONG_SELL"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def trading_health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "Trading Features API",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "signals": "operational",
            "binary": "operational",
            "analysis": "operational"
        }
    }

@router.get("/signals", response_model=Dict[str, TradingSignalResponse])
async def get_all_signals(
    session_id: Optional[str] = Query(None, description="Session ID for customization"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all trading signals"""
    try:
        # Set session for customization
        if session_id:
            customization_engine.set_active_session(session_id)
        
        signals = await signals_service.generate_all_signals()
        
        if not signals:
            raise HTTPException(
                status_code=503,
                detail="No trading signals available"
            )
        
        return signals
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{symbol}", response_model=TradingSignalResponse)
async def get_signal(
    symbol: str,
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trading signal for specific symbol"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        signal = await signals_service.get_signal(symbol.upper())
        
        if not signal:
            raise HTTPException(
                status_code=404,
                detail=f"No signal found for {symbol}"
            )
        
        return signal
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/asset/{asset_class}")
async def get_signals_by_asset(
    asset_class: str,
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get signals filtered by asset class (crypto, forex, metals)"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        signals = await signals_service.get_signals_by_asset_class(asset_class.upper())
        
        return signals
    
    except Exception as e:
        logger.error(f"Error getting signals for {asset_class}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/binary", response_model=BinaryArrayResponse)
async def get_binary_signals(
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get binary signals array for all instruments"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        binary_data = await binary_service.generate_binary_signals()
        
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

@router.get("/binary/{symbol}", response_model=BinarySignalResponse)
async def get_binary_signal(
    symbol: str,
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get binary signal for specific symbol"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        binary_signal = await binary_service.get_binary_for_symbol(symbol.upper())
        
        if not binary_signal:
            raise HTTPException(
                status_code=404,
                detail=f"No binary signal found for {symbol}"
            )
        
        return BinarySignalResponse(**binary_signal)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting binary signal for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/binary/stream")
async def get_binary_stream(
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get binary signals stream for real-time updates"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        binary_data = await binary_service.generate_binary_signals()
        
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

@router.get("/analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive market analysis"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        analysis_data = await analysis_service.analyze_market_trends()
        
        if "error" in analysis_data:
            raise HTTPException(status_code=503, detail=analysis_data["error"])
        
        return MarketAnalysisResponse(**analysis_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/trends")
async def get_trend_analysis(
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trend analysis data"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        analysis_data = await analysis_service.analyze_market_trends()
        
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

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current trading recommendations"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        recommendations = await signals_service.get_recommendations()
        
        return RecommendationsResponse(**recommendations)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trading recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_signal_performance(
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get signal performance metrics"""
    try:
        if session_id:
            customization_engine.set_active_session(session_id)
        
        performance = await signals_service.get_performance_metrics()
        
        return performance
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signal performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
