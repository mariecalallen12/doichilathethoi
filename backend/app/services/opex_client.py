"""
OPEX API Client
Integration layer for communicating with OPEX Core trading system
"""
import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class OPEXClient:
    """
    Client for interacting with OPEX Core API
    
    OPEX Core is a Kotlin-based cryptocurrency exchange system with microservices architecture.
    This client provides a Python interface to interact with OPEX services.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize OPEX client
        
        Args:
            base_url: Base URL of OPEX API service (defaults to config)
            api_key: API key for authentication (if required)
            timeout: Request timeout in seconds (defaults to config)
        """
        from app.core.config import settings
        
        self.base_url = (base_url or settings.OPEX_API_URL).rstrip('/')
        self.api_key = api_key or settings.OPEX_API_KEY
        self.timeout = timeout or settings.OPEX_TIMEOUT
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to OPEX API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            HTTPException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = {}
        
        if self.api_key:
            request_headers["Authorization"] = f"Bearer {self.api_key}"
        
        if headers:
            request_headers.update(headers)
        
        try:
            logger.debug(f"OPEX API request: {method} {endpoint} | params={params} | data={data}")
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"OPEX API response: {method} {endpoint} | status={response.status_code}")
            return result
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_response = e.response.json()
                error_detail = error_response.get("message", error_response.get("detail", str(error_response)))
            except:
                error_detail = e.response.text[:500] if e.response.text else "No error details"
            
            logger.error(
                f"OPEX API HTTP error: {method} {endpoint} | "
                f"status={e.response.status_code} | "
                f"error={error_detail} | "
                f"request_data={data} | "
                f"request_params={params}"
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"OPEX API error: {error_detail}"
            )
        except httpx.RequestError as e:
            logger.error(
                f"OPEX API connection error: {method} {endpoint} | "
                f"error={str(e)} | "
                f"error_type={type(e).__name__} | "
                f"url={url}"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"OPEX service unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(
                f"OPEX API unexpected error: {method} {endpoint} | "
                f"error={str(e)} | "
                f"error_type={type(e).__name__}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OPEX API error: {str(e)}"
            )
    
    # ========== Trading Operations ==========
    
    async def place_order(
        self,
        user_id: str,
        symbol: str,
        side: str,  # "BUY" or "SELL"
        order_type: str,  # "MARKET", "LIMIT", "STOP"
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a trading order
        
        Args:
            user_id: User ID
            symbol: Trading pair symbol (e.g., "BTC_USDT")
            side: Order side ("BUY" or "SELL")
            order_type: Order type ("MARKET", "LIMIT", "STOP")
            quantity: Order quantity
            price: Price for limit orders
            stop_price: Stop price for stop orders
            
        Returns:
            Order details
        """
        data = {
            "userId": user_id,
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity
        }
        
        if price:
            data["price"] = price
        if stop_price:
            data["stopPrice"] = stop_price
        
        return await self._request("POST", "/api/orders", data=data)
    
    async def cancel_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            user_id: User ID (for authorization)
            
        Returns:
            Cancelled order details
        """
        return await self._request(
            "DELETE",
            f"/api/orders/{order_id}",
            params={"userId": user_id}
        )
    
    async def get_orders(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get user's orders
        
        Args:
            user_id: User ID
            symbol: Filter by symbol
            status: Filter by status
            limit: Maximum number of orders to return
            
        Returns:
            List of orders
        """
        params = {"userId": user_id, "limit": limit}
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        
        response = await self._request("GET", "/api/orders", params=params)
        return response.get("orders", [])
    
    async def get_positions(
        self,
        user_id: str,
        symbol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's positions
        
        Args:
            user_id: User ID
            symbol: Filter by symbol
            
        Returns:
            List of positions
        """
        params = {"userId": user_id}
        if symbol:
            params["symbol"] = symbol
        
        response = await self._request("GET", "/api/positions", params=params)
        return response.get("positions", [])
    
    async def close_position(
        self,
        position_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Close a position
        
        Args:
            position_id: Position ID
            user_id: User ID
            
        Returns:
            Closed position details
        """
        return await self._request(
            "POST",
            f"/api/positions/{position_id}/close",
            data={"userId": user_id}
        )
    
    # ========== Market Data ==========
    
    async def get_orderbook(
        self,
        symbol: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get orderbook for a symbol
        
        Args:
            symbol: Trading pair symbol
            limit: Number of levels to return
            
        Returns:
            Orderbook data with bids and asks
        """
        return await self._request(
            "GET",
            f"/api/market/orderbook/{symbol}",
            params={"limit": limit}
        )
    
    async def get_trades(
        self,
        symbol: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent trades for a symbol
        
        Args:
            symbol: Trading pair symbol
            limit: Maximum number of trades
            
        Returns:
            List of recent trades
        """
        response = await self._request(
            "GET",
            f"/api/market/trades/{symbol}",
            params={"limit": limit}
        )
        return response.get("trades", [])
    
    async def get_candles(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV candles
        
        Args:
            symbol: Trading pair symbol
            interval: Time interval (1m, 5m, 1h, 1d, etc.)
            limit: Number of candles
            
        Returns:
            List of candle data
        """
        response = await self._request(
            "GET",
            f"/api/market/candles/{symbol}",
            params={"interval": interval, "limit": limit}
        )
        return response.get("candles", [])
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get ticker data for a symbol
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Ticker data
        """
        return await self._request("GET", f"/api/market/ticker/{symbol}")
    
    async def get_symbols(self) -> List[Dict[str, Any]]:
        """
        Get available trading symbols
        
        Returns:
            List of available symbols
        """
        response = await self._request("GET", "/api/market/symbols")
        return response.get("symbols", [])
    
    # ========== Admin Operations ==========
    
    async def admin_update_order(
        self,
        order_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Admin: Update an order (for adjustments)
        
        Args:
            order_id: Order ID
            updates: Fields to update
            
        Returns:
            Updated order details
        """
        return await self._request(
            "PUT",
            f"/api/admin/orders/{order_id}",
            data=updates
        )
    
    async def admin_force_cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Admin: Force cancel an order
        
        Args:
            order_id: Order ID
            
        Returns:
            Cancelled order details
        """
        return await self._request(
            "DELETE",
            f"/api/admin/orders/{order_id}/force"
        )
    
    async def admin_update_position(
        self,
        position_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Admin: Update a position
        
        Args:
            position_id: Position ID
            updates: Fields to update
            
        Returns:
            Updated position details
        """
        return await self._request(
            "PUT",
            f"/api/admin/positions/{position_id}",
            data=updates
        )
    
    async def admin_force_close_position(
        self,
        position_id: str
    ) -> Dict[str, Any]:
        """
        Admin: Force close a position
        
        Args:
            position_id: Position ID
            
        Returns:
            Closed position details
        """
        return await self._request(
            "POST",
            f"/api/admin/positions/{position_id}/force-close"
        )
    
    async def admin_update_price(
        self,
        symbol: str,
        price: float
    ) -> Dict[str, Any]:
        """
        Admin: Update market price (for testing/adjustments)
        
        Args:
            symbol: Trading pair symbol
            price: New price
            
        Returns:
            Updated price data
        """
        return await self._request(
            "PUT",
            f"/api/admin/prices/{symbol}",
            data={"price": price}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check OPEX API health
        
        Returns:
            Health status dictionary
        """
        try:
            # Try to access a simple endpoint
            response = await self.client.get("/actuator/health", timeout=5.0)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "opex_api": "available",
                    "response": response.json() if response.text else {}
                }
            else:
                return {
                    "status": "degraded",
                    "opex_api": "unavailable",
                    "status_code": response.status_code
                }
        except httpx.ConnectError:
            return {
                "status": "unavailable",
                "opex_api": "connection_failed",
                "message": "Cannot connect to OPEX API"
            }
        except httpx.TimeoutException:
            return {
                "status": "timeout",
                "opex_api": "timeout",
                "message": "OPEX API health check timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "opex_api": "error",
                "message": str(e)
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_opex_client: Optional[OPEXClient] = None


def get_opex_client() -> OPEXClient:
    """
    Get OPEX client instance (singleton)
    
    Returns:
        OPEXClient instance
    """
    global _opex_client
    
    if _opex_client is None:
        from app.core.config import settings
        
        _opex_client = OPEXClient(
            base_url=settings.OPEX_API_URL,
            api_key=settings.OPEX_API_KEY,
            timeout=settings.OPEX_TIMEOUT
        )
    
    return _opex_client

