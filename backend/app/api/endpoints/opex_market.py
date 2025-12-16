"""
OPEX Market Data Endpoints
Market data API endpoints using OPEX Core
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from ...services.opex_market_service import get_opex_market_service, OPEXMarketService

router = APIRouter(tags=["opex-market"])


@router.get("/health")
async def market_health_check():
    """Health check endpoint for market service"""
    try:
        from ...services.opex_client import get_opex_client
        opex_client = get_opex_client()
        opex_health = await opex_client.health_check()
        
        return {
            "status": opex_health.get("status", "unknown"),
            "service": "opex-market",
            "opex_api": opex_health
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "opex-market",
            "opex_available": False,
            "error": str(e)
        }


# Response Models
class OrderBookResponse(BaseModel):
    symbol: str
    bids: List[List[float]]  # [price, quantity]
    asks: List[List[float]]  # [price, quantity]
    timestamp: int


class TradeResponse(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: float
    price: float
    time: str


class CandleResponse(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class TickerResponse(BaseModel):
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float


class SymbolResponse(BaseModel):
    symbol: str
    base: str
    quote: str


@router.get("/orderbook/{symbol}", response_model=OrderBookResponse)
async def get_orderbook(
    symbol: str,
    limit: int = Query(20, ge=1, le=100),
    market_service: OPEXMarketService = Depends(get_opex_market_service)
):
    """Get orderbook for a symbol from OPEX"""
    try:
        result = await market_service.get_orderbook(symbol, limit)
        if result:
            return OrderBookResponse(**result)
        else:
            # Return empty orderbook if no data
            return OrderBookResponse(
                symbol=symbol,
                bids=[],
                asks=[],
                timestamp=int(__import__('time').time() * 1000)
            )
    except Exception as e:
        # Return empty orderbook on error instead of throwing
        return OrderBookResponse(
            symbol=symbol,
            bids=[],
            asks=[],
            timestamp=int(__import__('time').time() * 1000)
        )


@router.get("/trades/{symbol}", response_model=List[TradeResponse])
async def get_trades(
    symbol: str,
    limit: int = Query(50, ge=1, le=500),
    market_service: OPEXMarketService = Depends(get_opex_market_service)
):
    """Get recent trades for a symbol from OPEX"""
    try:
        trades = await market_service.get_trades(symbol, limit)
        return [TradeResponse(**trade) for trade in trades]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trades: {str(e)}"
        )


@router.get("/candles/{symbol}", response_model=List[CandleResponse])
async def get_candles(
    symbol: str,
    interval: str = Query("1h", regex="^(1m|5m|15m|30m|1h|4h|1d|1w)$"),
    limit: int = Query(100, ge=1, le=1000),
    market_service: OPEXMarketService = Depends(get_opex_market_service)
):
    """Get OHLCV candles for a symbol from OPEX"""
    try:
        candles = await market_service.get_candles(symbol, interval, limit)
        return [CandleResponse(**candle) for candle in candles]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get candles: {str(e)}"
        )


@router.get("/ticker/{symbol}", response_model=TickerResponse)
async def get_ticker(
    symbol: str,
    market_service: OPEXMarketService = Depends(get_opex_market_service)
):
    """Get ticker data for a symbol from OPEX"""
    try:
        result = await market_service.get_ticker(symbol)
        return TickerResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ticker: {str(e)}"
        )


@router.get("/symbols", response_model=List[SymbolResponse])
async def get_symbols(
    market_service: OPEXMarketService = Depends(get_opex_market_service)
):
    """Get available trading symbols from OPEX"""
    try:
        symbols = await market_service.get_symbols()
        if symbols:
            return [SymbolResponse(**symbol) for symbol in symbols]
        else:
            # Return fallback symbols if OPEX unavailable
            return [
                SymbolResponse(symbol="BTCUSDT", base="BTC", quote="USDT"),
                SymbolResponse(symbol="ETHUSDT", base="ETH", quote="USDT"),
                SymbolResponse(symbol="BNBUSDT", base="BNB", quote="USDT")
            ]
    except Exception as e:
        # Return fallback symbols on error
        return [
            SymbolResponse(symbol="BTCUSDT", base="BTC", quote="USDT"),
            SymbolResponse(symbol="ETHUSDT", base="ETH", quote="USDT"),
            SymbolResponse(symbol="BNBUSDT", base="BNB", quote="USDT")
        ]

