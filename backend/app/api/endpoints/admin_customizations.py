"""
Admin Customization API
=======================

Endpoints for managing data customization rules and sessions
Allows admins to modify market data, signals, and trading information
"""

from fastapi import APIRouter, Depends, HTTPException, Body, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from app.services.customization_engine import (
    customization_engine,
    CustomizationRule,
    SessionConfig
)
from app.dependencies import require_role
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin-customizations"])


# ============================================================================
# Request/Response Models
# ============================================================================

class RuleCreateRequest(BaseModel):
    """Request model for creating a rule"""
    name: str
    symbol: str = "*"
    price_adjustment: Optional[float] = None
    change_adjustment: Optional[float] = None
    force_signal: Optional[str] = None
    confidence_boost: Optional[float] = None
    custom_volume: Optional[float] = None
    custom_market_cap: Optional[float] = None
    enabled: bool = True


class SessionCreateRequest(BaseModel):
    """Request model for creating a session"""
    name: str
    session_id: Optional[str] = None


class BindRuleRequest(BaseModel):
    """Request model for binding a rule to a session"""
    rule_name: str


class ManualOverrideRequest(BaseModel):
    """Request model for manual data override"""
    symbol: str
    price: Optional[float] = None
    signal: Optional[str] = None
    confidence: Optional[float] = None


# ============================================================================
# Rules Management Endpoints
# ============================================================================

