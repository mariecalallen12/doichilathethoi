"""
Market Data Providers - Simplified for Backend Integration
============================================================

Simplified version without TradingSystemAPI dependencies
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class BinanceProvider:
    """Binance cryptocurrency data provider"""
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    SYMBOL_MAP = {
        "BTC": "BTCUSDT", "ETH": "ETHUSDT", "BNB": "BNBUSDT",
        "SOL": "SOLUSDT", "XRP": "XRPUSDT", "ADA": "ADAUSDT",
        "DOT": "DOTUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT",
        "DOGE": "DOGEUSDT", "MATIC": "MATICUSDT", "UNI": "UNIUSDT",
        "LTC": "LTCUSDT", "ATOM": "ATOMUSDT"
    }
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price from Binance"""
        try:
            binance_symbol = self.SYMBOL_MAP.get(symbol.upper())
            if not binance_symbol:
                return None
            
            async with aiohttp.ClientSession() as session:
                # Get ticker
                url = f"{self.BASE_URL}/ticker/24hr"
                params = {"symbol": binance_symbol}
                
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status != 200:
                        logger.error(f"Binance API error for {symbol}: {resp.status}")
                        return None
                    
                    data = await resp.json()
                    
                    return {
                        "symbol": symbol,
                        "price": float(data["lastPrice"]),
                        "change_24h": float(data["priceChangePercent"]),
                        "volume": float(data["volume"]),
                        "high_24h": float(data["highPrice"]),
                        "low_24h": float(data["lowPrice"]),
                        "timestamp": datetime.utcnow(),
                        "source": "binance"
                    }
        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {e}")
            return None
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """Get all cryptocurrency prices"""
        tasks = [self.get_price(symbol) for symbol in self.SYMBOL_MAP.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for result in results:
            if isinstance(result, dict) and result:
                prices[result["symbol"]] = result
        
        return prices


class ForexProvider:
    """Forex currency data provider"""
    
    BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    
    PAIRS = [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
        "AUD/USD", "USD/CAD", "NZD/USD"
    ]
    
    async def get_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get forex pair price"""
        try:
            base, quote = pair.split("/")
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/{base}"
                
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status != 200:
                        return None
                    
                    data = await resp.json()
                    rate = data["rates"].get(quote)
                    
                    if not rate:
                        return None
                    
                    # Simulate 24h change (placeholder - would need historical API)
                    import random
                    change_24h = random.uniform(-2.0, 2.0)
                    
                    return {
                        "symbol": pair,
                        "price": float(rate),
                        "change_24h": change_24h,
                        "timestamp": datetime.utcnow(),
                        "source": "exchangerate-api"
                    }
        except Exception as e:
            logger.error(f"Error fetching Forex data for {pair}: {e}")
            return None
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """Get all forex prices"""
        tasks = [self.get_price(pair) for pair in self.PAIRS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for result in results:
            if isinstance(result, dict) and result:
                prices[result["symbol"]] = result
        
        return prices


class MetalsProvider:
    """Precious metals data provider"""
    
    METALS = ["GOLD", "SILVER", "PLATINUM", "PALLADIUM"]
    
    async def get_price(self, metal: str) -> Optional[Dict[str, Any]]:
        """Get metal price (placeholder - would need real API)"""
        try:
            # Placeholder prices (would use real API like metals-api.com)
            import random
            
            base_prices = {
                "GOLD": 2000.0,
                "SILVER": 25.0,
                "PLATINUM": 1000.0,
                "PALLADIUM": 1500.0
            }
            
            if metal not in base_prices:
                return None
            
            price = base_prices[metal] * random.uniform(0.98, 1.02)
            change_24h = random.uniform(-3.0, 3.0)
            
            return {
                "symbol": metal,
                "price": price,
                "change_24h": change_24h,
                "timestamp": datetime.utcnow(),
                "source": "metals-placeholder"
            }
        except Exception as e:
            logger.error(f"Error fetching metal data for {metal}: {e}")
            return None
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """Get all metal prices"""
        tasks = [self.get_price(metal) for metal in self.METALS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for result in results:
            if isinstance(result, dict) and result:
                prices[result["symbol"]] = result
        
        return prices


class MarketDataAggregator:
    """Aggregates data from all providers"""
    
    def __init__(self):
        self.binance = BinanceProvider()
        self.forex = ForexProvider()
        self.metals = MetalsProvider()
        logger.info("MarketDataAggregator initialized")
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """Get all market data from all providers"""
        try:
            crypto_task = self.binance.get_all_prices()
            forex_task = self.forex.get_all_prices()
            metals_task = self.metals.get_all_prices()
            
            crypto, forex, metals = await asyncio.gather(
                crypto_task, forex_task, metals_task,
                return_exceptions=True
            )
            
            all_prices = {}
            
            if isinstance(crypto, dict):
                all_prices.update(crypto)
            if isinstance(forex, dict):
                all_prices.update(forex)
            if isinstance(metals, dict):
                all_prices.update(metals)
            
            logger.info(f"Fetched {len(all_prices)} market prices")
            return all_prices
            
        except Exception as e:
            logger.error(f"Error in MarketDataAggregator: {e}")
            return {}
    
    async def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price for a specific symbol"""
        # Determine which provider to use
        if symbol.upper() in BinanceProvider.SYMBOL_MAP:
            return await self.binance.get_price(symbol)
        elif "/" in symbol:  # Forex pair
            return await self.forex.get_price(symbol)
        elif symbol.upper() in MetalsProvider.METALS:
            return await self.metals.get_price(symbol)
        else:
            logger.warning(f"Unknown symbol: {symbol}")
            return None
