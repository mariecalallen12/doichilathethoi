#!/usr/bin/env python3
"""
Quick test for the crypto data API
"""

import asyncio
import sys
import os
sys.path.append('.')

# Import the aggregator
from free_crypto_data_aggregator import aggregator

async def quick_test():
    print("🚀 Testing Crypto Data API...")
    print("=" * 40)
    
    # Test BTC
    print("\n📊 Testing BTC price...")
    btc = await aggregator.get_aggregated_price('BTC')
    if "error" not in btc:
        print(f"✅ BTC Price: ${btc['price']:,.2f}")
        print(f"📈 Sources: {btc['source_count']}")
        print(f"💰 Change 24h: {btc['change_24h']:.3f}%")
        print(f"⏰ Timestamp: {btc['timestamp']}")
    else:
        print(f"❌ Error: {btc['error']}")
    
    # Test ETH
    print("\n📊 Testing ETH price...")
    eth = await aggregator.get_aggregated_price('ETH')
    if "error" not in eth:
        print(f"✅ ETH Price: ${eth['price']:,.2f}")
        print(f"📈 Sources: {eth['source_count']}")
    else:
        print(f"❌ Error: {eth['error']}")
    
    print("\n🎉 API Test Complete!")
    print("✨ Dữ liệu real-time miễn phí đã sẵn sàng!")

if __name__ == "__main__":
    asyncio.run(quick_test())