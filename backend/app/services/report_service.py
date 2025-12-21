"""
Report Service
Handles automated report generation (daily, weekly, monthly)
"""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import text
from ..db.session import async_session

logger = logging.getLogger(__name__)


async def generate_daily_report() -> Dict[str, Any]:
    """
    Generate daily system report
    """
    try:
        async with async_session() as db:
            # Get statistics for the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Count new users
            result = await db.execute(text("""
                SELECT COUNT(*) as new_users
                FROM users
                WHERE created_at >= :yesterday
            """), {"yesterday": yesterday})
            
            new_users = result.scalar() or 0
            
            # Count active trades
            result = await db.execute(text("""
                SELECT COUNT(*) as active_trades
                FROM trades
                WHERE created_at >= :yesterday
                AND status = 'active'
            """), {"yesterday": yesterday})
            
            active_trades = result.scalar() or 0
            
            report = {
                "type": "daily",
                "date": datetime.utcnow().date().isoformat(),
                "summary": f"Daily Report: {new_users} new users, {active_trades} active trades",
                "metrics": {
                    "new_users": new_users,
                    "active_trades": active_trades,
                    "period": "24h"
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Daily report generated: {report['summary']}")
            return report
            
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        return {
            "type": "daily",
            "error": str(e),
            "summary": "Report generation failed",
            "generated_at": datetime.utcnow().isoformat()
        }


async def generate_weekly_report() -> Dict[str, Any]:
    """
    Generate weekly system report
    """
    try:
        async with async_session() as db:
            # Get statistics for the last 7 days
            last_week = datetime.utcnow() - timedelta(days=7)
            
            # Count new users
            result = await db.execute(text("""
                SELECT COUNT(*) as new_users
                FROM users
                WHERE created_at >= :last_week
            """), {"last_week": last_week})
            
            new_users = result.scalar() or 0
            
            # Count total trades
            result = await db.execute(text("""
                SELECT COUNT(*) as total_trades
                FROM trades
                WHERE created_at >= :last_week
            """), {"last_week": last_week})
            
            total_trades = result.scalar() or 0
            
            report = {
                "type": "weekly",
                "week": datetime.utcnow().isocalendar()[1],
                "year": datetime.utcnow().year,
                "summary": f"Weekly Report: {new_users} new users, {total_trades} trades",
                "metrics": {
                    "new_users": new_users,
                    "total_trades": total_trades,
                    "period": "7d"
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Weekly report generated: {report['summary']}")
            return report
            
    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        return {
            "type": "weekly",
            "error": str(e),
            "summary": "Report generation failed",
            "generated_at": datetime.utcnow().isoformat()
        }


async def generate_monthly_report() -> Dict[str, Any]:
    """
    Generate monthly system report
    """
    try:
        async with async_session() as db:
            # Get statistics for the last 30 days
            last_month = datetime.utcnow() - timedelta(days=30)
            
            report = {
                "type": "monthly",
                "month": datetime.utcnow().month,
                "year": datetime.utcnow().year,
                "summary": "Monthly system report",
                "metrics": {
                    "period": "30d"
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Monthly report generated")
            return report
            
    except Exception as e:
        logger.error(f"Monthly report generation failed: {e}")
        return {
            "type": "monthly",
            "error": str(e),
            "summary": "Report generation failed",
            "generated_at": datetime.utcnow().isoformat()
        }
