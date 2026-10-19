"""stage76_watchlists

Revision ID: stage76_watchlists
Revises: stage74_chart_layouts
Create Date: 2026-10-19 12:00:00.000000

Stage 76 — Watchlists V1: Persistent Multi-Asset Watchlists.
Creates `watchlists` and `watchlist_items` tables backed by PostgreSQL
with owner-scoped isolation, monotonic revision tracking, unique normalized names,
canonical financial instrument foreign key references, and dense position ordering.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage76_watchlists"
down_revision: Union[str, Sequence[str], None] = "stage74_chart_layouts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create `watchlists` table
    op.create_table(
        "watchlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("normalized_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("revision", sa.BigInteger(), nullable=False, server_default="1"),
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
    )

    # Indexes on watchlists
    op.create_index(
        "ix_watchlists_owner_user_id",
        "watchlists",
        ["owner_user_id"],
    )

    op.create_index(
        "ix_watchlists_owner_updated",
        "watchlists",
        ["owner_user_id", sa.text("updated_at DESC")],
    )

    op.create_unique_constraint(
        "uq_watchlists_owner_normalized_name",
        "watchlists",
        ["owner_user_id", "normalized_name"],
    )

    # 2. Create `watchlist_items` table
    op.create_table(
        "watchlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "watchlist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlists.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "instrument_entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("market_series_id", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Indexes on watchlist_items
    op.create_index(
        "ix_watchlist_items_watchlist_position",
        "watchlist_items",
        ["watchlist_id", "position"],
    )

    op.create_index(
        "ix_watchlist_items_instrument",
        "watchlist_items",
        ["instrument_entity_id"],
    )

    op.create_unique_constraint(
        "uq_watchlist_items_membership",
        "watchlist_items",
        ["watchlist_id", "instrument_entity_id", "market_series_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_watchlist_items_membership", "watchlist_items", type_="unique")
    op.drop_index("ix_watchlist_items_instrument", table_name="watchlist_items")
    op.drop_index("ix_watchlist_items_watchlist_position", table_name="watchlist_items")
    op.drop_table("watchlist_items")

    op.drop_constraint("uq_watchlists_owner_normalized_name", "watchlists", type_="unique")
    op.drop_index("ix_watchlists_owner_updated", table_name="watchlists")
    op.drop_index("ix_watchlists_owner_user_id", table_name="watchlists")
    op.drop_table("watchlists")
