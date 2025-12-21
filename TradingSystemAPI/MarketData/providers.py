#!/usr/bin/env python3
"""
Market Data Providers
=====================

Data providers for different asset classes (Crypto, Forex, Metals)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Shared.models import PriceData, AssetClass, config
from Shared.utils import ApiClient, cache_manager, rate_limiter

logger = logging.getLogger(__name__)

# API Keys for new services - PLEASE REPLACE WITH YOUR ACTUAL KEYS
# These should be loaded from environment variables in a real application
FX_API_KEY = os.getenv("FXMARKETAPI_KEY", "YOUR_FXMARKETAPI_KEY")
METAL_API_KEY = os.getenv("METALPRICEAPI_KEY", "YOUR_METALPRICEAPI_KEY")


class BinanceDataProvider:
    """Binance market data provider for cryptocurrency"""
    
    def __init__(self):
        self.api_client = ApiClient(config.binance_base_url, rate_limiter, cache_manager)
        self.symbol_mappings = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT", 
            "BNB": "BNBUSDT",
            "SOL": "SOLUSDT",
            "XRP": "XRPUSDT",
            "ADA": "ADAUSDT",
            "DOT": "DOTUSDT",
            "AVAX": "AVAXUSDT",
            "LINK": "LINKUSDT",
            "DOGE": "DOGEUSDT",
            "MATIC": "MATICUSDT",
            "UNI": "UNIUSDT",
            "LTC": "LTCUSDT",
            "ATOM": "ATOMUSDT"
        }
    
    async def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get current price for a symbol"""
        try:
            async with self.api_client as client:
                binance_symbol = self.symbol_mappings.get(symbol.upper())
                if not binance_symbol:
                    logger.warning(f"No Binance mapping for {symbol}")
                    return None
                
                # Get 24hr ticker data
                data = await client.get(
                    "api/v3/ticker/24hr",
                    params={"symbol": binance_symbol},
                    cache_key=f"binance_24hr_{symbol}"
                )
                
                if data:
                    return PriceData(
                        symbol=symbol.upper(),
                        asset_class=AssetClass.CRYPTO,
                        price=float(data["lastPrice"]),
                        change_24h=float(data["priceChangePercent"]),
                        volume=float(data["volume"]),
                        high_24h=float(data["highPrice"]),
                        low_24h=float(data["lowPrice"]),
                        timestamp=datetime.now().isoformat(),
                        source="binance"
                    )
        except Exception as e:
            logger.error(f"Error getting Binance price for {symbol}: {e}")
        
        return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Get prices for multiple symbols"""
        tasks = [self.get_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, PriceData):
                prices[symbol] = result
            else:
                logger.error(f"Failed to get price for {symbol}: {result}")
        
        return prices
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview data"""
        try:
            async with self.api_client as client:
                # Get ticker for major symbols
                data = await client.get(
                    "api/v3/ticker/24hr",
                    cache_key="binance_market_overview"
                )
                
                if data and isinstance(data, list):
                    # Process market overview
                    total_volume = 0
                    gainers = []
                    losers = []
                    
                    for ticker in data[:50]:  # Top 50 by volume
                        price = float(ticker["lastPrice"])
                        change = float(ticker["priceChangePercent"])
                        volume = float(ticker["volume"])
                        
                        total_volume += volume
                        
                        if change > 0:
                            gainers.append({
                                "symbol": ticker["symbol"],
                                "price": price,
                                "change": change
                            })
                        else:
                            losers.append({
                                "symbol": ticker["symbol"],
                                "price": price,
                                "change": change
                            })
                    
                    # Sort and get top 10
                    gainers.sort(key=lambda x: x["change"], reverse=True)
                    losers.sort(key=lambda x: x["change"])
                    
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "total_volume": total_volume,
                        "top_gainers": gainers[:10],
                        "top_losers": losers[:10],
                        "market_count": len(data)
                    }
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
        
        return {}

