"""
OPEX User Service
Service for managing user accounts in OPEX system
"""
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from .opex_client import get_opex_client, OPEXClient

logger = logging.getLogger(__name__)


class OPEXUserService:
    """
    Service for managing users in OPEX system
    
    This service handles:
    - Creating user accounts in OPEX when users register
    - Initializing wallets for new users
    - Syncing user data between FastAPI backend and OPEX
    """
    
    def __init__(self, opex_client: Optional[OPEXClient] = None):
        """
        Initialize OPEX user service
        
        Args:
            opex_client: OPEX client instance (will create if not provided)
        """
        self.opex = opex_client or get_opex_client()
    
    async def create_user_account(
        self,
        user_id: int,
        email: str,
        phone: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a user account in OPEX system
        
        Args:
            user_id: User ID from FastAPI backend
            email: User email
            phone: User phone number (optional)
            full_name: User full name (optional)
            
        Returns:
            Created user account details from OPEX
            
        Note:
            OPEX may require user creation through its own API.
            This method attempts to create the user via OPEX API.
            If OPEX doesn't have a direct user creation endpoint,
            users may need to be created manually or through OPEX admin panel.
        """
        try:
            # Convert user_id to string for OPEX
            opex_user_id = str(user_id)
            
            # Prepare user data
            user_data = {
                "userId": opex_user_id,
                "email": email,
            }
            
            if phone:
                user_data["phone"] = phone
            if full_name:
                user_data["fullName"] = full_name
            
            logger.info(
                f"Creating OPEX user account: user_id={user_id} | "
                f"email={email} | "
                f"opex_user_id={opex_user_id}"
            )
            
            # Try to create user via OPEX API
            # Note: OPEX may not have a public user creation endpoint
            # In that case, this will fail gracefully and user creation
            # should be handled through OPEX admin panel or automated scripts
            try:
                result = await self.opex._request(
                    "POST",
                    "/api/users",
                    data=user_data
                )
                
                logger.info(
                    f"OPEX user account created successfully: "
                    f"user_id={user_id} | "
                    f"opex_user_id={opex_user_id}"
                )
                return result
                
            except HTTPException as e:
                # If user creation endpoint doesn't exist or user already exists
                if e.status_code == 404:
                    logger.warning(
                        f"OPEX user creation endpoint not available. "
                        f"User {user_id} may need to be created manually in OPEX."
                    )
                    # Return a placeholder response
                    return {
                        "userId": opex_user_id,
                        "email": email,
                        "status": "pending_manual_creation",
                        "message": "User account needs to be created in OPEX admin panel"
                    }
                elif e.status_code == 409:
                    logger.info(f"OPEX user {user_id} already exists")
                    return {
                        "userId": opex_user_id,
                        "email": email,
                        "status": "exists"
                    }
                else:
                    raise
            
        except Exception as e:
            logger.error(
                f"Failed to create OPEX user account: "
                f"user_id={user_id} | "
                f"email={email} | "
                f"error={str(e)} | "
                f"error_type={type(e).__name__}",
                exc_info=True
            )
            # Don't raise exception - user creation in OPEX is not critical
            # for backend registration. User can be created manually later.
            return {
                "userId": str(user_id),
                "email": email,
                "status": "error",
                "error": str(e)
            }
    
    async def initialize_wallet(
        self,
        user_id: int,
        currency: str = "USDT",
        initial_balance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Initialize wallet for a user in OPEX
        
        Args:
            user_id: User ID
            currency: Currency symbol (default: USDT)
            initial_balance: Initial balance (default: 0.0)
            
        Returns:
            Wallet initialization result
        """
        try:
            opex_user_id = str(user_id)
            
            logger.info(
                f"Initializing OPEX wallet: user_id={user_id} | "
                f"currency={currency} | "
                f"initial_balance={initial_balance}"
            )
            
            # Try to initialize wallet via OPEX API
            try:
                result = await self.opex._request(
                    "POST",
                    f"/api/users/{opex_user_id}/wallets",
                    data={
                        "currency": currency,
                        "initialBalance": initial_balance
                    }
                )
                
                logger.info(
                    f"OPEX wallet initialized: user_id={user_id} | "
                    f"currency={currency}"
                )
                return result
                
            except HTTPException as e:
                if e.status_code == 404:
                    logger.warning(
                        f"OPEX wallet initialization endpoint not available. "
                        f"Wallet for user {user_id} may need to be initialized manually."
                    )
                    return {
                        "userId": opex_user_id,
                        "currency": currency,
                        "status": "pending_manual_initialization"
                    }
                else:
                    raise
            
        except Exception as e:
            logger.error(
                f"Failed to initialize OPEX wallet: "
                f"user_id={user_id} | "
                f"currency={currency} | "
                f"error={str(e)}",
                exc_info=True
            )
            return {
                "userId": str(user_id),
                "currency": currency,
                "status": "error",
                "error": str(e)
            }
    
    async def get_user_account(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user account from OPEX
        
        Args:
            user_id: User ID
            
        Returns:
            User account details or None
        """
        try:
            opex_user_id = str(user_id)
            
            result = await self.opex._request(
                "GET",
                f"/api/users/{opex_user_id}"
            )
            
            return result
            
        except HTTPException as e:
            if e.status_code == 404:
                logger.info(f"OPEX user {user_id} not found")
                return None
            raise
        except Exception as e:
            logger.error(
                f"Failed to get OPEX user account: user_id={user_id} | error={str(e)}",
                exc_info=True
            )
            return None
    
    async def sync_user_to_opex(
        self,
        user_id: int,
        email: str,
        phone: Optional[str] = None,
        full_name: Optional[str] = None,
        initialize_wallet: bool = True
    ) -> Dict[str, Any]:
        """
        Sync user to OPEX system (create account + initialize wallet)
        
        Args:
            user_id: User ID from FastAPI backend
            email: User email
            phone: User phone number
            full_name: User full name
            initialize_wallet: Whether to initialize wallet (default: True)
            
        Returns:
            Sync result with account and wallet status
        """
        result = {
            "user_id": user_id,
            "account": None,
            "wallet": None,
            "success": False
        }
        
        # Create user account
        account_result = await self.create_user_account(
            user_id=user_id,
            email=email,
            phone=phone,
            full_name=full_name
        )
        result["account"] = account_result
        
        # Initialize wallet if requested
        if initialize_wallet:
            wallet_result = await self.initialize_wallet(
                user_id=user_id,
                currency="USDT",
                initial_balance=0.0
            )
            result["wallet"] = wallet_result
        
        # Determine success
        result["success"] = (
            account_result.get("status") in ["exists", "created"] or
            account_result.get("status") == "pending_manual_creation"
        )
        
        return result


# Singleton instance
_opex_user_service: Optional[OPEXUserService] = None


def get_opex_user_service() -> OPEXUserService:
    """
    Get OPEX user service instance (singleton)
    
    Returns:
        OPEXUserService instance
    """
    global _opex_user_service
    
    if _opex_user_service is None:
        _opex_user_service = OPEXUserService()
    
    return _opex_user_service

