"""FastAPI Router for Stage 119 - Universal Saved System and Cross-Module Library."""

from __future__ import annotations

import logging
from typing import Annotated, Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.saved.enums import (
    SavedModule,
    SavedSortOption,
    SavedTargetType,
)
from atlas.saved.errors import (
    SavedError,
)
from atlas.saved.models import SavedTargetDefinition
from atlas.saved.registry import list_supported_target_types
from atlas.saved.schemas import (
    AddItemsToCollectionRequest,
    AssignTagRequest,
    CreateSavedCollectionRequest,
    CreateSavedConfigurationRequest,
    CreateSavedItemRequest,
    CreateSavedTagRequest,
    ResolvedTargetDTO,
    ResolveTargetRequest,
    SavedBulkActionRequest,
    SavedBulkActionResponseDTO,
    SavedCollectionDTO,
    SavedCollectionTreeDTO,
    SavedItemDTO,
    SavedItemListResponseDTO,
    SavedLibrarySummaryDTO,
    SavedTagDTO,
    SavedViewConfigurationDTO,
    UpdateSavedCollectionRequest,
    UpdateSavedItemRequest,
    ValidateConfigurationRequest,
    ValidateConfigurationResponse,
)
from atlas.saved.service import SavedService
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/saved", tags=["Saved"])

_saved_service_instance: Optional[SavedService] = None


def _get_principal_user_id(principal: Any) -> str:
    """Extracts user ID from AuthPrincipal supporting sub or user_id."""
    return str(getattr(principal, "sub", getattr(principal, "user_id", "anonymous")))


def get_saved_service() -> SavedService:
    """Dependency injector for singleton SavedService."""
    global _saved_service_instance
    if _saved_service_instance is None:
        _saved_service_instance = SavedService()
    return _saved_service_instance


# -----------------------------------------------------------------------------
# Metadata Catalogs and Resolvers
# -----------------------------------------------------------------------------


