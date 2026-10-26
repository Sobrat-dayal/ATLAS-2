"""FastAPI Router for Company Supply Chain Intelligence (Stage 88).

Endpoints:
- GET /companies/{company_id}/supply-chain/overview
- GET /companies/{company_id}/supply-chain/suppliers
- GET /companies/{company_id}/supply-chain/customers
- GET /companies/{company_id}/supply-chain/network
- GET /companies/{company_id}/supply-chain/relationships/{relationship_id}
- GET /companies/{company_id}/supply-chain/relationships/{relationship_id}/evidence
- GET /companies/{company_id}/supply-chain/concentration
- GET /companies/{company_id}/supply-chain/history
- GET /companies/{company_id}/supply-chain/coverage
- GET /companies/{company_id}/supply-chain/filters
"""

import logging
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization.permissions import PermissionCode
from atlas.companies.supply_chain import (
    CompanySupplyChainService,
    ConcentrationResponseDTO,
    CustomersListResponseDTO,
    HistoricalTimelineResponseDTO,
    RelationshipEvidenceDTO,
    RelationshipLifecycleStatus,
    SuppliersListResponseDTO,
    SupplyChainCompanyNotFoundError,
    SupplyChainCoverageResponseDTO,
    SupplyChainError,
    SupplyChainInvalidDirectionError,
    SupplyChainNetworkResponseDTO,
    SupplyChainOverviewResponseDTO,
    SupplyChainRelationshipDTO,
    SupplyChainRelationshipNotFoundError,
    SupplyChainRelationshipType,
    SupplyChainTraversalLimitExceededError,
    VerificationStatus,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies/{company_id}/supply-chain",
    tags=["Company Supply Chains"],
)

_service_instance: Optional[CompanySupplyChainService] = None


def get_supply_chain_service() -> CompanySupplyChainService:
    """Dependency injector for CompanySupplyChainService singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = CompanySupplyChainService()
    return _service_instance


# -----------------------------------------------------------------------------
# 1. Overview
# -----------------------------------------------------------------------------


@router.get(
    "/overview",
    response_model=SupplyChainOverviewResponseDTO,
    summary="Get Supply Chain Overview",
    description="Returns top-level summary counts, primary foundry and assembler highlights, and concentration summaries.",
)
async def get_supply_chain_overview(
    company_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> SupplyChainOverviewResponseDTO:
    try:
        return service.get_overview(company_id)
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 2. Suppliers List
# -----------------------------------------------------------------------------


@router.get(
    "/suppliers",
    response_model=SuppliersListResponseDTO,
    summary="List Direct Suppliers",
    description="Retrieves direct verified supplier relationships filtered by type, verification state, or country.",
)
async def get_suppliers(
    company_id: str,
    relationship_type: Optional[SupplyChainRelationshipType] = Query(None),
    verification_status: Optional[VerificationStatus] = Query(None),
    country: Optional[str] = Query(None),
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> SuppliersListResponseDTO:
    try:
        return service.get_suppliers(
            company_id=company_id,
            relationship_type=relationship_type,
            verification_status=verification_status,
            country=country,
        )
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 3. Customers List
# -----------------------------------------------------------------------------


@router.get(
    "/customers",
    response_model=CustomersListResponseDTO,
    summary="List Direct Customers",
    description="Retrieves direct verified customer and distribution relationships.",
)
async def get_customers(
    company_id: str,
    relationship_type: Optional[SupplyChainRelationshipType] = Query(None),
    verification_status: Optional[VerificationStatus] = Query(None),
    country: Optional[str] = Query(None),
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CustomersListResponseDTO:
    try:
        return service.get_customers(
            company_id=company_id,
            relationship_type=relationship_type,
            verification_status=verification_status,
            country=country,
        )
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 4. Directed Network Graph
# -----------------------------------------------------------------------------


@router.get(
    "/network",
    response_model=SupplyChainNetworkResponseDTO,
    summary="Get Directed Network Graph",
    description="Returns nodes and directed edges for multi-tier network visualization with server-side traversal budgets.",
)
async def get_network(
    company_id: str,
    direction: str = Query("BOTH", description="UPSTREAM_SUPPLIER, DOWNSTREAM_CUSTOMER, or BOTH"),
    depth: int = Query(2, ge=1, le=3, description="Traversal tier depth (1, 2, or 3)"),
    max_nodes: int = Query(150, ge=10, le=300),
    max_edges: int = Query(300, ge=10, le=500),
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> SupplyChainNetworkResponseDTO:
    try:
        return service.get_network(
            company_id=company_id,
            direction=direction,
            depth=depth,
            max_nodes=max_nodes,
            max_edges=max_edges,
        )
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainInvalidDirectionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except SupplyChainTraversalLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 5. Relationship Details & Evidence
# -----------------------------------------------------------------------------


@router.get(
    "/relationships/{relationship_id}",
    response_model=SupplyChainRelationshipDTO,
    summary="Get Relationship Details",
    description="Retrieves comprehensive details for an individual commercial relationship.",
)
async def get_relationship_details(
    company_id: str,
    relationship_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> SupplyChainRelationshipDTO:
    try:
        return service.get_relationship(relationship_id)
    except SupplyChainRelationshipNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/relationships/{relationship_id}/evidence",
    response_model=List[RelationshipEvidenceDTO],
    summary="Get Relationship Evidence",
    description="Retrieves audited source filing citations and excerpts for an individual relationship.",
)
async def get_relationship_evidence(
    company_id: str,
    relationship_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[RelationshipEvidenceDTO]:
    try:
        return service.get_relationship_evidence(relationship_id)
    except SupplyChainRelationshipNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 6. Concentration & Dependency Analysis
# -----------------------------------------------------------------------------


@router.get(
    "/concentration",
    response_model=ConcentrationResponseDTO,
    summary="Get Concentration Observations",
    description="Returns disclosed customer revenue concentration and supplier spend dependencies.",
)
async def get_concentration(
    company_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> ConcentrationResponseDTO:
    try:
        return service.get_concentration(company_id)
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 7. Historical Timeline
# -----------------------------------------------------------------------------


@router.get(
    "/history",
    response_model=HistoricalTimelineResponseDTO,
    summary="Get Historical Relationship Milestones",
    description="Returns verifiable timeline events including initial disclosures, extensions, and renewals.",
)
async def get_history(
    company_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> HistoricalTimelineResponseDTO:
    try:
        return service.get_history(company_id)
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 8. Coverage & Data Quality Assessment
# -----------------------------------------------------------------------------


@router.get(
    "/coverage",
    response_model=SupplyChainCoverageResponseDTO,
    summary="Get Supply Chain Disclosure Coverage",
    description="Reports disclosure coverage boundaries, data freshness, and documented limitations.",
)
async def get_coverage(
    company_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> SupplyChainCoverageResponseDTO:
    try:
        return service.get_coverage(company_id)
    except SupplyChainCompanyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except SupplyChainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# -----------------------------------------------------------------------------
# 9. Available Filters Catalog
# -----------------------------------------------------------------------------


@router.get(
    "/filters",
    summary="Get Available Relationship Filters",
    description="Returns list of available relationship types and verification states for UI dropdowns.",
)
async def get_filters(
    company_id: str,
    service: CompanySupplyChainService = Depends(get_supply_chain_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> dict:
    return {
        "relationship_types": [t.value for t in SupplyChainRelationshipType],
        "verification_statuses": [v.value for v in VerificationStatus],
        "lifecycle_statuses": [st.value for st in RelationshipLifecycleStatus],
        "countries": [
            "United States",
            "Taiwan",
            "Japan",
            "South Korea",
            "Netherlands",
        ],
    }
