"""
OPEX Trading Endpoints
Trading API endpoints using OPEX Core backend
"""
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from ...dependencies import get_current_user
from ...models.user import User
from ...services.opex_trading_service import get_opex_trading_service, OPEXTradingService

router = APIRouter(tags=["opex-trading"])


@router.get("/health")
async def trading_health_check():
    """Health check endpoint for trading service"""
    try:
        from ...services.opex_client import get_opex_client
        opex_client = get_opex_client()
        opex_health = await opex_client.health_check()
        
        return {
            "status": opex_health.get("status", "unknown"),
            "service": "opex-trading",
            "opex_api": opex_health
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "opex-trading",
            "opex_available": False,
            "error": str(e)
        }


# Request/Response Models
class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    type: str  # "market", "limit", "stop"
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None


class OrderResponse(BaseModel):
    id: str
    user_id: int
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float]
    status: str
    filled_quantity: float
    filled_price: Optional[float]
    created_at: str
    updated_at: str


class PositionResponse(BaseModel):
    id: str
    user_id: int
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: Optional[float]
    unrealized_pnl: float
    realized_pnl: float
    leverage: float
    margin: float
    status: str
    created_at: str


@router.post("/orders", response_model=OrderResponse)
async def place_order(
    request: PlaceOrderRequest,
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Place a trading order via OPEX"""
    # Validate request data
    # 1. Validate symbol format
    if not request.symbol or not isinstance(request.symbol, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol is required and must be a string"
        )
    
    normalized_symbol = request.symbol.replace('/', '').replace('-', '').replace('_', '').upper().strip()
    if len(normalized_symbol) < 2 or len(normalized_symbol) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid symbol format: {request.symbol}"
        )
    
    # 2. Validate side
    side_lower = request.side.lower().strip()
    if side_lower not in ["buy", "sell"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid side: {request.side}. Must be 'buy' or 'sell'"
        )
    
    # 3. Validate order type
    type_lower = request.type.lower().strip()
    if type_lower not in ["market", "limit", "stop"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order type: {request.type}. Must be 'market', 'limit', or 'stop'"
        )
    
    # 4. Validate quantity
    if request.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantity must be greater than 0, got: {request.quantity}"
        )
    
    # 5. Validate price for limit/stop orders
    if type_lower in ["limit", "stop"]:
        if not request.price or request.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price is required and must be greater than 0 for {type_lower} orders"
            )
    
    # 6. Validate stop_price for stop orders
    if type_lower == "stop":
        if not request.stop_price or request.stop_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stop price is required and must be greater than 0 for stop orders"
            )
    
    # 7. Risk validation (pre-trade checks)
    try:
        from ...services.risk_validation_service import get_risk_validation_service
        risk_service = get_risk_validation_service()
        risk_result = await risk_service.validate_order(
            user_id=user.id,
            symbol=normalized_symbol,
            side=side_lower,
            order_type=type_lower,
            quantity=Decimal(str(request.quantity)),
            price=Decimal(str(request.price)) if request.price else None
        )
        # Log warnings if any
        if risk_result.get("warnings"):
            logger.warning(f"Risk validation warnings for user {user.id}: {risk_result['warnings']}")
    except HTTPException:
        raise  # Re-raise risk validation errors
    except Exception as risk_error:
        # Don't block order on risk validation errors - log and continue
        logger.warning(f"Risk validation failed (non-blocking): {risk_error}")
    
    try:
        result = await trading_service.place_order(
            user_id=user.id,
            symbol=normalized_symbol,
            side=side_lower,
            order_type=type_lower,
            quantity=Decimal(str(request.quantity)),
            price=Decimal(str(request.price)) if request.price else None,
            stop_price=Decimal(str(request.stop_price)) if request.stop_price else None
        )
        return OrderResponse(**result)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place order: {str(e)}"
        )


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    symbol: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Get user's orders from OPEX"""
    try:
        orders = await trading_service.get_orders(
            user_id=user.id,
            symbol=symbol,
            status=status,
            limit=limit
        )
        return [OrderResponse(**order) for order in orders]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orders: {str(e)}"
        )


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Cancel an order via OPEX"""
    try:
        result = await trading_service.cancel_order(
            order_id=order_id,
            user_id=user.id
        )
        return {"success": True, "order": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}"
        )


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    symbol: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Get user's positions from OPEX"""
    try:
        positions = await trading_service.get_positions(
            user_id=user.id,
            symbol=symbol
        )
        if positions:
            return [PositionResponse(**pos) for pos in positions]
        else:
            return []
    except Exception as e:
        # Return empty list on error instead of throwing
        return []


@router.post("/positions/{position_id}/close")
async def close_position(
    position_id: str,
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Close a position via OPEX"""
    try:
        result = await trading_service.close_position(
            position_id=position_id,
            user_id=user.id
        )
        return {"success": True, "position": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close position: {str(e)}"
        )


@router.get("/orderbook")
async def get_trading_orderbook(
    symbol: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Get orderbook for trading (redirects to market endpoint)"""
    from ...services.opex_market_service import get_opex_market_service
    
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol parameter is required"
        )
    
    try:
        market_service = get_opex_market_service()
        result = await market_service.get_orderbook(symbol, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orderbook: {str(e)}"
        )


@router.get("/statistics")
async def get_trading_statistics(
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Get trading statistics for the user"""
    try:
        # Get user's orders and positions
        orders = await trading_service.get_orders(user_id=user.id, limit=100)
        positions = await trading_service.get_positions(user_id=user.id)
        
        # Calculate statistics
        total_orders = len(orders) if orders else 0
        open_orders = len([o for o in orders if o.get("status") in ["pending", "open", "partial"]]) if orders else 0
        filled_orders = len([o for o in orders if o.get("status") == "filled"]) if orders else 0
        open_positions = len([p for p in positions if p.get("status") == "open"]) if positions else 0
        
        total_pnl = sum([float(p.get("unrealized_pnl", 0)) for p in positions if p.get("status") == "open"]) if positions else 0.0
        realized_pnl = sum([float(p.get("realized_pnl", 0)) for p in positions]) if positions else 0.0
        
        return {
            "orders": {
                "total": total_orders,
                "open": open_orders,
                "filled": filled_orders
            },
            "positions": {
                "open": open_positions,
                "total": len(positions) if positions else 0
            },
            "pnl": {
                "unrealized": total_pnl,
                "realized": realized_pnl,
                "total": total_pnl + realized_pnl
            }
        }
    except Exception as e:
        # Return empty statistics on error instead of throwing
        return {
            "orders": {
                "total": 0,
                "open": 0,
                "filled": 0
            },
            "positions": {
                "open": 0,
                "total": 0
            },
            "pnl": {
                "unrealized": 0.0,
                "realized": 0.0,
                "total": 0.0
            },
            "error": str(e)
        }


@router.post("/cache/invalidate")
async def invalidate_trading_cache(
    user: User = Depends(get_current_user),
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Invalidate cache for user's trading data"""
    try:
        trading_service._invalidate_user_cache(user.id)
        return {
            "status": "success",
            "message": "Cache invalidated",
            "user_id": user.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invalidate cache: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats(
    trading_service: OPEXTradingService = Depends(get_opex_trading_service)
):
    """Get cache statistics"""
    try:
        stats = trading_service.cache.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )

