"""SQLAlchemy database models for Stage 123 Terminal Execution Platform."""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from atlas.database import Base


class TerminalExecutionModel(Base):
    """Persisted execution job record."""

    __tablename__ = "terminal_executions"

    execution_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    terminal_session_id = Column(String(64), nullable=False, index=True)
    execution_type = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="CREATED", index=True)
    state_revision = Column(Integer, nullable=False, default=1)
    input_code = Column(Text, nullable=False)
    environment_id = Column(String(64), nullable=True)
    source_id = Column(String(64), nullable=True)
    resource_profile = Column(JSONB, nullable=False, default=dict)
    duration_ms = Column(Float, nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    row_count = Column(Integer, nullable=True)
    stdout_summary = Column(Text, nullable=True)
    tabular_result = Column(JSONB, nullable=True)
    idempotency_key = Column(String(128), nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_requested_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_terminal_executions_owner_status", "owner_user_id", "status"),
        Index("ix_terminal_executions_session", "terminal_session_id"),
        Index("ix_terminal_executions_idempotency", "idempotency_key"),
    )


class TerminalExecutionOutputModel(Base):
    """Chunked streaming output event."""

    __tablename__ = "terminal_execution_outputs"

    output_id = Column(String(64), primary_key=True)
    execution_id = Column(String(64), nullable=False, index=True)
    seq_num = Column(Integer, nullable=False)
    stream_type = Column(String(32), nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (Index("ix_terminal_execution_outputs_exec_seq", "execution_id", "seq_num"),)


class TerminalExecutionAuditModel(Base):
    """Audit log for execution operations, status changes, and permissions."""

    __tablename__ = "terminal_execution_audit_events"

    audit_id = Column(String(64), primary_key=True)
    execution_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    from_status = Column(String(32), nullable=True)
    to_status = Column(String(32), nullable=True)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    timestamp = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_terminal_execution_audit_exec", "execution_id"),
        Index("ix_terminal_execution_audit_user", "user_id"),
    )
