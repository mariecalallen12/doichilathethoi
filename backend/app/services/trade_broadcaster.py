"""
Trade Broadcaster Service
Generates and broadcasts trade updates via WebSocket
"""
import asyncio
import random
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal

logger = logging.getLogger(__name__)


class TradeBroadcaster:
    """Service to generate and broadcast trade updates"""
    
    def __init__(self):
        self.is_running = False
        self.broadcast_task: Optional[asyncio.Task] = None
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        self.base_prices = {
            "BTCUSDT": 45000.0,
            "ETHUSDT": 2500.0,
            "BNBUSDT": 300.0,
        }
        self.current_prices = self.base_prices.copy()
        self.previous_prices = self.base_prices.copy()  # Track previous prices for change calculation
        self.trade_counters = {symbol: 0 for symbol in self.symbols}
        self.broadcast_fn: Optional[callable] = None
        self.price_broadcast_fn: Optional[callable] = None
        
        # Configurable parameters for scenarios
        self.volatility = 0.005  # Default ±0.5%
        self.trend = "sideways"  # up, down, sideways
        self.volume_multiplier = 1.0  # Volume multiplier
        
    def set_broadcast_function(self, fn: callable):
        """Set the function to call for broadcasting trades"""
        self.broadcast_fn = fn
        
    def set_price_broadcast_function(self, fn: callable):
        """Set the function to call for broadcasting price updates"""
        self.price_broadcast_fn = fn
        
    async def start(self, interval_seconds: float = 2.0):
        """Start broadcasting trades periodically"""
        if self.is_running:
            logger.warning("Trade broadcaster already running")
            return
            
        self.is_running = True
        self.broadcast_task = asyncio.create_task(
            self._broadcast_loop(interval_seconds)
        )
        logger.info(f"Trade broadcaster started (interval: {interval_seconds}s)")
        
    async def stop(self):
        """Stop broadcasting trades"""
        self.is_running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
        logger.info("Trade broadcaster stopped")
        
    async def _broadcast_loop(self, interval_seconds: float):
        """Main loop to generate and broadcast trades"""
        while self.is_running:
            try:
                # Generate and broadcast a trade for a random symbol
                symbol = random.choice(self.symbols)
                trade = self._generate_trade(symbol)
                
                if self.broadcast_fn and trade:
                    await self.broadcast_fn(symbol, trade)
                
                # Also broadcast price update with change information
                if self.price_broadcast_fn and trade:
                    previous_price = self.previous_prices.get(symbol, self.base_prices.get(symbol, 100.0))
                    current_price = trade["price"]
                    change = current_price - previous_price
                    change_percent = (change / previous_price * 100) if previous_price > 0 else 0.0
                    
                    # Broadcast price update with change info
                    await self.price_broadcast_fn(
                        symbol,
                        current_price,
                        change=change,
                        change_percent=change_percent
                    )
                    
                    # Update previous price
                    self.previous_prices[symbol] = current_price
                    
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trade broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(interval_seconds)
                
    def _generate_trade(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate a realistic trade for a symbol"""
        try:
            base_price = self.current_prices.get(symbol, self.base_prices.get(symbol, 100.0))
            
            # Apply trend-based drift
            trend_drift = 0.0
            if self.trend == "up":
                trend_drift = self.volatility * 0.5  # Positive bias
            elif self.trend == "down":
                trend_drift = -self.volatility * 0.5  # Negative bias
            # sideways has no drift (0.0)
            
            # Small price variation with volatility
            price_change = random.uniform(-self.volatility, self.volatility) + trend_drift
            new_price = base_price * (1 + price_change)
            self.current_prices[symbol] = new_price
            
            # Generate trade
            self.trade_counters[symbol] += 1
            trade_id = f"{symbol}_{int(datetime.utcnow().timestamp() * 1000)}_{self.trade_counters[symbol]}"
            
            # Random quantity with volume multiplier
            base_quantity = random.uniform(0.01, 10.0)
            quantity = round(base_quantity * self.volume_multiplier, 4)
            
            # Random side (buy/sell)
            side = "buy" if random.random() > 0.5 else "sell"
            
            trade = {
                "id": trade_id,
                "price": round(new_price, 2),
                "quantity": quantity,
                "side": side,
                "timestamp": datetime.utcnow().isoformat(),
                "time": int(datetime.utcnow().timestamp() * 1000),
            }
            
            return trade
        except Exception as e:
            logger.error(f"Error generating trade for {symbol}: {e}")
            return None
            
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent simulated trades for a symbol (for REST API)"""
        trades = []
        base_price = self.current_prices.get(symbol, self.base_prices.get(symbol, 100.0))
        
        for i in range(limit):
            price_change = random.uniform(-0.01, 0.01)
            price = round(base_price * (1 + price_change), 2)
            quantity = round(random.uniform(0.01, 10.0), 4)
            side = "buy" if random.random() > 0.5 else "sell"
            
            trade_time = int(datetime.utcnow().timestamp() * 1000) - (i * random.randint(100, 10000))
            
            trades.append({
                "id": f"{symbol}_{trade_time}_{i}",
                "price": price,
                "quantity": quantity,
                "side": side,
                "timestamp": datetime.fromtimestamp(trade_time / 1000).isoformat(),
                "time": trade_time,
            })
            
        # Sort by time (newest first)
        trades.sort(key=lambda x: x["time"], reverse=True)
        return trades


# Singleton instance
_trade_broadcaster: Optional[TradeBroadcaster] = None


def get_trade_broadcaster() -> TradeBroadcaster:
    """Get the singleton trade broadcaster instance"""
    global _trade_broadcaster
    if _trade_broadcaster is None:
        _trade_broadcaster = TradeBroadcaster()
    return _trade_broadcaster


    # Scenario control methods
    def set_volatility(self, volatility: float):
        """Set price volatility (0.001 - 0.10)"""
        self.volatility = max(0.001, min(0.10, volatility))
        logger.info(f"Volatility set to {self.volatility}")
    
    def set_trend(self, trend: str):
        """Set market trend: up, down, sideways"""
        valid_trends = ["up", "down", "sideways"]
        if trend in valid_trends:
            self.trend = trend
            logger.info(f"Trend set to {self.trend}")
        else:
            logger.warning(f"Invalid trend: {trend}. Must be one of {valid_trends}")
    
    def set_volume_multiplier(self, multiplier: float):
        """Set volume multiplier (0.1 - 10.0)"""
        self.volume_multiplier = max(0.1, min(10.0, multiplier))
        logger.info(f"Volume multiplier set to {self.volume_multiplier}")
    
    def reset_to_defaults(self):
        """Reset all parameters to defaults"""
        self.volatility = 0.005
        self.trend = "sideways"
        self.volume_multiplier = 1.0
        self.current_prices = self.base_prices.copy()
        logger.info("Broadcaster reset to defaults")
