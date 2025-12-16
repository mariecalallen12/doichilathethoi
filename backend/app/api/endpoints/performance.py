"""
Performance Monitoring Endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict

from ...dependencies import get_current_user
from ...utils.performance_monitor import get_performance_monitor

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/metrics")
async def get_performance_metrics(
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """
    Get performance metrics summary.
    Useful for monitoring latency, throughput, and message sizes.
    """
    monitor = get_performance_monitor()
    return {
        "success": True,
        "data": monitor.get_summary(),
    }


@router.post("/metrics/reset")
async def reset_performance_metrics(
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """
    Reset performance metrics.
    Requires admin role.
    """
    monitor = get_performance_monitor()
    monitor.reset()
    return {
        "success": True,
        "message": "Performance metrics reset",
    }

