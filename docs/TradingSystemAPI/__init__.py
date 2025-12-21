# Trading System API - Root Module
"""
Trading System API - Dual Stream Architecture

Two-stream system:
- Stream 1: Market Data API (/market)
- Stream 2: Trading Features API (/trading)

Features:
- Real-time market data from multiple sources
- Binary trading signals (1=BULLISH, 0=BEARISH)
- Multi-asset support (Crypto, Forex, Metals)
- 100% free APIs
- Exchange-level accuracy
"""

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

# API modules
from .MarketData.api import market_app
from .TradingFeatures.api import trading_app
from .Shared.models import *

# Main application
from .main import main_app

__all__ = [
    "market_app",
    "trading_app", 
    "main_app",
    "__version__"
]