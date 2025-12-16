"""add_custom_id_to_user_profiles

Revision ID: 20250110_001_add_custom_id_to_user_profiles
Revises: 20250109_001_add_timescaledb_support
Create Date: 2025-01-10 12:00:00.000000

Migration để thêm trường custom_id vào bảng user_profiles
Cho phép khách hàng tự đặt ID/username tùy chỉnh
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250110_001_add_custom_id_to_user_profiles'
down_revision: Union[str, None] = '20250109_001_add_timescaledb_support'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Thêm cột custom_id vào bảng user_profiles
    - String(50): Độ dài tối đa 50 ký tự
    - nullable=True: Không bắt buộc
    - unique=True: Đảm bảo không trùng lặp
    - index=True: Tối ưu truy vấn
    """
    op.add_column(
        'user_profiles',
        sa.Column('custom_id', sa.String(50), nullable=True, unique=True, index=True)
    )


def downgrade() -> None:
    """
    Xóa cột custom_id khỏi bảng user_profiles
    """
    op.drop_column('user_profiles', 'custom_id')
