"""stage124_ai_assistant_v1

Revision ID: stage124_ai_assistant_v1
Revises: stage123_terminal_execution
Create Date: 2026-10-30 00:00:00.000000

Stage 124 — AI Assistant V1 and Universal ATLAS AI Overlay:
- ai_conversations: Persistent chat conversation threads with title, model, and metadata.
- ai_messages: Multi-turn message history with route context, token usage, and status.
- ai_generation_runs: Model inference execution runs with token metrics and duration.
- ai_assistant_user_preferences: Per-user AI preferences (model, dock side, width).
- ai_conversation_audit_events: Append-only audit trail for conversation lifecycle events.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage124_ai_assistant_v1"
down_revision: Union[str, Sequence[str], None] = "stage123_terminal_execution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. ai_conversations
    op.create_table(
        "ai_conversations",
        sa.Column("conversation_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False, server_default="New Conversation"),
        sa.Column("model_id", sa.String(length=64), nullable=False, server_default="atlas-intelligence-v1"),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="atlas"),
        sa.Column("system_prompt_override", sa.Text(), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("pinned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("message_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ai_conversations_owner", "ai_conversations", ["owner_user_id"])
    op.create_index("ix_ai_conversations_tenant", "ai_conversations", ["tenant_id"])
    op.create_index("ix_ai_conversations_user_updated", "ai_conversations", ["owner_user_id", "updated_at"])
    op.create_index("ix_ai_conversations_user_archived", "ai_conversations", ["owner_user_id", "is_archived"])
    op.create_index("ix_ai_conversations_user_pinned", "ai_conversations", ["owner_user_id", "is_pinned"])

    # 2. ai_messages
    op.create_table(
        "ai_messages",
        sa.Column("message_id", sa.String(length=64), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(length=64),
            sa.ForeignKey("ai_conversations.conversation_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="COMPLETED"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("route_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generation_run_id", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_messages_conversation", "ai_messages", ["conversation_id"])
    op.create_index("ix_ai_messages_owner", "ai_messages", ["owner_user_id"])
    op.create_index("ix_ai_messages_conv_created", "ai_messages", ["conversation_id", "created_at"])

    # 3. ai_generation_runs
    op.create_table(
        "ai_generation_runs",
        sa.Column("generation_id", sa.String(length=64), primary_key=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=False),
        sa.Column("user_message_id", sa.String(length=64), nullable=False),
        sa.Column("assistant_message_id", sa.String(length=64), nullable=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="RUNNING"),
        sa.Column("model_id", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ai_generation_runs_conversation", "ai_generation_runs", ["conversation_id"])
    op.create_index("ix_ai_generation_runs_owner", "ai_generation_runs", ["owner_user_id"])

    # 4. ai_assistant_user_preferences
    op.create_table(
        "ai_assistant_user_preferences",
        sa.Column("preference_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("default_model_id", sa.String(length=64), nullable=False, server_default="atlas-intelligence-v1"),
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.2"),
        sa.Column("send_on_enter", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sound_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("overlay_dock_side", sa.String(length=16), nullable=False, server_default="right"),
        sa.Column("overlay_width_px", sa.Integer(), nullable=False, server_default="420"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_assistant_user_preferences_owner", "ai_assistant_user_preferences", ["owner_user_id"])

    # 5. ai_conversation_audit_events
    op.create_table(
        "ai_conversation_audit_events",
        sa.Column("audit_id", sa.String(length=64), primary_key=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_conversation_audit_events_owner", "ai_conversation_audit_events", ["owner_user_id"])
    op.create_index("ix_ai_conversation_audit_events_conversation", "ai_conversation_audit_events", ["conversation_id"])


def downgrade() -> None:
    op.drop_table("ai_conversation_audit_events")
    op.drop_table("ai_assistant_user_preferences")
    op.drop_table("ai_generation_runs")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")

