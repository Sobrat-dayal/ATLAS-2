"""stage77_watchlist_columns

Revision ID: stage77_watchlist_columns
Revises: stage76_watchlists
Create Date: 2026-10-20 00:00:00.000000

Stage 77 — Advanced Watchlist Columns V1: Professional Configurable Financial Tables.
Creates `watchlist_column_preferences` table backed by PostgreSQL JSONB documents with
per-watchlist column visibility, ordering, widths, pinning, and sorting preferences,
with monotonic revision concurrency control and cascade deletion on parent watchlist.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage77_watchlist_columns"
down_revision: Union[str, Sequence[str], None] = "stage76_watchlists"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create `watchlist_column_preferences` table
    op.create_table(
        "watchlist_column_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "watchlist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlists.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "configuration_schema_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "revision",
            sa.BigInteger(),
            nullable=False,
            server_default="1",
        ),
        sa.Column(
            "configuration_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
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

    # Index on watchlist_id
    op.create_index(
        "ix_watchlist_column_preferences_watchlist",
        "watchlist_column_preferences",
        ["watchlist_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_watchlist_column_preferences_watchlist",
        table_name="watchlist_column_preferences",
    )
    op.drop_table("watchlist_column_preferences")
