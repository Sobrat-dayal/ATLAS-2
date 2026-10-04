"""stage16_entities

Revision ID: b3a479d2b271
Revises: 1c90fa701c49
Create Date: 2026-10-04 20:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3a479d2b271"
down_revision: Union[str, None] = "1c90fa701c49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create entity_types table
    op.create_table(
        "entity_types",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_key", sa.String(length=128), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
            ["parent_key"],
            ["entity_types.key"],
            ondelete="RESTRICT",
            name="fk_entity_types_parent_key",
        ),
        sa.PrimaryKeyConstraint("key", name="pk_entity_types"),
    )

    # 2. Seed canonical entity types
    entity_types_table = sa.table(
        "entity_types",
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("parent_key", sa.String),
        sa.column("is_system", sa.Boolean),
    )

    canonical_types = [
        {
            "key": "security",
            "name": "Security",
            "description": "A tradable financial asset",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "equity",
            "name": "Equity",
            "description": None,
            "parent_key": "security",
            "is_system": True,
        },
        {
            "key": "etf",
            "name": "ETF",
            "description": None,
            "parent_key": "security",
            "is_system": True,
        },
        {
            "key": "bond",
            "name": "Bond",
            "description": None,
            "parent_key": "security",
            "is_system": True,
        },
        {
            "key": "option",
            "name": "Option",
            "description": None,
            "parent_key": "security",
            "is_system": True,
        },
        {
            "key": "future",
            "name": "Future",
            "description": None,
            "parent_key": "security",
            "is_system": True,
        },
        {
            "key": "fund",
            "name": "Fund",
            "description": None,
            "parent_key": "security",
            "is_system": True,
        },
        {
            "key": "crypto",
            "name": "Crypto Asset",
            "description": "A digital or cryptographic asset",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "currency",
            "name": "Currency",
            "description": "A fiat currency",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "commodity",
            "name": "Commodity",
            "description": "A physical commodity",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "index",
            "name": "Index",
            "description": "A financial index",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "company",
            "name": "Company",
            "description": "A business entity or corporation",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "person",
            "name": "Person",
            "description": "An individual",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "country",
            "name": "Country",
            "description": "A sovereign state or territory",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "facility",
            "name": "Facility",
            "description": "A physical facility or installation",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "port",
            "name": "Port",
            "description": None,
            "parent_key": "facility",
            "is_system": True,
        },
        {
            "key": "airport",
            "name": "Airport",
            "description": None,
            "parent_key": "facility",
            "is_system": True,
        },
        {
            "key": "exchange",
            "name": "Exchange",
            "description": "A trading exchange or venue",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "economic_series",
            "name": "Economic Series",
            "description": "A macro-economic data series",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "news_event",
            "name": "News Event",
            "description": "An impactful news event",
            "parent_key": None,
            "is_system": True,
        },
        {
            "key": "research_document",
            "name": "Research Document",
            "description": "A published research document",
            "parent_key": None,
            "is_system": True,
        },
    ]

    op.bulk_insert(entity_types_table, canonical_types)

    # 3. Create entities table
    op.create_table(
        "entities",
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("entity_type", sa.String(length=128), nullable=False),
        sa.Column("canonical_name", sa.String(length=512), nullable=False),
        sa.Column("display_name", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
            ["entity_type"],
            ["entity_types.key"],
            ondelete="RESTRICT",
            name="fk_entities_entity_type",
        ),
        sa.PrimaryKeyConstraint("entity_id", name="pk_entities"),
    )

    op.create_index(op.f("ix_entities_entity_type"), "entities", ["entity_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_entities_entity_type"), table_name="entities")
    op.drop_table("entities")
    op.drop_table("entity_types")
