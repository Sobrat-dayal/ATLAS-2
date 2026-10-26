"""FastAPI Router for Company Peers and Comparable Company Analysis (Stage 87).

Endpoints:
- GET /companies/{company_id}/peers/overview
- GET /companies/{company_id}/peers/candidates
- GET /companies/{company_id}/peers/metrics
- POST /companies/{company_id}/peers/compare
- POST /companies/{company_id}/peers/history
- GET /companies/{company_id}/peers/groups
- POST /companies/{company_id}/peers/groups
- GET /companies/{company_id}/peers/groups/{group_id}
- PATCH /companies/{company_id}/peers/groups/{group_id}
- DELETE /companies/{company_id}/peers/groups/{group_id}
- GET /companies/{company_id}/peers/methodology
"""

import logging
from typing import Optional

from atlas.auth import AuthPrincipal
from atlas.authorization.permissions import PermissionCode
from atlas.companies.peers import (
    CandidatesResponseDTO,
    CompanyPeersService,
    CreatePeerGroupRequestDTO,
    HistoricalComparisonRequestDTO,
    HistoricalComparisonResponseDTO,
    MetricCatalogResponseDTO,
    PeerComparisonRequestDTO,
    PeerComparisonResponseDTO,
    PeerDuplicateCompanyError,
    PeerGroupNotAuthorizedError,
    PeerGroupNotFoundError,
    PeerGroupRevisionConflictError,
    PeerGroupSizeExceededError,
    PeerMethodologyResponseDTO,
    PeerSelfSelectionNotAllowedError,
    PeersOverviewResponseDTO,
    UpdatePeerGroupRequestDTO,
    UserPeerGroupDTO,
)
from atlas.companies.peers.errors import PeerCompanyNotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies/{company_id}/peers",
    tags=["Company Peers & Comparable Analysis"],
)

_service: Optional[CompanyPeersService] = None


def get_peers_service() -> CompanyPeersService:
    """Dependency injector for CompanyPeersService."""
    global _service
    if _service is None:
        _service = CompanyPeersService()
    return _service


@router.get(
    "/overview",
    response_model=PeersOverviewResponseDTO,
    summary="Get peer overview and industry classification",
)
async def get_peers_overview(
    company_id: str,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> PeersOverviewResponseDTO:
    """Returns verified industry classification, candidate count, default group, and key highlights."""
    try:
        return service.get_overview(company_id=company_id, user_id=current_user.sub)
    except PeerCompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Error loading peers overview for %s", company_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/candidates",
    response_model=CandidatesResponseDTO,
    summary="Discover comparable peer candidates",
)
async def get_peer_candidates(
    company_id: str,
    limit: int = Query(20, ge=1, le=50, description="Maximum candidate companies to return"),
    competitors_only: bool = Query(
        False, description="Filter only to verified commercial competitors"
    ),
    service: CompanyPeersService = Depends(get_peers_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CandidatesResponseDTO:
    """Resolves comparable peer candidates with explainable selection reasons."""
    try:
        return service.get_candidates(
            company_id=company_id, limit=limit, competitors_only=competitors_only
        )
    except PeerCompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Error discovering peer candidates for %s", company_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/metrics",
    response_model=MetricCatalogResponseDTO,
    summary="Get catalog of compatible comparison metrics",
)
async def get_peer_metrics(
    company_id: str,
    service: CompanyPeersService = Depends(get_peers_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> MetricCatalogResponseDTO:
    """Returns the registered catalog of financial scale, profitability, valuation, and leverage metrics."""
    return service.get_available_metrics()


@router.post(
    "/compare",
    response_model=PeerComparisonResponseDTO,
    summary="Run cross-company financial and valuation comparison",
)
async def compare_company_peers(
    company_id: str,
    request: PeerComparisonRequestDTO,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> PeerComparisonResponseDTO:
    """Computes comparable metric observations and cross-sectional benchmark statistics (median, mean, percentiles)."""
    try:
        return service.compare_peers(
            company_id=company_id, user_id=current_user.sub, request=request
        )
    except PeerCompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except PeerGroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Error executing peer comparison for %s", company_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.post(
    "/history",
    response_model=HistoricalComparisonResponseDTO,
    summary="Get multi-company historical trend series",
)
async def compare_company_history(
    company_id: str,
    request: HistoricalComparisonRequestDTO,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> HistoricalComparisonResponseDTO:
    """Returns multi-period historical time-series for the subject and peers."""
    try:
        return service.compare_history(
            company_id=company_id, user_id=current_user.sub, request=request
        )
    except PeerCompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Error executing peer historical comparison for %s", company_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


# -----------------------------------------------------------------------------
# User Peer Group Management Endpoints
# -----------------------------------------------------------------------------


@router.get(
    "/groups",
    response_model=list[UserPeerGroupDTO],
    summary="List saved user peer groups",
)
async def list_user_peer_groups(
    company_id: str,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> list[UserPeerGroupDTO]:
    """Lists saved custom peer groups accessible to the authenticated user."""
    return service.get_user_peer_groups(company_id=company_id, user_id=current_user.sub)


@router.post(
    "/groups",
    response_model=UserPeerGroupDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom peer group",
)
async def create_user_peer_group(
    company_id: str,
    request: CreatePeerGroupRequestDTO,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserPeerGroupDTO:
    """Creates a new user peer group with size limits and duplicate checks."""
    try:
        return service.create_peer_group(
            company_id=company_id, user_id=current_user.sub, request=request
        )
    except (
        PeerSelfSelectionNotAllowedError,
        PeerDuplicateCompanyError,
        PeerGroupSizeExceededError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except PeerCompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Error creating peer group")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/groups/{group_id}",
    response_model=UserPeerGroupDTO,
    summary="Get single peer group detail",
)
async def get_peer_group_detail(
    company_id: str,
    group_id: str,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserPeerGroupDTO:
    """Retrieves specific peer group verifying ownership."""
    try:
        return service.get_peer_group(group_id=group_id, user_id=current_user.sub)
    except PeerGroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except PeerGroupNotAuthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc


@router.patch(
    "/groups/{group_id}",
    response_model=UserPeerGroupDTO,
    summary="Update custom peer group",
)
async def update_user_peer_group(
    company_id: str,
    group_id: str,
    request: UpdatePeerGroupRequestDTO,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> UserPeerGroupDTO:
    """Updates peer group membership or description with revision conflict checking."""
    try:
        return service.update_peer_group(
            group_id=group_id, user_id=current_user.sub, request=request
        )
    except PeerGroupRevisionConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except (
        PeerSelfSelectionNotAllowedError,
        PeerDuplicateCompanyError,
        PeerGroupSizeExceededError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except PeerGroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except PeerGroupNotAuthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc
    except Exception as exc:
        logger.exception("Error updating peer group %s", group_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete custom peer group",
)
async def delete_user_peer_group(
    company_id: str,
    group_id: str,
    service: CompanyPeersService = Depends(get_peers_service),
    current_user: AuthPrincipal = Depends(get_current_user),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> None:
    """Deletes a custom user peer group."""
    try:
        service.delete_peer_group(group_id=group_id, user_id=current_user.sub)
    except PeerGroupNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except PeerGroupNotAuthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc


@router.get(
    "/methodology",
    response_model=PeerMethodologyResponseDTO,
    summary="Get peer selection and benchmarking methodology rules",
)
async def get_peer_methodology(
    company_id: str,
    service: CompanyPeersService = Depends(get_peers_service),
    _: None = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> PeerMethodologyResponseDTO:
    """Discloses the transparent candidate scoring, alignment rules, and statistical definitions."""
    return service.get_methodology()
