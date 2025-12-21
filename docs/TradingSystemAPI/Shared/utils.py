#!/usr/bin/env python3
"""
Shared Utilities for Trading System API
=====================================

Common utility functions and helpers
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from .models import PriceData, TradingSignal, AssetClass, SignalType, config

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple cache manager for API responses"""
    
    def __init__(self, ttl: int = config.cache_ttl):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached values"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_call = {}
    
    async def wait(self, source: str) -> None:
        """Wait if necessary to respect rate limit"""
        now = time.time()
        if source in self.last_call:
            elapsed = now - self.last_call[source]
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        self.last_call[source] = time.time()

class ApiClient:
    """Base API client with caching and rate limiting"""
    
    def __init__(self, base_url: str, rate_limiter: RateLimiter, cache_manager: CacheManager):
        self.base_url = base_url
        self.rate_limiter = rate_limiter
        self.cache_manager = cache_manager
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get(self, endpoint: str, params: Dict = None, cache_key: str = None) -> Optional[Dict]:
        """GET request with caching and rate limiting"""
        # Check cache first
        if cache_key:
            cached = self.cache_manager.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
        
        # Rate limiting
        await self.rate_limiter.wait(self.base_url)
        
        # Make request
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache the result
                    if cache_key:
                        self.cache_manager.set(cache_key, data)
                    
                    return data
                else:
                    logger.error(f"API request failed: {response.status} - {url}")
                    return None
        except Exception as e:
            logger.error(f"API request error: {e} - {url}")
            return None

class SignalCalculator:
    """Utility class for calculating trading signals"""
    
    @staticmethod
    def generate_signal(price: float, change_24h: float, volume: float = None) -> SignalType:
        """Generate signal based on price change"""
        abs_change = abs(change_24h)
        
        if change_24h > 0:
            if abs_change >= config.signal_thresholds["extreme"]:
                return SignalType.STRONG_BUY
            elif abs_change >= config.signal_thresholds["strong"]:
                return SignalType.BUY
            elif abs_change >= config.signal_thresholds["moderate"]:
                return SignalType.UP
            else:
                return SignalType.UP
        else:
            if abs_change >= config.signal_thresholds["extreme"]:
                return SignalType.STRONG_SELL
            elif abs_change >= config.signal_thresholds["strong"]:
                return SignalType.SELL
            elif abs_change >= config.signal_thresholds["moderate"]:
                return SignalType.DOWN
            else:
                return SignalType.DOWN
    
    @staticmethod
    def calculate_signal_strength(change_24h: float) -> float:
        """Calculate signal strength 0-100"""
        abs_change = abs(change_24h)
        
        if abs_change >= config.signal_thresholds["extreme"]:
            return 100
        elif abs_change >= config.signal_thresholds["strong"]:
            return 80 + (abs_change - config.signal_thresholds["strong"]) / (config.signal_thresholds["extreme"] - config.signal_thresholds["strong"]) * 20
        elif abs_change >= config.signal_thresholds["moderate"]:
            return 50 + (abs_change - config.signal_thresholds["moderate"]) / (config.signal_thresholds["strong"] - config.signal_thresholds["moderate"]) * 30
        elif abs_change >= config.signal_thresholds["weak"]:
            return 25 + (abs_change - config.signal_thresholds["weak"]) / (config.signal_thresholds["moderate"] - config.signal_thresholds["weak"]) * 25
        else:
            return 10 + (abs_change / config.signal_thresholds["weak"]) * 15
    
    @staticmethod
    def calculate_confidence(price: float, change_24h: float, volume: float = None) -> float:
        """Calculate confidence score based on multiple factors"""
        confidence = config.confidence_factors["base"]
        
        # Volume factor
        if volume:
            if volume > 1000000:
                confidence += config.confidence_factors["high_volume"]
        
        # Price change consistency
        abs_change = abs(change_24h)
        if abs_change > 2:
            confidence += config.confidence_factors["strong_move"]
        elif abs_change > 1:
            confidence += 10
        elif abs_change > 0.5:
            confidence += 5
        
        # Price level factor
        if price > 1000:
            confidence += config.confidence_factors["high_price"]
        elif price > 100:
            confidence += 5
        
        return min(confidence, 100)
    
    @staticmethod
    def calculate_targets(price: float, change_24h: float, signal: SignalType) -> Tuple[float, float, float]:
        """Calculate entry, target, and stop loss prices"""
        if signal in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP]:
            entry = price
            if signal == SignalType.STRONG_BUY:
                target = price * 1.03
                stop_loss = price * 0.98
            elif signal == SignalType.BUY:
                target = price * 1.02
                stop_loss = price * 0.985
            else:  # UP
                target = price * 1.01
                stop_loss = price * 0.99
        else:
            entry = price
            if signal == SignalType.STRONG_SELL:
                target = price * 0.97
                stop_loss = price * 1.02
            elif signal == SignalType.SELL:
                target = price * 0.98
                stop_loss = price * 1.015
            else:  # DOWN
                target = price * 0.99
                stop_loss = price * 1.01
        
        return entry, target, stop_loss

class DataFormatter:
    """Utility class for formatting data for display"""
    
    @staticmethod
    def format_price(price: float, symbol: str = None) -> str:
        """Format price based on symbol type"""
        if symbol and any(metal in symbol for metal in ["XAU", "XAG"]):
            return f"${price:.2f}"
        elif symbol and any(curr in symbol for curr in ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]):
            return f"{price:.5f}"
        else:
            return f"${price:.4f}"
    
    @staticmethod
    def format_change(change_24h: float) -> str:
        """Format 24h change percentage"""
        return f"{change_24h:+.2f}%"
    
    @staticmethod
    def get_signal_emoji(signal_type: SignalType) -> str:
        """Get emoji for signal type"""
        emojis = {
            SignalType.STRONG_BUY: "🟢🔺",
            SignalType.BUY: "🟢↗️",
            SignalType.UP: "🟢↑",
            SignalType.DOWN: "🔴↓",
            SignalType.SELL: "🔴↘️",
            SignalType.STRONG_SELL: "🔴🔻"
        }
        return emojis.get(signal_type, "⚪")
    
    @staticmethod
    def get_binary_code(signal_type: SignalType) -> str:
        """Get binary code for signal"""
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP]:
            return "1"
        else:
            return "0"

# Global instances
cache_manager = CacheManager()
rate_limiter = RateLimiter()
signal_calculator = SignalCalculator()
data_formatter = DataFormatter()