@router.get("/customizations/rules", response_model=List[CustomizationRule])
async def list_rules(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    List all customization rules
    
    Returns:
        List of all rules in the system
    """
    try:
        rules = customization_engine.list_all_rules()
        logger.info(f"Admin {user.email} listed {len(rules)} customization rules")
        return rules
    except Exception as e:
        logger.error(f"Error listing rules: {e}")
        raise HTTPException(500, "Failed to list rules")


@router.get("/customizations/rules/{name}", response_model=CustomizationRule)
async def get_rule(
    name: str,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Get a specific customization rule
    
    Args:
        name: Rule name
        
    Returns:
        The customization rule
    """
    rule = customization_engine.get_rule(name)
    if not rule:
        raise HTTPException(404, f"Rule '{name}' not found")
    
    return rule


@router.post("/customizations/rules", status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreateRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Create a new customization rule
    
    Args:
        rule_data: Rule configuration
        
    Returns:
        Created rule information
    """
    try:
        # Convert request to CustomizationRule
        rule = CustomizationRule(**rule_data.dict())
        
        # Add to engine
        customization_engine.add_rule(rule)
        
        logger.info(f"Admin {user.email} created rule: {rule.name}")
        
        return {
            "message": "Rule created successfully",
            "rule": rule
        }
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise HTTPException(400, f"Failed to create rule: {str(e)}")


@router.put("/customizations/rules/{name}")
async def update_rule(
    name: str,
    rule_data: RuleCreateRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Update an existing customization rule
    
    Args:
        name: Rule name to update
        rule_data: New rule configuration
        
    Returns:
        Success message
    """
    try:
        # Check if rule exists
        if not customization_engine.get_rule(name):
            raise HTTPException(404, f"Rule '{name}' not found")
        
        # Convert and update
        rule = CustomizationRule(name=name, **rule_data.dict(exclude={"name"}))
        customization_engine.update_rule(name, rule)
        
        logger.info(f"Admin {user.email} updated rule: {name}")
        
        return {
            "message": "Rule updated successfully",
            "rule": rule
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule: {e}")
        raise HTTPException(400, f"Failed to update rule: {str(e)}")


@router.delete("/customizations/rules/{name}")
async def delete_rule(
    name: str,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Delete a customization rule
    
    Args:
        name: Rule name to delete
        
    Returns:
        Success message
    """
    if customization_engine.remove_rule(name):
        logger.info(f"Admin {user.email} deleted rule: {name}")
        return {"message": f"Rule '{name}' deleted successfully"}
    else:
        raise HTTPException(404, f"Rule '{name}' not found")


# ============================================================================
# Session Management Endpoints
# ============================================================================

@router.get("/customizations/sessions", response_model=List[SessionConfig])
async def list_sessions(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    List all customization sessions
    
    Returns:
        List of all sessions
    """
    sessions = list(customization_engine.sessions.values())
    logger.info(f"Admin {user.email} listed {len(sessions)} sessions")
    return sessions


@router.post("/customizations/sessions", response_model=SessionConfig, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreateRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Create a new customization session
    
    Args:
        session_data: Session name and optional ID
        
    Returns:
        Created session configuration
    """
    try:
        session = customization_engine.create_session(
            name=session_data.name,
            session_id=session_data.session_id
        )
        
        logger.info(f"Admin {user.email} created session: {session.session_id}")
        
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(400, f"Failed to create session: {str(e)}")


@router.delete("/customizations/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Delete a customization session
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        Success message
    """
    if customization_engine.delete_session(session_id):
        logger.info(f"Admin {user.email} deleted session: {session_id}")
        return {"message": f"Session '{session_id}' deleted successfully"}
    else:
        raise HTTPException(404, f"Session '{session_id}' not found")


# ============================================================================
# Session-Rule Binding Endpoints
# ============================================================================

@router.post("/customizations/sessions/{session_id}/bind")
async def bind_rule_to_session(
    session_id: str,
    bind_data: BindRuleRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Bind a rule to a session
    
    Args:
        session_id: Session ID
        bind_data: Rule name to bind
        
    Returns:
        Success message
    """
    if customization_engine.bind_rule_to_session(session_id, bind_data.rule_name):
        logger.info(f"Admin {user.email} bound rule '{bind_data.rule_name}' to session '{session_id}'")
        return {
            "message": f"Rule '{bind_data.rule_name}' bound to session '{session_id}'",
            "session_id": session_id,
            "rule_name": bind_data.rule_name
        }
    else:
        raise HTTPException(400, "Failed to bind rule to session")


@router.post("/customizations/sessions/{session_id}/unbind")
async def unbind_rule_from_session(
    session_id: str,
    bind_data: BindRuleRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Unbind a rule from a session
    
    Args:
        session_id: Session ID
        bind_data: Rule name to unbind
        
    Returns:
        Success message
    """
    if customization_engine.unbind_rule_from_session(session_id, bind_data.rule_name):
        logger.info(f"Admin {user.email} unbound rule '{bind_data.rule_name}' from session '{session_id}'")
        return {"message": f"Rule '{bind_data.rule_name}' unbound from session '{session_id}'"}
    else:
        raise HTTPException(400, "Failed to unbind rule from session")


# ============================================================================
# Session Activation Endpoints
# ============================================================================

@router.post("/customizations/sessions/{session_id}/activate")
async def activate_session(
    session_id: str,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Activate a customization session
    
    Args:
        session_id: Session ID to activate
        
    Returns:
        Success message
    """
    try:
        customization_engine.enable_customizations(session_id)
        logger.info(f"Admin {user.email} activated session: {session_id}")
        return {
            "message": f"Session '{session_id}' activated",
            "session_id": session_id,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error activating session: {e}")
        raise HTTPException(400, f"Failed to activate session: {str(e)}")


@router.post("/customizations/sessions/{session_id}/deactivate")
async def deactivate_session(
    session_id: str,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Deactivate a customization session
    
    Args:
        session_id: Session ID to deactivate
        
    Returns:
        Success message
    """
    try:
        customization_engine.disable_customizations(session_id)
        logger.info(f"Admin {user.email} deactivated session: {session_id}")
        return {
            "message": f"Session '{session_id}' deactivated",
            "session_id": session_id,
            "status": "inactive"
        }
    except Exception as e:
        logger.error(f"Error deactivating session: {e}")
        raise HTTPException(400, f"Failed to deactivate session: {str(e)}")


# ============================================================================
# Manual Override Endpoints
# ============================================================================

@router.post("/customizations/manual-override")
async def set_manual_override(
    override_data: ManualOverrideRequest,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Set manual data override for a symbol
    
    Args:
        override_data: Symbol and values to override
        
    Returns:
        Success message
    """
    try:
        if override_data.price is not None:
            customization_engine.set_manual_price(override_data.symbol, override_data.price)
        
        if override_data.signal is not None:
            customization_engine.set_manual_signal(override_data.symbol, override_data.signal)
        
        if override_data.confidence is not None:
            customization_engine.set_manual_confidence(override_data.symbol, override_data.confidence)
        
        logger.info(f"Admin {user.email} set manual override for {override_data.symbol}")
        
        return {
            "message": f"Manual override set for {override_data.symbol}",
            "symbol": override_data.symbol,
            "overrides": override_data.dict(exclude_none=True)
        }
    except Exception as e:
        logger.error(f"Error setting manual override: {e}")
        raise HTTPException(400, f"Failed to set manual override: {str(e)}")


@router.delete("/customizations/manual-override/{symbol}")
async def clear_manual_override(
    symbol: str,
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Clear manual override for a symbol
    
    Args:
        symbol: Symbol to clear overrides for
        
    Returns:
        Success message
    """
    customization_engine.clear_manual_overrides(symbol)
    logger.info(f"Admin {user.email} cleared manual override for {symbol}")
    return {"message": f"Manual override cleared for {symbol}"}


@router.delete("/customizations/manual-override")
async def clear_all_manual_overrides(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Clear all manual overrides
    
    Returns:
        Success message
    """
    customization_engine.clear_manual_overrides()
    logger.info(f"Admin {user.email} cleared all manual overrides")
    return {"message": "All manual overrides cleared"}


# ============================================================================
# Status & Info Endpoints
# ============================================================================

@router.get("/customizations/status")
async def get_customization_status(
    user: User = Depends(require_role(["admin", "owner"]))
):
    """
    Get overall customization system status
    
    Returns:
        System status information
    """
    return {
        "total_rules": len(customization_engine.global_rules),
        "total_sessions": len(customization_engine.sessions),
        "active_session": customization_engine._current_session,
        "global_enabled": customization_engine.enabled_globally,
        "manual_overrides": {
            "prices": len(customization_engine.manual_prices),
            "signals": len(customization_engine.manual_signals),
            "confidence": len(customization_engine.manual_confidence)
        }
    }
