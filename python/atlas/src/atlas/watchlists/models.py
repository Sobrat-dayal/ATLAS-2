"""SQLAlchemy storage models for Watchlists V1 (Stage 76)."""

import datetime
import uuid
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas.database.base import Base


class Watchlist(Base):
    """
    Authoritative database table representing a user-owned Watchlist.
    """

    __tablename__ = "watchlists"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    revision: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1, server_default="1")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[List["WatchlistItem"]] = relationship(
        "WatchlistItem",
        back_populates="watchlist",
        cascade="all, delete-orphan",
        order_by="WatchlistItem.position",
        lazy="selectin",
    )

    column_preference: Mapped[Optional["WatchlistColumnPreference"]] = relationship(
        "WatchlistColumnPreference",
        back_populates="watchlist",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_watchlists_owner_updated", "owner_user_id", "updated_at"),
        UniqueConstraint(
            "owner_user_id", "normalized_name", name="uq_watchlists_owner_normalized_name"
        ),
    )


class WatchlistItem(Base):
    """
    Membership record linking a watchlist to a canonical financial instrument.
    """

    __tablename__ = "watchlist_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    watchlist_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    instrument_entity_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("financial_instruments.entity_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    market_series_id: Mapped[str] = mapped_column(
        String(128), nullable=False, default="", server_default=""
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")

    __table_args__ = (
        Index("ix_watchlist_items_watchlist_position", "watchlist_id", "position"),
        UniqueConstraint(
            "watchlist_id",
            "instrument_entity_id",
            "market_series_id",
            name="uq_watchlist_items_membership",
        ),
    )


class WatchlistColumnPreference(Base):
    """
    Authoritative database table storing per-watchlist column configuration preferences.
    """

    __tablename__ = "watchlist_column_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    watchlist_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("watchlists.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    configuration_schema_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    revision: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1, server_default="1")
    configuration_jsonb: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="column_preference")
