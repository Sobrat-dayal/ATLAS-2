"""stage57_equity_listing_metadata

Revision ID: stage57_equity_listing_metadata
Revises: 9b2c3d4e5f6a
Create Date: 2026-10-15 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage57_equity_listing_metadata"
down_revision: Union[str, Sequence[str], None] = "9b2c3d4e5f6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. Create equity_listing_metadata table
    # -----------------------------------------------------------------------
    op.create_table(
        "equity_listing_metadata",
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exchange_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("exchange_mic", sa.String(length=16), nullable=True),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("quote_currency", sa.String(length=16), server_default="USD", nullable=False),
        sa.Column("listing_status", sa.String(length=32), server_default="ACTIVE", nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("metadata_provenance", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["instrument_entity_id"],
            ["securities.entity_id"],
            ondelete="CASCADE",
            name="fk_equity_listing_metadata_instrument",
        ),
        sa.ForeignKeyConstraint(
            ["exchange_entity_id"],
            ["exchanges.entity_id"],
            ondelete="SET NULL",
            name="fk_equity_listing_metadata_exchange",
        ),
        sa.PrimaryKeyConstraint("listing_id", name="pk_equity_listing_metadata"),
    )

    op.create_index(
        "ix_equity_listing_metadata_instrument",
        "equity_listing_metadata",
        ["instrument_entity_id"],
        unique=False,
    )
    op.create_index(
        "ix_equity_listing_metadata_exchange",
        "equity_listing_metadata",
        ["exchange_entity_id"],
        unique=False,
    )
    op.create_index(
        "ix_equity_listing_metadata_symbol",
        "equity_listing_metadata",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        "ix_equity_listing_metadata_exchange_mic",
        "equity_listing_metadata",
        ["exchange_mic"],
        unique=False,
    )
    op.create_index(
        "ix_equity_listing_metadata_status",
        "equity_listing_metadata",
        ["listing_status"],
        unique=False,
    )
    op.create_index(
        "uq_equity_listing_metadata_scoped",
        "equity_listing_metadata",
        ["instrument_entity_id", "exchange_mic", "symbol"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("equity_listing_metadata")
