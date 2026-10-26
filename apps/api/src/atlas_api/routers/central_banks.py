"""FastAPI Router for Central Bank Intelligence (Stage 91).

Endpoints:
- GET /api/v1/economics/central-banks
- GET /api/v1/economics/central-banks/{bank_id}/overview
- GET /api/v1/economics/central-banks/{bank_id}/profile
- GET /api/v1/economics/central-banks/{bank_id}/framework
- GET /api/v1/economics/central-banks/{bank_id}/instruments
- GET /api/v1/economics/central-banks/{bank_id}/instruments/{instrument_code}
- GET /api/v1/economics/central-banks/{bank_id}/rates
- GET /api/v1/economics/central-banks/{bank_id}/decisions
- GET /api/v1/economics/central-banks/{bank_id}/decisions/{decision_id}
- GET /api/v1/economics/central-banks/{bank_id}/meetings
- GET /api/v1/economics/central-banks/{bank_id}/meetings/{meeting_id}
- GET /api/v1/economics/central-banks/{bank_id}/meetings/{meeting_id}/voting
- GET /api/v1/economics/central-banks/{bank_id}/publications
- GET /api/v1/economics/central-banks/{bank_id}/publications/{document_id}
- GET /api/v1/economics/central-banks/{bank_id}/speeches
- GET /api/v1/economics/central-banks/{bank_id}/guidance
- GET /api/v1/economics/central-banks/{bank_id}/balance-sheet
- GET /api/v1/economics/central-banks/{bank_id}/programs
- GET /api/v1/economics/central-banks/{bank_id}/timeline
- GET /api/v1/economics/central-banks/{bank_id}/coverage
"""

import logging
from datetime import datetime
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.authorization.permissions import PermissionCode
from atlas.economics.central_banks import (
    CentralBankBalanceSheetSummaryDTO,
    CentralBankCoverageResponseDTO,
    CentralBankDecisionNotFoundError,
    CentralBankInstitutionDTO,
    CentralBankInstrumentNotFoundError,
    CentralBankMeetingNotFoundError,
    CentralBankNotFoundError,
    CentralBankOverviewDTO,
    CentralBankPolicyProgramDTO,
    CentralBankPublicationNotFoundError,
    CentralBankService,
    CommitteeVotingRecordDTO,
    MonetaryPolicyDecisionDTO,
    MonetaryPolicyFrameworkDTO,
    MonetaryPolicyMeetingDTO,
    OfficialForwardGuidanceDTO,
    OfficialPublicationDTO,
    OfficialSpeechDTO,
    PolicyInstrumentDTO,
    PolicyTimelineEventDTO,
    CommitteeMetadataDTO,
    HistoricalRatePointDTO,
    InflationTargetDTO,
    SourceProvenanceDTO,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import RequirePermission

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/economics/central-banks",
    tags=["Central Banks"],
)

_service: Optional[CentralBankService] = None


def get_central_bank_service() -> CentralBankService:
    global _service
    if _service is None:
        _service = CentralBankService()
    return _service


