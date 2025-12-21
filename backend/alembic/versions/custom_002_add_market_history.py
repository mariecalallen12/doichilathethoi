"""add forex and metal history tables

Revision ID: custom_002_market_history
Revises: custom_001_add_tables
Create Date: 2025-12-21 00:47:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'custom_002_market_history'
down_revision = 'custom_001_add_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create historical data tables for self-calculated 24h change"""
    
    # Forex historical data table
    op.create_table(
        'forex_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('pair', sa.String(20), nullable=False, index=True),
        sa.Column('price', sa.Numeric(20, 8), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('source', sa.String(50), nullable=True),  # Track data source
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Metal historical data table
    op.create_table(
        'metal_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(20), nullable=False, index=True),
        sa.Column('price', sa.Numeric(20, 8), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create composite indexes for faster queries
    op.create_index(
        'idx_forex_history_pair_timestamp',
        'forex_history',
        ['pair', 'timestamp']
    )
    
    op.create_index(
        'idx_metal_history_symbol_timestamp',
        'metal_history',
        ['symbol', 'timestamp']
    )
    
    # Create unique constraint to prevent duplicate entries
    op.create_index(
        'idx_forex_unique_pair_time',
        'forex_history',
        ['pair', 'timestamp'],
        unique=True
    )
    
    op.create_index(
        'idx_metal_unique_symbol_time',
        'metal_history',
        ['symbol', 'timestamp'],
        unique=True
    )


def downgrade() -> None:
    """Drop historical data tables"""
    
    # Drop indexes first
    op.drop_index('idx_metal_unique_symbol_time', table_name='metal_history')
    op.drop_index('idx_forex_unique_pair_time', table_name='forex_history')
    op.drop_index('idx_metal_history_symbol_timestamp', table_name='metal_history')
    op.drop_index('idx_forex_history_pair_timestamp', table_name='forex_history')
    
    # Drop tables
    op.drop_table('metal_history')
    op.drop_table('forex_history')
