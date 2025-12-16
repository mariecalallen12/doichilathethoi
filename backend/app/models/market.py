"""
Market Data Models
Digital Utopia Platform

Models cho Market Data History, Price Feeds, và Market Analysis
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime, Text, 
    ForeignKey, DECIMAL, Index, func
)
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .base import Base, TimestampMixin


class MarketDataHistory(Base, TimestampMixin):
    """
    Bảng market_data_history - Lịch sử dữ liệu thị trường
    
    Lưu trữ dữ liệu giá lịch sử cho các cặp giao dịch
    """
    __tablename__ = "market_data_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Symbol
    symbol = Column(String(20), nullable=False, index=True)
    base_asset = Column(String(20), nullable=False)
    quote_asset = Column(String(20), nullable=False)
    
    # Price data (OHLCV)
    open_price = Column(DECIMAL(20, 8), nullable=False)
    high_price = Column(DECIMAL(20, 8), nullable=False)
    low_price = Column(DECIMAL(20, 8), nullable=False)
    close_price = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(DECIMAL(20, 8), nullable=False)
    
    # Timeframe
    timeframe = Column(String(10), nullable=False, index=True)  # 1m, 5m, 15m, 1h, 4h, 1d, 1w
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Additional data
    number_of_trades = Column(Integer, default=0)
    taker_buy_volume = Column(DECIMAL(20, 8), nullable=True)
    taker_sell_volume = Column(DECIMAL(20, 8), nullable=True)
    
    # Metadata
    source = Column(String(50), nullable=True)  # binance, coinbase, etc.
    meta_data = Column(JSONB, default={})  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_market_data_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MarketDataHistory(symbol={self.symbol}, timeframe={self.timeframe}, timestamp={self.timestamp})>"


class MarketPrice(Base, TimestampMixin):
    """
    Bảng market_prices - Giá thị trường hiện tại
    
    Cache giá hiện tại cho các cặp giao dịch
    """
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Symbol
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    base_asset = Column(String(20), nullable=False)
    quote_asset = Column(String(20), nullable=False)
    
    # Current price
    price = Column(DECIMAL(20, 8), nullable=False)
    price_change_24h = Column(DECIMAL(20, 8), nullable=True)
    price_change_percent_24h = Column(DECIMAL(10, 4), nullable=True)
    
    # Volume
    volume_24h = Column(DECIMAL(20, 8), nullable=True)
    quote_volume_24h = Column(DECIMAL(20, 8), nullable=True)
    
    # High/Low 24h
    high_24h = Column(DECIMAL(20, 8), nullable=True)
    low_24h = Column(DECIMAL(20, 8), nullable=True)
    
    # Last update
    last_update = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    def __repr__(self):
        return f"<MarketPrice(symbol={self.symbol}, price={self.price})>"


class MarketAnalysis(Base, TimestampMixin):
    """
    Bảng market_analysis - Phân tích thị trường
    
    Lưu trữ kết quả phân tích kỹ thuật và cơ bản
    """
    __tablename__ = "market_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Symbol
    symbol = Column(String(20), nullable=False, index=True)
    
    # Analysis type
    analysis_type = Column(String(50), nullable=False, index=True)  # technical, fundamental, sentiment
    
    # Analysis data
    indicators = Column(JSONB, default={})  # RSI, MACD, Bollinger Bands, etc.
    signals = Column(JSONB, default=[])  # Buy, Sell, Hold signals
    sentiment_score = Column(DECIMAL(5, 2), nullable=True)  # -100 to 100
    
    # Predictions
    price_prediction = Column(JSONB, default={})  # Short-term, medium-term, long-term
    confidence_score = Column(DECIMAL(5, 2), nullable=True)  # 0-100
    
    # Timeframe
    timeframe = Column(String(10), nullable=False)
    analysis_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Source
    source = Column(String(50), nullable=True)  # ai_model, technical_analysis, etc.
    meta_data = Column(JSONB, default={}, name='metadata')  # Renamed to avoid SQLAlchemy conflict, but keep DB column name
    
    def __repr__(self):
        return f"<MarketAnalysis(symbol={self.symbol}, type={self.analysis_type}, date={self.analysis_date})>"


class PriceTick(Base):
    """
    Bảng price_tick - Tick data cho time-series analysis
    
    Lưu trữ từng tick price để hỗ trợ replay và phân tích chi tiết.
    Sử dụng TimescaleDB hypertable để tối ưu performance.
    """
    __tablename__ = "price_tick"
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    # Symbol
    symbol = Column(String(20), nullable=False, index=True)
    
    # Price và volume
    price = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(DECIMAL(20, 8), nullable=False, default=0)
    
    # Timestamp (partition key cho TimescaleDB)
    ts = Column(DateTime(timezone=True), nullable=False, index=True, server_default=sa.func.now())
    
    # Source
    source = Column(String(50), nullable=True, default="simulator")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_price_tick_symbol_ts', 'symbol', 'ts'),
    )
    
    def __repr__(self):
        return f"<PriceTick(symbol={self.symbol}, price={self.price}, ts={self.ts})>"

