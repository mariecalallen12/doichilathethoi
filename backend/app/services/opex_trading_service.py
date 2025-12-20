"""
OPEX Trading Service
Integration layer for trading operations using OPEX Core
"""
import logging
import time
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException

from .opex_client import get_opex_client, OPEXClient
from ..services.cache_service import CacheService

logger = logging.getLogger(__name__)

# Structured logging helper
def log_trading_operation(operation: str, status: str, details: Dict[str, Any] = None):
    """Log trading operation with structured format"""
    log_data = {
        "operation": operation,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "opex-trading"
    }
    if details:
        log_data.update(details)
    
    if status == "error":
        logger.error(f"Trading {operation}: {log_data}")
    elif status == "warning":
        logger.warning(f"Trading {operation}: {log_data}")
    else:
        logger.info(f"Trading {operation}: {log_data}")


class OPEXTradingService:
    """
    Trading service that uses OPEX Core for order execution
    
    This service acts as a bridge between the FastAPI backend and OPEX trading system.
    It handles order placement, cancellation, position management, etc.
    """
    
    def __init__(self, opex_client: Optional[OPEXClient] = None, cache_service: Optional[CacheService] = None):
        """
        Initialize OPEX trading service
        
        Args:
            opex_client: OPEX client instance (will create if not provided)
            cache_service: Cache service instance
        """
        self.opex = opex_client or get_opex_client()
        self.cache = cache_service or CacheService()
        
        # Cache TTLs (in seconds)
        self.CACHE_TTL_ORDERS = 10  # 10 seconds for orders (user-specific)
        self.CACHE_TTL_POSITIONS = 10  # 10 seconds for positions (user-specific)
        self.CACHE_TTL_STATISTICS = 30  # 30 seconds for statistics
    
    def _invalidate_user_cache(self, user_id: int):
        """Invalidate cache for a user's trading data"""
        patterns = [
            f"opex:trading:orders:{user_id}:*",
            f"opex:trading:positions:{user_id}:*",
            f"opex:trading:statistics:{user_id}:*"
        ]
        for pattern in patterns:
            self.cache.delete_pattern(pattern)
    
    async def place_order(
        self,
        user_id: int,
        symbol: str,
        side: str,  # "buy" or "sell"
        order_type: str,  # "market", "limit", "stop"
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Place a trading order via OPEX
        
        Args:
            user_id: User ID
            symbol: Trading pair symbol (will be converted to OPEX format)
            side: Order side ("buy" or "sell")
            order_type: Order type ("market", "limit", "stop")
            quantity: Order quantity
            price: Price for limit orders
            stop_price: Stop price for stop orders
            
        Returns:
            Order details from OPEX
        """
        # Convert symbol format (e.g., "BTCUSDT" -> "BTC_USDT")
        opex_symbol = self._convert_symbol(symbol)
        
        # Convert side to OPEX format
        opex_side = side.upper()  # "BUY" or "SELL"
        
        # Convert order type to OPEX format
        opex_order_type = order_type.upper()  # "MARKET", "LIMIT", "STOP"
        
        try:
            logger.info(
                f"Placing order via OPEX: user={user_id} | "
                f"symbol={symbol}->{opex_symbol} | "
                f"side={side}->{opex_side} | "
                f"type={order_type}->{opex_order_type} | "
                f"quantity={quantity} | "
                f"price={price} | "
                f"stop_price={stop_price}"
            )
            
            result = await self.opex.place_order(
                user_id=str(user_id),
                symbol=opex_symbol,
                side=opex_side,
                order_type=opex_order_type,
                quantity=float(quantity),
                price=float(price) if price else None,
                stop_price=float(stop_price) if stop_price else None
            )
            
            logger.info(
                f"Order placed successfully via OPEX: "
                f"order_id={result.get('id')} | "
                f"user={user_id} | "
                f"symbol={opex_symbol}"
            )
            return result
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is (they already have proper error messages)
            raise
        except Exception as e:
            logger.error(
                f"Failed to place order via OPEX: "
                f"user={user_id} | "
                f"symbol={symbol}->{opex_symbol} | "
                f"side={side} | "
                f"type={order_type} | "
                f"quantity={quantity} | "
                f"error={str(e)} | "
                f"error_type={type(e).__name__}",
                exc_info=True
            )
            raise
    
    async def cancel_order(
        self,
        order_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Cancel an order via OPEX
        
        Args:
            order_id: Order ID from OPEX
            user_id: User ID (for authorization)
            
        Returns:
            Cancelled order details
        """
        try:
            result = await self.opex.cancel_order(
                order_id=order_id,
                user_id=str(user_id)
            )
            
            logger.info(f"Order cancelled via OPEX: {order_id}")
            
            # Broadcast order update via WebSocket
            try:
                from ...api.websocket import broadcast_order_update
                converted_order = self._convert_order_from_opex(result)
                await broadcast_order_update(user_id, converted_order)
            except Exception as ws_error:
                logger.warning(f"Failed to broadcast order cancellation: {ws_error}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to cancel order via OPEX: {e}")
            raise
    
    async def get_orders(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get user's orders from OPEX
        
        Args:
            user_id: User ID
            symbol: Filter by symbol
            status: Filter by status
            limit: Maximum number of orders
            
        Returns:
            List of orders
        """
        start_time = time.time()
        try:
            opex_symbol = self._convert_symbol(symbol) if symbol else None
            
            orders = await self.opex.get_orders(
                user_id=str(user_id),
                symbol=opex_symbol,
                status=status,
                limit=limit
            )
            
            duration = time.time() - start_time
            
            # Convert OPEX format to our format
            if orders:
                result = [self._convert_order_from_opex(order) for order in orders]
                log_trading_operation(
                    "get_orders",
                    "success",
                    {
                        "user_id": user_id,
                        "symbol": symbol,
                        "count": len(result),
                        "duration_ms": duration * 1000
                    }
                )
                return result
            else:
                log_trading_operation(
                    "get_orders",
                    "success",
                    {
                        "user_id": user_id,
                        "symbol": symbol,
                        "count": 0,
                        "duration_ms": duration * 1000
                    }
                )
                return []
            
        except Exception as e:
            duration = time.time() - start_time
            log_trading_operation(
                "get_orders",
                "error",
                {
                    "user_id": user_id,
                    "symbol": symbol,
                    "error": str(e),
                    "duration_ms": duration * 1000
                }
            )
            # Return empty list instead of raising
            return []
    
    async def get_positions(
        self,
        user_id: int,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's positions from OPEX
        
        Args:
            user_id: User ID
            symbol: Filter by symbol
            
        Returns:
            List of positions
        """
        start_time = time.time()
        try:
            opex_symbol = self._convert_symbol(symbol) if symbol else None
            
            positions = await self.opex.get_positions(
                user_id=str(user_id),
                symbol=opex_symbol
            )
            
            duration = time.time() - start_time
            
            # Convert OPEX format to our format
            if positions:
                result = [self._convert_position_from_opex(pos) for pos in positions]
                log_trading_operation(
                    "get_positions",
                    "success",
                    {
                        "user_id": user_id,
                        "symbol": symbol,
                        "count": len(result),
                        "duration_ms": duration * 1000
                    }
                )
                return result
            else:
                log_trading_operation(
                    "get_positions",
                    "success",
                    {
                        "user_id": user_id,
                        "symbol": symbol,
                        "count": 0,
                        "duration_ms": duration * 1000
                    }
                )
                return []
            
        except Exception as e:
            duration = time.time() - start_time
            log_trading_operation(
                "get_positions",
                "error",
                {
                    "user_id": user_id,
                    "symbol": symbol,
                    "error": str(e),
                    "duration_ms": duration * 1000
                }
            )
            # Return empty list instead of raising
            return []
    
    async def close_position(
        self,
        position_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Close a position via OPEX
        
        Args:
            position_id: Position ID from OPEX
            user_id: User ID
            
        Returns:
            Closed position details
        """
        try:
            result = await self.opex.close_position(
                position_id=position_id,
                user_id=str(user_id)
            )
            
            logger.info(f"Position closed via OPEX: {position_id}")
            
            # Broadcast position update via WebSocket
            try:
                from ...api.websocket import broadcast_position_update
                converted_position = self._convert_position_from_opex(result)
                await broadcast_position_update(user_id, converted_position)
            except Exception as ws_error:
                logger.warning(f"Failed to broadcast position update: {ws_error}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to close position via OPEX: {e}")
            raise
    
    def _convert_symbol(self, symbol: str) -> str:
        """
        Convert symbol format from our format to OPEX format
        
        Args:
            symbol: Symbol in our format (e.g., "BTCUSDT", "BTC/USDT")
            
        Returns:
            Symbol in OPEX format (e.g., "BTC_USDT")
        """
        # Remove slashes and convert to uppercase
        symbol = symbol.replace('/', '').replace('-', '').upper()
        
        # Common base currencies
        base_currencies = ['BTC', 'ETH', 'BNB', 'SOL', 'DOGE', 'TON']
        quote_currencies = ['USDT', 'USD', 'IRT', 'BUSD', 'EUR', 'GBP']
        
        # Try to detect base and quote
        for base in base_currencies:
            if symbol.startswith(base):
                remaining = symbol[len(base):]
                if remaining in quote_currencies:
                    return f"{base}_{remaining}"
        
        # If no match, try to split at common lengths
        if len(symbol) >= 6:
            # Assume first 3 chars are base, rest is quote
            base = symbol[:3]
            quote = symbol[3:]
            return f"{base}_{quote}"
        
        # Fallback: return as-is (OPEX might accept it)
        return symbol
    
    def _convert_order_from_opex(self, opex_order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert OPEX order format to our format
        
        Args:
            opex_order: Order from OPEX API
            
        Returns:
            Order in our format
        """
        return {
            "id": str(opex_order.get("id", "")),
            "user_id": int(opex_order.get("userId", 0)),
            "symbol": self._convert_symbol_from_opex(opex_order.get("symbol", "")),
            "side": opex_order.get("side", "").lower(),
            "type": opex_order.get("type", "").lower(),
            "quantity": float(opex_order.get("quantity", 0)),
            "price": float(opex_order.get("price", 0)) if opex_order.get("price") else None,
            "stop_price": float(opex_order.get("stopPrice", 0)) if opex_order.get("stopPrice") else None,
            "status": opex_order.get("status", "").lower(),
            "filled_quantity": float(opex_order.get("filledQuantity", 0)),
            "filled_price": float(opex_order.get("filledPrice", 0)) if opex_order.get("filledPrice") else None,
            "created_at": opex_order.get("createdAt", datetime.utcnow().isoformat()),
            "updated_at": opex_order.get("updatedAt", datetime.utcnow().isoformat())
        }
    
    def _convert_position_from_opex(self, opex_position: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert OPEX position format to our format
        
        Args:
            opex_position: Position from OPEX API
            
        Returns:
            Position in our format
        """
        return {
            "id": str(opex_position.get("id", "")),
            "user_id": int(opex_position.get("userId", 0)),
            "symbol": self._convert_symbol_from_opex(opex_position.get("symbol", "")),
            "side": opex_position.get("side", "").lower(),
            "quantity": float(opex_position.get("quantity", 0)),
            "entry_price": float(opex_position.get("entryPrice", 0)),
            "current_price": float(opex_position.get("currentPrice", 0)) if opex_position.get("currentPrice") else None,
            "unrealized_pnl": float(opex_position.get("unrealizedPnl", 0)),
            "realized_pnl": float(opex_position.get("realizedPnl", 0)),
            "leverage": float(opex_position.get("leverage", 1)),
            "margin": float(opex_position.get("margin", 0)),
            "status": "open" if not opex_position.get("closed") else "closed",
            "created_at": opex_position.get("createdAt", datetime.utcnow().isoformat()),
            "closed_at": opex_position.get("closedAt") if opex_position.get("closed") else None
        }
    
    def _convert_symbol_from_opex(self, symbol: str) -> str:
        """
        Convert symbol from OPEX format to our format
        
        Args:
            symbol: Symbol in OPEX format (e.g., "BTC_USDT")
            
        Returns:
            Symbol in our format (e.g., "BTCUSDT")
        """
        return symbol.replace('_', '').replace('-', '')


# Singleton instance
_opex_trading_service: Optional[OPEXTradingService] = None


def get_opex_trading_service() -> OPEXTradingService:
    """
    Get OPEX trading service instance (singleton)
    
    Returns:
        OPEXTradingService instance
    """
    global _opex_trading_service
    
    if _opex_trading_service is None:
        _opex_trading_service = OPEXTradingService()
    
    return _opex_trading_service

