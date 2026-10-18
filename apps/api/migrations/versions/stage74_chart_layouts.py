"""stage74_chart_layouts

Revision ID: stage74_chart_layouts
Revises: stage58_fund_metadata_and_nav
Create Date: 2026-10-18 10:00:00.000000

Stage 74 — Persistent Professional Chart Workspaces (Saved Chart Layouts V1).
Creates `chart_layouts` table backed by PostgreSQL JSONB documents with
owner-scoped isolation, monotonic revision tracking, unique normalized names,
and at most one default layout per user.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage74_chart_layouts"
down_revision: Union[str, Sequence[str], None] = "stage58_fund_metadata_and_nav"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chart_layouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("normalized_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("document_schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("revision", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("layout_document", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
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

    # 1. Indexes for fast owner-scoped querying and sorting
    op.create_index(
        "ix_chart_layouts_owner_user_id",
        "chart_layouts",
        ["owner_user_id"],
    )

    op.create_index(
        "ix_chart_layouts_owner_updated",
        "chart_layouts",
        ["owner_user_id", sa.text("updated_at DESC")],
    )

    # 2. Unique normalized name per owner
    op.create_unique_constraint(
        "uq_chart_layouts_owner_normalized_name",
        "chart_layouts",
        ["owner_user_id", "normalized_name"],
    )

    # 3. Partial unique index for at most one default layout per owner
    op.create_index(
        "uq_chart_layouts_owner_default",
        "chart_layouts",
        ["owner_user_id"],
        unique=True,
        postgresql_where=sa.text("is_default = TRUE"),
    )


def downgrade() -> None:
    op.drop_index("uq_chart_layouts_owner_default", table_name="chart_layouts")
    op.drop_constraint("uq_chart_layouts_owner_normalized_name", "chart_layouts", type_="unique")
    op.drop_index("ix_chart_layouts_owner_updated", table_name="chart_layouts")
    op.drop_index("ix_chart_layouts_owner_user_id", table_name="chart_layouts")
    op.drop_table("chart_layouts")
