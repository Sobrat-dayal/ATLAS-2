"""Pydantic V2 Request and Response Schemas for Stage 119 - Universal Saved System."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from atlas.saved.enums import (
    ResourceAvailabilityStatus,
    SavedBulkActionType,
    SavedModule,
    SavedReferenceSemantics,
    SavedTargetType,
    ViewConfigurationType,
)


class CreateSavedItemRequest(BaseModel):
    """Payload to save an authoritative ATLAS resource reference."""

    target_type: SavedTargetType = Field(..., description="Canonical resource category.")
    target_id: str = Field(
        ..., min_length=1, max_length=512, description="Target resource identifier."
    )
    target_revision_id: Optional[str] = Field(
        None, max_length=128, description="Immutable revision identifier if applicable."
    )
    display_title_override: Optional[str] = Field(
        None, max_length=200, description="Optional custom user title."
    )
    user_note: Optional[str] = Field(
        None, max_length=5000, description="Optional private user annotation."
    )
    favorite: bool = Field(False, description="Whether to mark as favorite upon saving.")
    pinned: bool = Field(False, description="Whether to pin to the top of views.")
    collection_ids: List[str] = Field(
        default_factory=list, description="Collections to assign the saved item to."
    )
    tags: List[str] = Field(default_factory=list, description="Tags to assign.")
    view_configuration_id: Optional[str] = Field(
        None, description="Optional linked view configuration."
    )
    idempotency_key: Optional[str] = Field(
        None, max_length=128, description="Idempotency key to avoid duplicate saves."
    )


class UpdateSavedItemRequest(BaseModel):
    """Payload to update user metadata on an existing saved item."""

    display_title_override: Optional[str] = Field(None, max_length=200)
    user_note: Optional[str] = Field(None, max_length=5000)
    favorite: Optional[bool] = None
    pinned: Optional[bool] = None
    target_revision_id: Optional[str] = Field(None, max_length=128)
    expected_row_version: Optional[int] = Field(
        None, description="Optimistic concurrency control version."
    )


class SavedItemDTO(BaseModel):
    """Public representation of a saved item with runtime availability."""

    saved_item_id: str
    owner_user_id: str
    organization_id: Optional[str] = None
    target_type: SavedTargetType
    target_id: str
    target_revision_id: Optional[str] = None
    target_module: SavedModule
    canonical_title: str
    display_title: str
    user_note: Optional[str] = None
    favorite: bool
    pinned: bool
    view_configuration_id: Optional[str] = None
    semantics: SavedReferenceSemantics
    collection_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    availability_status: ResourceAvailabilityStatus
    safe_deep_link: str
    warnings: List[str] = Field(default_factory=list)
    saved_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    row_version: int


class SavedItemListResponseDTO(BaseModel):
    """Paginated list of saved items."""

    items: List[SavedItemDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int


class CreateSavedCollectionRequest(BaseModel):
    """Payload to create an organizational collection."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_collection_id: Optional[str] = None
    sort_order: int = 0


class UpdateSavedCollectionRequest(BaseModel):
    """Payload to edit collection properties."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_collection_id: Optional[str] = None
    sort_order: Optional[int] = None
    expected_row_version: Optional[int] = None


class SavedCollectionDTO(BaseModel):
    """Public representation of a saved collection."""

    collection_id: str
    owner_user_id: str
    name: str
    description: Optional[str] = None
    parent_collection_id: Optional[str] = None
    item_count: int = 0
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    row_version: int


class SavedCollectionTreeDTO(BaseModel):
    """Hierarchical nested representation of a collection node."""

    collection: SavedCollectionDTO
    children: List[SavedCollectionTreeDTO] = Field(default_factory=list)


class AddItemsToCollectionRequest(BaseModel):
    """Add one or more saved items to a collection."""

    saved_item_ids: List[str] = Field(..., min_length=1)


class CreateSavedTagRequest(BaseModel):
    """Create a user tag."""

    name: str = Field(..., min_length=1, max_length=50)


class SavedTagDTO(BaseModel):
    """Public representation of a tag with item count."""

    tag_id: str
    name: str
    normalized_name: str
    item_count: int = 0
    created_at: datetime


class AssignTagRequest(BaseModel):
    """Assign a tag by name to a saved item."""

    name: str = Field(..., min_length=1, max_length=50)


class SavedViewConfigurationDTO(BaseModel):
    """Public representation of a validated view configuration."""

    configuration_id: str
    configuration_type: ViewConfigurationType
    schema_version: int
    payload: Dict[str, Any]
    payload_hash: str
    target_module: SavedModule
    created_at: datetime
    updated_at: datetime


class CreateSavedConfigurationRequest(BaseModel):
    """Create a user view configuration."""

    configuration_type: ViewConfigurationType
    schema_version: int = 1
    payload: Dict[str, Any]
    target_module: SavedModule


class UpdateSavedConfigurationRequest(BaseModel):
    """Update a view configuration payload."""

    payload: Dict[str, Any]
    schema_version: Optional[int] = None


class ValidateConfigurationRequest(BaseModel):
    """Validate or dry-run migrate a configuration payload."""

    configuration_type: ViewConfigurationType
    schema_version: int
    payload: Dict[str, Any]
    target_version: Optional[int] = None


class ValidateConfigurationResponse(BaseModel):
    """Result of configuration validation or dry-run migration."""

    valid: bool
    schema_version: int
    sanitized_payload: Dict[str, Any]
    payload_hash: str
    migrated_payload: Optional[Dict[str, Any]] = None
    migrated_version: Optional[int] = None
    warnings: List[str] = Field(default_factory=list)


class ResolveTargetRequest(BaseModel):
    """Request to resolve a target without saving it."""

    target_type: SavedTargetType
    target_id: str
    requested_revision_id: Optional[str] = None


class ResolvedTargetDTO(BaseModel):
    """Runtime availability resolution of a target."""

    target_type: SavedTargetType
    target_id: str
    exists: bool
    authorized: bool
    entitled: bool
    status: ResourceAvailabilityStatus
    canonical_title: str
    target_module: SavedModule
    safe_deep_link: str
    target_revision_id: Optional[str] = None
    latest_revision_id: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class SavedBulkActionRequest(BaseModel):
    """Batch action payload."""

    action: SavedBulkActionType
    saved_item_ids: List[str] = Field(..., min_length=1, max_length=500)
    collection_id: Optional[str] = None
    tag_name: Optional[str] = None


class BulkActionItemResultDTO(BaseModel):
    """Result of a single item in a batch operation."""

    saved_item_id: str
    success: bool
    error: Optional[str] = None


class SavedBulkActionResponseDTO(BaseModel):
    """Summary of batch operation execution."""

    action: SavedBulkActionType
    total_requested: int
    succeeded_count: int
    failed_count: int
    results: List[BulkActionItemResultDTO]


class SavedLibrarySummaryDTO(BaseModel):
    """KPI metrics for the user's saved library."""

    total_saved_items: int
    favorite_count: int
    pinned_count: int
    collection_count: int
    tag_count: int
    recent_saves_count: int
