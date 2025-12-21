#!/usr/bin/env python3
"""
Free Crypto Data Aggregator - Production Ready Implementation
============================================================

Aggregates real-time cryptocurrency data from multiple free sources:
1. Binance Market Data (100% free, no auth)
2. FreeCryptoAPI (100k requests/month free)
3. CoinGecko (10k calls/month free)

Features:
- Real-time price aggregation
- WebSocket streaming support
- Rate limiting và caching
- Error handling và fallbacks
- FastAPI REST endpoints
"""

import asyncio
import aiohttp
import websockets
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PriceData:
    """Structured price data"""
    symbol: str
    price: float
    change_24h: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    source: str = ""
    timestamp: str = ""

class FreeCryptoAggregator:
    def __init__(self):
        self.binance_base = "https://data-api.binance.vision"
        self.binance_ws = "wss://data-stream.binance.vision:443/ws"
        self.freekcrypto_base = "https://api.freecryptoapi.com/v1"
        self.freekcrypto_api_key = None  # Set your API key here
        
        # Symbol mappings
        self.symbol_mappings = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "BNB": "binancecoin",
            "ADA": "cardano",
            "XRP": "ripple",
            "SOL": "solana",
            "DOGE": "dogecoin",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LTC": "litecoin",
            "AVAX": "avalanche-2",
            "LINK": "chainlink",
            "UNI": "uniswap",
            "ATOM": "cosmos"
        }
        
        # Rate limiting
        self.last_request = {}
        self.rate_limits = {
            "binance": {"calls": 0, "window": 60},  # No limit for market data
            "freekcrypto": {"calls": 0, "window": 60, "max_calls": 100},  # 100 requests/min
            "coingecko": {"calls": 0, "window": 60, "max_calls": 30}  # 30 calls/min
        }
        
        # Cache
        self.cache = {}
        self.cache_ttl = 30  # seconds
        
    def _can_make_request(self, source: str) -> bool:
        """Check if we can make a request to the source"""
        now = time.time()
        if source not in self.last_request:
            self.last_request[source] = now
            return True
            
        if now - self.last_request[source] >= 0.1:  # 0.1 second between requests (more permissive)
            self.last_request[source] = now
            return True
        return False
    
    async def get_binance_price(self, symbol: str) -> Optional[PriceData]:
        """Get real-time price from Binance (100% free, no auth)"""
        if not self._can_make_request("binance"):
            logger.warning(f"Binance rate limit reached for {symbol}")
            return None
            
        try:
            # Binance uses USDT pairs
            binance_symbol = f"{symbol.upper()}USDT"
            url = f"{self.binance_base}/api/v3/ticker/24hr"
            params = {"symbol": binance_symbol}
            
            logger.info(f"Fetching Binance data for {symbol} -> {binance_symbol}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Binance success for {symbol}: ${data['lastPrice']}")
                        
                        return PriceData(
                            symbol=symbol.upper(),
                            price=float(data["lastPrice"]),
                            change_24h=float(data["priceChangePercent"]),
                            volume=float(data["volume"]),
                            source="binance",
                            timestamp=datetime.now().isoformat()
                        )
                    else:
                        logger.error(f"Binance HTTP {response.status} for {symbol}: {await response.text()[:200]}")
        except Exception as e:
            logger.error(f"Binance API error for {symbol}: {e}")
        
        return None
    
    async def get_freekcrypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get price from FreeCryptoAPI (free tier)"""
        if not self.freekcrypto_api_key:
            logger.warning("FreeCryptoAPI key not configured")
            return None
            
        if not self._can_make_request("freekcrypto"):
            return None
            
        try:
            url = f"{self.freekcrypto_base}/getData"
            params = {
                "symbol": symbol.upper(),
                "apiKey": self.freekcrypto_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("success") and "data" in data:
                            crypto_data = data["data"]
                            
                            return PriceData(
                                symbol=symbol.upper(),
                                price=float(crypto_data["price"]),
                                change_24h=float(crypto_data.get("change_24h", 0)),
                                volume=float(crypto_data.get("volume", 0)),
                                market_cap=float(crypto_data.get("market_cap", 0)),
                                source="freekcrypto",
                                timestamp=datetime.now().isoformat()
                            )
        except Exception as e:
            logger.error(f"FreeCryptoAPI error for {symbol}: {e}")
        
        return None
    
    async def get_coingecko_price(self, symbol: str) -> Optional[PriceData]:
        """Get price from CoinGecko (free tier)"""
        if not self._can_make_request("coingecko"):
            logger.warning(f"CoinGecko rate limit reached for {symbol}")
            return None
            
        try:
            coin_id = self.symbol_mappings.get(symbol.upper())
            if not coin_id:
                logger.warning(f"No CoinGecko mapping for {symbol}")
                return None
                
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
                "include_market_cap": "true"
            }
            
            logger.info(f"Fetching CoinGecko data for {symbol} -> {coin_id}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if coin_id in data:
                            coin_data = data[coin_id]
                            logger.info(f"CoinGecko success for {symbol}: ${coin_data['usd']}")
                            
                            return PriceData(
                                symbol=symbol.upper(),
                                price=float(coin_data["usd"]),
                                change_24h=float(coin_data.get("usd_24h_change", 0)),
                                volume=float(coin_data.get("usd_24h_vol", 0)),
                                market_cap=float(coin_data.get("usd_market_cap", 0)),
                                source="coingecko",
                                timestamp=datetime.now().isoformat()
                            )
                        else:
                            logger.error(f"CoinGecko: {coin_id} not found in response for {symbol}")
                    else:
                        logger.error(f"CoinGecko HTTP {response.status} for {symbol}: {await response.text()[:200]}")
        except Exception as e:
            logger.error(f"CoinGecko API error for {symbol}: {e}")
        
        return None
    
    async def get_aggregated_price(self, symbol: str) -> Dict[str, Any]:
        """Get aggregated price from multiple sources"""
        cache_key = f"price_{symbol.upper()}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        # Get prices from all sources concurrently
        tasks = [
            self.get_binance_price(symbol),
            self.get_freekcrypto_price(symbol),
            self.get_coingecko_price(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        valid_prices = [r for r in results if isinstance(r, PriceData)]
        
        if not valid_prices:
            return {
                "error": f"No price data available for {symbol.upper()}",
                "symbol": symbol.upper(),
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate aggregated price
        prices = [p.price for p in valid_prices]
        avg_price = sum(prices) / len(prices)
        
        # Use Binance as primary source if available, otherwise average
        binance_price = next((p for p in valid_prices if p.source == "binance"), None)
        primary_price = binance_price.price if binance_price else avg_price
        
        # Compile result
        result = {
            "symbol": symbol.upper(),
            "price": round(primary_price, 8),
            "aggregated_price": round(avg_price, 8),
            "sources": [p.__dict__ for p in valid_prices],
            "source_count": len(valid_prices),
            "price_spread": round(max(prices) - min(prices), 8),
            "change_24h": valid_prices[0].change_24h if valid_prices[0].change_24h else 0,
            "volume": valid_prices[0].volume if valid_prices[0].volume else 0,
            "market_cap": valid_prices[0].market_cap if valid_prices[0].market_cap else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        self.cache[cache_key] = (result, time.time())
        
        return result
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get aggregated prices for multiple symbols"""
        tasks = [self.get_aggregated_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            "prices": {symbol: result for symbol, result in zip(symbols, results)},
            "timestamp": datetime.now().isoformat(),
            "total_symbols": len(symbols),
            "successful_sources": len([r for r in results if "error" not in r])
        }

