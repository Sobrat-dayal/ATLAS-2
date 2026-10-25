"""SQLAlchemy storage models for Watchlist Alerts V1 (Stage 80)."""

import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas.database.base import Base


class WatchlistAlertRule(Base):
    """
    Authoritative database table representing a user-defined financial alert rule.
    """

    __tablename__ = "watchlist_alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    watchlist_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    watchlist_item_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlist_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    market_series_identity: Mapped[str] = mapped_column(String(128), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    quote_measure: Mapped[str] = mapped_column(String(32), nullable=False)
    comparison_operator: Mapped[str] = mapped_column(String(16), nullable=False)

    threshold_decimal: Mapped[float] = mapped_column(Numeric(28, 8), nullable=False)
    threshold_unit: Mapped[str] = mapped_column(String(32), nullable=False)
    reference_methodology: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    recurrence_policy: Mapped[str] = mapped_column(
        String(32), nullable=False, default="ONE_SHOT", server_default="ONE_SHOT"
    )
    cooldown_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="ENABLED", server_default="ENABLED"
    )
    revision: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=1, server_default="1"
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    evaluation_state: Mapped[Optional["WatchlistAlertEvaluationState"]] = relationship(
        "WatchlistAlertEvaluationState",
        back_populates="alert",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    triggers: Mapped[list["WatchlistAlertTrigger"]] = relationship(
        "WatchlistAlertTrigger",
        back_populates="alert",
        cascade="all, delete-orphan",
        order_by="WatchlistAlertTrigger.created_at.desc()",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_alert_rules_owner_enabled", "owner_user_id", "enabled"),
        Index("ix_alert_rules_series_measure", "market_series_identity", "quote_measure", "enabled"),
        Index("ix_alert_rules_watchlist", "watchlist_id"),
        Index("ix_alert_rules_item", "watchlist_item_id"),
    )


class WatchlistAlertEvaluationState(Base):
    """
    Authoritative state tracking for server-side alert evaluation (crossing, baseline, cooldown).
    """

    __tablename__ = "watchlist_alert_evaluation_state"

    alert_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlist_alert_rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    rule_revision: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=1, server_default="1"
    )
    evaluation_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="WAITING_FOR_BASELINE",
        server_default="WAITING_FOR_BASELINE",
    )
    armed_side: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    last_qualified_value: Mapped[Optional[float]] = mapped_column(Numeric(28, 8), nullable=True)
    last_qualified_observation_time: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_qualified_observation_identity: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    source_sequence_context: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_trigger_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cooldown_until: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    baseline_established: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    alert: Mapped["WatchlistAlertRule"] = relationship(
        "WatchlistAlertRule", back_populates="evaluation_state"
    )


class WatchlistAlertTrigger(Base):
    """
    Immutable audit record of a triggered alert event.
    """

    __tablename__ = "watchlist_alert_triggers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlist_alert_rules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_revision: Mapped[int] = mapped_column(BigInteger, nullable=False)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    watchlist_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    watchlist_item_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    instrument_entity_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    market_series_identity: Mapped[str] = mapped_column(String(128), nullable=False)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    event_identity: Mapped[str] = mapped_column(String(128), nullable=False)
    observation_value: Mapped[float] = mapped_column(Numeric(28, 8), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Numeric(28, 8), nullable=False)
    quote_measure: Mapped[str] = mapped_column(String(32), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    venue: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    observation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    evaluated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    trigger_dedup_key: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)

    notification_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING"
    )
    notification_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    notification_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    alert: Mapped["WatchlistAlertRule"] = relationship("WatchlistAlertRule", back_populates="triggers")

    __table_args__ = (
        Index("ix_alert_triggers_owner_time", "owner_user_id", "created_at"),
        Index("ix_alert_triggers_alert_time", "alert_id", "created_at"),
        UniqueConstraint("trigger_dedup_key", name="uq_watchlist_alert_triggers_dedup"),
    )


class WatchlistAlertNotificationOutbox(Base):
    """
    Transactional outbox for reliable, asynchronous notification dispatch to Stage 49.
    """

    __tablename__ = "watchlist_alert_notification_outbox"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trigger_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlist_alert_triggers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default="PENDING"
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=5, server_default="5")
    next_attempt_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_attempt_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_alert_outbox_status_attempt", "status", "next_attempt_at"),
    )
