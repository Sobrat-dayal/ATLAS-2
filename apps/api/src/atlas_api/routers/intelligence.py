"""FastAPI Router for ATLAS INTELLIGENCE V1 (Stage 138).

Prefix: /intelligence (accessible at /api/v1/intelligence)

Provides institutional endpoints for:
- Intelligence Command Center capabilities & guarantees
- Unified Overview orchestration (events, monetary policy, earnings, physical world)
- Canonical investigation presets & panel descriptors
- Typed unified search with entity disambiguation
- Source health, freshness, and outage resilience
- Canonical entity context resolution
- Structured investigation persistence & tenant authorization
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.intelligence import (
    AtlasIntelligenceService,
    IntelligenceEntityNotFoundError,
    IntelligenceInvestigationContext,
    IntelligenceInvestigationPreset,
    IntelligenceLookAheadViolationError,
    IntelligenceOverviewResponse,
    IntelligencePanelDefinition,
    IntelligenceSavedInvestigation,
    IntelligenceSearchResult,
    IntelligenceTenantAccessDeniedError,
    SectionStatus,
    SourceFreshnessRecord,
)
from ..auth.dependencies import get_optional_user

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

# Singleton service instance
_intelligence_service = AtlasIntelligenceService()


def get_intelligence_service() -> AtlasIntelligenceService:
    return _intelligence_service


# -----------------------------------------------------------------------------
# Request Models
# -----------------------------------------------------------------------------
class OverviewRequest(BaseModel):
    as_of: Optional[datetime] = None
    selected_entity_id: Optional[str] = None
    selected_portfolio_id: Optional[str] = None


class UnifiedSearchRequest(BaseModel):
    query: str
    limit: int = 15


class EntityContextRequest(BaseModel):
    entity_id: str
    node_type: Optional[GraphNodeType] = None
    as_of: Optional[datetime] = None


class SaveInvestigationRequest(BaseModel):
    investigation_id: str
    title: str
    description: Optional[str] = None
    primary_subject: Optional[str] = None
    preset_id: Optional[str] = None
    context: IntelligenceInvestigationContext


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.get("/capabilities")
def get_capabilities(
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> Dict[str, Any]:
    """Return Stage 138 Intelligence capabilities and institutional guarantees."""
    return service.get_capabilities()


@router.post("/overview", response_model=IntelligenceOverviewResponse)
def get_overview(
    req: OverviewRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> IntelligenceOverviewResponse:
    """Generate the unified Overview command center payload with partial resilience."""
    tenant_id = user.tenant_id if user else None
    try:
        return service.get_overview(
            user_tenant_id=tenant_id,
            as_of=req.as_of,
            selected_entity_id=req.selected_entity_id,
            selected_portfolio_id=req.selected_portfolio_id
        )
    except IntelligenceLookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.code, "message": str(e)})


@router.get("/presets", response_model=List[IntelligenceInvestigationPreset])
def list_presets(
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> List[IntelligenceInvestigationPreset]:
    """List canonical multi-panel investigation presets."""
    return service.list_presets()


@router.get("/panels", response_model=List[IntelligencePanelDefinition])
def list_panels(
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> List[IntelligencePanelDefinition]:
    """List registered intelligence panel descriptors."""
    return service.list_panels()


@router.post("/search", response_model=List[IntelligenceSearchResult])
def search_intelligence(
    req: UnifiedSearchRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> List[IntelligenceSearchResult]:
    """Execute typed search with strict entity disambiguation across events, entities, and sources."""
    tenant_id = user.tenant_id if user else None
    return service.search(query=req.query, limit=req.limit, user_tenant_id=tenant_id)


@router.get("/sources/status", response_model=List[SourceFreshnessRecord])
def get_sources_status(
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> List[SourceFreshnessRecord]:
    """Return factual source health, freshness, and dataset telemetry."""
    return service.get_sources_status()


@router.post("/sources/{source_id}/simulate-outage")
def simulate_source_outage(
    source_id: str,
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> Dict[str, Any]:
    """Simulate an upstream data provider outage for resilience testing."""
    service.source_registry.simulate_outage(source_id)
    return {"status": "OUTAGE_SIMULATED", "source_id": source_id}


@router.post("/sources/{source_id}/restore")
def restore_source(
    source_id: str,
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> Dict[str, Any]:
    """Restore provider back to healthy status."""
    service.source_registry.restore_source(source_id)
    return {"status": "RESTORED", "source_id": source_id}


@router.post("/entities/context")
def resolve_entity_context(
    req: EntityContextRequest,
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> Dict[str, Any]:
    """Resolve canonical entity intelligence context."""
    try:
        return service.resolve_entity_context(
            entity_id=req.entity_id,
            node_type=req.node_type,
            as_of=req.as_of
        )
    except IntelligenceEntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": e.code, "message": str(e)})


@router.post("/investigations", response_model=IntelligenceSavedInvestigation)
def save_investigation(
    req: SaveInvestigationRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> IntelligenceSavedInvestigation:
    """Persist a structured investigation record."""
    owner_id = user.user_id if user else "ANONYMOUS_ANALYST"
    tenant_id = user.tenant_id if user else req.context.tenant_id

    saved = IntelligenceSavedInvestigation(
        investigation_id=req.investigation_id,
        title=req.title,
        description=req.description,
        owner_id=owner_id,
        tenant_id=tenant_id,
        primary_subject=req.primary_subject,
        preset_id=req.preset_id,
        context=req.context
    )
    return service.save_investigation(saved, user_tenant_id=tenant_id)


@router.get("/investigations/{investigation_id}", response_model=IntelligenceSavedInvestigation)
def get_investigation(
    investigation_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasIntelligenceService = Depends(get_intelligence_service)
) -> IntelligenceSavedInvestigation:
    """Retrieve a saved investigation verifying tenant permissions."""
    tenant_id = user.tenant_id if user else None
    try:
        return service.get_investigation(investigation_id, requesting_tenant_id=tenant_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Investigation '{investigation_id}' not found.")
    except IntelligenceTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": e.code, "message": str(e)})
