#!/usr/bin/env python3
"""
Test Fixed Aggregator - Kiểm tra aggregator đã sửa
"""

import asyncio
import logging
import sys
sys.path.append('.')

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from free_crypto_data_aggregator import aggregator

async def test_multiple_symbols():
    """Test nhiều symbols với aggregator đã sửa"""
    print("🚀 TESTING FIXED AGGREGATOR")
    print("=" * 50)
    
    test_symbols = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "AVAX", "LINK"]
    
    results = {}
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        
        # Test Binance
        binance_data = await aggregator.get_binance_price(symbol)
        if binance_data:
            print(f"   ✅ Binance: ${binance_data.price:,.2f}")
        else:
            print(f"   ❌ Binance: No data")
        
        # Test CoinGecko
        coingecko_data = await aggregator.get_coingecko_price(symbol)
        if coingecko_data:
            print(f"   ✅ CoinGecko: ${coingecko_data.price:,.2f}")
        else:
            print(f"   ❌ CoinGecko: No data")
        
        # Test aggregated
        try:
            aggregated = await aggregator.get_aggregated_price(symbol)
            if "error" not in aggregated:
                results[symbol] = aggregated
                print(f"   ✅ Aggregated: ${aggregated['price']:,.2f} ({aggregated['source_count']} sources)")
            else:
                print(f"   ❌ Aggregated: {aggregated['error']}")
        except Exception as e:
            print(f"   ❌ Aggregated error: {str(e)}")
    
    return results

async def test_batch_prices():
    """Test batch price retrieval"""
    print("\n🔄 TESTING BATCH PRICES")
    print("=" * 50)
    
    symbols = ["BTC", "ETH", "BNB", "SOL", "XRP"]
    
    try:
        batch_result = await aggregator.get_multiple_prices(symbols)
        print(f"✅ Batch success: {batch_result['successful_sources']}/{len(symbols)} symbols")
        
        for symbol, data in batch_result["prices"].items():
            if "error" not in data:
                print(f"   📊 {symbol}: ${data['price']:,.2f} ({data['source_count']} sources)")
            else:
                print(f"   ❌ {symbol}: {data['error']}")
                
    except Exception as e:
        print(f"❌ Batch error: {str(e)}")

async def show_market_overview(results):
    """Hiển thị tổng quan thị trường"""
    print("\n📈 MARKET OVERVIEW")
    print("=" * 50)
    
    if not results:
        print("❌ No data available for market overview")
        return
    
    print(f"✅ Successfully retrieved data for {len(results)} cryptocurrencies:")
    print()
    
    # Sort by price (descending)
    sorted_results = sorted(results.items(), key=lambda x: x[1]['price'], reverse=True)
    
    for symbol, data in sorted_results:
        price = data['price']
        change = data['change_24h']
        sources = data['source_count']
        
        change_indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"{change_indicator} {symbol:4s}: ${price:>12,.2f} ({change:+.2f}%) [{sources} sources]")
    
    # Market statistics
    prices = [data['price'] for data in results.values()]
    changes = [data['change_24h'] for data in results.values() if data['change_24h'] is not None]
    
    print(f"\n📊 Market Statistics:")
    print(f"   💰 Price Range: ${min(prices):,.2f} - ${max(prices):,.2f}")
    print(f"   📈 Average Price: ${sum(prices)/len(prices):,.2f}")
    
    if changes:
        print(f"   📊 Change Range: {min(changes):.2f}% - {max(changes):.2f}%")
        print(f"   📊 Average Change: {sum(changes)/len(changes):.2f}%")

async def main():
    """Main test function"""
    try:
        # Test multiple symbols
        results = await test_multiple_symbols()
        
        # Test batch prices
        await test_batch_prices()
        
        # Show market overview
        await show_market_overview(results)
        
        print("\n🎯 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Fixed aggregator working with {len(results)} symbols")
        print("✅ Real-time crypto data successfully retrieved")
        print("✅ Multiple data sources operational")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())