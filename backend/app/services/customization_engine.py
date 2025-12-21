"""
Customization Engine - Session-Aware Data Modification
======================================================

Upgraded version of custom_data_manager with:
- Session-based rule management
- Database persistence
- Redis caching for multi-instance support
- Enhanced admin controls
"""

import uuid
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Models
# ============================================================================

class CustomizationRule(BaseModel):
    """Rule for customizing API data"""
    name: str
    symbol: str = "*"  # Pattern: "*" = all symbols, otherwise exact match
    price_adjustment: Optional[float] = None  # Percentage adjustment (+/-)
    change_adjustment: Optional[float] = None  # Percentage change adjustment
    force_signal: Optional[str] = None  # Force specific signal (BUY/SELL/STRONG_BUY/STRONG_SELL)
    confidence_boost: Optional[float] = None  # Boost confidence by percentage
    custom_volume: Optional[float] = None  # Override volume
    custom_market_cap: Optional[float] = None  # Override market cap
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionConfig(BaseModel):
    """Session configuration"""
    session_id: str
    name: str
    enabled: bool = True
    rule_names: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Customization Engine
# ============================================================================

class CustomizationEngine:
    """
    Session-aware customization engine for API data modification
    
    Features:
    - Per-session rule management
    - Global rules support
    - Manual overrides
    - Database persistence (TODO)
    - Redis caching (TODO)
    """
    
    def __init__(self):
        # Global rule storage: rule_name -> CustomizationRule
        self.global_rules: Dict[str, CustomizationRule] = {}
        
        # Session-to-rules mapping: session_id -> Set[rule_name]
        self.session_rules: Dict[str, Set[str]] = {}
        
        # Session configurations
        self.sessions: Dict[str, SessionConfig] = {}
        
        # Current active session (set by middleware)
        self._current_session: Optional[str] = None
        
        # Global enable/disable flag
        self.enabled_globally: bool = False
        
        # Manual overrides (highest priority)
        self.manual_prices: Dict[str, float] = {}
        self.manual_signals: Dict[str, str] = {}
        self.manual_confidence: Dict[str, float] = {}
        
        logger.info("CustomizationEngine initialized")
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    def set_active_session(self, session_id: Optional[str]) -> None:
        """Set the current active session (called by middleware)"""
        self._current_session = session_id
        if session_id:
            logger.debug(f"Active session set to: {session_id}")
    
    def create_session(self, name: str, session_id: Optional[str] = None) -> SessionConfig:
        """Create a new session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = SessionConfig(
            session_id=session_id,
            name=name,
            enabled=True,
            rule_names=[]
        )
        self.sessions[session_id] = session
        self.session_rules[session_id] = set()
        
        logger.info(f"Created session: {session_id} ({name})")
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.session_rules.pop(session_id, None)
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def enable_customizations(self, session_id: Optional[str] = None) -> None:
        """Enable customizations for a session or globally"""
        if session_id:
            if session_id in self.sessions:
                self.sessions[session_id].enabled = True
                logger.info(f"Enabled customizations for session: {session_id}")
        else:
            self.enabled_globally = True
            logger.info("Enabled customizations globally")
    
    def disable_customizations(self, session_id: Optional[str] = None) -> None:
        """Disable customizations for a session or globally"""
        if session_id:
            if session_id in self.sessions:
                self.sessions[session_id].enabled = False
                logger.info(f"Disabled customizations for session: {session_id}")
        else:
            self.enabled_globally = False
            logger.info("Disabled customizations globally")
    
    # ========================================================================
    # Rule Management (CRUD)
    # ========================================================================
    
    def add_rule(self, rule: CustomizationRule) -> None:
        """Add or update a global rule"""
        rule.updated_at = datetime.utcnow()
        self.global_rules[rule.name] = rule
        logger.info(f"Added rule: {rule.name} for symbol {rule.symbol}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule"""
        if rule_name in self.global_rules:
            del self.global_rules[rule_name]
            # Remove from all sessions
            for session_rules in self.session_rules.values():
                session_rules.discard(rule_name)
            logger.info(f"Removed rule: {rule_name}")
            return True
        return False
    
    def update_rule(self, rule_name: str, rule: CustomizationRule) -> None:
        """Update an existing rule"""
        rule.updated_at = datetime.utcnow()
        self.global_rules[rule_name] = rule
        logger.info(f"Updated rule: {rule_name}")
    
    def get_rule(self, rule_name: str) -> Optional[CustomizationRule]:
        """Get a specific rule"""
        return self.global_rules.get(rule_name)
    
    def list_all_rules(self) -> List[CustomizationRule]:
        """List all global rules"""
        return list(self.global_rules.values())
    
    # ========================================================================
    # Session-Rule Binding
    # ========================================================================
    
    def bind_rule_to_session(self, session_id: str, rule_name: str) -> bool:
        """Bind a rule to a session"""
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return False
        
        if rule_name not in self.global_rules:
            logger.error(f"Rule not found: {rule_name}")
            return False
        
        self.session_rules[session_id].add(rule_name)
        self.sessions[session_id].rule_names.append(rule_name)
        logger.info(f"Bound rule {rule_name} to session {session_id}")
        return True
    
    def unbind_rule_from_session(self, session_id: str, rule_name: str) -> bool:
        """Unbind a rule from a session"""
        if session_id in self.session_rules:
            self.session_rules[session_id].discard(rule_name)
            if session_id in self.sessions:
                try:
                    self.sessions[session_id].rule_names.remove(rule_name)
                except ValueError:
                    pass
            logger.info(f"Unbound rule {rule_name} from session {session_id}")
            return True
        return False
    
    # ========================================================================
    # Active Rules Resolution
    # ========================================================================
    
    def get_active_rules(self) -> List[CustomizationRule]:
        """Get currently active rules for the current session"""
        # Check current session first
        if self._current_session and self._current_session in self.sessions:
            session = self.sessions[self._current_session]
            if session.enabled:
                return [
                    self.global_rules[name]
                    for name in self.session_rules.get(self._current_session, set())
                    if name in self.global_rules and self.global_rules[name].enabled
                ]
        
        # Fall back to global rules if enabled
        if self.enabled_globally:
            return [rule for rule in self.global_rules.values() if rule.enabled]
        
        return []
    
    def _matching_rules(self, symbol: str) -> List[CustomizationRule]:
        """Get rules matching the symbol"""
        rules = self.get_active_rules()
        return [r for r in rules if r.symbol == "*" or r.symbol == symbol]
    
    # ========================================================================
    # Data Modification Methods
    # ========================================================================
    
    def apply_price_modification(self, symbol: str, price: float) -> float:
        """Apply price modifications"""
        # Manual override has highest priority
        if symbol in self.manual_prices:
            return self.manual_prices[symbol]
        
        # Apply rules
        for rule in self._matching_rules(symbol):
            if rule.price_adjustment is not None:
                price = price * (1 + rule.price_adjustment / 100)
                logger.debug(f"Applied price adjustment for {symbol}: {rule.price_adjustment}%")
        
        return price
    
    def apply_change_modification(self, symbol: str, change: float) -> float:
        """Apply change modifications"""
        for rule in self._matching_rules(symbol):
            if rule.change_adjustment is not None:
                change = change + rule.change_adjustment
                logger.debug(f"Applied change adjustment for {symbol}: +{rule.change_adjustment}")
        
        return change
    
    def apply_signal_override(self, symbol: str, original_signal: str) -> str:
        """Apply signal overrides"""
        # Manual override
        if symbol in self.manual_signals:
            return self.manual_signals[symbol]
        
        # Rule override
        for rule in self._matching_rules(symbol):
            if rule.force_signal:
                logger.debug(f"Applied signal override for {symbol}: {original_signal} -> {rule.force_signal}")
                return rule.force_signal
        
        return original_signal
    
    def apply_confidence_boost(self, symbol: str, confidence: float) -> float:
        """Apply confidence boosts"""
        # Manual override
        if symbol in self.manual_confidence:
            return self.manual_confidence[symbol]
        
        # Rule boost
        for rule in self._matching_rules(symbol):
            if rule.confidence_boost is not None:
                confidence = confidence * (1 + rule.confidence_boost / 100)
                logger.debug(f"Applied confidence boost for {symbol}: {rule.confidence_boost}%")
        
        return min(confidence, 100.0)  # Cap at 100%
    
    def apply_volume_customization(self, symbol: str, original_volume: float) -> float:
        """Apply volume customizations"""
        for rule in self._matching_rules(symbol):
            if rule.custom_volume is not None:
                return rule.custom_volume
        return original_volume
    
    def apply_market_cap_customization(self, symbol: str, original_cap: float) -> float:
        """Apply market cap customizations"""
        for rule in self._matching_rules(symbol):
            if rule.custom_market_cap is not None:
                return rule.custom_market_cap
        return original_cap
    
    # ========================================================================
    # Manual Overrides
    # ========================================================================
    
    def set_manual_price(self, symbol: str, price: float) -> None:
        """Set manual price override"""
        self.manual_prices[symbol] = price
        logger.info(f"Set manual price for {symbol}: ${price}")
    
    def set_manual_signal(self, symbol: str, signal: str) -> None:
        """Set manual signal override"""
        self.manual_signals[symbol] = signal
        logger.info(f"Set manual signal for {symbol}: {signal}")
    
    def set_manual_confidence(self, symbol: str, confidence: float) -> None:
        """Set manual confidence override"""
        self.manual_confidence[symbol] = confidence
        logger.info(f"Set manual confidence for {symbol}: {confidence}%")
    
    def clear_manual_overrides(self, symbol: Optional[str] = None) -> None:
        """Clear manual overrides"""
        if symbol:
            self.manual_prices.pop(symbol, None)
            self.manual_signals.pop(symbol, None)
            self.manual_confidence.pop(symbol, None)
            logger.info(f"Cleared manual overrides for {symbol}")
        else:
            self.manual_prices.clear()
            self.manual_signals.clear()
            self.manual_confidence.clear()
            logger.info("Cleared all manual overrides")


# ============================================================================
# Singleton Instance
# ============================================================================

customization_engine = CustomizationEngine()
