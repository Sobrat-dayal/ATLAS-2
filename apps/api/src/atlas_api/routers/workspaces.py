"""
FastAPI Router for Stage 120 — Workspaces Architecture.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from atlas.auth import AuthPrincipal
from atlas.workspaces.enums import WorkspaceSortOption
from atlas.workspaces.errors import WorkspaceError
from atlas.workspaces.schemas import (
    AddPanelRequest,
    CreateLinkGroupRequest,
    CreateWorkspaceRequest,
    DuplicateWorkspaceRequest,
    UpdateLayoutRequest,
    UpdateLinkGroupContextRequest,
    UpdatePanelRequest,
    UpdateWorkspaceMetadataRequest,
)
from atlas.workspaces.service import WorkspaceService
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

# Singleton service instance
_workspace_service = WorkspaceService()


def get_workspace_service() -> WorkspaceService:
    return _workspace_service


def _get_principal_user_id(principal: AuthPrincipal) -> str:
    user_id = getattr(principal, "user_id", None) or getattr(principal, "sub", None)
    if not user_id:
        return "usr_default_trader"
    return str(user_id)


# ---------------- Workspace Endpoints ----------------


@router.get("", response_model=list[dict[str, Any]])
def list_workspaces(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    sort_by: WorkspaceSortOption = Query(WorkspaceSortOption.RECENTLY_OPENED),
    include_archived: bool = Query(False),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Lists workspaces owned by the authenticated user."""
    user_id = _get_principal_user_id(current_user)
    try:
        return service.list_workspaces(
            user_id=user_id, sort_by=sort_by, include_archived=include_archived
        )
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_workspace(
    request: CreateWorkspaceRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Creates a new workspace, either custom or from a template."""
    user_id = _get_principal_user_id(current_user)
    org_id = getattr(current_user, "org_id", None)
    try:
        ws = service.create_workspace(
            owner_user_id=user_id,
            name=request.name,
            description=request.description,
            template_id=request.template_id,
            initial_layout=request.initial_layout,
            organization_id=org_id,
        )
        return ws.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/templates", response_model=list[dict[str, Any]])
def list_templates(service: WorkspaceService = Depends(get_workspace_service)):
    """Lists built-in desk templates."""
    return [t.to_dict() for t in service.list_templates()]


@router.get("/templates/{template_id}", response_model=dict[str, Any])
def get_template(template_id: str, service: WorkspaceService = Depends(get_workspace_service)):
    """Retrieves definition of a specific desk template."""
    try:
        tmpl = service.get_template(template_id)
        return tmpl.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/panel-types", response_model=list[dict[str, Any]])
def list_panel_types(service: WorkspaceService = Depends(get_workspace_service)):
    """Returns canonical panel type definitions."""
    return [p.to_dict() for p in service.list_panel_types()]


@router.get("/{workspace_id}", response_model=dict[str, Any])
def get_workspace(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Retrieves workspace metadata and current layout tree."""
    user_id = _get_principal_user_id(current_user)
    try:
        ws = service.get_workspace(workspace_id, user_id)
        layout = service.get_layout(workspace_id, user_id)
        link_groups = service.list_link_groups(workspace_id, user_id)

        data = ws.to_dict()
        data["layout"] = layout.to_dict()
        data["link_groups"] = [g.to_dict() for g in link_groups]
        return data
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.patch("/{workspace_id}", response_model=dict[str, Any])
def update_workspace(
    workspace_id: str,
    request: UpdateWorkspaceMetadataRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Updates workspace title, description, favorite flag, or user settings."""
    user_id = _get_principal_user_id(current_user)
    try:
        ws = service.update_workspace_metadata(
            workspace_id=workspace_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            is_favorite=request.is_favorite,
            settings=request.settings,
        )
        return ws.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    permanent: bool = Query(False),
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Deletes or soft-deletes a workspace."""
    user_id = _get_principal_user_id(current_user)
    try:
        service.delete_workspace(workspace_id, user_id, permanent=permanent)
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post(
    "/{workspace_id}/duplicate", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED
)
def duplicate_workspace(
    workspace_id: str,
    request: DuplicateWorkspaceRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Clones a workspace with new identifiers for all panels and layout nodes."""
    user_id = _get_principal_user_id(current_user)
    try:
        dup = service.duplicate_workspace(workspace_id, user_id, new_name=request.new_name)
        return dup.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("/{workspace_id}/restore", response_model=dict[str, Any])
def restore_workspace(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Restores a soft-deleted workspace."""
    user_id = _get_principal_user_id(current_user)
    try:
        ws = service.restore_workspace(workspace_id, user_id)
        return ws.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("/{workspace_id}/set-default", response_model=dict[str, Any])
def set_default_workspace(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Designates this workspace as the user's default desk."""
    user_id = _get_principal_user_id(current_user)
    try:
        ws = service.set_default_workspace(workspace_id, user_id)
        return ws.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


# ---------------- Layout Operations ----------------


@router.get("/{workspace_id}/layout", response_model=dict[str, Any])
def get_layout(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Retrieves current layout definition."""
    user_id = _get_principal_user_id(current_user)
    try:
        layout = service.get_layout(workspace_id, user_id)
        return layout.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.put("/{workspace_id}/layout", response_model=dict[str, Any])
def update_layout(
    workspace_id: str,
    request: UpdateLayoutRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Saves layout with optimistic concurrency control."""
    user_id = _get_principal_user_id(current_user)
    try:
        updated = service.update_layout(
            workspace_id=workspace_id,
            user_id=user_id,
            expected_revision=request.expected_revision,
            layout_data=request.layout,
        )
        return updated.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("/{workspace_id}/recover", response_model=dict[str, Any])
def recover_layout(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Recovers a corrupted layout tree into a safe arrangement."""
    user_id = _get_principal_user_id(current_user)
    try:
        recovered = service.recover_layout(workspace_id, user_id)
        return recovered.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/{workspace_id}/revisions", response_model=list[dict[str, Any]])
def list_revisions(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Lists layout revision history."""
    user_id = _get_principal_user_id(current_user)
    try:
        revs = service.get_revisions(workspace_id, user_id)
        return [r.to_dict() for r in revs]
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


# ---------------- Panel Operations ----------------


@router.post(
    "/{workspace_id}/panels", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED
)
def add_panel(
    workspace_id: str,
    request: AddPanelRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Instantiates a new panel and docks it into the workspace layout."""
    user_id = _get_principal_user_id(current_user)
    try:
        panel = service.add_panel(
            workspace_id=workspace_id,
            user_id=user_id,
            panel_type_id=request.panel_type_id,
            title_override=request.title_override,
            configuration=request.configuration,
            link_group_id=request.link_group_id,
            dock_target_panel_id=request.dock_target_panel_id,
            dock_position=request.dock_position,
        )
        return panel.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.patch("/{workspace_id}/panels/{panel_id}", response_model=dict[str, Any])
def update_panel(
    workspace_id: str,
    panel_id: str,
    request: UpdatePanelRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Updates an individual panel's title, config, or link group."""
    user_id = _get_principal_user_id(current_user)
    try:
        panel = service.update_panel_configuration(
            workspace_id=workspace_id,
            user_id=user_id,
            panel_instance_id=panel_id,
            title_override=request.title_override,
            configuration=request.configuration,
            link_group_id=request.link_group_id,
            independent_mode=request.independent_mode,
        )
        return panel.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.delete("/{workspace_id}/panels/{panel_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_panel(
    workspace_id: str,
    panel_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Removes a panel instance and prunes it from the layout tree."""
    user_id = _get_principal_user_id(current_user)
    try:
        service.remove_panel(workspace_id, user_id, panel_id)
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


# ---------------- Link Group Operations ----------------


@router.get("/{workspace_id}/link-groups", response_model=list[dict[str, Any]])
def list_link_groups(
    workspace_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Lists link groups in a workspace."""
    user_id = _get_principal_user_id(current_user)
    try:
        groups = service.list_link_groups(workspace_id, user_id)
        return [g.to_dict() for g in groups]
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post(
    "/{workspace_id}/link-groups",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
)
def create_link_group(
    workspace_id: str,
    request: CreateLinkGroupRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Creates a link group for synchronized context sharing."""
    user_id = _get_principal_user_id(current_user)
    try:
        group = service.create_link_group(
            workspace_id=workspace_id,
            user_id=user_id,
            name=request.name,
            color=request.color,
            initial_context=request.initial_context,
        )
        return group.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.patch("/{workspace_id}/link-groups/{group_id}", response_model=dict[str, Any])
def update_link_group(
    workspace_id: str,
    group_id: str,
    request: UpdateLinkGroupContextRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Updates shared context values on a link group."""
    user_id = _get_principal_user_id(current_user)
    try:
        group = service.update_link_group_context(
            workspace_id=workspace_id,
            user_id=user_id,
            link_group_id=group_id,
            context_updates=request.context,
        )
        return group.to_dict()
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.delete("/{workspace_id}/link-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link_group(
    workspace_id: str,
    group_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: WorkspaceService = Depends(get_workspace_service),
):
    """Deletes a link group and reverts member panels to independent mode."""
    user_id = _get_principal_user_id(current_user)
    try:
        service.delete_link_group(workspace_id, user_id, group_id)
    except WorkspaceError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )
