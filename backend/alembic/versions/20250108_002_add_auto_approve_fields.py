"""add_auto_approve_fields

Revision ID: 20250108_002_add_auto_approve_fields
Revises: 20250108_001_unify_schema
Create Date: 2025-01-08 12:00:00.000000

Migration để thêm các fields cho tính năng auto approve registration
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250108_002_add_auto_approve_fields'
down_revision: Union[str, None] = '20250108_001_unify_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Thêm các columns cho auto approve registration:
    - is_approved: BOOLEAN - Trạng thái đã được approve chưa
    - approved_at: TIMESTAMP - Thời gian được approve
    - approved_by: INTEGER - User ID của admin approve (FK to users.id)
    """
    
    # Thêm is_approved column
    try:
        op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=True, server_default='false'))
    except Exception:
        pass  # Column đã tồn tại
    
    # Thêm approved_at column
    try:
        op.add_column('users', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    except Exception:
        pass  # Column đã tồn tại
    
    # Thêm approved_by column
    try:
        op.add_column('users', sa.Column('approved_by', sa.Integer(), nullable=True))
        # Thêm foreign key constraint
        op.create_foreign_key(
            'fk_users_approved_by',
            'users', 'users',
            ['approved_by'], ['id'],
            ondelete='SET NULL'
        )
    except Exception:
        pass  # Column đã tồn tại
    
    # Tạo index cho is_approved để query nhanh hơn
    try:
        op.create_index('ix_users_is_approved', 'users', ['is_approved'], unique=False, if_not_exists=True)
    except Exception:
        pass
    
    # Update existing users: set is_approved = true nếu status = 'active'
    # Wrap in try-except để tránh lỗi nếu đã được update trước đó
    try:
        op.execute("""
            UPDATE users 
            SET is_approved = true 
            WHERE status = 'active' AND is_approved IS NULL
        """)
    except Exception:
        pass  # Đã được update hoặc không cần update


def downgrade() -> None:
    """
    Xóa các columns đã thêm
    """
    try:
        op.drop_index('ix_users_is_approved', table_name='users', if_exists=True)
    except Exception:
        pass
    
    try:
        op.drop_constraint('fk_users_approved_by', 'users', type_='foreignkey')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'approved_by')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'approved_at')
    except Exception:
        pass
    
    try:
        op.drop_column('users', 'is_approved')
    except Exception:
        pass

