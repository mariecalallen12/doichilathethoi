"""
Market data endpoints
Implements real-time market data functionality with customization support
Enhanced with Twelve Data + Self-calculated 24h change
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import random
import aiohttp
import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.middleware.auth import get_current_user
from app.db.session import get_db
from app.models.market import MarketDataHistory, MarketPrice as MarketPriceModel, MarketAnalysis
from app.models.user import User
from app.services.market_generator import generate_candles
from app.services.customization_engine import customization_engine
from app.services.market_data_enhanced import get_enhanced_aggregator
from app.core.config import settings
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()
security = HTTPBearer()

# Define response models locally since they're used here
class OrderBookResponse(BaseModel):
    symbol: str
    bids: List[Dict[str, Any]]
    asks: List[Dict[str, Any]]
    last_update_id: Optional[int] = None
    timestamp: Optional[int] = None

class MarketPricesResponse(BaseModel):
    prices: Dict[str, Any]
    timestamp: datetime
    symbols: List[str]
    data_source: str

class TradeHistoryResponse(BaseModel):
    symbol: str
    trades: List[Dict[str, Any]]
    timestamp: Optional[datetime] = None

# Market data sources configuration (from Next.js source)
MARKET_DATA_SOURCES = {
    "COINGECKO": {
        "base_url": "https://api.coingecko.com/api/v3",
        "rate_limit": 100  # requests per minute
    },
    "BINANCE": {
        "base_url": "https://api.binance.com/api/v3", 
        "rate_limit": 1200  # requests per minute
    },
    "EXCHANGERATE": {
        "base_url": "https://api.exchangerate-api.com/v4/latest",
        "rate_limit": 1500  # requests per month
    }
}

# Cache for market data
price_cache = {}
CACHE_DURATION = 5  # seconds

class MarketDataService:
    """Market data service with real API integration"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_with_timeout(self, url: str, timeout: int = 5, **kwargs) -> Optional[Dict]:
        """Fetch data with timeout and error handling"""
        try:
            async with self.session.get(url, timeout=timeout, **kwargs) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
            return None

    async def get_crypto_prices(self, symbols: List[str]) -> Dict[str, MarketPriceModel]:
        """Get real-time crypto prices using Binance and CoinGecko APIs"""
        prices = {}
        
        # Try Binance first (fastest and most reliable)
        for symbol in symbols:
            cache_key = f"binance_{symbol}"
            cached = price_cache.get(cache_key)
            
            if cached and (datetime.now() - cached['timestamp']).seconds < CACHE_DURATION:
                prices[symbol] = cached['data']
                continue

            # Fetch from Binance
            binance_symbol = symbol.replace('USDT', 'USDT')
            url = f"{MARKET_DATA_SOURCES['BINANCE']['base_url']}/ticker/24hr?symbol={binance_symbol}"
            
            data = await self.fetch_with_timeout(url)
            if data and isinstance(data, dict):
                try:
                    price_data = MarketPriceModel(
                        symbol=symbol,
                        price=float(data.get('lastPrice', 0)),
                        change_24h=float(data.get('priceChange', 0)),
                        change_percent=float(data.get('priceChangePercent', 0)) / 100,
                        volume_24h=float(data.get('volume', 0)),
                        high_24h=float(data.get('highPrice', 0)),
                        low_24h=float(data.get('lowPrice', 0)),
                        timestamp=int(datetime.now().timestamp())
                    )
                    
                    # Cache the result
                    price_cache[cache_key] = {
                        'data': price_data,
                        'timestamp': datetime.now()
                    }
                    prices[symbol] = price_data
                    
                except (ValueError, TypeError) as e:
                    print(f"Error parsing Binance data for {symbol}: {e}")
        
        # Fallback to CoinGecko for missing symbols
        missing_symbols = [s for s in symbols if s not in prices]
        if missing_symbols:
            coin_ids = []
            for symbol in missing_symbols:
                coin_symbol = symbol.replace('USDT', '').lower()
                # Coin mapping
                coin_map = {
                    'btc': 'bitcoin',
                    'eth': 'ethereum', 
                    'bnb': 'binancecoin',
                    'ada': 'cardano',
                    'dot': 'polkadot',
                    'link': 'chainlink',
                    'ltc': 'litecoin',
                    'xrp': 'ripple',
                    'bch': 'bitcoin-cash',
                    'sol': 'solana',
                    'matic': 'polygon',
                    'avax': 'avalanche-2'
                }
                coin_id = coin_map.get(coin_symbol, coin_symbol)
                coin_ids.append(coin_id)
            
            if coin_ids:
                url = f"{MARKET_DATA_SOURCES['COINGECKO']['base_url']}/coins/markets?vs_currency=usd&ids={','.join(coin_ids)}"
                
                data = await self.fetch_with_timeout(url)
                if data and isinstance(data, list):
                    for coin in data:
                        try:
                            symbol = f"{coin['symbol'].upper()}USDT"
                            if symbol in missing_symbols:
                                price_data = MarketPriceModel(
                                    symbol=symbol,
                                    price=float(coin.get('current_price', 0)),
                                    change_24h=float(coin.get('price_change_24h', 0)),
                                    change_percent=float(coin.get('price_change_percentage_24h', 0)) / 100,
                                    volume_24h=float(coin.get('total_volume', 0)),
                                    high_24h=float(coin.get('high_24h', 0)),
                                    low_24h=float(coin.get('low_24h', 0)),
                                    timestamp=int(datetime.now().timestamp())
                                )
                                
                                cache_key = f"coingecko_{symbol}"
                                price_cache[cache_key] = {
                                    'data': price_data,
                                    'timestamp': datetime.now()
                                }
                                prices[symbol] = price_data
                                
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing CoinGecko data for {coin.get('symbol', 'unknown')}: {e}")
        
        return prices

    async def get_forex_prices(self, symbols: List[str]) -> Dict[str, MarketPriceModel]:
        """Get real-time forex prices using ExchangeRate API"""
        prices = {}
        
        try:
            url = f"{MARKET_DATA_SOURCES['EXCHANGERATE']['base_url']}/USD"
            data = await self.fetch_with_timeout(url)
            
            if data and isinstance(data, dict):
                rates = data.get('rates', {})
                
                for symbol in symbols:
                    # Parse currency pair
                    if '/' in symbol:
                        base, quote = symbol.split('/')
                    else:
                        base, quote = symbol[:3], symbol[3:6]
                    
                    try:
                        # Calculate exchange rate
                        if base == 'USD':
                            price = rates.get(quote, 1.0)
                        elif quote == 'USD':
                            price = 1.0 / (rates.get(base, 1.0))
                        else:
                            # Cross currency pair
                            base_to_usd = 1.0 / (rates.get(base, 1.0))
                            usd_to_quote = rates.get(quote, 1.0)
                            price = base_to_usd * usd_to_quote
                        
                        # Add realistic market movement
                        volatility = 0.02  # 2% daily volatility
                        change = (random.random() - 0.5) * price * volatility
                        current_price = price + change
                        
                        price_data = MarketPriceModel(
                            symbol=symbol,
                            price=round(current_price, 4),
                            change_24h=round(change, 4),
                            change_percent=round((change / price) * 10000, 4),
                            volume_24h=random.randint(100000, 100000000),
                            high_24h=round((price + abs(change) * 2) * 10000) / 10000,
                            low_24h=round((price - abs(change) * 2) * 10000) / 10000,
                            timestamp=int(datetime.now().timestamp())
                        )
                        
                        prices[symbol] = price_data
                        
                    except (ValueError, TypeError, ZeroDivisionError) as e:
                        print(f"Error calculating forex rate for {symbol}: {e}")
                        
        except Exception as e:
            print(f"Error fetching forex data: {e}")
        
        return prices

    def generate_fallback_data(self, symbol: str) -> MarketPriceModel:
        """Generate realistic fallback data for missing symbols"""
        base_price = random.uniform(0.1, 100000)  # Random base price
        change = (random.random() - 0.5) * base_price * 0.05  # 5% max change
        
        return MarketPrice(
            symbol=symbol,
            price=round(base_price + change, 2),
            change_24h=round(change, 2),
            change_percent=round((change / base_price) * 100, 2),
            volume_24h=random.randint(10000, 100000000),
            high_24h=round((base_price + abs(change) * 2), 2),
            low_24h=round((base_price - abs(change) * 2), 2),
            timestamp=int(datetime.now().timestamp())
        )

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get real order book data from database - DEPRECATED: Use endpoint directly"""
        # This method is deprecated - order book now comes from real trading orders
        # Kept for backward compatibility but should not be used
        return {
            'symbol': symbol,
            'bids': [],
            'asks': [],
            'last_update_id': int(datetime.now().timestamp())
        }

    async def get_trade_history(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Generate realistic trade history"""
        trades = []
        
        # Get base price from market data
        base_price = 50000
        cache_key = f"price_{symbol}"
        if cache_key in price_cache:
            base_price = price_cache[cache_key]['data'].price
        
        for i in range(limit):
            price_variation = (random.random() - 0.5) * base_price * 0.01
            price = round((base_price + price_variation) * 100) / 100
            quantity = round((random.uniform(0.1, 5)) * 1000) / 1000
            is_buyer = random.random() > 0.5
            
            trade_time = int(datetime.now().timestamp() * 1000) - (i * random.randint(100, 10000))
            
            trades.append({
                'id': f"trade_{int(datetime.now().timestamp())}_{i}",
                'price': price,
                'quantity': quantity,
                'time': trade_time,
                'timestamp': datetime.fromtimestamp(trade_time / 1000).isoformat(),
                'is_buyer_maker': not is_buyer,
                'is_best_match': random.random() > 0.7
            })
        
        # Sort by time (newest first)
        trades.sort(key=lambda x: x['time'], reverse=True)
        
        return trades


