import uuid
from typing import Optional, List, Annotated

from fastapi import APIRouter, Depends, Query
from atlas.capabilities import CapabilityGateway, CapabilityRef, CapabilityExecutionContext
from atlas_api.capabilities_dependencies import get_capability_gateway, get_capability_execution_context
from atlas.resolution.schemas import EntityResolutionResponse

router = APIRouter(prefix="/resolution", tags=["Resolution"])


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
    gateway: Annotated[CapabilityGateway, Depends(get_capability_gateway)] = None,
    context: Annotated[CapabilityExecutionContext, Depends(get_capability_execution_context)] = None,
):
    """
    Deterministically resolves a string to one or more Universal Entities.
    """
    payload = {
        "query": query,
        "entity_type_hints": entity_type_hints,
        "identifier_scheme_hint": identifier_scheme_hint,
        "scope_entity_id": scope_entity_id,
        "namespace": namespace,
        "language_code": language_code,
        "include_historical": include_historical,
        "max_candidates": max_candidates
    }
    
    result = await gateway.execute(
        ref=CapabilityRef(key="entity.resolve"),
        payload=payload,
        execution_context=context
    )
    return result
