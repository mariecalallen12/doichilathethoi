"""
Simulator Data Endpoints
Provides access to simulated trading data
"""
import random
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from ...services.trade_broadcaster import get_trade_broadcaster

router = APIRouter(tags=["simulator"])


class TradeData(BaseModel):
    id: str
    price: float
    quantity: float
    side: str
    timestamp: str
    time: int


class OrderBookLevel(BaseModel):
    price: float
    quantity: float


class OrderBookData(BaseModel):
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: int


class CandleData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@router.get("/trades")
async def get_sim_trades(
    symbol: Optional[str] = Query(None, description="Trading symbol (e.g., BTCUSDT)"),
    limit: int = Query(50, ge=1, le=500, description="Number of trades to return")
):
    """
    Get simulated trades
    
    If symbol is provided, returns trades for that symbol.
    Otherwise, returns trades for all symbols.
    """
    try:
        broadcaster = get_trade_broadcaster()
        
        if symbol:
            trades = broadcaster.get_recent_trades(symbol, limit)
            return {
                "success": True,
                "symbol": symbol,
                "trades": trades,
                "count": len(trades)
            }
        else:
            # Return trades for all symbols
            all_trades = {}
            for sym in broadcaster.symbols:
                trades = broadcaster.get_recent_trades(sym, limit // len(broadcaster.symbols))
                all_trades[sym] = trades
            return {
                "success": True,
                "trades": all_trades,
                "symbols": broadcaster.symbols
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulated trades: {str(e)}"
        )


@router.get("/orderbook")
async def get_sim_orderbook(
    symbol: Optional[str] = Query("BTCUSDT", description="Trading symbol")
):
    """Get simulated orderbook for a symbol"""
    try:
        broadcaster = get_trade_broadcaster()
        base_price = broadcaster.current_prices.get(symbol, broadcaster.base_prices.get(symbol, 100.0))
        
        # Generate simple orderbook
        bids = []
        asks = []
        
        # Generate 10 bid levels (below current price)
        for i in range(10):
            price = round(base_price * (1 - (i + 1) * 0.001), 2)
            quantity = round(random.uniform(0.1, 5.0), 4)
            bids.append({"price": price, "quantity": quantity})
            
        # Generate 10 ask levels (above current price)
        for i in range(10):
            price = round(base_price * (1 + (i + 1) * 0.001), 2)
            quantity = round(random.uniform(0.1, 5.0), 4)
            asks.append({"price": price, "quantity": quantity})
            
        return {
            "success": True,
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulated orderbook: {str(e)}"
        )


@router.get("/candles")
async def get_sim_candles(
    symbol: Optional[str] = Query("BTCUSDT", description="Trading symbol"),
    interval: str = Query("1h", description="Candle interval"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles")
):
    """Get simulated candles for a symbol"""
    try:
        from ...services.market_generator import generate_candles
        
        candles = generate_candles(symbol or "BTCUSDT", limit, interval)
        
        # Convert to expected format
        result = []
        for candle in candles:
            result.append({
                "timestamp": int(datetime.fromisoformat(candle["timestamp"].replace("Z", "+00:00")).timestamp()),
                "open": candle["open"],
                "high": candle["high"],
                "low": candle["low"],
                "close": candle["close"],
                "volume": candle["volume"]
            })
            
        return {
            "success": True,
            "symbol": symbol or "BTCUSDT",
            "interval": interval,
            "candles": result,
            "count": len(result)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulated candles: {str(e)}"
        )


@router.get("/snapshot")
async def get_sim_snapshot():
    """Get complete simulator snapshot"""
    try:
        broadcaster = get_trade_broadcaster()
        
        snapshot = {
            "prices": broadcaster.current_prices.copy(),
            "symbols": broadcaster.symbols,
            "is_running": broadcaster.is_running,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": snapshot
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulator snapshot: {str(e)}"
        )

