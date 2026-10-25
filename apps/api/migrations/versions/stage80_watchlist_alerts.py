"""stage80_watchlist_alerts

Revision ID: stage80_watchlist_alerts
Revises: stage77_watchlist_columns
Create Date: 2026-10-25 00:00:00.000000

Stage 80 — Watchlist Alerts V1: Persistent Financial Monitoring Rules, Realtime Price Thresholds,
Qualified Percentage-Change Conditions, Event-Driven Alert Evaluation, Durable Notification Delivery,
Trigger History, Cooldowns, Deduplication, Entitlement Enforcement and Production-Grade Alert Lifecycle Management.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage80_watchlist_alerts"
down_revision: Union[str, Sequence[str], None] = "stage77_watchlist_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create `watchlist_alert_rules` table
    op.create_table(
        "watchlist_alert_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column(
            "watchlist_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlists.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "watchlist_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlist_items.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "instrument_entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column("market_series_identity", sa.String(128), nullable=False),
        sa.Column("symbol", sa.String(64), nullable=False),
        sa.Column("rule_type", sa.String(64), nullable=False),
        sa.Column("rule_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("quote_measure", sa.String(32), nullable=False),
        sa.Column("comparison_operator", sa.String(16), nullable=False),
        sa.Column("threshold_decimal", sa.Numeric(28, 8), nullable=False),
        sa.Column("threshold_unit", sa.String(32), nullable=False),
        sa.Column("reference_methodology", sa.String(64), nullable=True),
        sa.Column("recurrence_policy", sa.String(32), nullable=False, server_default="ONE_SHOT"),
        sa.Column("cooldown_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("state", sa.String(32), nullable=False, server_default="ENABLED"),
        sa.Column("revision", sa.BigInteger(), nullable=False, server_default="1"),
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
    )

    op.create_index(
        "ix_alert_rules_owner_enabled",
        "watchlist_alert_rules",
        ["owner_user_id", "enabled"],
    )
    op.create_index(
        "ix_alert_rules_series_measure",
        "watchlist_alert_rules",
        ["market_series_identity", "quote_measure", "enabled"],
    )
    op.create_index(
        "ix_alert_rules_watchlist",
        "watchlist_alert_rules",
        ["watchlist_id"],
    )
    op.create_index(
        "ix_alert_rules_item",
        "watchlist_alert_rules",
        ["watchlist_item_id"],
    )

    # 2. Create `watchlist_alert_evaluation_state` table
    op.create_table(
        "watchlist_alert_evaluation_state",
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlist_alert_rules.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("rule_revision", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column(
            "evaluation_status",
            sa.String(32),
            nullable=False,
            server_default="WAITING_FOR_BASELINE",
        ),
        sa.Column("armed_side", sa.String(16), nullable=True),
        sa.Column("last_qualified_value", sa.Numeric(28, 8), nullable=True),
        sa.Column("last_qualified_observation_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_qualified_observation_identity", sa.String(128), nullable=True),
        sa.Column("source_sequence_context", sa.String(128), nullable=True),
        sa.Column("last_trigger_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cooldown_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "baseline_established",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # 3. Create `watchlist_alert_triggers` table
    op.create_table(
        "watchlist_alert_triggers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "alert_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlist_alert_rules.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("rule_revision", sa.BigInteger(), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("watchlist_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("watchlist_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("instrument_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("market_series_identity", sa.String(128), nullable=False),
        sa.Column("symbol", sa.String(64), nullable=False),
        sa.Column("event_identity", sa.String(128), nullable=False),
        sa.Column("observation_value", sa.Numeric(28, 8), nullable=False),
        sa.Column("threshold_value", sa.Numeric(28, 8), nullable=False),
        sa.Column("quote_measure", sa.String(32), nullable=False),
        sa.Column("rule_type", sa.String(64), nullable=False),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("venue", sa.String(64), nullable=True),
        sa.Column("observation_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trigger_dedup_key", sa.String(256), nullable=False, unique=True),
        sa.Column(
            "notification_status",
            sa.String(32),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notification_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_alert_triggers_owner_time",
        "watchlist_alert_triggers",
        ["owner_user_id", "created_at"],
    )
    op.create_index(
        "ix_alert_triggers_alert_time",
        "watchlist_alert_triggers",
        ["alert_id", "created_at"],
    )

    # 4. Create `watchlist_alert_notification_outbox` table
    op.create_table(
        "watchlist_alert_notification_outbox",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "trigger_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("watchlist_alert_triggers.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("alert_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="5"),
        sa.Column(
            "next_attempt_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
    )

    op.create_index(
        "ix_alert_outbox_status_attempt",
        "watchlist_alert_notification_outbox",
        ["status", "next_attempt_at"],
    )


def downgrade() -> None:
    op.drop_table("watchlist_alert_notification_outbox")
    op.drop_table("watchlist_alert_triggers")
    op.drop_table("watchlist_alert_evaluation_state")
    op.drop_table("watchlist_alert_rules")
