"""create_all_tables

Revision ID: 001_create_all_tables
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_create_all_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system_role', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_name'), 'permissions', ['name'], unique=True)
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_permissions_id'), 'role_permissions', ['id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('phone_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('kyc_status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('customer_payment_id', sa.String(length=50), nullable=True),
        sa.Column('referral_code', sa.String(length=50), nullable=True),
        sa.Column('referred_by', sa.Integer(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('account_locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('terms_accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('privacy_accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['referred_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_status'), 'users', ['status'], unique=False)
    op.create_index(op.f('ix_users_customer_payment_id'), 'users', ['customer_payment_id'], unique=True)
    op.create_index(op.f('ix_users_referral_code'), 'users', ['referral_code'], unique=False)
    op.create_index(op.f('ix_users_kyc_status'), 'users', ['kyc_status'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('id_type', sa.String(length=50), nullable=True),
        sa.Column('id_number', sa.String(length=100), nullable=True),
        sa.Column('id_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('id_front_url', sa.String(length=500), nullable=True),
        sa.Column('id_back_url', sa.String(length=500), nullable=True),
        sa.Column('selfie_url', sa.String(length=500), nullable=True),
        sa.Column('bank_account_name', sa.String(length=255), nullable=True),
        sa.Column('bank_account_number', sa.String(length=50), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('bank_branch', sa.String(length=100), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=255), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{"email": true, "sms": false, "push": true}'),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_phone'), 'user_profiles', ['phone'], unique=False)
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('device_id', sa.String(length=255), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_revoked'), 'refresh_tokens', ['revoked'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)

    # Create wallet_balances table
    op.create_table(
        'wallet_balances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(length=20), nullable=False),
        sa.Column('available_balance', sa.Numeric(precision=20, scale=8), nullable=False, server_default='0'),
        sa.Column('locked_balance', sa.Numeric(precision=20, scale=8), nullable=False, server_default='0'),
        sa.Column('pending_balance', sa.Numeric(precision=20, scale=8), nullable=False, server_default='0'),
        sa.Column('reserved_balance', sa.Numeric(precision=20, scale=8), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'asset', name='uq_wallet_user_asset')
    )
    op.create_index(op.f('ix_wallet_balances_user_id'), 'wallet_balances', ['user_id'], unique=False)
    op.create_index(op.f('ix_wallet_balances_asset'), 'wallet_balances', ['asset'], unique=False)
    op.create_index(op.f('ix_wallet_balances_id'), 'wallet_balances', ['id'], unique=False)

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('asset', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('fee', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('net_amount', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('balance_before', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('balance_after', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('bank_account', sa.String(length=50), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('transaction_hash', sa.String(length=255), nullable=True),
        sa.Column('from_address', sa.String(length=255), nullable=True),
        sa.Column('to_address', sa.String(length=255), nullable=True),
        sa.Column('network', sa.String(length=50), nullable=True),
        sa.Column('confirmations', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_type'), 'transactions', ['transaction_type'], unique=False)
    op.create_index(op.f('ix_transactions_status'), 'transactions', ['status'], unique=False)
    op.create_index(op.f('ix_transactions_asset'), 'transactions', ['asset'], unique=False)
    op.create_index(op.f('ix_transactions_reference_id'), 'transactions', ['reference_id'], unique=False)
    op.create_index(op.f('ix_transactions_external_id'), 'transactions', ['external_id'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_hash'), 'transactions', ['transaction_hash'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)

    # Create exchange_rates table
    op.create_table(
        'exchange_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('base_asset', sa.String(length=20), nullable=False),
        sa.Column('target_asset', sa.String(length=20), nullable=False),
        sa.Column('rate', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('inverse_rate', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('base_asset', 'target_asset', name='uq_exchange_rate_pair')
    )
    op.create_index(op.f('ix_exchange_rates_base_asset'), 'exchange_rates', ['base_asset'], unique=False)
    op.create_index(op.f('ix_exchange_rates_target_asset'), 'exchange_rates', ['target_asset'], unique=False)
    op.create_index(op.f('ix_exchange_rates_id'), 'exchange_rates', ['id'], unique=False)

    # Create trading_orders table
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
    op.create_index(op.f('ix_trading_orders_user_id'), 'trading_orders', ['user_id'], unique=False)
    op.create_index(op.f('ix_trading_orders_symbol'), 'trading_orders', ['symbol'], unique=False)
    op.create_index(op.f('ix_trading_orders_status'), 'trading_orders', ['status'], unique=False)
    op.create_index(op.f('ix_trading_orders_id'), 'trading_orders', ['id'], unique=False)

    # Create portfolio_positions table
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
    op.create_index(op.f('ix_portfolio_positions_user_id'), 'portfolio_positions', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_positions_symbol'), 'portfolio_positions', ['symbol'], unique=False)
    op.create_index(op.f('ix_portfolio_positions_is_closed'), 'portfolio_positions', ['is_closed'], unique=False)
    op.create_index(op.f('ix_portfolio_positions_id'), 'portfolio_positions', ['id'], unique=False)

    # Create iceberg_orders table
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
        sa.ForeignKeyConstraint(['parent_order_id'], ['trading_orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_iceberg_orders_symbol'), 'iceberg_orders', ['symbol'], unique=False)
    op.create_index(op.f('ix_iceberg_orders_status'), 'iceberg_orders', ['status'], unique=False)
    op.create_index(op.f('ix_iceberg_orders_id'), 'iceberg_orders', ['id'], unique=False)

    # Create oco_orders table
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
        sa.ForeignKeyConstraint(['primary_order_id'], ['trading_orders.id'], ),
        sa.ForeignKeyConstraint(['secondary_order_id'], ['trading_orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oco_orders_symbol'), 'oco_orders', ['symbol'], unique=False)
    op.create_index(op.f('ix_oco_orders_status'), 'oco_orders', ['status'], unique=False)
    op.create_index(op.f('ix_oco_orders_id'), 'oco_orders', ['id'], unique=False)

    # Create trailing_stop_orders table
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
        sa.ForeignKeyConstraint(['parent_order_id'], ['trading_orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trailing_stop_orders_symbol'), 'trailing_stop_orders', ['symbol'], unique=False)
    op.create_index(op.f('ix_trailing_stop_orders_status'), 'trailing_stop_orders', ['status'], unique=False)
    op.create_index(op.f('ix_trailing_stop_orders_id'), 'trailing_stop_orders', ['id'], unique=False)

    # Create kyc_documents table
    op.create_table(
        'kyc_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('document_number', sa.String(length=100), nullable=True),
        sa.Column('document_file_url', sa.String(length=500), nullable=True),
        sa.Column('file_hash', sa.String(length=255), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('issuing_authority', sa.String(length=255), nullable=True),
        sa.Column('issuing_country', sa.String(length=100), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('ai_verification_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('ai_verification_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kyc_documents_user_id'), 'kyc_documents', ['user_id'], unique=False)
    op.create_index(op.f('ix_kyc_documents_verification_status'), 'kyc_documents', ['verification_status'], unique=False)
    op.create_index(op.f('ix_kyc_documents_id'), 'kyc_documents', ['id'], unique=False)

    # Create compliance_events table
    op.create_table(
        'compliance_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=True, server_default='medium'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='open'),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('risk_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('escalated', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('escalated_to', sa.Integer(), nullable=True),
        sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolution_action', sa.String(length=100), nullable=True),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('related_transaction_id', sa.Integer(), nullable=True),
        sa.Column('related_order_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['escalated_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_events_user_id'), 'compliance_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_compliance_events_event_type'), 'compliance_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_compliance_events_severity'), 'compliance_events', ['severity'], unique=False)
    op.create_index(op.f('ix_compliance_events_status'), 'compliance_events', ['status'], unique=False)
    op.create_index(op.f('ix_compliance_events_id'), 'compliance_events', ['id'], unique=False)

    # Create risk_assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assessment_type', sa.String(length=50), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('assessment_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('factors_considered', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}'),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('assessed_by', sa.Integer(), nullable=True),
        sa.Column('assessment_method', sa.String(length=50), nullable=True, server_default='automated'),
        sa.Column('next_review_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('previous_assessment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['previous_assessment_id'], ['risk_assessments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_assessments_user_id'), 'risk_assessments', ['user_id'], unique=False)
    op.create_index(op.f('ix_risk_assessments_risk_level'), 'risk_assessments', ['risk_level'], unique=False)
    op.create_index(op.f('ix_risk_assessments_status'), 'risk_assessments', ['status'], unique=False)
    op.create_index(op.f('ix_risk_assessments_id'), 'risk_assessments', ['id'], unique=False)

    # Create aml_screenings table
    op.create_table(
        'aml_screenings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('screening_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='clean'),
        sa.Column('risk_level', sa.String(length=20), nullable=True, server_default='low'),
        sa.Column('findings', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('sanctions_match', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('pep_match', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('adverse_media_match', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('watchlist_match', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sources_checked', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}'),
        sa.Column('last_checked', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('next_review', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('trigger_transaction_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_aml_screenings_user_id'), 'aml_screenings', ['user_id'], unique=False)
    op.create_index(op.f('ix_aml_screenings_status'), 'aml_screenings', ['status'], unique=False)
    op.create_index(op.f('ix_aml_screenings_id'), 'aml_screenings', ['id'], unique=False)

    # Create trading_bots table
    op.create_table(
        'trading_bots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('strategy_id', sa.String(length=100), nullable=True),
        sa.Column('strategy_name', sa.String(length=255), nullable=True),
        sa.Column('strategy_parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('symbols', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}'),
        sa.Column('base_amount', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('leverage', sa.Numeric(precision=10, scale=2), nullable=True, server_default='1'),
        sa.Column('max_positions', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('risk_per_trade', sa.Numeric(precision=5, scale=2), nullable=True, server_default='1'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='PAUSED'),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('winning_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('losing_trades', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_pnl', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('max_drawdown', sa.Numeric(precision=20, scale=8), nullable=True, server_default='0'),
        sa.Column('logs', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('error_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('last_error_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trading_bots_user_id'), 'trading_bots', ['user_id'], unique=False)
    op.create_index(op.f('ix_trading_bots_status'), 'trading_bots', ['status'], unique=False)
    op.create_index(op.f('ix_trading_bots_id'), 'trading_bots', ['id'], unique=False)

    # Create watchlists table
    op.create_table(
        'watchlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True, server_default='Default'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('symbols', postgresql.ARRAY(sa.String()), nullable=True, server_default='{}'),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_watchlists_id'), 'watchlists', ['id'], unique=False)

    # Create referral_codes table
    op.create_table(
        'referral_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('used_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('commission_rate', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('commission_type', sa.String(length=50), nullable=True, server_default='percentage'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referral_codes_staff_id'), 'referral_codes', ['staff_id'], unique=False)
    op.create_index(op.f('ix_referral_codes_code'), 'referral_codes', ['code'], unique=True)
    op.create_index(op.f('ix_referral_codes_token'), 'referral_codes', ['token'], unique=True)
    op.create_index(op.f('ix_referral_codes_status'), 'referral_codes', ['status'], unique=False)
    op.create_index(op.f('ix_referral_codes_id'), 'referral_codes', ['id'], unique=False)

    # Create referral_registrations table
    op.create_table(
        'referral_registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('referral_code_id', sa.Integer(), nullable=False),
        sa.Column('referred_user_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=20), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='pending'),
        sa.Column('commission_paid', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('commission_amount', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('commission_paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_deposit_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_trade_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['referral_code_id'], ['referral_codes.id'], ),
        sa.ForeignKeyConstraint(['referred_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referred_user_id')
    )
    op.create_index(op.f('ix_referral_registrations_referral_code_id'), 'referral_registrations', ['referral_code_id'], unique=False)
    op.create_index(op.f('ix_referral_registrations_referred_user_id'), 'referral_registrations', ['referred_user_id'], unique=True)
    op.create_index(op.f('ix_referral_registrations_id'), 'referral_registrations', ['id'], unique=False)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('result', sa.String(length=50), nullable=True, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True, server_default='info'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_type'), 'audit_logs', ['resource_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_id'), 'audit_logs', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)

    # Create analytics_events table
    op.create_table(
        'analytics_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('event_category', sa.String(length=50), nullable=True),
        sa.Column('event_label', sa.String(length=255), nullable=True),
        sa.Column('event_value', sa.Integer(), nullable=True),
        sa.Column('event_properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('page_url', sa.String(length=500), nullable=True),
        sa.Column('referrer', sa.String(length=500), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('browser', sa.String(length=100), nullable=True),
        sa.Column('os', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_events_user_id'), 'analytics_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_analytics_events_event_name'), 'analytics_events', ['event_name'], unique=False)
    op.create_index(op.f('ix_analytics_events_event_category'), 'analytics_events', ['event_category'], unique=False)
    op.create_index(op.f('ix_analytics_events_session_id'), 'analytics_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_analytics_events_id'), 'analytics_events', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('analytics_events')
    op.drop_table('audit_logs')
    op.drop_table('referral_registrations')
    op.drop_table('referral_codes')
    op.drop_table('watchlists')
    op.drop_table('trading_bots')
    op.drop_table('aml_screenings')
    op.drop_table('risk_assessments')
    op.drop_table('compliance_events')
    op.drop_table('kyc_documents')
    op.drop_table('trailing_stop_orders')
    op.drop_table('oco_orders')
    op.drop_table('iceberg_orders')
    op.drop_table('portfolio_positions')
    op.drop_table('trading_orders')
    op.drop_table('exchange_rates')
    op.drop_table('transactions')
    op.drop_table('wallet_balances')
    op.drop_table('refresh_tokens')
    op.drop_table('user_profiles')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')

