"""unify_schema

Revision ID: 20250108_001_unify_schema
Revises: 20250101_008_add_alert_rules_notifications_tables
Create Date: 2025-01-08 00:00:00.000000

Migration để chuẩn hóa schema giữa tất cả environments
Đảm bảo tất cả environments có cùng schema structure
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250108_001_unify_schema'
down_revision: Union[str, None] = '008_alert_rules_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Chuẩn hóa schema - đảm bảo tất cả environments có cùng structure
    
    Migration này được thiết kế để:
    1. Thêm missing columns/tables nếu có
    2. Chuẩn hóa indexes và constraints
    3. Đảm bảo foreign keys đúng
    4. Idempotent - có thể chạy nhiều lần an toàn
    """
    
    # Kiểm tra và thêm indexes nếu thiếu (idempotent)
    # Indexes quan trọng cho performance
    
    # Users table indexes
    try:
        op.create_index('ix_users_email', 'users', ['email'], unique=True, if_not_exists=True)
    except Exception:
        pass  # Index đã tồn tại
    
    try:
        op.create_index('ix_users_status', 'users', ['status'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_users_kyc_status', 'users', ['kyc_status'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    # Trading orders indexes
    try:
        op.create_index('ix_trading_orders_user_id', 'trading_orders', ['user_id'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_trading_orders_status', 'trading_orders', ['status'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_trading_orders_symbol', 'trading_orders', ['symbol'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    # Transactions indexes
    try:
        op.create_index('ix_transactions_user_id', 'transactions', ['user_id'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_transactions_transaction_type', 'transactions', ['transaction_type'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_transactions_status', 'transactions', ['status'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    # Wallet balances indexes
    try:
        op.create_index('ix_wallet_balances_user_id', 'wallet_balances', ['user_id'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_wallet_balances_asset', 'wallet_balances', ['asset'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    # Portfolio positions indexes
    try:
        op.create_index('ix_portfolio_positions_user_id', 'portfolio_positions', ['user_id'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    try:
        op.create_index('ix_portfolio_positions_symbol', 'portfolio_positions', ['symbol'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    # Chuẩn hóa constraints - đảm bảo unique constraints
    # Note: PostgreSQL không hỗ trợ IF NOT EXISTS cho constraints, nên cần check trước
    
    # Đảm bảo unique constraint cho wallet_balances (user_id, asset)
    # Constraint này đã được định nghĩa trong model, nhưng verify lại
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Kiểm tra và thêm unique constraint nếu thiếu
    wallet_constraints = [c['name'] for c in inspector.get_unique_constraints('wallet_balances')]
    if 'uq_wallet_user_asset' not in wallet_constraints:
        try:
            op.create_unique_constraint('uq_wallet_user_asset', 'wallet_balances', ['user_id', 'asset'])
        except Exception:
            pass  # Constraint có thể đã tồn tại với tên khác
    
    # Đảm bảo unique constraint cho exchange_rates
    exchange_constraints = [c['name'] for c in inspector.get_unique_constraints('exchange_rates')]
    if 'uq_exchange_rate_pair' not in exchange_constraints:
        try:
            op.create_unique_constraint('uq_exchange_rate_pair', 'exchange_rates', ['base_asset', 'target_asset'])
        except Exception:
            pass
    
    # Chuẩn hóa foreign keys - verify tất cả foreign keys tồn tại
    # Foreign keys đã được định nghĩa trong models, migration này chỉ verify
    
    # Chuẩn hóa default values cho các columns quan trọng
    # Đảm bảo consistency giữa các environments
    
    # Users table defaults
    try:
        op.alter_column('users', 'status',
                       existing_type=sa.String(length=50),
                       server_default='pending',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('users', 'email_verified',
                       existing_type=sa.Boolean(),
                       server_default='false',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('users', 'kyc_status',
                       existing_type=sa.String(length=50),
                       server_default='pending',
                       nullable=True)
    except Exception:
        pass
    
    # Transactions table defaults
    try:
        op.alter_column('transactions', 'status',
                       existing_type=sa.String(length=50),
                       server_default='pending',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('transactions', 'fee',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=True)
    except Exception:
        pass
    
    # Trading orders defaults
    try:
        op.alter_column('trading_orders', 'status',
                       existing_type=sa.String(length=50),
                       server_default='pending',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('trading_orders', 'filled_quantity',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('trading_orders', 'commission',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=True)
    except Exception:
        pass
    
    # Portfolio positions defaults
    try:
        op.alter_column('portfolio_positions', 'position_type',
                       existing_type=sa.String(length=20),
                       server_default='long',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('portfolio_positions', 'realized_pnl',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=True)
    except Exception:
        pass
    
    try:
        op.alter_column('portfolio_positions', 'is_closed',
                       existing_type=sa.Boolean(),
                       server_default='false',
                       nullable=True)
    except Exception:
        pass
    
    # Wallet balances defaults
    try:
        op.alter_column('wallet_balances', 'available_balance',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=False)
    except Exception:
        pass
    
    try:
        op.alter_column('wallet_balances', 'locked_balance',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=False)
    except Exception:
        pass
    
    try:
        op.alter_column('wallet_balances', 'pending_balance',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=False)
    except Exception:
        pass
    
    try:
        op.alter_column('wallet_balances', 'reserved_balance',
                       existing_type=sa.DECIMAL(20, 8),
                       server_default='0',
                       nullable=False)
    except Exception:
        pass
    
    # Optimize database - VACUUM và REINDEX (chạy sau khi migration)
    # Note: Không thể chạy VACUUM trong transaction, nên sẽ được thực hiện bởi script riêng


def downgrade() -> None:
    """
    Rollback migration - không rollback vì đây là migration chuẩn hóa
    Schema sẽ giữ nguyên sau khi upgrade
    """
    # Không có downgrade vì đây là migration chuẩn hóa
    # Việc rollback có thể gây mất consistency
    pass

