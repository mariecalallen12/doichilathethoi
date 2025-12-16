"""add_diagnostic_reports_table

Revision ID: 007_diagnostic_reports
Revises: 006_two_factor
Create Date: 2025-01-01 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "007_diagnostic_reports"
down_revision: Union[str, None] = "006_two_factor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create trading_diagnostic_reports table
    op.create_table(
        'trading_diagnostic_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        
        # Status fields (JSONB)
        sa.Column('auth_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('api_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ws_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('component_status', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Errors and recommendations (JSONB)
        sa.Column('errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('warnings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Raw diagnostic data (JSONB)
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Overall health status
        sa.Column('overall_health', sa.String(length=20), nullable=True),
        
        # Metadata
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('collection_duration_ms', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Foreign key constraint
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        
        # Primary key
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index(op.f('ix_trading_diagnostic_reports_id'), 'trading_diagnostic_reports', ['id'], unique=False)
    op.create_index(op.f('ix_trading_diagnostic_reports_user_id'), 'trading_diagnostic_reports', ['user_id'], unique=False)
    op.create_index(op.f('ix_trading_diagnostic_reports_overall_health'), 'trading_diagnostic_reports', ['overall_health'], unique=False)
    op.create_index(op.f('ix_trading_diagnostic_reports_created_at'), 'trading_diagnostic_reports', ['created_at'], unique=False)
    
    # Composite index for common queries (user_id + created_at for user reports, overall_health + created_at for health filtering)
    op.create_index('ix_trading_diagnostic_reports_user_created', 'trading_diagnostic_reports', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_trading_diagnostic_reports_health_created', 'trading_diagnostic_reports', ['overall_health', 'created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_trading_diagnostic_reports_health_created', table_name='trading_diagnostic_reports')
    op.drop_index('ix_trading_diagnostic_reports_user_created', table_name='trading_diagnostic_reports')
    op.drop_index(op.f('ix_trading_diagnostic_reports_created_at'), table_name='trading_diagnostic_reports')
    op.drop_index(op.f('ix_trading_diagnostic_reports_overall_health'), table_name='trading_diagnostic_reports')
    op.drop_index(op.f('ix_trading_diagnostic_reports_user_id'), table_name='trading_diagnostic_reports')
    op.drop_index(op.f('ix_trading_diagnostic_reports_id'), table_name='trading_diagnostic_reports')
    
    # Drop table
    op.drop_table('trading_diagnostic_reports')

