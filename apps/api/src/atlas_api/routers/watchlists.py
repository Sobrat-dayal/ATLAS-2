"""FastAPI Router for Watchlists V1 (Stage 76).

Exposes authenticated REST endpoints under `/watchlists`:
- GET /watchlists: List user's saved watchlists with pagination
- POST /watchlists: Create a new watchlist
- GET /watchlists/{id}: Retrieve watchlist metadata and membership items with qualified snapshots
- PATCH /watchlists/{id}: Rename/update metadata with optimistic revision protection
- DELETE /watchlists/{id}: Delete a watchlist
- POST /watchlists/{id}/items: Add a canonical financial instrument
- DELETE /watchlists/{id}/items/{item_id}: Remove a membership item
- PUT /watchlists/{id}/items/order: Atomically reorder items with revision check
"""

import logging
import uuid
from decimal import Decimal
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import LiveQuoteStateStore
from atlas.watchlists import (
    AddWatchlistItemRequest,
    DuplicateWatchlistItemError,
    InstrumentNotFoundError,
    InvalidReorderRequestError,
    InvalidWatchlistNameError,
    ReorderWatchlistItemsRequest,
    ReorderWatchlistItemsResponse,
    WatchlistCreateRequest,
    WatchlistDetailResponse,
    WatchlistItemNotFoundError,
    WatchlistItemQuotaExceededError,
    WatchlistItemResponse,
    WatchlistListResponse,
    WatchlistNameConflictError,
    WatchlistNotFoundError,
    WatchlistQuotaExceededError,
    WatchlistRepository,
    WatchlistRevisionConflictError,
    WatchlistService,
    WatchlistSummaryResponse,
    WatchlistUpdateRequest,
)
from atlas.watchlists.alerts import alerts_router
from atlas.watchlists.columns import (
    ColumnConfigRevisionConflictError,
    ColumnLimitExceededError,
    ColumnNotFoundError,
    ColumnNotSortableError,
    IncompatibleSortUnitsError,
    InvalidColumnOrderError,
    InvalidColumnWidthError,
    InvalidPinConfigurationError,
    RequiredColumnHiddenError,
    UnsupportedConfigVersionError,
    WatchlistColumnDefinitionResponse,
    WatchlistColumnPreferenceRepository,
    WatchlistColumnPreferencesResponse,
    WatchlistColumnPreferencesUpdateRequest,
    WatchlistColumnService,
    WatchlistRowsResponse,
)
from atlas.watchlists.enrichment import (
    EnrichmentCategory,
    EnrichmentColumnMetadata,
    WatchlistEnrichmentRequest,
    WatchlistEnrichmentResponse,
    WatchlistEnrichmentService,
    list_enrichment_columns,
)
from atlas.watchlists.enrichment.planner import EnrichmentItemContext
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


def get_watchlist_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WatchlistService:
    quote_service = None
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client is not None:
        try:
            quote_store = LiveQuoteStateStore(redis_client)
            quote_service = LiveQuoteService(quote_store)
        except Exception as e:
            logger.warning("Could not instantiate LiveQuoteService from redis: %s", e)

    repository = WatchlistRepository(session)
    return WatchlistService(
        repository=repository,
        quote_service=quote_service,
        db_session=session,
    )


def get_watchlist_column_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WatchlistColumnService:
    watchlist_service = get_watchlist_service(request, session)
    pref_repo = WatchlistColumnPreferenceRepository(session)
    return WatchlistColumnService(
        preference_repository=pref_repo,
        watchlist_repository=watchlist_service.repository,
        watchlist_service=watchlist_service,
    )


