#!/usr/bin/env python3
"""
Customer Trading Dashboard - Binary Signals Display
=================================================

Giao diện hiển thị signals cho khách hàng với:
- Binary codes rõ ràng (1=UP/BUY, 0=DOWN/SELL)
- Multi-asset classes (Crypto, Forex, Metals)
- Real-time price movements
- Trading recommendations
- USDT-based calculations
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from trading_signals_system import trading_system, AssetClass, SignalType

logger = logging.getLogger(__name__)

class CustomerTradingDashboard:
    def __init__(self):
        self.trading_system = trading_system
        
    def get_signal_color(self, signal_type: SignalType) -> str:
        """Get color for signal type"""
        colors = {
            SignalType.STRONG_BUY: "🟢",
            SignalType.BUY: "🟢",
            SignalType.UP: "🟢",
            SignalType.DOWN: "🔴",
            SignalType.SELL: "🔴",
            SignalType.STRONG_SELL: "🔴"
        }
        return colors.get(signal_type, "⚪")
    
    def get_binary_indicator(self, signal_type: SignalType) -> str:
        """Get binary indicator for signal"""
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP]:
            return "1"
        else:
            return "0"
    
    def format_price(self, price: float, symbol: str) -> str:
        """Format price based on symbol type"""
        if any(metal in symbol for metal in ["XAU", "XAG"]):
            return f"${price:.2f}"
        elif any(forex in symbol for forex in ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]):
            return f"{price:.5f}"
        else:
            return f"${price:.4f}"
    
    async def get_metals_price_alternative(self, symbol: str) -> dict:
        """Alternative metals price source"""
        try:
            # Use metals-api.com (free tier)
            metals_mapping = {"XAU/USD": "gold", "XAG/USD": "silver"}
            metal = metals_mapping.get(symbol, "gold")
            
            url = f"https://api.metals-api.com/v1/latest/{metal}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rates" in data and "USD" in data["rates"]:
                            price = float(data["rates"]["USD"])
                            change_24h = 0.1  # Mock change for demo
                            
                            return {
                                "price": price,
                                "change_24h": change_24h,
                                "success": True
                            }
        except Exception as e:
            logger.error(f"Metals API error: {e}")
        
        # Fallback mock data
        return {
            "price": 2650.50 if "XAU" in symbol else 31.25,
            "change_24h": 0.15 if "XAU" in symbol else -0.05,
            "success": False
        }
    
    async def generate_customer_signals(self) -> dict:
        """Generate signals formatted for customer display"""
        print("🎯 GENERATING CUSTOMER TRADING SIGNALS")
        print("=" * 60)
        
        # Get crypto signals
        crypto_signals = []
        for symbol, config in self.trading_system.trading_symbols["CRYPTO"].items():
            signal = await self.trading_system.get_crypto_signal(symbol, config)
            if signal:
                crypto_signals.append(self.format_signal_for_customer(signal))
        
        # Get forex signals  
        forex_signals = []
        for symbol, config in self.trading_system.trading_symbols["FOREX"].items():
            signal = await self.trading_system.get_forex_signal(symbol, config)
            if signal:
                forex_signals.append(self.format_signal_for_customer(signal))
        
        # Get metals signals (with alternative source)
        metals_signals = []
        for symbol, config in self.trading_system.trading_symbols["METALS"].items():
            metals_data = await self.get_metals_price_alternative(symbol)
            if metals_data["success"]:
                # Create manual signal for metals
                signal = self.create_manual_metals_signal(symbol, metals_data)
                metals_signals.append(self.format_signal_for_customer(signal))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(crypto_signals) + len(forex_signals) + len(metals_signals),
            "crypto": crypto_signals,
            "forex": forex_signals,
            "metals": metals_signals,
            "summary": self.generate_market_summary(crypto_signals, forex_signals, metals_signals)
        }
    
    def create_manual_metals_signal(self, symbol: str, data: dict) -> dict:
        """Create manual signal for metals"""
        price = data["price"]
        change_24h = data["change_24h"]
        
        signal_type = SignalType.UP if change_24h > 0 else SignalType.DOWN
        signal_strength = self.trading_system._calculate_signal_strength(change_24h)
        confidence = self.trading_system._calculate_confidence(price, change_24h)
        entry, target, stop_loss = self.trading_system._calculate_targets(price, change_24h, signal_type)
        
        return {
            "symbol": symbol,
            "asset_class": AssetClass.METALS,
            "current_price": price,
            "price_change_24h": change_24h,
            "signal": signal_type,
            "signal_strength": signal_strength,
            "confidence": confidence,
            "entry_price": entry,
            "target_price": target,
            "stop_loss": stop_loss,
            "timeframe": "1H",
            "timestamp": datetime.now().isoformat()
        }
    
    def format_signal_for_customer(self, signal) -> dict:
        """Format signal for customer display"""
        return {
            "symbol": signal.symbol,
            "asset_class": signal.asset_class.value,
            "current_price": self.format_price(signal.current_price, signal.symbol),
            "price_change_24h": f"{signal.price_change_24h:+.2f}%",
            "signal": signal.signal.value,
            "signal_emoji": self.get_signal_color(signal.signal),
            "binary_code": self.get_binary_indicator(signal.signal),
            "signal_strength": f"{signal.signal_strength:.0f}%",
            "confidence": f"{signal.confidence:.0f}%",
            "entry_price": self.format_price(signal.entry_price, signal.symbol),
            "target_price": self.format_price(signal.target_price, signal.symbol),
            "stop_loss": self.format_price(signal.stop_loss, signal.symbol),
            "recommendation": self.get_recommendation_text(signal),
            "timeframe": signal.timeframe
        }
    
    def get_recommendation_text(self, signal) -> str:
        """Get human-readable recommendation"""
        signal_type = signal.signal
        strength = signal.signal_strength
        
        if signal_type == SignalType.STRONG_BUY:
            return f"Strong Buy Signal - {strength:.0f}% confidence"
        elif signal_type == SignalType.BUY:
            return f"Buy Signal - {strength:.0f}% confidence"
        elif signal_type == SignalType.UP:
            return f"Upward Trend - Monitor for entry"
        elif signal_type == SignalType.STRONG_SELL:
            return f"Strong Sell Signal - {strength:.0f}% confidence"
        elif signal_type == SignalType.SELL:
            return f"Sell Signal - {strength:.0f}% confidence"
        else:
            return f"Downward Trend - Consider exit"
    
    def generate_market_summary(self, crypto_signals, forex_signals, metals_signals) -> dict:
        """Generate market summary statistics"""
        all_signals = crypto_signals + forex_signals + metals_signals
        
        if not all_signals:
            return {"message": "No signals available"}
        
        # Count binary indicators
        binary_ones = sum(1 for signal in all_signals if signal["binary_code"] == "1")
        binary_zeros = len(all_signals) - binary_ones
        
        # Calculate average change
        changes = []
        for signal in all_signals:
            try:
                change_str = signal["price_change_24h"].replace('%', '').replace('+', '')
                changes.append(float(change_str))
            except:
                pass
        
        avg_change = sum(changes) / len(changes) if changes else 0
        
        return {
            "total_signals": len(all_signals),
            "bullish_signals": binary_ones,
            "bearish_signals": binary_zeros,
            "market_sentiment": "BULLISH" if binary_ones > binary_zeros else "BEARISH",
            "average_change_24h": f"{avg_change:+.2f}%",
            "strongest_signal": max(all_signals, key=lambda x: x["signal_strength"])["symbol"],
            "most_confident": max(all_signals, key=lambda x: float(x["confidence"].replace('%', '')))["symbol"]
        }
    
    def display_dashboard(self, signals_data: dict):
        """Display formatted dashboard for customers"""
        print("\n" + "="*80)
        print("🎯 CUSTOMER TRADING SIGNALS DASHBOARD")
        print("="*80)
        print(f"⏰ Last Updated: {signals_data['timestamp']}")
        print(f"📊 Total Signals: {signals_data['total_signals']}")
        
        # Market summary
        summary = signals_data["summary"]
        print(f"\n📈 MARKET OVERVIEW:")
        print(f"   Sentiment: {summary.get('market_sentiment', 'NEUTRAL')}")
        print(f"   Bullish: {summary.get('bullish_signals', 0)} | Bearish: {summary.get('bearish_signals', 0)}")
        print(f"   Avg Change: {summary.get('average_change_24h', '0.00%')}")
        print(f"   Strongest: {summary.get('strongest_signal', 'N/A')}")
        
        # Crypto signals
        print(f"\n🪙 CRYPTOCURRENCY SIGNALS ({len(signals_data['crypto'])} instruments):")
        print("-" * 80)
        print(f"{'Symbol':<8} {'Price':<12} {'24h Change':<10} {'Signal':<12} {'Binary':<6} {'Strength':<8} {'Recommendation'}")
        print("-" * 80)
        
        for signal in signals_data["crypto"][:10]:  # Show top 10
            print(f"{signal['symbol']:<8} {signal['current_price']:<12} {signal['price_change_24h']:<10} "
                  f"{signal['signal_emoji']}{signal['signal']:<8} {signal['binary_code']:<6} "
                  f"{signal['signal_strength']:<8} {signal['recommendation'][:25]}...")
        
        # Forex signals
        print(f"\n💱 FOREX SIGNALS ({len(signals_data['forex'])} pairs):")
        print("-" * 80)
        print(f"{'Pair':<8} {'Rate':<12} {'24h Change':<10} {'Signal':<12} {'Binary':<6} {'Strength':<8} {'Recommendation'}")
        print("-" * 80)
        
        for signal in signals_data["forex"]:
            print(f"{signal['symbol']:<8} {signal['current_price']:<12} {signal['price_change_24h']:<10} "
                  f"{signal['signal_emoji']}{signal['signal']:<8} {signal['binary_code']:<6} "
                  f"{signal['signal_strength']:<8} {signal['recommendation'][:25]}...")
        
        # Metals signals
        if signals_data["metals"]:
            print(f"\n🥇 PRECIOUS METALS ({len(signals_data['metals'])} instruments):")
            print("-" * 80)
            print(f"{'Metal':<8} {'Price':<12} {'24h Change':<10} {'Signal':<12} {'Binary':<6} {'Strength':<8} {'Recommendation'}")
            print("-" * 80)
            
            for signal in signals_data["metals"]:
                print(f"{signal['symbol']:<8} {signal['current_price']:<12} {signal['price_change_24h']:<10} "
                      f"{signal['signal_emoji']}{signal['signal']:<8} {signal['binary_code']:<6} "
                      f"{signal['signal_strength']:<8} {signal['recommendation'][:25]}...")
        
        # Binary summary table
        print(f"\n🔢 BINARY SIGNALS SUMMARY:")
        print("-" * 50)
        print(f"{'Category':<15} {'Total':<6} {'Bullish(1)':<12} {'Bearish(0)':<11}")
        print("-" * 50)
        
        crypto_bullish = sum(1 for s in signals_data["crypto"] if s["binary_code"] == "1")
        crypto_bearish = len(signals_data["crypto"]) - crypto_bullish
        
        forex_bullish = sum(1 for s in signals_data["forex"] if s["binary_code"] == "1")
        forex_bearish = len(signals_data["forex"]) - forex_bullish
        
        metals_bullish = sum(1 for s in signals_data["metals"] if s["binary_code"] == "1")
        metals_bearish = len(signals_data["metals"]) - metals_bullish
        
        print(f"{'Crypto':<15} {len(signals_data['crypto']):<6} {crypto_bullish:<12} {crypto_bearish:<11}")
        print(f"{'Forex':<15} {len(signals_data['forex']):<6} {forex_bullish:<12} {forex_bearish:<11}")
        print(f"{'Metals':<15} {len(signals_data['metals']):<6} {metals_bullish:<12} {metals_bearish:<11}")
        print("-" * 50)
        
        total_bullish = crypto_bullish + forex_bullish + metals_bullish
        total_bearish = crypto_bearish + forex_bearish + metals_bearish
        print(f"{'TOTAL':<15} {signals_data['total_signals']:<6} {total_bullish:<12} {total_bearish:<11}")

async def main():
    """Main function to run customer dashboard"""
    dashboard = CustomerTradingDashboard()
    
    try:
        # Generate signals
        signals_data = await dashboard.generate_customer_signals()
        
        # Display dashboard
        dashboard.display_dashboard(signals_data)
        
        print(f"\n✅ Customer trading dashboard generated successfully!")
        print(f"📱 Ready for customer display with binary indicators")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())