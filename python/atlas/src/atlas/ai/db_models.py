"""SQLAlchemy Declarative Models for Stage 124 AI Assistant V1."""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from atlas.database.base import Base


class AiConversationModel(Base):
    """Persisted chat conversation thread."""

    __tablename__ = "ai_conversations"

    conversation_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    model_id = Column(String(64), nullable=False, default="atlas-intelligence-v1")
    provider = Column(String(64), nullable=False, default="atlas")
    system_prompt_override = Column(Text, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    is_pinned = Column(Boolean, nullable=False, default=False)
    pinned_at = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    extra_metadata = Column("metadata", JSON, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_message_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_ai_conversations_user_updated", "owner_user_id", "updated_at"),
        Index("ix_ai_conversations_user_archived", "owner_user_id", "is_archived"),
        Index("ix_ai_conversations_user_pinned", "owner_user_id", "is_pinned"),
    )


class AiMessageModel(Base):
    """Persisted user or assistant message turn."""

    __tablename__ = "ai_messages"

    message_id = Column(String(64), primary_key=True)
    conversation_id = Column(
        String(64),
        ForeignKey("ai_conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=True)
    role = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="COMPLETED")
    content = Column(Text, nullable=False)
    route_context = Column(JSON, nullable=True)
    token_count = Column(Integer, nullable=False, default=0)
    generation_run_id = Column(String(64), nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSON, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (Index("ix_ai_messages_conv_created", "conversation_id", "created_at"),)


class AiGenerationRunModel(Base):
    """Execution record for each LLM response generation."""

    __tablename__ = "ai_generation_runs"

    generation_id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), nullable=False, index=True)
    user_message_id = Column(String(64), nullable=False)
    assistant_message_id = Column(String(64), nullable=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="RUNNING")
    model_id = Column(String(64), nullable=False)
    provider = Column(String(64), nullable=False)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Float, nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)


class AiAssistantUserPreferencesModel(Base):
    """User preferences for the AI Assistant overlay and behaviour."""

    __tablename__ = "ai_assistant_user_preferences"

    preference_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, unique=True, index=True)
    tenant_id = Column(String(64), nullable=True)
    default_model_id = Column(String(64), nullable=False, default="atlas-intelligence-v1")
    temperature = Column(Float, nullable=False, default=0.2)
    send_on_enter = Column(Boolean, nullable=False, default=True)
    sound_enabled = Column(Boolean, nullable=False, default=False)
    overlay_dock_side = Column(String(16), nullable=False, default="right")
    overlay_width_px = Column(Integer, nullable=False, default=420)
    extra_metadata = Column("metadata", JSON, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AiConversationAuditEventModel(Base):
    """Audit log for conversation lifecycle events."""

    __tablename__ = "ai_conversation_audit_events"

    audit_id = Column(String(64), primary_key=True)
    conversation_id = Column(String(64), nullable=True, index=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
