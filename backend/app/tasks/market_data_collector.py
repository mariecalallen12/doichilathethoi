"""
Market Data Collector - Background Task
========================================

Collects and stores market data every hour for 24h change calculation
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.customization import ForexHistory, MetalHistory
from app.services.market_providers_simple import ForexProvider, MetalsProvider

logger = logging.getLogger(__name__)


class MarketDataCollector:
    """Background task to collect and store market data"""
    
    def __init__(self):
        self.forex_provider = ForexProvider()
        self.metals_provider = MetalsProvider()
        self.is_running = False
    
    async def collect_forex_prices(self, db: Session) -> int:
        """Collect and store all forex prices"""
        collected = 0
        
        for pair in self.forex_provider.PAIRS:
            try:
                data = await self.forex_provider.get_price(pair)
                
                if data and "price" in data:
                    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
                    
                    existing = db.query(ForexHistory)\
                        .filter(ForexHistory.pair == pair)\
                        .filter(ForexHistory.timestamp == current_hour)\
                        .first()
                    
                    if not existing:
                        history = ForexHistory(
                            pair=pair,
                            price=data["price"],
                            timestamp=current_hour,
                            source=data.get("source", "exchangerate-api")
                        )
                        db.add(history)
                        collected += 1
                        logger.info(f"Stored forex price: {pair} = {data['price']}")
                
            except Exception as e:
                logger.error(f"Error collecting forex price for {pair}: {e}")
        
        db.commit()
        return collected
    
    async def collect_metal_prices(self, db: Session) -> int:
        """Collect and store all metal prices"""
        collected = 0
        
        for metal in self.metals_provider.METALS:
            try:
                data = await self.metals_provider.get_price(metal)
                
                if data and "price" in data:
                    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
                    
                    existing = db.query(MetalHistory)\
                        .filter(MetalHistory.symbol == metal)\
                        .filter(MetalHistory.timestamp == current_hour)\
                        .first()
                    
                    if not existing:
                        history = MetalHistory(
                            symbol=metal,
                            price=data["price"],
                            timestamp=current_hour,
                            source=data.get("source", "metals-placeholder")
                        )
                        db.add(history)
                        collected += 1
                        logger.info(f"Stored metal price: {metal} = {data['price']}")
                
            except Exception as e:
                logger.error(f"Error collecting metal price for {metal}: {e}")
        
        db.commit()
        return collected
    
    async def collect_all(self):
        """Collect all market data"""
        db = SessionLocal()
        
        try:
            logger.info("Starting market data collection...")
            forex_count = await self.collect_forex_prices(db)
            metal_count = await self.collect_metal_prices(db)
            logger.info(f"Collection complete: {forex_count} forex, {metal_count} metal prices")
            
        except Exception as e:
            logger.error(f"Error in collection: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def run_scheduler(self, interval_hours: int = 1):
        """Run collector on schedule"""
        self.is_running = True
        logger.info(f"Collector started (interval: {interval_hours}h)")
        
        await self.collect_all()
        
        while self.is_running:
            await asyncio.sleep(interval_hours * 3600)
            await self.collect_all()
    
    def stop(self):
        """Stop the collector"""
        self.is_running = False


collector = MarketDataCollector()

async def start_collector(interval_hours: int = 1):
    await collector.run_scheduler(interval_hours)

def stop_collector():
    collector.stop()
