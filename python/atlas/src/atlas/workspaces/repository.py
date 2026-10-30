"""
Thread-safe Repository for ATLAS Workspaces Architecture (Stage 120).
"""

import hashlib
import json
import threading
import uuid
from datetime import datetime
from typing import Any, Optional

from atlas.workspaces.enums import (
    PanelTypeId,
    SplitOrientation,
    WorkspaceAuditEventType,
    WorkspaceSortOption,
    WorkspaceStatus,
    WorkspaceType,
)
from atlas.workspaces.errors import (
    WorkspaceAccessDeniedError,
    WorkspaceLayoutRevisionConflictError,
    WorkspaceLinkGroupNotFoundError,
    WorkspaceNameInvalidError,
    WorkspaceNotFoundError,
    WorkspacePanelNotFoundError,
)
from atlas.workspaces.layout_validator import (
    create_safe_recovery_layout,
    parse_layout_node,
    validate_layout_tree,
)
from atlas.workspaces.models import (
    LayoutNode,
    PanelNode,
    SplitNode,
    TabStackNode,
    Workspace,
    WorkspaceAuditEvent,
    WorkspaceLayout,
    WorkspaceLayoutRevision,
    WorkspaceLinkGroup,
    WorkspacePanelInstance,
)
from atlas.workspaces.panel_registry import get_panel_type_definition
from atlas.workspaces.templates import get_workspace_template


