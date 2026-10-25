"""FastAPI Router for Watchlist Enrichment (Stage 79).

Exposes authenticated REST endpoints under `/watchlists`:
- POST /watchlists/{id}/enrichment/query: Batch query financial enrichment values for watchlist items.
- GET /watchlists/enrichment/capabilities: Discover supported enrichment columns and metadata.
"""

import logging
import uuid
from decimal import Decimal
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.auth import AuthPrincipal
from atlas.watchlists.repository import WatchlistRepository

from .models import (
    EnrichmentCategory,
    EnrichmentColumnMetadata,
    WatchlistEnrichmentRequest,
    WatchlistEnrichmentResponse,
)
from .planner import EnrichmentItemContext
from .registry import list_enrichment_columns
from .service import WatchlistEnrichmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlists", tags=["Watchlist Enrichment"])


def get_current_user() -> AuthPrincipal:
    """Dependency placeholder replaced by atlas_api auth in production."""
    raise NotImplementedError


def get_db_session() -> AsyncSession:
    """Dependency placeholder replaced by atlas_api database session in production."""
    raise NotImplementedError


@router.get(
    "/enrichment/capabilities",
    response_model=List[EnrichmentColumnMetadata],
    summary="List enrichment capabilities",
    description="Returns the full catalog of registered financial enrichment column definitions.",
)
async def get_enrichment_capabilities(
    category: Optional[EnrichmentCategory] = Query(None, description="Optional category filter"),
) -> List[EnrichmentColumnMetadata]:
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
) -> WatchlistEnrichmentResponse:
    user_id = uuid.UUID(principal.user_id)
    repo = WatchlistRepository(session)
    watchlist = await repo.get_by_id(id, owner_user_id=user_id)
    if watchlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WATCHLIST_NOT_FOUND", "message": f"Watchlist {id} not found."},
        )

    # Convert items to EnrichmentItemContext
    items_context: List[EnrichmentItemContext] = []
    quotes_map: dict[uuid.UUID, Decimal] = {}

    for item in watchlist.items:
        if request.item_ids and item.item_id not in request.item_ids:
            continue

        asset_class = getattr(item, "asset_class", "equity") or "equity"
        quote_currency = getattr(item, "quote_currency", "USD") or "USD"
        market_series = f"{item.instrument_entity_id}:1D:CLOSE"

        items_context.append(
            EnrichmentItemContext(
                item_id=item.item_id,
                instrument_id=item.instrument_entity_id,
                market_series_id=market_series,
                asset_class=asset_class,
                quote_currency=quote_currency,
                company_id=getattr(item, "company_id", None),
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
