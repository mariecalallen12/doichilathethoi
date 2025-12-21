"""
Customization Models
=====================

SQLAlchemy models for customization functionality
"""

from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class CustomRule(Base):
    """Customization rule model"""
    
    __tablename__ = "custom_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, default="*", index=True)
    price_adjustment = Column(Numeric(10, 2), nullable=True)
    change_adjustment = Column(Numeric(10, 2), nullable=True)
    force_signal = Column(String(20), nullable=True)
    confidence_boost = Column(Numeric(10, 2), nullable=True)
    custom_volume = Column(Numeric(20, 2), nullable=True)
    custom_market_cap = Column(Numeric(20, 2), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)  # Foreign key to users table
    description = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "symbol": self.symbol,
            "price_adjustment": float(self.price_adjustment) if self.price_adjustment else None,
            "change_adjustment": float(self.change_adjustment) if self.change_adjustment else None,
            "force_signal": self.force_signal,
            "confidence_boost": float(self.confidence_boost) if self.confidence_boost else None,
            "custom_volume": float(self.custom_volume) if self.custom_volume else None,
            "custom_market_cap": float(self.custom_market_cap) if self.custom_market_cap else None,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "description": self.description
        }


class CustomizationSession(Base):
    """Customization session model"""
    
    __tablename__ = "customization_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    bindings = relationship("SessionRuleBinding", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "rule_names": [b.rule_name for b in self.bindings] if self.bindings else []
        }


class SessionRuleBinding(Base):
    """Session-Rule binding model (many-to-many)"""
    
    __tablename__ = "session_rule_bindings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), ForeignKey("customization_sessions.session_id", ondelete="CASCADE"), nullable=False)
    rule_name = Column(String(100), ForeignKey("custom_rules.name", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("CustomizationSession", back_populates="bindings")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "rule_name": self.rule_name,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ManualOverride(Base):
    """Manual data override model"""
    
    __tablename__ = "manual_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    override_type = Column(String(20), nullable=False)  # 'price', 'signal', 'confidence'
    override_value = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "symbol": self.symbol,
            "override_type": self.override_type,
            "override_value": self.override_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "active": self.active
        }


class CustomizationAuditLog(Base):
    """Audit log for customization changes"""
    
    __tablename__ = "customization_audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(50), nullable=False)  # 'create_rule', 'update_rule', 'delete_rule', etc.
    entity_type = Column(String(50), nullable=False)  # 'rule', 'session', 'binding', 'override'
    entity_id = Column(String(100), nullable=False)
    user_id = Column(Integer, nullable=True)
    changes = Column(JSONB, nullable=True)  # Store before/after values as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "user_id": self.user_id,
            "changes": self.changes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ip_address": self.ip_address
        }


class ForexHistory(Base):
    """Historical forex data for 24h change calculation"""
    
    __tablename__ = "forex_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pair = Column(String(20), nullable=False, index=True)
    price = Column(Numeric(20, 8), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "pair": self.pair,
            "price": float(self.price),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source
        }


class MetalHistory(Base):
    """Historical metal data for 24h change calculation"""
    
    __tablename__ = "metal_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Numeric(20, 8), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": float(self.price),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source
        }
