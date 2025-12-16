"""
Analysis module endpoints for FastAPI.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...dependencies import get_current_user
from ...db.session import get_db
from ...models.user import User
from ...schemas.analysis import (
    TechnicalAnalysisRequest, TechnicalAnalysisResponse,
    FundamentalAnalysisRequest, FundamentalAnalysisResponse,
    SentimentRequest, SentimentResponse, SentimentData,
    SignalsRequest, SignalsResponse, TradingSignal,
    BacktestRequest, BacktestResponse, BacktestResult,
    ApiResponse, ApiError
)
from ...services.analysis_service import AnalysisService

router = APIRouter()


# ========== Technical Analysis Endpoints ==========

@router.get("/technical/{symbol}", response_model=TechnicalAnalysisResponse)
async def get_technical_analysis(
    symbol: str = Path(..., description="Trading symbol"),
    timeframe: str = Query("1d", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w"),
    indicators: Optional[str] = Query(None, description="Comma-separated list of indicators"),
    db: Session = Depends(get_db)
):
    """Get technical analysis for symbol"""
    try:
        service = AnalysisService(db)
        
        indicator_list = None
        if indicators:
            indicator_list = [i.strip() for i in indicators.split(",")]
        
        result = service.get_technical_analysis(
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicator_list
        )
        
        return TechnicalAnalysisResponse(
            success=True,
            data=result,
            metadata={"symbol": symbol, "timeframe": timeframe}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching technical analysis: {str(e)}"
        )


# ========== Fundamental Analysis Endpoints ==========

@router.get("/fundamental/{symbol}", response_model=FundamentalAnalysisResponse)
async def get_fundamental_analysis(
    symbol: str = Path(..., description="Trading symbol"),
    db: Session = Depends(get_db)
):
    """Get fundamental analysis for symbol"""
    try:
        service = AnalysisService(db)
        result = service.get_fundamental_analysis(symbol=symbol)
        
        return FundamentalAnalysisResponse(
            success=True,
            data=result,
            metadata={"symbol": symbol}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching fundamental analysis: {str(e)}"
        )


# ========== Sentiment Endpoints ==========

@router.get("/sentiment", response_model=SentimentResponse)
async def get_sentiment(
    symbol: Optional[str] = Query(None, description="Trading symbol"),
    timeframe: str = Query("24h", description="Timeframe for sentiment analysis"),
    db: Session = Depends(get_db)
):
    """Get market sentiment"""
    try:
        service = AnalysisService(db)
        result = service.get_sentiment(symbol=symbol, timeframe=timeframe)
        
        sentiment_data = SentimentData(**result)
        
        return SentimentResponse(
            success=True,
            data=sentiment_data,
            metadata={"timeframe": timeframe}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching sentiment: {str(e)}"
        )


# ========== Signals Endpoints ==========

@router.get("/signals", response_model=SignalsResponse)
async def get_signals(
    symbol: Optional[str] = Query(None, description="Trading symbol"),
    timeframe: str = Query("1d", description="Timeframe"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trading signals"""
    try:
        service = AnalysisService(db)
        signals = service.get_signals(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        signal_objects = [TradingSignal(**s) for s in signals]
        
        return SignalsResponse(
            success=True,
            data=signal_objects,
            total=len(signal_objects),
            metadata={"timeframe": timeframe}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching signals: {str(e)}"
        )


# ========== Backtest Endpoints ==========

@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run backtest for trading strategy"""
    try:
        service = AnalysisService(db)
        result = service.run_backtest(
            symbol=request.symbol,
            strategy=request.strategy,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_balance=request.initial_balance,
            parameters=request.parameters
        )
        
        backtest_result = BacktestResult(**result)
        
        return BacktestResponse(
            success=True,
            data=backtest_result,
            metadata={"created_at": datetime.utcnow()}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running backtest: {str(e)}"
        )

