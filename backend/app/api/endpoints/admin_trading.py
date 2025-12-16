"""
Admin Trading Endpoints
Admin endpoints for managing trading operations via OPEX
Allows admins to edit orders, positions, prices, and balances
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from decimal import Decimal

from ...dependencies import get_current_user, require_role
from ...db.session import get_db
from ...models.user import User
from ...services.opex_client import get_opex_client, OPEXClient
from sqlalchemy.orm import Session

router = APIRouter(tags=["admin-trading"])


# Request Models
class UpdateOrderRequest(BaseModel):
    price: Optional[float] = None
    quantity: Optional[float] = None
    status: Optional[str] = None


class UpdatePositionRequest(BaseModel):
    quantity: Optional[float] = None
    entry_price: Optional[float] = None
    leverage: Optional[float] = None


class UpdatePriceRequest(BaseModel):
    price: float
    reason: Optional[str] = None


class UpdateBalanceRequest(BaseModel):
    asset: str
    amount: float
    operation: str  # "add", "subtract", "set"
    reason: Optional[str] = None


@router.put("/trading/orders/{order_id}")
async def admin_update_order(
    order_id: str,
    request: UpdateOrderRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    opex_client: OPEXClient = Depends(get_opex_client)
):
    """Admin: Update an order (for adjustments)"""
    try:
        updates = {}
        if request.price is not None:
            updates["price"] = request.price
        if request.quantity is not None:
            updates["quantity"] = request.quantity
        if request.status is not None:
            updates["status"] = request.status
        
        result = await opex_client.admin_update_order(order_id, updates)
        return {"success": True, "order": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order: {str(e)}"
        )


@router.delete("/trading/orders/{order_id}/force")
async def admin_force_cancel_order(
    order_id: str,
    user: User = Depends(require_role(["admin", "owner"])),
    opex_client: OPEXClient = Depends(get_opex_client)
):
    """Admin: Force cancel an order"""
    try:
        result = await opex_client.admin_force_cancel_order(order_id)
        return {"success": True, "order": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to force cancel order: {str(e)}"
        )


@router.put("/trading/positions/{position_id}")
async def admin_update_position(
    position_id: str,
    request: UpdatePositionRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    opex_client: OPEXClient = Depends(get_opex_client)
):
    """Admin: Update a position (for adjustments)"""
    try:
        updates = {}
        if request.quantity is not None:
            updates["quantity"] = request.quantity
        if request.entry_price is not None:
            updates["entryPrice"] = request.entry_price
        if request.leverage is not None:
            updates["leverage"] = request.leverage
        
        result = await opex_client.admin_update_position(position_id, updates)
        return {"success": True, "position": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update position: {str(e)}"
        )


@router.post("/trading/positions/{position_id}/force-close")
async def admin_force_close_position(
    position_id: str,
    user: User = Depends(require_role(["admin", "owner"])),
    opex_client: OPEXClient = Depends(get_opex_client)
):
    """Admin: Force close a position"""
    try:
        result = await opex_client.admin_force_close_position(position_id)
        return {"success": True, "position": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to force close position: {str(e)}"
        )


@router.put("/trading/prices/{symbol}")
async def admin_update_price(
    symbol: str,
    request: UpdatePriceRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    opex_client: OPEXClient = Depends(get_opex_client)
):
    """Admin: Update market price (for testing/adjustments)"""
    try:
        result = await opex_client.admin_update_price(symbol, request.price)
        return {
            "success": True,
            "symbol": symbol,
            "new_price": request.price,
            "reason": request.reason,
            "updated_by": user.id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update price: {str(e)}"
        )


@router.put("/trading/balances/{user_id}")
async def admin_update_balance(
    user_id: int,
    request: UpdateBalanceRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Admin: Update user balance"""
    try:
        from ...models.financial import WalletBalance
        
        # Get or create wallet balance
        balance = db.query(WalletBalance).filter(
            WalletBalance.user_id == user_id,
            WalletBalance.asset == request.asset
        ).first()
        
        if not balance:
            balance = WalletBalance(
                user_id=user_id,
                asset=request.asset,
                available_balance=Decimal("0"),
                locked_balance=Decimal("0")
            )
            db.add(balance)
        
        # Update balance based on operation
        if request.operation == "add":
            balance.available_balance += Decimal(str(request.amount))
        elif request.operation == "subtract":
            balance.available_balance -= Decimal(str(request.amount))
            if balance.available_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient balance"
                )
        elif request.operation == "set":
            balance.available_balance = Decimal(str(request.amount))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid operation. Must be 'add', 'subtract', or 'set'"
            )
        
        db.commit()
        db.refresh(balance)
        
        return {
            "success": True,
            "user_id": user_id,
            "asset": request.asset,
            "new_balance": float(balance.available_balance),
            "operation": request.operation,
            "amount": request.amount,
            "reason": request.reason,
            "updated_by": user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update balance: {str(e)}"
        )


@router.get("/trading/adjustments")
async def get_adjustment_history(
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get trading adjustment history"""
    try:
        from ...models.system import TradingAdjustment
        from sqlalchemy import desc
        
        query = db.query(TradingAdjustment)
        
        if user_id:
            query = query.filter(TradingAdjustment.user_id == user_id)
        
        adjustments = query.order_by(desc(TradingAdjustment.created_at)).limit(limit).all()
        
        return {
            "adjustments": [
                {
                    "id": adj.id,
                    "admin_user_id": adj.admin_user_id,
                    "user_id": adj.user_id,
                    "adjustment_type": adj.adjustment_type,
                    "target_value": adj.target_value,
                    "previous_value": adj.previous_value,
                    "result": adj.result,
                    "created_at": adj.created_at.isoformat()
                }
                for adj in adjustments
            ],
            "total": len(adjustments)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get adjustments: {str(e)}"
        )