@router.get(
    "/columns",
    response_model=list[WatchlistColumnDefinitionResponse],
    summary="List available watchlist columns",
    description="Returns the approved catalog of typed watchlist column definitions.",
)
async def list_column_definitions(
    service: Annotated[WatchlistColumnService, Depends(get_watchlist_column_service)],
) -> list[WatchlistColumnDefinitionResponse]:
    return service.list_column_definitions()


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
    response_model=WatchlistListResponse,
    summary="List user's watchlists",
    description="Lists summary metadata for watchlists owned by the authenticated user.",
)
async def list_watchlists(
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> WatchlistListResponse:
    response.headers["Cache-Control"] = "private, no-store"
    user_id = uuid.UUID(principal.user_id)
    return await service.list_watchlists(owner_user_id=user_id, page=page, page_size=page_size)


@router.post(
    "",
    response_model=WatchlistSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new watchlist",
    description="Creates a new persistent watchlist owned by the authenticated user.",
)
async def create_watchlist(
    request: WatchlistCreateRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> WatchlistSummaryResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        return await service.create_watchlist(owner_user_id=user_id, request=request)
    except WatchlistQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistNameConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except InvalidWatchlistNameError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


@router.get(
    "/{id}",
    response_model=WatchlistDetailResponse,
    summary="Get watchlist details and items",
    description=(
        "Retrieves a watchlist with its ordered canonical financial instrument items "
        "and latest qualified quote snapshots."
    ),
)
async def get_watchlist(
    id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
    page: int = Query(1, ge=1, description="Items page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
) -> WatchlistDetailResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        detail = await service.get_watchlist(
            watchlist_id=id, owner_user_id=user_id, page=page, page_size=page_size
        )
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["ETag"] = f'W/"{detail.revision}"'
        return detail
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.patch(
    "/{id}",
    response_model=WatchlistSummaryResponse,
    summary="Update watchlist metadata",
    description="Updates display name or description with optimistic concurrency protection.",
)
async def update_watchlist(
    id: uuid.UUID,
    request: WatchlistUpdateRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
    if_match: Optional[str] = Header(
        None, description="Optional If-Match header with expected revision"
    ),
) -> WatchlistSummaryResponse:
    user_id = uuid.UUID(principal.user_id)
    expected_rev = _parse_etag(if_match)
    try:
        return await service.update_watchlist(
            watchlist_id=id,
            owner_user_id=user_id,
            request=request,
            expected_revision=expected_rev,
        )
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistRevisionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED
            if if_match
            else status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistNameConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except InvalidWatchlistNameError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a watchlist",
    description="Deletes a watchlist and all of its membership records atomically.",
)
async def delete_watchlist(
    id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> None:
    user_id = uuid.UUID(principal.user_id)
    try:
        await service.delete_watchlist(watchlist_id=id, owner_user_id=user_id)
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.post(
    "/{id}/items",
    response_model=WatchlistItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an instrument to a watchlist",
    description="Adds a canonical financial instrument to the watchlist.",
)
async def add_watchlist_item(
    id: uuid.UUID,
    request: AddWatchlistItemRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> WatchlistItemResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        return await service.add_item(watchlist_id=id, owner_user_id=user_id, request=request)
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except InstrumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except DuplicateWatchlistItemError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistItemQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": e.code, "message": e.message},
        )


@router.delete(
    "/{id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an item from a watchlist",
    description=(
        "Removes an instrument membership entry and reindexes positions to maintain dense ordering."
    ),
)
async def remove_watchlist_item(
    id: uuid.UUID,
    item_id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> None:
    user_id = uuid.UUID(principal.user_id)
    try:
        await service.remove_item(watchlist_id=id, item_id=item_id, owner_user_id=user_id)
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.put(
    "/{id}/items/order",
    response_model=ReorderWatchlistItemsResponse,
    summary="Reorder watchlist items",
    description=(
        "Persists dense reordered positions for all items with revision concurrency control."
    ),
)
async def reorder_watchlist_items(
    id: uuid.UUID,
    request: ReorderWatchlistItemsRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistService, Depends(get_watchlist_service)],
    if_match: Optional[str] = Header(
        None, description="Optional If-Match header with expected revision"
    ),
) -> ReorderWatchlistItemsResponse:
    user_id = uuid.UUID(principal.user_id)
    # If If-Match header provided, override or verify with request body expected_revision
    if if_match:
        parsed_header_rev = _parse_etag(if_match)
        if parsed_header_rev is not None and parsed_header_rev != request.expected_revision:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail={
                    "code": "REVISION_CONFLICT",
                    "message": (
                        f"If-Match revision ({parsed_header_rev}) conflicts with "
                        f"payload revision ({request.expected_revision})"
                    ),
                },
            )

    try:
        return await service.reorder_items(watchlist_id=id, owner_user_id=user_id, request=request)
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except WatchlistRevisionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED
            if if_match
            else status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except InvalidReorderRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


# =============================================================================
# Stage 77: Watchlist Columns & Preferences Endpoints
# =============================================================================


@router.get(
    "/{id}/columns",
    response_model=WatchlistColumnPreferencesResponse,
    summary="Get watchlist column preferences",
    description="Retrieves the column configuration and revision for the owned watchlist.",
)
async def get_watchlist_column_preferences(
    id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistColumnService, Depends(get_watchlist_column_service)],
) -> WatchlistColumnPreferencesResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        prefs = await service.get_preferences(watchlist_id=id, owner_user_id=user_id)
        response.headers["ETag"] = f'W/"{prefs.revision}"'
        response.headers["Cache-Control"] = "private, no-cache"
        return prefs
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.put(
    "/{id}/columns",
    response_model=WatchlistColumnPreferencesResponse,
    summary="Update watchlist column preferences",
    description="Saves normalized column configuration with optimistic concurrency protection.",
)
async def update_watchlist_column_preferences(
    id: uuid.UUID,
    request: WatchlistColumnPreferencesUpdateRequest,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistColumnService, Depends(get_watchlist_column_service)],
    if_match: Optional[str] = Header(
        None, description="Optional If-Match header with expected revision"
    ),
) -> WatchlistColumnPreferencesResponse:
    user_id = uuid.UUID(principal.user_id)
    expected_rev = request.expected_revision
    if if_match:
        parsed_header_rev = _parse_etag(if_match)
        if parsed_header_rev is not None:
            expected_rev = parsed_header_rev

    req_with_rev = WatchlistColumnPreferencesUpdateRequest(
        configuration=request.configuration,
        expected_revision=expected_rev,
    )

    try:
        updated = await service.update_preferences(
            watchlist_id=id, owner_user_id=user_id, request=req_with_rev
        )
        response.headers["ETag"] = f'W/"{updated.revision}"'
        return updated
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except ColumnConfigRevisionConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED
            if if_match
            else status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message},
        )
    except (
        RequiredColumnHiddenError,
        InvalidColumnOrderError,
        InvalidColumnWidthError,
        InvalidPinConfigurationError,
        ColumnLimitExceededError,
        ColumnNotFoundError,
        UnsupportedConfigVersionError,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


@router.post(
    "/{id}/columns/reset",
    response_model=WatchlistColumnPreferencesResponse,
    summary="Reset watchlist column preferences",
    description="Resets the watchlist table configuration back to canonical default.",
)
async def reset_watchlist_column_preferences(
    id: uuid.UUID,
    response: Response,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistColumnService, Depends(get_watchlist_column_service)],
) -> WatchlistColumnPreferencesResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        res = await service.reset_preferences(watchlist_id=id, owner_user_id=user_id)
        response.headers["ETag"] = f'W/"{res.revision}"'
        return res
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )


