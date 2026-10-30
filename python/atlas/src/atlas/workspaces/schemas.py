"""
Pydantic Request and Response Schemas for ATLAS Workspaces Architecture (Stage 120).
"""

from typing import Any, Optional

from pydantic import BaseModel, Field

from atlas.workspaces.enums import PanelTypeId


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Workspace display name")
    description: Optional[str] = Field(
        None, max_length=500, description="Optional desk description"
    )
    template_id: Optional[str] = Field(
        None, description="Optional ID of template to derive layout from"
    )
    initial_layout: Optional[dict[str, Any]] = Field(
        None, description="Custom layout tree definition"
    )


class UpdateWorkspaceMetadataRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_favorite: Optional[bool] = None
    settings: Optional[dict[str, Any]] = None


class DuplicateWorkspaceRequest(BaseModel):
    new_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UpdateLayoutRequest(BaseModel):
    expected_revision: int = Field(
        ..., description="Expected current revision number for optimistic concurrency"
    )
    layout: dict[str, Any] = Field(..., description="Complete layout tree definition")


class AddPanelRequest(BaseModel):
    panel_type_id: PanelTypeId = Field(..., description="Registered panel type identifier")
    title_override: Optional[str] = Field(None, max_length=100)
    configuration: Optional[dict[str, Any]] = Field(default_factory=dict)
    link_group_id: Optional[str] = None
    dock_target_panel_id: Optional[str] = None
    dock_position: str = Field("right", pattern="^(right|bottom|tab)$")


class UpdatePanelRequest(BaseModel):
    title_override: Optional[str] = Field(None, max_length=100)
    configuration: Optional[dict[str, Any]] = None
    link_group_id: Optional[str] = None
    independent_mode: Optional[bool] = None


class CreateLinkGroupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field("#3b82f6", max_length=20)
    initial_context: Optional[dict[str, Any]] = Field(default_factory=dict)


class UpdateLinkGroupContextRequest(BaseModel):
    context: dict[str, Any] = Field(
        ..., description="Context dimensions to merge into the link group"
    )


class WorkspaceSummaryResponse(BaseModel):
    workspace_id: str
    owner_user_id: str
    name: str
    description: Optional[str]
    workspace_type: str
    template_origin_id: Optional[str]
    layout_revision: int
    is_default: bool
    is_favorite: bool
    status: str
    panel_count: int
    created_at: str
    updated_at: str
    last_opened_at: str


class WorkspaceDetailResponse(BaseModel):
    workspace_id: str
    owner_user_id: str
    name: str
    description: Optional[str]
    workspace_type: str
    template_origin_id: Optional[str]
    layout_schema_version: int
    layout_revision: int
    is_default: bool
    is_favorite: bool
    status: str
    settings: dict[str, Any]
    layout: dict[str, Any]
    link_groups: list[dict[str, Any]]
    created_at: str
    updated_at: str
    last_opened_at: str