@router.get("/prices", response_model=MarketPricesResponse)
async def get_market_prices(
    symbol: Optional[str] = Query(None, description="Single symbol to fetch"),
    symbols: Optional[str] = Query(None, description="Comma-separated symbols"),
    db: Session = Depends(get_db)
):
    """
    Get real-time market prices with REAL 24h change
    
    Data sources:
    - Crypto: Binance (100% real - price + 24h change + volume)
    - Forex: Twelve Data API (primary) → Self-calculated (fallback)
    - Metals: Self-calculated from hourly stored data
    
    Supports customization via X-Session-Id header
    """
    try:
        # Get enhanced aggregator with database session
        aggregator = get_enhanced_aggregator(db)
        
        # Fetch data using enhanced aggregator
        if symbol:
            # Single symbol
            raw_data = await aggregator.get_price(symbol.upper())
            if raw_data:
                prices_data = {symbol.upper(): raw_data}
            else:
                prices_data = {}
        elif symbols:
            # Multiple symbols
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
            prices_data = {}
            for sym in symbol_list:
                data = await aggregator.get_price(sym)
                if data:
                    prices_data[sym] = data
        else:
            # All available prices
            prices_data = await aggregator.get_all_prices()
        
        # Apply customizations to each symbol
        for sym, data in prices_data.items():
            if data and "price" in data:
                # Apply price modification
                data["price"] = customization_engine.apply_price_modification(
                    sym, data["price"]
                )
                # Apply change modification
                if "change_24h" in data:
                    data["change_24h"] = customization_engine.apply_change_modification(
                        sym, data["change_24h"]
                    )
                # Apply volume customization
                if "volume" in data:
                    data["volume"] = customization_engine.apply_volume_customization(
                        sym, data["volume"]
                    )
        
        logging.info(f"Market data fetched (enhanced): {len(prices_data)} symbols")
        
        return MarketPricesResponse(
            prices=prices_data,
            timestamp=datetime.now(),
            symbols=list(prices_data.keys()),
            data_source="enhanced+customized"
        )
        
    except Exception as e:
        print(f"Get market prices error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market data"
        )