@router.get(
    "/types",
    response_model=List[SavedTargetDefinition],
    summary="Get Supported Saved Target Types",
)
def get_supported_types(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> List[SavedTargetDefinition]:
    """Returns canonical definitions of all supported target resource categories."""
    return list_supported_target_types()


@router.post(
    "/resolve",
    response_model=ResolvedTargetDTO,
    summary="Resolve Target Resource",
)
def resolve_target(
    req: ResolveTargetRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> ResolvedTargetDTO:
    """Evaluates target resource existence, caller permissions, and safe deep link without saving."""
    try:
        user_id = _get_principal_user_id(current_user)
        org_id = str(current_user.org_id) if getattr(current_user, "org_id", None) else None
        entitlements = (
            list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
        )
        return service.resolve_target(
            user_id=user_id,
            request=req,
            organization_id=org_id,
            user_entitlements=entitlements,
        )
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/summary",
    response_model=SavedLibrarySummaryDTO,
    summary="Get Library Summary KPIs",
)
def get_library_summary(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedLibrarySummaryDTO:
    """Returns aggregated summary metrics for the authenticated user's saved library."""
    user_id = _get_principal_user_id(current_user)
    return service.get_library_summary(user_id=user_id)


# -----------------------------------------------------------------------------
# Saved Items CRUD
# -----------------------------------------------------------------------------


@router.get(
    "",
    response_model=SavedItemListResponseDTO,
    summary="List Saved Items",
)
def list_saved_items(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
    search: Optional[str] = Query(None, description="Free text search query"),
    target_type: Optional[SavedTargetType] = Query(None, description="Filter by resource type"),
    target_module: Optional[SavedModule] = Query(None, description="Filter by source module"),
    collection_id: Optional[str] = Query(None, description="Filter by collection membership"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    favorite: Optional[bool] = Query(None, description="Filter by favorite flag"),
    pinned: Optional[bool] = Query(None, description="Filter by pinned flag"),
    sort_by: SavedSortOption = Query(SavedSortOption.RECENTLY_SAVED, description="Sort order"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> SavedItemListResponseDTO:
    """Returns paginated, sorted, and filtered saved items for the user."""
    user_id = _get_principal_user_id(current_user)
    entitlements = list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
    return service.list_items(
        user_id=user_id,
        search=search,
        target_type=target_type,
        target_module=target_module,
        collection_id=collection_id,
        tag_name=tag,
        favorite=favorite,
        pinned=pinned,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        user_entitlements=entitlements,
    )


@router.post(
    "",
    response_model=SavedItemDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Save Resource Reference",
)
def save_item(
    req: CreateSavedItemRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    """Persists a new canonical resource reference or analytical configuration."""
    try:
        user_id = _get_principal_user_id(current_user)
        org_id = str(current_user.org_id) if getattr(current_user, "org_id", None) else None
        entitlements = (
            list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
        )
        return service.save_item(
            user_id=user_id,
            request=req,
            organization_id=org_id,
            user_entitlements=entitlements,
        )
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{saved_item_id}",
    response_model=SavedItemDTO,
    summary="Get Saved Item Details",
)
def get_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    """Retrieves full details and evaluated runtime availability for a saved item."""
    try:
        user_id = _get_principal_user_id(current_user)
        entitlements = (
            list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
        )
        return service.get_item(
            saved_item_id=saved_item_id,
            user_id=user_id,
            user_entitlements=entitlements,
        )
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/{saved_item_id}",
    response_model=SavedItemDTO,
    summary="Update Saved Item Metadata",
)
def update_saved_item(
    saved_item_id: str,
    req: UpdateSavedItemRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    """Updates user-controlled metadata (note, title override, favorite, pin) with version checks."""
    try:
        user_id = _get_principal_user_id(current_user)
        entitlements = (
            list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
        )
        return service.update_item(
            saved_item_id=saved_item_id,
            user_id=user_id,
            request=req,
            user_entitlements=entitlements,
        )
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/{saved_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Saved Item",
)
def delete_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> None:
    """Safely removes item from saved library (does not delete underlying original resource)."""
    try:
        user_id = _get_principal_user_id(current_user)
        service.soft_delete_item(saved_item_id=saved_item_id, user_id=user_id)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{saved_item_id}/restore",
    response_model=SavedItemDTO,
    summary="Restore Soft-Deleted Item",
)
def restore_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    """Restores a previously removed item to the active library."""
    try:
        user_id = _get_principal_user_id(current_user)
        entitlements = (
            list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
        )
        return service.restore_item(
            saved_item_id=saved_item_id,
            user_id=user_id,
            user_entitlements=entitlements,
        )
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# -----------------------------------------------------------------------------
# Favorites and Pinning
# -----------------------------------------------------------------------------


@router.put(
    "/{saved_item_id}/favorite",
    response_model=SavedItemDTO,
    summary="Mark as Favorite",
)
def favorite_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    try:
        user_id = _get_principal_user_id(current_user)
        return service.toggle_favorite(saved_item_id=saved_item_id, user_id=user_id, favorite=True)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/{saved_item_id}/favorite",
    response_model=SavedItemDTO,
    summary="Unmark Favorite",
)
def unfavorite_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    try:
        user_id = _get_principal_user_id(current_user)
        return service.toggle_favorite(saved_item_id=saved_item_id, user_id=user_id, favorite=False)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put(
    "/{saved_item_id}/pin",
    response_model=SavedItemDTO,
    summary="Pin Saved Item",
)
def pin_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    try:
        user_id = _get_principal_user_id(current_user)
        return service.toggle_pin(saved_item_id=saved_item_id, user_id=user_id, pinned=True)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/{saved_item_id}/pin",
    response_model=SavedItemDTO,
    summary="Unpin Saved Item",
)
def unpin_saved_item(
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedItemDTO:
    try:
        user_id = _get_principal_user_id(current_user)
        return service.toggle_pin(saved_item_id=saved_item_id, user_id=user_id, pinned=False)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# -----------------------------------------------------------------------------
# Collections
# -----------------------------------------------------------------------------


@router.get(
    "/collections",
    response_model=List[SavedCollectionDTO],
    summary="List Collections",
)
def list_collections(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> List[SavedCollectionDTO]:
    """Returns organizational collections owned by the user."""
    user_id = _get_principal_user_id(current_user)
    return service.list_collections(user_id=user_id)


@router.get(
    "/collections/tree",
    response_model=List[SavedCollectionTreeDTO],
    summary="Get Collection Hierarchy Tree",
)
def get_collection_tree(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> List[SavedCollectionTreeDTO]:
    """Returns full nested hierarchical collection tree for navigation."""
    user_id = _get_principal_user_id(current_user)
    return service.get_collection_tree(user_id=user_id)


@router.post(
    "/collections",
    response_model=SavedCollectionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Collection",
)
def create_collection(
    req: CreateSavedCollectionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedCollectionDTO:
    """Creates a new organizational collection with hierarchy validation."""
    try:
        user_id = _get_principal_user_id(current_user)
        org_id = str(current_user.org_id) if getattr(current_user, "org_id", None) else None
        return service.create_collection(user_id=user_id, request=req, organization_id=org_id)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/collections/{collection_id}",
    response_model=SavedCollectionDTO,
    summary="Update Collection",
)
def update_collection(
    collection_id: str,
    req: UpdateSavedCollectionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedCollectionDTO:
    """Updates collection name, description, or parent with cycle detection."""
    try:
        user_id = _get_principal_user_id(current_user)
        return service.update_collection(collection_id=collection_id, user_id=user_id, request=req)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/collections/{collection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Collection",
)
def delete_collection(
    collection_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> None:
    """Deletes collection without removing underlying saved resources."""
    try:
        user_id = _get_principal_user_id(current_user)
        service.delete_collection(collection_id=collection_id, user_id=user_id)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/collections/{collection_id}/items",
    status_code=status.HTTP_200_OK,
    summary="Add Items to Collection",
)
def add_items_to_collection(
    collection_id: str,
    req: AddItemsToCollectionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> Dict[str, Any]:
    """Assigns saved items to the specified collection."""
    try:
        user_id = _get_principal_user_id(current_user)
        service.add_items_to_collection(
            collection_id=collection_id, user_id=user_id, saved_item_ids=req.saved_item_ids
        )
        return {"status": "ok", "added_count": len(req.saved_item_ids)}
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/collections/{collection_id}/items/{saved_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Item from Collection",
)
def remove_item_from_collection(
    collection_id: str,
    saved_item_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> None:
    """Removes collection membership without removing item from global library."""
    try:
        user_id = _get_principal_user_id(current_user)
        service.remove_item_from_collection(
            collection_id=collection_id, user_id=user_id, saved_item_id=saved_item_id
        )
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------


@router.get(
    "/tags",
    response_model=List[SavedTagDTO],
    summary="List User Tags",
)
def list_tags(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> List[SavedTagDTO]:
    """Returns all tags with item counts owned by the user."""
    user_id = _get_principal_user_id(current_user)
    return service.list_tags(user_id=user_id)


@router.post(
    "/tags",
    response_model=SavedTagDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Tag",
)
def create_tag(
    req: CreateSavedTagRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedTagDTO:
    """Creates a user tag."""
    try:
        user_id = _get_principal_user_id(current_user)
        return service.create_tag(user_id=user_id, request=req)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{saved_item_id}/tags",
    response_model=SavedTagDTO,
    summary="Assign Tag to Item",
)
def assign_tag_to_item(
    saved_item_id: str,
    req: AssignTagRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedTagDTO:
    """Assigns tag by name to a saved item."""
    try:
        user_id = _get_principal_user_id(current_user)
        return service.assign_tag(saved_item_id=saved_item_id, user_id=user_id, tag_name=req.name)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/{saved_item_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Tag from Item",
)
def remove_tag_from_item(
    saved_item_id: str,
    tag_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> None:
    """Removes a tag association from a saved item."""
    try:
        user_id = _get_principal_user_id(current_user)
        service.remove_tag(saved_item_id=saved_item_id, user_id=user_id, tag_id=tag_id)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# -----------------------------------------------------------------------------
# View Configurations
# -----------------------------------------------------------------------------


@router.post(
    "/configurations",
    response_model=SavedViewConfigurationDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create View Configuration",
)
def create_configuration(
    req: CreateSavedConfigurationRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedViewConfigurationDTO:
    """Validates, sanitizes secrets, and saves an analytical presentation view configuration."""
    try:
        user_id = _get_principal_user_id(current_user)
        return service.save_configuration(user_id=user_id, request=req)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/configurations/{configuration_id}",
    response_model=SavedViewConfigurationDTO,
    summary="Get View Configuration",
)
def get_configuration(
    configuration_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedViewConfigurationDTO:
    """Retrieves an authorized view configuration."""
    try:
        user_id = _get_principal_user_id(current_user)
        return service.get_configuration(configuration_id=configuration_id, user_id=user_id)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/configurations/validate",
    response_model=ValidateConfigurationResponse,
    summary="Validate View Configuration Payload",
)
def validate_configuration_payload(
    req: ValidateConfigurationRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> ValidateConfigurationResponse:
    """Validates schema structure, tests migrations, and detects forbidden executable payloads."""
    try:
        user_id = _get_principal_user_id(current_user)
        return service.validate_configuration(user_id=user_id, request=req)
    except SavedError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# -----------------------------------------------------------------------------
# Bulk Operations
# -----------------------------------------------------------------------------


@router.post(
    "/bulk",
    response_model=SavedBulkActionResponseDTO,
    summary="Execute Bulk Action",
)
def execute_bulk_action(
    req: SavedBulkActionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[SavedService, Depends(get_saved_service)],
) -> SavedBulkActionResponseDTO:
    """Executes batch favorite, pin, collection membership, tagging, or deletion."""
    user_id = _get_principal_user_id(current_user)
    entitlements = list(current_user.entitlements) if hasattr(current_user, "entitlements") else []
    return service.execute_bulk_action(user_id=user_id, request=req, user_entitlements=entitlements)
