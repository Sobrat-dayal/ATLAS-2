"""FastAPI Router for Saved Chart Layouts (Stage 74).

Exposes authenticated REST endpoints under `/charts/layouts`:
- GET /charts/layouts: List user's saved layouts with pagination and search
- POST /charts/layouts: Create a new saved layout document
- GET /charts/layouts/{id}: Retrieve layout document with ETag
- PUT /charts/layouts/{id}: Replace saved layout configuration with If-Match concurrency check
- PATCH /charts/layouts/{id}: Update metadata (rename, description, default flag)
- POST /charts/layouts/{id}/duplicate: Duplicate a layout
- DELETE /charts/layouts/{id}: Delete a layout
- GET /charts/layouts/{id}/export: Portable configuration export envelope
"""

import uuid
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.charts.layouts import (
    ChartLayoutCreateRequest,
    ChartLayoutDetailResponse,
    ChartLayoutDuplicateRequest,
    ChartLayoutExportEnvelope,
    ChartLayoutListResponse,
    ChartLayoutMetadataPatchRequest,
    ChartLayoutRepository,
    ChartLayoutService,
    ChartLayoutUpdateRequest,
    ForbiddenFieldDetectedError,
    InvalidLayoutNameError,
    JsonNestingDepthExceededError,
    LayoutNameConflictError,
    LayoutNotFoundError,
    LayoutPayloadTooLargeError,
    LayoutQuotaExceededError,
    LayoutRevisionConflictError,
    UnsupportedSchemaVersionError,
)
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session

router = APIRouter(prefix="/charts/layouts", tags=["Chart Layouts"])


def get_chart_layout_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChartLayoutService:
    repository = ChartLayoutRepository(session)
    return ChartLayoutService(repository)


def _parse_etag(if_match: Optional[str]) -> Optional[int]:
    """Parses numeric revision from ETag header format (e.g. W/"3" or "3")."""
    if not if_match:
        return None
    cleaned = if_match.strip()
    if cleaned.startswith('W/"') and cleaned.endswith('"'):
        cleaned = cleaned[3:-1]
    elif cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    try:
        return int(cleaned)
    except ValueError:
        return None


@router.get(
    "",
    response_model=ChartLayoutListResponse,
    summary="List saved chart layouts",
    description="Lists persistent chart workspace layouts belonging to the authenticated user.",
)
async def list_chart_layouts(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term matching layout name"),
) -> ChartLayoutListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    user_id = uuid.UUID(principal.user_id)
    return await service.list_layouts(
        owner_user_id=user_id,
        page=page,
        page_size=page_size,
        search=search,
    )


@router.post(
    "",
    response_model=ChartLayoutDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a saved chart layout",
    description="Saves the current multi-chart workspace configuration as a new persistent record.",
)
async def create_chart_layout(
    request: ChartLayoutCreateRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
) -> ChartLayoutDetailResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        detail = await service.create_layout(user_id, request)
        response.headers["ETag"] = f'W/"{detail.revision}"'
        response.headers["Location"] = f"/api/v1/charts/layouts/{detail.id}"
        return detail
    except LayoutNameConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except LayoutQuotaExceededError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (
        LayoutPayloadTooLargeError,
        ForbiddenFieldDetectedError,
        JsonNestingDepthExceededError,
        InvalidLayoutNameError,
        UnsupportedSchemaVersionError,
    ) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{layout_id}",
    response_model=ChartLayoutDetailResponse,
    summary="Get saved chart layout by ID",
    description="Retrieves a single chart layout configuration document.",
)
async def get_chart_layout(
    layout_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
) -> ChartLayoutDetailResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        detail = await service.get_layout(layout_id, user_id)
        response.headers["ETag"] = f'W/"{detail.revision}"'
        response.headers["Cache-Control"] = "private, no-store"
        return detail
    except LayoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart layout '{layout_id}' not found.",
        )


@router.put(
    "/{layout_id}",
    response_model=ChartLayoutDetailResponse,
    summary="Update saved chart layout",
    description="Updates the complete layout document with atomic optimistic concurrency control.",
)
async def update_chart_layout(
    layout_id: uuid.UUID,
    request: ChartLayoutUpdateRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
    if_match: Annotated[Optional[str], Header()] = None,
) -> ChartLayoutDetailResponse:
    user_id = uuid.UUID(principal.user_id)

    # Resolve expected revision from header or body
    header_revision = _parse_etag(if_match)
    expected_rev = header_revision if header_revision is not None else request.expected_revision

    if expected_rev is None:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail=(
                "If-Match header or expected_revision in request body is "
                "required for optimistic concurrency."
            ),
        )

    # Sync expected_revision to request object
    request.expected_revision = expected_rev

    try:
        detail = await service.update_layout(layout_id, user_id, request)
        response.headers["ETag"] = f'W/"{detail.revision}"'
        return detail
    except LayoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart layout '{layout_id}' not found.",
        )
    except LayoutRevisionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(e),
        )
    except (
        LayoutPayloadTooLargeError,
        ForbiddenFieldDetectedError,
        JsonNestingDepthExceededError,
        UnsupportedSchemaVersionError,
    ) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/{layout_id}",
    response_model=ChartLayoutDetailResponse,
    summary="Update chart layout metadata",
    description="Renames or toggles the default status of a saved chart layout.",
)
async def patch_chart_layout_metadata(
    layout_id: uuid.UUID,
    request: ChartLayoutMetadataPatchRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
) -> ChartLayoutDetailResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        detail = await service.patch_metadata(layout_id, user_id, request)
        response.headers["ETag"] = f'W/"{detail.revision}"'
        return detail
    except LayoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart layout '{layout_id}' not found.",
        )
    except LayoutNameConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except InvalidLayoutNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{layout_id}/duplicate",
    response_model=ChartLayoutDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate saved chart layout",
    description="Clones an existing layout document under a new UUID and distinct name.",
)
async def duplicate_chart_layout(
    layout_id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
    request: Optional[ChartLayoutDuplicateRequest] = None,
) -> ChartLayoutDetailResponse:
    user_id = uuid.UUID(principal.user_id)
    new_name = request.new_name if request else None
    try:
        detail = await service.duplicate_layout(layout_id, user_id, new_name=new_name)
        response.headers["ETag"] = f'W/"{detail.revision}"'
        response.headers["Location"] = f"/api/v1/charts/layouts/{detail.id}"
        return detail
    except LayoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart layout '{layout_id}' not found.",
        )
    except LayoutQuotaExceededError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (LayoutNameConflictError, InvalidLayoutNameError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{layout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved chart layout",
    description="Permanently removes a saved chart layout record owned by the authenticated user.",
)
async def delete_chart_layout(
    layout_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
) -> None:
    user_id = uuid.UUID(principal.user_id)
    try:
        await service.delete_layout(layout_id, user_id)
    except LayoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart layout '{layout_id}' not found.",
        )


@router.get(
    "/{layout_id}/export",
    response_model=ChartLayoutExportEnvelope,
    summary="Export chart layout document",
    description="Generates a validated portable JSON configuration envelope.",
)
async def export_chart_layout(
    layout_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ChartLayoutService, Depends(get_chart_layout_service)],
) -> ChartLayoutExportEnvelope:
    user_id = uuid.UUID(principal.user_id)
    try:
        return await service.export_layout(layout_id, user_id)
    except LayoutNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chart layout '{layout_id}' not found.",
        )
