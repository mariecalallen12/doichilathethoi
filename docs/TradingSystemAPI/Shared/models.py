#!/usr/bin/env python3
"""
Shared Data Models for Trading System API
========================================

Common data structures and models used across the system
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

class SignalType(Enum):
    """Trading signal types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    UP = "UP"
    DOWN = "DOWN"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class AssetClass(Enum):
    """Asset class types"""
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    METALS = "METALS"
    COMMODITIES = "COMMODITIES"

class TimeFrame(Enum):
    """Trading timeframes"""
    ONE_MINUTE = "1M"
    FIVE_MINUTES = "5M"
    FIFTEEN_MINUTES = "15M"
    ONE_HOUR = "1H"
    FOUR_HOURS = "4H"
    ONE_DAY = "1D"

@dataclass
class PriceData:
    """Basic price data structure"""
    symbol: str
    asset_class: AssetClass
    price: float
    change_24h: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: str = ""
    source: str = ""

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    asset_class: AssetClass
    current_price: float
    price_change_24h: float
    signal: SignalType
    signal_strength: float  # 0-100
    confidence: float  # 0-100
    entry_price: float
    target_price: float
    stop_loss: float
    timeframe: str
    timestamp: str
    volume: Optional[float] = None
    market_cap: Optional[float] = None

@dataclass
class MarketSummary:
    """Market overview summary"""
    total_signals: int
    bullish_signals: int
    bearish_signals: int
    market_sentiment: str
    average_change_24h: float
    strongest_signal: str
    most_confident: str
    timestamp: str

@dataclass
class ApiResponse:
    """Standard API response format"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: str = ""
    error_code: Optional[str] = None

@dataclass
class Configuration:
    """System configuration"""
    # API Settings
    binance_base_url: str = "https://data-api.binance.vision"
    forex_base_url: str = "https://api.exchangerate-api.com/v4/latest"
    metals_base_url: str = "https://api.metals-api.com/v1"
    
    # Rate Limits
    binance_rate_limit: float = 0.1  # seconds
    forex_rate_limit: float = 1.0
    metals_rate_limit: float = 10.0
    
    # Cache Settings
    cache_ttl: int = 30  # seconds
    
    # Trading Parameters
    signal_thresholds: Dict[str, float] = None
    confidence_factors: Dict[str, float] = None
    
    def __post_init__(self):
        if self.signal_thresholds is None:
            self.signal_thresholds = {
                "weak": 0.5,
                "moderate": 1.0,
                "strong": 2.0,
                "extreme": 5.0
            }
        
        if self.confidence_factors is None:
            self.confidence_factors = {
                "base": 50.0,
                "high_volume": 20.0,
                "strong_move": 15.0,
                "high_price": 10.0
            }

# Global configuration instance
config = Configuration()