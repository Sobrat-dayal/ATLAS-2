"""stage125_ai_context_awareness

Revision ID: stage125_ai_context_awareness
Revises: stage124_ai_assistant_v1
Create Date: 2026-10-30 00:00:00.000000

Stage 125 — ATLAS AI Context Awareness Engine:
- ai_context_preferences: User preferences for AI context modes, permissions, and entity pinning.
- ai_context_source_manifests: Immutable audit records linking generation runs to verified context items.
- ai_context_audit_events: Append-only audit trail for context queries, overrides, and resolution events.
- ai_generation_runs: Adds source_manifest_id column for direct manifest correlation.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage125_ai_context_awareness"
down_revision: Union[str, Sequence[str], None] = "stage124_ai_assistant_v1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. ai_context_preferences
    op.create_table(
        "ai_context_preferences",
        sa.Column("preference_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("context_mode", sa.String(length=32), nullable=False, server_default="FOCUSED"),
        sa.Column("allow_workspace_context", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("allow_portfolio_holdings_context", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allow_research_drafts_context", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("pinned_context_references", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("excluded_context_references", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("provider_disclosure_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_context_prefs_user", "ai_context_preferences", ["owner_user_id"])
    op.create_index("ix_ai_context_prefs_tenant", "ai_context_preferences", ["tenant_id"])

    # 2. ai_context_source_manifests
    op.create_table(
        "ai_context_source_manifests",
        sa.Column("manifest_id", sa.String(length=64), primary_key=True),
        sa.Column("generation_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("context_mode", sa.String(length=32), nullable=False, server_default="FOCUSED"),
        sa.Column("source_items", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("total_estimated_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assembled_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_context_manifests_gen", "ai_context_source_manifests", ["generation_id"])
    op.create_index("ix_ai_context_manifests_user", "ai_context_source_manifests", ["owner_user_id"])

    # 3. ai_context_audit_events
    op.create_table(
        "ai_context_audit_events",
        sa.Column("audit_id", sa.String(length=64), primary_key=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_context_audit_type_user", "ai_context_audit_events", ["event_type", "owner_user_id"])
    op.create_index("ix_ai_context_audit_created", "ai_context_audit_events", ["created_at"])

    # 4. Add source_manifest_id to ai_generation_runs
    op.add_column(
        "ai_generation_runs",
        sa.Column("source_manifest_id", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ai_generation_runs", "source_manifest_id")
    op.drop_table("ai_context_audit_events")
    op.drop_table("ai_context_source_manifests")
    op.drop_table("ai_context_preferences")

