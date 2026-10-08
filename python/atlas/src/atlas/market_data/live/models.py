import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Index, Integer
from sqlalchemy.dialects.postgresql import UUID

from atlas.database import Base


class MarketDataLiveQuoteTarget(Base):
    """
    Authoritative state for which instruments should be actively subscribed to
    for live market data quotes.
    """
    __tablename__ = "market_data_live_quote_targets"

    instrument_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), primary_key=True)
    provider_id = Column(String(255), nullable=False)
    
    # Optional variant/exchange specific routing info
    variant = Column(String(255), nullable=True)
    
    is_enabled = Column(Boolean, nullable=False, default=True)
    
    # Freshness policy overrides
    freshness_fresh_until_seconds = Column(Integer, nullable=True)
    freshness_stale_after_seconds = Column(Integer, nullable=True)
    freshness_age_basis = Column(String(50), nullable=True)
    freshness_source_timestamp_fallback = Column(String(50), nullable=True)
    
    # Lease management for concurrent workers
    lease_owner = Column(String(255), nullable=True)
    lease_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_live_quote_targets_lease", "is_enabled", "provider_id", "lease_owner"),
    )