# FastAPI Application
app = FastAPI(
    title="Free Crypto Data API",
    description="Real-time cryptocurrency data aggregation from free sources",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global aggregator
aggregator = FreeCryptoAggregator()

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "service": "Free Crypto Data API",
        "version": "1.0.0",
        "description": "Aggregates real-time crypto data from free sources",
        "sources": {
            "binance": "Market Data (100% free, no auth)",
            "freekcrypto": "100k requests/month (free API key required)",
            "coingecko": "10k calls/month (free tier)"
        },
        "endpoints": {
            "price": "/api/price/{symbol}",
            "multiple_prices": "/api/prices/{symbols}",
            "health": "/health",
            "docs": "/docs"
        },
        "example_usage": {
            "single_price": "/api/price/BTC",
            "multiple_prices": "/api/prices/BTC,ETH,BNB"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "binance": "available",
            "freekcrypto": "available" if aggregator.freekcrypto_api_key else "api_key_required",
            "coingecko": "available"
        },
        "cache_size": len(aggregator.cache)
    }

@app.get("/api/price/{symbol}")
async def get_price(
    symbol: str,
    source: Optional[str] = Query(None, description="Specific source: binance, freecrypto, coingecko")
):
    """Get aggregated price for a single symbol"""
    symbol = symbol.upper().strip()
    
    try:
        if source:
            # Get price from specific source
            if source.lower() == "binance":
                price_data = await aggregator.get_binance_price(symbol)
            elif source.lower() == "freekcrypto":
                price_data = await aggregator.get_freekcrypto_price(symbol)
            elif source.lower() == "coingecko":
                price_data = await aggregator.get_coingecko_price(symbol)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
            
            if price_data:
                return price_data.__dict__
            else:
                raise HTTPException(status_code=404, detail=f"No data available from {source}")
        else:
            # Get aggregated price
            result = await aggregator.get_aggregated_price(symbol)
            if "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prices/{symbols}")
