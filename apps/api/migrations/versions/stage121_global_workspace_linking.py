"""stage121_global_workspace_linking

Revision ID: stage121_global_workspace_linking
Revises: stage120_workspaces_foundation
Create Date: 2026-10-30 00:00:00.000000

Stage 121 — Global Workspace Linking & Cross-Module Context Synchronization:
- global_context_channels: Link channels (Link A, B, C, D) with scopes and revisions.
- global_context_channel_memberships: Panel instance subscriptions with directional dimensions.
- global_context_snapshots: Historical context snapshots for recovery and audit.
- global_context_audit_events: Append-only audit log for context mutations.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage121_global_workspace_linking"
down_revision: Union[str, Sequence[str], None] = "stage120_workspaces_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. global_context_channels
    op.create_table(
        "global_context_channels",
        sa.Column("channel_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("workspace_id", sa.String(length=64), nullable=True, index=True),
        sa.Column("scope", sa.String(length=32), nullable=False, server_default="WORKSPACE"),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("display_color_token", sa.String(length=32), nullable=False, server_default="#3b82f6"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("supported_dimensions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("context_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ctx_channels_user_scope", "global_context_channels", ["owner_user_id", "scope"])

    # 2. global_context_channel_memberships
    op.create_table(
        "global_context_channel_memberships",
        sa.Column("subscription_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column(
            "channel_id",
            sa.String(length=64),
            sa.ForeignKey("global_context_channels.channel_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("panel_instance_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("mode", sa.String(length=32), nullable=False, server_default="BIDIRECTIONAL"),
        sa.Column("inbound_dimensions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("outbound_dimensions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("priority_policy", sa.String(length=32), nullable=False, server_default="NORMAL"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        "ix_ctx_channel_panel_unique",
        "global_context_channel_memberships",
        ["channel_id", "panel_instance_id"],
        unique=True,
    )

    # 3. global_context_snapshots
    op.create_table(
        "global_context_snapshots",
        sa.Column("snapshot_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column(
            "channel_id",
            sa.String(length=64),
            sa.ForeignKey("global_context_channels.channel_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("context_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_ctx_snapshot_channel_rev", "global_context_snapshots", ["channel_id", "revision"])

    # 4. global_context_audit_events
    op.create_table(
        "global_context_audit_events",
        sa.Column("audit_id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("channel_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("user_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("global_context_audit_events")
    op.drop_table("global_context_snapshots")
    op.drop_table("global_context_channel_memberships")
    op.drop_table("global_context_channels")