@router.get(
    "",
    response_model=List[CentralBankInstitutionDTO],
    summary="List Supported Central Banks & Monetary Authorities",
    description="Returns registry metadata profiles for all supported central banks and monetary authorities.",
)
async def list_central_banks(
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[CentralBankInstitutionDTO]:
    return service.list_institutions()


@router.get(
    "/coverage",
    response_model=List[CentralBankCoverageResponseDTO],
    summary="Get System-Wide Central Bank Intelligence Coverage Catalog",
    description="Returns verified coverage matrices for all supported central banks and monetary authorities.",
)
async def list_all_coverage(
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[CentralBankCoverageResponseDTO]:
    return [service.get_coverage(inst.central_bank_id) for inst in service.list_institutions()]


@router.get(
    "/{bank_id}",
    response_model=CentralBankInstitutionDTO,
    summary="Get Central Bank Identity (Direct Alias)",
    description="Direct endpoint returning official institution identity metadata.",
)
async def get_central_bank_by_id(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CentralBankInstitutionDTO:
    try:
        return service.get_institution(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/overview",
    response_model=CentralBankOverviewDTO,
    summary="Get Central Bank Master Research Overview",
    description="Returns high-density analytical snapshot with framework, policy rates, latest decision, and balance sheet summary.",
)
async def get_central_bank_overview(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CentralBankOverviewDTO:
    try:
        return service.get_overview(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/profile",
    response_model=CentralBankInstitutionDTO,
    summary="Get Central Bank Institutional Profile",
    description="Returns official headquarters, founding year, policy committee name, and official website.",
)
async def get_central_bank_profile(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CentralBankInstitutionDTO:
    try:
        return service.get_institution(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/framework",
    response_model=MonetaryPolicyFrameworkDTO,
    summary="Get Monetary Policy Framework & Inflation Target",
    description="Returns statutory mandate, operating strategy, target inflation metric, and target range or tolerance band.",
)
async def get_monetary_policy_framework(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> MonetaryPolicyFrameworkDTO:
    try:
        return service.get_framework(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/targets",
    response_model=InflationTargetDTO,
    summary="Get Official Central Bank Inflation Targets",
    description="Returns verified inflation target metrics, numeric target levels, target ranges, tolerance bands, and target horizons.",
)
async def get_inflation_targets(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> InflationTargetDTO:
    try:
        return service.get_targets(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/committee",
    response_model=CommitteeMetadataDTO,
    summary="Get Monetary Policy Committee Metadata & Mandate",
    description="Returns official monetary policy committee name, structure, total voting membership, and charter reference.",
)
async def get_committee_metadata(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CommitteeMetadataDTO:
    try:
        return service.get_committee_metadata(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/instruments",
    response_model=List[PolicyInstrumentDTO],
    summary="Get Administered Monetary Policy Instruments",
    description="Returns all operational interest rate instruments, categories, representations, and current values.",
)
async def get_policy_instruments(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[PolicyInstrumentDTO]:
    try:
        return service.get_instruments(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/instruments/{instrument_code}",
    response_model=PolicyInstrumentDTO,
    summary="Get Specific Monetary Policy Instrument",
    description="Returns single policy instrument details by code or identifier.",
)
async def get_policy_instrument(
    bank_id: str,
    instrument_code: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> PolicyInstrumentDTO:
    try:
        return service.get_instrument(bank_id, instrument_code)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except CentralBankInstrumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/rates",
    response_model=List[PolicyInstrumentDTO],
    summary="Get Current Official Policy Interest Rates",
    description="Returns current administered rates and target ranges with effective dates.",
)
async def get_current_policy_rates(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[PolicyInstrumentDTO]:
    try:
        return service.get_instruments(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/rates/history",
    response_model=List[HistoricalRatePointDTO],
    summary="Get Historical Official Policy Interest Rate Points",
    description="Returns chronological official policy rate decisions and instrument observations with effective dates.",
)
async def get_historical_rates(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[HistoricalRatePointDTO]:
    try:
        return service.get_rate_history(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/decisions",
    response_model=List[MonetaryPolicyDecisionDTO],
    summary="Get Monetary Policy Decision History",
    description="Returns historical official monetary policy decisions with basis-point rate changes and statement links.",
)
async def get_policy_decisions(
    bank_id: str,
    as_of: Optional[datetime] = Query(None, description="Optional point-in-time timestamp (YYYY-MM-DDTHH:MM:SS) to exclude future announcements."),
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[MonetaryPolicyDecisionDTO]:
    try:
        if as_of is not None:
            return service.filter_decisions_point_in_time(bank_id, as_of)
        return service.get_decisions(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/decisions/{decision_id}",
    response_model=MonetaryPolicyDecisionDTO,
    summary="Get Specific Policy Decision Detail",
    description="Returns policy decision details, rationale, and exact basis-point changes.",
)
async def get_policy_decision(
    bank_id: str,
    decision_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> MonetaryPolicyDecisionDTO:
    try:
        return service.get_decision(decision_id)
    except CentralBankDecisionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/meetings",
    response_model=List[MonetaryPolicyMeetingDTO],
    summary="Get Monetary Policy Meetings History",
    description="Returns policy committee meeting dates, decision links, and minutes publication timestamps.",
)
async def get_policy_meetings(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[MonetaryPolicyMeetingDTO]:
    try:
        return service.get_meetings(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/meetings/{meeting_id}",
    response_model=MonetaryPolicyMeetingDTO,
    summary="Get Specific Meeting Details",
    description="Returns detailed records for a specific monetary policy meeting.",
)
async def get_policy_meeting(
    bank_id: str,
    meeting_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> MonetaryPolicyMeetingDTO:
    try:
        return service.get_meeting(meeting_id)
    except CentralBankMeetingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/meetings/{meeting_id}/voting",
    response_model=Optional[CommitteeVotingRecordDTO],
    summary="Get Committee Voting Record and Dissent Rationale",
    description="Returns published committee votes for/against/abstain and dissenting member rationales where officially disclosed.",
)
async def get_meeting_voting_record(
    bank_id: str,
    meeting_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> Optional[CommitteeVotingRecordDTO]:
    try:
        return service.get_voting_record(meeting_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/publications",
    response_model=List[OfficialPublicationDTO],
    summary="Get Official Central Bank Publications & Statements",
    description="Returns verified monetary policy statements, minutes, and monetary policy reports.",
)
async def get_publications(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[OfficialPublicationDTO]:
    try:
        return service.get_publications(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/publications/{document_id}",
    response_model=OfficialPublicationDTO,
    summary="Get Specific Official Publication",
    description="Returns sanitized excerpts and source URLs for an official central bank document.",
)
async def get_publication(
    bank_id: str,
    document_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> OfficialPublicationDTO:
    try:
        return service.get_publication(document_id)
    except CentralBankPublicationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/speeches",
    response_model=List[OfficialSpeechDTO],
    summary="Get Official Policymaker Speeches",
    description="Returns transcripts and key takeaways from central bank governors and committee members.",
)
async def get_speeches(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[OfficialSpeechDTO]:
    try:
        return service.get_speeches(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/guidance",
    response_model=List[OfficialForwardGuidanceDTO],
    summary="Get Official Forward Guidance Excerpts",
    description="Returns verbatim forward guidance quotes from official statements without speculative rate forecasts.",
)
async def get_forward_guidance(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[OfficialForwardGuidanceDTO]:
    try:
        return service.get_guidance(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/balance-sheet",
    response_model=Optional[CentralBankBalanceSheetSummaryDTO],
    summary="Get Central Bank Balance Sheet Summary",
    description="Returns total assets, liabilities, securities holdings, and reserve balances.",
)
async def get_balance_sheet(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> Optional[CentralBankBalanceSheetSummaryDTO]:
    try:
        return service.get_balance_sheet(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/programs",
    response_model=List[CentralBankPolicyProgramDTO],
    summary="Get Central Bank Asset Purchase & QT Programs",
    description="Returns quantitative easing (QE), asset purchase runoff (QT), and liquidity programs.",
)
async def get_policy_programs(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[CentralBankPolicyProgramDTO]:
    try:
        return service.get_programs(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/timeline",
    response_model=List[PolicyTimelineEventDTO],
    summary="Get Historical Monetary Policy Timeline",
    description="Returns chronological events across rate decisions, meetings, and major policy communications.",
)
async def get_policy_timeline(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> List[PolicyTimelineEventDTO]:
    try:
        return service.get_timeline(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/coverage",
    response_model=CentralBankCoverageResponseDTO,
    summary="Get Central Bank Intelligence Coverage Matrix",
    description="Returns verification coverage of available policy rate series, decisions, minutes, and balance sheet data.",
)
async def get_central_bank_coverage(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> CentralBankCoverageResponseDTO:
    try:
        return service.get_coverage(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/{bank_id}/sources",
    response_model=SourceProvenanceDTO,
    summary="Get Official Source Provenance & Data Authority Metadata",
    description="Returns official publishing authority, source tier, verified website, and point-in-time status.",
)
async def get_source_provenance(
    bank_id: str,
    service: CentralBankService = Depends(get_central_bank_service),
    _user: AuthPrincipal = Depends(get_current_user),
    _perm: bool = Depends(RequirePermission(PermissionCode.ATLAS_ACCESS)),
) -> SourceProvenanceDTO:
    try:
        return service.get_sources(bank_id)
    except CentralBankNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
