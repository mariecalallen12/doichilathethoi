"""
Trading Signals Service
======================
Backend implementation for trading signals, binary signals, and analysis
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp
from decimal import Decimal

logger = logging.getLogger(__name__)


class TradingSignalsService:
    """Generate trading signals from market data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 30  # seconds
        
    async def generate_all_signals(self) -> Dict[str, Any]:
        """Generate trading signals for all symbols"""
        try:
            # Get market data from market providers
            from app.services.market_providers_simple import BinanceProvider
            
            provider = BinanceProvider()
            symbols = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "AVAX", "LINK"]
            
            signals = {}
            for symbol in symbols:
                price_data = await provider.get_price(symbol)
                if price_data:
                    signal = self._generate_signal(symbol, price_data)
                    signals[symbol] = signal
            
            return signals
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return {}
    
    def _generate_signal(self, symbol: str, price_data: Dict) -> Dict[str, Any]:
        """Generate signal for a single symbol"""
        try:
            current_price = float(price_data.get("price", 0))
            change_24h = float(price_data.get("change_24h", 0))
            volume = price_data.get("volume", "0")
            
            # Determine signal type based on price change
            if change_24h >= 5.0:
                signal = "STRONG_BUY"
                signal_emoji = "🟢🔺"
                signal_strength = "extreme"
            elif change_24h >= 2.0:
                signal = "BUY"
                signal_emoji = "🟢↗️"
                signal_strength = "strong"
            elif change_24h >= 0.5:
                signal = "UP"
                signal_emoji = "🟢↑"
                signal_strength = "moderate"
            elif change_24h <= -5.0:
                signal = "STRONG_SELL"
                signal_emoji = "🔴🔻"
                signal_strength = "extreme"
            elif change_24h <= -2.0:
                signal = "SELL"
                signal_emoji = "🔴↘️"
                signal_strength = "strong"
            elif change_24h <= -0.5:
                signal = "DOWN"
                signal_emoji = "🔴↓"
                signal_strength = "moderate"
            else:
                signal = "NEUTRAL"
                signal_emoji = "⚪️→"
                signal_strength = "weak"
            
            # Calculate confidence based on absolute change
            abs_change = abs(change_24h)
            if abs_change >= 5.0:
                confidence = "95%"
            elif abs_change >= 2.0:
                confidence = "85%"
            elif abs_change >= 1.0:
                confidence = "75%"
            elif abs_change >= 0.5:
                confidence = "65%"
            else:
                confidence = "50%"
            
            # Calculate targets
            entry_price = current_price
            if change_24h > 0:
                target_price = current_price * 1.05  # 5% profit target
                stop_loss = current_price * 0.98  # 2% stop loss
                recommendation = f"Consider buying {symbol} at current levels"
            else:
                target_price = current_price * 0.95
                stop_loss = current_price * 1.02
                recommendation = f"Consider selling or staying out of {symbol}"
            
            return {
                "symbol": symbol,
                "asset_class": "CRYPTO",
                "current_price": f"${current_price:,.2f}",
                "price_change_24h": f"{change_24h:+.2f}%",
                "signal": signal,
                "signal_emoji": signal_emoji,
                "signal_strength": signal_strength,
                "confidence": confidence,
                "entry_price": f"${entry_price:,.2f}",
                "target_price": f"${target_price:,.2f}",
                "stop_loss": f"${stop_loss:,.2f}",
                "recommendation": recommendation,
                "timeframe": "24h",
                "timestamp": datetime.now().isoformat(),
                "volume": volume
            }
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return {}


