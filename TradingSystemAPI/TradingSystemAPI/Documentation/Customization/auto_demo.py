#!/usr/bin/env python3
"""
Automatic Customization Demo - Full Examples
============================================

Comprehensive demo of all customization features (automatic mode)
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Documentation.Customization.custom_data_manager import CustomizationRule, custom_manager

class AutoCustomizationDemo:
    """Complete automatic demo of customization capabilities"""
    
    def __init__(self):
        self.demo_symbols = ["BTC", "ETH", "SOL", "XRP", "ADA"]
        self.original_data = {
            "BTC": {"price": 88169.00, "change": 0.05, "signal": "UP", "confidence": 75.0},
            "ETH": {"price": 2975.00, "change": -0.33, "signal": "DOWN", "confidence": 60.0},
            "SOL": {"price": 126.20, "change": -0.71, "signal": "DOWN", "confidence": 65.0},
            "XRP": {"price": 1.93, "change": 1.30, "signal": "UP", "confidence": 70.0},
            "ADA": {"price": 0.37, "change": -0.80, "signal": "DOWN", "confidence": 55.0}
        }
    
    def clear_demo_data(self):
        """Clear all previous customizations"""
        custom_manager.clear_all_modifications()
        print("🧹 Cleared all customizations")
    
    def show_original_data(self):
        """Display original data before customization"""
        print("\n📊 ORIGINAL DATA (Before Customization)")
        print("=" * 60)
        for symbol, data in self.original_data.items():
            print(f"{symbol:4s}: ${data['price']:>10.2f} | {data['change']:+6.2f}% | "
                  f"{data['signal']:>12s} | Confidence: {data['confidence']:>5.1f}%")
    
    def show_customized_data(self, title):
        """Display customized data after applying rules"""
        print(f"\n🎯 {title}")
        print("=" * 60)
        for symbol, data in self.original_data.items():
            # Apply customizations
            price = custom_manager.apply_price_modification(symbol, data['price'])
            change = custom_manager.apply_change_modification(symbol, data['change'])
            signal = custom_manager.apply_signal_override(symbol, data['signal'])
            confidence = custom_manager.apply_confidence_boost(symbol, data['confidence'])
            
            # Check if modifications were applied
            modifications = []
            if price != data['price']:
                modifications.append(f"Price: ${data['price']:.2f} → ${price:.2f}")
            if change != data['change']:
                modifications.append(f"Change: {data['change']:+.2f}% → {change:+.2f}%")
            if signal != data['signal']:
                modifications.append(f"Signal: {data['signal']} → {signal}")
            if confidence != data['confidence']:
                modifications.append(f"Confidence: {data['confidence']:.1f}% → {confidence:.1f}%")
            
            mod_indicator = " ✏️" if modifications else ""
            
            print(f"{symbol:4s}: ${price:>10.2f} | {change:+6.2f}% | "
                  f"{signal:>12s} | Confidence: {confidence:>5.1f}%{mod_indicator}")
            
            if modifications:
                print(f"     └─ Changes: {', '.join(modifications)}")
    
    def demo_scenario_1_bullish_market(self):
        """Demo Scenario 1: Bullish Market for Marketing"""
        print("\n🚀 DEMO SCENARIO 1: BULLISH MARKET (Marketing Campaign)")
        print("Goal: Make everything look positive for customer attraction")
        
        # Setup: Make everything bullish
        custom_manager.add_rule(CustomizationRule(
            name="Marketing_Bullish",
            symbol="*",  # All symbols
            price_adjustment=5.0,      # +5% price boost
            change_adjustment=2.0,     # +2% change boost
            force_signal="STRONG_BUY", # Force strong buy signals
            confidence_boost=20.0      # +20% confidence
        ))
        
        self.show_customized_data("BULLISH MARKET DATA (After Marketing Customization)")
        
        print("\n💡 Use Case: Marketing website, promotional materials")
        print("📊 Impact: All prices up, all signals bullish, high confidence")
    
    def demo_scenario_2_bearish_market(self):
        """Demo Scenario 2: Bearish Market for Risk Testing"""
        print("\n📉 DEMO SCENARIO 2: BEARISH MARKET (Risk Testing)")
        print("Goal: Test system behavior with negative market conditions")
        
        self.clear_demo_data()
        
        # Setup: Make everything bearish
        custom_manager.add_rule(CustomizationRule(
            name="Risk_Testing_Bearish",
            symbol="*",
            price_adjustment=-5.0,     # -5% price drop
            change_adjustment=-2.0,    # -2% change drop
            force_signal="STRONG_SELL",# Force strong sell signals
            confidence_boost=15.0      # High confidence in bearish signals
        ))
        
        self.show_customized_data("BEARISH MARKET DATA (After Risk Testing Customization)")
        
        print("\n💡 Use Case: Risk management testing, stress testing")
        print("📊 Impact: All prices down, all signals bearish, risk scenarios")
    
    def demo_scenario_3_selective_boost(self):
        """Demo Scenario 3: Selective Boost for VIP Clients"""
        print("\n👑 DEMO SCENARIO 3: SELECTIVE BOOST (VIP Treatment)")
        print("Goal: Premium experience for VIP clients")
        
        self.clear_demo_data()
        
        # Setup: Boost only top cryptocurrencies
        custom_manager.add_rule(CustomizationRule(
            name="VIP_BTC_ETH_Boost",
            symbol="BTC",  # Bitcoin premium treatment
            price_adjustment=3.0,
            change_adjustment=1.0,
            force_signal="STRONG_BUY",
            confidence_boost=30.0
        ))
        
        custom_manager.add_rule(CustomizationRule(
            name="VIP_ETH_Premium",
            symbol="ETH",
            price_adjustment=2.5,
            change_adjustment=0.8,
            force_signal="BUY",
            confidence_boost=25.0
        ))
        
        # XRP gets moderate boost
        custom_manager.set_manual_signal("XRP", "STRONG_BUY")
        custom_manager.set_confidence_boost("XRP", 20.0)
        
        self.show_customized_data("VIP CLIENT DATA (After Selective Customization)")
        
        print("\n💡 Use Case: VIP client dashboards, premium features")
        print("📊 Impact: BTC/ETH get premium treatment, others moderate")
    
    def demo_scenario_4_manual_overrides(self):
        """Demo Scenario 4: Manual Overrides for Specific Needs"""
        print("\n🔧 DEMO SCENARIO 4: MANUAL OVERRIDES (Custom Requirements)")
        print("Goal: Manual control for specific requirements")
        
        self.clear_demo_data()
        
        # Manual overrides
        custom_manager.set_manual_price("BTC", 100000.00)  # Set BTC to $100k
        custom_manager.set_manual_price("XRP", 5.00)      # Set XRP to $5
        custom_manager.set_manual_signal("SOL", "STRONG_BUY")  # Force SOL bullish
        custom_manager.set_confidence_boost("ADA", 40.0)  # High confidence for ADA
        
        self.show_customized_data("MANUAL OVERRIDES (After Manual Customization)")
        
        print("\n💡 Use Case: Specific client requirements, custom pricing")
        print("📊 Impact: Direct price setting, signal forcing, confidence boosting")
    
    def demo_scenario_5_conservative_approach(self):
        """Demo Scenario 5: Conservative Signals for Risk-Averse Clients"""
        print("\n🛡️ DEMO SCENARIO 5: CONSERVATIVE APPROACH (Risk-Averse)")
        print("Goal: Lower confidence, more cautious signals")
        
        self.clear_demo_data()
        
        # Conservative approach: lower confidence, moderate signals
        custom_manager.add_rule(CustomizationRule(
            name="Conservative_Signals",
            symbol="*",
            confidence_boost=-15.0,  # Reduce confidence by 15%
            price_adjustment=-1.0,   # Slightly conservative pricing
            force_signal="UP"        # Force only upward trend (not strong buy)
        ))
        
        self.show_customized_data("CONSERVATIVE DATA (After Conservative Customization)")
        
        print("\n💡 Use Case: Risk-averse clients, conservative investment strategies")
        print("📊 Impact: Lower confidence, cautious signals, conservative pricing")
    
    def demo_scenario_6_toggle_demo(self):
        """Demo Scenario 6: Toggle Customizations On/Off"""
        print("\n🔄 DEMO SCENARIO 6: TOGGLE DEMO (Enable/Disable)")
        print("Goal: Show how to toggle customizations on/off")
        
        # Enable with bullish rules
        custom_manager.add_rule(CustomizationRule(
            name="Toggle_Demo_Bullish",
            symbol="*",
            price_adjustment=10.0,
            confidence_boost=25.0
        ))
        
        print("\nWith customizations ENABLED:")
        custom_manager.enable_customizations()
        self.show_customized_data("CUSTOMIZATIONS ENABLED")
        
        print("\nWith customizations DISABLED:")
        custom_manager.disable_customizations()
        self.show_customized_data("CUSTOMIZATIONS DISABLED (Original Data)")
        
        # Re-enable
        custom_manager.enable_customizations()
        print("\nCustomizations RE-ENABLED")
        
        print("\n💡 Use Case: Testing with/without customizations, A/B testing")
        print("📊 Impact: Easy toggle between original and customized data")
    
    def show_active_rules(self):
        """Show currently active rules"""
        print(f"\n📋 CURRENTLY ACTIVE RULES:")
        active_rules = custom_manager.get_active_rules()
        if active_rules:
            for rule_name in active_rules:
                rule = custom_manager.customization_rules[rule_name]
                print(f"   • {rule_name}: {rule.symbol} "
                      f"(Price: {rule.price_adjustment or 0:+.1f}%, "
                      f"Signal: {rule.force_signal or 'auto'}, "
                      f"Confidence: +{rule.confidence_boost or 0:.1f}%)")
        else:
            print("   No active rules")
    
    def run_complete_demo(self):
        """Run complete automatic customization demo"""
        print("🎮 COMPREHENSIVE CUSTOMIZATION DEMO")
        print("=" * 60)
        print("This demo shows all customization capabilities")
        print("for technical staff integration with various projects")
        
        # Show original data
        self.show_original_data()
        
        # Run all scenarios automatically
        scenarios = [
            self.demo_scenario_1_bullish_market,
            self.demo_scenario_2_bearish_market,
            self.demo_scenario_3_selective_boost,
            self.demo_scenario_4_manual_overrides,
            self.demo_scenario_5_conservative_approach,
            self.demo_scenario_6_toggle_demo
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            scenario()
            print(f"\n✅ Scenario {i}/6 completed")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETE - ALL SCENARIOS SHOWN")
        print("=" * 60)
        
        self.show_active_rules()
        
        print(f"\n✅ SUMMARY:")
        print(f"   • All 6 customization scenarios demonstrated")
        print(f"   • Price adjustments: ✅ Working")
        print(f"   • Signal overrides: ✅ Working")
        print(f"   • Confidence boosting: ✅ Working")
        print(f"   • Manual overrides: ✅ Working")
        print(f"   • Enable/Disable toggle: ✅ Working")
        
        print(f"\n🚀 READY FOR PRODUCTION:")
        print(f"   • Import: from Documentation.Customization.custom_data_manager import custom_manager")
        print(f"   • Use cases: Marketing, Testing, VIP treatment, Manual control")
        print(f"   • Flexibility: 100% customizable data for any project requirement")
        
        # Cleanup
        self.clear_demo_data()
        print(f"\n🧹 Demo cleanup completed - all customizations cleared")

def main():
    """Main automatic demo function"""
    demo = AutoCustomizationDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()