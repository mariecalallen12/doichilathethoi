from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List
import psutil
import time
from datetime import datetime, timedelta
import redis.asyncio as redis
from ..dependencies import get_db, get_current_user
from ..core.config import settings
import logging

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = logging.getLogger(__name__)

# In-memory logs storage (in production, use proper logging aggregation)
system_logs = []
MAX_LOGS = 1000

def add_log(service: str, level: str, message: str):
    """Add log entry to in-memory storage"""
    global system_logs
    system_logs.append({
        "id": len(system_logs),
        "timestamp": datetime.utcnow().isoformat(),
        "service": service,
        "level": level,
        "message": message
    })
    # Keep only last MAX_LOGS entries
    if len(system_logs) > MAX_LOGS:
        system_logs = system_logs[-MAX_LOGS:]

@router.get("/redis/health")
async def get_redis_health(current_user: dict = Depends(get_current_user)):
    """Get Redis health status"""
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Get Redis info
        info = await redis_client.info()
        
        # Get key count
        keys_count = await redis_client.dbsize()
        
        # Calculate memory usage
        memory_used = info.get('used_memory_human', 'N/A')
        
        # Get connection count
        connected_clients = info.get('connected_clients', 0)
        
        await redis_client.close()
        
        add_log("redis", "info", f"Health check completed - {connected_clients} connections")
        
        return {
            "status": "healthy",
            "host": "redis:6379",
            "connections": connected_clients,
            "keys": keys_count,
            "memoryUsed": memory_used,
            "version": info.get('redis_version', 'N/A'),
            "uptime": info.get('uptime_in_seconds', 0)
        }
    except Exception as e:
        add_log("redis", "error", f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Redis unhealthy: {str(e)}")

@router.get("/db/health")
async def get_db_health(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get PostgreSQL database health status"""
    try:
        # Test connection
        result = await db.execute(text("SELECT 1"))
        
        # Get database size
        size_result = await db.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """))
        db_size = size_result.scalar()
        
        # Get active connections
        conn_result = await db.execute(text("""
            SELECT count(*) FROM pg_stat_activity 
            WHERE state = 'active'
        """))
        active_connections = conn_result.scalar()
        
        # Get table count
        table_result = await db.execute(text("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        table_count = table_result.scalar()
        
        add_log("db", "info", f"Health check completed - {active_connections} active connections")
        
        return {
            "status": "healthy",
            "host": "db:5432",
            "connections": active_connections,
            "size": db_size,
            "tables": table_count,
            "version": "PostgreSQL 15"
        }
    except Exception as e:
        add_log("db", "error", f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")

@router.get("/websocket/stats")
async def get_websocket_stats(current_user: dict = Depends(get_current_user)):
    """Get WebSocket connection statistics"""
    try:
        # In production, get real stats from connection manager
        # For now, return mock data
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Count active WebSocket connections from Redis
        market_connections = await redis_client.scard("ws:market:connections") or 0
        trading_connections = await redis_client.scard("ws:trading:connections") or 0
        notification_connections = await redis_client.scard("ws:notifications:connections") or 0
        
        total = market_connections + trading_connections + notification_connections
        
        await redis_client.close()
        
        return {
            "total": total,
            "market": market_connections,
            "trading": trading_connections,
            "notifications": notification_connections
        }
    except Exception as e:
        logger.error(f"Failed to get WebSocket stats: {e}")
        return {
            "total": 0,
            "market": 0,
            "trading": 0,
            "notifications": 0
        }

@router.get("/logs")
async def get_system_logs(
    limit: int = 100,
    service: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get recent system logs"""
    logs = system_logs[-limit:]
    
    if service:
        logs = [log for log in logs if log["service"] == service]
    
    return logs

@router.get("/metrics")
async def get_system_metrics(current_user: dict = Depends(get_current_user)):
    """Get system-wide metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Network stats
        net_io = psutil.net_io_counters()
        
        add_log("backend", "info", f"Metrics collected - CPU: {cpu_percent}%, Memory: {memory_percent}%")
        
        return {
            "cpu": round(cpu_percent, 2),
            "memory": round(memory_percent, 2),
            "disk": round(disk_percent, 2),
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        add_log("backend", "error", f"Failed to collect metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts")
async def create_alert(
    alert_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Create system alert"""
    try:
        add_log(
            service=alert_data.get("service", "system"),
            level=alert_data.get("level", "warning"),
            message=alert_data.get("message", "Alert triggered")
        )
        
        # In production, send to alert management system
        return {"status": "alert_created", "data": alert_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/summary")
async def get_health_summary(current_user: dict = Depends(get_current_user)):
    """Get overall health summary of all services"""
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check Backend
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        summary["services"]["backend"] = {
            "status": "healthy",
            "metrics": {"cpu": cpu, "memory": memory}
        }
    except Exception as e:
        summary["services"]["backend"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        summary["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        summary["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
    
    return summary
