#!/usr/bin/env python3
"""
Market Reality Control API
=========================

Admin API endpoints for controlling market data customizations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import logging

# Import custom data manager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Documentation.Customization.custom_data_manager import custom_manager, CustomizationRule

logger = logging.getLogger(__name__)

# Create router
control_router = APIRouter()

# ============================================================================
# REQUEST MODELS
# ============================================================================

class GlobalCustomizationRequest(BaseModel):
    """Request model for global customization"""
    price_adjustment: Optional[float] = None
    change_adjustment: Optional[float] = None
    force_signal: Optional[str] = None
    confidence_boost: Optional[float] = None

class SymbolCustomizationRequest(BaseModel):
    """Request model for symbol-specific customization"""
    manual_price: Optional[float] = None
    force_signal: Optional[str] = None
    confidence_boost: Optional[float] = None
    price_adjustment: Optional[float] = None
    change_adjustment: Optional[float] = None

class CustomizationRuleRequest(BaseModel):
    """Request model for creating custom rule"""
    name: str
    symbol: str
    price_adjustment: Optional[float] = None
    change_adjustment: Optional[float] = None
    force_signal: Optional[str] = None
    confidence_boost: Optional[float] = None
    custom_volume: Optional[float] = None
    custom_market_cap: Optional[float] = None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@control_router.get("/info")
async def get_api_info():
    """Get Market Reality Control API information"""
    return {
        "name": "Market Reality Control API",
        "version": "1.0.0",
        "description": "Admin API for controlling market data customizations",
        "endpoints": {
            "global": "/global - Set global market customizations",
            "symbol": "/symbol/{symbol} - Set symbol-specific customizations",
            "preset": "/preset/{name} - Apply scenario preset",
            "active": "/active - Get active customizations",
            "toggle": "/toggle - Enable/disable customizations",
            "clear": "/clear - Clear all customizations"
        }
    }

@control_router.post("/global")
async def set_global_customization(data: GlobalCustomizationRequest):
    """
    Apply global market customizations to all symbols
    
    Example:
    {
        "price_adjustment": 5.0,      # +5% price increase
        "change_adjustment": 2.0,     # +2% change boost
        "force_signal": "STRONG_BUY", # Force bullish signal
        "confidence_boost": 20.0      # +20% confidence
    }
    """
    try:
        # Create global rule
        rule = CustomizationRule(
            name="Admin_Global_Customization",
            symbol="*",  # Apply to all symbols
            price_adjustment=data.price_adjustment,
            change_adjustment=data.change_adjustment,
            force_signal=data.force_signal,
            confidence_boost=data.confidence_boost
        )
        
        # Remove existing global rule if any
        custom_manager.remove_rule("Admin_Global_Customization")
        
        # Add new rule
        custom_manager.add_rule(rule)
        
        logger.info(f"Global customization applied: {data}")
        
        return {
            "success": True,
            "applied": "all_symbols",
            "rule": {
                "name": rule.name,
                "symbol": rule.symbol,
                "price_adjustment": rule.price_adjustment,
                "change_adjustment": rule.change_adjustment,
                "force_signal": rule.force_signal,
                "confidence_boost": rule.confidence_boost
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error applying global customization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.post("/symbol/{symbol}")
async def set_symbol_customization(symbol: str, data: SymbolCustomizationRequest):
    """
    Apply customization to specific symbol
    
    Example for BTC:
    {
        "manual_price": 100000.00,    # Set BTC to $100K
        "force_signal": "STRONG_BUY", # Force bullish
        "confidence_boost": 25.0      # +25% confidence
    }
    """
    try:
        symbol = symbol.upper()
        
        # Apply manual overrides
        if data.manual_price is not None:
            custom_manager.set_manual_price(symbol, data.manual_price)
        
        if data.force_signal is not None:
            custom_manager.set_manual_signal(symbol, data.force_signal)
        
        if data.confidence_boost is not None:
            custom_manager.set_confidence_boost(symbol, data.confidence_boost)
        
        # Create symbol-specific rule if price/change adjustment provided
        if data.price_adjustment is not None or data.change_adjustment is not None:
            rule = CustomizationRule(
                name=f"Admin_{symbol}_Customization",
                symbol=symbol,
                price_adjustment=data.price_adjustment,
                change_adjustment=data.change_adjustment
            )
            custom_manager.remove_rule(rule.name)
            custom_manager.add_rule(rule)
        
        logger.info(f"Symbol customization applied for {symbol}: {data}")
        
        return {
            "success": True,
            "symbol": symbol,
            "customizations": {
                "manual_price": data.manual_price,
                "force_signal": data.force_signal,
                "confidence_boost": data.confidence_boost,
                "price_adjustment": data.price_adjustment,
                "change_adjustment": data.change_adjustment
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error applying symbol customization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.post("/preset/{preset_name}")
async def apply_preset(preset_name: str):
    """
    Apply pre-configured scenario preset
    
    Available presets:
    - marketing: Bullish campaign (+5% prices, STRONG_BUY, +20% confidence)
    - risk_test: Bearish test (-5% prices, STRONG_SELL, +15% confidence)
    - vip: VIP treatment (+3% prices, BUY, +30% confidence)
    - conservative: Conservative signals (-1% prices, UP only, -15% confidence)
    - demo: Demo presentation (+10% prices, STRONG_BUY, +35% confidence)
    """
    try:
        presets = {
            "marketing": {
                "name": "Marketing_Campaign",
                "price_adj": 5.0,
                "change_adj": 2.0,
                "signal": "STRONG_BUY",
                "conf": 20.0,
                "description": "Bullish campaign for customer acquisition"
            },
            "risk_test": {
                "name": "Risk_Testing",
                "price_adj": -5.0,
                "change_adj": -2.0,
                "signal": "STRONG_SELL",
                "conf": 15.0,
                "description": "Bearish scenario for risk testing"
            },
            "vip": {
                "name": "VIP_Treatment",
                "price_adj": 3.0,
                "change_adj": 1.5,
                "signal": "BUY",
                "conf": 30.0,
                "description": "Premium data for VIP clients"
            },
            "conservative": {
                "name": "Conservative_Mode",
                "price_adj": -1.0,
                "change_adj": -0.5,
                "signal": "UP",
                "conf": -15.0,
                "description": "Conservative signals for risk-averse clients"
            },
            "demo": {
                "name": "Demo_Presentation",
                "price_adj": 10.0,
                "change_adj": 5.0,
                "signal": "STRONG_BUY",
                "conf": 35.0,
                "description": "Impressive data for presentations"
            }
        }
        
        if preset_name not in presets:
            raise HTTPException(
                status_code=404,
                detail=f"Preset '{preset_name}' not found. Available: {list(presets.keys())}"
            )
        
        preset = presets[preset_name]
        
        # Clear existing customizations
        custom_manager.clear_all_modifications()
        
        # Apply preset rule
        rule = CustomizationRule(
            name=preset["name"],
            symbol="*",
            price_adjustment=preset["price_adj"],
            change_adjustment=preset["change_adj"],
            force_signal=preset["signal"],
            confidence_boost=preset["conf"]
        )
        
        custom_manager.add_rule(rule)
        custom_manager.enable_customizations()
        
        logger.info(f"Preset '{preset_name}' applied")
        
        return {
            "success": True,
            "preset": preset_name,
            "description": preset["description"],
            "applied": {
                "price_adjustment": preset["price_adj"],
                "change_adjustment": preset["change_adj"],
                "force_signal": preset["signal"],
                "confidence_boost": preset["conf"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.get("/active")
async def get_active_customizations():
    """Get all active customizations"""
    try:
        active_rules = custom_manager.get_active_rules()
        
        return {
            "enabled": custom_manager.active_customizations,
            "total_rules": len(active_rules),
            "active_rules": active_rules,
            "manual_overrides": {
                "prices": {k: f"${v:,.2f}" for k, v in custom_manager.price_modifiers.items()},
                "signals": custom_manager.signal_overrides,
                "confidence_boosts": {k: f"+{v}%" for k, v in custom_manager.confidence_boosts.items()}
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting active customizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.post("/toggle")
async def toggle_customizations(enabled: bool):
    """
    Enable or disable all customizations
    
    POST /toggle?enabled=true  - Enable customizations
    POST /toggle?enabled=false - Disable customizations
    """
    try:
        if enabled:
            custom_manager.enable_customizations()
            logger.info("Customizations ENABLED")
        else:
            custom_manager.disable_customizations()
            logger.info("Customizations DISABLED")
        
        return {
            "success": True,
            "enabled": enabled,
            "status": "ENABLED" if enabled else "DISABLED",
            "message": f"Customizations have been {'enabled' if enabled else 'disabled'}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error toggling customizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.delete("/clear")
async def clear_all_customizations():
    """
    Emergency clear all customizations
    
    This will:
    - Remove all customization rules
    - Clear all manual overrides
    - Reset to original market data
    """
    try:
        custom_manager.clear_all_modifications()
        custom_manager.disable_customizations()
        
        logger.warning("All customizations CLEARED (Emergency reset)")
        
        return {
            "success": True,
            "cleared": True,
            "message": "All customizations have been cleared. System reset to original data.",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing customizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.post("/rule")
async def create_custom_rule(rule_data: CustomizationRuleRequest):
    """
    Create a custom customization rule
    
    This allows creating fully customized rules with all options
    """
    try:
        rule = CustomizationRule(
            name=rule_data.name,
            symbol=rule_data.symbol,
            price_adjustment=rule_data.price_adjustment,
            change_adjustment=rule_data.change_adjustment,
            force_signal=rule_data.force_signal,
            confidence_boost=rule_data.confidence_boost,
            custom_volume=rule_data.custom_volume,
            custom_market_cap=rule_data.custom_market_cap
        )
        
        custom_manager.add_rule(rule)
        
        logger.info(f"Custom rule created: {rule_data.name}")
        
        return {
            "success": True,
            "rule": {
                "name": rule.name,
                "symbol": rule.symbol,
                "price_adjustment": rule.price_adjustment,
                "change_adjustment": rule.change_adjustment,
                "force_signal": rule.force_signal,
                "confidence_boost": rule.confidence_boost
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating custom rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.delete("/rule/{rule_name}")
async def delete_rule(rule_name: str):
    """Delete a specific customization rule"""
    try:
        success = custom_manager.remove_rule(rule_name)
        
        if success:
            logger.info(f"Rule deleted: {rule_name}")
            return {
                "success": True,
                "rule_name": rule_name,
                "message": f"Rule '{rule_name}' has been deleted",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@control_router.get("/presets")
async def list_presets():
    """List all available scenario presets"""
    return {
        "presets": {
            "marketing": {
                "name": "Marketing Campaign",
                "description": "Bullish campaign for customer acquisition",
                "effect": "+5% prices, STRONG_BUY signals, +20% confidence"
            },
            "risk_test": {
                "name": "Risk Testing",
                "description": "Bearish scenario for risk testing",
                "effect": "-5% prices, STRONG_SELL signals, +15% confidence"
            },
            "vip": {
                "name": "VIP Treatment",
                "description": "Premium data for VIP clients",
                "effect": "+3% prices, BUY signals, +30% confidence"
            },
            "conservative": {
                "name": "Conservative Mode",
                "description": "Conservative signals for risk-averse clients",
                "effect": "-1% prices, UP signals only, -15% confidence"
            },
            "demo": {
                "name": "Demo Presentation",
                "description": "Impressive data for presentations",
                "effect": "+10% prices, STRONG_BUY signals, +35% confidence"
            }
        }
    }
