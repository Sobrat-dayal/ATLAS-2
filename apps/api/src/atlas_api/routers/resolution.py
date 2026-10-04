from typing import Optional, List
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.resolution.schemas import EntityResolutionResponse, EntityResolutionRequest
from atlas.resolution.service import EntityResolutionService
from atlas_api.dependencies import get_db_session

router = APIRouter(prefix="/resolution", tags=["Resolution"])


def get_resolution_service(
    session: AsyncSession = Depends(get_db_session),
) -> EntityResolutionService:
    return EntityResolutionService(session)


@router.get("/resolve", response_model=EntityResolutionResponse)
async def resolve_entity(
    query: str = Query(..., min_length=1, max_length=512, description="The string to resolve (e.g. ticker, name, identifier)"),
    entity_type_hints: Optional[List[str]] = Query(None),
    identifier_scheme_hint: Optional[str] = Query(None),
    scope_entity_id: Optional[uuid.UUID] = Query(None),
    namespace: Optional[str] = Query(None),
    language_code: Optional[str] = Query(None),
    include_historical: bool = Query(False),
    max_candidates: int = Query(10, ge=1, le=25),
    service: EntityResolutionService = Depends(get_resolution_service),
):
    """
    Deterministically resolves a string to one or more Universal Entities.
    """
    req = EntityResolutionRequest(
        query=query,
        entity_type_hints=entity_type_hints,
        identifier_scheme_hint=identifier_scheme_hint,
        scope_entity_id=scope_entity_id,
        namespace=namespace,
        language_code=language_code,
        include_historical=include_historical,
        max_candidates=max_candidates
    )
    return await service.resolve_entity(req)
