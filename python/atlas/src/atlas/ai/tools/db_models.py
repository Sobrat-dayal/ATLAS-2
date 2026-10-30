"""SQLAlchemy ORM models for Stage 126: ATLAS AI Tool Gateway.

Defines persistence schema for tool execution calls, human approval requests,
user tool preferences, and audit events.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from atlas.infrastructure.database import Base


class AiToolCallModel(Base):
    """Stores record of every proposed and executed AI tool invocation."""

    __tablename__ = "ai_tool_calls"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    tool_id = Column(String(128), nullable=False, index=True)
    tool_version = Column(String(32), default="1.0.0", nullable=False)
    status = Column(String(32), nullable=False, index=True)
    arguments = Column(JSONB, nullable=False, default=dict)
    normalized_arguments_hash = Column(String(64), nullable=False, index=True)
    result = Column(JSONB, nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    approval_class = Column(String(32), default="NO_APPROVAL_REQUIRED", nullable=False)
    approval_request_id = Column(String(64), nullable=True)
    generation_run_id = Column(String(64), nullable=True, index=True)
    conversation_id = Column(String(64), nullable=True, index=True)
    tenant_id = Column(String(64), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_ai_tool_calls_user_created", "user_id", "created_at"),
        Index("ix_ai_tool_calls_tool_status", "tool_id", "status"),
    )


class AiToolApprovalRequestModel(Base):
    """Stores human approval tokens binding authorized operations to user decisions."""

    __tablename__ = "ai_tool_approval_requests"

    id = Column(String(64), primary_key=True)
    tool_call_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    tool_id = Column(String(128), nullable=False, index=True)
    approval_class = Column(String(32), nullable=False)
    normalized_arguments_hash = Column(String(64), nullable=False)
    arguments_summary = Column(JSONB, nullable=False, default=dict)
    status = Column(String(32), default="PENDING", nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    decision_reason = Column(Text, nullable=True)
    tenant_id = Column(String(64), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AiToolPreferencesModel(Base):
    """User preferences for tool enablement, discovery, and auto-approval."""

    __tablename__ = "ai_tool_preferences"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), unique=True, nullable=False, index=True)
    enabled_tools = Column(JSONB, default=list, nullable=False)
    disabled_tools = Column(JSONB, default=list, nullable=False)
    auto_approve_read_only = Column(Boolean, default=True, nullable=False)
    require_approval_for_sensitive = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AiToolAuditEventModel(Base):
    """Append-only audit trail recording every tool execution and approval decision."""

    __tablename__ = "ai_tool_audit_events"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    tool_id = Column(String(128), nullable=False, index=True)
    tool_call_id = Column(String(64), nullable=True, index=True)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False, default=dict)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
