"""Add historical_market_data_ingestion_runs

Revision ID: 363f5a71dd6a
Revises: stage32_provider_routing
Create Date: 2026-10-08 19:34:57.109767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '363f5a71dd6a'
down_revision: Union[str, Sequence[str], None] = 'stage32_provider_routing'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'historical_market_data_ingestion_runs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('instrument_id', sa.UUID(), nullable=False),
        sa.Column('interval', sa.String(length=32), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('provider_key', sa.String(length=64), nullable=False),
        sa.Column('bars_ingested', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.id'], ondelete='CASCADE')
    )
    op.create_index(
        'ix_historical_market_data_ingestion_runs_instrument_id',
        'historical_market_data_ingestion_runs',
        ['instrument_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'ix_historical_market_data_ingestion_runs_instrument_id',
        table_name='historical_market_data_ingestion_runs'
    )
    op.drop_table('historical_market_data_ingestion_runs')
