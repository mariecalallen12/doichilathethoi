"""merge divergent branches

Revision ID: fe36376b3c66
Revises: 20250112_002_seed_education_support_legal_data, custom_002_market_history
Create Date: 2025-12-21 03:18:46.257163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe36376b3c66'
down_revision: Union[str, None] = ('20250112_002_seed_education_support_legal_data', 'custom_002_market_history')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
