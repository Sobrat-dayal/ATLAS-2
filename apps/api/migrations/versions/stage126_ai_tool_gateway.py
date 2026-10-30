"""stage126_ai_tool_gateway

Revision ID: stage126_ai_tool_gateway
Revises: stage125_ai_context_awareness
Create Date: 2026-10-30 00:00:00.000000

Stage 126 — ATLAS AI Tool Gateway:
- ai_tool_calls: Persistent record of proposed, validated, and executed tool calls.
- ai_tool_approval_requests: Human-in-the-loop approval tokens with argument hashes and expiration.
- ai_tool_preferences: User settings for tool discovery, auto-approval, and permissions.
- ai_tool_audit_events: Append-only audit trail for all tool execution and security governance events.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage126_ai_tool_gateway"
down_revision: Union[str, Sequence[str], None] = "stage125_ai_context_awareness"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. ai_tool_calls
    op.create_table(
        "ai_tool_calls",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("tool_id", sa.String(length=128), nullable=False),
        sa.Column("tool_version", sa.String(length=32), nullable=False, server_default="1.0.0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PROPOSED"),
        sa.Column("arguments", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("normalized_arguments_hash", sa.String(length=64), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),
        sa.Column("approval_class", sa.String(length=32), nullable=False, server_default="NO_APPROVAL_REQUIRED"),
        sa.Column("approval_request_id", sa.String(length=64), nullable=True),
        sa.Column("generation_run_id", sa.String(length=64), nullable=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_tool_calls_user_id", "ai_tool_calls", ["user_id"])
    op.create_index("ix_ai_tool_calls_tool_id", "ai_tool_calls", ["tool_id"])
    op.create_index("ix_ai_tool_calls_status", "ai_tool_calls", ["status"])
    op.create_index("ix_ai_tool_calls_normalized_hash", "ai_tool_calls", ["normalized_arguments_hash"])
    op.create_index("ix_ai_tool_calls_gen_run", "ai_tool_calls", ["generation_run_id"])
    op.create_index("ix_ai_tool_calls_conv", "ai_tool_calls", ["conversation_id"])

    # 2. ai_tool_approval_requests
    op.create_table(
        "ai_tool_approval_requests",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("tool_call_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("tool_id", sa.String(length=128), nullable=False),
        sa.Column("approval_class", sa.String(length=32), nullable=False),
        sa.Column("normalized_arguments_hash", sa.String(length=64), nullable=False),
        sa.Column("arguments_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="PENDING"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_tool_approvals_user_id", "ai_tool_approval_requests", ["user_id"])
    op.create_index("ix_ai_tool_approvals_tool_id", "ai_tool_approval_requests", ["tool_id"])
    op.create_index("ix_ai_tool_approvals_status", "ai_tool_approval_requests", ["status"])

    # 3. ai_tool_preferences
    op.create_table(
        "ai_tool_preferences",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("enabled_tools", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("disabled_tools", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("auto_approve_read_only", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("require_approval_for_sensitive", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_tool_preferences_user_id", "ai_tool_preferences", ["user_id"])

    # 4. ai_tool_audit_events
    op.create_table(
        "ai_tool_audit_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("tool_id", sa.String(length=128), nullable=False),
        sa.Column("tool_call_id", sa.String(length=64), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_tool_audit_events_user_id", "ai_tool_audit_events", ["user_id"])
    op.create_index("ix_ai_tool_audit_events_tool_id", "ai_tool_audit_events", ["tool_id"])


def downgrade() -> None:
    op.drop_table("ai_tool_audit_events")
    op.drop_table("ai_tool_preferences")
    op.drop_table("ai_tool_approval_requests")
    op.drop_table("ai_tool_calls")

