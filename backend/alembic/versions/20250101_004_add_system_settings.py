"""add_system_settings

Revision ID: 004_add_system_settings
Revises: 003_add_market_data_tables
Create Date: 2025-01-01 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_add_system_settings'
down_revision: Union[str, None] = '003_add_market_data_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
    
    # Insert default registration fields config
    import json
    default_config = {
        "fields": [
            {"key": "fullName", "label": "Họ và Tên", "enabled": True, "required": True, "type": "text", "placeholder": "Nhập họ và tên đầy đủ"},
            {"key": "email", "label": "Email", "enabled": True, "required": True, "type": "email", "placeholder": "example@gmail.com"},
            {"key": "phone", "label": "Số Điện Thoại", "enabled": True, "required": True, "type": "tel", "placeholder": "+84 xxx xxx xxx"},
            {"key": "dateOfBirth", "label": "Ngày Sinh", "enabled": False, "required": False, "type": "date", "placeholder": ""},
            {"key": "password", "label": "Mật Khẩu", "enabled": True, "required": True, "type": "password", "placeholder": "Tối thiểu 8 ký tự"},
            {"key": "confirmPassword", "label": "Xác Nhận Mật Khẩu", "enabled": True, "required": True, "type": "password", "placeholder": "Nhập lại mật khẩu"},
            {"key": "country", "label": "Quốc Gia", "enabled": True, "required": True, "type": "select", "placeholder": "Chọn quốc gia"},
            {"key": "tradingExperience", "label": "Kinh Nghiệm Giao Dịch", "enabled": True, "required": False, "type": "select", "placeholder": "Chọn mức độ kinh nghiệm"},
            {"key": "referralCode", "label": "Mã Giới Thiệu", "enabled": True, "required": False, "type": "text", "placeholder": "Nhập mã giới thiệu (nếu có)"},
            {"key": "agreeTerms", "label": "Đồng ý điều khoản", "enabled": True, "required": True, "type": "checkbox", "placeholder": ""},
            {"key": "agreeMarketing", "label": "Đồng ý nhận marketing", "enabled": True, "required": False, "type": "checkbox", "placeholder": ""}
        ]
    }
    
    # Insert using connection to properly handle JSONB
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            INSERT INTO system_settings (key, value, description, is_public)
            VALUES (
                'registration_fields',
                CAST(:config AS jsonb),
                'Cấu hình các trường đăng ký người dùng',
                true
            )
        """),
        {"config": json.dumps(default_config, ensure_ascii=False)}
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_key'), table_name='system_settings')
    op.drop_table('system_settings')