class WorkspaceRepository:
    """Thread-safe in-memory and persistence-ready repository for Workspaces."""

    def __init__(self):
        self._lock = threading.RLock()
        self._workspaces: dict[str, Workspace] = {}
        self._layouts: dict[str, WorkspaceLayout] = {}
        self._link_groups: dict[str, list[WorkspaceLinkGroup]] = {}
        self._revisions: dict[str, list[WorkspaceLayoutRevision]] = {}
        self._audit_events: list[WorkspaceAuditEvent] = []

    def create_workspace(
        self,
        owner_user_id: str,
        name: str,
        description: Optional[str] = None,
        workspace_type: WorkspaceType = WorkspaceType.CUSTOM,
        template_origin_id: Optional[str] = None,
        initial_layout: Optional[dict[str, Any]] = None,
        organization_id: Optional[str] = None,
    ) -> Workspace:
        """Creates and stores a new workspace."""
        clean_name = (name or "").strip()
        if not clean_name:
            raise WorkspaceNameInvalidError("Workspace name cannot be empty.")
        if len(clean_name) > 100:
            raise WorkspaceNameInvalidError("Workspace name cannot exceed 100 characters.")

        if template_origin_id and workspace_type == WorkspaceType.CUSTOM:
            workspace_type = WorkspaceType.TEMPLATE_DERIVED

        workspace_id = f"ws_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        with self._lock:
            # Check if this should be default (if user has no other workspaces)
            user_workspaces = [
                w
                for w in self._workspaces.values()
                if w.owner_user_id == owner_user_id and w.status == WorkspaceStatus.ACTIVE
            ]
            is_default = len(user_workspaces) == 0

            workspace = Workspace(
                workspace_id=workspace_id,
                owner_user_id=owner_user_id,
                name=clean_name,
                description=description.strip() if description else None,
                organization_id=organization_id,
                workspace_type=workspace_type,
                template_origin_id=template_origin_id,
                layout_schema_version=1,
                layout_revision=1,
                is_default=is_default,
                is_favorite=False,
                status=WorkspaceStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                last_opened_at=now,
            )
            self._workspaces[workspace_id] = workspace

            # Initialize layout and panels
            if template_origin_id:
                template = get_workspace_template(template_origin_id)
                root_node = parse_layout_node(template.layout_definition["root_node"])
                panel_instances: dict[str, WorkspacePanelInstance] = {}
                for pdef in template.panel_definitions:
                    pid = pdef["panel_instance_id"]
                    ptype = PanelTypeId(pdef["panel_type_id"])
                    panel_instances[pid] = WorkspacePanelInstance(
                        panel_instance_id=pid,
                        workspace_id=workspace_id,
                        panel_type_id=ptype,
                        title_override=pdef.get("title_override"),
                        configuration=dict(pdef.get("configuration", {})),
                        link_group_id=pdef.get("link_group_id"),
                        independent_mode=pdef.get("link_group_id") is None,
                        created_at=now,
                        updated_at=now,
                    )
            elif initial_layout and "root_node" in initial_layout:
                root_node = parse_layout_node(initial_layout["root_node"])
                panel_instances = {}
                for pid, pdata in initial_layout.get("panel_instances", {}).items():
                    ptype = PanelTypeId(pdata["panel_type_id"])
                    panel_instances[pid] = WorkspacePanelInstance(
                        panel_instance_id=pid,
                        workspace_id=workspace_id,
                        panel_type_id=ptype,
                        title_override=pdata.get("title_override"),
                        configuration=dict(pdata.get("configuration", {})),
                        link_group_id=pdata.get("link_group_id"),
                        independent_mode=pdata.get("independent_mode", False),
                        created_at=now,
                        updated_at=now,
                    )
            else:
                # Default blank workspace: 1 default chart panel
                pid = f"p_chart_{uuid.uuid4().hex[:6]}"
                root_node = PanelNode(node_id="node_default_chart", panel_instance_id=pid)
                panel_instances = {
                    pid: WorkspacePanelInstance(
                        panel_instance_id=pid,
                        workspace_id=workspace_id,
                        panel_type_id=PanelTypeId.INSTRUMENT_CHART,
                        title_override="Main Chart",
                        configuration={"symbol": "AAPL", "timeframe": "1D"},
                        link_group_id="link_group_a",
                        independent_mode=False,
                        created_at=now,
                        updated_at=now,
                    )
                }

            # Validate layout invariants
            validate_layout_tree(root_node, set(panel_instances.keys()))

            layout = WorkspaceLayout(
                root_node=root_node,
                panel_instances=panel_instances,
                schema_version=1,
            )
            self._layouts[workspace_id] = layout

            # Initialize default link groups
            default_link_group = WorkspaceLinkGroup(
                link_group_id="link_group_a",
                workspace_id=workspace_id,
                name="Group A",
                color="#3b82f6",
                context={"INSTRUMENT": "AAPL", "TIMEFRAME": "1D"},
                version=1,
            )
            self._link_groups[workspace_id] = [default_link_group]

            # Record initial revision
            payload_str = json.dumps(layout.to_dict(), sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
            rev = WorkspaceLayoutRevision(
                revision_id=f"rev_{uuid.uuid4().hex[:8]}",
                workspace_id=workspace_id,
                revision_number=1,
                layout_payload=layout.to_dict(),
                created_by=owner_user_id,
                payload_hash=payload_hash,
                created_at=now,
            )
            self._revisions[workspace_id] = [rev]

            # Audit event
            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=owner_user_id,
                event_type=WorkspaceAuditEventType.WORKSPACE_CREATED,
                details={"name": clean_name, "template_origin_id": template_origin_id},
            )

            return workspace

    def get_workspace(self, workspace_id: str, user_id: str) -> Workspace:
        """Retrieves a workspace by ID, verifying user access."""
        with self._lock:
            ws = self._workspaces.get(workspace_id)
            if not ws or ws.status == WorkspaceStatus.SOFT_DELETED:
                raise WorkspaceNotFoundError(workspace_id)
            if ws.owner_user_id != user_id:
                raise WorkspaceAccessDeniedError(workspace_id, user_id)

            ws.last_opened_at = datetime.utcnow()
            return ws

    def list_workspaces(
        self,
        user_id: str,
        sort_by: WorkspaceSortOption = WorkspaceSortOption.RECENTLY_OPENED,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        """Lists workspaces owned by the user, enriched with panel counts."""
        with self._lock:
            allowed_statuses = [WorkspaceStatus.ACTIVE]
            if include_archived:
                allowed_statuses.append(WorkspaceStatus.ARCHIVED)

            user_workspaces = [
                ws
                for ws in self._workspaces.values()
                if ws.owner_user_id == user_id and ws.status in allowed_statuses
            ]

            if sort_by == WorkspaceSortOption.RECENTLY_OPENED:
                user_workspaces.sort(key=lambda w: w.last_opened_at, reverse=True)
            elif sort_by == WorkspaceSortOption.RECENTLY_MODIFIED:
                user_workspaces.sort(key=lambda w: w.updated_at, reverse=True)
            elif sort_by == WorkspaceSortOption.NAME:
                user_workspaces.sort(key=lambda w: w.name.lower())
            elif sort_by == WorkspaceSortOption.FAVORITES:
                user_workspaces.sort(key=lambda w: (not w.is_favorite, w.name.lower()))

            results: list[dict[str, Any]] = []
            for ws in user_workspaces:
                layout = self._layouts.get(ws.workspace_id)
                panel_count = len(layout.panel_instances) if layout else 0
                item = ws.to_dict()
                item["panel_count"] = panel_count
                results.append(item)

            return results

    def update_workspace_metadata(
        self,
        workspace_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        settings: Optional[dict[str, Any]] = None,
    ) -> Workspace:
        """Updates workspace name, description, favorite flag, or settings."""
        with self._lock:
            ws = self.get_workspace(workspace_id, user_id)
            now = datetime.utcnow()

            if name is not None:
                clean_name = name.strip()
                if not clean_name:
                    raise WorkspaceNameInvalidError("Workspace name cannot be empty.")
                if len(clean_name) > 100:
                    raise WorkspaceNameInvalidError("Workspace name cannot exceed 100 characters.")
                ws.name = clean_name

            if description is not None:
                ws.description = description.strip() if description else None

            if is_favorite is not None:
                ws.is_favorite = is_favorite

            if settings is not None:
                ws.settings.update(settings)

            ws.updated_at = now

            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.WORKSPACE_UPDATED,
                details={"name": ws.name, "is_favorite": ws.is_favorite},
            )
            return ws

    def duplicate_workspace(
        self, workspace_id: str, user_id: str, new_name: Optional[str] = None
    ) -> Workspace:
        """Clones an existing workspace, allocating fresh IDs for all panels and nodes."""
        with self._lock:
            src_ws = self.get_workspace(workspace_id, user_id)
            src_layout = self._layouts.get(workspace_id)
            if not src_layout:
                raise WorkspaceNotFoundError(workspace_id)

            copy_name = new_name or f"{src_ws.name} (Copy)"
            new_ws_id = f"ws_{uuid.uuid4().hex[:12]}"
            now = datetime.utcnow()

            # Map old panel instance IDs to new IDs
            id_map: dict[str, str] = {}
            new_panels: dict[str, WorkspacePanelInstance] = {}
            for old_pid, old_p in src_layout.panel_instances.items():
                new_pid = f"p_{old_p.panel_type_id.value.lower()}_{uuid.uuid4().hex[:6]}"
                id_map[old_pid] = new_pid
                new_panels[new_pid] = WorkspacePanelInstance(
                    panel_instance_id=new_pid,
                    workspace_id=new_ws_id,
                    panel_type_id=old_p.panel_type_id,
                    title_override=old_p.title_override,
                    configuration=dict(old_p.configuration),
                    link_group_id=old_p.link_group_id,
                    independent_mode=old_p.independent_mode,
                    created_at=now,
                    updated_at=now,
                )

            # Deep clone layout tree with new node IDs and remapped panel IDs
            def _clone_node(node: LayoutNode) -> LayoutNode:
                new_node_id = f"node_{uuid.uuid4().hex[:8]}"
                if isinstance(node, SplitNode):
                    return SplitNode(
                        node_id=new_node_id,
                        orientation=node.orientation,
                        children=[_clone_node(c) for c in node.children],
                        size_ratios=list(node.size_ratios),
                        min_size_rules=dict(node.min_size_rules),
                    )
                elif isinstance(node, TabStackNode):
                    new_pids = [id_map.get(pid, pid) for pid in node.panel_instance_ids]
                    active_pid = id_map.get(
                        node.active_panel_instance_id, new_pids[0] if new_pids else ""
                    )
                    return TabStackNode(
                        node_id=new_node_id,
                        panel_instance_ids=new_pids,
                        active_panel_instance_id=active_pid,
                    )
                elif isinstance(node, PanelNode):
                    return PanelNode(
                        node_id=new_node_id,
                        panel_instance_id=id_map.get(
                            node.panel_instance_id, node.panel_instance_id
                        ),
                    )
                return node

            cloned_root = _clone_node(src_layout.root_node)

            new_ws = Workspace(
                workspace_id=new_ws_id,
                owner_user_id=user_id,
                name=copy_name,
                description=src_ws.description,
                organization_id=src_ws.organization_id,
                workspace_type=WorkspaceType.CUSTOM,
                template_origin_id=src_ws.template_origin_id,
                layout_schema_version=src_ws.layout_schema_version,
                layout_revision=1,
                is_default=False,
                is_favorite=False,
                status=WorkspaceStatus.ACTIVE,
                settings=dict(src_ws.settings),
                created_at=now,
                updated_at=now,
                last_opened_at=now,
            )
            self._workspaces[new_ws_id] = new_ws
            self._layouts[new_ws_id] = WorkspaceLayout(
                root_node=cloned_root,
                panel_instances=new_panels,
                schema_version=1,
            )

            # Copy link groups
            src_groups = self._link_groups.get(workspace_id, [])
            new_groups: list[WorkspaceLinkGroup] = []
            for g in src_groups:
                new_groups.append(
                    WorkspaceLinkGroup(
                        link_group_id=g.link_group_id,
                        workspace_id=new_ws_id,
                        name=g.name,
                        color=g.color,
                        context=dict(g.context),
                        version=1,
                    )
                )
            self._link_groups[new_ws_id] = new_groups

            # Audit event
            self._record_audit_event(
                workspace_id=new_ws_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.WORKSPACE_DUPLICATED,
                details={"source_workspace_id": workspace_id, "name": copy_name},
            )

            return new_ws

    def delete_workspace(self, workspace_id: str, user_id: str, permanent: bool = False) -> None:
        """Deletes or soft-deletes a workspace."""
        with self._lock:
            ws = self.get_workspace(workspace_id, user_id)
            if permanent:
                del self._workspaces[workspace_id]
                self._layouts.pop(workspace_id, None)
                self._link_groups.pop(workspace_id, None)
                self._revisions.pop(workspace_id, None)
            else:
                ws.status = WorkspaceStatus.SOFT_DELETED
                ws.deleted_at = datetime.utcnow()
                ws.updated_at = datetime.utcnow()

            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.WORKSPACE_DELETED,
                details={"permanent": permanent},
            )

    def restore_workspace(self, workspace_id: str, user_id: str) -> Workspace:
        """Restores a soft-deleted workspace."""
        with self._lock:
            ws = self._workspaces.get(workspace_id)
            if not ws:
                raise WorkspaceNotFoundError(workspace_id)
            if ws.owner_user_id != user_id:
                raise WorkspaceAccessDeniedError(workspace_id, user_id)

            ws.status = WorkspaceStatus.ACTIVE
            ws.deleted_at = None
            ws.updated_at = datetime.utcnow()

            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.WORKSPACE_RESTORED,
                details={},
            )
            return ws

    def set_default_workspace(self, workspace_id: str, user_id: str) -> Workspace:
        """Sets the selected workspace as default and unsets all others for user."""
        with self._lock:
            target_ws = self.get_workspace(workspace_id, user_id)
            for ws in self._workspaces.values():
                if ws.owner_user_id == user_id:
                    ws.is_default = ws.workspace_id == workspace_id
                    ws.updated_at = datetime.utcnow()
            return target_ws

    # ---------------- Layout Operations ----------------

    def get_layout(self, workspace_id: str, user_id: str) -> WorkspaceLayout:
        """Retrieves layout for authorized workspace."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            layout = self._layouts.get(workspace_id)
            if not layout:
                raise WorkspaceNotFoundError(workspace_id)
            return layout

    def update_layout(
        self,
        workspace_id: str,
        user_id: str,
        expected_revision: int,
        layout_data: dict[str, Any],
    ) -> WorkspaceLayout:
        """
        Updates layout with optimistic concurrency control.
        Validates tree invariants before accepting.
        """
        with self._lock:
            ws = self.get_workspace(workspace_id, user_id)

            if expected_revision != ws.layout_revision:
                raise WorkspaceLayoutRevisionConflictError(
                    workspace_id=workspace_id,
                    expected_revision=expected_revision,
                    actual_revision=ws.layout_revision,
                )

            # Parse root node
            root_dict = layout_data.get("root_node")
            if not root_dict:
                raise WorkspaceLayoutRevisionConflictError(
                    workspace_id, expected_revision, ws.layout_revision
                )
            root_node = parse_layout_node(root_dict)

            # Existing panels or updated panel definitions
            existing_layout = self._layouts.get(workspace_id)
            panel_instances = existing_layout.panel_instances if existing_layout else {}

            if "panel_instances" in layout_data:
                for pid, pdata in layout_data["panel_instances"].items():
                    if pid in panel_instances:
                        p = panel_instances[pid]
                        if "title_override" in pdata:
                            p.title_override = pdata["title_override"]
                        if "configuration" in pdata:
                            p.configuration = dict(pdata["configuration"])
                        if "link_group_id" in pdata:
                            p.link_group_id = pdata["link_group_id"]
                        if "independent_mode" in pdata:
                            p.independent_mode = pdata["independent_mode"]
                        p.updated_at = datetime.utcnow()

            # Enforce layout invariants
            validate_layout_tree(root_node, set(panel_instances.keys()))

            new_layout = WorkspaceLayout(
                root_node=root_node,
                panel_instances=panel_instances,
                schema_version=layout_data.get("schema_version", 1),
            )
            self._layouts[workspace_id] = new_layout

            # Increment revision
            ws.layout_revision += 1
            ws.updated_at = datetime.utcnow()

            # Save historical revision
            payload_str = json.dumps(new_layout.to_dict(), sort_keys=True)
            payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
            rev = WorkspaceLayoutRevision(
                revision_id=f"rev_{uuid.uuid4().hex[:8]}",
                workspace_id=workspace_id,
                revision_number=ws.layout_revision,
                layout_payload=new_layout.to_dict(),
                created_by=user_id,
                payload_hash=payload_hash,
                created_at=datetime.utcnow(),
            )
            if workspace_id not in self._revisions:
                self._revisions[workspace_id] = []
            self._revisions[workspace_id].append(rev)

            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.LAYOUT_UPDATED,
                details={"revision": ws.layout_revision},
            )

            return new_layout

    def recover_layout(self, workspace_id: str, user_id: str) -> WorkspaceLayout:
        """Recovers a broken workspace layout by regenerating a clean layout for all panel instances."""
        with self._lock:
            ws = self.get_workspace(workspace_id, user_id)
            current_layout = self._layouts.get(workspace_id)
            panel_ids = list(current_layout.panel_instances.keys()) if current_layout else []

            safe_root = create_safe_recovery_layout(panel_ids)
            recovered_layout = WorkspaceLayout(
                root_node=safe_root,
                panel_instances=current_layout.panel_instances if current_layout else {},
                schema_version=1,
            )
            self._layouts[workspace_id] = recovered_layout
            ws.layout_revision += 1
            ws.updated_at = datetime.utcnow()
            return recovered_layout

    def get_revisions(self, workspace_id: str, user_id: str) -> list[WorkspaceLayoutRevision]:
        """Returns revision history for workspace."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            return list(self._revisions.get(workspace_id, []))

    # ---------------- Panel Operations ----------------

    def add_panel(
        self,
        workspace_id: str,
        user_id: str,
        panel_type_id: PanelTypeId,
        title_override: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        link_group_id: Optional[str] = None,
        dock_target_panel_id: Optional[str] = None,
        dock_position: str = "right",  # "right", "bottom", "tab"
    ) -> WorkspacePanelInstance:
        """Adds a new panel instance to the workspace and automatically mounts it into the layout."""
        with self._lock:
            ws = self.get_workspace(workspace_id, user_id)
            layout = self._layouts.get(workspace_id)
            if not layout:
                raise WorkspaceNotFoundError(workspace_id)

            defn = get_panel_type_definition(panel_type_id)
            new_pid = f"p_{panel_type_id.value.lower()}_{uuid.uuid4().hex[:6]}"
            now = datetime.utcnow()

            panel_instance = WorkspacePanelInstance(
                panel_instance_id=new_pid,
                workspace_id=workspace_id,
                panel_type_id=panel_type_id,
                title_override=title_override or defn.display_name,
                configuration=configuration or {},
                link_group_id=link_group_id,
                independent_mode=link_group_id is None,
                created_at=now,
                updated_at=now,
            )
            layout.panel_instances[new_pid] = panel_instance

            # Automatically dock panel into layout tree
            new_panel_node = PanelNode(
                node_id=f"node_{uuid.uuid4().hex[:8]}", panel_instance_id=new_pid
            )
            if isinstance(layout.root_node, SplitNode):
                # Add as child to root split or nest
                layout.root_node.children.append(new_panel_node)
                count = len(layout.root_node.children)
                layout.root_node.size_ratios = [1.0 / count] * count
            elif isinstance(layout.root_node, PanelNode):
                # Upgrade single panel into a horizontal split
                orientation = (
                    SplitOrientation.VERTICAL
                    if dock_position == "bottom"
                    else SplitOrientation.HORIZONTAL
                )
                layout.root_node = SplitNode(
                    node_id=f"split_{uuid.uuid4().hex[:8]}",
                    orientation=orientation,
                    children=[layout.root_node, new_panel_node],
                    size_ratios=[0.5, 0.5],
                )
            elif isinstance(layout.root_node, TabStackNode):
                layout.root_node.panel_instance_ids.append(new_pid)
                layout.root_node.active_panel_instance_id = new_pid

            # Increment revision
            ws.layout_revision += 1
            ws.updated_at = now

            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.PANEL_ADDED,
                details={"panel_instance_id": new_pid, "panel_type_id": panel_type_id.value},
            )

            return panel_instance

    def update_panel_configuration(
        self,
        workspace_id: str,
        user_id: str,
        panel_instance_id: str,
        title_override: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        link_group_id: Optional[str] = None,
        independent_mode: Optional[bool] = None,
    ) -> WorkspacePanelInstance:
        """Updates configuration, title, or link-group membership of an individual panel."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            layout = self._layouts.get(workspace_id)
            if not layout or panel_instance_id not in layout.panel_instances:
                raise WorkspacePanelNotFoundError(panel_instance_id)

            panel = layout.panel_instances[panel_instance_id]
            if title_override is not None:
                panel.title_override = title_override.strip() if title_override else None
            if configuration is not None:
                panel.configuration.update(configuration)
            if link_group_id is not None:
                panel.link_group_id = link_group_id if link_group_id != "none" else None
            if independent_mode is not None:
                panel.independent_mode = independent_mode

            panel.updated_at = datetime.utcnow()
            return panel

    def remove_panel(self, workspace_id: str, user_id: str, panel_instance_id: str) -> None:
        """Removes a panel from the workspace and prunes it from the layout tree."""
        with self._lock:
            ws = self.get_workspace(workspace_id, user_id)
            layout = self._layouts.get(workspace_id)
            if not layout or panel_instance_id not in layout.panel_instances:
                raise WorkspacePanelNotFoundError(panel_instance_id)

            del layout.panel_instances[panel_instance_id]

            # Prune node from tree
            def _prune(node: LayoutNode) -> Optional[LayoutNode]:
                if isinstance(node, PanelNode):
                    return None if node.panel_instance_id == panel_instance_id else node
                elif isinstance(node, TabStackNode):
                    node.panel_instance_ids = [
                        pid for pid in node.panel_instance_ids if pid != panel_instance_id
                    ]
                    if not node.panel_instance_ids:
                        return None
                    if node.active_panel_instance_id == panel_instance_id:
                        node.active_panel_instance_id = node.panel_instance_ids[0]
                    return node
                elif isinstance(node, SplitNode):
                    new_children = []
                    for child in node.children:
                        pruned = _prune(child)
                        if pruned:
                            new_children.append(pruned)
                    if not new_children:
                        return None
                    if len(new_children) == 1:
                        return new_children[0]
                    node.children = new_children
                    node.size_ratios = [1.0 / len(new_children)] * len(new_children)
                    return node
                return node

            pruned_root = _prune(layout.root_node)
            layout.root_node = pruned_root or create_safe_recovery_layout([])

            ws.layout_revision += 1
            ws.updated_at = datetime.utcnow()

            self._record_audit_event(
                workspace_id=workspace_id,
                user_id=user_id,
                event_type=WorkspaceAuditEventType.PANEL_REMOVED,
                details={"panel_instance_id": panel_instance_id},
            )

    # ---------------- Link Groups Operations ----------------

    def list_link_groups(self, workspace_id: str, user_id: str) -> list[WorkspaceLinkGroup]:
        """Lists active link groups for workspace."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            return list(self._link_groups.get(workspace_id, []))

    def create_link_group(
        self,
        workspace_id: str,
        user_id: str,
        name: str,
        color: str = "#3b82f6",
        initial_context: Optional[dict[str, Any]] = None,
    ) -> WorkspaceLinkGroup:
        """Creates a new link group for cross-panel state synchronization."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            gid = f"link_group_{uuid.uuid4().hex[:6]}"
            group = WorkspaceLinkGroup(
                link_group_id=gid,
                workspace_id=workspace_id,
                name=name.strip(),
                color=color,
                context=initial_context or {},
                version=1,
            )
            if workspace_id not in self._link_groups:
                self._link_groups[workspace_id] = []
            self._link_groups[workspace_id].append(group)
            return group

    def update_link_group_context(
        self,
        workspace_id: str,
        user_id: str,
        link_group_id: str,
        context_updates: dict[str, Any],
    ) -> WorkspaceLinkGroup:
        """Updates context values for a link group."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            groups = self._link_groups.get(workspace_id, [])
            group = next((g for g in groups if g.link_group_id == link_group_id), None)
            if not group:
                raise WorkspaceLinkGroupNotFoundError(link_group_id)

            group.context.update(context_updates)
            group.version += 1
            return group

    def delete_link_group(self, workspace_id: str, user_id: str, link_group_id: str) -> None:
        """Deletes a link group and detaches participating panels."""
        with self._lock:
            self.get_workspace(workspace_id, user_id)
            if workspace_id in self._link_groups:
                self._link_groups[workspace_id] = [
                    g for g in self._link_groups[workspace_id] if g.link_group_id != link_group_id
                ]

            # Detach panels
            layout = self._layouts.get(workspace_id)
            if layout:
                for p in layout.panel_instances.values():
                    if p.link_group_id == link_group_id:
                        p.link_group_id = None
                        p.independent_mode = True

    # ---------------- Audit Operations ----------------

    def _record_audit_event(
        self,
        workspace_id: str,
        user_id: str,
        event_type: WorkspaceAuditEventType,
        details: dict[str, Any],
    ) -> None:
        """Appends an immutable audit event."""
        event = WorkspaceAuditEvent(
            event_id=f"audit_{uuid.uuid4().hex[:10]}",
            workspace_id=workspace_id,
            user_id=user_id,
            event_type=event_type,
            details=details,
            created_at=datetime.utcnow(),
        )
        self._audit_events.append(event)
