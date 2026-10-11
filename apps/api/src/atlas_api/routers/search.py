import logging
import time
from typing import List, Optional

from atlas.authorization import PermissionCode
from atlas.entities.types import EntityTypeKey
from atlas.search.models import GlobalSearchRequest, GlobalSearchResponse
from atlas.search.repository import GlobalSearchRepository
from atlas.search.service import GlobalSearchService
from atlas.search.settings import GlobalSearchSettings
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas_api.authorization.dependencies import RequirePermission
from atlas_api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])


def get_search_service(session: AsyncSession = Depends(get_db_session)) -> GlobalSearchService:
    settings = GlobalSearchSettings()
    repo = GlobalSearchRepository(session, settings)
    return GlobalSearchService(repo, settings)


@router.get("/entities", response_model=GlobalSearchResponse)
async def search_entities(
    q: str = Query(..., description="The search query"),
    entity_types: Optional[List[EntityTypeKey]] = Query(None, description="Filter by entity types"),
    limit: Optional[int] = Query(
        None, ge=1, le=50, description="Maximum number of results to return"
    ),
    service: GlobalSearchService = Depends(get_search_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
):
    start_time = time.perf_counter()
    try:
        request = GlobalSearchRequest(query=q, entity_types=entity_types, limit=limit)
        response = await service.search_entities(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "global_search_completed",
            extra={
                "component": "global_search",
                "query_length": len(q),
                "entity_type_filter_count": len(entity_types) if entity_types else 0,
                "result_count": len(response.results),
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response
    except ValueError as e:
        if str(e) == "SEARCH_QUERY_TOO_LONG":
            raise HTTPException(status_code=400, detail="Search query is too long")
        return GlobalSearchResponse(results=[])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Global search error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Search backend unavailable")
