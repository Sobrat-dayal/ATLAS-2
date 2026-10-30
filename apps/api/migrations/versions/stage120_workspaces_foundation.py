"""stage120_workspaces_foundation

Revision ID: stage120_workspaces_foundation
Revises: stage119_universal_saved_system
Create Date: 2026-10-30 00:00:00.000000

Stage 120 — Workspaces Architecture: Multi-panel financial desks, layout trees,
panel instances, cross-panel link groups, templates, and revision tracking.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage120_workspaces_foundation"
down_revision: Union[str, Sequence[str], None] = "stage119_universal_saved_system"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. workspaces table
    op.create_table(
        "workspaces",
        sa.Column("workspace_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(length=64), nullable=True, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("workspace_type", sa.String(length=32), nullable=False, server_default="CUSTOM"),
        sa.Column("template_origin_id", sa.String(length=64), nullable=True),
        sa.Column("layout_schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("layout_revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ACTIVE", index=True),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_opened_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_workspaces_user_status", "workspaces", ["owner_user_id", "status"])
    op.create_index("ix_workspaces_user_default", "workspaces", ["owner_user_id", "is_default"])

    # 2. workspace_layout_revisions table
    op.create_table(
        "workspace_layout_revisions",
        sa.Column("revision_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=64), sa.ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("layout_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ws_layout_rev_ws_num", "workspace_layout_revisions", ["workspace_id", "revision_number"], unique=True)

    # 3. workspace_panel_instances table
    op.create_table(
        "workspace_panel_instances",
        sa.Column("panel_instance_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=64), sa.ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("panel_type_id", sa.String(length=64), nullable=False),
        sa.Column("title_override", sa.String(length=128), nullable=True),
        sa.Column("configuration", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("link_group_id", sa.String(length=64), nullable=True),
        sa.Column("independent_mode", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # 4. workspace_link_groups table
    op.create_table(
        "workspace_link_groups",
        sa.Column("link_group_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=64), sa.ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("color", sa.String(length=32), nullable=False, server_default="#3b82f6"),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    # 5. workspace_templates table
    op.create_table(
        "workspace_templates",
        sa.Column("template_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("layout_definition", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("panel_definitions", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("required_capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )

    # 6. workspace_audit_events table
    op.create_table(
        "workspace_audit_events",
        sa.Column("event_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("workspace_id", sa.String(length=64), sa.ForeignKey("workspaces.workspace_id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("workspace_audit_events")
    op.drop_table("workspace_templates")
    op.drop_table("workspace_link_groups")
    op.drop_table("workspace_panel_instances")
    op.drop_table("workspace_layout_revisions")
    op.drop_table("workspaces")

