"""add_two_factor_fields

Revision ID: 006_two_factor
Revises: 005_invoices_payments
Create Date: 2025-01-01 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006_two_factor"
down_revision: Union[str, None] = "005_invoices_payments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Two-factor authentication fields on users table
    op.add_column(
        "users",
        sa.Column(
            "two_factor_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("two_factor_secret", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "two_factor_backup_codes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
        ),
    )
    op.create_index(
        op.f("ix_users_two_factor_enabled"),
        "users",
        ["two_factor_enabled"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_two_factor_enabled"), table_name="users")
    op.drop_column("users", "two_factor_backup_codes")
    op.drop_column("users", "two_factor_secret")
    op.drop_column("users", "two_factor_enabled")

