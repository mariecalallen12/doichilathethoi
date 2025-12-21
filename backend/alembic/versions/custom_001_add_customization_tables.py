"""add customization tables

Revision ID: custom_001_add_tables
Revises: 
Create Date: 2025-12-21 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'custom_001_add_tables'
down_revision = None  # Update this to point to your latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create customization tables"""
    
    # 1. Create custom_rules table
    op.create_table(
        'custom_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('symbol', sa.String(20), nullable=False, default='*', index=True),
        sa.Column('price_adjustment', sa.Numeric(10, 2), nullable=True),
        sa.Column('change_adjustment', sa.Numeric(10, 2), nullable=True),
        sa.Column('force_signal', sa.String(20), nullable=True),
        sa.Column('confidence_boost', sa.Numeric(10, 2), nullable=True),
        sa.Column('custom_volume', sa.Numeric(20, 2), nullable=True),
        sa.Column('custom_market_cap', sa.Numeric(20, 2), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),  # User ID who created the rule
        sa.Column('description', sa.Text(), nullable=True),
    )
    
    # 2. Create customization_sessions table
    op.create_table(
        'customization_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_id', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),  # User ID who created the session
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),  # Optional expiration
    )
    
    # 3. Create session_rule_bindings table (many-to-many relationship)
    op.create_table(
        'session_rule_bindings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['customization_sessions.session_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rule_name'], ['custom_rules.name'], ondelete='CASCADE'),
        sa.UniqueConstraint('session_id', 'rule_name', name='unique_session_rule'),
    )
    
    # 4. Create manual_overrides table (for tracking manual data overrides)
    op.create_table(
        'manual_overrides',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('symbol', sa.String(20), nullable=False, index=True),
        sa.Column('override_type', sa.String(20), nullable=False),  # 'price', 'signal', 'confidence'
        sa.Column('override_value', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, default=True),
    )
    
    # 5. Create customization_audit_log table (for tracking changes)
    op.create_table(
        'customization_audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('action', sa.String(50), nullable=False),  # 'create_rule', 'update_rule', 'delete_rule', etc.
        sa.Column('entity_type', sa.String(50), nullable=False),  # 'rule', 'session', 'binding', 'override'
        sa.Column('entity_id', sa.String(100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('changes', postgresql.JSONB(), nullable=True),  # Store before/after values
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
    )
    
    # Create indexes for better query performance
    op.create_index('idx_custom_rules_enabled', 'custom_rules', ['enabled'])
    op.create_index('idx_customization_sessions_enabled', 'customization_sessions', ['enabled'])
    op.create_index('idx_manual_overrides_active', 'manual_overrides', ['active', 'symbol'])
    op.create_index('idx_audit_log_created_at', 'customization_audit_log', ['created_at'])
    op.create_index('idx_audit_log_entity', 'customization_audit_log', ['entity_type', 'entity_id'])


def downgrade() -> None:
    """Drop customization tables"""
    
    # Drop indexes first
    op.drop_index('idx_audit_log_entity', table_name='customization_audit_log')
    op.drop_index('idx_audit_log_created_at', table_name='customization_audit_log')
    op.drop_index('idx_manual_overrides_active', table_name='manual_overrides')
    op.drop_index('idx_customization_sessions_enabled', table_name='customization_sessions')
    op.drop_index('idx_custom_rules_enabled', table_name='custom_rules')
    
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('customization_audit_log')
    op.drop_table('manual_overrides')
    op.drop_table('session_rule_bindings')
    op.drop_table('customization_sessions')
    op.drop_table('custom_rules')
