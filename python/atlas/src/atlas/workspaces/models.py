"""
Canonical Dataclass Models for ATLAS Workspaces Architecture (Stage 120).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from atlas.workspaces.enums import (
    LayoutNodeType,
    PanelTypeId,
    SplitOrientation,
    WorkspaceAuditEventType,
    WorkspaceStatus,
    WorkspaceType,
)


@dataclass
class LayoutNode:
    """Base class for nodes in the layout tree."""

    node_id: str
    node_type: LayoutNodeType = LayoutNodeType.PANEL

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class SplitNode(LayoutNode):
    """Container dividing its area into adjacent sub-regions."""

    node_type: LayoutNodeType = LayoutNodeType.SPLIT
    orientation: SplitOrientation = SplitOrientation.HORIZONTAL
    children: list["LayoutNode"] = field(default_factory=list)
    size_ratios: list[float] = field(default_factory=list)
    min_size_rules: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "orientation": self.orientation.value,
            "children": [c.to_dict() for c in self.children],
            "size_ratios": self.size_ratios,
            "min_size_rules": self.min_size_rules,
        }


@dataclass
class TabStackNode(LayoutNode):
    """Container holding multiple panel instances behind a tab bar."""

    node_type: LayoutNodeType = LayoutNodeType.TAB_STACK
    panel_instance_ids: list[str] = field(default_factory=list)
    active_panel_instance_id: str = ""

    def __post_init__(self):
        if not self.active_panel_instance_id and self.panel_instance_ids:
            self.active_panel_instance_id = self.panel_instance_ids[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "panel_instance_ids": self.panel_instance_ids,
            "active_panel_instance_id": self.active_panel_instance_id,
        }


@dataclass
class PanelNode(LayoutNode):
    """Leaf node hosting a single panel instance."""

    node_type: LayoutNodeType = LayoutNodeType.PANEL
    panel_instance_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "panel_instance_id": self.panel_instance_id,
        }


@dataclass
class WorkspacePanelInstance:
    """An instantiated panel inside a workspace."""

    panel_instance_id: str
    workspace_id: str
    panel_type_id: PanelTypeId
    title_override: Optional[str] = None
    configuration: dict[str, Any] = field(default_factory=dict)
    link_group_id: Optional[str] = None
    independent_mode: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel_instance_id": self.panel_instance_id,
            "workspace_id": self.workspace_id,
            "panel_type_id": self.panel_type_id.value,
            "title_override": self.title_override,
            "configuration": self.configuration,
            "link_group_id": self.link_group_id,
            "independent_mode": self.independent_mode,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class WorkspaceLinkGroup:
    """Channel for synchronizing state (e.g. ticker, date, portfolio) across panels."""

    link_group_id: str
    workspace_id: str
    name: str
    color: str = "#3b82f6"  # Blue default
    context: dict[str, Any] = field(default_factory=dict)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "link_group_id": self.link_group_id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "color": self.color,
            "context": self.context,
            "version": self.version,
        }


@dataclass
class WorkspaceLayout:
    """Composite layout definition containing tree and panels."""

    root_node: LayoutNode
    panel_instances: dict[str, WorkspacePanelInstance] = field(default_factory=dict)
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_node": self.root_node.to_dict(),
            "panel_instances": {pid: p.to_dict() for pid, p in self.panel_instances.items()},
            "schema_version": self.schema_version,
        }


@dataclass
class Workspace:
    """Core domain model representing a financial analytical workspace/desk."""

    workspace_id: str
    owner_user_id: str
    name: str
    description: Optional[str] = None
    organization_id: Optional[str] = None
    workspace_type: WorkspaceType = WorkspaceType.CUSTOM
    template_origin_id: Optional[str] = None
    layout_schema_version: int = 1
    layout_revision: int = 1
    is_default: bool = False
    is_favorite: bool = False
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    settings: dict[str, Any] = field(default_factory=lambda: {"autosave": True, "density": "dense"})
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_opened_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "owner_user_id": self.owner_user_id,
            "organization_id": self.organization_id,
            "name": self.name,
            "description": self.description,
            "workspace_type": self.workspace_type.value,
            "template_origin_id": self.template_origin_id,
            "layout_schema_version": self.layout_schema_version,
            "layout_revision": self.layout_revision,
            "is_default": self.is_default,
            "is_favorite": self.is_favorite,
            "status": self.status.value,
            "settings": self.settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_opened_at": self.last_opened_at.isoformat(),
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }


@dataclass
class WorkspaceTemplate:
    """Canonical pre-configured desk template."""

    template_id: str
    name: str
    description: str
    category: str
    layout_definition: dict[str, Any]
    panel_definitions: list[dict[str, Any]]
    required_capabilities: list[str] = field(default_factory=list)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "layout_definition": self.layout_definition,
            "panel_definitions": self.panel_definitions,
            "required_capabilities": self.required_capabilities,
            "version": self.version,
        }


@dataclass
class WorkspaceLayoutRevision:
    """Historical snapshot of a workspace layout revision."""

    revision_id: str
    workspace_id: str
    revision_number: int
    layout_payload: dict[str, Any]
    created_by: str
    payload_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "revision_id": self.revision_id,
            "workspace_id": self.workspace_id,
            "revision_number": self.revision_number,
            "layout_payload": self.layout_payload,
            "created_by": self.created_by,
            "payload_hash": self.payload_hash,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class WorkspaceAuditEvent:
    """Durable audit event for workspace modifications."""

    event_id: str
    workspace_id: str
    user_id: str
    event_type: WorkspaceAuditEventType
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "event_type": self.event_type.value,
            "details": self.details,
            "created_at": self.created_at.isoformat(),
        }
