"""stage53_user_activity

Revision ID: 8f1a2b3c4d5e
Revises: 7e8f9012abcd
Create Date: 2026-10-13 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8f1a2b3c4d5e"
down_revision: Union[str, Sequence[str], None] = "7e8f9012abcd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create user_activity_events table
    op.create_table(
        "user_activity_events",
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("module_id", sa.String(length=64), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["entity_id"],
            ["entities.entity_id"],
            ondelete="SET NULL",
            name="fk_user_activity_entity_id",
        ),
        sa.PrimaryKeyConstraint("activity_id", name="pk_user_activity_events"),
    )

    # 2. Check Constraints
    op.create_check_constraint(
        "ck_user_activity_event_type",
        "user_activity_events",
        "event_type IN ('MODULE_OPENED', 'ENTITY_SELECTED')",
    )
    op.create_check_constraint(
        "ck_user_activity_payload_consistency",
        "user_activity_events",
        "(event_type = 'MODULE_OPENED' AND module_id IS NOT NULL AND entity_id IS NULL) OR "
        "(event_type = 'ENTITY_SELECTED' AND entity_id IS NOT NULL)",
    )

    # 3. Indexes
    op.create_index(
        "ix_user_activity_events_user_occurred_id",
        "user_activity_events",
        ["user_id", sa.text("occurred_at DESC"), sa.text("activity_id DESC")],
    )
    op.create_index(
        "uq_user_activity_events_user_client_event",
        "user_activity_events",
        ["user_id", "client_event_id"],
        unique=True,
    )
    op.create_index(
        "ix_user_activity_events_occurred_at",
        "user_activity_events",
        ["occurred_at"],
    )


def downgrade() -> None:
    op.drop_table("user_activity_events")
