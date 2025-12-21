#!/usr/bin/env python3
"""
Test imports for each module
"""

def test_shared_imports():
    """Test Shared module imports"""
    try:
        import sys
        sys.path.append('.')
        from Shared.models import AssetClass, SignalType, config
        from Shared.utils import CacheManager, RateLimiter, SignalCalculator
        print("✅ Shared imports successful")
        return True
    except Exception as e:
        print(f"❌ Shared imports failed: {e}")
        return False

def test_marketdata_imports():
    """Test MarketData module imports"""
    try:
        import sys
        sys.path.append('.')
        from MarketData.providers import BinanceDataProvider, MarketDataAggregator
        print("✅ MarketData imports successful")
        return True
    except Exception as e:
        print(f"❌ MarketData imports failed: {e}")
        return False

def test_tradingfeatures_imports():
    """Test TradingFeatures module imports"""
    try:
        import sys
        sys.path.append('.')
        from TradingFeatures.signals import TradingSignalsGenerator, BinarySignalsGenerator
        print("✅ TradingFeatures imports successful")
        return True
    except Exception as e:
        print(f"❌ TradingFeatures imports failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING IMPORTS")
    print("=" * 40)
    
    shared_ok = test_shared_imports()
    market_ok = test_marketdata_imports()
    trading_ok = test_tradingfeatures_imports()
    
    print(f"\n📊 Results:")
    print(f"   Shared: {'✅' if shared_ok else '❌'}")
    print(f"   MarketData: {'✅' if market_ok else '❌'}")
    print(f"   TradingFeatures: {'✅' if trading_ok else '❌'}")
    
    if all([shared_ok, market_ok, trading_ok]):
        print(f"\n🎉 All imports successful!")
    else:
        print(f"\n⚠️ Some imports failed - check dependencies")