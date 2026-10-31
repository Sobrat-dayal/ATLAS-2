"""FastAPI Router for ATLAS God's Eye Financial Intelligence (Stage 140).

Prefix: /intelligence/gods-eye (accessible at /api/v1/intelligence/gods-eye)

Provides institutional endpoints for:
- God's Eye capabilities and safety guarantees
- 8 Canonical Investigation Lenses
- Cross-domain investigation execution
- Bitemporal "World Time Travel" historical reconstruction
- Entity situational awareness queries
- Historical vintage comparisons
- Read-only AI tool execution (atlas.gods_eye.investigate)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.intelligence.gods_eye import (
    AtlasGodsEyeService,
    GodsEyeContext,
    GodsEyeDomainError,
    GodsEyeEntityNotFoundError,
    GodsEyeInvestigationResult,
    GodsEyeLensDefinition,
    GodsEyeLensType,
    GodsEyeLookAheadViolationError,
    GodsEyeQuotaExceededError,
    GodsEyeSourceUnavailableError,
    GodsEyeTenantAccessDeniedError,
    GodsEyeTraversalLimitExceededError,
    GodsEyeViewMode,
)
from ..auth.dependencies import get_optional_user

router = APIRouter(prefix="/intelligence/gods-eye", tags=["gods-eye-intelligence"])

_gods_eye_service = AtlasGodsEyeService()


def get_gods_eye_service() -> AtlasGodsEyeService:
    return _gods_eye_service


# -----------------------------------------------------------------------------
# Request Schemas
# -----------------------------------------------------------------------------
class InvestigateRequest(BaseModel):
    lens: GodsEyeLensType = GodsEyeLensType.GLOBAL_EVENTS
    as_of: Optional[datetime] = None
    selected_entity_id: Optional[str] = None
    selected_event_id: Optional[str] = None
    selected_portfolio_id: Optional[str] = None
    tenant_id: str = "default"
    view_mode: GodsEyeViewMode = GodsEyeViewMode.TWO_DIMENSIONAL
    max_graph_depth: int = 2
    max_entities: int = 50
    scoring_policy_id: Optional[str] = None
    search_query: Optional[str] = None


class HistoricalReconstructionRequest(BaseModel):
    as_of: datetime
    lens: GodsEyeLensType = GodsEyeLensType.HISTORICAL_RESEARCH
    selected_entity_id: Optional[str] = None


class CompareVintagesRequest(BaseModel):
    entity_id: str
    as_of_v1: datetime
    as_of_v2: datetime


class AiToolInvestigateRequest(BaseModel):
    lens: str = "GLOBAL_EVENTS"
    as_of: Optional[str] = None
    entity_id: Optional[str] = None
    event_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    max_depth: int = 2
    query: Optional[str] = None


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.get("/capabilities", summary="God's Eye Capabilities and Guarantees")
def get_capabilities(
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> Dict[str, Any]:
    return service.get_capabilities()


@router.get("/lenses", summary="List Canonical Investigation Lenses")
def list_lenses(
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> List[GodsEyeLensDefinition]:
    return service.list_lenses()


@router.get("/lens/{lens_id}", summary="Get Single Lens Definition")
def get_lens(
    lens_id: str,
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> GodsEyeLensDefinition:
    return service.get_lens(lens_id)


@router.post("/investigate", summary="Execute God's Eye Investigation")
def investigate(
    req: InvestigateRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> GodsEyeInvestigationResult:
    try:
        ctx = GodsEyeContext(
            lens=req.lens,
            as_of=req.as_of,
            selected_entity_id=req.selected_entity_id,
            selected_event_id=req.selected_event_id,
            selected_portfolio_id=req.selected_portfolio_id,
            tenant_id=req.tenant_id,
            user_id=principal.user_id if principal else None,
            view_mode=req.view_mode,
            max_graph_depth=req.max_graph_depth,
            max_entities=req.max_entities,
            scoring_policy_id=req.scoring_policy_id,
            search_query=req.search_query,
        )
        return service.investigate(ctx, principal=principal)
    except GodsEyeLookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except GodsEyeTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except GodsEyeTraversalLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except GodsEyeSourceUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.message)
    except GodsEyeDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/entity/{entity_id}", summary="Entity Situational Awareness")
def get_entity_situational_awareness(
    entity_id: str,
    lens: GodsEyeLensType = GodsEyeLensType.CORPORATE_INTELLIGENCE,
    as_of: Optional[datetime] = None,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> GodsEyeInvestigationResult:
    try:
        ctx = GodsEyeContext(
            lens=lens,
            as_of=as_of,
            selected_entity_id=entity_id,
            user_id=principal.user_id if principal else None,
        )
        return service.investigate(ctx, principal=principal)
    except GodsEyeLookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except GodsEyeDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/historical-reconstruction", summary="Historical World Reconstruction")
def reconstruct_historical_world(
    req: HistoricalReconstructionRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> GodsEyeInvestigationResult:
    try:
        return service.reconstruct_historical_world(
            as_of=req.as_of,
            lens=req.lens,
            entity_id=req.selected_entity_id,
            principal=principal,
        )
    except GodsEyeLookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except GodsEyeDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/compare-vintages", summary="Compare Historical Vintages")
def compare_vintages(
    req: CompareVintagesRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> Dict[str, Any]:
    try:
        return service.compare_historical_vintages(
            entity_id=req.entity_id,
            as_of_v1=req.as_of_v1,
            as_of_v2=req.as_of_v2,
            principal=principal,
        )
    except GodsEyeDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/ai-tool/investigate", summary="AI Investigation Tool Backend")
def ai_tool_investigate(
    req: AiToolInvestigateRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasGodsEyeService = Depends(get_gods_eye_service),
) -> Dict[str, Any]:
    try:
        return service.execute_ai_investigation_tool(req.model_dump(), principal=principal)
    except GodsEyeLookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except GodsEyeTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except GodsEyeDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

