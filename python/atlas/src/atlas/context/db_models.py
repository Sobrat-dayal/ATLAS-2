"""
SQLAlchemy Declarative Models for ATLAS Stage 121: Global Workspace Linking.
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)

from atlas.database import Base


class GlobalContextChannelModel(Base):
    """Link Channel entity allowing cross-panel & cross-workspace context synchronization."""

    __tablename__ = "global_context_channels"

    channel_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    workspace_id = Column(String(64), nullable=True, index=True)
    scope = Column(String(32), nullable=False, default="WORKSPACE")
    name = Column(String(64), nullable=False)
    display_color_token = Column(String(32), nullable=False, default="#3b82f6")
    enabled = Column(Boolean, nullable=False, default=True)
    supported_dimensions = Column(JSON, nullable=False, default=list)
    context_snapshot = Column(JSON, nullable=False, default=dict)
    revision = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class GlobalContextChannelMembershipModel(Base):
    """Registration of a panel instance into a specific link channel with directional dimensions."""

    __tablename__ = "global_context_channel_memberships"

    subscription_id = Column(String(64), primary_key=True)
    channel_id = Column(
        String(64),
        ForeignKey("global_context_channels.channel_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    panel_instance_id = Column(String(64), nullable=False, index=True)
    mode = Column(String(32), nullable=False, default="BIDIRECTIONAL")
    inbound_dimensions = Column(JSON, nullable=False, default=list)
    outbound_dimensions = Column(JSON, nullable=False, default=list)
    active = Column(Boolean, nullable=False, default=True)
    priority_policy = Column(String(32), nullable=False, default="NORMAL")

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ctx_channel_panel_unique", "channel_id", "panel_instance_id", unique=True),
    )


class GlobalContextSnapshotModel(Base):
    """Historical persisted snapshot of a link channel's financial context."""

    __tablename__ = "global_context_snapshots"

    snapshot_id = Column(String(64), primary_key=True)
    channel_id = Column(
        String(64),
        ForeignKey("global_context_channels.channel_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision = Column(Integer, nullable=False)
    context_payload = Column(JSON, nullable=False)
    created_by = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class GlobalContextAuditEventModel(Base):
    """Append-only audit trail for context channel lifecycle and security events."""

    __tablename__ = "global_context_audit_events"

    audit_id = Column(String(64), primary_key=True)
    channel_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
