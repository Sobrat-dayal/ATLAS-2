"""stage58_fund_metadata_and_nav

Revision ID: stage58_fund_metadata_and_nav
Revises: stage57_equity_listing_metadata
Create Date: 2026-10-15 11:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage58_fund_metadata_and_nav"
down_revision: Union[str, Sequence[str], None] = "stage57_equity_listing_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. Create fund_metadata table
    # -----------------------------------------------------------------------
    op.create_table(
        "fund_metadata",
        sa.Column(
            "instrument_entity_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("fund_type", sa.String(length=64), nullable=False),
        sa.Column("product_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("domicile", sa.String(length=64), nullable=True),
        sa.Column("inception_date", sa.Date(), nullable=True),
        sa.Column("investment_category", sa.String(length=128), nullable=True),
        sa.Column("distribution_policy", sa.String(length=64), nullable=True),
        sa.Column("base_currency", sa.String(length=16), server_default="USD", nullable=False),
        sa.Column(
            "share_class_currency", sa.String(length=16), server_default="USD", nullable=False
        ),
        sa.Column("benchmark_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("benchmark_name", sa.String(length=256), nullable=True),
        sa.Column("manager_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("manager_name", sa.String(length=256), nullable=True),
        sa.Column("sponsor_name", sa.String(length=256), nullable=True),
        sa.Column("fund_objective", sa.Text(), nullable=True),
        sa.Column("net_expense_ratio", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("gross_expense_ratio", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("fee_metric_type", sa.String(length=64), nullable=True),
        sa.Column("fee_effective_date", sa.Date(), nullable=True),
        sa.Column("total_aum", sa.Numeric(precision=38, scale=2), nullable=True),
        sa.Column("aum_currency", sa.String(length=16), nullable=True),
        sa.Column("aum_as_of_date", sa.Date(), nullable=True),
        sa.Column("aum_scope", sa.String(length=64), nullable=True),
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
            name="fk_fund_metadata_instrument",
        ),
        sa.ForeignKeyConstraint(
            ["product_entity_id"],
            ["entities.entity_id"],
            ondelete="SET NULL",
            name="fk_fund_metadata_product",
        ),
        sa.ForeignKeyConstraint(
            ["benchmark_entity_id"],
            ["entities.entity_id"],
            ondelete="SET NULL",
            name="fk_fund_metadata_benchmark",
        ),
        sa.ForeignKeyConstraint(
            ["manager_entity_id"],
            ["entities.entity_id"],
            ondelete="SET NULL",
            name="fk_fund_metadata_manager",
        ),
        sa.PrimaryKeyConstraint("instrument_entity_id", name="pk_fund_metadata"),
    )

    op.create_index(
        "ix_fund_metadata_fund_type",
        "fund_metadata",
        ["fund_type"],
        unique=False,
    )
    op.create_index(
        "ix_fund_metadata_domicile",
        "fund_metadata",
        ["domicile"],
        unique=False,
    )
    op.create_index(
        "ix_fund_metadata_category",
        "fund_metadata",
        ["investment_category"],
        unique=False,
    )

    # -----------------------------------------------------------------------
    # 2. Create fund_listing_metadata table
    # -----------------------------------------------------------------------
    op.create_table(
        "fund_listing_metadata",
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exchange_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("exchange_mic", sa.String(length=16), nullable=True),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("trading_currency", sa.String(length=16), server_default="USD", nullable=False),
        sa.Column("listing_status", sa.String(length=32), server_default="ACTIVE", nullable=False),
        sa.Column(
            "is_primary_listing", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
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
            name="fk_fund_listing_metadata_instrument",
        ),
        sa.ForeignKeyConstraint(
            ["exchange_entity_id"],
            ["exchanges.entity_id"],
            ondelete="SET NULL",
            name="fk_fund_listing_metadata_exchange",
        ),
        sa.PrimaryKeyConstraint("listing_id", name="pk_fund_listing_metadata"),
    )

    op.create_index(
        "ix_fund_listing_metadata_instrument",
        "fund_listing_metadata",
        ["instrument_entity_id"],
        unique=False,
    )
    op.create_index(
        "ix_fund_listing_metadata_symbol",
        "fund_listing_metadata",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        "ix_fund_listing_metadata_exchange_mic",
        "fund_listing_metadata",
        ["exchange_mic"],
        unique=False,
    )
    op.create_index(
        "uq_fund_listing_metadata_scoped",
        "fund_listing_metadata",
        ["instrument_entity_id", "exchange_mic", "symbol"],
        unique=True,
    )

    # -----------------------------------------------------------------------
    # 3. Create fund_nav_observations table
    # -----------------------------------------------------------------------
    op.create_table(
        "fund_nav_observations",
        sa.Column("nav_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nav_per_unit", sa.Numeric(precision=38, scale=6), nullable=False),
        sa.Column("nav_currency", sa.String(length=16), nullable=False),
        sa.Column("valuation_date", sa.Date(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "valuation_method",
            sa.String(length=64),
            server_default="OFFICIAL_CLOSE_NAV",
            nullable=True,
        ),
        sa.Column("provider_key", sa.String(length=64), nullable=True),
        sa.Column("provenance", sa.String(length=128), nullable=True),
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
            name="fk_fund_nav_observations_instrument",
        ),
        sa.PrimaryKeyConstraint("nav_id", name="pk_fund_nav_observations"),
    )

    op.create_index(
        "ix_fund_nav_observations_instrument",
        "fund_nav_observations",
        ["instrument_entity_id"],
        unique=False,
    )
    op.create_index(
        "ix_fund_nav_observations_valuation_date",
        "fund_nav_observations",
        ["valuation_date"],
        unique=False,
    )
    op.create_index(
        "uq_fund_nav_observations_scoped",
        "fund_nav_observations",
        ["instrument_entity_id", "valuation_date", "nav_currency"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("fund_nav_observations")
    op.drop_table("fund_listing_metadata")
    op.drop_table("fund_metadata")
