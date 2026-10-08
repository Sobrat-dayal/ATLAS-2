"""Add freshness overrides to live quote targets

Revision ID: b2b3c4d5e6f7
Revises: 9e8a7b6c5d4e
Create Date: 2026-10-08 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2b3c4d5e6f7'
down_revision: Union[str, None] = '9e8a7b6c5d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('market_data_live_quote_targets', sa.Column('freshness_fresh_until_seconds', sa.Integer(), nullable=True))
    op.add_column('market_data_live_quote_targets', sa.Column('freshness_stale_after_seconds', sa.Integer(), nullable=True))
    op.add_column('market_data_live_quote_targets', sa.Column('freshness_age_basis', sa.String(length=50), nullable=True))
    op.add_column('market_data_live_quote_targets', sa.Column('freshness_source_timestamp_fallback', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('market_data_live_quote_targets', 'freshness_source_timestamp_fallback')
    op.drop_column('market_data_live_quote_targets', 'freshness_age_basis')
    op.drop_column('market_data_live_quote_targets', 'freshness_stale_after_seconds')
    op.drop_column('market_data_live_quote_targets', 'freshness_fresh_until_seconds')