async def get_multiple_prices(
    symbols: str,
    limit: int = Query(20, le=50, description="Limit number of symbols")
):
    """Get aggregated prices for multiple symbols (comma-separated)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        symbol_list = symbol_list[:limit]  # Apply limit
        
        result = await aggregator.get_multiple_prices(symbol_list)
        return result
        
    except Exception as e:
        logger.error(f"Error getting multiple prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/supported-symbols")
async def get_supported_symbols():
    """Get list of supported cryptocurrency symbols"""
    return {
        "supported_symbols": list(aggregator.symbol_mappings.keys()),
        "total_supported": len(aggregator.symbol_mappings),
        "note": "Additional symbols may be available via Binance API"
    }

# WebSocket endpoint for real-time streaming (if needed)
@app.websocket("/ws/price/{symbol}")
async def websocket_price_feed(websocket, symbol: str):
    """WebSocket endpoint for real-time price updates"""
    await websocket.accept()
    symbol = symbol.upper().strip()
    
    try:
        while True:
            # Get fresh price data
            price_data = await aggregator.get_aggregated_price(symbol)
            
            # Send to client
            await websocket.send_json({
                "symbol": symbol,
                "data": price_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"WebSocket connection closed for {symbol}")
    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
        await websocket.close()

async def demo():
    """Demo function to test the aggregator"""
    print("🚀 Free Crypto Data Aggregator Demo")
    print("=" * 50)
    
    # Test single price
    print("\n📊 Testing single price for BTC...")
    btc_price = await aggregator.get_aggregated_price("BTC")
    print(json.dumps(btc_price, indent=2))
    
    # Test multiple prices
    print("\n📊 Testing multiple prices...")
    symbols = ["BTC", "ETH", "BNB", "ADA", "SOL"]
    multi_prices = await aggregator.get_multiple_prices(symbols)
    print(f"Successfully retrieved prices for {multi_prices['successful_sources']}/{len(symbols)} symbols")
    
    # Show first few results
    for symbol, data in list(multi_prices["prices"].items())[:3]:
        if "error" not in data:
            print(f"{symbol}: ${data['price']:,.2f} (sources: {data['source_count']})")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Free Crypto Data Aggregator")
    parser.add_argument("--mode", choices=["api", "demo"], default="api", 
                       help="Run as API server or demo")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")
    parser.add_argument("--api-key", help="FreeCryptoAPI key (optional)")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        aggregator.freekcrypto_api_key = args.api_key
    
    if args.mode == "demo":
        # Run demo
        asyncio.run(demo())
    else:
        # Run API server
        print("🚀 Starting Free Crypto Data API Server...")
        print(f"📡 API: http://{args.host}:{args.port}")
        print(f"📖 Docs: http://{args.host}:{args.port}/docs")
        print("📊 Sources: Binance (free), FreeCryptoAPI, CoinGecko")
        print("\nPress Ctrl+C to stop...\n")
        
        try:
            uvicorn.run(
                app, 
                host=args.host, 
                port=args.port,
                log_level="info"
            )
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")