@router.get(
    "/{id}/rows",
    response_model=WatchlistRowsResponse,
    summary="Get projected watchlist rows",
    description=(
        "Projects watchlist rows into typed cell values across columns with global sorting."
    ),
)
async def get_projected_watchlist_rows(
    id: uuid.UUID,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[WatchlistColumnService, Depends(get_watchlist_column_service)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_column_id: Optional[str] = Query(None, description="Optional column ID to sort by"),
    sort_direction: Optional[str] = Query(
        None, pattern="^(asc|desc)$", description="Sort direction"
    ),
) -> WatchlistRowsResponse:
    user_id = uuid.UUID(principal.user_id)
    try:
        return await service.get_projected_rows(
            watchlist_id=id,
            owner_user_id=user_id,
            page=page,
            page_size=page_size,
            sort_column_id=sort_column_id,
            sort_direction=sort_direction,
        )
    except WatchlistNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message},
        )
    except (ColumnNotSortableError, IncompatibleSortUnitsError, ColumnNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        )


# =============================================================================
# Stage 79: Enrichment Endpoints
# =============================================================================


@router.get(
    "/enrichment/capabilities",
    response_model=list[EnrichmentColumnMetadata],
    summary="List enrichment capabilities",
    description="Returns the full catalog of registered financial enrichment column definitions.",
)
async def get_enrichment_capabilities(
    category: Optional[EnrichmentCategory] = Query(None, description="Optional category filter"),
) -> list[EnrichmentColumnMetadata]:
    """Returns supported enrichment column specifications."""
    return list_enrichment_columns(category=category)


@router.post(
    "/{id}/enrichment/query",
    response_model=WatchlistEnrichmentResponse,
    summary="Query watchlist enrichment",
    description="Batch resolves company fundamentals, ratios, technicals, events, and news for watchlist items.",
)
async def query_watchlist_enrichment(
    id: uuid.UUID,
    request: WatchlistEnrichmentRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    watchlist_service: Annotated[WatchlistService, Depends(get_watchlist_service)],
) -> WatchlistEnrichmentResponse:
    user_id = uuid.UUID(principal.user_id)
    repo = WatchlistRepository(session)
    watchlist = await repo.get_by_id(id, owner_user_id=user_id)
    if watchlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WATCHLIST_NOT_FOUND", "message": f"Watchlist {id} not found."},
        )

    # Resolve items with latest quotes and metadata
    all_items = watchlist.items
    resolved_items = await watchlist_service._resolve_items_metadata_and_quotes(all_items)

    items_context: list[EnrichmentItemContext] = []
    quotes_map: dict[uuid.UUID, Decimal] = {}

    for item_resp in resolved_items:
        if request.item_ids and item_resp.id not in request.item_ids:
            continue

        inst_id = item_resp.instrument_entity_id
        if item_resp.last_price is not None:
            try:
                quotes_map[inst_id] = Decimal(str(item_resp.last_price))
            except Exception:
                pass

        items_context.append(
            EnrichmentItemContext(
                item_id=item_resp.id,
                instrument_id=inst_id,
                market_series_id=item_resp.market_series_id,
                asset_class=item_resp.asset_class or "equity",
                quote_currency=item_resp.quote_currency or "USD",
                company_id=item_resp.issuer_entity_id,
            )
        )

    service = WatchlistEnrichmentService(session=session)
    return await service.execute_enrichment_query(
        watchlist_id=id,
        membership_revision=watchlist.revision,
        items=items_context,
        request=request,
        quotes_map=quotes_map,
    )


# Mount Watchlist Alerts V1 subrouter (Stage 80)
router.include_router(alerts_router)

