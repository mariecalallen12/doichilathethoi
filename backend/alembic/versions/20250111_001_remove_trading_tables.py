"""remove_trading_tables

Revision ID: 20250111_001_remove_trading_tables
Revises: 20250110_001_add_custom_id_to_user_profiles
Create Date: 2025-01-11 12:00:00.000000

Migration để xóa toàn bộ trading tables và related components
Xóa: trading_orders, portfolio_positions, iceberg_orders, oco_orders, trailing_stop_orders
Xóa foreign key từ trading_adjustments đến portfolio_positions
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250111_001_remove_trading_tables'
down_revision: Union[str, None] = '20250110_001_add_custom_id_to_user_profiles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Xóa toàn bộ trading tables và related foreign keys
    
    Thứ tự xóa:
    1. Xóa foreign key constraints từ các bảng khác
    2. Xóa các bảng phụ thuộc (iceberg_orders, oco_orders, trailing_stop_orders)
    3. Xóa các bảng chính (portfolio_positions, trading_orders)
    """
    
    # 1. Xóa foreign key constraint từ trading_adjustments đến portfolio_positions
    # Kiểm tra xem constraint có tồn tại không
    try:
        op.drop_constraint(
            'trading_adjustments_position_id_fkey',
            'trading_adjustments',
            type_='foreignkey'
        )
    except Exception:
        # Constraint có thể không tồn tại hoặc có tên khác
        pass
    
    # 2. Xóa các bảng phụ thuộc trước (có foreign key đến trading_orders)
    
    # Xóa trailing_stop_orders
    try:
        op.drop_index('ix_trailing_stop_orders_id', table_name='trailing_stop_orders', if_exists=True)
        op.drop_index('ix_trailing_stop_orders_status', table_name='trailing_stop_orders', if_exists=True)
        op.drop_index('ix_trailing_stop_orders_symbol', table_name='trailing_stop_orders', if_exists=True)
        op.drop_table('trailing_stop_orders')
    except Exception:
        pass
    
    # Xóa oco_orders
    try:
        op.drop_index('ix_oco_orders_id', table_name='oco_orders', if_exists=True)
        op.drop_index('ix_oco_orders_status', table_name='oco_orders', if_exists=True)
        op.drop_index('ix_oco_orders_symbol', table_name='oco_orders', if_exists=True)
        op.drop_table('oco_orders')
    except Exception:
        pass
    
    # Xóa iceberg_orders
    try:
        op.drop_index('ix_iceberg_orders_id', table_name='iceberg_orders', if_exists=True)
        op.drop_index('ix_iceberg_orders_status', table_name='iceberg_orders', if_exists=True)
        op.drop_index('ix_iceberg_orders_symbol', table_name='iceberg_orders', if_exists=True)
        op.drop_table('iceberg_orders')
    except Exception:
        pass
    
    # 3. Xóa các bảng chính
    
    # Xóa portfolio_positions
    try:
        op.drop_index('ix_portfolio_positions_id', table_name='portfolio_positions', if_exists=True)
        op.drop_index('ix_portfolio_positions_is_closed', table_name='portfolio_positions', if_exists=True)
        op.drop_index('ix_portfolio_positions_symbol', table_name='portfolio_positions', if_exists=True)
        op.drop_index('ix_portfolio_positions_user_id', table_name='portfolio_positions', if_exists=True)
        op.drop_table('portfolio_positions')
    except Exception:
        pass
    
    # Xóa trading_orders
    try:
        op.drop_index('ix_trading_orders_id', table_name='trading_orders', if_exists=True)
        op.drop_index('ix_trading_orders_status', table_name='trading_orders', if_exists=True)
        op.drop_index('ix_trading_orders_symbol', table_name='trading_orders', if_exists=True)
        op.drop_index('ix_trading_orders_user_id', table_name='trading_orders', if_exists=True)
        op.drop_table('trading_orders')
    except Exception:
        pass


