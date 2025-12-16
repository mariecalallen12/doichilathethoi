"""
Trading Models - Stub File
These models were removed in migration 20250111_001_remove_trading_tables
This stub file exists to prevent import errors until all references are cleaned up
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

# Stub classes - these should not be used
class TradingOrder(Base):
    __tablename__ = "trading_orders_stub"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    # Stub - table doesn't exist

class PortfolioPosition(Base):
    __tablename__ = "portfolio_positions_stub"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    # Stub - table doesn't exist

