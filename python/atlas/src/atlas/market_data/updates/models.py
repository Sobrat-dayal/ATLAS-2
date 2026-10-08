import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import UUID

from atlas.database import Base


class MarketDataUpdateTarget(Base):
    __tablename__ = "market_data_update_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False, index=True)
    interval = Column(String(32), nullable=False)
    # variant
    adjustment = Column(String(32), nullable=False, default="RAW")
    
    enabled = Column(Boolean, nullable=False, default=True)
    initial_start_at = Column(DateTime(timezone=True), nullable=False)
    cadence_seconds = Column(Integer, nullable=False)
    revision_lookback_seconds = Column(Integer, nullable=False, default=0)
    
    next_run_at = Column(DateTime(timezone=True), nullable=False)
    last_successful_coverage_end_at = Column(DateTime(timezone=True), nullable=True)
    
    provider_override = Column(String(64), nullable=True)
    
    consecutive_failures = Column(Integer, nullable=False, default=0)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_code = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index("ix_market_data_update_targets_due", "enabled", "next_run_at"),
    )

class MarketDataUpdateJob(Base):
    __tablename__ = "market_data_update_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_id = Column(UUID(as_uuid=True), ForeignKey("market_data_update_targets.id"), nullable=False, index=True)
    
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    range_start_at = Column(DateTime(timezone=True), nullable=False)
    range_end_at = Column(DateTime(timezone=True), nullable=False)
    
    provider_override = Column(String(64), nullable=True)
    
    status = Column(String(32), nullable=False)  # queued, running, retry_wait, succeeded, failed, cancelled
    available_at = Column(DateTime(timezone=True), nullable=False)
    
    attempt_count = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False)
    
    lease_owner = Column(String(255), nullable=True)
    lease_expires_at = Column(DateTime(timezone=True), nullable=True)
    heartbeat_at = Column(DateTime(timezone=True), nullable=True)
    
    final_ingestion_run_id = Column(UUID(as_uuid=True), nullable=True)
    final_error_code = Column(String(255), nullable=True)
    final_error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index("ix_market_data_update_jobs_claim", "status", "available_at", "scheduled_for"),
        # One active job per target constraint
        Index(
            "uq_active_job_per_target", 
            "target_id", 
            unique=True, 
            postgresql_where=(status.in_(["queued", "running", "retry_wait"]))
        ),
        # Unique scheduled job
        Index(
            "uq_job_target_scheduled",
            "target_id", "scheduled_for",
            unique=True
        )
    )

class MarketDataUpdateJobAttempt(Base):
    __tablename__ = "market_data_update_job_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("market_data_update_jobs.id"), nullable=False, index=True)
    attempt_number = Column(Integer, nullable=False)
    worker_id = Column(String(255), nullable=False)
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String(32), nullable=False) # running, succeeded, failed, cancelled
    
    ingestion_run_id = Column(UUID(as_uuid=True), ForeignKey("historical_market_data_ingestion_runs.id"), nullable=True)
    error_code = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index("uq_attempt_job_number", "job_id", "attempt_number", unique=True),
    )
