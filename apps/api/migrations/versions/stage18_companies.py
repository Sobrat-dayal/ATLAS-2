"""stage18_companies

Revision ID: stage18_companies
Revises: stage17_instruments
Create Date: 2026-10-04 20:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "stage18_companies"
down_revision: Union[str, None] = "stage17_instruments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("legal_name", sa.String(length=512), nullable=True),
        sa.Column("short_name", sa.String(length=256), nullable=True),
        sa.Column("organization_type", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("founded_date", sa.Date(), nullable=True),
        sa.Column("website_url", sa.String(length=2048), nullable=True),
        sa.Column("primary_country_entity_id", sa.UUID(), nullable=True),
        sa.CheckConstraint(
            "organization_type IN ('public_company', 'private_company', 'state_owned', 'subsidiary', 'joint_venture', 'nonprofit', 'partnership', 'cooperative', 'other')",
            name="chk_companies_organization_type",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'dissolved', 'acquired', 'bankrupt', 'restructured', 'other')",
            name="chk_companies_status",
        ),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.entity_id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("entity_id"),
    )
    op.create_index(
        op.f("ix_companies_primary_country_entity_id"),
        "companies",
        ["primary_country_entity_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_primary_country_entity_id"), table_name="companies")
    op.drop_table("companies")
