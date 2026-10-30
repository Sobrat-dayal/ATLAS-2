"""stage119_universal_saved_system

Revision ID: stage119_universal_saved_system
Revises: stage80_watchlist_alerts
Create Date: 2026-10-30 00:00:00.000000

Stage 119 — Universal Saved System, Cross-Module Bookmarking, Collections, Tags, Notes,
View Configurations, Reference Resolution, and Persistent Financial Intelligence Library.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage119_universal_saved_system"
down_revision: Union[str, Sequence[str], None] = "stage80_watchlist_alerts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create `saved_view_configurations` table
    op.create_table(
        "saved_view_configurations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("configuration_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("target_module", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # 2. Create `saved_items` table
    op.create_table(
        "saved_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("target_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("target_id", sa.String(length=512), nullable=False, index=True),
        sa.Column("target_revision_id", sa.String(length=128), nullable=True),
        sa.Column("target_module", sa.String(length=64), nullable=False, index=True),
        sa.Column("canonical_title", sa.String(length=512), nullable=False),
        sa.Column("display_title_override", sa.String(length=256), nullable=True),
        sa.Column("user_note", sa.Text(), nullable=True),
        sa.Column("favorite", sa.Boolean(), server_default=sa.text("false"), nullable=False, index=True),
        sa.Column("pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False, index=True),
        sa.Column(
            "view_configuration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("saved_view_configurations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("semantics", sa.String(length=64), server_default="LIVE_REFERENCE", nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("row_version", sa.Integer(), server_default="1", nullable=False),
    )
    op.create_index(
        "ix_saved_items_owner_type_target",
        "saved_items",
        ["owner_user_id", "target_type", "target_id"],
    )
    op.create_index(
        "ix_saved_items_owner_recent",
        "saved_items",
        ["owner_user_id", "saved_at"],
    )

    # 3. Create `saved_collections` table
    op.create_table(
        "saved_collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "parent_collection_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("saved_collections.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("row_version", sa.Integer(), server_default="1", nullable=False),
    )

    # 4. Create `saved_collection_memberships` table
    op.create_table(
        "saved_collection_memberships",
        sa.Column(
            "collection_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("saved_collections.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "saved_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("saved_items.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
    )

    # 5. Create `saved_tags` table
    op.create_table(
        "saved_tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("normalized_name", sa.String(length=64), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("owner_user_id", "normalized_name", name="uq_saved_tags_owner_norm"),
    )

    # 6. Create `saved_item_tags` table
    op.create_table(
        "saved_item_tags",
        sa.Column(
            "saved_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("saved_items.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("saved_tags.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
    )

    # 7. Create `saved_audit_events` table
    op.create_table(
        "saved_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False, index=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("target_entity_id", sa.String(length=128), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("saved_audit_events")
    op.drop_table("saved_item_tags")
    op.drop_table("saved_tags")
    op.drop_table("saved_collection_memberships")
    op.drop_table("saved_collections")
    op.drop_table("saved_items")
    op.drop_table("saved_view_configurations")

