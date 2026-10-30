"""SQLAlchemy declarative database models for Stage 122 Terminal Shell."""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
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


class TerminalSessionModel(Base):
    """Persisted terminal session record."""

    __tablename__ = "terminal_sessions"

    session_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    terminal_type = Column(String(32), nullable=False, index=True)
    display_name = Column(String(128), nullable=False)
    lifecycle = Column(String(32), nullable=False, default="ACTIVE")
    connection_state = Column(String(32), nullable=False, default="CONNECTED")
    execution_capability = Column(String(32), nullable=False, default="DISABLED")
    status = Column(String(32), nullable=False, default="READY")
    session_order = Column(Integer, nullable=False, default=0)
    configuration_schema_version = Column(Integer, nullable=False, default=1)
    version = Column(BigInteger, nullable=False, default=1)
    draft_content = Column(Text, nullable=False, default="")
    scrollback_limit = Column(Integer, nullable=False, default=2000)
    appearance_options = Column(JSONB, nullable=False, default=dict)
    input_options = Column(JSONB, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_active_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    closed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_terminal_sessions_owner_order", "owner_user_id", "session_order"),
        Index("ix_terminal_sessions_owner_type", "owner_user_id", "terminal_type"),
    )


class TerminalUserPreferencesModel(Base):
    """User-level persistent terminal UI and editor preferences."""

    __tablename__ = "terminal_user_preferences"

    user_id = Column(String(64), primary_key=True)
    font_size = Column(Integer, nullable=False, default=12)
    font_family = Column(
        String(256), nullable=False, default="JetBrains Mono, Fira Code, Menlo, monospace"
    )
    line_height = Column(Float, nullable=False, default=1.45)
    scrollback_limit = Column(Integer, nullable=False, default=2000)
    cursor_style = Column(String(32), nullable=False, default="BLOCK")
    word_wrap = Column(Boolean, nullable=False, default=True)
    terminal_height = Column(Integer, nullable=False, default=320)
    default_tab_type = Column(String(32), nullable=False, default="ATLAS_CLI")
    restore_previous_tabs = Column(Boolean, nullable=False, default=True)
    timestamp_display = Column(Boolean, nullable=False, default=True)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class TerminalAuditEventModel(Base):
    """Append-only audit trail for terminal operations and lifecycle changes."""

    __tablename__ = "terminal_audit_events"

    event_id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    session_id = Column(String(64), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    payload = Column(JSONB, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (Index("ix_terminal_audit_user_time", "user_id", "created_at"),)
