"""
Admin Simulation Control Endpoints
Endpoints for controlling market data simulation
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import time

from ...dependencies import get_current_user, require_role
from ...db.session import get_db
from ...models.user import User

router = APIRouter(tags=["admin-simulation"])


# Request Models
class SimulationConfigRequest(BaseModel):
    interval_seconds: Optional[float] = None
    symbols: Optional[List[str]] = None
    volatility: Optional[float] = None
    trend: Optional[str] = None
    volume_multiplier: Optional[float] = None


# Response Models
class SimulationStatusResponse(BaseModel):
    is_running: bool
    current_scenario: Optional[dict]
    symbols: List[str]
    current_prices: dict
    interval_seconds: float
    uptime_seconds: int
    volatility: float
    trend: str
    volume_multiplier: float


@router.get("/simulation/status", response_model=SimulationStatusResponse)
async def get_simulation_status(
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get current simulation status"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        from ...services.scenario_manager import get_scenario_manager
        
        broadcaster = get_trade_broadcaster()
        scenario_mgr = get_scenario_manager()
        
        # Calculate uptime
        uptime = 0
        if broadcaster.is_running and hasattr(broadcaster, 'start_time'):
            uptime = int(time.time() - broadcaster.start_time)
        
        # Get active scenario from DB
        active_scenario = scenario_mgr.get_active_scenario(db)
        
        return {
            "is_running": broadcaster.is_running,
            "current_scenario": active_scenario,
            "symbols": broadcaster.symbols,
            "current_prices": broadcaster.current_prices,
            "interval_seconds": 2.0,
            "uptime_seconds": uptime,
            "volatility": getattr(broadcaster, 'volatility', 0.005),
            "trend": getattr(broadcaster, 'trend', 'sideways'),
            "volume_multiplier": getattr(broadcaster, 'volume_multiplier', 1.0)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulation status: {str(e)}"
        )


@router.post("/simulation/start")
async def start_simulation(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Start market data simulation"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        
        broadcaster = get_trade_broadcaster()
        
        if broadcaster.is_running:
            return {
                "success": True,
                "message": "Simulation is already running"
            }
        
        # Store start time
        broadcaster.start_time = time.time()
        
        await broadcaster.start(interval_seconds=2.0)
        
        return {
            "success": True,
            "message": "Simulation started successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start simulation: {str(e)}"
        )


@router.post("/simulation/stop")
async def stop_simulation(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Stop market data simulation"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        
        broadcaster = get_trade_broadcaster()
        
        if not broadcaster.is_running:
            return {
                "success": True,
                "message": "Simulation is not running"
            }
        
        await broadcaster.stop()
        
        return {
            "success": True,
            "message": "Simulation stopped successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop simulation: {str(e)}"
        )


@router.post("/simulation/restart")
async def restart_simulation(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Restart simulation"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        
        broadcaster = get_trade_broadcaster()
        
        # Stop if running
        if broadcaster.is_running:
            await broadcaster.stop()
        
        # Wait a bit
        import asyncio
        await asyncio.sleep(0.5)
        
        # Start again
        broadcaster.start_time = time.time()
        await broadcaster.start(interval_seconds=2.0)
        
        return {
            "success": True,
            "message": "Simulation restarted successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart simulation: {str(e)}"
        )


@router.put("/simulation/config")
async def update_simulation_config(
    config: SimulationConfigRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Update simulation configuration"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        
        broadcaster = get_trade_broadcaster()
        was_running = broadcaster.is_running
        
        # Update interval (requires restart)
        if config.interval_seconds is not None:
            if was_running:
                await broadcaster.stop()
                import asyncio
                await asyncio.sleep(0.5)
                broadcaster.start_time = time.time()
                await broadcaster.start(interval_seconds=config.interval_seconds)
        
        # Update symbols
        if config.symbols is not None:
            broadcaster.symbols = config.symbols
            # Initialize prices for new symbols
            for symbol in config.symbols:
                if symbol not in broadcaster.current_prices:
                    broadcaster.current_prices[symbol] = broadcaster.base_prices.get(symbol, 100.0)
                    broadcaster.trade_counters[symbol] = 0
        
        # Update volatility
        if config.volatility is not None:
            broadcaster.set_volatility(config.volatility)
        
        # Update trend
        if config.trend is not None:
            broadcaster.set_trend(config.trend)
        
        # Update volume multiplier
        if config.volume_multiplier is not None:
            broadcaster.set_volume_multiplier(config.volume_multiplier)
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "config": {
                "interval_seconds": config.interval_seconds,
                "symbols": config.symbols or broadcaster.symbols,
                "volatility": broadcaster.volatility,
                "trend": broadcaster.trend,
                "volume_multiplier": broadcaster.volume_multiplier
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update config: {str(e)}"
        )


@router.post("/simulation/reset-prices")
async def reset_prices(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Reset all prices to base values"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        
        broadcaster = get_trade_broadcaster()
        broadcaster.current_prices = broadcaster.base_prices.copy()
        broadcaster.previous_prices = broadcaster.base_prices.copy()
        
        # Reset trade counters
        broadcaster.trade_counters = {symbol: 0 for symbol in broadcaster.symbols}
        
        return {
            "success": True,
            "message": "Prices reset to base values",
            "prices": broadcaster.current_prices
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset prices: {str(e)}"
        )


@router.get("/simulation/metrics")
async def get_simulation_metrics(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """Get simulation performance metrics"""
    try:
        from ...services.trade_broadcaster import get_trade_broadcaster
        
        broadcaster = get_trade_broadcaster()
        
        # Calculate metrics
        total_trades = sum(broadcaster.trade_counters.values())
        
        price_changes = {}
        for symbol in broadcaster.symbols:
            base = broadcaster.base_prices.get(symbol, 0)
            current = broadcaster.current_prices.get(symbol, 0)
            if base > 0:
                change_percent = ((current - base) / base) * 100
                price_changes[symbol] = {
                    "base": base,
                    "current": current,
                    "change": current - base,
                    "change_percent": round(change_percent, 2)
                }
        
        return {
            "total_trades_generated": total_trades,
            "trades_per_symbol": broadcaster.trade_counters,
            "price_changes": price_changes,
            "is_running": broadcaster.is_running,
            "config": {
                "volatility": broadcaster.volatility,
                "trend": broadcaster.trend,
                "volume_multiplier": broadcaster.volume_multiplier
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )
