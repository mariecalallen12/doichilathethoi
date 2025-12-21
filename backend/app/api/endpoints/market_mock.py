"""
Mock Market Data Endpoint for Testing
Provides fallback market data when external sources are not available
"""
from fastapi import APIRouter, Query
from typing import Optional
import random
from datetime import datetime
from ...services.market_generator import generate_candles, _seed_price

router = APIRouter(tags=["market-mock"])


@router.get("/health")
async def market_mock_health():
    """Health check for mock market data"""
    return {
        "status": "healthy",
        "service": "market-mock",
        "mode": "simulation"
    }


@router.get("/ticker/{symbol}")
async def get_mock_ticker(symbol: str):
    """Get mock ticker data for a symbol"""
    base_price = _seed_price(symbol)
    change_percent = random.uniform(-5.0, 5.0)
    
    return {
        "symbol": symbol,
        "price": base_price,
        "change_24h": base_price * (change_percent / 100),
        "change_percent_24h": change_percent,
        "volume_24h": random.uniform(1000, 100000),
        "high_24h": base_price * 1.05,
        "low_24h": base_price * 0.95,
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
        "source": "mock"
    }


@router.get("/candles/{symbol}")
async def get_mock_candles(
    symbol: str,
    interval: str = Query("1h"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get mock OHLCV candles"""
    candles = generate_candles(symbol, limit, interval)
    return {
        "symbol": symbol,
        "interval": interval,
        "candles": candles,
        "source": "mock"
    }


@router.get("/orderbook/{symbol}")
async def get_mock_orderbook(
    symbol: str,
    limit: int = Query(20, ge=1, le=100)
):
    """Get mock orderbook data"""
    base_price = _seed_price(symbol)
    bids = []
    asks = []
    
    for i in range(limit):
        # Bids
        bid_price = base_price * (1 - (i + 1) * 0.0001)
        bid_volume = random.uniform(0.1, 10.0)
        bids.append([bid_price, bid_volume])
        
        # Asks
        ask_price = base_price * (1 + (i + 1) * 0.0001)
        ask_volume = random.uniform(0.1, 10.0)
        asks.append([ask_price, ask_volume])
    
    return {
        "symbol": symbol,
        "bids": bids,
        "asks": asks,
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
        "source": "mock"
    }


@router.get("/trades/{symbol}")
async def get_mock_trades(
    symbol: str,
    limit: int = Query(50, ge=1, le=500)
):
    """Get mock recent trades"""
    base_price = _seed_price(symbol)
    trades = []
    current_time = int(datetime.utcnow().timestamp() * 1000)
    
    for i in range(limit):
        price_variation = random.uniform(-0.001, 0.001)
        price = base_price * (1 + price_variation)
        quantity = random.uniform(0.01, 5.0)
        side = random.choice(['buy', 'sell'])
        
        trades.append({
            "id": str(current_time - (i * 1000)),
            "symbol": symbol,
            "price": price,
            "quantity": quantity,
            "side": side,
            "time": datetime.fromtimestamp((current_time - (i * 1000)) / 1000).isoformat(),
            "source": "mock"
        })
    
    return {
        "symbol": symbol,
        "trades": trades,
        "source": "mock"
    }


@router.get("/symbols")
async def get_mock_symbols():
    """Get list of available mock symbols"""
    return {
        "symbols": [
            {"symbol": "BTCUSDT", "base": "BTC", "quote": "USDT"},
            {"symbol": "ETHUSDT", "base": "ETH", "quote": "USDT"},
            {"symbol": "BNBUSDT", "base": "BNB", "quote": "USDT"},
            {"symbol": "SOLUSDT", "base": "SOL", "quote": "USDT"},
            {"symbol": "DOGEUSDT", "base": "DOGE", "quote": "USDT"},
        ],
        "source": "mock"
    }
