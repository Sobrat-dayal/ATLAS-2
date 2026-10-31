"""FastAPI Router for ATLAS Financial and Economic Exposure Engine (Stage 137).

Prefixes:
- /intelligence/exposure
- /exposure (aliased for direct module access)

Provides institutional endpoints for:
- Capabilities and registered measure definitions
- Company geographic and segment revenue exposure analysis
- Portfolio holding weights, net/gross exposure, and look-through
- Event-driven exposure linking knowledge graph events to financial subjects
- Deterministic user scenario shock execution
- Point-in-time calculation lineage and coverage summaries
- Reference test fixtures (Tests A through X)
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.exposure import (
    AnalysisRunStatus,
    AtlasExposureEngineService,
    AtlasExposureResult,
    ConsolidationBasis,
    CoverageStatus,
    ExposureAnalysisRun,
    ExposureCoverageSummary,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureMeasureDefinition,
    ExposureRelationshipStrength,
    ExposureScenarioDefinition,
    ExposureScenarioRun,
    ExposureScenarioShock,
    ExposureType,
    UncertaintyClass,
)
from atlas.exposure.errors import (
    CycleDetectedError,
    DoubleCountingError,
    ExposureDomainError,
    IncompatiblePeriodError,
    InvalidDenominatorError,
    LookAheadViolationError,
    MissingCurrencyRateError,
    ProhibitedInferenceError,
    SourceLicenseRevokedError,
    TenantExposureAccessDeniedError,
)
from atlas.exposure.calculations.portfolio import PortfolioPosition
from atlas.exposure.seed import (
    COMPANY_ACME,
    COMPANY_BETA,
    PORTFOLIO_ALPHA,
    REGION_EUROPE,
    get_fixture_a_geographic_revenue,
    get_fixture_b_facility_count,
    get_fixture_c_portfolio_sector,
    get_fixture_d_long_short,
    get_fixture_e_fund_lookthrough,
    get_fixture_f_fund_cycle,
    get_fixture_g_consolidation,
    get_fixture_h_minority_ownership,
    get_fixture_k_interest_rate_sensitivity,
    get_fixture_t_scenario,
    get_fixture_u_derivative,
    get_fixture_x_geographic_residual,
)
from ..auth.dependencies import get_optional_user

router = APIRouter(prefix="/intelligence/exposure", tags=["exposure"])

# Singleton service instance
_exposure_service = AtlasExposureEngineService()


def get_exposure_service() -> AtlasExposureEngineService:
    return _exposure_service


# -----------------------------------------------------------------------------
# Request / Response Schemas
# -----------------------------------------------------------------------------
class CompanyAnalysisRequest(BaseModel):
    company_ref: CanonicalGraphNodeRef
    segments: List[Dict[str, Any]]
    total_consolidated_revenue: Decimal
    currency: str = "USD"
    period: str = "FY2024"
    as_of: Optional[datetime] = None


class PortfolioAnalysisRequest(BaseModel):
    portfolio_ref: CanonicalGraphNodeRef
    positions: List[PortfolioPosition]
    nav: Optional[Decimal] = None
    currency: str = "USD"
    as_of: Optional[datetime] = None


class EventExposureRequest(BaseModel):
    event_ref: CanonicalGraphNodeRef
    subject_ref: CanonicalGraphNodeRef
    exposure_type: ExposureType
    exposure_domain: ExposureDomain
    measure_id: str
    amount: Optional[Decimal] = None
    currency: Optional[str] = "USD"
    percentage: Optional[Decimal] = None
    graph_path_ids: List[str] = Field(default_factory=list)
    explanation: str


class ScenarioRunRequest(BaseModel):
    scenario_id: str
    scenario_name: str
    shocks: List[ExposureScenarioShock]
    positions: List[Dict[str, Any]]
    base_currency: str = "USD"


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.get("/capabilities")
def get_capabilities(
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> Dict[str, Any]:
    """Return engine metadata, supported domains, registered measures, and compliance guarantees."""
    return service.get_capabilities()


@router.get("/measures")
def list_measures(
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> List[ExposureMeasureDefinition]:
    """List all registered exposure measure definitions with numerators and denominators."""
    return service.list_measures()


@router.post("/analyze/company", status_code=status.HTTP_200_OK)
def analyze_company_exposure(
    req: CompanyAnalysisRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> ExposureAnalysisRun:
    """Run geographic revenue exposure calculation for a company."""
    tenant_id = user.tenant_id if user else None
    try:
        return service.analyze_company(
            company_ref=req.company_ref,
            segments=req.segments,
            total_consolidated_revenue=req.total_consolidated_revenue,
            currency=req.currency,
            period=req.period,
            as_of=req.as_of,
            tenant_id=tenant_id
        )
    except InvalidDenominatorError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error": e.code, "message": str(e)})
    except LookAheadViolationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": e.code, "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/analyze/portfolio", status_code=status.HTTP_200_OK)
def analyze_portfolio_exposure(
    req: PortfolioAnalysisRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> ExposureAnalysisRun:
    """Run portfolio exposure analysis (Net vs Gross, Sectors, Countries)."""
    tenant_id = user.tenant_id if user else req.portfolio_ref.tenant_id
    try:
        return service.analyze_portfolio(
            portfolio_ref=req.portfolio_ref,
            positions=req.positions,
            nav=req.nav,
            currency=req.currency,
            as_of=req.as_of,
            tenant_id=tenant_id
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/analyze/event", status_code=status.HTTP_200_OK)
def analyze_event_exposure(
    req: EventExposureRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> ExposureAnalysisRun:
    """Connect an event to an entity via knowledge graph exposure traversal."""
    tenant_id = user.tenant_id if user else None
    return service.analyze_event(
        event_ref=req.event_ref,
        subject_ref=req.subject_ref,
        exposure_type=req.exposure_type,
        exposure_domain=req.exposure_domain,
        measure_id=req.measure_id,
        amount=req.amount,
        currency=req.currency,
        percentage=req.percentage,
        graph_path_ids=req.graph_path_ids,
        explanation=req.explanation,
        tenant_id=tenant_id
    )


@router.post("/scenarios/run", status_code=status.HTTP_200_OK)
def run_scenario(
    req: ScenarioRunRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> ExposureScenarioRun:
    """Run a deterministic scenario shock calculation."""
    tenant_id = user.tenant_id if user else None
    scenario_def = ExposureScenarioDefinition(
        scenario_id=req.scenario_id,
        scenario_name=req.scenario_name,
        owner_id=user.user_id if user else "ANONYMOUS",
        shocks=req.shocks
    )
    return service.run_scenario(scenario_def, req.positions, tenant_id=tenant_id)


@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> ExposureAnalysisRun:
    """Retrieve an exposure run by id with tenant privacy checks."""
    tenant_id = user.tenant_id if user else None
    try:
        return service.get_run(run_id, requesting_tenant_id=tenant_id)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Run '{run_id}' not found.")
    except TenantExposureAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": e.code, "message": str(e)})


@router.get("/runs/{run_id}/results")
def get_run_results(
    run_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> List[AtlasExposureResult]:
    """Retrieve results list for an exposure run."""
    run = get_run(run_id, user, service)
    return run.results


@router.get("/runs/{run_id}/coverage")
def get_run_coverage(
    run_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> Optional[ExposureCoverageSummary]:
    """Retrieve coverage summary and unallocated residual for a run."""
    run = get_run(run_id, user, service)
    return run.coverage_summary


@router.get("/lineage/{exposure_id}")
def get_lineage(
    exposure_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: AtlasExposureEngineService = Depends(get_exposure_service)
) -> Dict[str, Any]:
    """Retrieve mathematical lineage and source link for an exposure result."""
    tenant_id = user.tenant_id if user else None
    try:
        item = service.get_lineage(exposure_id, requesting_tenant_id=tenant_id)
        return item.model_dump()
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lineage not found.")
    except TenantExposureAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": e.code, "message": str(e)})
    except SourceLicenseRevokedError as e:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail={"error": e.code, "message": str(e)})


@router.get("/fixtures/{fixture_id}")
def get_fixture_data(fixture_id: str) -> Dict[str, Any]:
    """Retrieve reference fixture definitions for validation."""
    fid = fixture_id.upper()
    if fid == "A":
        return get_fixture_a_geographic_revenue()
    elif fid == "B":
        return get_fixture_b_facility_count()
    elif fid == "C":
        c = get_fixture_c_portfolio_sector()
        return {"nav": str(c["nav"]), "positions": [p.model_dump() for p in c["positions"]]}
    elif fid == "D":
        return {"positions": [p.model_dump() for p in get_fixture_d_long_short()]}
    elif fid == "K":
        k = get_fixture_k_interest_rate_sensitivity()
        return {"dv01": str(k["dv01"]), "shift_bps": str(k["shift_bps"])}
    elif fid == "X":
        x = get_fixture_x_geographic_residual()
        return {"total_revenue": str(x["total_revenue"]), "segments": [{"region_name": s["region_name"], "revenue": str(s["revenue"])} for s in x["segments"]]}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture {fixture_id} not found.")

