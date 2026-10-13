"""stage54_tasks_approvals

Revision ID: 9b2c3d4e5f6a
Revises: 8f1a2b3c4d5e
Create Date: 2026-10-13 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9b2c3d4e5f6a"
down_revision: Union[str, Sequence[str], None] = "8f1a2b3c4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -----------------------------------------------------------------------
    # 1. Create user_tasks table
    # -----------------------------------------------------------------------
    op.create_table(
        "user_tasks",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="OPEN", nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("module_id", sa.String(length=64), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["entities.entity_id"],
            ondelete="SET NULL",
            name="fk_user_tasks_entity_id",
        ),
        sa.PrimaryKeyConstraint("task_id", name="pk_user_tasks"),
    )

    op.create_check_constraint(
        "ck_user_tasks_status",
        "user_tasks",
        "status IN ('OPEN', 'COMPLETED', 'CANCELLED')",
    )
    op.create_check_constraint(
        "ck_user_tasks_title_not_empty",
        "user_tasks",
        "length(trim(title)) > 0",
    )
    op.create_index(
        "ix_user_tasks_owner_status_due",
        "user_tasks",
        ["owner_user_id", "status", "due_at"],
    )
    op.create_index(
        "ix_user_tasks_owner_created_id",
        "user_tasks",
        ["owner_user_id", sa.text("created_at DESC"), sa.text("task_id DESC")],
    )
    op.create_index(
        "uq_user_tasks_owner_idempotency",
        "user_tasks",
        ["owner_user_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    # -----------------------------------------------------------------------
    # 2. Create approval_requests table
    # -----------------------------------------------------------------------
    op.create_table(
        "approval_requests",
        sa.Column("approval_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("producer_key", sa.String(length=64), nullable=False),
        sa.Column("action_kind", sa.String(length=64), nullable=False),
        sa.Column("proposal_reference", sa.String(length=256), nullable=False),
        sa.Column("proposal_digest", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("summary", sa.String(length=2000), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="PENDING", nullable=False),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("approval_id", name="pk_approval_requests"),
    )

    op.create_check_constraint(
        "ck_approval_request_status",
        "approval_requests",
        "status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')",
    )
    op.create_index(
        "uq_approval_requests_producer_idempotency",
        "approval_requests",
        ["producer_key", "idempotency_key", "approver_user_id"],
        unique=True,
    )
    op.create_index(
        "ix_approval_requests_approver_status_expires",
        "approval_requests",
        ["approver_user_id", "status", "expires_at"],
    )
    op.create_index(
        "ix_approval_requests_approver_requested",
        "approval_requests",
        ["approver_user_id", sa.text("requested_at DESC"), sa.text("approval_id DESC")],
    )

    # -----------------------------------------------------------------------
    # 3. Create approval_decisions table
    # -----------------------------------------------------------------------
    op.create_table(
        "approval_decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approval_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("decision_idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["approval_id"],
            ["approval_requests.approval_id"],
            ondelete="CASCADE",
            name="fk_approval_decisions_approval_id",
        ),
        sa.PrimaryKeyConstraint("decision_id", name="pk_approval_decisions"),
        sa.UniqueConstraint("approval_id", name="uq_approval_decisions_approval_id"),
    )

    op.create_check_constraint(
        "ck_approval_decision_type",
        "approval_decisions",
        "decision IN ('APPROVE', 'REJECT')",
    )
    op.create_index(
        "uq_approval_decisions_approver_idempotency",
        "approval_decisions",
        ["approver_user_id", "decision_idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("approval_decisions")
    op.drop_table("approval_requests")
    op.drop_table("user_tasks")
