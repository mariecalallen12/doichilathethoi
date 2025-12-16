"""
OPEX Market Data Service
Integration layer for market data operations using OPEX Core
"""
import logging
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

from .opex_client import get_opex_client, OPEXClient
from ..services.cache_service import CacheService

logger = logging.getLogger(__name__)

# Structured logging helper
def log_market_operation(operation: str, status: str, details: Dict[str, Any] = None):
    """Log market operation with structured format"""
    log_data = {
        "operation": operation,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "opex-market"
    }
    if details:
        log_data.update(details)
    
    if status == "error":
        logger.error(f"Market {operation}: {log_data}")
    elif status == "warning":
        logger.warning(f"Market {operation}: {log_data}")
    else:
        logger.info(f"Market {operation}: {log_data}")


class OPEXMarketService:
    """
    Market data service that uses OPEX Core
    
    Provides access to orderbook, trades, candles, ticker data from OPEX
    """
    
    def __init__(self, opex_client: Optional[OPEXClient] = None, cache_service: Optional[CacheService] = None):
        """
        Initialize OPEX market service
        
        Args:
            opex_client: OPEX client instance (will create if not provided)
            cache_service: Cache service instance
        """
        self.opex = opex_client or get_opex_client()
        self.cache = cache_service or CacheService()
        
        # Cache TTLs (in seconds)
        self.CACHE_TTL_SYMBOLS = 300  # 5 minutes
        self.CACHE_TTL_ORDERBOOK = 1  # 1 second for orderbook (very dynamic)
        self.CACHE_TTL_TICKER = 5  # 5 seconds for ticker
        self.CACHE_TTL_TRADES = 10  # 10 seconds for trades
    
    async def get_orderbook(
        self,
        symbol: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get orderbook for a symbol
        
        Args:
            symbol: Trading pair symbol
            limit: Number of levels
            
        Returns:
            Orderbook data
        """
        try:
            opex_symbol = self._convert_symbol(symbol)
            result = await self.opex.get_orderbook(opex_symbol, limit)
            if result:
                log_market_operation(
                    "get_orderbook",
                    "success",
                    {"symbol": symbol, "limit": limit}
                )
                return result
            else:
                # Return empty orderbook
                log_market_operation(
                    "get_orderbook",
                    "warning",
                    {"symbol": symbol, "message": "Empty result from OPEX"}
                )
                return {
                    "symbol": symbol,
                    "bids": [],
                    "asks": [],
                    "timestamp": int(__import__('time').time() * 1000)
                }
        except Exception as e:
            log_market_operation(
                "get_orderbook",
                "error",
                {
                    "symbol": symbol,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            logger.error(f"Failed to get orderbook from OPEX for {symbol}: {e}", exc_info=True)
            # Return empty orderbook instead of raising
            return {
                "symbol": symbol,
                "bids": [],
                "asks": [],
                "timestamp": int(__import__('time').time() * 1000)
            }
    
    async def get_trades(
        self,
        symbol: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent trades
        
        Args:
            symbol: Trading pair symbol
            limit: Maximum number of trades
            
        Returns:
            List of trades (empty list on error)
        """
        try:
            opex_symbol = self._convert_symbol(symbol)
            trades = await self.opex.get_trades(opex_symbol, limit)
            result = [self._convert_trade_from_opex(trade) for trade in trades]
            log_market_operation(
                "get_trades",
                "success",
                {"symbol": symbol, "count": len(result)}
            )
            return result
        except Exception as e:
            log_market_operation(
                "get_trades",
                "error",
                {
                    "symbol": symbol,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            logger.error(f"Failed to get trades from OPEX for {symbol}: {e}", exc_info=True)
            # Return empty list instead of raising
            return []
    
    async def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV candles
        
        Args:
            symbol: Trading pair symbol
            interval: Time interval
            limit: Number of candles
            
        Returns:
            List of candles (empty list on error)
        """
        try:
            opex_symbol = self._convert_symbol(symbol)
            candles = await self.opex.get_candles(opex_symbol, interval, limit)
            log_market_operation(
                "get_candles",
                "success",
                {"symbol": symbol, "interval": interval, "count": len(candles)}
            )
            return candles
        except Exception as e:
            log_market_operation(
                "get_candles",
                "error",
                {
                    "symbol": symbol,
                    "interval": interval,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            logger.error(f"Failed to get candles from OPEX for {symbol} ({interval}): {e}", exc_info=True)
            # Return empty list instead of raising
            return []
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get ticker data
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Ticker data (empty dict with symbol on error)
        """
        try:
            opex_symbol = self._convert_symbol(symbol)
            ticker = await self.opex.get_ticker(opex_symbol)
            log_market_operation(
                "get_ticker",
                "success",
                {"symbol": symbol}
            )
            return ticker
        except Exception as e:
            log_market_operation(
                "get_ticker",
                "error",
                {
                    "symbol": symbol,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            logger.error(f"Failed to get ticker from OPEX for {symbol}: {e}", exc_info=True)
            # Return minimal ticker data instead of raising
            return {
                "symbol": symbol,
                "price": 0.0,
                "change_24h": 0.0,
                "change_percent_24h": 0.0,
                "volume_24h": 0.0,
                "high_24h": 0.0,
                "low_24h": 0.0
            }
    
    async def get_symbols(self) -> List[Dict[str, Any]]:
        """
        Get available trading symbols (with caching)
        
        Returns:
            List of symbols
        """
        cache_key = "opex:market:symbols"
        
        # Try to get from cache first
        cached = self.cache.get(cache_key)
        if cached:
            log_market_operation(
                "get_symbols",
                "cache_hit",
                {"count": len(cached)}
            )
            return cached
        
        # Cache miss - fetch from OPEX
        start_time = time.time()
        try:
            symbols = await self.opex.get_symbols()
            duration = time.time() - start_time
            
            if symbols:
                result = [self._convert_symbol_from_opex(s) for s in symbols]
                # Cache the result
                self.cache.set(cache_key, result, self.CACHE_TTL_SYMBOLS)
                log_market_operation(
                    "get_symbols",
                    "success",
                    {
                        "count": len(result),
                        "duration_ms": duration * 1000,
                        "cache": "miss"
                    }
                )
                return result
            else:
                # Return fallback symbols
                fallback = [
                    {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT"},
                    {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT"},
                    {"symbol": "BNBUSDT", "base": "BNB", "quote": "USDT"}
                ]
                # Cache fallback too
                self.cache.set(cache_key, fallback, self.CACHE_TTL_SYMBOLS)
                log_market_operation(
                    "get_symbols",
                    "warning",
                    {
                        "count": 0,
                        "duration_ms": duration * 1000,
                        "message": "No symbols returned, using fallback"
                    }
                )
                return fallback
        except Exception as e:
            duration = time.time() - start_time
            # Try to return cached data even if stale
            cached = self.cache.get(cache_key)
            if cached:
                log_market_operation(
                    "get_symbols",
                    "error_cached",
                    {
                        "error": str(e),
                        "duration_ms": duration * 1000
                    }
                )
                return cached
            
            log_market_operation(
                "get_symbols",
                "error",
                {
                    "error": str(e),
                    "duration_ms": duration * 1000,
                    "message": "Using fallback symbols"
                }
            )
            # Return fallback symbols instead of raising
            return [
                {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT"},
                {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT"},
                {"symbol": "BNBUSDT", "base": "BNB", "quote": "USDT"}
            ]
    
    def _convert_symbol(self, symbol: str) -> str:
        """Convert symbol to OPEX format"""
        symbol = symbol.replace('/', '').replace('-', '').upper()
        base_currencies = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TON']
        quote_currencies = ['USDT', 'USD', 'IRT', 'BUSD', 'EUR', 'GBP']
        
        for base in base_currencies:
            if symbol.startswith(base):
                remaining = symbol[len(base):]
                if remaining in quote_currencies:
                    return f"{base}_{remaining}"
        
        if len(symbol) >= 6:
            return f"{symbol[:3]}_{symbol[3:]}"
        
        return symbol
    
    def _convert_symbol_from_opex(self, symbol: Dict[str, Any]) -> Dict[str, Any]:
        """Convert symbol from OPEX format"""
        symbol_str = symbol.get("symbol", "")
        return {
            "symbol": symbol_str.replace('_', ''),
            "base": symbol.get("base", ""),
            "quote": symbol.get("quote", "")
        }
    
    def _convert_trade_from_opex(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """Convert trade from OPEX format"""
        return {
            "id": str(trade.get("id", "")),
            "symbol": trade.get("symbol", "").replace('_', ''),
            "side": trade.get("side", "").lower(),
            "quantity": float(trade.get("quantity", 0)),
            "price": float(trade.get("price", 0)),
            "time": trade.get("time", "")
        }


# Singleton instance
_opex_market_service: Optional[OPEXMarketService] = None


def get_opex_market_service() -> OPEXMarketService:
    """
    Get OPEX market service instance (singleton)
    
    Returns:
        OPEXMarketService instance
    """
    global _opex_market_service
    
    if _opex_market_service is None:
        _opex_market_service = OPEXMarketService()
    
    return _opex_market_service

