"""
SQLAlchemy Declarative Database Models for ATLAS Workspaces Architecture (Stage 120).
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
    Text,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class WorkspaceModel(Base):
    """Stores top-level workspace metadata and lifecycle status."""

    __tablename__ = "workspaces"

    workspace_id = Column(String(64), primary_key=True)
    owner_user_id = Column(String(64), nullable=False, index=True)
    organization_id = Column(String(64), nullable=True, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    workspace_type = Column(String(32), nullable=False, default="CUSTOM")
    template_origin_id = Column(String(64), nullable=True)
    layout_schema_version = Column(Integer, nullable=False, default=1)
    layout_revision = Column(Integer, nullable=False, default=1)
    is_default = Column(Boolean, nullable=False, default=False)
    is_favorite = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False, default="ACTIVE", index=True)
    settings = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_opened_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_workspaces_user_status", "owner_user_id", "status"),
        Index("ix_workspaces_user_default", "owner_user_id", "is_default"),
    )


class WorkspaceLayoutRevisionModel(Base):
    """Historical record of layout versions for audit and recovery."""

    __tablename__ = "workspace_layout_revisions"

    revision_id = Column(String(64), primary_key=True)
    workspace_id = Column(
        String(64),
        ForeignKey("workspaces.workspace_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision_number = Column(Integer, nullable=False)
    layout_payload = Column(JSON, nullable=False)
    created_by = Column(String(64), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ws_layout_rev_ws_num", "workspace_id", "revision_number", unique=True),
    )


class WorkspacePanelInstanceModel(Base):
    """Individual panel instance registered to a workspace."""

    __tablename__ = "workspace_panel_instances"

    panel_instance_id = Column(String(64), primary_key=True)
    workspace_id = Column(
        String(64),
        ForeignKey("workspaces.workspace_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    panel_type_id = Column(String(64), nullable=False)
    title_override = Column(String(128), nullable=True)
    configuration = Column(JSON, nullable=False, default=dict)
    link_group_id = Column(String(64), nullable=True)
    independent_mode = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkspaceLinkGroupModel(Base):
    """Link group channel for cross-panel state synchronization."""

    __tablename__ = "workspace_link_groups"

    link_group_id = Column(String(64), primary_key=True)
    workspace_id = Column(
        String(64),
        ForeignKey("workspaces.workspace_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(64), nullable=False)
    color = Column(String(32), nullable=False, default="#3b82f6")
    context = Column(JSON, nullable=False, default=dict)
    version = Column(Integer, nullable=False, default=1)


class WorkspaceTemplateModel(Base):
    """Persistent template definitions."""

    __tablename__ = "workspace_templates"

    template_id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    layout_definition = Column(JSON, nullable=False)
    panel_definitions = Column(JSON, nullable=False)
    required_capabilities = Column(JSON, nullable=False, default=list)
    version = Column(Integer, nullable=False, default=1)


class WorkspaceAuditEventModel(Base):
    """Append-only audit log for workspace state modifications."""

    __tablename__ = "workspace_audit_events"

    event_id = Column(String(64), primary_key=True)
    workspace_id = Column(
        String(64),
        ForeignKey("workspaces.workspace_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
