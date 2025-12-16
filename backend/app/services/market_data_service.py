"""
Market Data Service

Tính toán market data cho preview (market cap, volume, supply, etc.)
từ simulator state và candles.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal

from .trading_data_simulator import get_trading_data_simulator


class MarketDataService:
    """Service for calculating market data from simulator state."""
    
    # Supply configuration cho các symbols
    # Trong production, có thể lưu trong system_settings
    SUPPLY_CONFIG = {
        "BTCUSDT": {
            "circulating": 19960000,  # 19.96M BTC
            "total": 19960000,
            "max": 21000000
        },
        "ETHUSDT": {
            "circulating": 120000000,  # 120M ETH
            "total": 120000000,
            "max": 0  # No max supply
        },
        "BNBUSDT": {
            "circulating": 157000000,  # 157M BNB
            "total": 157000000,
            "max": 200000000
        }
    }
    
    def __init__(self):
        self.simulator = get_trading_data_simulator()
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Lấy market data đầy đủ cho một symbol.
        
        Args:
            symbol: Symbol để lấy market data (ví dụ: "BTCUSDT")
            
        Returns:
            Dict chứa market data:
            - price: Giá hiện tại
            - change_24h: Thay đổi giá 24h
            - change_percent_24h: Thay đổi % 24h
            - market_cap: Market cap (price * circulating_supply)
            - volume_24h: Volume 24h
            - fdv: Fully Diluted Valuation
            - vol_mkt_cap_24h: Volume/Market Cap ratio
            - supply: Dict với circulating, total, max
            - high_24h, low_24h: High/Low 24h
        """
        try:
            # Lấy state từ simulator
            snapshot = await self.simulator.get_snapshot()
            
            if symbol not in snapshot.prices:
                raise ValueError(f"Symbol {symbol} not found in simulator")
            
            # Lấy price hiện tại
            current_price = float(snapshot.prices[symbol].price)
            
            # Lấy candles để tính 24h data
            candles_24h = await self._get_24h_candles(symbol)
            
            # Tính toán các chỉ số
            change_24h, change_percent_24h = self._calculate_24h_change(
                current_price, candles_24h
            )
            
            high_24h, low_24h = self._calculate_24h_high_low(candles_24h)
            
            volume_24h = self._calculate_24h_volume(candles_24h)
            
            # Lấy supply config
            supply_config = self.SUPPLY_CONFIG.get(symbol, {
                "circulating": 1000000,
                "total": 1000000,
                "max": 0
            })
            
            # Tính market cap
            market_cap = current_price * supply_config["circulating"]
            
            # Tính FDV (Fully Diluted Valuation)
            fdv = 0
            if supply_config["max"] > 0:
                fdv = current_price * supply_config["max"]
            else:
                fdv = market_cap  # Nếu không có max supply, dùng circulating
            
            # Tính Volume/Market Cap ratio
            vol_mkt_cap_24h = (volume_24h / market_cap * 100) if market_cap > 0 else 0
            
            return {
                "symbol": symbol,
                "price": current_price,
                "change_24h": change_24h,
                "change_percent_24h": change_percent_24h,
                "market_cap": market_cap,
                "volume_24h": volume_24h,
                "fdv": fdv,
                "vol_mkt_cap_24h": vol_mkt_cap_24h,
                "supply": {
                    "circulating": supply_config["circulating"],
                    "total": supply_config["total"],
                    "max": supply_config["max"]
                },
                "high_24h": high_24h,
                "low_24h": low_24h,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting market data for {symbol}: {e}")
            # Return default values on error
            return self._get_default_market_data(symbol)
    
    async def _get_24h_candles(self, symbol: str) -> List[Dict]:
        """
        Lấy candles trong 24h từ simulator.
        
        Args:
            symbol: Symbol để lấy candles
            
        Returns:
            List của candles trong 24h
        """
        try:
            # Lấy candles từ simulator
            snapshot = await self.simulator.get_snapshot()
            candles = snapshot.candles.get(symbol, [])
            
            # Filter candles trong 24h
            now = datetime.utcnow()
            cutoff = now - timedelta(hours=24)
            
            filtered_candles = []
            for candle in candles:
                if candle.start_ts >= cutoff:
                    filtered_candles.append({
                        "open": float(candle.open),
                        "high": float(candle.high),
                        "low": float(candle.low),
                        "close": float(candle.close),
                        "volume": float(candle.volume),
                        "start_ts": candle.start_ts
                    })
            
            return filtered_candles
            
        except Exception as e:
            print(f"Error getting 24h candles for {symbol}: {e}")
            return []
    
    def _calculate_24h_change(self, current_price: float, candles_24h: List[Dict]) -> tuple[float, float]:
        """
        Tính change và change % trong 24h.
        
        Args:
            current_price: Giá hiện tại
            candles_24h: List candles trong 24h
            
        Returns:
            Tuple(change_24h, change_percent_24h)
        """
        if not candles_24h:
            return 0.0, 0.0
        
        # Lấy candle cũ nhất trong 24h
        oldest_candle = candles_24h[-1]
        old_price = oldest_candle["close"]
        
        change_24h = current_price - old_price
        change_percent_24h = (change_24h / old_price * 100) if old_price > 0 else 0.0
        
        return change_24h, change_percent_24h
    
    def _calculate_24h_high_low(self, candles_24h: List[Dict]) -> tuple[float, float]:
        """
        Tính high/low trong 24h.
        
        Args:
            candles_24h: List candles trong 24h
            
        Returns:
            Tuple(high_24h, low_24h)
        """
        if not candles_24h:
            return 0.0, 0.0
        
        high_24h = max(candle["high"] for candle in candles_24h)
        low_24h = min(candle["low"] for candle in candles_24h)
        
        return high_24h, low_24h
    
    def _calculate_24h_volume(self, candles_24h: List[Dict]) -> float:
        """
        Tính volume trong 24h.
        
        Args:
            candles_24h: List candles trong 24h
            
        Returns:
            Total volume 24h
        """
        if not candles_24h:
            return 0.0
        
        total_volume = sum(candle["volume"] for candle in candles_24h)
        return total_volume
    
    def _get_default_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Return default market data khi có lỗi.
        
        Args:
            symbol: Symbol
            
        Returns:
            Default market data dict
        """
        supply_config = self.SUPPLY_CONFIG.get(symbol, {
            "circulating": 1000000,
            "total": 1000000,
            "max": 0
        })
        
        default_price = 45000.0 if "BTC" in symbol else 2500.0 if "ETH" in symbol else 300.0
        
        return {
            "symbol": symbol,
            "price": default_price,
            "change_24h": 0.0,
            "change_percent_24h": 0.0,
            "market_cap": default_price * supply_config["circulating"],
            "volume_24h": 0.0,
            "fdv": default_price * (supply_config["max"] if supply_config["max"] > 0 else supply_config["circulating"]),
            "vol_mkt_cap_24h": 0.0,
            "supply": supply_config,
            "high_24h": default_price,
            "low_24h": default_price,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_multiple_market_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Lấy market data cho nhiều symbols.
        
        Args:
            symbols: List của symbols
            
        Returns:
            Dict mapping symbol -> market data
        """
        results = {}
        
        for symbol in symbols:
            results[symbol] = await self.get_market_data(symbol)
        
        return results


# Singleton instance
market_data_service = MarketDataService()


def get_market_data_service() -> MarketDataService:
    """Get market data service instance."""
    return market_data_service
