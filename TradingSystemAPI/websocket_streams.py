#!/usr/bin/env python3
"""
WebSocket Streaming Endpoints for TradingSystemAPI
==================================================

Real-time data streaming via WebSocket
- Market prices stream (continuous updates)
- Trading signals stream (on change)
- Binary sentiment stream (real-time)
"""

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List, Set
import asyncio
import json
import logging
from datetime import datetime

# Import from existing modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Shared.utils import data_formatter
from MarketData.providers import MarketDataAggregator
from TradingFeatures.signals import TradingSignalsGenerator, BinarySignalsGenerator

logger = logging.getLogger(__name__)

# Create router
ws_router = APIRouter()

# Connection manager
class StreamManager:
    def __init__(self):
        # Active WebSocket connections
        self.market_connections: Set[WebSocket] = set()
        self.signals_connections: Set[WebSocket] = set()
        self.binary_connections: Set[WebSocket] = set()
        
        # Background tasks
        self.market_task = None
        self.signals_task = None
        self.binary_task = None
        
        # Data generators
        self.market_aggregator = MarketDataAggregator()
        self.signals_generator = TradingSignalsGenerator()
        self.binary_generator = BinarySignalsGenerator()
        
        # Cache for detecting changes
        self.last_market_data = {}
        self.last_signals = {}
        self.last_binary = None
    
    async def connect_market(self, websocket: WebSocket):
        """Connect to market data stream"""
        await websocket.accept()
        self.market_connections.add(websocket)
        logger.info(f"Market stream connected. Total: {len(self.market_connections)}")
        
        # Start background task if not running
        if not self.market_task or self.market_task.done():
            self.market_task = asyncio.create_task(self.stream_market_data())
    
    async def connect_signals(self, websocket: WebSocket):
        """Connect to signals stream"""
        await websocket.accept()
        self.signals_connections.add(websocket)
        logger.info(f"Signals stream connected. Total: {len(self.signals_connections)}")
        
        # Start background task if not running
        if not self.signals_task or self.signals_task.done():
            self.signals_task = asyncio.create_task(self.stream_signals())
    
    async def connect_binary(self, websocket: WebSocket):
        """Connect to binary stream"""
        await websocket.accept()
        self.binary_connections.add(websocket)
        logger.info(f"Binary stream connected. Total: {len(self.binary_connections)}")
        
        # Start background task if not running
        if not self.binary_task or self.binary_task.done():
            self.binary_task = asyncio.create_task(self.stream_binary())
    
    def disconnect(self, websocket: WebSocket, stream_type: str):
        """Disconnect from stream"""
        if stream_type == "market":
            self.market_connections.discard(websocket)
            logger.info(f"Market stream disconnected. Remaining: {len(self.market_connections)}")
        elif stream_type == "signals":
            self.signals_connections.discard(websocket)
            logger.info(f"Signals stream disconnected. Remaining: {len(self.signals_connections)}")
        elif stream_type == "binary":
            self.binary_connections.discard(websocket)
            logger.info(f"Binary stream disconnected. Remaining: {len(self.binary_connections)}")
    
    async def stream_market_data(self):
        """Background task: Stream market prices continuously"""
        while self.market_connections:
            try:
                # Fetch latest market data
                prices_dict = await self.market_aggregator.get_all_prices()
                
                # Check for changes and broadcast
                for symbol, price_data in prices_dict.items():
                    current_price = price_data.price
                    last_price = self.last_market_data.get(symbol, {}).get('price')
                    
                    # Always send or send if changed
                    if True:  # Send all updates (can change to: current_price != last_price)
                        message = {
                            "type": "market_update",
                            "symbol": symbol,
                            "data": {
                                "price": data_formatter.format_price(price_data.price, symbol),
                                "change_24h": data_formatter.format_change(price_data.change_24h or 0),
                                "volume": f"{price_data.volume:,.0f}" if price_data.volume else None,
                                "high": data_formatter.format_price(price_data.high_24h, symbol) if price_data.high_24h else None,
                                "low": data_formatter.format_price(price_data.low_24h, symbol) if price_data.low_24h else None,
                                "timestamp": datetime.now().isoformat(),
                                "source": price_data.source
                            }
                        }
                        
                        await self.broadcast(message, self.market_connections)
                        
                        # Update cache
                        self.last_market_data[symbol] = {
                            'price': current_price,
                            'timestamp': datetime.now()
                        }
                
                # Wait before next update (5 seconds)
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in market stream: {e}")
                await asyncio.sleep(5)
    
    async def stream_signals(self):
        """Background task: Stream trading signals"""
        while self.signals_connections:
            try:
                # Generate signals
                signals_dict = await self.signals_generator.generate_all_signals()
                
                # Broadcast all signals
                for symbol, signal in signals_dict.items():
                    message = {
                        "type": "signal_update",
                        "symbol": symbol,
                        "data": {
                            "signal": signal.signal.value,
                            "signal_strength": data_formatter.get_signal_emoji(signal.signal),
                            "confidence": data_formatter.format_percentage(signal.confidence),
                            "entry_price": data_formatter.format_price(signal.current_price, symbol),
                            "target_price": data_formatter.format_price(signal.target_price, symbol),
                            "stop_loss": data_formatter.format_price(signal.stop_loss, symbol),
                            "recommendation": signal.recommendation,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    await self.broadcast(message, self.signals_connections)
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in signals stream: {e}")
                await asyncio.sleep(30)
    
    async def stream_binary(self):
        """Background task: Stream binary sentiment"""
        while self.binary_connections:
            try:
                # Generate binary array
                binary_data = await self.binary_generator.generate_binary_array()
                
                message = {
                    "type": "binary_update",
                    "data": {
                        "binary_string": binary_data.binary_string,
                        "binary_array": binary_data.binary_array,
                        "symbols": binary_data.symbols,
                        "bullish_signals": binary_data.bullish_signals,
                        "bearish_signals": binary_data.bearish_signals,
                        "total_signals": binary_data.total_signals,
                        "market_sentiment": binary_data.market_sentiment,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                await self.broadcast(message, self.binary_connections)
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in binary stream: {e}")
                await asyncio.sleep(30)
    
    async def broadcast(self, message: dict, connections: Set[WebSocket]):
        """Broadcast message to all connections in set"""
        disconnected = set()
        message_json = json.dumps(message)
        
        for connection in connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.add(connection)
        
        # Remove disconnected
        connections -= disconnected

# Global manager
stream_manager = StreamManager()

# WebSocket endpoints
@ws_router.websocket("/market/stream")
async def market_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market prices
    
    Streams continuous price updates for all instruments
    Update frequency: ~5 seconds
    
    Message format:
    {
        "type": "market_update",
        "symbol": "BTC",
        "data": {
            "price": "$88,169.00",
            "change_24h": "+0.05%",
            "volume": "5,284",
            ...
        }
    }
    """
    await stream_manager.connect_market(websocket)
    try:
        while True:
            # Keep connection alive, wait for client messages
            data = await websocket.receive_text()
            # Echo back if needed
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket, "market")
    except Exception as e:
        logger.error(f"Market stream error: {e}")
        stream_manager.disconnect(websocket, "market")

@ws_router.websocket("/trading/signals/stream")
async def signals_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time trading signals
    
    Streams signal updates
    Update frequency: ~30 seconds
    
    Message format:
    {
        "type": "signal_update",
        "symbol": "BTC",
        "data": {
            "signal": "STRONG_BUY",
            "confidence": "95%",
            ...
        }
    }
    """
    await stream_manager.connect_signals(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket, "signals")
    except Exception as e:
        logger.error(f"Signals stream error: {e}")
        stream_manager.disconnect(websocket, "signals")

@ws_router.websocket("/trading/binary/stream")
async def binary_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time binary sentiment
    
    Streams binary array and market sentiment
    Update frequency: ~30 seconds
    
    Message format:
    {
        "type": "binary_update",
        "data": {
            "binary_string": "101100...",
            "market_sentiment": "BULLISH",
            ...
        }
    }
    """
    await stream_manager.connect_binary(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        stream_manager.disconnect(websocket, "binary")
    except Exception as e:
        logger.error(f"Binary stream error: {e}")
        stream_manager.disconnect(websocket, "binary")
