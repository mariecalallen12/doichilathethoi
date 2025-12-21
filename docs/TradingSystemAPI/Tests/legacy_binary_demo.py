#!/usr/bin/env python3
"""
Simple Binary Signals Demo
=========================

Simple demonstration of binary trading signals for customers
"""

import asyncio
import json
import sys
sys.path.append('.')

from customer_trading_dashboard import CustomerTradingDashboard

async def demo_binary_signals():
    """Demo binary signals for customer presentation"""
    print("🎯 BINARY TRADING SIGNALS DEMO")
    print("=" * 60)
    print("🔢 1 = BULLISH (UP/BUY)")
    print("🔢 0 = BEARISH (DOWN/SELL)")
    print("=" * 60)
    
    dashboard = CustomerTradingDashboard()
    signals_data = await dashboard.generate_customer_signals()
    
    # Binary-only display
    print(f"\n📊 BINARY SIGNALS ARRAY:")
    print("-" * 40)
    
    all_signals = signals_data["crypto"] + signals_data["forex"] + signals_data["metals"]
    
    print(f"{'Symbol':<10} {'Price':<12} {'Change':<8} {'Binary':<6} {'Status'}")
    print("-" * 40)
    
    binary_string = ""
    for signal in all_signals:
        status = "BULLISH" if signal["binary_code"] == "1" else "BEARISH"
        print(f"{signal['symbol']:<10} {signal['current_price']:<12} {signal['price_change_24h']:<8} {signal['binary_code']:<6} {status}")
        binary_string += signal["binary_code"]
    
    print("-" * 40)
    print(f"Binary Array: {binary_string}")
    print(f"Total Signals: {len(all_signals)}")
    
    # Summary by asset class
    print(f"\n📈 SUMMARY BY ASSET CLASS:")
    print("-" * 40)
    
    for asset_class in ["crypto", "forex", "metals"]:
        signals = signals_data[asset_class]
        bullish = sum(1 for s in signals if s["binary_code"] == "1")
        bearish = len(signals) - bullish
        
        print(f"{asset_class.upper():<8}: {bullish} bullish (1) | {bearish} bearish (0)")
    
    # Overall market sentiment
    total_bullish = sum(1 for s in all_signals if s["binary_code"] == "1")
    total_bearish = len(all_signals) - total_bullish
    sentiment = "BULLISH" if total_bullish > total_bearish else "BEARISH"
    
    print(f"\n🎯 MARKET SENTIMENT: {sentiment}")
    print(f"📊 Bullish Signals: {total_bullish} ({total_bullish/len(all_signals)*100:.1f}%)")
    print(f"📊 Bearish Signals: {total_bearish} ({total_bearish/len(all_signals)*100:.1f}%)")
    
    # JSON output for integration
    print(f"\n📱 JSON OUTPUT FOR CUSTOMER INTEGRATION:")
    print("-" * 50)
    
    json_output = {
        "timestamp": signals_data["timestamp"],
        "market_sentiment": sentiment,
        "total_signals": len(all_signals),
        "binary_array": [s["binary_code"] for s in all_signals],
        "symbols": [s["symbol"] for s in all_signals],
        "signals": all_signals
    }
    
    print(json.dumps(json_output, indent=2)[:500] + "...")
    
    return json_output

async def main():
    """Main demo function"""
    try:
        result = await demo_binary_signals()
        print(f"\n✅ Binary signals demo completed successfully!")
        print(f"🔗 Ready for customer integration")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())