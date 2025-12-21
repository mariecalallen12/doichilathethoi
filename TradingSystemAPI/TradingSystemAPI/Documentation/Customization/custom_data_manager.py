#!/usr/bin/env python3
"""
Custom Data Manager
===================

Cho phép can thiệp và điều chỉnh dữ liệu API theo ý muốn
"""

import asyncio
import random
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class CustomizationRule:
    """Rule for customizing API data"""
    name: str
    symbol: str  # Symbol to apply rule to (or "*" for all)
    price_adjustment: Optional[float] = None  # Percentage adjustment
    change_adjustment: Optional[float] = None  # Percentage change adjustment
    force_signal: Optional[str] = None  # Force specific signal (BUY/SELL/UP/DOWN)
    confidence_boost: Optional[float] = None  # Boost confidence by percentage
    custom_volume: Optional[float] = None  # Override volume
    custom_market_cap: Optional[float] = None  # Override market cap
    enable: bool = True

class CustomDataManager:
    """Manages custom data modifications for API responses"""
    
    def __init__(self):
        self.customization_rules: Dict[str, CustomizationRule] = {}
        self.price_modifiers: Dict[str, float] = {}
        self.signal_overrides: Dict[str, str] = {}
        self.confidence_boosts: Dict[str, float] = {}
        self.active_customizations = True
        
    def add_rule(self, rule: CustomizationRule) -> None:
        """Add a customization rule"""
        self.customization_rules[rule.name] = rule
        print(f"✅ Added customization rule: {rule.name} for {rule.symbol}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a customization rule"""
        if rule_name in self.customization_rules:
            del self.customization_rules[rule_name]
            print(f"🗑️ Removed customization rule: {rule_name}")
            return True
        return False
    
    def apply_price_modification(self, symbol: str, original_price: float) -> float:
        """Apply price modifications based on rules"""
        if not self.active_customizations:
            return original_price
        
        # Check for specific symbol rules
        for rule in self.customization_rules.values():
            if rule.enable and (rule.symbol == symbol or rule.symbol == "*"):
                if rule.price_adjustment is not None:
                    modified_price = original_price * (1 + rule.price_adjustment / 100)
                    print(f"📊 Price modified for {symbol}: ${original_price:.2f} -> ${modified_price:.2f} ({rule.price_adjustment:+.1f}%)")
                    return modified_price
        
        return original_price
    
    def apply_change_modification(self, symbol: str, original_change: float) -> float:
        """Apply change modifications based on rules"""
        if not self.active_customizations:
            return original_change
        
        for rule in self.customization_rules.values():
            if rule.enable and (rule.symbol == symbol or rule.symbol == "*"):
                if rule.change_adjustment is not None:
                    modified_change = original_change + rule.change_adjustment
                    print(f"📈 Change modified for {symbol}: {original_change:+.2f}% -> {modified_change:+.2f}%")
                    return modified_change
        
        return original_change
    
    def apply_signal_override(self, symbol: str, original_signal: str) -> str:
        """Apply signal overrides based on rules"""
        if not self.active_customizations:
            return original_signal
        
        for rule in self.customization_rules.values():
            if rule.enable and (rule.symbol == symbol or rule.symbol == "*"):
                if rule.force_signal is not None:
                    print(f"🎯 Signal overridden for {symbol}: {original_signal} -> {rule.force_signal}")
                    return rule.force_signal
        
        return original_signal
    
    def apply_confidence_boost(self, symbol: str, original_confidence: float) -> float:
        """Apply confidence boosts based on rules"""
        if not self.active_customizations:
            return original_confidence
        
        for rule in self.customization_rules.values():
            if rule.enable and (rule.symbol == symbol or rule.symbol == "*"):
                if rule.confidence_boost is not None:
                    boosted_confidence = min(original_confidence + rule.confidence_boost, 100)
                    print(f"💪 Confidence boosted for {symbol}: {original_confidence:.1f}% -> {boosted_confidence:.1f}%")
                    return boosted_confidence
        
        return original_confidence
    
    def set_manual_price(self, symbol: str, price: float) -> None:
        """Set manual price for a symbol"""
        self.price_modifiers[symbol] = price
        print(f"🔧 Manual price set for {symbol}: ${price:.2f}")
    
    def set_manual_signal(self, symbol: str, signal: str) -> None:
        """Set manual signal for a symbol"""
        self.signal_overrides[symbol] = signal
        print(f"🎯 Manual signal set for {symbol}: {signal}")
    
    def set_confidence_boost(self, symbol: str, boost: float) -> None:
        """Set confidence boost for a symbol"""
        self.confidence_boosts[symbol] = boost
        print(f"💪 Confidence boost set for {symbol}: +{boost:.1f}%")
    
    def enable_customizations(self) -> None:
        """Enable customizations"""
        self.active_customizations = True
        print("✅ Customizations enabled")
    
    def disable_customizations(self) -> None:
        """Disable customizations"""
        self.active_customizations = False
        print("❌ Customizations disabled")
    
    def get_active_rules(self) -> List[str]:
        """Get list of active customization rules"""
        return [name for name, rule in self.customization_rules.items() if rule.enable]
    
    def clear_all_modifications(self) -> None:
        """Clear all customizations"""
        self.customization_rules.clear()
        self.price_modifiers.clear()
        self.signal_overrides.clear()
        self.confidence_boosts.clear()
        print("🧹 All customizations cleared")
    
    def generate_demo_data(self, symbol: str, price: float, change: float, signal: str, confidence: float) -> Dict[str, Any]:
        """Generate demo customized data"""
        print(f"\n🎮 GENERATING CUSTOMIZED DATA FOR {symbol}")
        print("-" * 50)
        
        # Apply manual price if set
        if symbol in self.price_modifiers:
            price = self.price_modifiers[symbol]
            print(f"🔧 Manual price applied: ${price:.2f}")
        
        # Apply price modifications
        modified_price = self.apply_price_modification(symbol, price)
        
        # Apply change modifications
        modified_change = self.apply_change_modification(symbol, change)
        
        # Apply signal overrides
        if symbol in self.signal_overrides:
            signal = self.signal_overrides[symbol]
            print(f"🎯 Manual signal applied: {signal}")
        
        modified_signal = self.apply_signal_override(symbol, signal)
        
        # Apply confidence boosts
        if symbol in self.confidence_boosts:
            boost = self.confidence_boosts[symbol]
            confidence = min(confidence + boost, 100)
            print(f"💪 Manual confidence boost: +{boost:.1f}%")
        
        boosted_confidence = self.apply_confidence_boost(symbol, confidence)
        
        return {
            "symbol": symbol,
            "original_data": {
                "price": price,
                "change": change,
                "signal": signal,
                "confidence": confidence
            },
            "customized_data": {
                "price": modified_price,
                "change": modified_change,
                "signal": modified_signal,
                "confidence": boosted_confidence
            },
            "modifications_applied": {
                "price_changed": modified_price != price,
                "change_changed": modified_change != change,
                "signal_changed": modified_signal != signal,
                "confidence_changed": boosted_confidence != confidence
            },
            "timestamp": datetime.now().isoformat()
        }

# Global instance
custom_manager = CustomDataManager()

def demo_customization_scenarios():
    """Demo various customization scenarios"""
    print("🚀 DEMO: CUSTOMIZATION SCENARIOS")
    print("=" * 60)
    
    # Scenario 1: Boost BTC price and force bullish signal
    print("\n📊 SCENARIO 1: Make BTC look more attractive")
    custom_manager.add_rule(CustomizationRule(
        name="BTC_Bullish_Boost",
        symbol="BTC",
        price_adjustment=5.0,  # +5% price
        change_adjustment=2.0,  # +2% change
        force_signal="STRONG_BUY",
        confidence_boost=15.0  # +15% confidence
    ))
    
    btc_data = custom_manager.generate_demo_data("BTC", 88169.00, 0.05, "UP", 75.0)
    print(f"📋 Result: {btc_data}")
    
    # Scenario 2: Make ETH look bearish
    print("\n📉 SCENARIO 2: Make ETH look bearish")
    custom_manager.add_rule(CustomizationRule(
        name="ETH_Bearish_Signal",
        symbol="ETH",
        price_adjustment=-3.0,  # -3% price
        change_adjustment=-1.5,  # -1.5% change
        force_signal="STRONG_SELL",
        confidence_boost=20.0
    ))
    
    eth_data = custom_manager.generate_demo_data("ETH", 2975.00, -0.33, "DOWN", 60.0)
    print(f"📋 Result: {eth_data}")
    
    # Scenario 3: Global boost for all symbols
    print("\n🌍 SCENARIO 3: Global confidence boost")
    custom_manager.add_rule(CustomizationRule(
        name="Global_Confidence_Boost",
        symbol="*",  # Apply to all
        confidence_boost=10.0
    ))
    
    # Scenario 4: Manual override for specific symbol
    print("\n🔧 SCENARIO 4: Manual override")
    custom_manager.set_manual_price("XRP", 5.00)  # Set XRP to $5.00
    custom_manager.set_manual_signal("XRP", "STRONG_BUY")  # Force bullish
    custom_manager.set_confidence_boost("XRP", 25.0)  # High confidence
    
    xrp_data = custom_manager.generate_demo_data("XRP", 1.93, 1.30, "UP", 65.0)
    print(f"📋 Result: {xrp_data}")
    
    print(f"\n✅ Demo completed!")
    print(f"📊 Active rules: {custom_manager.get_active_rules()}")

if __name__ == "__main__":
    demo_customization_scenarios()