class BinarySignalsService:
    """Convert trading signals to binary format"""
    
    async def generate_binary_array(self) -> Dict[str, Any]:
        """Generate binary array from trading signals"""
        try:
            signals_service = TradingSignalsService()
            signals = await signals_service.generate_all_signals()
            
            binary_array = []
            symbols = []
            bullish_count = 0
            bearish_count = 0
            
            for symbol, signal_data in signals.items():
                signal_type = signal_data.get("signal", "NEUTRAL")
                
                # Convert to binary: 1 = BULLISH, 0 = BEARISH
                if signal_type in ["STRONG_BUY", "BUY", "UP"]:
                    binary_array.append("1")
                    bullish_count += 1
                else:
                    binary_array.append("0")
                    bearish_count += 1
                
                symbols.append(symbol)
            
            # Determine market sentiment
            if bullish_count > bearish_count:
                sentiment = "BULLISH"
            elif bearish_count > bullish_count:
                sentiment = "BEARISH"
            else:
                sentiment = "NEUTRAL"
            
            return {
                "timestamp": datetime.now().isoformat(),
                "total_signals": len(binary_array),
                "bullish_signals": bullish_count,
                "bearish_signals": bearish_count,
                "market_sentiment": sentiment,
                "binary_array": binary_array,
                "binary_string": "".join(binary_array),
                "symbols": symbols
            }
        except Exception as e:
            logger.error(f"Error generating binary array: {e}")
            return {}
    
    async def get_binary_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Get binary signal for specific symbol"""
        try:
            signals_service = TradingSignalsService()
            signals = await signals_service.generate_all_signals()
            
            signal_data = signals.get(symbol.upper())
            if not signal_data:
                return {}
            
            signal_type = signal_data.get("signal", "NEUTRAL")
            binary_code = "1" if signal_type in ["STRONG_BUY", "BUY", "UP"] else "0"
            
            return {
                "symbol": symbol,
                "binary_code": binary_code,
                "signal": signal_type,
                "current_price": signal_data.get("current_price"),
                "price_change_24h": signal_data.get("price_change_24h"),
                "recommendation": signal_data.get("recommendation"),
                "signal_strength": signal_data.get("signal_strength"),
                "confidence": signal_data.get("confidence"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting binary for {symbol}: {e}")
            return {}


class TradingAnalysisService:
    """Provide market analysis and recommendations"""
    
    async def get_market_analysis(self) -> Dict[str, Any]:
        """Get comprehensive market analysis"""
        try:
            signals_service = TradingSignalsService()
            signals = await signals_service.generate_all_signals()
            
            # Analyze by asset class
            asset_analysis = {
                "CRYPTO": {
                    "total": len(signals),
                    "bullish": 0,
                    "bearish": 0,
                    "neutral": 0
                }
            }
            
            top_gainers = []
            top_losers = []
            high_confidence = []
            
            for symbol, signal_data in signals.items():
                signal_type = signal_data.get("signal", "NEUTRAL")
                confidence = signal_data.get("confidence", "50%")
                change_24h = float(signal_data.get("price_change_24h", "0").replace("%", "").replace("+", ""))
                
                # Count by signal type
                if signal_type in ["STRONG_BUY", "BUY", "UP"]:
                    asset_analysis["CRYPTO"]["bullish"] += 1
                elif signal_type in ["STRONG_SELL", "SELL", "DOWN"]:
                    asset_analysis["CRYPTO"]["bearish"] += 1
                else:
                    asset_analysis["CRYPTO"]["neutral"] += 1
                
                # Track top gainers/losers
                signal_info = {
                    "symbol": symbol,
                    "change_24h": f"{change_24h:+.2f}%",
                    "signal": signal_type,
                    "confidence": confidence
                }
                
                if change_24h > 0:
                    top_gainers.append(signal_info)
                else:
                    top_losers.append(signal_info)
                
                # High confidence signals
                conf_value = int(confidence.replace("%", ""))
                if conf_value >= 85:
                    high_confidence.append(signal_info)
            
            # Sort and limit
            top_gainers = sorted(top_gainers, key=lambda x: float(x["change_24h"].replace("%", "")), reverse=True)[:5]
            top_losers = sorted(top_losers, key=lambda x: float(x["change_24h"].replace("%", "")))[:5]
            
            return {
                "timestamp": datetime.now().isoformat(),
                "asset_class_analysis": asset_analysis,
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "high_confidence_signals": high_confidence
            }
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return {}
    
    async def get_recommendations(self) -> Dict[str, Any]:
        """Get trading recommendations"""
        try:
            signals_service = TradingSignalsService()
            signals = await signals_service.generate_all_signals()
            
            recommendations = {
                "STRONG_BUY": [],
                "BUY": [],
                "HOLD": [],
                "SELL": [],
                "STRONG_SELL": []
            }
            
            for symbol, signal_data in signals.items():
                signal_type = signal_data.get("signal", "NEUTRAL")
                
                rec_item = {
                    "symbol": symbol,
                    "current_price": signal_data.get("current_price"),
                    "target_price": signal_data.get("target_price"),
                    "stop_loss": signal_data.get("stop_loss"),
                    "confidence": signal_data.get("confidence"),
                    "recommendation": signal_data.get("recommendation")
                }
                
                if signal_type == "STRONG_BUY":
                    recommendations["STRONG_BUY"].append(rec_item)
                elif signal_type == "BUY":
                    recommendations["BUY"].append(rec_item)
                elif signal_type in ["UP", "DOWN"]:
                    recommendations["HOLD"].append(rec_item)
                elif signal_type == "SELL":
                    recommendations["SELL"].append(rec_item)
                elif signal_type == "STRONG_SELL":
                    recommendations["STRONG_SELL"].append(rec_item)
            
            summary = {
                "STRONG_BUY": len(recommendations["STRONG_BUY"]),
                "BUY": len(recommendations["BUY"]),
                "HOLD": len(recommendations["HOLD"]),
                "SELL": len(recommendations["SELL"]),
                "STRONG_SELL": len(recommendations["STRONG_SELL"])
            }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "recommendations": recommendations,
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {}
