"""
Trading Data Simulator
Generates realistic trading data for testing and demonstration
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TradingDataSimulator:
    """Simulates trading data in real-time"""
    
    def __init__(self):
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.current_prices: Dict[str, float] = {
            'BTC/USD': 43250.0,
            'ETH/USD': 2650.0,
            'EUR/USD': 1.0849,
            'GBP/USD': 1.26,
            'GOLD': 2045.30,
        }
        
    async def start(self):
        """Start the simulator"""
        if self.is_running:
            logger.warning("Simulator already running")
            return
            
        self.is_running = True
        self._task = asyncio.create_task(self._simulation_loop())
        logger.info("Trading data simulator started")
        
    async def stop(self):
        """Stop the simulator"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Trading data simulator stopped")
        
    async def _simulation_loop(self):
        """Main simulation loop"""
        while self.is_running:
            try:
                # Update prices with small random changes
                for symbol in self.current_prices:
                    change_percent = random.uniform(-0.5, 0.5) / 100
                    self.current_prices[symbol] *= (1 + change_percent)
                
                await asyncio.sleep(1)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Simulation error: {e}")
                await asyncio.sleep(5)
                
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        return self.current_prices.get(symbol)
        
    def get_all_prices(self) -> Dict[str, float]:
        """Get all current prices"""
        return self.current_prices.copy()

# Global instance
_simulator: Optional[TradingDataSimulator] = None

def get_trading_data_simulator() -> TradingDataSimulator:
    """Get or create the global simulator instance"""
    global _simulator
    if _simulator is None:
        _simulator = TradingDataSimulator()
    return _simulator
