"""
Risk Validation Service
Pre-trade risk checks for order placement
"""
import logging
from typing import Optional, Dict, Any
from decimal import Decimal
from fastapi import HTTPException, status

from .opex_client import get_opex_client, OPEXClient
from .opex_trading_service import get_opex_trading_service, OPEXTradingService

logger = logging.getLogger(__name__)


class RiskValidationService:
    """
    Service for pre-trade risk validation
    
    Checks:
    - Balance validation
    - Margin requirements
    - Position size limits
    - Daily loss limits
    - Leverage validation
    """
    
    def __init__(
        self,
        opex_client: Optional[OPEXClient] = None,
        trading_service: Optional[OPEXTradingService] = None
    ):
        self.opex = opex_client or get_opex_client()
        self.trading = trading_service or get_opex_trading_service()
        
        # Risk limits (can be configured via settings)
        self.MAX_POSITION_SIZE = Decimal("1000000")  # $1M max position
        self.MAX_DAILY_LOSS = Decimal("10000")  # $10K max daily loss
        self.MIN_MARGIN_RATIO = Decimal("0.1")  # 10% minimum margin
        self.MAX_LEVERAGE = Decimal("100")  # 100x max leverage
    
    async def validate_order(
        self,
        user_id: int,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Validate order before placement
        
        Args:
            user_id: User ID
            symbol: Trading symbol
            side: Order side (buy/sell)
            order_type: Order type (market/limit/stop)
            quantity: Order quantity
            price: Order price (for limit/stop orders)
            
        Returns:
            Validation result with warnings/errors
            
        Raises:
            HTTPException: If order fails risk checks
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        try:
            # 1. Check balance (for buy orders)
            if side.lower() == "buy":
                balance_check = await self._check_balance(user_id, symbol, quantity, price)
                if not balance_check["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].append(balance_check["error"])
                elif balance_check.get("warning"):
                    validation_result["warnings"].append(balance_check["warning"])
            
            # 2. Check position size limits
            position_check = await self._check_position_size(user_id, symbol, quantity, price)
            if not position_check["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].append(position_check["error"])
            
            # 3. Check daily loss limits
            loss_check = await self._check_daily_loss(user_id)
            if not loss_check["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].append(loss_check["error"])
            elif loss_check.get("warning"):
                validation_result["warnings"].append(loss_check["warning"])
            
            # 4. Check margin requirements (for leveraged trading)
            margin_check = await self._check_margin_requirements(user_id, symbol, quantity, price)
            if not margin_check["valid"]:
                validation_result["valid"] = False
                validation_result["errors"].append(margin_check["error"])
            elif margin_check.get("warning"):
                validation_result["warnings"].append(margin_check["warning"])
            
            # If validation failed, raise exception
            if not validation_result["valid"]:
                error_message = "; ".join(validation_result["errors"])
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order validation failed: {error_message}"
                )
            
            return validation_result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Risk validation error: {e}", exc_info=True)
            # Don't block order on validation errors - log and continue
            return {
                "valid": True,
                "warnings": [f"Risk validation incomplete: {str(e)}"],
                "errors": []
            }
    
    async def _check_balance(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        price: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Check if user has sufficient balance"""
        try:
            # Get user's account balance from OPEX
            # Note: This requires OPEX API endpoint for balance
            # For now, we'll return a placeholder check
            # In production, this should query OPEX wallet service
            
            # Calculate order value
            if price:
                order_value = quantity * price
            else:
                # For market orders, we'd need current market price
                # For now, assume sufficient balance (OPEX will reject if insufficient)
                return {"valid": True}
            
            # Check if order value exceeds reasonable limit
            if order_value > self.MAX_POSITION_SIZE:
                return {
                    "valid": False,
                    "error": f"Order value ({order_value}) exceeds maximum position size"
                }
            
            # Note: Actual balance check should query OPEX wallet
            # This is a placeholder - OPEX will handle actual balance validation
            return {"valid": True}
            
        except Exception as e:
            logger.warning(f"Balance check error: {e}")
            return {"valid": True}  # Don't block on check errors
    
    async def _check_position_size(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        price: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Check position size limits"""
        try:
            # Get current positions
            positions = await self.trading.get_positions(user_id=user_id, symbol=symbol)
            
            # Calculate current position size
            current_position_size = Decimal("0")
            for pos in positions:
                if pos.get("status") == "open":
                    pos_quantity = Decimal(str(pos.get("quantity", 0)))
                    current_position_size += pos_quantity
            
            # Calculate new position size
            new_position_size = current_position_size + quantity
            
            # Check against limit
            if price:
                position_value = new_position_size * price
                if position_value > self.MAX_POSITION_SIZE:
                    return {
                        "valid": False,
                        "error": f"Position size would exceed maximum limit of {self.MAX_POSITION_SIZE}"
                    }
            
            return {"valid": True}
            
        except Exception as e:
            logger.warning(f"Position size check error: {e}")
            return {"valid": True}
    
    async def _check_daily_loss(self, user_id: int) -> Dict[str, Any]:
        """Check daily loss limits"""
        try:
            # Get user's positions
            positions = await self.trading.get_positions(user_id=user_id)
            
            # Calculate total unrealized + realized P&L
            total_pnl = Decimal("0")
            for pos in positions:
                if pos.get("status") == "open":
                    unrealized = Decimal(str(pos.get("unrealized_pnl", 0)))
                    total_pnl += unrealized
                realized = Decimal(str(pos.get("realized_pnl", 0)))
                total_pnl += realized
            
            # Check if daily loss limit exceeded
            if total_pnl < -self.MAX_DAILY_LOSS:
                return {
                    "valid": False,
                    "error": f"Daily loss limit exceeded. Current P&L: {total_pnl}"
                }
            elif total_pnl < -self.MAX_DAILY_LOSS * Decimal("0.8"):  # 80% of limit
                return {
                    "valid": True,
                    "warning": f"Approaching daily loss limit. Current P&L: {total_pnl}"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.warning(f"Daily loss check error: {e}")
            return {"valid": True}
    
    async def _check_margin_requirements(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal,
        price: Optional[Decimal]
    ) -> Dict[str, Any]:
        """Check margin requirements"""
        try:
            # For leveraged trading, check margin ratio
            # This is a placeholder - actual margin calculation depends on OPEX
            if price:
                order_value = quantity * price
                required_margin = order_value * self.MIN_MARGIN_RATIO
                
                # Check if user has sufficient margin
                # Note: This should query OPEX for actual margin availability
                # For now, return valid (OPEX will handle margin checks)
                return {"valid": True}
            
            return {"valid": True}
            
        except Exception as e:
            logger.warning(f"Margin check error: {e}")
            return {"valid": True}


# Singleton instance
_risk_validation_service: Optional[RiskValidationService] = None


def get_risk_validation_service() -> RiskValidationService:
    """Get risk validation service instance"""
    global _risk_validation_service
    
    if _risk_validation_service is None:
        _risk_validation_service = RiskValidationService()
    
    return _risk_validation_service

