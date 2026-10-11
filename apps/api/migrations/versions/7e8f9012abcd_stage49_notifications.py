"""stage49_notifications

Revision ID: 7e8f9012abcd
Revises: 6cf729b2c092
Create Date: 2026-10-12 01:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7e8f9012abcd"
down_revision: Union[str, Sequence[str], None] = "6cf729b2c092"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create notifications table
    op.create_table(
        "notifications",
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("message", sa.String(length=2000), nullable=False),
        sa.Column("producer_key", sa.String(length=128), nullable=False),
        sa.Column("dedupe_key", sa.String(length=256), nullable=True),
        sa.Column("action_kind", sa.String(length=32), nullable=False, server_default="none"),
        sa.Column("action_route", sa.String(length=256), nullable=True),
        sa.Column("action_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["action_entity_id"],
            ["entities.entity_id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("notification_id"),
    )

    # 2. Check Constraints
    op.create_check_constraint(
        "ck_notifications_category",
        "notifications",
        "category IN ('general', 'system', 'security', 'data', 'market', 'research', 'account')",
    )
    op.create_check_constraint(
        "ck_notifications_severity",
        "notifications",
        "severity IN ('info', 'success', 'warning', 'error')",
    )
    op.create_check_constraint(
        "ck_notifications_action_kind",
        "notifications",
        "action_kind IN ('none', 'internal_route', 'entity_route')",
    )
    op.create_check_constraint(
        "ck_notifications_action_consistency",
        "notifications",
        "(action_kind = 'none' AND action_route IS NULL AND action_entity_id IS NULL) OR "
        "(action_kind = 'internal_route' AND action_route IS NOT NULL AND action_entity_id IS NULL) OR "
        "(action_kind = 'entity_route' AND action_route IS NOT NULL AND action_entity_id IS NOT NULL)",
    )

    # 3. Indexes
    op.create_index(
        "ix_notifications_recipient_pagination",
        "notifications",
        ["recipient_user_id", sa.text("created_at DESC"), sa.text("notification_id DESC")],
    )
    op.create_index(
        "ix_notifications_recipient_unread",
        "notifications",
        ["recipient_user_id", sa.text("created_at DESC")],
        postgresql_where=sa.text("read_at IS NULL AND archived_at IS NULL"),
    )
    op.create_index(
        "uq_notifications_recipient_producer_dedupe",
        "notifications",
        ["recipient_user_id", "producer_key", "dedupe_key"],
        unique=True,
        postgresql_where=sa.text("dedupe_key IS NOT NULL"),
    )
    op.create_index(
        "ix_notifications_recipient_archived",
        "notifications",
        ["recipient_user_id", sa.text("archived_at DESC")],
        postgresql_where=sa.text("archived_at IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("notifications")