@router.get("/trade-history/{symbol}", response_model=TradeHistoryResponse)
async def get_trade_history(
    symbol: str,
    limit: int = Query(50, ge=1, le=200, description="Number of trades to return"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get trade history for a symbol"""
    try:
        async with MarketDataService() as service:
            trades_data = await service.get_trade_history(symbol, limit)
            
            return TradeHistoryResponse(
                symbol=symbol,
                trades=trades_data,
                timestamp=datetime.now()
            )
            
    except Exception as e:
        print(f"Get trade history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy lịch sử giao dịch"
        )


@router.get("/historical-data/{symbol}")
async def get_historical_data(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles to return"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical market data (OHLCV) for a symbol"""
    try:
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Query database for historical data
        query = db.query(MarketDataHistory).filter(
            MarketDataHistory.symbol == symbol.upper(),
            MarketDataHistory.timeframe == timeframe,
            MarketDataHistory.timestamp >= start_date,
            MarketDataHistory.timestamp <= end_date
        ).order_by(MarketDataHistory.timestamp.desc()).limit(limit)
        
        history_data = query.all()
        
        # Format response
        candles = []
        for candle in reversed(history_data):  # Reverse to get chronological order
            candles.append({
                "timestamp": candle.timestamp.isoformat(),
                "open": float(candle.open_price),
                "high": float(candle.high_price),
                "low": float(candle.low_price),
                "close": float(candle.close_price),
                "volume": float(candle.volume),
                "number_of_trades": candle.number_of_trades or 0
            })
        
        # Nếu không có dữ liệu thật, sinh dữ liệu fallback từ generator
        if not candles:
            candles = generate_candles(symbol, limit=limit, timeframe=timeframe)
        
        return {
            "success": True,
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": candles,
            "count": len(candles),
            "message": "No historical data available (using generated fallback)" if not history_data else None
        }
        
    except Exception as e:
        print(f"Get historical data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy dữ liệu lịch sử"
        )


@router.get("/analysis/{symbol}")
async def get_market_analysis(
    symbol: str,
    analysis_type: str = Query("technical", description="Analysis type: technical, fundamental, sentiment"),
    timeframe: str = Query("1d", description="Timeframe for analysis"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get market analysis for a symbol"""
    try:
        # Query latest analysis from database
        analysis = db.query(MarketAnalysis).filter(
            MarketAnalysis.symbol == symbol.upper(),
            MarketAnalysis.analysis_type == analysis_type,
            MarketAnalysis.timeframe == timeframe
        ).order_by(MarketAnalysis.analysis_date.desc()).first()
        
        if analysis:
            return {
                "success": True,
                "symbol": symbol.upper(),
                "analysis_type": analysis_type,
                "timeframe": timeframe,
                "indicators": analysis.indicators or {},
                "signals": analysis.signals or [],
                "sentiment_score": float(analysis.sentiment_score) if analysis.sentiment_score else None,
                "price_prediction": analysis.price_prediction or {},
                "confidence_score": float(analysis.confidence_score) if analysis.confidence_score else None,
                "analysis_date": analysis.analysis_date.isoformat(),
                "source": analysis.source
            }
        
        # Return empty analysis if not in DB - no mock/sample data
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market analysis not found for symbol {symbol.upper()} with type {analysis_type} and timeframe {timeframe}"
        )
        
    except Exception as e:
        print(f"Get market analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy phân tích thị trường"
        )


@router.get("/data-feeds")
async def get_data_feeds(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available market data feeds and their status"""
    try:
        # Get active market prices count
        active_prices_count = db.query(MarketPriceModel).filter(
            MarketPriceModel.is_active == True
        ).count()
        
        # Get latest update time
        latest_update = db.query(MarketPriceModel.last_update).filter(
            MarketPriceModel.is_active == True
        ).order_by(MarketPriceModel.last_update.desc()).first()
        
        return {
            "success": True,
            "feeds": [
                {
                    "name": "Binance",
                    "type": "crypto",
                    "status": "active",
                    "rate_limit": "1200 req/min",
                    "supported_symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT"]
                },
                {
                    "name": "CoinGecko",
                    "type": "crypto",
                    "status": "active",
                    "rate_limit": "100 req/min",
                    "supported_symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "LTCUSDT"]
                },
                {
                    "name": "ExchangeRate API",
                    "type": "forex",
                    "status": "active",
                    "rate_limit": "1500 req/month",
                    "supported_symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
                }
            ],
            "statistics": {
                "active_symbols": active_prices_count,
                "last_update": latest_update[0].isoformat() if latest_update and latest_update[0] else None,
                "total_feeds": 3
            }
        }
        
    except Exception as e:
        print(f"Get data feeds error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy thông tin data feeds"
        )


@router.get("/instruments")
async def get_market_instruments():
    """
    Get list of available trading instruments/symbols
    Public endpoint - no authentication required
    """
    try:
        # Define available instruments organized by category
        instruments = {
            "forex": [
                {"symbol": "EURUSD", "name": "Euro / US Dollar", "category": "forex", "base": "EUR", "quote": "USD"},
                {"symbol": "GBPUSD", "name": "British Pound / US Dollar", "category": "forex", "base": "GBP", "quote": "USD"},
                {"symbol": "USDJPY", "name": "US Dollar / Japanese Yen", "category": "forex", "base": "USD", "quote": "JPY"},
                {"symbol": "AUDUSD", "name": "Australian Dollar / US Dollar", "category": "forex", "base": "AUD", "quote": "USD"},
                {"symbol": "USDCHF", "name": "US Dollar / Swiss Franc", "category": "forex", "base": "USD", "quote": "CHF"},
                {"symbol": "USDCAD", "name": "US Dollar / Canadian Dollar", "category": "forex", "base": "USD", "quote": "CAD"},
                {"symbol": "NZDUSD", "name": "New Zealand Dollar / US Dollar", "category": "forex", "base": "NZD", "quote": "USD"},
            ],
            "crypto": [
                {"symbol": "BTCUSDT", "name": "Bitcoin / USDT", "category": "crypto", "base": "BTC", "quote": "USDT"},
                {"symbol": "ETHUSDT", "name": "Ethereum / USDT", "category": "crypto", "base": "ETH", "quote": "USDT"},
                {"symbol": "BNBUSDT", "name": "Binance Coin / USDT", "category": "crypto", "base": "BNB", "quote": "USDT"},
                {"symbol": "SOLUSDT", "name": "Solana / USDT", "category": "crypto", "base": "SOL", "quote": "USDT"},
                {"symbol": "ADAUSDT", "name": "Cardano / USDT", "category": "crypto", "base": "ADA", "quote": "USDT"},
                {"symbol": "DOTUSDT", "name": "Polkadot / USDT", "category": "crypto", "base": "DOT", "quote": "USDT"},
                {"symbol": "LINKUSDT", "name": "Chainlink / USDT", "category": "crypto", "base": "LINK", "quote": "USDT"},
            ],
            "commodities": [
                {"symbol": "GOLD", "name": "Gold", "category": "commodities", "base": "XAU", "quote": "USD"},
                {"symbol": "SILVER", "name": "Silver", "category": "commodities", "base": "XAG", "quote": "USD"},
                {"symbol": "OIL", "name": "Crude Oil", "category": "commodities", "base": "CL", "quote": "USD"},
            ],
            "indices": [
                {"symbol": "SPX500", "name": "S&P 500", "category": "indices", "base": "SPX", "quote": "USD"},
                {"symbol": "NAS100", "name": "NASDAQ 100", "category": "indices", "base": "NDX", "quote": "USD"},
                {"symbol": "DJ30", "name": "Dow Jones 30", "category": "indices", "base": "DJI", "quote": "USD"},
            ]
        }
        
        # Flatten list for compatibility
        all_instruments = []
        for category, items in instruments.items():
            all_instruments.extend(items)
        
        return {
            "success": True,
            "instruments": all_instruments,
            "by_category": instruments,
            "total_count": len(all_instruments),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Get market instruments error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách công cụ giao dịch"
        )


@router.get("/summary")
async def get_market_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get market summary with key statistics"""
    try:
        # Get top symbols by volume
        top_symbols = db.query(MarketPriceModel).filter(
            MarketPriceModel.is_active == True
        ).order_by(MarketPriceModel.volume_24h.desc()).limit(10).all()
        
        symbols_summary = []
        total_volume_24h = 0
        
        for price in top_symbols:
            symbols_summary.append({
                "symbol": price.symbol,
                "price": float(price.price),
                "change_24h": float(price.price_change_percent_24h) if price.price_change_percent_24h else 0,
                "volume_24h": float(price.volume_24h) if price.volume_24h else 0
            })
            if price.volume_24h:
                total_volume_24h += float(price.volume_24h)
        
        # Calculate market stats
        gainers = [s for s in symbols_summary if s["change_24h"] > 0]
        losers = [s for s in symbols_summary if s["change_24h"] < 0]
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "market_statistics": {
                "total_symbols": len(symbols_summary),
                "total_volume_24h": round(total_volume_24h, 2),
                "gainers": len(gainers),
                "losers": len(losers),
                "unchanged": len(symbols_summary) - len(gainers) - len(losers)
            },
            "top_symbols": symbols_summary[:5],
            "top_gainers": sorted(gainers, key=lambda x: x["change_24h"], reverse=True)[:3],
            "top_losers": sorted(losers, key=lambda x: x["change_24h"])[:3]
        }
        
    except Exception as e:
        print(f"Get market summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy tóm tắt thị trường"
        )