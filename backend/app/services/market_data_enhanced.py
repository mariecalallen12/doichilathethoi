"""
Enhanced Market Data Provider with Real 24h Change
===================================================

Hybrid approach:
- Primary: Twelve Data API (800 req/day free)
- Fallback: Self-calculated from historical database
- Crypto: Binance (unchanged - 100% real)
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import os

from sqlalchemy.orm import Session
from sqlalchemy import desc

logger = logging.getLogger(__name__)


class TwelveDataProvider:
    """Twelve Data API provider for Forex with 24h change"""
    
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TWELVEDATA_API_KEY")
        self.request_count = 0
        self.daily_limit = 800
    
    async def get_forex_with_change(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get forex price with real 24h change from Twelve Data
        
        Args:
            pair: Forex pair (e.g., "EUR/USD")
            
        Returns:
            Dict with price and change_24h, or None if failed
        """
        if not self.api_key:
            logger.warning("Twelve Data API key not configured")
            return None
        
        if self.request_count >= self.daily_limit:
            logger.warning("Twelve Data daily limit reached")
            return None
        
        try:
            # Convert pair format: "EUR/USD" -> "EUR/USD"
            symbol = pair.replace("/", "/")
            
            url = f"{self.BASE_URL}/time_series"
            params = {
                "symbol": symbol,
                "interval": "1day",
                "outputsize": 2,  # Get last 2 days
                "apikey": self.api_key,
                "format": "JSON"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        logger.error(f"Twelve Data API error: {resp.status}")
                        return None
                    
                    data = await resp.json()
                    
                    # Check for error
                    if "status" in data and data["status"] == "error":
                        logger.error(f"Twelve Data error: {data.get('message')}")
                        return None
                    
                    # Parse response
                    if "values" in data and len(data["values"]) >= 2:
                        current = float(data["values"][0]["close"])
                        previous = float(data["values"][1]["close"])
                        
                        change_24h = ((current - previous) / previous) * 100
                        
                        self.request_count += 1
                        
                        logger.info(f"Twelve Data: {pair} = {current}, change = {change_24h:.2f}%")
                        
                        return {
                            "symbol": pair,
                            "price": current,
                            "change_24h": change_24h,
                            "timestamp": datetime.utcnow(),
                            "source": "twelvedata"
                        }
                    else:
                        logger.warning(f"Twelve Data: insufficient data for {pair}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Twelve Data timeout for {pair}")
            return None
        except Exception as e:
            logger.error(f"Twelve Data error for {pair}: {e}")
            return None
    
    def reset_daily_counter(self):
        """Reset daily request counter (call at midnight)"""
        self.request_count = 0


class HistoricalDataCalculator:
    """Calculate 24h change from stored historical data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_forex_change(self, pair: str) -> Optional[Dict[str, Any]]:
        """Calculate 24h change from database history"""
        from app.models.customization import ForexHistory
        
        try:
            # Get current price (most recent)
            current_record = self.db.query(ForexHistory)\
                .filter(ForexHistory.pair == pair)\
                .order_by(desc(ForexHistory.timestamp))\
                .first()
            
            if not current_record:
                logger.warning(f"No historical data for {pair}")
                return None
            
            # Get price from 24h ago
            time_24h_ago = datetime.utcnow() - timedelta(hours=24)
            
            historical_record = self.db.query(ForexHistory)\
                .filter(ForexHistory.pair == pair)\
                .filter(ForexHistory.timestamp <= time_24h_ago)\
                .order_by(desc(ForexHistory.timestamp))\
                .first()
            
            if not historical_record:
                logger.warning(f"No 24h historical data for {pair}")
                return None
            
            # Calculate change
            current_price = float(current_record.price)
            historical_price = float(historical_record.price)
            
            change_24h = ((current_price - historical_price) / historical_price) * 100
            
            logger.info(f"Self-calculated: {pair} = {current_price}, change = {change_24h:.2f}%")
            
            return {
                "symbol": pair,
                "price": current_price,
                "change_24h": change_24h,
                "timestamp": current_record.timestamp,
                "source": "self-calculated"
            }
            
        except Exception as e:
            logger.error(f"Error calculating change for {pair}: {e}")
            return None
    
    async def get_metal_change(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Calculate 24h change for metals from database"""
        from app.models.customization import MetalHistory
        
        try:
            # Get current price
            current_record = self.db.query(MetalHistory)\
                .filter(MetalHistory.symbol == symbol)\
                .order_by(desc(MetalHistory.timestamp))\
                .first()
            
            if not current_record:
                return None
            
            # Get price from 24h ago
            time_24h_ago = datetime.utcnow() - timedelta(hours=24)
            
            historical_record = self.db.query(MetalHistory)\
                .filter(MetalHistory.symbol == symbol)\
                .filter(MetalHistory.timestamp <= time_24h_ago)\
                .order_by(desc(MetalHistory.timestamp))\
                .first()
            
            if not historical_record:
                return None
            
            # Calculate change
            current_price = float(current_record.price)
            historical_price = float(historical_record.price)
            
            change_24h = ((current_price - historical_price) / historical_price) * 100
            
            return {
                "symbol": symbol,
                "price": current_price,
                "change_24h": change_24h,
                "timestamp": current_record.timestamp,
                "source": "self-calculated"
            }
            
        except Exception as e:
            logger.error(f"Error calculating metal change for {symbol}: {e}")
            return None


class EnhancedMarketDataAggregator:
    """
    Enhanced aggregator with real 24h change
    
    Strategy:
    - Crypto: Binance (unchanged)
    - Forex: Twelve Data (primary) -> Self-calculated (fallback)
    - Metals: Self-calculated
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.twelvedata = TwelveDataProvider()
        self.historical = HistoricalDataCalculator(db)
        
        # Import base providers
        from app.services.market_providers_simple import (
            BinanceProvider,
            ForexProvider,
            MetalsProvider
        )
        
        self.binance = BinanceProvider()
        self.forex_base = ForexProvider()
        self.metals_base = MetalsProvider()
        
        logger.info("Enhanced Market Data Aggregator initialized")
    
    async def get_crypto_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get crypto with real 24h change (Binance)"""
        # Binance already provides real 24h change
        return await self.binance.get_price(symbol)
    
    async def get_forex_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get forex with real 24h change
        
        Priority:
        1. Twelve Data (if API key available and within limit)
        2. Self-calculated (if historical data exists)
        3. Current price only (fallback)
        """
        # Try Twelve Data first
        if self.twelvedata.api_key:
            data = await self.twelvedata.get_forex_with_change(pair)
            if data:
                return data
            logger.info(f"Twelve Data unavailable for {pair}, trying self-calculated")
        
        # Fallback to self-calculated
        data = await self.historical.get_forex_change(pair)
        if data:
            return data
        
        # Last resort: current price only (no 24h change)
        logger.warning(f"No 24h change available for {pair}, using current price only")
        base_data = await self.forex_base.get_price(pair)
        if base_data:
            base_data["change_24h"] = 0.0  # No change data
            base_data["source"] = "fallback-no-change"
        
        return base_data
    
    async def get_metal_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get metal with real 24h change (self-calculated)"""
        # Try self-calculated
        data = await self.historical.get_metal_change(symbol)
        if data:
            return data
        
        # Fallback: current price only
        logger.warning(f"No 24h change available for {symbol}, using current price only")
        base_data = await self.metals_base.get_price(symbol)
        if base_data:
            base_data["change_24h"] = 0.0
            base_data["source"] = "fallback-no-change"
        
        return base_data
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """Get all market data with real 24h changes"""
        all_prices = {}
        
        # Crypto (Binance)
        crypto_symbols = list(self.binance.SYMBOL_MAP.keys())
        for symbol in crypto_symbols:
            data = await self.get_crypto_price(symbol)
            if data:
                all_prices[symbol] = data
        
        # Forex
        forex_pairs = self.forex_base.PAIRS
        for pair in forex_pairs:
            data = await self.get_forex_price(pair)
            if data:
                all_prices[pair] = data
        
        # Metals
        metals = self.metals_base.METALS
        for metal in metals:
            data = await self.get_metal_price(metal)
            if data:
                all_prices[metal] = data
        
        logger.info(f"Fetched {len(all_prices)} prices with real/calculated 24h changes")
        
        return all_prices
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price for any symbol (auto-detect type)"""
        # Determine type
        if symbol.upper() in self.binance.SYMBOL_MAP:
            return await self.get_crypto_price(symbol)
        elif "/" in symbol:
            return await self.get_forex_price(symbol)
        elif symbol.upper() in self.metals_base.METALS:
            return await self.get_metal_price(symbol)
        else:
            logger.warning(f"Unknown symbol type: {symbol}")
            return None


# Factory function
def get_enhanced_aggregator(db: Session) -> EnhancedMarketDataAggregator:
    """Get enhanced aggregator instance"""
    return EnhancedMarketDataAggregator(db)
