"""SQLAlchemy Declarative Models for Stage 125 ATLAS AI Context Awareness."""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
)

from atlas.database.base import Base


class AiContextPreferencesModel(Base):
    """User preferences for AI Context modes, permissions, and entity pinning."""

    __tablename__ = "ai_context_preferences"

    preference_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, unique=True, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    context_mode = Column(String(32), nullable=False, default="FOCUSED")
    allow_workspace_context = Column(Boolean, nullable=False, default=True)
    allow_portfolio_holdings_context = Column(Boolean, nullable=False, default=False)
    allow_research_drafts_context = Column(Boolean, nullable=False, default=False)
    pinned_context_references = Column(JSON, nullable=False, default=list)
    excluded_context_references = Column(JSON, nullable=False, default=list)
    provider_disclosure_enabled = Column(Boolean, nullable=False, default=True)
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

    __table_args__ = (
        Index("ix_ai_context_prefs_user", "owner_user_id"),
        Index("ix_ai_context_prefs_tenant", "tenant_id"),
    )


class AiContextSourceManifestModel(Base):
    """Immutable audit and provenance record linking a generation run to verified context items."""

    __tablename__ = "ai_context_source_manifests"

    manifest_id = Column(String(64), primary_key=True)
    generation_id = Column(String(64), nullable=False, unique=True, index=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    context_mode = Column(String(32), nullable=False, default="FOCUSED")
    source_items = Column(JSON, nullable=False, default=list)
    total_estimated_tokens = Column(Integer, nullable=False, default=0)
    assembled_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    extra_metadata = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_ai_context_manifests_gen", "generation_id"),
        Index("ix_ai_context_manifests_user", "owner_user_id"),
    )


class AiContextAuditEventModel(Base):
    """Append-only audit trail for context queries, overrides, and resolution events."""

    __tablename__ = "ai_context_audit_events"

    audit_id = Column(String(64), primary_key=True)
    event_type = Column(String(64), nullable=False, index=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_ai_context_audit_type_user", "event_type", "owner_user_id"),
        Index("ix_ai_context_audit_created", "created_at"),
    )