class ForexDataProvider:
    """Forex data provider for currency pairs"""
    
    def __init__(self):
        # This client is now only used for fallback if the new API fails
        self.api_client = ApiClient(config.forex_base_url, rate_limiter, cache_manager)
        self.currency_pairs = [
            "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF",
            "AUD/USD", "USD/CAD", "NZD/USD"
        ]
    
    async def get_price(self, pair: str) -> Optional[PriceData]:
        """Get price and 24h change for a currency pair from FXMarketAPI."""
        try:
            # FXMarketAPI uses pairs without "/" e.g., EURUSD
            api_pair = pair.replace("/", "")
            yesterday = (datetime.today() - timedelta(days=1)).isoformat()
            today = datetime.today().isoformat()
            url = (
                f"https://fxmarketapi.com/apichange?api_key={FX_API_KEY}"
                f"&currency={api_pair}&start_date={yesterday}&end_date={today}"
            )
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                if "price" in data and api_pair in data["price"]:
                    change_data = data["price"][api_pair]
                    return PriceData(
                        symbol=pair,
                        asset_class=AssetClass.FOREX,
                        price=float(change_data["end_rate"]),
                        change_24h=float(change_data["pct_change"]),
                        timestamp=datetime.now().isoformat(),
                        source="fxmarketapi.com"
                    )
        except Exception as e:
            logger.error(f"Error getting Forex price for {pair} from FXMarketAPI: {e}")
            # Fallback to old method if new one fails
            return await self.get_price_fallback(pair)
            
        return None

    async def get_price_fallback(self, pair: str) -> Optional[PriceData]:
        """Fallback to the old method of getting price data."""
        logger.warning(f"Falling back to old provider for Forex pair {pair}")
        try:
            async with self.api_client as client:
                if "/" not in pair: return None
                base, quote = pair.split("/")
                data = await client.get(f"latest/{base.upper()}", cache_key=f"forex_{pair}")
                if data and "rates" in data:
                    price = float(data["rates"].get(quote.upper(), 1.0))
                    # Mock 24h change for forex
                    change_24h = (price - 1.0) * 0.1 
                    return PriceData(
                        symbol=pair, asset_class=AssetClass.FOREX, price=price,
                        change_24h=change_24h, timestamp=datetime.now().isoformat(),
                        source="exchangerate-api-fallback"
                    )
        except Exception as e:
            logger.error(f"Fallback Forex provider error for {pair}: {e}")
        return None

    async def get_multiple_prices(self, pairs: List[str]) -> Dict[str, PriceData]:
        """Get prices for multiple currency pairs"""
        tasks = [self.get_price(pair) for pair in pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for pair, result in zip(pairs, results):
            if isinstance(result, PriceData):
                prices[pair] = result
            else:
                logger.error(f"Failed to get price for {pair}: {result}")
        
        return prices

class MetalsDataProvider:
    """Precious metals data provider"""
    
    def __init__(self):
        # This client is now only used for fallback if the new API fails
        self.api_client = ApiClient(config.metals_base_url, rate_limiter, cache_manager)
        self.metals_mapping = {
            "XAU/USD": "XAU",
            "XAG/USD": "XAG"
        }

    async def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get price and 24h change for a precious metal from MetalpriceAPI."""
        try:
            metal_symbol = self.metals_mapping.get(symbol)
            if not metal_symbol:
                logger.warning(f"No metals mapping for {symbol}")
                return None
            
            url = (
                f"https://api.metalpriceapi.com/v1/change?"
                f"api_key={METAL_API_KEY}&base=USD&currencies={metal_symbol}&date_type=recent"
            )
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("success") and "rates" in data and metal_symbol in data["rates"]:
                    change_data = data["rates"][metal_symbol]
                    return PriceData(
                        symbol=symbol,
                        asset_class=AssetClass.METALS,
                        price=float(change_data["price"]),
                        change_24h=float(change_data["change_pct"]),
                        timestamp=datetime.now().isoformat(),
                        source="metalpriceapi.com"
                    )
        except Exception as e:
            logger.error(f"Error getting metals price for {symbol} from MetalpriceAPI: {e}")
            # Fallback to old method if new one fails
            return await self.get_price_fallback(symbol)

        return None
    
    async def get_price_fallback(self, symbol: str) -> Optional[PriceData]:
        """Fallback to the old method of getting price data."""
        logger.warning(f"Falling back to old provider for metal {symbol}")
        try:
            async with self.api_client as client:
                metal = self.metals_mapping.get(symbol)
                if not metal: return None
                data = await client.get(f"latest/{metal}", cache_key=f"metals_{symbol}")
                if data and "rates" in data and "USD" in data["rates"]:
                    price = float(data["rates"]["USD"])
                    # Mock 24h change
                    change_24h = 0.15 if "XAU" in symbol else -0.05
                    return PriceData(
                        symbol=symbol, asset_class=AssetClass.METALS, price=price,
                        change_24h=change_24h, timestamp=datetime.now().isoformat(),
                        source="metals-api-fallback"
                    )
        except Exception as e:
            logger.error(f"Fallback Metals provider error for {symbol}: {e}")
        return None

    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, PriceData]:
        """Get prices for multiple metals"""
        tasks = [self.get_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, PriceData):
                prices[symbol] = result
            else:
                logger.error(f"Failed to get price for {symbol}: {result}")
        
        return prices

class MarketDataAggregator:
    """Main market data aggregator"""
    
    def __init__(self):
        self.binance = BinanceDataProvider()
        self.forex = ForexDataProvider()
        self.metals = MetalsDataProvider()
    
    async def get_all_prices(self) -> Dict[str, PriceData]:
        """Get prices from all providers"""
        all_prices = {}
        
        # Get crypto prices
        crypto_symbols = list(self.binance.symbol_mappings.keys())
        crypto_prices = await self.binance.get_multiple_prices(crypto_symbols)
        all_prices.update(crypto_prices)
        
        # Get forex prices
        forex_prices = await self.forex.get_multiple_prices(self.forex.currency_pairs)
        all_prices.update(forex_prices)
        
        # Get metals prices
        metals_prices = await self.metals.get_multiple_prices(list(self.metals.metals_mapping.keys()))
        all_prices.update(metals_prices)
        
        return all_prices
    
    async def get_prices_by_asset_class(self, asset_class: AssetClass) -> Dict[str, PriceData]:
        """Get prices filtered by asset class"""
        all_prices = await self.get_all_prices()
        return {symbol: price for symbol, price in all_prices.items() 
                if price.asset_class == asset_class}
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Get comprehensive market summary"""
        all_prices = await self.get_all_prices()
        
        if not all_prices:
            return {"error": "No market data available"}
        
        # Count by asset class
        crypto_count = sum(1 for price in all_prices.values() if price.asset_class == AssetClass.CRYPTO)
        forex_count = sum(1 for price in all_prices.values() if price.asset_class == AssetClass.FOREX)
        metals_count = sum(1 for price in all_prices.values() if price.asset_class == AssetClass.METALS)
        
        # Calculate averages
        changes = [price.change_24h for price in all_prices.values() if price.change_24h is not None]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Find strongest moves
        if changes:
            max_gain = max(changes)
            max_loss = min(changes)
            
            gainer = next((price for price in all_prices.values() 
                          if price.change_24h == max_gain), None)
            loser = next((price for price in all_prices.values() 
                         if price.change_24h == max_loss), None)
        else:
            max_gain = max_loss = 0
            gainer = loser = None
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_instruments": len(all_prices),
            "by_asset_class": {
                "crypto": crypto_count,
                "forex": forex_count,
                "metals": metals_count
            },
            "market_stats": {
                "average_change_24h": avg_change,
                "max_gain_24h": max_gain,
                "max_loss_24h": max_loss
            },
            "top_performers": {
                "gainer": {
                    "symbol": gainer.symbol if gainer else None,
                    "change": gainer.change_24h if gainer else None,
                    "price": gainer.price if gainer else None
                } if gainer else None,
                "loser": {
                    "symbol": loser.symbol if loser else None,
                    "change": loser.change_24h if loser else None,
                    "price": loser.price if loser else None
                } if loser else None
            }
        }