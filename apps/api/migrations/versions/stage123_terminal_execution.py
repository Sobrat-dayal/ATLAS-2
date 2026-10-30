"""stage123_terminal_execution

Revision ID: stage123_terminal_execution
Revises: stage122_terminal_shell
Create Date: 2026-10-30 00:00:00.000000

Stage 123 — Sandboxed Terminal Execution Platform:
- terminal_executions: Persisted execution jobs across Python, SQL, and ATLAS CLI.
- terminal_execution_outputs: Bounded stream events (stdout, stderr, tabular, errors).
- terminal_execution_audit_events: Append-only audit trail for execution lifecycle and permissions.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage123_terminal_execution"
down_revision: Union[str, Sequence[str], None] = "stage122_terminal_shell"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. terminal_executions
    op.create_table(
        "terminal_executions",
        sa.Column("execution_id", sa.String(length=64), primary_key=True),
        sa.Column("owner_user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("terminal_session_id", sa.String(length=64), nullable=False),
        sa.Column("execution_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="CREATED"),
        sa.Column("state_revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("input_code", sa.Text(), nullable=False),
        sa.Column("environment_id", sa.String(length=64), nullable=True),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("resource_profile", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("stdout_summary", sa.Text(), nullable=True),
        sa.Column("tabular_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_requested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_terminal_executions_owner_status",
        "terminal_executions",
        ["owner_user_id", "status"],
    )
    op.create_index(
        "ix_terminal_executions_session",
        "terminal_executions",
        ["terminal_session_id"],
    )
    op.create_index(
        "ix_terminal_executions_idempotency",
        "terminal_executions",
        ["idempotency_key"],
    )

    # 2. terminal_execution_outputs
    op.create_table(
        "terminal_execution_outputs",
        sa.Column("output_id", sa.String(length=64), primary_key=True),
        sa.Column("execution_id", sa.String(length=64), nullable=False),
        sa.Column("seq_num", sa.Integer(), nullable=False),
        sa.Column("stream_type", sa.String(length=32), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_terminal_execution_outputs_exec_seq",
        "terminal_execution_outputs",
        ["execution_id", "seq_num"],
    )

    # 3. terminal_execution_audit_events
    op.create_table(
        "terminal_execution_audit_events",
        sa.Column("audit_id", sa.String(length=64), primary_key=True),
        sa.Column("execution_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_terminal_execution_audit_exec",
        "terminal_execution_audit_events",
        ["execution_id"],
    )
    op.create_index(
        "ix_terminal_execution_audit_user",
        "terminal_execution_audit_events",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("terminal_execution_audit_events")
    op.drop_table("terminal_execution_outputs")
    op.drop_table("terminal_executions")

