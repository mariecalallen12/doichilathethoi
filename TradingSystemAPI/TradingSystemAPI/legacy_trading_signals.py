#!/usr/bin/env python3
"""
Trading Signals System - Binary Signal Generator
===============================================

Chuyển đổi dữ liệu từ multiple asset classes thành binary trading signals:
- Cryptocurrency (BTC, ETH, SOL, XRP...)
- Forex Pairs (EUR/USD, GBP/USD, USD/JPY...)
- Precious Metals (Gold XAU, Silver XAG)
- Commodities (Oil, Gas)

Tất cả denominated in USDT for consistent trading
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    UP = "UP"
    DOWN = "DOWN"
    BUY = "BUY"
    SELL = "SELL"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class AssetClass(Enum):
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    METALS = "METALS"
    COMMODITIES = "COMMODITIES"

@dataclass
class TradingSignal:
    """Trading signal structure"""
    symbol: str
    asset_class: AssetClass
    current_price: float
    price_change_24h: float
    signal: SignalType
    signal_strength: float  # 0-100
    confidence: float  # 0-100
    entry_price: float
    target_price: float
    stop_loss: float
    timeframe: str
    timestamp: str
    volume: Optional[float] = None
    market_cap: Optional[float] = None

class TradingSignalsSystem:
    def __init__(self):
        self.binance_base = "https://data-api.binance.vision"
        self.fx_base = "https://api.exchangerate-api.com/v4/latest"  # Free forex API
        self.metals_base = "https://api.metals.live/v1"  # Metals API
        self.cache = {}
        self.cache_ttl = 30  # 30 seconds cache
        
        # Trading symbols with asset classes
        self.trading_symbols = {
            # CRYPTO - All vs USDT
            "CRYPTO": {
                "BTC": {"binance": "BTCUSDT", "name": "Bitcoin"},
                "ETH": {"binance": "ETHUSDT", "name": "Ethereum"},
                "SOL": {"binance": "SOLUSDT", "name": "Solana"},
                "XRP": {"binance": "XRPUSDT", "name": "Ripple"},
                "ADA": {"binance": "ADAUSDT", "name": "Cardano"},
                "DOT": {"binance": "DOTUSDT", "name": "Polkadot"},
                "AVAX": {"binance": "AVAXUSDT", "name": "Avalanche"},
                "LINK": {"binance": "LINKUSDT", "name": "Chainlink"},
                "BNB": {"binance": "BNBUSDT", "name": "Binance Coin"},
                "DOGE": {"binance": "DOGEUSDT", "name": "Dogecoin"},
                "MATIC": {"binance": "MATICUSDT", "name": "Polygon"},
                "UNI": {"binance": "UNIUSDT", "name": "Uniswap"},
                "LTC": {"binance": "LTCUSDT", "name": "Litecoin"},
                "ATOM": {"binance": "ATOMUSDT", "name": "Cosmos"}
            },
            
            # FOREX - Major pairs vs USD
            "FOREX": {
                "EUR/USD": {"fx_api": "EUR", "base": "USD", "name": "Euro Dollar"},
                "GBP/USD": {"fx_api": "GBP", "base": "USD", "name": "British Pound"},
                "USD/JPY": {"fx_api": "JPY", "base": "USD", "name": "Dollar Yen"},
                "USD/CHF": {"fx_api": "CHF", "base": "USD", "name": "Dollar Swiss"},
                "AUD/USD": {"fx_api": "AUD", "base": "USD", "name": "Australian Dollar"},
                "USD/CAD": {"fx_api": "CAD", "base": "USD", "name": "Dollar Canadian"},
                "NZD/USD": {"fx_api": "NZD", "base": "USD", "name": "New Zealand Dollar"}
            },
            
            # METALS - Precious metals
            "METALS": {
                "XAU/USD": {"metals": "XAU", "name": "Gold"},
                "XAG/USD": {"metals": "XAG", "name": "Silver"}
            },
            
            # COMMODITIES - Energy and others
            "COMMODITIES": {
                "OIL/USD": {"commodity": "WTI", "name": "Crude Oil"},
                "GAS/USD": {"commodity": "NG", "name": "Natural Gas"}
            }
        }
        
        # Signal calculation parameters
        self.signal_thresholds = {
            "weak": 0.5,    # 0.5% change
            "moderate": 1.0, # 1% change  
            "strong": 2.0,   # 2% change
            "extreme": 5.0   # 5% change
        }
    
    def _generate_signal(self, price: float, change_24h: float, volume: float = None) -> SignalType:
        """Generate trading signal based on price change"""
        abs_change = abs(change_24h)
        
        if change_24h > 0:
            if abs_change >= self.signal_thresholds["extreme"]:
                return SignalType.STRONG_BUY
            elif abs_change >= self.signal_thresholds["strong"]:
                return SignalType.BUY
            elif abs_change >= self.signal_thresholds["moderate"]:
                return SignalType.UP
            else:
                return SignalType.UP
        else:
            if abs_change >= self.signal_thresholds["extreme"]:
                return SignalType.STRONG_SELL
            elif abs_change >= self.signal_thresholds["strong"]:
                return SignalType.SELL
            elif abs_change >= self.signal_thresholds["moderate"]:
                return SignalType.DOWN
            else:
                return SignalType.DOWN
    
    def _calculate_signal_strength(self, change_24h: float) -> float:
        """Calculate signal strength 0-100"""
        abs_change = abs(change_24h)
        if abs_change >= self.signal_thresholds["extreme"]:
            return 100
        elif abs_change >= self.signal_thresholds["strong"]:
            return 80 + (abs_change - self.signal_thresholds["strong"]) / (self.signal_thresholds["extreme"] - self.signal_thresholds["strong"]) * 20
        elif abs_change >= self.signal_thresholds["moderate"]:
            return 50 + (abs_change - self.signal_thresholds["moderate"]) / (self.signal_thresholds["strong"] - self.signal_thresholds["moderate"]) * 30
        elif abs_change >= self.signal_thresholds["weak"]:
            return 25 + (abs_change - self.signal_thresholds["weak"]) / (self.signal_thresholds["moderate"] - self.signal_thresholds["weak"]) * 25
        else:
            return 10 + (abs_change / self.signal_thresholds["weak"]) * 15
    
    def _calculate_confidence(self, price: float, change_24h: float, volume: float = None) -> float:
        """Calculate confidence score based on multiple factors"""
        confidence = 50  # Base confidence
        
        # Volume factor (if available)
        if volume:
            if volume > 1000000:  # High volume
                confidence += 20
            elif volume > 100000:  # Medium volume
                confidence += 10
        
        # Price change consistency
        abs_change = abs(change_24h)
        if abs_change > 2:  # Strong move
            confidence += 15
        elif abs_change > 1:  # Moderate move
            confidence += 10
        elif abs_change > 0.5:  # Weak move
            confidence += 5
        
        # Price level factor (higher prices = more reliable)
        if price > 1000:
            confidence += 10
        elif price > 100:
            confidence += 5
        
        return min(confidence, 100)
    
    def _calculate_targets(self, price: float, change_24h: float, signal: SignalType) -> tuple:
        """Calculate entry, target, and stop loss prices"""
        if signal in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP]:
            entry = price
            # Target 1-3% up for BUY, 0.5-1% for UP
            if signal == SignalType.STRONG_BUY:
                target = price * 1.03
                stop_loss = price * 0.98
            elif signal == SignalType.BUY:
                target = price * 1.02
                stop_loss = price * 0.985
            else:  # UP
                target = price * 1.01
                stop_loss = price * 0.99
        else:
            entry = price
            # Target 1-3% down for SELL, 0.5-1% for DOWN
            if signal == SignalType.STRONG_SELL:
                target = price * 0.97
                stop_loss = price * 1.02
            elif signal == SignalType.SELL:
                target = price * 0.98
                stop_loss = price * 1.015
            else:  # DOWN
                target = price * 0.99
                stop_loss = price * 1.01
        
        return entry, target, stop_loss
    
    async def get_crypto_signal(self, symbol: str, config: Dict) -> Optional[TradingSignal]:
        """Get trading signal for cryptocurrency"""
        try:
            binance_symbol = config["binance"]
            url = f"{self.binance_base}/api/v3/ticker/24hr"
            params = {"symbol": binance_symbol}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        price = float(data["lastPrice"])
                        change_24h = float(data["priceChangePercent"])
                        volume = float(data["volume"])
                        
                        signal = self._generate_signal(price, change_24h, volume)
                        strength = self._calculate_signal_strength(change_24h)
                        confidence = self._calculate_confidence(price, change_24h, volume)
                        entry, target, stop_loss = self._calculate_targets(price, change_24h, signal)
                        
                        return TradingSignal(
                            symbol=symbol,
                            asset_class=AssetClass.CRYPTO,
                            current_price=price,
                            price_change_24h=change_24h,
                            signal=signal,
                            signal_strength=strength,
                            confidence=confidence,
                            entry_price=entry,
                            target_price=target,
                            stop_loss=stop_loss,
                            timeframe="1H",
                            timestamp=datetime.now().isoformat(),
                            volume=volume
                        )
        except Exception as e:
            logger.error(f"Error getting crypto signal for {symbol}: {e}")
        
        return None
    
    async def get_forex_signal(self, symbol: str, config: Dict) -> Optional[TradingSignal]:
        """Get trading signal for forex pair"""
        try:
            fx_api = config["fx_api"]
            url = f"{self.fx_base}/{fx_api}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rates" in data:
                            rate = data["rates"].get(config["base"], 1.0)
                            price = float(rate)
                            
                            # Mock 24h change for forex (you'd need historical data for real calculation)
                            change_24h = (price - 1.0) * 0.1  # Small mock change
                            
                            signal = self._generate_signal(price, change_24h)
                            strength = self._calculate_signal_strength(change_24h)
                            confidence = self._calculate_confidence(price, change_24h)
                            entry, target, stop_loss = self._calculate_targets(price, change_24h, signal)
                            
                            return TradingSignal(
                                symbol=symbol,
                                asset_class=AssetClass.FOREX,
                                current_price=price,
                                price_change_24h=change_24h,
                                signal=signal,
                                signal_strength=strength,
                                confidence=confidence,
                                entry_price=entry,
                                target_price=target,
                                stop_loss=stop_loss,
                                timeframe="1H",
                                timestamp=datetime.now().isoformat()
                            )
        except Exception as e:
            logger.error(f"Error getting forex signal for {symbol}: {e}")
        
        return None
    
    async def get_metals_signal(self, symbol: str, config: Dict) -> Optional[TradingSignal]:
        """Get trading signal for precious metals"""
        try:
            metals_symbol = config["metals"]
            url = f"{self.metals_base}/spot/{metals_symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "rate" in data:
                            price = float(data["rate"])
                            
                            # Mock 24h change for metals
                            change_24h = (price - 2000) * 0.001 if metals_symbol == "XAU" else (price - 25) * 0.01
                            
                            signal = self._generate_signal(price, change_24h)
                            strength = self._calculate_signal_strength(change_24h)
                            confidence = self._calculate_confidence(price, change_24h)
                            entry, target, stop_loss = self._calculate_targets(price, change_24h, signal)
                            
                            return TradingSignal(
                                symbol=symbol,
                                asset_class=AssetClass.METALS,
                                current_price=price,
                                price_change_24h=change_24h,
                                signal=signal,
                                signal_strength=strength,
                                confidence=confidence,
                                entry_price=entry,
                                target_price=target,
                                stop_loss=stop_loss,
                                timeframe="1H",
                                timestamp=datetime.now().isoformat()
                            )
        except Exception as e:
            logger.error(f"Error getting metals signal for {symbol}: {e}")
        
        return None
    
    async def get_all_signals(self) -> Dict[str, List[TradingSignal]]:
        """Get trading signals for all instruments"""
        all_signals = {}
        
        for asset_class, symbols in self.trading_symbols.items():
            signals = []
            
            for symbol, config in symbols.items():
                if asset_class == "CRYPTO":
                    signal = await self.get_crypto_signal(symbol, config)
                elif asset_class == "FOREX":
                    signal = await self.get_forex_signal(symbol, config)
                elif asset_class == "METALS":
                    signal = await self.get_metals_signal(symbol, config)
                else:
                    continue
                
                if signal:
                    signals.append(signal)
            
            all_signals[asset_class] = signals
        
        return all_signals
    
    def format_signal_display(self, signal: TradingSignal) -> Dict[str, Any]:
        """Format signal for display"""
        # Signal emoji mapping
        signal_emojis = {
            SignalType.STRONG_BUY: "🟢🔺",
            SignalType.BUY: "🟢↗️",
            SignalType.UP: "🟢↑",
            SignalType.DOWN: "🔴↓",
            SignalType.SELL: "🔴↘️",
            SignalType.STRONG_SELL: "🔴🔻"
        }
        
        return {
            "symbol": signal.symbol,
            "asset_class": signal.asset_class.value,
            "current_price": f"{signal.current_price:.6f}",
            "price_change_24h": f"{signal.price_change_24h:+.2f}%",
            "signal": signal.signal.value,
            "signal_emoji": signal_emojis.get(signal.signal, "⚪"),
            "signal_strength": f"{signal.signal_strength:.0f}%",
            "confidence": f"{signal.confidence:.0f}%",
            "entry_price": f"{signal.entry_price:.6f}",
            "target_price": f"{signal.target_price:.6f}",
            "stop_loss": f"{signal.stop_loss:.6f}",
            "timeframe": signal.timeframe,
            "timestamp": signal.timestamp,
            "binary_code": "1" if signal.signal in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP] else "0"
        }

# Global trading system instance
trading_system = TradingSignalsSystem()

async def main():
    """Demo the trading signals system"""
    print("🚀 TRADING SIGNALS SYSTEM DEMO")
    print("=" * 60)
    
    # Get all signals
    all_signals = await trading_system.get_all_signals()
    
    for asset_class, signals in all_signals.items():
        print(f"\n📊 {asset_class} SIGNALS:")
        print("-" * 40)
        
        for signal in signals[:5]:  # Show first 5 signals
            display = trading_system.format_signal_display(signal)
            print(f"{display['signal_emoji']} {signal.symbol:8s} | ${display['current_price']:>12s} | {display['price_change_24h']:>8s} | {display['signal']:>12s} | Binary: {display['binary_code']}")
    
    print(f"\n✅ Total signals generated: {sum(len(signals) for signals in all_signals.values())}")

if __name__ == "__main__":
    asyncio.run(main())