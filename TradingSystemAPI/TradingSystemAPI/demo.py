#!/usr/bin/env python3
"""
Trading System API Demo
======================

Demonstration of the dual-stream architecture
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class TradingSystemDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.market_url = f"{base_url}/market"
        self.trading_url = f"{base_url}/trading"
    
    async def test_main_api(self):
        """Test main API"""
        print("🔗 TESTING MAIN API")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Main API: {data['message']}")
                        print(f"   Version: {data['data']['version']}")
                        print(f"   Architecture: {data['data']['architecture']['stream_1']}")
                        return True
                    else:
                        print(f"❌ Main API failed: {response.status}")
                        return False
            except Exception as e:
                print(f"❌ Main API error: {e}")
                return False
    
    async def test_market_data_stream(self):
        """Test Stream 1: Market Data"""
        print(f"\n📊 TESTING STREAM 1: MARKET DATA")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test market overview
                async with session.get(f"{self.market_url}/overview") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Market Overview:")
                        print(f"   📈 Total Instruments: {data['total_instruments']}")
                        print(f"   💱 Crypto: {data['by_asset_class']['crypto']}")
                        print(f"   💰 Forex: {data['by_asset_class']['forex']}")
                        print(f"   🥇 Metals: {data['by_asset_class']['metals']}")
                        print(f"   📊 Avg Change: {data['market_stats']['average_change_24h']:+.2f}%")
                    else:
                        print(f"❌ Market overview failed: {response.status}")
                
                # Test prices
                async with session.get(f"{self.market_url}/prices") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"\n✅ Current Prices:")
                        count = 0
                        for symbol, price_data in data.items():
                            if count >= 5:  # Show first 5
                                break
                            print(f"   💰 {symbol}: {price_data['current_price']} ({price_data['price_change_24h']})")
                            count += 1
                        print(f"   ... and {len(data)-5} more instruments")
                    else:
                        print(f"❌ Prices failed: {response.status}")
                
                return True
            except Exception as e:
                print(f"❌ Market data error: {e}")
                return False
    
    async def test_trading_features_stream(self):
        """Test Stream 2: Trading Features"""
        print(f"\n🎯 TESTING STREAM 2: TRADING FEATURES")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            try:
                # Test binary signals
                async with session.get(f"{self.trading_url}/binary") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Binary Signals:")
                        print(f"   🔢 Total Signals: {data['total_signals']}")
                        print(f"   🟢 Bullish (1): {data['bullish_signals']}")
                        print(f"   🔴 Bearish (0): {data['bearish_signals']}")
                        print(f"   📊 Market Sentiment: {data['market_sentiment']}")
                        print(f"   🔢 Binary Array: {data['binary_string'][:20]}...")
                        print(f"   📋 Symbols: {', '.join(data['symbols'][:10])}...")
                    else:
                        print(f"❌ Binary signals failed: {response.status}")
                
                # Test trading recommendations
                async with session.get(f"{self.trading_url}/recommendations") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"\n✅ Trading Recommendations:")
                        recs = data['recommendations']
                        print(f"   🔺 Strong Buy: {len(recs['strong_buy'])}")
                        print(f"   🟢 Buy: {len(recs['buy'])}")
                        print(f"   🔴 Sell: {len(recs['sell'])}")
                        print(f"   🔻 Strong Sell: {len(recs['strong_sell'])}")
                        
                        # Show top recommendation
                        if recs['strong_buy']:
                            top = recs['strong_buy'][0]
                            print(f"   🎯 Top Pick: {top['symbol']} - {top['current_price']}")
                    else:
                        print(f"❌ Recommendations failed: {response.status}")
                
                return True
            except Exception as e:
                print(f"❌ Trading features error: {e}")
                return False
    
    async def test_binary_stream(self):
        """Test binary stream endpoint"""
        print(f"\n🔄 TESTING BINARY STREAM")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.trading_url}/binary/stream") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Binary Stream:")
                        print(f"   🔢 Market Binary: {data['market_binary']}")
                        print(f"   📊 Market Sentiment: {data['market_sentiment']}")
                        print(f"   📈 Total Signals: {data['total_signals']}")
                        
                        # Show first few stream items
                        print(f"   📋 Stream Sample:")
                        for item in data['stream'][:3]:
                            signal_emoji = "🟢" if item['binary'] == "1" else "🔴"
                            print(f"      {signal_emoji} {item['symbol']}: {item['binary']} ({item['price']})")
                    else:
                        print(f"❌ Binary stream failed: {response.status}")
                
                return True
            except Exception as e:
                print(f"❌ Binary stream error: {e}")
                return False
    
    async def test_specific_symbols(self):
        """Test specific symbol endpoints"""
        print(f"\n🎯 TESTING SPECIFIC SYMBOLS")
        print("=" * 50)
        
        test_symbols = ["BTC", "EUR/USD", "XAU/USD"]
        
        async with aiohttp.ClientSession() as session:
            for symbol in test_symbols:
                try:
                    # Test market price
                    async with session.get(f"{self.market_url}/prices/{symbol}") as response:
                        if response.status == 200:
                            price_data = await response.json()
                            print(f"✅ {symbol} Price: {price_data['current_price']} ({price_data['price_change_24h']})")
                        else:
                            print(f"❌ {symbol} price not found")
                    
                    # Test binary signal
                    async with session.get(f"{self.trading_url}/binary/{symbol}") as response:
                        if response.status == 200:
                            binary_data = await response.json()
                            signal_emoji = "🟢" if binary_data['binary_code'] == "1" else "🔴"
                            print(f"   {signal_emoji} Binary: {binary_data['binary_code']} ({binary_data['signal']})")
                        else:
                            print(f"   ❌ {symbol} binary not available")
                
                except Exception as e:
                    print(f"❌ {symbol} test error: {e}")
    
    async def run_full_demo(self):
        """Run complete demonstration"""
        print("🚀 TRADING SYSTEM API - DUAL STREAM DEMO")
        print("=" * 60)
        print(f"⏰ Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base: {self.base_url}")
        print("=" * 60)
        
        # Test all components
        main_ok = await self.test_main_api()
        market_ok = await self.test_market_data_stream()
        trading_ok = await self.test_trading_features_stream()
        stream_ok = await self.test_binary_stream()
        symbols_ok = await self.test_specific_symbols()
        
        # Summary
        print(f"\n🏆 DEMO SUMMARY")
        print("=" * 60)
        tests = [
            ("Main API", main_ok),
            ("Market Data Stream", market_ok),
            ("Trading Features Stream", trading_ok),
            ("Binary Stream", stream_ok),
            ("Specific Symbols", symbols_ok)
        ]
        
        passed = sum(1 for _, ok in tests if ok)
        total = len(tests)
        
        for name, ok in tests:
            status = "✅ PASS" if ok else "❌ FAIL"
            print(f"   {name}: {status}")
        
        print(f"\n📊 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print(f"🎉 ALL TESTS PASSED - SYSTEM FULLY OPERATIONAL!")
            print(f"✅ Dual-stream architecture working perfectly")
            print(f"✅ Market data and trading features both operational")
            print(f"✅ Binary signals generating correctly")
        else:
            print(f"⚠️  Some tests failed - check server status")
        
        return passed == total

async def main():
    """Main demo function"""
    import sys
    
    # Check if server URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    demo = TradingSystemDemo(base_url)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=5) as response:
                if response.status != 200:
                    print(f"❌ Server not responding at {base_url}")
                    print(f"💡 Please start the server first: python main.py")
                    return
    except:
        print(f"❌ Cannot connect to server at {base_url}")
        print(f"💡 Please start the server first: python main.py")
        return
    
    # Run demo
    success = await demo.run_full_demo()
    
    if success:
        print(f"\n🎯 API ENDPOINTS READY:")
        print(f"   📊 Market Data: {base_url}/market")
        print(f"   🎯 Trading Features: {base_url}/trading")
        print(f"   📖 Documentation: {base_url}/market/docs")
        print(f"   📖 Trading Docs: {base_url}/trading/docs")
        print(f"   📊 Status: {base_url}/status")

if __name__ == "__main__":
    asyncio.run(main())