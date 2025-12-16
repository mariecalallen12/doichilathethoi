"""
Analysis module schemas for FastAPI endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ========== Technical Analysis Schemas ==========

class TechnicalAnalysisRequest(BaseModel):
    """Request model for technical analysis"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    timeframe: Optional[str] = Field(default="1d", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w")
    indicators: Optional[List[str]] = Field(default=None, description="List of indicators to include")


class IndicatorData(BaseModel):
    """Technical indicator data"""
    name: str
    value: float
    signal: Optional[str] = None  # buy, sell, hold
    metadata: Dict[str, Any] = {}


class TechnicalAnalysisResponse(BaseModel):
    """Technical analysis response model"""
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}


# ========== Fundamental Analysis Schemas ==========

class FundamentalAnalysisRequest(BaseModel):
    """Request model for fundamental analysis"""
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")


class FundamentalAnalysisResponse(BaseModel):
    """Fundamental analysis response model"""
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}


# ========== Sentiment Schemas ==========

class SentimentRequest(BaseModel):
    """Request model for sentiment analysis"""
    symbol: Optional[str] = None
    timeframe: Optional[str] = Field(default="24h", description="Timeframe for sentiment analysis")


class SentimentData(BaseModel):
    """Sentiment data"""
    symbol: Optional[str] = None
    sentiment_score: float  # -100 to 100
    bullish_percent: float
    bearish_percent: float
    neutral_percent: float
    sources: Dict[str, Any] = {}
    timestamp: datetime


class SentimentResponse(BaseModel):
    """Sentiment response wrapper"""
    success: bool
    data: SentimentData
    metadata: Dict[str, Any] = {}


# ========== Trading Signals Schemas ==========

class SignalsRequest(BaseModel):
    """Request model for trading signals"""
    symbol: Optional[str] = None
    timeframe: Optional[str] = Field(default="1d")
    limit: int = Field(default=10, ge=1, le=50)


class TradingSignal(BaseModel):
    """Trading signal model"""
    symbol: str
    signal_type: str  # buy, sell, hold
    strength: float  # 0.0 to 1.0
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    timeframe: str
    indicators: Dict[str, Any] = {}
    confidence: float  # 0.0 to 1.0
    timestamp: datetime


class SignalsResponse(BaseModel):
    """Signals response wrapper"""
    success: bool
    data: List[TradingSignal]
    total: int
    metadata: Dict[str, Any] = {}


# ========== Backtest Schemas ==========

class BacktestRequest(BaseModel):
    """Request model for backtest"""
    symbol: str = Field(..., description="Trading symbol")
    strategy: str = Field(..., description="Strategy name or ID")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_balance: float = Field(default=10000.0, ge=0.0)
    parameters: Dict[str, Any] = {}


class BacktestResult(BaseModel):
    """Backtest result model"""
    backtest_id: str
    symbol: str
    strategy: str
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_return: float
    total_return_percent: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: Optional[float] = None
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: Optional[float] = None
    trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class BacktestResponse(BaseModel):
    """Backtest response wrapper"""
    success: bool
    data: BacktestResult
    metadata: Dict[str, Any] = {}


# ========== Generic Response Schemas ==========

class ApiResponse(BaseModel):
    """Generic API response"""
    success: bool
    data: Any
    metadata: Dict[str, Any] = {}


class ApiError(BaseModel):
    """Generic API error response"""
    error: bool = True
    message: str
    status_code: int
    timestamp: str

