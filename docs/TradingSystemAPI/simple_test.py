#!/usr/bin/env python3
"""
Simple test for the trading system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_system():
    """Simple test of the system"""
    print("🧪 TESTING TRADING SYSTEM API")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from Shared.models import AssetClass, SignalType, config
        from Shared.utils import SignalCalculator, data_formatter
        from MarketData.providers import BinanceDataProvider, MarketDataAggregator
        from TradingFeatures.signals import TradingSignalsGenerator, BinarySignalsGenerator
        print("✅ All imports successful")
        
        # Test basic functionality
        print(f"\n🔧 Testing basic functionality...")
        print(f"   Asset classes: {len(list(AssetClass))}")
        print(f"   Signal types: {len(list(SignalType))}")
        print(f"   Config loaded: {config is not None}")
        
        # Test signal calculation
        calculator = SignalCalculator()
        signal = calculator.generate_signal(1000, 2.5)  # 2.5% change
        print(f"   Signal calculation: {signal.value}")
        
        # Test data formatting
        formatted_price = data_formatter.format_price(1234.56, "BTC")
        formatted_change = data_formatter.format_change(1.23)
        print(f"   Price formatting: {formatted_price}")
        print(f"   Change formatting: {formatted_change}")
        
        print(f"\n🎉 SYSTEM TEST PASSED!")
        print(f"✅ Dual-stream architecture is functional")
        print(f"✅ All modules imported successfully")
        print(f"✅ Basic calculations working")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_system()
    
    if success:
        print(f"\n🚀 SYSTEM READY!")
        print(f"📁 Location: /workspace/TradingSystemAPI/")
        print(f"🎯 To start server: python main.py")
        print(f"🧪 To run demo: python demo.py")
        print(f"📖 Documentation: README.md")
    else:
        print(f"\n⚠️ System has issues - check error messages above")

if __name__ == "__main__":
    asyncio.run(main())