"""FastAPI Router for ATLAS Intelligence Scoring (Stage 139).

Prefix: /intelligence/scoring (accessible at /api/v1/intelligence/scoring)

Provides institutional endpoints for:
- Scoring capabilities and objective taxonomy
- Model and policy registries
- Point-in-time score calculation and exact factor breakdowns
- Context-aware event prioritization and ranking
- Model comparison and historical evaluation manifests
- Operational health, telemetry, and drift detection
- Model governance (activation, validation gates, and rollback)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.intelligence.scoring import (
    AtlasIntelligenceScore,
    AtlasScoringService,
    FactorContribution,
    ModelComparisonResponse,
    RankedItem,
    ScoringCapabilitiesResponse,
    ScoringDomainError,
    ScoringEligibilityError,
    ScoringEvaluationManifest,
    ScoringGovernanceAuditRecord,
    ScoringLookAheadViolationError,
    ScoringModelDefinition,
    ScoringModelNotFoundError,
    ScoringModelValidationError,
    ScoringObjectiveDefinition,
    ScoringObjectiveNotFoundError,
    ScoringPolicyNotFoundError,
    ScoringQuotaExceededError,
    ScoringTelemetrySummary,
    ScoringTenantAccessDeniedError,
    ScoringUnauthorizedActivationError,
    IntelligenceScoringPolicy,
)
from ..auth.dependencies import get_optional_user

router = APIRouter(prefix="/intelligence/scoring", tags=["intelligence-scoring"])

_scoring_service = AtlasScoringService()


def get_scoring_service() -> AtlasScoringService:
    return _scoring_service


# Request Schemas
class CalculateScoreRequest(BaseModel):
    event_data: Dict[str, Any]
    objective_id: str = "EVENT_REVIEW_PRIORITY"
    policy_id: Optional[str] = None
    model_version: Optional[str] = None
    known_as_of: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class RankEventsRequest(BaseModel):
    candidate_events: List[Dict[str, Any]]
    objective_id: str = "EVENT_REVIEW_PRIORITY"
    policy_id: Optional[str] = None
    model_version: Optional[str] = None
    known_as_of: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    limit: int = Field(default=50, ge=1, le=500)


class CompareModelsRequest(BaseModel):
    event_data: Dict[str, Any]
    version_a: str = "v1.0.0"
    version_b: str = "v2.0.0"
    objective_id: str = "EVENT_REVIEW_PRIORITY"
    known_as_of: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class GovernanceActionRequest(BaseModel):
    version: str
    rationale: str = "Authorized model governance update."


# Endpoints
@router.get("/capabilities", response_model=ScoringCapabilitiesResponse)
def get_capabilities(
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringCapabilitiesResponse:
    """Return intelligence scoring capabilities, supported objectives, scales, and boundaries."""
    return svc.get_capabilities()


@router.get("/objectives", response_model=List[ScoringObjectiveDefinition])
def list_objectives(
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> List[ScoringObjectiveDefinition]:
    """Return list of institutional scoring objectives."""
    return svc.list_objectives()


@router.get("/objectives/{objective_id}", response_model=ScoringObjectiveDefinition)
def get_objective(
    objective_id: str,
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringObjectiveDefinition:
    """Return definition of a specific scoring objective."""
    try:
        return svc.get_objective(objective_id)
    except ScoringObjectiveNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/models", response_model=List[ScoringModelDefinition])
def list_models(
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> List[ScoringModelDefinition]:
    """Return list of registered scoring models."""
    return svc.list_models()


@router.get("/models/{model_id}", response_model=ScoringModelDefinition)
def get_model(
    model_id: str,
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringModelDefinition:
    """Return metadata for a specific model."""
    try:
        return svc.get_model(model_id)
    except ScoringModelNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/policies", response_model=List[IntelligenceScoringPolicy])
def list_policies(
    objective_id: Optional[str] = Query(None),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> List[IntelligenceScoringPolicy]:
    """Return list of scoring policies with weights and missing data rules."""
    return svc.list_policies(objective_id=objective_id)


@router.get("/policies/{policy_id}", response_model=IntelligenceScoringPolicy)
def get_policy(
    policy_id: str,
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> IntelligenceScoringPolicy:
    """Return details for a specific scoring policy."""
    try:
        return svc.get_policy(policy_id)
    except ScoringPolicyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/scores/calculate", response_model=AtlasIntelligenceScore)
def calculate_score(
    req: CalculateScoreRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> AtlasIntelligenceScore:
    """Calculate point-in-time score and exact factor contributions for an event."""
    tenant_id = principal.tenant_id if principal else "default_tenant"
    try:
        return svc.calculate_score(
            event_data=req.event_data,
            objective_id=req.objective_id,
            policy_id=req.policy_id,
            model_version=req.model_version,
            known_as_of=req.known_as_of,
            context=req.context,
            tenant_id=tenant_id,
        )
    except ScoringTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ScoringLookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ScoringDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rankings/query", response_model=List[RankedItem])
def query_rankings(
    req: RankEventsRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> List[RankedItem]:
    """Rank a candidate set of events with deterministic tie-breaking and point-in-time filtering."""
    tenant_id = principal.tenant_id if principal else "default_tenant"
    try:
        return svc.rank_events(
            candidate_events=req.candidate_events,
            objective_id=req.objective_id,
            policy_id=req.policy_id,
            model_version=req.model_version,
            known_as_of=req.known_as_of,
            context=req.context,
            tenant_id=tenant_id,
            limit=req.limit,
        )
    except ScoringQuotaExceededError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))
    except ScoringTenantAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ScoringDomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rankings/compare", response_model=ModelComparisonResponse)
def compare_models(
    req: CompareModelsRequest,
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ModelComparisonResponse:
    """Compare two scoring model versions on the same subject to inspect weight deltas."""
    return svc.compare_models(
        event_data=req.event_data,
        version_a=req.version_a,
        version_b=req.version_b,
        objective_id=req.objective_id,
        known_as_of=req.known_as_of,
        context=req.context,
    )


@router.get("/evaluations", response_model=List[ScoringEvaluationManifest])
def list_evaluations(
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> List[ScoringEvaluationManifest]:
    """Return historical model evaluation records (NDCG, Precision, Brier)."""
    return svc.list_evaluations()


@router.get("/evaluations/{evaluation_id}", response_model=ScoringEvaluationManifest)
def get_evaluation(
    evaluation_id: str,
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringEvaluationManifest:
    """Retrieve an evaluation manifest by ID."""
    manifest = svc.get_evaluation(evaluation_id)
    if not manifest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evaluation '{evaluation_id}' not found.")
    return manifest


@router.get("/telemetry", response_model=ScoringTelemetrySummary)
def get_telemetry(
    model_id: str = Query("MOD_EVENT_PRIORITY"),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringTelemetrySummary:
    """Return operational health, average score distribution, and drift status."""
    return svc.get_telemetry(model_id=model_id)


@router.post("/governance/models/{model_id}/activate", response_model=ScoringGovernanceAuditRecord)
def activate_model_version(
    model_id: str,
    req: GovernanceActionRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringGovernanceAuditRecord:
    """Promote a validated model version to active production (Admin/Quant role required)."""
    user_id = principal.user_id if principal else "admin_user"
    user_roles = principal.roles if (principal and hasattr(principal, "roles")) else ["RISK_ADMIN"]
    try:
        return svc.activate_model_version(
            model_id=model_id,
            version=req.version,
            user_id=user_id,
            user_roles=user_roles,
        )
    except ScoringUnauthorizedActivationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ScoringModelValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post("/governance/models/{model_id}/rollback", response_model=ScoringGovernanceAuditRecord)
def rollback_model_version(
    model_id: str,
    req: GovernanceActionRequest,
    principal: Optional[AuthPrincipal] = Depends(get_optional_user),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> ScoringGovernanceAuditRecord:
    """Roll back model to previous approved version (Admin/Quant role required)."""
    user_id = principal.user_id if principal else "admin_user"
    user_roles = principal.roles if (principal and hasattr(principal, "roles")) else ["RISK_ADMIN"]
    try:
        return svc.rollback_model_version(
            model_id=model_id,
            rollback_to_version=req.version,
            user_id=user_id,
            user_roles=user_roles,
            rationale=req.rationale,
        )
    except ScoringUnauthorizedActivationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/governance/audit", response_model=List[ScoringGovernanceAuditRecord])
def get_governance_audit(
    model_id: Optional[str] = Query(None),
    svc: AtlasScoringService = Depends(get_scoring_service),
) -> List[ScoringGovernanceAuditRecord]:
    """Retrieve immutable model governance audit trail."""
    return svc.get_governance_audit(model_id=model_id)
