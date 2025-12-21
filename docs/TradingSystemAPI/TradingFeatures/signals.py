#!/usr/bin/env python3
"""
Trading Signals Generator
========================

Generates binary trading signals and recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Shared.models import TradingSignal, AssetClass, SignalType, MarketSummary
from Shared.utils import SignalCalculator, data_formatter
from MarketData.providers import MarketDataAggregator

logger = logging.getLogger(__name__)

class TradingSignalsGenerator:
    """Generates trading signals from market data"""
    
    def __init__(self):
        self.market_aggregator = MarketDataAggregator()
        self.signal_calculator = SignalCalculator()
    
    async def generate_signal(self, symbol: str, price_data) -> Optional[TradingSignal]:
        """Generate trading signal for a single symbol"""
        try:
            if not price_data or price_data.change_24h is None:
                return None
            
            # Calculate signal components
            signal_type = self.signal_calculator.generate_signal(
                price_data.price, 
                price_data.change_24h, 
                price_data.volume
            )
            
            signal_strength = self.signal_calculator.calculate_signal_strength(price_data.change_24h)
            confidence = self.signal_calculator.calculate_confidence(
                price_data.price, 
                price_data.change_24h, 
                price_data.volume
            )
            
            entry_price, target_price, stop_loss = self.signal_calculator.calculate_targets(
                price_data.price, 
                price_data.change_24h, 
                signal_type
            )
            
            return TradingSignal(
                symbol=symbol,
                asset_class=price_data.asset_class,
                current_price=price_data.price,
                price_change_24h=price_data.change_24h,
                signal=signal_type,
                signal_strength=signal_strength,
                confidence=confidence,
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                timeframe="1H",
                timestamp=datetime.now().isoformat(),
                volume=price_data.volume,
                market_cap=price_data.market_cap
            )
        
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def generate_all_signals(self) -> Dict[str, TradingSignal]:
        """Generate signals for all available instruments"""
        try:
            # Get all market data
            all_prices = await self.market_aggregator.get_all_prices()
            
            # Generate signals for each instrument
            signals = {}
            tasks = []
            
            for symbol, price_data in all_prices.items():
                task = self.generate_signal(symbol, price_data)
                tasks.append((symbol, task))
            
            # Wait for all signals to be generated
            for symbol, task in tasks:
                signal = await task
                if signal:
                    signals[symbol] = signal
            
            return signals
        
        except Exception as e:
            logger.error(f"Error generating all signals: {e}")
            return {}
    
    async def generate_signals_by_asset_class(self, asset_class: AssetClass) -> Dict[str, TradingSignal]:
        """Generate signals filtered by asset class"""
        try:
            prices = await self.market_aggregator.get_prices_by_asset_class(asset_class)
            signals = {}
            
            for symbol, price_data in prices.items():
                signal = await self.generate_signal(symbol, price_data)
                if signal:
                    signals[symbol] = signal
            
            return signals
        
        except Exception as e:
            logger.error(f"Error generating signals for {asset_class}: {e}")
            return {}
    
    def generate_market_summary(self, signals: Dict[str, TradingSignal]) -> MarketSummary:
        """Generate market summary from signals"""
        if not signals:
            return MarketSummary(
                total_signals=0,
                bullish_signals=0,
                bearish_signals=0,
                market_sentiment="NEUTRAL",
                average_change_24h=0,
                strongest_signal="N/A",
                most_confident="N/A",
                timestamp=datetime.now().isoformat()
            )
        
        # Count bullish vs bearish
        bullish_count = sum(1 for signal in signals.values() 
                          if signal.signal in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP])
        bearish_count = len(signals) - bullish_count
        
        # Calculate average change
        changes = [signal.price_change_24h for signal in signals.values() 
                  if signal.price_change_24h is not None]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Find strongest and most confident signals
        strongest_signal = max(signals.values(), key=lambda s: s.signal_strength)
        most_confident = max(signals.values(), key=lambda s: s.confidence)
        
        # Determine market sentiment
        if bullish_count > bearish_count:
            sentiment = "BULLISH"
        elif bearish_count > bullish_count:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
        
        return MarketSummary(
            total_signals=len(signals),
            bullish_signals=bullish_count,
            bearish_signals=bearish_count,
            market_sentiment=sentiment,
            average_change_24h=avg_change,
            strongest_signal=strongest_signal.symbol,
            most_confident=most_confident.symbol,
            timestamp=datetime.now().isoformat()
        )

class BinarySignalsGenerator:
    """Generates binary trading signals (1=BULLISH, 0=BEARISH)"""
    
    def __init__(self):
        self.signals_generator = TradingSignalsGenerator()
    
    async def generate_binary_signals(self) -> Dict[str, Any]:
        """Generate binary signals for all instruments"""
        try:
            # Generate all signals
            signals = await self.signals_generator.generate_all_signals()
            
            if not signals:
                return {"error": "No signals generated"}
            
            # Create binary arrays
            binary_array = []
            symbols = []
            detailed_signals = []
            
            for symbol, signal in signals.items():
                binary_code = data_formatter.get_binary_code(signal.signal)
                binary_array.append(binary_code)
                symbols.append(symbol)
                
                # Format for display
                detailed_signals.append({
                    "symbol": signal.symbol,
                    "asset_class": signal.asset_class.value,
                    "current_price": data_formatter.format_price(signal.current_price, signal.symbol),
                    "price_change_24h": data_formatter.format_change(signal.price_change_24h),
                    "signal": signal.signal.value,
                    "signal_emoji": data_formatter.get_signal_emoji(signal.signal),
                    "binary_code": binary_code,
                    "signal_strength": f"{signal.signal_strength:.0f}%",
                    "confidence": f"{signal.confidence:.0f}%",
                    "entry_price": data_formatter.format_price(signal.entry_price, signal.symbol),
                    "target_price": data_formatter.format_price(signal.target_price, signal.symbol),
                    "stop_loss": data_formatter.format_price(signal.stop_loss, signal.symbol),
                    "recommendation": self._get_recommendation_text(signal),
                    "timeframe": signal.timeframe
                })
            
            # Generate market summary
            summary = self.signals_generator.generate_market_summary(signals)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_signals": len(signals),
                "binary_array": binary_array,
                "binary_string": "".join(binary_array),
                "symbols": symbols,
                "signals": detailed_signals,
                "summary": {
                    "total_signals": summary.total_signals,
                    "bullish_signals": summary.bullish_signals,
                    "bearish_signals": summary.bearish_signals,
                    "market_sentiment": summary.market_sentiment,
                    "average_change_24h": f"{summary.average_change_24h:+.2f}%",
                    "strongest_signal": summary.strongest_signal,
                    "most_confident": summary.most_confident
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating binary signals: {e}")
            return {"error": str(e)}
    
    def _get_recommendation_text(self, signal: TradingSignal) -> str:
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
    
    async def get_binary_for_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get binary signal for specific symbol"""
        try:
            signals = await self.signals_generator.generate_all_signals()
            
            if symbol.upper() not in signals:
                return None
            
            signal = signals[symbol.upper()]
            
            return {
                "symbol": signal.symbol,
                "binary_code": data_formatter.get_binary_code(signal.signal),
                "signal": signal.signal.value,
                "current_price": data_formatter.format_price(signal.current_price, signal.symbol),
                "price_change_24h": data_formatter.format_change(signal.price_change_24h),
                "recommendation": self._get_recommendation_text(signal),
                "signal_strength": f"{signal.signal_strength:.0f}%",
                "confidence": f"{signal.confidence:.0f}%",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting binary signal for {symbol}: {e}")
            return None

class TradingAnalysis:
    """Provides trading analysis and insights"""
    
    def __init__(self):
        self.signals_generator = TradingSignalsGenerator()
    
    async def analyze_market_trends(self) -> Dict[str, Any]:
        """Analyze current market trends"""
        try:
            signals = await self.signals_generator.generate_all_signals()
            
            if not signals:
                return {"error": "No signals available for analysis"}
            
            # Analyze by asset class
            asset_analysis = {}
            for asset_class in AssetClass:
                class_signals = {symbol: signal for symbol, signal in signals.items() 
                               if signal.asset_class == asset_class}
                
                if class_signals:
                    bullish = sum(1 for s in class_signals.values() 
                                if s.signal in [SignalType.BUY, SignalType.STRONG_BUY, SignalType.UP])
                    bearish = len(class_signals) - bullish
                    
                    changes = [s.price_change_24h for s in class_signals.values() 
                             if s.price_change_24h is not None]
                    avg_change = sum(changes) / len(changes) if changes else 0
                    
                    asset_analysis[asset_class.value] = {
                        "total": len(class_signals),
                        "bullish": bullish,
                        "bearish": bearish,
                        "average_change": avg_change,
                        "sentiment": "BULLISH" if bullish > bearish else "BEARISH"
                    }
            
            # Find top performers
            top_gainers = sorted([signal for signal in signals.values() 
                                if signal.price_change_24h > 0], 
                               key=lambda x: x.price_change_24h, reverse=True)[:5]
            
            top_losers = sorted([signal for signal in signals.values() 
                               if signal.price_change_24h < 0], 
                              key=lambda x: x.price_change_24h)[:5]
            
            # High confidence signals
            high_confidence = [signal for signal in signals.values() 
                             if signal.confidence > 70][:10]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "asset_class_analysis": asset_analysis,
                "top_gainers": [
                    {
                        "symbol": signal.symbol,
                        "change": signal.price_change_24h,
                        "price": signal.current_price,
                        "confidence": signal.confidence
                    } for signal in top_gainers
                ],
                "top_losers": [
                    {
                        "symbol": signal.symbol,
                        "change": signal.price_change_24h,
                        "price": signal.current_price,
                        "confidence": signal.confidence
                    } for signal in top_losers
                ],
                "high_confidence_signals": [
                    {
                        "symbol": signal.symbol,
                        "signal": signal.signal.value,
                        "confidence": signal.confidence,
                        "strength": signal.signal_strength
                    } for signal in high_confidence
                ]
            }
        
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return {"error": str(e)}