import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException

from atlas_api.dependencies import get_db_session
from sqlalchemy.orm import Session

from atlas.authorization.dependencies import require_permissions
from atlas.search.models import GlobalSearchRequest, GlobalSearchResponse
from atlas.search.settings import GlobalSearchSettings
from atlas.search.repository import GlobalSearchRepository
from atlas.search.service import GlobalSearchService
from atlas.entities.types import EntityTypeKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

def get_search_service(session: Session = Depends(get_db_session)) -> GlobalSearchService:
    settings = GlobalSearchSettings()
    repo = GlobalSearchRepository(session, settings)
    return GlobalSearchService(repo, settings)


@router.get("/entities", response_model=GlobalSearchResponse)
def search_entities(
    q: str = Query(..., description="The search query"),
    entity_types: Optional[List[EntityTypeKey]] = Query(None, description="Filter by entity types"),
    limit: Optional[int] = Query(None, description="Maximum number of results to return"),
    service: GlobalSearchService = Depends(get_search_service),
    _=Depends(require_permissions(["atlas.access"]))
):
    try:
        request = GlobalSearchRequest(
            query=q,
            entity_types=entity_types,
            limit=limit
        )
        return service.search_entities(request)
    except ValueError as e:
        if str(e) == "SEARCH_QUERY_TOO_LONG":
            raise HTTPException(status_code=400, detail="Search query is too long")
        # For normalization errors where the string is empty
        return GlobalSearchResponse(results=[])
    except Exception as e:
        logger.error(f"Global search error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Search backend unavailable")
