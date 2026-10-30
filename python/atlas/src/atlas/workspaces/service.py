"""
High-Level Service Orchestrator for ATLAS Workspaces Architecture (Stage 120).
"""

from typing import Any, Optional

from atlas.workspaces.enums import PanelTypeId, WorkspaceSortOption, WorkspaceType
from atlas.workspaces.models import (
    Workspace,
    WorkspaceLayout,
    WorkspaceLayoutRevision,
    WorkspaceLinkGroup,
    WorkspacePanelInstance,
    WorkspaceTemplate,
)
from atlas.workspaces.panel_registry import PanelTypeDefinition, list_panel_type_definitions
from atlas.workspaces.repository import WorkspaceRepository
from atlas.workspaces.templates import get_workspace_template, list_workspace_templates


class WorkspaceService:
    """Orchestrates workspace lifecycle, layouts, panels, templates, and link groups."""

    def __init__(self, repository: Optional[WorkspaceRepository] = None):
        self.repository = repository or WorkspaceRepository()

    def create_workspace(
        self,
        owner_user_id: str,
        name: str,
        description: Optional[str] = None,
        template_id: Optional[str] = None,
        initial_layout: Optional[dict[str, Any]] = None,
        organization_id: Optional[str] = None,
    ) -> Workspace:
        """Creates a workspace from blank or from template."""
        ws_type = WorkspaceType.TEMPLATE_DERIVED if template_id else WorkspaceType.CUSTOM
        return self.repository.create_workspace(
            owner_user_id=owner_user_id,
            name=name,
            description=description,
            workspace_type=ws_type,
            template_origin_id=template_id,
            initial_layout=initial_layout,
            organization_id=organization_id,
        )

    def get_workspace(self, workspace_id: str, user_id: str) -> Workspace:
        return self.repository.get_workspace(workspace_id, user_id)

    def list_workspaces(
        self,
        user_id: str,
        sort_by: WorkspaceSortOption = WorkspaceSortOption.RECENTLY_OPENED,
        include_archived: bool = False,
    ) -> list[dict[str, Any]]:
        return self.repository.list_workspaces(user_id, sort_by, include_archived)

    def update_workspace_metadata(
        self,
        workspace_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        settings: Optional[dict[str, Any]] = None,
    ) -> Workspace:
        return self.repository.update_workspace_metadata(
            workspace_id, user_id, name, description, is_favorite, settings
        )

    def duplicate_workspace(
        self, workspace_id: str, user_id: str, new_name: Optional[str] = None
    ) -> Workspace:
        return self.repository.duplicate_workspace(workspace_id, user_id, new_name)

    def delete_workspace(self, workspace_id: str, user_id: str, permanent: bool = False) -> None:
        self.repository.delete_workspace(workspace_id, user_id, permanent)

    def restore_workspace(self, workspace_id: str, user_id: str) -> Workspace:
        return self.repository.restore_workspace(workspace_id, user_id)

    def set_default_workspace(self, workspace_id: str, user_id: str) -> Workspace:
        return self.repository.set_default_workspace(workspace_id, user_id)

    # Layout & Panels
    def get_layout(self, workspace_id: str, user_id: str) -> WorkspaceLayout:
        return self.repository.get_layout(workspace_id, user_id)

    def update_layout(
        self,
        workspace_id: str,
        user_id: str,
        expected_revision: int,
        layout_data: dict[str, Any],
    ) -> WorkspaceLayout:
        return self.repository.update_layout(workspace_id, user_id, expected_revision, layout_data)

    def recover_layout(self, workspace_id: str, user_id: str) -> WorkspaceLayout:
        return self.repository.recover_layout(workspace_id, user_id)

    def get_revisions(self, workspace_id: str, user_id: str) -> list[WorkspaceLayoutRevision]:
        return self.repository.get_revisions(workspace_id, user_id)

    def add_panel(
        self,
        workspace_id: str,
        user_id: str,
        panel_type_id: PanelTypeId,
        title_override: Optional[str] = None,
        configuration: Optional[dict[str, Any]] = None,
        link_group_id: Optional[str] = None,
        dock_target_panel_id: Optional[str] = None,
        dock_position: str = "right",
    ) -> WorkspacePanelInstance:
        return self.repository.add_panel(
            workspace_id=workspace_id,
            user_id=user_id,
            panel_type_id=panel_type_id,
            title_override=title_override,
            configuration=configuration,
            link_group_id=link_group_id,
            dock_target_panel_id=dock_target_panel_id,
            dock_position=dock_position,
        )

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
        return self.repository.update_panel_configuration(
            workspace_id=workspace_id,
            user_id=user_id,
            panel_instance_id=panel_instance_id,
            title_override=title_override,
            configuration=configuration,
            link_group_id=link_group_id,
            independent_mode=independent_mode,
        )

    def remove_panel(self, workspace_id: str, user_id: str, panel_instance_id: str) -> None:
        self.repository.remove_panel(workspace_id, user_id, panel_instance_id)

    # Link Groups
    def list_link_groups(self, workspace_id: str, user_id: str) -> list[WorkspaceLinkGroup]:
        return self.repository.list_link_groups(workspace_id, user_id)

    def create_link_group(
        self,
        workspace_id: str,
        user_id: str,
        name: str,
        color: str = "#3b82f6",
        initial_context: Optional[dict[str, Any]] = None,
    ) -> WorkspaceLinkGroup:
        return self.repository.create_link_group(
            workspace_id, user_id, name, color, initial_context
        )

    def update_link_group_context(
        self,
        workspace_id: str,
        user_id: str,
        link_group_id: str,
        context_updates: dict[str, Any],
    ) -> WorkspaceLinkGroup:
        return self.repository.update_link_group_context(
            workspace_id, user_id, link_group_id, context_updates
        )

    def delete_link_group(self, workspace_id: str, user_id: str, link_group_id: str) -> None:
        self.repository.delete_link_group(workspace_id, user_id, link_group_id)

    # Templates & Catalog
    def list_templates(self) -> list[WorkspaceTemplate]:
        return list_workspace_templates()

    def get_template(self, template_id: str) -> WorkspaceTemplate:
        return get_workspace_template(template_id)

    def list_panel_types(self) -> list[PanelTypeDefinition]:
        return list_panel_type_definitions()
