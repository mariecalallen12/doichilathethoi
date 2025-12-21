#!/usr/bin/env python3
"""
Debug Crypto APIs - Tìm hiểu tại sao chỉ BTC hoạt động
"""

import asyncio
import aiohttp
import sys
sys.path.append('.')

from free_crypto_data_aggregator import aggregator

async def test_binance_api_directly():
    """Test Binance API trực tiếp cho nhiều symbols"""
    print("🔍 DEBUGGING BINANCE API")
    print("=" * 50)
    
    test_symbols = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA"]
    binance_base = "https://data-api.binance.vision"
    
    async with aiohttp.ClientSession() as session:
        for symbol in test_symbols:
            try:
                binance_symbol = f"{symbol.upper()}USDT"
                url = f"{binance_base}/api/v3/ticker/24hr"
                params = {"symbol": binance_symbol}
                
                print(f"\n📡 Testing {symbol} -> {binance_symbol}")
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ SUCCESS: ${float(data['lastPrice']):,.2f}")
                        print(f"   📊 24h Change: {float(data['priceChangePercent']):.2f}%")
                        print(f"   💹 Volume: {float(data['volume']):,.2f}")
                    else:
                        print(f"   ❌ HTTP {response.status}: {await response.text()[:100]}")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")

async def test_coingecko_api_directly():
    """Test CoinGecko API trực tiếp"""
    print("\n🔍 DEBUGGING COINGECKO API")
    print("=" * 50)
    
    # Test some common symbols with their CoinGecko IDs
    test_mappings = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "DOT": "polkadot",
        "AVAX": "avalanche-2",
        "LINK": "chainlink"
    }
    
    async with aiohttp.ClientSession() as session:
        # Test single coin first
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,binancecoin,solana,ripple",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true"
        }
        
        try:
            print(f"\n📡 Testing CoinGecko batch API...")
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS: Got data for {len(data)} coins")
                    for coin_id, coin_data in data.items():
                        print(f"   📊 {coin_id}: ${coin_data['usd']:,.2f} (24h: {coin_data.get('usd_24h_change', 0):.2f}%)")
                else:
                    print(f"   ❌ HTTP {response.status}: {await response.text()[:100]}")
                    
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        # Test individual coins
        print(f"\n📡 Testing individual CoinGecko APIs...")
        for symbol, coin_id in list(test_mappings.items())[:3]:
            try:
                url = "https://api.coingecko.com/api/v3/simple/price"
                params = {
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true"
                }
                
                async with session.get(url, params=params, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        if coin_id in data:
                            price = data[coin_id]['usd']
                            change = data[coin_id].get('usd_24h_change', 0)
                            print(f"   ✅ {symbol} ({coin_id}): ${price:,.2f} (24h: {change:.2f}%)")
                        else:
                            print(f"   ❌ {symbol}: Coin ID not found in response")
                    else:
                        print(f"   ❌ {symbol}: HTTP {response.status}")
                        
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {str(e)[:50]}")

async def test_aggregator_methods():
    """Test các phương thức của aggregator"""
    print("\n🔍 DEBUGGING AGGREGATOR METHODS")
    print("=" * 50)
    
    test_symbols = ["BTC", "ETH", "BNB"]
    
    for symbol in test_symbols:
        print(f"\n📡 Testing {symbol} with aggregator...")
        
        # Test Binance method
        try:
            binance_data = await aggregator.get_binance_price(symbol)
            if binance_data:
                print(f"   ✅ Binance: ${binance_data.price:,.2f}")
            else:
                print(f"   ❌ Binance: No data")
        except Exception as e:
            print(f"   ❌ Binance error: {str(e)[:50]}")
        
        # Test CoinGecko method
        try:
            coingecko_data = await aggregator.get_coingecko_price(symbol)
            if coingecko_data:
                print(f"   ✅ CoinGecko: ${coingecko_data.price:,.2f}")
            else:
                print(f"   ❌ CoinGecko: No data")
        except Exception as e:
            print(f"   ❌ CoinGecko error: {str(e)[:50]}")

async def check_symbol_mappings():
    """Kiểm tra symbol mappings"""
    print("\n🔍 CHECKING SYMBOL MAPPINGS")
    print("=" * 50)
    
    print("Current symbol mappings in aggregator:")
    for symbol, coin_id in aggregator.symbol_mappings.items():
        print(f"   {symbol} -> {coin_id}")
    
    print(f"\nTesting mapping lookup:")
    test_symbols = ["BTC", "ETH", "BNB", "SOL", "XRP"]
    for symbol in test_symbols:
        coin_id = aggregator.symbol_mappings.get(symbol.upper())
        print(f"   {symbol}: {coin_id}")

async def main():
    """Main debug function"""
    print("🔧 CRYPTO API DEBUGGING SESSION")
    print("=" * 60)
    
    await check_symbol_mappings()
    await test_binance_api_directly()
    await test_coingecko_api_directly()
    await test_aggregator_methods()
    
    print("\n🎯 DEBUG SUMMARY")
    print("=" * 60)
    print("Check the results above to identify:")
    print("1. Which APIs are working correctly")
    print("2. Which symbols are failing and why")
    print("3. Whether the issue is with:")
    print("   - API connectivity")
    print("   - Symbol mappings")
    print("   - Rate limiting")
    print("   - Data format parsing")

if __name__ == "__main__":
    asyncio.run(main())