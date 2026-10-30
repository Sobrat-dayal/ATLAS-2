"""stage122_terminal_shell

Revision ID: stage122_terminal_shell
Revises: stage121_global_workspace_linking
Create Date: 2026-10-30 00:00:00.000000

Stage 122 — Integrated ATLAS Terminal Shell:
- terminal_sessions: Persistent sessions across ATLAS CLI, Python, SQL, Logs, Agents, and MCP.
- terminal_user_preferences: User terminal preferences (height, font size/family, scrollback limit).
- terminal_audit_events: Append-only audit trail for session lifecycle and terminal operations.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage122_terminal_shell"
down_revision: Union[str, Sequence[str], None] = "stage121_global_workspace_linking"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. terminal_sessions
    op.create_table(
        "terminal_sessions",
        sa.Column("session_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("workspace_id", sa.String(length=64), nullable=True),
        sa.Column("terminal_type", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("lifecycle", sa.String(length=32), nullable=False, server_default="ACTIVE"),
        sa.Column("connection_state", sa.String(length=32), nullable=False, server_default="CONNECTED"),
        sa.Column("execution_capability", sa.String(length=32), nullable=False, server_default="DISABLED"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="READY"),
        sa.Column("session_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("configuration_schema_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("draft_content", sa.Text(), nullable=False, server_default=""),
        sa.Column("scrollback_limit", sa.Integer(), nullable=False, server_default="2000"),
        sa.Column("appearance_options", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("input_options", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_terminal_sessions_owner_order", "terminal_sessions", ["owner_user_id", "session_order"])
    op.create_index("ix_terminal_sessions_owner_type", "terminal_sessions", ["owner_user_id", "terminal_type"])
    op.create_index("ix_terminal_sessions_workspace", "terminal_sessions", ["workspace_id"])

    # 2. terminal_user_preferences
    op.create_table(
        "terminal_user_preferences",
        sa.Column("user_id", sa.String(length=64), primary_key=True),
        sa.Column("font_size", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("font_family", sa.String(length=256), nullable=False, server_default="JetBrains Mono, Fira Code, Menlo, monospace"),
        sa.Column("line_height", sa.Float(), nullable=False, server_default="1.45"),
        sa.Column("scrollback_limit", sa.Integer(), nullable=False, server_default="2000"),
        sa.Column("cursor_style", sa.String(length=32), nullable=False, server_default="BLOCK"),
        sa.Column("word_wrap", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("terminal_height", sa.Integer(), nullable=False, server_default="320"),
        sa.Column("default_tab_type", sa.String(length=32), nullable=False, server_default="ATLAS_CLI"),
        sa.Column("restore_previous_tabs", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("timestamp_display", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # 3. terminal_audit_events
    op.create_table(
        "terminal_audit_events",
        sa.Column("event_id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_terminal_audit_user_time", "terminal_audit_events", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("terminal_audit_events")
    op.drop_table("terminal_user_preferences")
    op.drop_table("terminal_sessions")

