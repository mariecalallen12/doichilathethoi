"""seed_initial_data

Revision ID: 002_seed_initial_data
Revises: 001_create_all_tables
Create Date: 2025-01-01 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_seed_initial_data'
down_revision: Union[str, None] = '001_create_all_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert roles
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('is_system_role', sa.Boolean),
    )
    
    op.bulk_insert(roles_table, [
        {
            'id': 1,
            'name': 'owner',
            'description': 'Chủ sở hữu hệ thống - Toàn quyền',
            'is_system_role': True,
        },
        {
            'id': 2,
            'name': 'admin',
            'description': 'Quản trị viên - Quản lý hệ thống',
            'is_system_role': True,
        },
        {
            'id': 3,
            'name': 'staff',
            'description': 'Nhân viên - Hỗ trợ khách hàng',
            'is_system_role': True,
        },
        {
            'id': 4,
            'name': 'customer',
            'description': 'Khách hàng - Người dùng thông thường',
            'is_system_role': True,
        },
    ])
    
    # Insert permissions
    permissions_table = sa.table(
        'permissions',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('resource', sa.String),
        sa.column('action', sa.String),
    )
    
    permissions_data = [
        # User management
        {'id': 1, 'name': 'users.view', 'description': 'Xem danh sách người dùng', 'resource': 'users', 'action': 'view'},
        {'id': 2, 'name': 'users.create', 'description': 'Tạo người dùng mới', 'resource': 'users', 'action': 'create'},
        {'id': 3, 'name': 'users.update', 'description': 'Cập nhật thông tin người dùng', 'resource': 'users', 'action': 'update'},
        {'id': 4, 'name': 'users.delete', 'description': 'Xóa người dùng', 'resource': 'users', 'action': 'delete'},
        {'id': 5, 'name': 'users.manage_roles', 'description': 'Quản lý vai trò người dùng', 'resource': 'users', 'action': 'manage_roles'},
        
        # Trading management
        {'id': 10, 'name': 'trading.view', 'description': 'Xem giao dịch', 'resource': 'trading', 'action': 'view'},
        {'id': 11, 'name': 'trading.create', 'description': 'Tạo lệnh giao dịch', 'resource': 'trading', 'action': 'create'},
        {'id': 12, 'name': 'trading.cancel', 'description': 'Hủy lệnh giao dịch', 'resource': 'trading', 'action': 'cancel'},
        {'id': 13, 'name': 'trading.manage', 'description': 'Quản lý giao dịch (admin)', 'resource': 'trading', 'action': 'manage'},
        
        # Financial management
        {'id': 20, 'name': 'financial.view', 'description': 'Xem giao dịch tài chính', 'resource': 'financial', 'action': 'view'},
        {'id': 21, 'name': 'financial.deposit', 'description': 'Nạp tiền', 'resource': 'financial', 'action': 'deposit'},
        {'id': 22, 'name': 'financial.withdraw', 'description': 'Rút tiền', 'resource': 'financial', 'action': 'withdraw'},
        {'id': 23, 'name': 'financial.approve', 'description': 'Duyệt giao dịch tài chính', 'resource': 'financial', 'action': 'approve'},
        
        # Admin management
        {'id': 30, 'name': 'admin.dashboard', 'description': 'Truy cập dashboard admin', 'resource': 'admin', 'action': 'dashboard'},
        {'id': 31, 'name': 'admin.analytics', 'description': 'Xem analytics', 'resource': 'admin', 'action': 'analytics'},
        {'id': 32, 'name': 'admin.reports', 'description': 'Xem báo cáo', 'resource': 'admin', 'action': 'reports'},
        {'id': 33, 'name': 'admin.settings', 'description': 'Quản lý cài đặt hệ thống', 'resource': 'admin', 'action': 'settings'},
        {'id': 34, 'name': 'admin.logs', 'description': 'Xem audit logs', 'resource': 'admin', 'action': 'logs'},
        
        # Compliance management
        {'id': 40, 'name': 'compliance.kyc', 'description': 'Quản lý KYC', 'resource': 'compliance', 'action': 'kyc'},
        {'id': 41, 'name': 'compliance.aml', 'description': 'Quản lý AML', 'resource': 'compliance', 'action': 'aml'},
        {'id': 42, 'name': 'compliance.risk', 'description': 'Đánh giá rủi ro', 'resource': 'compliance', 'action': 'risk'},
    ]
    
    op.bulk_insert(permissions_table, permissions_data)
    
    # Insert role_permissions (owner gets all, admin gets most, staff gets limited, customer gets basic)
    role_permissions_table = sa.table(
        'role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer),
    )
    
    # Owner: all permissions (only IDs that exist: 1-5, 10-13, 20-23, 30-34, 40-42)
    # Note: IDs 6-9, 14-19, 24-29, 35-39 are skipped as they don't exist
    valid_permission_ids = [1, 2, 3, 4, 5, 10, 11, 12, 13, 20, 21, 22, 23, 30, 31, 32, 33, 34, 40, 41, 42]
    owner_permissions = [{'role_id': 1, 'permission_id': pid} for pid in valid_permission_ids]
    
    # Admin: all except owner-specific
    admin_permissions = [
        {'role_id': 2, 'permission_id': pid} for pid in [1, 3, 4, 5, 10, 11, 12, 13, 20, 21, 22, 23, 30, 31, 32, 33, 34, 40, 41, 42]
    ]
    
    # Staff: view and basic management
    staff_permissions = [
        {'role_id': 3, 'permission_id': pid} for pid in [1, 20, 23, 30, 40, 41]
    ]
    
    # Customer: basic trading and financial
    customer_permissions = [
        {'role_id': 4, 'permission_id': pid} for pid in [10, 11, 12, 20, 21, 22]
    ]
    
    op.bulk_insert(role_permissions_table, owner_permissions + admin_permissions + staff_permissions + customer_permissions)
    
    # Insert exchange rates (common pairs)
    exchange_rates_table = sa.table(
        'exchange_rates',
        sa.column('base_asset', sa.String),
        sa.column('target_asset', sa.String),
        sa.column('rate', sa.Numeric),
        sa.column('inverse_rate', sa.Numeric),
        sa.column('is_active', sa.Boolean),
        sa.column('priority', sa.Integer),
        sa.column('source', sa.String),
    )
    
    # Common exchange rates (mock values - will be updated by market data service)
    exchange_rates_data = [
        {'base_asset': 'USD', 'target_asset': 'VND', 'rate': 25000, 'inverse_rate': 0.00004, 'is_active': True, 'priority': 1, 'source': 'internal'},
        {'base_asset': 'VND', 'target_asset': 'USD', 'rate': 0.00004, 'inverse_rate': 25000, 'is_active': True, 'priority': 1, 'source': 'internal'},
        {'base_asset': 'USDT', 'target_asset': 'USD', 'rate': 1.0, 'inverse_rate': 1.0, 'is_active': True, 'priority': 1, 'source': 'internal'},
        {'base_asset': 'USD', 'target_asset': 'USDT', 'rate': 1.0, 'inverse_rate': 1.0, 'is_active': True, 'priority': 1, 'source': 'internal'},
        {'base_asset': 'BTC', 'target_asset': 'USD', 'rate': 45000, 'inverse_rate': 0.000022, 'is_active': True, 'priority': 1, 'source': 'internal'},
        {'base_asset': 'ETH', 'target_asset': 'USD', 'rate': 2500, 'inverse_rate': 0.0004, 'is_active': True, 'priority': 1, 'source': 'internal'},
    ]
    
    op.bulk_insert(exchange_rates_table, exchange_rates_data)


def downgrade() -> None:
    # Delete exchange rates
    op.execute("DELETE FROM exchange_rates")
    
    # Delete role_permissions
    op.execute("DELETE FROM role_permissions")
    
    # Delete permissions
    op.execute("DELETE FROM permissions")
    
    # Delete roles
    op.execute("DELETE FROM roles")

