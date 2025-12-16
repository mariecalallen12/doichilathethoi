"""add_market_data_tables

Revision ID: 003_add_market_data_tables
Revises: 002_seed_initial_data
Create Date: 2025-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_market_data_tables'
down_revision: Union[str, None] = '002_seed_initial_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create market_data_history table
    op.create_table(
        'market_data_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('base_asset', sa.String(length=20), nullable=False),
        sa.Column('quote_asset', sa.String(length=20), nullable=False),
        sa.Column('open_price', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('high_price', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('low_price', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('close_price', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('volume', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('number_of_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('taker_buy_volume', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('taker_sell_volume', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_history_symbol'), 'market_data_history', ['symbol'], unique=False)
    op.create_index(op.f('ix_market_data_history_timeframe'), 'market_data_history', ['timeframe'], unique=False)
    op.create_index(op.f('ix_market_data_history_timestamp'), 'market_data_history', ['timestamp'], unique=False)
    op.create_index('idx_market_data_symbol_timeframe_timestamp', 'market_data_history', ['symbol', 'timeframe', 'timestamp'], unique=False)

    # Create market_prices table
    op.create_table(
        'market_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('base_asset', sa.String(length=20), nullable=False),
        sa.Column('quote_asset', sa.String(length=20), nullable=False),
        sa.Column('price', sa.DECIMAL(20, 8), nullable=False),
        sa.Column('price_change_24h', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('price_change_percent_24h', sa.DECIMAL(10, 4), nullable=True),
        sa.Column('volume_24h', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('quote_volume_24h', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('high_24h', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('low_24h', sa.DECIMAL(20, 8), nullable=True),
        sa.Column('last_update', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )
    op.create_index(op.f('ix_market_prices_symbol'), 'market_prices', ['symbol'], unique=True)
    op.create_index(op.f('ix_market_prices_last_update'), 'market_prices', ['last_update'], unique=False)
    op.create_index(op.f('ix_market_prices_is_active'), 'market_prices', ['is_active'], unique=False)

    # Create market_analysis table
    op.create_table(
        'market_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('indicators', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('signals', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('sentiment_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('price_prediction', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('confidence_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('timeframe', sa.String(length=10), nullable=False),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_analysis_symbol'), 'market_analysis', ['symbol'], unique=False)
    op.create_index(op.f('ix_market_analysis_analysis_type'), 'market_analysis', ['analysis_type'], unique=False)
    op.create_index(op.f('ix_market_analysis_analysis_date'), 'market_analysis', ['analysis_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_market_analysis_analysis_date'), table_name='market_analysis')
    op.drop_index(op.f('ix_market_analysis_analysis_type'), table_name='market_analysis')
    op.drop_index(op.f('ix_market_analysis_symbol'), table_name='market_analysis')
    op.drop_table('market_analysis')
    
    op.drop_index(op.f('ix_market_prices_is_active'), table_name='market_prices')
    op.drop_index(op.f('ix_market_prices_last_update'), table_name='market_prices')
    op.drop_index(op.f('ix_market_prices_symbol'), table_name='market_prices')
    op.drop_table('market_prices')
    
    op.drop_index('idx_market_data_symbol_timeframe_timestamp', table_name='market_data_history')
    op.drop_index(op.f('ix_market_data_history_timestamp'), table_name='market_data_history')
    op.drop_index(op.f('ix_market_data_history_timeframe'), table_name='market_data_history')
    op.drop_index(op.f('ix_market_data_history_symbol'), table_name='market_data_history')
    op.drop_table('market_data_history')

