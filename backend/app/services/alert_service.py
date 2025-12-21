"""
Alert Service
Handles alert rules checking and triggering
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import text
from ..db.session import async_session

logger = logging.getLogger(__name__)


async def check_alert_rules() -> List[Dict[str, Any]]:
    """
    Check all alert rules and return triggered alerts
    """
    triggered_alerts = []
    
    try:
        # Check various alert conditions
        
        # 1. Check for high trading volume
        volume_alert = await check_high_volume_alert()
        if volume_alert:
            triggered_alerts.append(volume_alert)
        
        # 2. Check for price movements
        price_alert = await check_price_movement_alert()
        if price_alert:
            triggered_alerts.append(price_alert)
        
        # 3. Check for system issues
        system_alert = await check_system_alert()
        if system_alert:
            triggered_alerts.append(system_alert)
        
        if triggered_alerts:
            logger.info(f"{len(triggered_alerts)} alerts triggered")
        
        return triggered_alerts
        
    except Exception as e:
        logger.error(f"Alert rule checking failed: {e}")
        return []


async def check_high_volume_alert() -> Dict[str, Any] | None:
    """
    Check for high trading volume alerts
    """
    try:
        async with async_session() as db:
            result = await db.execute(text("""
                SELECT COUNT(*) as count
                FROM trades
                WHERE created_at >= NOW() - INTERVAL '5 minutes'
            """))
            
            trade_count = result.scalar() or 0
            
            # Threshold: more than 100 trades in 5 minutes
            if trade_count > 100:
                return {
                    "severity": "warning",
                    "message": f"High trading volume detected: {trade_count} trades in 5 minutes",
                    "service": "trading",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "trade_count": trade_count,
                        "threshold": 100
                    }
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Volume alert check failed: {e}")
        return None


async def check_price_movement_alert() -> Dict[str, Any] | None:
    """
    Check for significant price movements
    """
    try:
        # Placeholder - implement actual price movement logic
        # This would check market data for sudden price changes
        return None
        
    except Exception as e:
        logger.error(f"Price movement alert check failed: {e}")
        return None


async def check_system_alert() -> Dict[str, Any] | None:
    """
    Check for system-level issues
    """
    try:
        import psutil
        
        # Check if database is accessible
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        
        # Check CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 95:
            return {
                "severity": "critical",
                "message": f"Critical CPU usage: {cpu_percent}%",
                "service": "system",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        if memory_percent > 95:
            return {
                "severity": "critical",
                "message": f"Critical memory usage: {memory_percent}%",
                "service": "system",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return None
        
    except Exception as e:
        logger.error(f"System alert check failed: {e}")
        return {
            "severity": "critical",
            "message": f"System health check failed: {str(e)}",
            "service": "system",
            "timestamp": datetime.utcnow().isoformat()
        }


async def create_alert_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new alert rule
    """
    try:
        # Placeholder - implement alert rule storage
        logger.info(f"Alert rule created: {rule.get('name', 'unnamed')}")
        return {
            "success": True,
            "rule_id": "generated_id",
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to create alert rule: {e}")
        raise


async def get_alert_history(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get alert history
    """
    try:
        # Placeholder - implement alert history retrieval
        return []
    except Exception as e:
        logger.error(f"Failed to get alert history: {e}")
        return []