def downgrade() -> None:
    """
    Khôi phục lại trading tables (không khuyến khích sử dụng)
    Chỉ để rollback trong trường hợp cần thiết
    """
    # Note: Downgrade này chỉ tạo lại cấu trúc bảng cơ bản
    # Dữ liệu sẽ bị mất
    
    # Tạo lại trading_orders
    op.create_table(
        'trading_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_type', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('stop_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('time_in_force', sa.String(length=10), nullable=True, server_default='GTC'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('filled_quantity', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('filled_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('remaining_quantity', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('average_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('commission', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('filled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trading_orders_user_id', 'trading_orders', ['user_id'], unique=False)
    op.create_index('ix_trading_orders_symbol', 'trading_orders', ['symbol'], unique=False)
    op.create_index('ix_trading_orders_status', 'trading_orders', ['status'], unique=False)
    op.create_index('ix_trading_orders_id', 'trading_orders', ['id'], unique=False)
    
    # Tạo lại portfolio_positions
    op.create_table(
        'portfolio_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('average_price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('market_value', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('unrealized_pnl', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('realized_pnl', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('position_type', sa.String(length=20), nullable=True, server_default='long'),
        sa.Column('entry_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('entry_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('leverage', sa.Numeric(precision=10, scale=2), nullable=True, server_default='1'),
        sa.Column('margin_used', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('is_closed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('closed_reason', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_portfolio_positions_user_id', 'portfolio_positions', ['user_id'], unique=False)
    op.create_index('ix_portfolio_positions_symbol', 'portfolio_positions', ['symbol'], unique=False)
    op.create_index('ix_portfolio_positions_is_closed', 'portfolio_positions', ['is_closed'], unique=False)
    op.create_index('ix_portfolio_positions_id', 'portfolio_positions', ['id'], unique=False)
    
    # Tạo lại iceberg_orders
    op.create_table(
        'iceberg_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_order_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('total_quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('slice_quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('remaining_quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('slices_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_filled', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('average_fill_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_order_id'], ['trading_orders.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_iceberg_orders_symbol', 'iceberg_orders', ['symbol'], unique=False)
    op.create_index('ix_iceberg_orders_status', 'iceberg_orders', ['status'], unique=False)
    op.create_index('ix_iceberg_orders_id', 'iceberg_orders', ['id'], unique=False)
    
    # Tạo lại oco_orders
    op.create_table(
        'oco_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('primary_order_id', sa.Integer(), nullable=True),
        sa.Column('secondary_order_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('primary_side', sa.String(length=10), nullable=True),
        sa.Column('secondary_side', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('triggered_order_id', sa.Integer(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['primary_order_id'], ['trading_orders.id']),
        sa.ForeignKeyConstraint(['secondary_order_id'], ['trading_orders.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_oco_orders_symbol', 'oco_orders', ['symbol'], unique=False)
    op.create_index('ix_oco_orders_status', 'oco_orders', ['status'], unique=False)
    op.create_index('ix_oco_orders_id', 'oco_orders', ['id'], unique=False)
    
    # Tạo lại trailing_stop_orders
    op.create_table(
        'trailing_stop_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('parent_order_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('stop_type', sa.String(length=20), nullable=True),
        sa.Column('stop_value', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('trailing_distance', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('current_stop_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('activation_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('highest_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('lowest_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_order_id'], ['trading_orders.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_trailing_stop_orders_symbol', 'trailing_stop_orders', ['symbol'], unique=False)
    op.create_index('ix_trailing_stop_orders_status', 'trailing_stop_orders', ['status'], unique=False)
    op.create_index('ix_trailing_stop_orders_id', 'trailing_stop_orders', ['id'], unique=False)
    
    # Khôi phục foreign key từ trading_adjustments đến portfolio_positions
    op.create_foreign_key(
        'trading_adjustments_position_id_fkey',
        'trading_adjustments',
        'portfolio_positions',
        ['position_id'],
        ['id'],
        ondelete='SET NULL'
    )

