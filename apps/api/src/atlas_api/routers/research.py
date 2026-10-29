"""FastAPI Router for Institutional Financial Research Platform (Stage 104).

Endpoints (mounted under /api/v1):
- GET    /api/v1/research/overview
- GET    /api/v1/research/investigations
- POST   /api/v1/research/investigations
- GET    /api/v1/research/investigations/{id}
- PATCH  /api/v1/research/investigations/{id}
- DELETE /api/v1/research/investigations/{id}
- POST   /api/v1/research/investigations/{id}/archive
- GET    /api/v1/research/investigations/{id}/activity

- GET    /api/v1/research/investigations/{id}/questions
- POST   /api/v1/research/investigations/{id}/questions
- PATCH  /api/v1/research/questions/{id}
- DELETE /api/v1/research/questions/{id}

- GET    /api/v1/research/investigations/{id}/hypotheses
- POST   /api/v1/research/investigations/{id}/hypotheses
- PATCH  /api/v1/research/hypotheses/{id}
- DELETE /api/v1/research/hypotheses/{id}

- GET    /api/v1/research/investigations/{id}/notes
- POST   /api/v1/research/investigations/{id}/notes
- GET    /api/v1/research/notes/{id}
- PATCH  /api/v1/research/notes/{id}
- DELETE /api/v1/research/notes/{id}
- GET    /api/v1/research/notes/{id}/revisions

- GET    /api/v1/research/investigations/{id}/claims
- POST   /api/v1/research/investigations/{id}/claims
- PATCH  /api/v1/research/claims/{id}
- DELETE /api/v1/research/claims/{id}

- GET    /api/v1/research/sources
- GET    /api/v1/research/investigations/{id}/sources
- POST   /api/v1/research/investigations/{id}/sources
- DELETE /api/v1/research/investigations/{id}/sources/{source_id}

- GET    /api/v1/research/investigations/{id}/evidence
- POST   /api/v1/research/investigations/{id}/evidence
- DELETE /api/v1/research/evidence/{id}
- GET    /api/v1/research/investigations/{id}/citations

- GET    /api/v1/research-documents/{entity_id}  (Stage 36 legacy compatibility)
"""

import uuid
from typing import List, Optional

from atlas.auth import AuthPrincipal
from atlas.research.enums import (
    AnalysisInputPolicy,
    InvestigationLifecycleStatus,
    ReportLifecycleStatus,
    ResearchAnalysisType,
    ResearchReportType,
    ResearchResourceType,
    ResearchRole,
    ResearchSourceType,
    ResearchType,
    ReviewDecisionType,
    ReviewScope,
    ReviewStatus,
)
from atlas.research.errors import (
    ResearchAnalysisAccessDeniedError,
    ResearchAnalysisConfigurationInvalidError,
    ResearchAnalysisExecutionFailedError,
    ResearchAnalysisNotFoundError,
    ResearchAnalysisRevisionConflictError,
    ResearchAnalysisRunNotFoundError,
    ResearchAnalysisTypeUnsupportedError,
    ResearchAssumptionNotFoundError,
    ResearchClaimNotFoundError,
    ResearchComparisonIncompatibleError,
    ResearchComparisonResourceLimitError,
    ResearchDiscoveryQueryInvalidError,
    ResearchDocumentNotFoundError,
    ResearchDocumentSectionNotFoundError,
    ResearchDocumentTableNotFoundError,
    ResearchEvidenceCandidateNotFoundError,
    ResearchEvidenceNotFoundError,
    ResearchEvidenceSourceMissingError,
    ResearchFindingAccessDeniedError,
    ResearchFindingNotFoundError,
    ResearchFindingRevisionConflictError,
    ResearchHypothesisEvaluationInvalidError,
    ResearchHypothesisEvaluationNotFoundError,
    ResearchHypothesisNotFoundError,
    ResearchInvestigationAccessDeniedError,
    ResearchInvestigationNotFoundError,
    ResearchInvestigationRevisionConflictError,
    ResearchInvestmentThesisAccessDeniedError,
    ResearchInvestmentThesisNotFoundError,
    ResearchInvestmentThesisRevisionConflictError,
    ResearchNoteAccessDeniedError,
    ResearchNoteContentInvalidError,
    ResearchNoteNotFoundError,
    ResearchNoteRevisionConflictError,
    ResearchQuestionNotFoundError,
    # Stage 107 Errors
    ResearchReportAccessDeniedError,
    ResearchReportExportAccessDeniedError,
    ResearchReportExportNotFoundError,
    ResearchReportFinalizedImmutableError,
    ResearchReportNotFoundError,
    ResearchReportRevisionConflictError,
    ResearchReportSectionNotFoundError,
    ResearchReportTemplateUnavailableError,
    ResearchScenarioConfigurationInvalidError,
    ResearchSemanticSearchUnavailableError,
    ResearchSourceNotFoundError,
    ResearchSourceUrlUnsafeError,
    ResearchThesisArgumentNotFoundError,
    # Stage 108 Errors
    ResearchAccessGrantForbiddenError,
    ResearchAccessGrantNotFoundError,
    ResearchAccessRevokedError,
    ResearchAccessRoleInvalidError,
    ResearchCirculationAccessDeniedError,
    ResearchCirculationNotFoundError,
    ResearchCirculationRevokedError,
    ResearchCommentAccessDeniedError,
    ResearchCommentAnchorInvalidError,
    ResearchCommentNotFoundError,
    ResearchCommentThreadNotFoundError,
    ResearchParticipantCrossTenantError,
    ResearchParticipantIneligibleError,
    ResearchQualityGateFailedError,
    ResearchReviewAccessDeniedError,
    ResearchReviewAlreadyDecidedError,
    ResearchReviewDuplicateActiveRequestError,
    ResearchReviewInvalidTransitionError,
    ResearchReviewNotFoundError,
    ResearchReviewRevisionMismatchError,
    ResearchReviewSelfApprovalForbiddenError,
    # Stage 109 Errors
    ResearchImpactNotFoundError,
    ResearchKnowledgeAccessDeniedError,
    ResearchKnowledgeEntryNotFoundError,
    ResearchRevalidationAccessDeniedError,
    ResearchRevalidationNotFoundError,
    ResearchRevalidationTargetUnavailableError,
    ResearchSourceChangeDuplicateError,
    ResearchSourceChangeNotFoundError,
    ResearchUpdateAlreadyResolvedError,
    ResearchUpdateInvalidStateTransitionError,
    ResearchUpdateItemAccessDeniedError,
    ResearchUpdateItemNotFoundError,
)
from atlas.research.schemas import (
    # Stage 106 Schemas
    AnalysisProvenanceResponseDTO,
    AttachResearchEvidenceDTO,
    # Stage 107 Schemas
    CompareReportRevisionsRequestDTO,
    CompareReportRevisionsResponseDTO,
    ConvertEvidenceCandidateDTO,
    CreateReportExportRequest,
    CreateReportSectionRequest,
    CreateResearchAnalysisDTO,
    CreateResearchAssumptionDTO,
    CreateResearchClaimDTO,
    CreateResearchFindingDTO,
    CreateResearchHypothesisDTO,
    CreateResearchInvestigationDTO,
    CreateResearchNoteDTO,
    CreateResearchQuestionDTO,
    CreateResearchReportRequest,
    CreateResearchThesisRequest,
    CreateThesisArgumentRequest,
    DocumentComparisonRequestDTO,
    DocumentComparisonResultDTO,
    DocumentSearchRequestDTO,
    DocumentSearchResponseDTO,
    EvaluateResearchHypothesisDTO,
    EvidenceCandidateListResponseDTO,
    ExecuteSensitivityScenarioDTO,
    FinalizeReportRequest,
    FinancialFactsCompareRequestDTO,
    FinancialFactsCompareResponseDTO,
    LinkResearchSourceDTO,
    ReorderReportSectionsRequest,
    ResearchActivityTimelineResponseDTO,
    ResearchAnalysisDTO,
    ResearchAnalysisListResponseDTO,
    ResearchAnalysisResultDTO,
    ResearchAnalysisRunDTO,
    ResearchAnalysisRunListResponseDTO,
    ResearchAnalysisTypeListResponseDTO,
    ResearchAssumptionDTO,
    ResearchAssumptionListResponseDTO,
    ResearchCitationListResponseDTO,
    ResearchClaimDTO,
    ResearchClaimListResponseDTO,
    ResearchDocumentOutlineDTO,
    ResearchDocumentProcessingStatusDTO,
    ResearchDocumentResponse,
    ResearchDocumentSectionDTO,
    ResearchDocumentTableDTO,
    ResearchDocumentTableListResponseDTO,
    ResearchEvidenceDTO,
    ResearchEvidenceListResponseDTO,
    ResearchFindingDTO,
    ResearchFindingListResponseDTO,
    ResearchHypothesisDTO,
    ResearchHypothesisEvaluationDTO,
    ResearchHypothesisEvaluationListResponseDTO,
    ResearchHypothesisListResponseDTO,
    ResearchInvestigationDTO,
    ResearchInvestigationListResponseDTO,
    ResearchNoteDTO,
    ResearchNoteListResponseDTO,
    ResearchNoteRevisionDTO,
    ResearchOverviewSummaryDTO,
    ResearchQuestionDTO,
    ResearchQuestionListResponseDTO,
    ResearchReportDetailResponse,
    ResearchReportExportListResponse,
    ResearchReportExportResponse,
    ResearchReportListResponse,
    ResearchReportRevisionListResponseDTO,
    ResearchReportSectionDTO,
    ResearchReportTemplateDTO,
    ResearchReportTemplateListResponseDTO,
    ResearchReportVerificationResponse,
    ResearchSensitivityResultDTO,
    ResearchSourceDiscoveryQueryDTO,
    ResearchSourceDiscoveryResponseDTO,
    ResearchSourceListResponseDTO,
    ResearchSourceReferenceDTO,
    ResearchSourceTypeListResponseDTO,
    ResearchThesisArgumentDTO,
    ResearchThesisDetailResponse,
    ResearchThesisResponse,
    ResolveEvidenceLocationRequestDTO,
    ResolveEvidenceLocationResponseDTO,
    UpdateReportSectionRequest,
    UpdateResearchAnalysisDTO,
    UpdateResearchClaimDTO,
    UpdateResearchFindingDTO,
    UpdateResearchHypothesisDTO,
    UpdateResearchInvestigationDTO,
    UpdateResearchNoteDTO,
    UpdateResearchQuestionDTO,
    UpdateResearchReportRequest,
    UpdateResearchThesisRequest,
    ValidateAnalysisSpecificationRequestDTO,
    ValidateAnalysisSpecificationResponseDTO,
    VerifyReportRequest,
    # Stage 108 Schemas
    CreateAccessGrantRequest,
    CreateCirculationRequest,
    CreateCommentReplyRequest,
    CreateCommentThreadRequest,
    CreateReviewDecisionRequest,
    CreateReviewRequest,
    QualityGateResultResponse,
    ResearchAccessGrantListResponse,
    ResearchAccessGrantResponse,
    ResearchApprovalStatusResponse,
    ResearchCommentResponse,
    ResearchCommentThreadListResponse,
    ResearchCommentThreadResponse,
    ResearchInternalCirculationListResponse,
    ResearchInternalCirculationResponse,
    ResearchReviewAuditEventListResponse,
    ResearchReviewDecisionResponse,
    ResearchReviewListResponse,
    ResearchReviewRequestResponse,
    RunQualityGateRequest,
    UpdateAccessGrantRequest,
    UpdateCommentRequest,
    UpdateReviewRequest,
    # Stage 109 Schemas
    CreateRevalidationRequest,
    CreateSourceChangeEventRequest,
    CreateUpdateItemRequest,
    ResearchDependencyEdgeResponse,
    ResearchDependencyLineageResponse,
    ResearchImpactAssessmentResponse,
    ResearchImpactListResponse,
    ResearchKnowledgeEntryResponse,
    ResearchKnowledgeSearchQuery,
    ResearchKnowledgeSearchResponse,
    ResearchOverviewSummaryResponse,
    ResearchRevalidationIssueResponse,
    ResearchRevalidationResultResponse,
    ResearchSourceChangeEventListResponse,
    ResearchSourceChangeEventResponse,
    ResearchUpdateItemListResponse,
    ResearchUpdateItemResponse,
    ResolveUpdateItemRequest,
)
from atlas.research.service import (
    ResearchDocumentService,
    ResearchService,
    get_research_service,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session

from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session

router = APIRouter(
    tags=["Research"],
)


def _get_user_id(user: AuthPrincipal) -> str:
    """Extract authenticated user identifier."""
    if hasattr(user, "sub") and user.sub:
        return str(user.sub)
    if hasattr(user, "user_id") and user.user_id:
        return str(user.user_id)
    if hasattr(user, "id") and user.id:
        return str(user.id)
    return "default-user"


# ---------------------------------------------------------------------------
# Research Overview
# ---------------------------------------------------------------------------

@router.get(
    "/research/overview",
    response_model=ResearchOverviewSummaryDTO,
    status_code=status.HTTP_200_OK,
    summary="Get user research dashboard overview and summary metrics",
)
def get_research_overview(
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.get_overview_summary(user_id=user_id)


# ---------------------------------------------------------------------------
# Research Investigations
# ---------------------------------------------------------------------------

@router.get(
    "/research/investigations",
    response_model=ResearchInvestigationListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List user-owned research investigations with filters",
)
def list_investigations(
    entity_id: Optional[str] = Query(None, description="Filter by company or instrument ID/ticker"),
    status_filter: Optional[InvestigationLifecycleStatus] = Query(None, alias="status", description="Filter by lifecycle status"),
    research_type: Optional[ResearchType] = Query(None, description="Filter by research type"),
    q: Optional[str] = Query(None, description="Text query on title, objective, or description"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    items, total = service.list_investigations(
        user_id=user_id,
        entity_id=entity_id,
        status=status_filter,
        research_type=research_type,
        q=q,
        limit=limit,
        offset=offset,
    )
    return ResearchInvestigationListResponseDTO(
        items=items,
        total_count=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/research/investigations",
    response_model=ResearchInvestigationDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new canonical research investigation",
)
def create_investigation(
    payload: CreateResearchInvestigationDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_investigation(payload, user_id=user_id)
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/research/investigations/{investigation_id}",
    response_model=ResearchInvestigationDTO,
    status_code=status.HTTP_200_OK,
    summary="Get research investigation details",
)
def get_investigation(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_investigation(investigation_id, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/investigations/{investigation_id}",
    response_model=ResearchInvestigationDTO,
    status_code=status.HTTP_200_OK,
    summary="Revision-safe update of investigation metadata",
)
def update_investigation(
    payload: UpdateResearchInvestigationDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_investigation(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchInvestigationRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/archive",
    response_model=ResearchInvestigationDTO,
    status_code=status.HTTP_200_OK,
    summary="Archive a research investigation",
)
def archive_investigation(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.archive_investigation(investigation_id, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/research/investigations/{investigation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a research investigation",
)
def delete_investigation(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        deleted = service.delete_investigation(investigation_id, user_id=user_id)
        return {"deleted": deleted}
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/investigations/{investigation_id}/activity",
    response_model=ResearchActivityTimelineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get chronological activity audit history for an investigation",
)
def get_investigation_activity(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        activities = service.list_activity(investigation_id, user_id=user_id)
        return ResearchActivityTimelineResponseDTO(items=activities, total_count=len(activities))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Research Questions
# ---------------------------------------------------------------------------

@router.get(
    "/research/investigations/{investigation_id}/questions",
    response_model=ResearchQuestionListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List analyst questions for an investigation",
)
def list_questions(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_questions(investigation_id, user_id=user_id)
        return ResearchQuestionListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/questions",
    response_model=ResearchQuestionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add a research question to an investigation",
)
def add_question(
    payload: CreateResearchQuestionDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.add_question(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.patch(
    "/research/questions/{question_id}",
    response_model=ResearchQuestionDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a research question",
)
def update_question(
    payload: UpdateResearchQuestionDTO,
    question_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_question(question_id, payload, user_id=user_id)
    except ResearchQuestionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/questions/{question_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a research question",
)
def delete_question(
    question_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        deleted = service.delete_question(question_id, user_id=user_id)
        return {"deleted": deleted}
    except ResearchQuestionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Research Hypotheses
# ---------------------------------------------------------------------------

@router.get(
    "/research/investigations/{investigation_id}/hypotheses",
    response_model=ResearchHypothesisListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List analyst hypotheses for an investigation",
)
def list_hypotheses(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_hypotheses(investigation_id, user_id=user_id)
        return ResearchHypothesisListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/hypotheses",
    response_model=ResearchHypothesisDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add a hypothesis to an investigation",
)
def add_hypothesis(
    payload: CreateResearchHypothesisDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.add_hypothesis(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.patch(
    "/research/hypotheses/{hypothesis_id}",
    response_model=ResearchHypothesisDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a research hypothesis status and links",
)
def update_hypothesis(
    payload: UpdateResearchHypothesisDTO,
    hypothesis_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_hypothesis(hypothesis_id, payload, user_id=user_id)
    except ResearchHypothesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/hypotheses/{hypothesis_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a research hypothesis",
)
def delete_hypothesis(
    hypothesis_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        deleted = service.delete_hypothesis(hypothesis_id, user_id=user_id)
        return {"deleted": deleted}
    except ResearchHypothesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Research Notes
# ---------------------------------------------------------------------------

@router.get(
    "/research/investigations/{investigation_id}/notes",
    response_model=ResearchNoteListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List structured research notes for an investigation",
)
def list_notes(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_notes(investigation_id, user_id=user_id)
        return ResearchNoteListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/notes",
    response_model=ResearchNoteDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a structured research note",
)
def create_note(
    payload: CreateResearchNoteDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_note(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/research/notes/{note_id}",
    response_model=ResearchNoteDTO,
    status_code=status.HTTP_200_OK,
    summary="Get research note by ID",
)
def get_note(
    note_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_note(note_id, user_id=user_id)
    except ResearchNoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchNoteAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/notes/{note_id}",
    response_model=ResearchNoteDTO,
    status_code=status.HTTP_200_OK,
    summary="Revision-safe update of note content with conflict detection",
)
def update_note(
    payload: UpdateResearchNoteDTO,
    note_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_note(note_id, payload, user_id=user_id)
    except ResearchNoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchNoteAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/notes/{note_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a research note",
)
def delete_note(
    note_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        deleted = service.delete_note(note_id, user_id=user_id)
        return {"deleted": deleted}
    except ResearchNoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchNoteAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/notes/{note_id}/revisions",
    response_model=List[ResearchNoteRevisionDTO],
    status_code=status.HTTP_200_OK,
    summary="Get point-in-time edit revisions for a research note",
)
def get_note_revisions(
    note_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_note_revisions(note_id, user_id=user_id)
    except ResearchNoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchNoteAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Research Claims
# ---------------------------------------------------------------------------

@router.get(
    "/research/investigations/{investigation_id}/claims",
    response_model=ResearchClaimListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List claims for an investigation",
)
def list_claims(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_claims(investigation_id, user_id=user_id)
        return ResearchClaimListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/claims",
    response_model=ResearchClaimDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a claim with fact-vs-interpretation qualification",
)
def create_claim(
    payload: CreateResearchClaimDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_claim(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.patch(
    "/research/claims/{claim_id}",
    response_model=ResearchClaimDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a claim statement, category, or evidence status",
)
def update_claim(
    payload: UpdateResearchClaimDTO,
    claim_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_claim(claim_id, payload, user_id=user_id)
    except ResearchClaimNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/claims/{claim_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a research claim",
)
def delete_claim(
    claim_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        deleted = service.delete_claim(claim_id, user_id=user_id)
        return {"deleted": deleted}
    except ResearchClaimNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Research Sources & Library
# ---------------------------------------------------------------------------

@router.get(
    "/research/sources",
    response_model=ResearchSourceListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Search canonical research sources catalog (Filings, News, Economics, Facts)",
)
def list_sources(
    source_type: Optional[ResearchSourceType] = Query(None, description="Filter by canonical source type"),
    entity_id: Optional[str] = Query(None, description="Filter by company/instrument/macro entity"),
    q: Optional[str] = Query(None, description="Search query across source titles, publishers, documents"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    items = service.list_sources(source_type=source_type, entity_id=entity_id, q=q)
    return ResearchSourceListResponseDTO(items=items, total_count=len(items))


@router.get(
    "/research/investigations/{investigation_id}/sources",
    response_model=ResearchSourceListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List sources linked to an investigation",
)
def list_investigation_sources(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_investigation_sources(investigation_id, user_id=user_id)
        return ResearchSourceListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/sources",
    response_model=ResearchSourceReferenceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Link an existing or register a new verified source to an investigation",
)
def link_source(
    payload: LinkResearchSourceDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.link_source_to_investigation(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchSourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchSourceUrlUnsafeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/research/investigations/{investigation_id}/sources/{source_reference_id}",
    status_code=status.HTTP_200_OK,
    summary="Unlink a source from an investigation",
)
def unlink_source(
    investigation_id: str = Path(...),
    source_reference_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        unlinked = service.unlink_source_from_investigation(investigation_id, source_reference_id, user_id=user_id)
        return {"unlinked": unlinked}
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Research Evidence & Citations
# ---------------------------------------------------------------------------

@router.get(
    "/research/investigations/{investigation_id}/evidence",
    response_model=ResearchEvidenceListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List evidence records attached to an investigation",
)
def list_evidence(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_evidence(investigation_id, user_id=user_id)
        return ResearchEvidenceListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/investigations/{investigation_id}/evidence",
    response_model=ResearchEvidenceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Attach verified evidence with source location and excerpt",
)
def attach_evidence(
    payload: AttachResearchEvidenceDTO,
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.attach_evidence(investigation_id, payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchEvidenceSourceMissingError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchNoteContentInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/evidence/{evidence_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove an evidence record",
)
def remove_evidence(
    evidence_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        removed = service.remove_evidence(evidence_id, user_id=user_id)
        return {"removed": removed}
    except ResearchEvidenceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/investigations/{investigation_id}/citations",
    response_model=ResearchCitationListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List citations generated for an investigation",
)
def list_citations(
    investigation_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_citations(investigation_id, user_id=user_id)
        return ResearchCitationListResponseDTO(items=items, total_count=len(items))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 105 — Advanced Research Source Discovery
# ---------------------------------------------------------------------------

@router.post(
    "/research/sources/search",
    response_model=ResearchSourceDiscoveryResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Advanced multi-facet discovery across canonical research sources",
)
def discover_sources(
    payload: ResearchSourceDiscoveryQueryDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.discover_sources(payload, user_id=user_id)
    except ResearchDiscoveryQueryInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ResearchSemanticSearchUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/research/source-types",
    response_model=ResearchSourceTypeListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get canonical research source type taxonomy and distribution metadata",
)
def get_source_types(
    service: ResearchService = Depends(get_research_service),
    _user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_source_types()


# ---------------------------------------------------------------------------
# Stage 105 — Document Intelligence & Processing
# ---------------------------------------------------------------------------

@router.get(
    "/research/documents/{document_id}",
    response_model=ResearchSourceReferenceDTO,
    status_code=status.HTTP_200_OK,
    summary="Get canonical document metadata, origin, and source provenance",
)
def get_document(
    document_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    _user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_source(document_id)
    except ResearchSourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/documents/{document_id}/processing-status",
    response_model=ResearchDocumentProcessingStatusDTO,
    status_code=status.HTTP_200_OK,
    summary="Get document processing audit lifecycle, parsing statistics, and status",
)
def get_document_processing_status(
    document_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_document_processing_status(document_id, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/documents/{document_id}/outline",
    response_model=ResearchDocumentOutlineDTO,
    status_code=status.HTTP_200_OK,
    summary="Get structured hierarchical document outline with section anchors and paths",
)
def get_document_outline(
    document_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_document_outline(document_id, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/documents/{document_id}/sections",
    response_model=List[ResearchDocumentSectionDTO],
    status_code=status.HTTP_200_OK,
    summary="Get all extracted sections with character span offsets for a document",
)
def list_document_sections(
    document_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_document_sections(document_id, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/documents/{document_id}/sections/{section_id}",
    response_model=ResearchDocumentSectionDTO,
    status_code=status.HTTP_200_OK,
    summary="Get specific section text, heading path, and span location",
)
def get_document_section(
    document_id: str = Path(...),
    section_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_document_section(document_id, section_id, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchDocumentSectionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/research/documents/{document_id}/search",
    response_model=DocumentSearchResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Execute in-document keyword search with snippet highlighting and section anchors",
)
def search_document(
    payload: DocumentSearchRequestDTO,
    document_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.search_document(document_id, payload, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchDiscoveryQueryInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/research/documents/{document_id}/tables",
    response_model=ResearchDocumentTableListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get structured financial tables extracted from filing with unit and currency qualification",
)
def list_document_tables(
    document_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_document_tables(document_id, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/documents/{document_id}/tables/{table_id}",
    response_model=ResearchDocumentTableDTO,
    status_code=status.HTTP_200_OK,
    summary="Get specific financial table matrix with cells, headers, and footnotes",
)
def get_document_table(
    document_id: str = Path(...),
    table_id: str = Path(...),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_document_table(document_id, table_id, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchDocumentTableNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 105 — Evidence Candidate Discovery & Anchor Resolution
# ---------------------------------------------------------------------------

@router.post(
    "/research/evidence/candidates",
    response_model=EvidenceCandidateListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Discover pre-extracted evidence candidates from source filings and reports",
)
def list_evidence_candidates(
    document_id: Optional[str] = Query(None, description="Filter candidates by document ID"),
    investigation_id: Optional[str] = Query(None, description="Optional target investigation ID"),
    limit: int = Query(20, ge=1, le=100),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.list_evidence_candidates(
        investigation_id=investigation_id,
        source_id=document_id,
        user_id=user_id,
        limit=limit,
    )


@router.post(
    "/research/evidence/resolve-location",
    response_model=ResolveEvidenceLocationResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Validate that a source location anchor (page, section, span) exists and points to actual text",
)
def resolve_evidence_location(
    payload: ResolveEvidenceLocationRequestDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.resolve_evidence_location(payload, user_id=user_id)


@router.post(
    "/research/evidence/convert-candidate",
    response_model=ResearchEvidenceDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Promote an evidence candidate into verified Stage 104 ResearchEvidence for an investigation",
)
def convert_evidence_candidate(
    payload: ConvertEvidenceCandidateDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.convert_evidence_candidate(payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchEvidenceCandidateNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 105 — Document Comparison & Financial Fact Variance
# ---------------------------------------------------------------------------

@router.post(
    "/research/documents/compare",
    response_model=DocumentComparisonResultDTO,
    status_code=status.HTTP_200_OK,
    summary="Execute two-document comparison with aligned section text diffs and change detection",
)
def compare_documents_endpoint(
    payload: DocumentComparisonRequestDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.compare_documents(payload, user_id=user_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchComparisonIncompatibleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ResearchComparisonResourceLimitError as e:
        raise HTTPException(status_code=status.HTTP_413_PAYLOAD_TOO_LARGE, detail=str(e))


@router.post(
    "/research/financial-facts/compare",
    response_model=FinancialFactsCompareResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Compare financial statement facts across periods with delta, percentage delta, and zero-base validation",
)
def compare_financial_facts_endpoint(
    payload: FinancialFactsCompareRequestDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.compare_financial_facts(payload, user_id=user_id)
    except ResearchComparisonIncompatibleError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 106 Research Analysis Domain & Specifications
# ---------------------------------------------------------------------------

@router.get(
    "/research/analysis-types",
    response_model=ResearchAnalysisTypeListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List supported institutional research analysis types",
)
def list_analysis_types_endpoint(
    service: ResearchService = Depends(get_research_service),
    _user=Depends(get_current_user),
):
    items = service.list_analysis_types()
    return ResearchAnalysisTypeListResponseDTO(analysis_types=items, total_count=len(items))


@router.get(
    "/research/analyses",
    response_model=ResearchAnalysisListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List user-owned institutional research analyses",
)
def list_analyses_endpoint(
    investigation_id: Optional[str] = Query(None, description="Filter by investigation ID"),
    analysis_type: Optional[ResearchAnalysisType] = Query(None, description="Filter by analysis type"),
    subject_entity_id: Optional[str] = Query(None, description="Filter by primary subject entity ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    items = service.list_analyses(
        user_id=user_id,
        investigation_id=investigation_id,
        analysis_type=analysis_type,
        subject_entity_id=subject_entity_id,
    )
    return ResearchAnalysisListResponseDTO(analyses=items, total_count=len(items))


@router.post(
    "/research/analyses",
    response_model=ResearchAnalysisDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new institutional research analysis specification",
)
def create_analysis_endpoint(
    payload: CreateResearchAnalysisDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_analysis(payload, user_id=user_id)
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchAnalysisTypeUnsupportedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ResearchAnalysisConfigurationInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/research/analyses/{id}",
    response_model=ResearchAnalysisDTO,
    status_code=status.HTTP_200_OK,
    summary="Get research analysis details by ID",
)
def get_analysis_endpoint(
    id: str = Path(..., description="The analysis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_analysis(id, user_id=user_id)
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/analyses/{id}",
    response_model=ResearchAnalysisDTO,
    status_code=status.HTTP_200_OK,
    summary="Update research analysis definition with optimistic concurrency",
)
def update_analysis_endpoint(
    id: str = Path(..., description="The analysis ID"),
    payload: UpdateResearchAnalysisDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_analysis(id, payload, user_id=user_id)
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchAnalysisRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResearchAnalysisConfigurationInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/analyses/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete research analysis",
)
def delete_analysis_endpoint(
    id: str = Path(..., description="The analysis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_analysis(id, user_id=user_id)
        return {"success": True, "message": f"Analysis '{id}' deleted successfully."}
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/analyses/{id}/duplicate",
    response_model=ResearchAnalysisDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a research analysis into draft status",
)
def duplicate_analysis_endpoint(
    id: str = Path(..., description="The analysis ID to duplicate"),
    target_investigation_id: Optional[str] = Query(None, description="Optional target investigation ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.duplicate_analysis(id, user_id=user_id)
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchInvestigationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/analyses/validate",
    response_model=ValidateAnalysisSpecificationResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Validate analysis specification before execution",
)
def validate_analysis_specification_endpoint(
    payload: ValidateAnalysisSpecificationRequestDTO,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.validate_analysis_specification(payload, user_id=user_id)


# ---------------------------------------------------------------------------
# Stage 106 Analysis Runs, Results & Provenance
# ---------------------------------------------------------------------------

@router.post(
    "/research/analyses/{id}/runs",
    response_model=ResearchAnalysisRunDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Execute a reproducible research analysis run",
)
def execute_analysis_run_endpoint(
    id: str = Path(..., description="The analysis ID"),
    input_policy: AnalysisInputPolicy = Query(AnalysisInputPolicy.PINNED_SOURCE_VERSION, description="Input data policy"),
    temporal_cutoff: Optional[str] = Query(None, description="Optional historical public information cutoff date (YYYY-MM-DD)"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.execute_analysis_run(
            analysis_id=id,
            user_id=user_id,
            input_policy=input_policy,
            temporal_cutoff=temporal_cutoff,
        )
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchAnalysisExecutionFailedError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/research/analyses/{id}/runs",
    response_model=ResearchAnalysisRunListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List historical execution runs for an analysis",
)
def list_analysis_runs_endpoint(
    id: str = Path(..., description="The analysis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_analysis_runs(id, user_id=user_id)
        return ResearchAnalysisRunListResponseDTO(analysis_id=id, runs=items, total_count=len(items))
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/analysis-runs/{run_id}",
    response_model=ResearchAnalysisRunDTO,
    status_code=status.HTTP_200_OK,
    summary="Get execution metadata for an analysis run",
)
def get_analysis_run_endpoint(
    run_id: str = Path(..., description="The run ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_analysis_run(run_id, user_id=user_id)
    except (ResearchAnalysisRunNotFoundError, ResearchAnalysisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/analysis-runs/{run_id}/results",
    response_model=ResearchAnalysisResultDTO,
    status_code=status.HTTP_200_OK,
    summary="Get calculated observations, charts, and summary statistics for an analysis run",
)
def get_analysis_run_results_endpoint(
    run_id: str = Path(..., description="The run ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_analysis_run_result(run_id, user_id=user_id)
    except (ResearchAnalysisRunNotFoundError, ResearchAnalysisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/analysis-runs/{run_id}/provenance",
    response_model=AnalysisProvenanceResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Inspect exact source data manifest, revision watermarks, and calculation lineage",
)
def get_analysis_run_provenance_endpoint(
    run_id: str = Path(..., description="The run ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_analysis_run_provenance(run_id, user_id=user_id)
    except (ResearchAnalysisRunNotFoundError, ResearchAnalysisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 106 Hypothesis Evaluation
# ---------------------------------------------------------------------------

@router.post(
    "/research/hypotheses/{id}/evaluations",
    response_model=ResearchHypothesisEvaluationDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Evaluate an analyst hypothesis against reproducible analysis results",
)
def evaluate_hypothesis_endpoint(
    id: str = Path(..., description="The hypothesis ID"),
    payload: EvaluateResearchHypothesisDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.evaluate_hypothesis(id, payload, user_id=user_id)
    except ResearchHypothesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ResearchAnalysisRunNotFoundError, ResearchAnalysisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchHypothesisEvaluationInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/research/hypotheses/{id}/evaluations",
    response_model=ResearchHypothesisEvaluationListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List hypothesis evaluation history",
)
def list_hypothesis_evaluations_endpoint(
    id: str = Path(..., description="The hypothesis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_hypothesis_evaluations(id, user_id=user_id)
        return ResearchHypothesisEvaluationListResponseDTO(hypothesis_id=id, evaluations=items, total_count=len(items))
    except ResearchHypothesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/hypothesis-evaluations/{id}",
    response_model=ResearchHypothesisEvaluationDTO,
    status_code=status.HTTP_200_OK,
    summary="Get hypothesis evaluation details, criteria, and limitations",
)
def get_hypothesis_evaluation_endpoint(
    id: str = Path(..., description="The evaluation ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_hypothesis_evaluation(id, user_id=user_id)
    except ResearchHypothesisEvaluationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestigationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 106 Research Findings
# ---------------------------------------------------------------------------

@router.get(
    "/research/findings",
    response_model=ResearchFindingListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List research findings across investigations and analyses",
)
def list_all_findings_endpoint(
    investigation_id: Optional[str] = Query(None, description="Optional filter by investigation ID"),
    analysis_id: Optional[str] = Query(None, description="Optional filter by analysis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    items = service.list_findings(user_id=user_id, analysis_id=analysis_id, investigation_id=investigation_id)
    return ResearchFindingListResponseDTO(findings=items, total_count=len(items))


@router.get(
    "/research/analyses/{id}/findings",
    response_model=ResearchFindingListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List research findings attached to an analysis",
)
def list_analysis_findings_endpoint(
    id: str = Path(..., description="The analysis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    items = service.list_findings(user_id=user_id, analysis_id=id)
    return ResearchFindingListResponseDTO(findings=items, total_count=len(items))


@router.post(
    "/research/analyses/{id}/findings",
    response_model=ResearchFindingDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Record an institutional research finding with evidence and limitations",
)
def create_finding_endpoint(
    id: str = Path(..., description="The analysis ID"),
    payload: CreateResearchFindingDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_finding(id, payload, user_id=user_id)
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/findings/{id}",
    response_model=ResearchFindingDTO,
    status_code=status.HTTP_200_OK,
    summary="Get research finding details",
)
def get_finding_endpoint(
    id: str = Path(..., description="The finding ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_finding(id, user_id=user_id)
    except ResearchFindingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchFindingAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/findings/{id}",
    response_model=ResearchFindingDTO,
    status_code=status.HTTP_200_OK,
    summary="Update research finding statement, review status, or evidence",
)
def update_finding_endpoint(
    id: str = Path(..., description="The finding ID"),
    payload: UpdateResearchFindingDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_finding(id, payload, user_id=user_id)
    except ResearchFindingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchFindingAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchFindingRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/research/findings/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete research finding",
)
def delete_finding_endpoint(
    id: str = Path(..., description="The finding ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_finding(id, user_id=user_id)
        return {"success": True, "message": f"Finding '{id}' deleted successfully."}
    except ResearchFindingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchFindingAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 106 Assumptions & Scenario Sensitivity
# ---------------------------------------------------------------------------

@router.get(
    "/research/analyses/{id}/assumptions",
    response_model=ResearchAssumptionListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List explicit analyst assumptions for an analysis",
)
def list_assumptions_endpoint(
    id: str = Path(..., description="The analysis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        items = service.list_assumptions(id, user_id=user_id)
        return ResearchAssumptionListResponseDTO(analysis_id=id, assumptions=items, total_count=len(items))
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/analyses/{id}/assumptions",
    response_model=ResearchAssumptionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add an explicit analyst assumption with unit and source context",
)
def create_assumption_endpoint(
    id: str = Path(..., description="The analysis ID"),
    payload: CreateResearchAssumptionDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_assumption(id, payload, user_id=user_id)
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/research/assumptions/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an analyst assumption",
)
def delete_assumption_endpoint(
    id: str = Path(..., description="The assumption ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_assumption(id, user_id=user_id)
        return {"success": True, "message": f"Assumption '{id}' deleted successfully."}
    except ResearchAssumptionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/analyses/{id}/scenarios/sensitivity",
    response_model=ResearchSensitivityResultDTO,
    status_code=status.HTTP_200_OK,
    summary="Execute deterministic what-if sensitivity matrix for an analysis",
)
def execute_sensitivity_scenario_endpoint(
    id: str = Path(..., description="The analysis ID"),
    payload: ExecuteSensitivityScenarioDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.execute_sensitivity_scenario(id, payload, user_id=user_id)
    except ResearchAnalysisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchAnalysisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchScenarioConfigurationInvalidError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 107 Research Reports & Report Templates
# ---------------------------------------------------------------------------

@router.get(
    "/research/report-templates",
    response_model=ResearchReportTemplateListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List institutional research report templates",
)
def list_report_templates_endpoint(
    service: ResearchService = Depends(get_research_service),
    _user=Depends(get_current_user),
):
    return service.list_report_templates()


@router.get(
    "/research/report-templates/{template_id}",
    response_model=ResearchReportTemplateDTO,
    status_code=status.HTTP_200_OK,
    summary="Get report template schema by ID",
)
def get_report_template_endpoint(
    template_id: str = Path(..., description="Template ID"),
    service: ResearchService = Depends(get_research_service),
    _user=Depends(get_current_user),
):
    try:
        return service.get_report_template(template_id)
    except ResearchReportTemplateUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/reports",
    response_model=ResearchReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="List user-owned institutional research reports",
)
def list_reports_endpoint(
    investigation_id: Optional[str] = Query(None, description="Filter by investigation ID"),
    report_type: Optional[ResearchReportType] = Query(None, description="Filter by report type"),
    status_filter: Optional[ReportLifecycleStatus] = Query(None, alias="status", description="Filter by status"),
    subject_id: Optional[str] = Query(None, description="Filter by primary subject ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.list_reports(
        user_id=user_id,
        investigation_id=investigation_id,
        report_type=report_type,
        status=status_filter,
        subject_id=subject_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/research/reports",
    response_model=ResearchReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new institutional research report",
)
def create_report_endpoint(
    payload: CreateResearchReportRequest,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_report(payload, user_id=user_id)
    except ResearchReportTemplateUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/reports/{id}",
    response_model=ResearchReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get research report details with sections and manifests",
)
def get_report_endpoint(
    id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_report(id, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/reports/{id}",
    response_model=ResearchReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update research report parameters with optimistic concurrency",
)
def update_report_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: UpdateResearchReportRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_report(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportFinalizedImmutableError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ResearchReportRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/research/reports/{id}/finalize",
    response_model=ResearchReportDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Finalize and freeze research report into immutable snapshot",
)
def finalize_report_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: FinalizeReportRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.finalize_report(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/research/reports/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete or archive research report",
)
def delete_report_endpoint(
    id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_report(id, user_id=user_id)
        return {"success": True, "message": f"Report '{id}' deleted successfully."}
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 107 Report Sections
# ---------------------------------------------------------------------------

@router.get(
    "/research/reports/{id}/sections",
    response_model=List[ResearchReportSectionDTO],
    status_code=status.HTTP_200_OK,
    summary="List structured sections of a report",
)
def list_report_sections_endpoint(
    id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_report_sections(id, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/reports/{id}/sections",
    response_model=ResearchReportSectionDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add a structured section to a report",
)
def create_report_section_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: CreateReportSectionRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_report_section(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportFinalizedImmutableError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.patch(
    "/research/reports/{id}/sections/{section_id}",
    response_model=ResearchReportSectionDTO,
    status_code=status.HTTP_200_OK,
    summary="Update section heading or content blocks",
)
def update_report_section_endpoint(
    id: str = Path(..., description="Report ID"),
    section_id: str = Path(..., description="Section ID"),
    payload: UpdateReportSectionRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_report_section(id, section_id, payload, user_id=user_id)
    except ResearchReportSectionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportFinalizedImmutableError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/research/reports/{id}/sections/{section_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete section from report",
)
def delete_report_section_endpoint(
    id: str = Path(..., description="Report ID"),
    section_id: str = Path(..., description="Section ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_report_section(id, section_id, user_id=user_id)
        return {"success": True, "message": f"Section '{section_id}' removed."}
    except ResearchReportSectionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportFinalizedImmutableError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post(
    "/research/reports/{id}/sections/reorder",
    response_model=List[ResearchReportSectionDTO],
    status_code=status.HTTP_200_OK,
    summary="Safely reorder sections without destroying references",
)
def reorder_report_sections_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: ReorderReportSectionsRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.reorder_report_sections(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportFinalizedImmutableError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 107 Revisions & Comparison
# ---------------------------------------------------------------------------

@router.get(
    "/research/reports/{id}/revisions",
    response_model=ResearchReportRevisionListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List revision history entries for a report",
)
def list_report_revisions_endpoint(
    id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_report_revisions(id, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/reports/{id}/revisions/compare",
    response_model=CompareReportRevisionsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Compare two revisions of a report and return diff",
)
def compare_report_revisions_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: CompareReportRevisionsRequestDTO = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.compare_report_revisions(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 107 Automated Verification
# ---------------------------------------------------------------------------

@router.post(
    "/research/reports/{id}/verify",
    response_model=ResearchReportVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Run structural, citation, analysis embed, and temporal cutoff checks",
)
def verify_report_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: VerifyReportRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.verify_report(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/research/reports/{id}/verification",
    response_model=Optional[ResearchReportVerificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get latest verification result for a report",
)
def get_latest_verification_endpoint(
    id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_latest_verification(id, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 107 PDF & DOCX Exports
# ---------------------------------------------------------------------------

@router.post(
    "/research/reports/{id}/exports",
    response_model=ResearchReportExportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate institutional publication PDF or DOCX report export",
)
def create_report_export_endpoint(
    id: str = Path(..., description="Report ID"),
    payload: CreateReportExportRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_report_export(id, payload, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReportRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/research/reports/{id}/exports",
    response_model=ResearchReportExportListResponse,
    status_code=status.HTTP_200_OK,
    summary="List publication export jobs for a report",
)
def list_report_exports_endpoint(
    id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_report_exports(id, user_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/report-exports/{export_id}",
    response_model=ResearchReportExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get export artifact metadata and status",
)
def get_report_export_endpoint(
    export_id: str = Path(..., description="Export ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_report_export(export_id, user_id=user_id)
    except ResearchReportExportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportExportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/report-exports/{export_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download authorized PDF or DOCX binary report artifact",
)
def download_report_export_endpoint(
    export_id: str = Path(..., description="Export ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        content, media_type, filename = service.download_export_file(export_id, user_id=user_id)
        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(content)),
            },
        )
    except ResearchReportExportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReportExportAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 107 Structured Investment Theses & Arguments
# ---------------------------------------------------------------------------

@router.get(
    "/research/theses",
    response_model=List[ResearchThesisResponse],
    status_code=status.HTTP_200_OK,
    summary="List user-owned investment theses",
)
def list_theses_endpoint(
    investigation_id: Optional[str] = Query(None, description="Filter by investigation ID"),
    report_id: Optional[str] = Query(None, description="Filter by report ID"),
    subject_id: Optional[str] = Query(None, description="Filter by subject ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.list_theses(
        user_id=user_id,
        investigation_id=investigation_id,
        report_id=report_id,
        subject_id=subject_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/research/theses",
    response_model=ResearchThesisDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new structured investment thesis",
)
def create_thesis_endpoint(
    payload: CreateResearchThesisRequest,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.create_thesis(payload, user_id=user_id)


@router.get(
    "/research/theses/{id}",
    response_model=ResearchThesisDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get investment thesis details and structured arguments",
)
def get_thesis_endpoint(
    id: str = Path(..., description="Thesis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_thesis(id, user_id=user_id)
    except ResearchInvestmentThesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestmentThesisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/theses/{id}",
    response_model=ResearchThesisDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update investment thesis statement or summaries",
)
def update_thesis_endpoint(
    id: str = Path(..., description="Thesis ID"),
    payload: UpdateResearchThesisRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_thesis(id, payload, user_id=user_id)
    except ResearchInvestmentThesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestmentThesisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchInvestmentThesisRevisionConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete(
    "/research/theses/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete investment thesis",
)
def delete_thesis_endpoint(
    id: str = Path(..., description="Thesis ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_thesis(id, user_id=user_id)
        return {"success": True, "message": f"Thesis '{id}' deleted successfully."}
    except ResearchInvestmentThesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestmentThesisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/theses/{id}/arguments",
    response_model=ResearchThesisArgumentDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Add supporting or opposing argument to investment thesis",
)
def create_thesis_argument_endpoint(
    id: str = Path(..., description="Thesis ID"),
    payload: CreateThesisArgumentRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_thesis_argument(id, payload, user_id=user_id)
    except ResearchInvestmentThesisNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestmentThesisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/research/theses/{id}/arguments/{argument_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete argument node from thesis",
)
def delete_thesis_argument_endpoint(
    id: str = Path(..., description="Thesis ID"),
    argument_id: str = Path(..., description="Argument ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        service.delete_thesis_argument(id, argument_id, user_id=user_id)
        return {"success": True, "message": f"Argument '{argument_id}' deleted."}
    except ResearchThesisArgumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchInvestmentThesisAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ---------------------------------------------------------------------------
# Stage 108 Collaboration, Review Workflows, Quality Gates & Circulation
# ---------------------------------------------------------------------------

@router.get(
    "/research/resources/{resource_type}/{resource_id}/participants",
    response_model=ResearchAccessGrantListResponse,
    status_code=status.HTTP_200_OK,
    summary="List access grants and collaborators for a research resource",
)
def list_resource_participants_endpoint(
    resource_type: ResearchResourceType = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_access_grants(resource_type, resource_id, actor_id=user_id)
    except (ResearchInvestigationNotFoundError, ResearchReportNotFoundError, ResearchInvestmentThesisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReviewAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/resources/{resource_type}/{resource_id}/participants",
    response_model=ResearchAccessGrantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grant collaboration access to a user on a research resource",
)
def create_resource_participant_endpoint(
    resource_type: ResearchResourceType = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
    payload: CreateAccessGrantRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_access_grant(resource_type, resource_id, payload, actor_id=user_id)
    except (ResearchInvestigationNotFoundError, ResearchReportNotFoundError, ResearchInvestmentThesisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ResearchAccessGrantForbiddenError, ResearchReviewAccessDeniedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch(
    "/research/participants/{grant_id}",
    response_model=ResearchAccessGrantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update participant role grant",
)
def update_participant_grant_endpoint(
    grant_id: str = Path(..., description="Access grant ID"),
    payload: UpdateAccessGrantRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_access_grant(grant_id, payload, actor_id=user_id)
    except ResearchAccessGrantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ResearchAccessGrantForbiddenError, ResearchReviewAccessDeniedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/research/participants/{grant_id}",
    response_model=ResearchAccessGrantResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke participant access grant",
)
def revoke_participant_grant_endpoint(
    grant_id: str = Path(..., description="Access grant ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.revoke_access_grant(grant_id, actor_id=user_id)
    except ResearchAccessGrantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (ResearchAccessGrantForbiddenError, ResearchReviewAccessDeniedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/reviews",
    response_model=ResearchReviewListResponse,
    status_code=status.HTTP_200_OK,
    summary="List or query formal research review requests",
)
def list_review_requests_endpoint(
    target_id: Optional[str] = Query(None, description="Target report or thesis ID"),
    reviewer_id: Optional[str] = Query(None, description="Assigned reviewer ID"),
    requested_by: Optional[str] = Query(None, description="Requester user ID"),
    status_filter: Optional[ReviewStatus] = Query(None, alias="status", description="Review status filter"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_review_requests(
        target_id=target_id,
        reviewer_id=reviewer_id,
        requested_by=requested_by,
        status=status_filter,
    )


@router.post(
    "/research/reviews",
    response_model=ResearchReviewRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a research report or thesis for formal peer review",
)
def create_review_request_endpoint(
    payload: CreateReviewRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.submit_review_request(payload, actor_id=user_id)
    except (ResearchReportNotFoundError, ResearchInvestmentThesisNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReviewDuplicateActiveRequestError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except (ResearchReviewRevisionMismatchError, ResearchReviewSelfApprovalForbiddenError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/research/reviews/{review_id}",
    response_model=ResearchReviewRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Get details of a specific review request",
)
def get_review_request_endpoint(
    review_id: str = Path(..., description="Review request ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_review_request(review_id, actor_id=user_id)
    except ResearchReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/research/reviews/{review_id}",
    response_model=ResearchReviewRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Update review instructions or assigned reviewer",
)
def update_review_request_endpoint(
    review_id: str = Path(..., description="Review request ID"),
    payload: UpdateReviewRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_review_request(review_id, payload, actor_id=user_id)
    except ResearchReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReviewAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/reviews/{review_id}/cancel",
    response_model=ResearchReviewRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel an active review request",
)
def cancel_review_request_endpoint(
    review_id: str = Path(..., description="Review request ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.cancel_review_request(review_id, actor_id=user_id)
    except ResearchReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReviewAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ResearchReviewInvalidTransitionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/research/reviews/{review_id}/decisions",
    response_model=ResearchReviewDecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a formal review decision (Approve, Request Changes, Reject)",
)
def decide_review_endpoint(
    review_id: str = Path(..., description="Review request ID"),
    payload: CreateReviewDecisionRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.decide_review(review_id, payload, actor_id=user_id)
    except ResearchReviewNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchReviewAlreadyDecidedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ResearchReviewSelfApprovalForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (ResearchReviewRevisionMismatchError, ResearchReviewInvalidTransitionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/research/reports/{report_id}/approval-status",
    response_model=ResearchApprovalStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get formal review approval certification status for a report revision",
)
def get_report_approval_status_endpoint(
    report_id: str = Path(..., description="Report ID"),
    revision_number: Optional[int] = Query(None, description="Optional target revision number"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_report_approval_status(report_id, revision_number=revision_number, actor_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/resources/{resource_type}/{resource_id}/comments",
    response_model=ResearchCommentThreadListResponse,
    status_code=status.HTTP_200_OK,
    summary="List anchored comment threads for a research resource",
)
def list_comments_endpoint(
    resource_type: str = Path(..., description="Resource type e.g. REPORT, INVESTIGATION"),
    resource_id: str = Path(..., description="Resource ID"),
    revision_number: Optional[int] = Query(None, description="Target revision number"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.list_comment_threads(resource_type, resource_id, revision_number=revision_number, actor_id=user_id)


@router.post(
    "/research/resources/{resource_type}/{resource_id}/comments",
    response_model=ResearchCommentThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an anchored comment thread on a section, block, or evidence",
)
def create_comment_thread_endpoint(
    resource_type: str = Path(..., description="Resource type e.g. REPORT, INVESTIGATION"),
    resource_id: str = Path(..., description="Resource ID"),
    payload: CreateCommentThreadRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.create_comment_thread(resource_type, resource_id, payload, actor_id=user_id)
    except (ResearchReportNotFoundError, ResearchInvestigationNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchCommentAnchorInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/research/comment-threads/{thread_id}/replies",
    response_model=ResearchCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post a reply in an existing comment thread",
)
def add_comment_reply_endpoint(
    thread_id: str = Path(..., description="Comment thread ID"),
    payload: CreateCommentReplyRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.add_comment_reply(thread_id, payload, actor_id=user_id)
    except ResearchCommentThreadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/research/comments/{comment_id}",
    response_model=ResearchCommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit an authored comment body",
)
def update_comment_endpoint(
    comment_id: str = Path(..., description="Comment ID"),
    payload: UpdateCommentRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.update_comment(comment_id, payload, actor_id=user_id)
    except (ResearchCommentNotFoundError, ResearchCommentAccessDeniedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/comment-threads/{thread_id}/resolve",
    response_model=ResearchCommentThreadResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve a comment thread",
)
def resolve_comment_thread_endpoint(
    thread_id: str = Path(..., description="Comment thread ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.resolve_comment_thread(thread_id, actor_id=user_id)
    except ResearchCommentThreadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/research/comment-threads/{thread_id}/reopen",
    response_model=ResearchCommentThreadResponse,
    status_code=status.HTTP_200_OK,
    summary="Reopen a resolved comment thread",
)
def reopen_comment_thread_endpoint(
    thread_id: str = Path(..., description="Comment thread ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.reopen_comment_thread(thread_id, actor_id=user_id)
    except ResearchCommentThreadNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/research/reports/{report_id}/quality-gate",
    response_model=QualityGateResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute comprehensive governance quality gate evaluation on report revision",
)
def run_quality_gate_endpoint(
    report_id: str = Path(..., description="Report ID"),
    payload: RunQualityGateRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.run_quality_gate(report_id, payload, actor_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/reports/{report_id}/circulation",
    response_model=ResearchInternalCirculationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List internal circulation records for a research report",
)
def list_circulations_endpoint(
    report_id: str = Path(..., description="Report ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.list_internal_circulations(report_id, actor_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/research/reports/{report_id}/circulation",
    response_model=ResearchInternalCirculationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Circulate an approved or finalized report to internal recipients",
)
def create_circulation_endpoint(
    report_id: str = Path(..., description="Report ID"),
    payload: CreateCirculationRequest = ...,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.circulate_report_internally(report_id, payload, actor_id=user_id)
    except ResearchReportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchQualityGateFailedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ResearchCirculationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/circulation/{circulation_id}/revoke",
    response_model=ResearchInternalCirculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke an internal circulation grant",
)
def revoke_circulation_endpoint(
    circulation_id: str = Path(..., description="Circulation ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.revoke_internal_circulation(circulation_id, actor_id=user_id)
    except ResearchCirculationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchCirculationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/resources/{resource_type}/{resource_id}/audit-events",
    response_model=ResearchReviewAuditEventListResponse,
    status_code=status.HTTP_200_OK,
    summary="List collaboration and review audit trail events for a resource",
)
def list_resource_audit_events_endpoint(
    resource_type: str = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.list_review_audit_events(resource_id, actor_id=user_id)


# ---------------------------------------------------------------------------
# Stage 109 Research Overview, Knowledge, Dependency Lineage, Monitoring & Lifecycle Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/research/overview/summary",
    response_model=ResearchOverviewSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get unified institutional research overview summary counts",
)
def get_research_overview_summary_endpoint(
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.get_institutional_overview_summary(user_id=user_id)


@router.post(
    "/research/knowledge/search",
    response_model=ResearchKnowledgeSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search across authorized research knowledge entries with structured filters",
)
def search_knowledge_endpoint(
    data: ResearchKnowledgeSearchQuery,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.search_knowledge(data, user_id=user_id)


@router.get(
    "/research/knowledge/{entry_id}",
    response_model=ResearchKnowledgeEntryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single research knowledge entry by ID",
)
def get_knowledge_entry_endpoint(
    entry_id: str = Path(..., description="Knowledge Entry ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.get_knowledge_entry(entry_id, user_id=user_id)
    except ResearchKnowledgeEntryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchKnowledgeAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/dependencies/lineage/{resource_type}/{resource_id}",
    response_model=ResearchDependencyLineageResponse,
    status_code=status.HTTP_200_OK,
    summary="Traverse bounded upstream and downstream dependency lineage graph",
)
def get_dependency_lineage_endpoint(
    resource_type: str = Path(..., description="Root resource type"),
    resource_id: str = Path(..., description="Root resource ID"),
    max_depth: int = Query(5, ge=1, le=10, description="Maximum traversal depth"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.get_dependency_lineage(
        root_type=resource_type, root_id=resource_id, user_id=user_id, max_depth=max_depth
    )


@router.post(
    "/research/source-changes",
    response_model=ResearchSourceChangeEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a canonical data source revision or amendment event",
)
def record_source_change_endpoint(
    data: CreateSourceChangeEventRequest,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.record_source_change_event(data, actor_id=user_id)
    except ResearchSourceChangeDuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/research/source-changes",
    response_model=ResearchSourceChangeEventListResponse,
    status_code=status.HTTP_200_OK,
    summary="List detected canonical source-change events",
)
def list_source_changes_endpoint(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_source_change_events(source_type=source_type, limit=limit, offset=offset)


@router.get(
    "/research/source-changes/{change_event_id}",
    response_model=ResearchSourceChangeEventResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single source-change event by ID",
)
def get_source_change_endpoint(
    change_event_id: str = Path(..., description="Change event ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    try:
        return service.get_source_change_event(change_event_id)
    except ResearchSourceChangeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/research/source-changes/{change_event_id}/impacts",
    response_model=ResearchImpactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List evaluated research impact assessments for a source change",
)
def list_change_impacts_endpoint(
    change_event_id: str = Path(..., description="Change event ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_impact_assessments(change_event_id=change_event_id)


@router.get(
    "/research/impacts",
    response_model=ResearchImpactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List evaluated research impact assessments",
)
def list_impacts_endpoint(
    target_id: Optional[str] = Query(None, description="Filter by target research artifact ID"),
    change_event_id: Optional[str] = Query(None, description="Filter by change event ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_impact_assessments(change_event_id=change_event_id, target_id=target_id)


@router.post(
    "/research/revalidations",
    response_model=ResearchRevalidationResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute automated evidence and reference revalidation on a research artifact",
)
def run_revalidation_endpoint(
    data: CreateRevalidationRequest,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.run_revalidation(data, actor_id=user_id)
    except ResearchRevalidationTargetUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchRevalidationAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/research/resources/{resource_type}/{resource_id}/revalidations",
    response_model=List[ResearchRevalidationResultResponse],
    status_code=status.HTTP_200_OK,
    summary="List revalidation results for a research artifact",
)
def list_resource_revalidations_endpoint(
    resource_type: str = Path(..., description="Resource type"),
    resource_id: str = Path(..., description="Resource ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    return service.list_revalidation_results(target_id=resource_id)


@router.get(
    "/research/updates",
    response_model=ResearchUpdateItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="List actionable items in the research update queue",
)
def list_updates_endpoint(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    investigation_id: Optional[str] = Query(None, description="Filter by investigation ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    st = None
    if status_filter:
        try:
            from atlas.research.enums import UpdateItemStatus
            st = UpdateItemStatus(status_filter)
        except ValueError:
            pass
    return service.list_update_items(
        user_id=user_id, status=st, investigation_id=investigation_id, limit=limit, offset=offset
    )


@router.post(
    "/research/updates",
    response_model=ResearchUpdateItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an actionable research update queue item",
)
def create_update_item_endpoint(
    data: CreateUpdateItemRequest,
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    return service.create_update_item(data, user_id=user_id)


@router.post(
    "/research/updates/{update_item_id}/acknowledge",
    response_model=ResearchUpdateItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Acknowledge a research update queue item",
)
def acknowledge_update_endpoint(
    update_item_id: str = Path(..., description="Update item ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.acknowledge_update_item(update_item_id, user_id=user_id)
    except ResearchUpdateItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchUpdateItemAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/updates/{update_item_id}/resolve",
    response_model=ResearchUpdateItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve a research update queue item with resolution note",
)
def resolve_update_endpoint(
    data: ResolveUpdateItemRequest,
    update_item_id: str = Path(..., description="Update item ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.resolve_update_item(update_item_id, data=data, user_id=user_id)
    except ResearchUpdateItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchUpdateItemAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/updates/{update_item_id}/dismiss",
    response_model=ResearchUpdateItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Dismiss a research update queue item",
)
def dismiss_update_endpoint(
    update_item_id: str = Path(..., description="Update item ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.dismiss_update_item(update_item_id, user_id=user_id)
    except ResearchUpdateItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchUpdateItemAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/research/updates/{update_item_id}/reopen",
    response_model=ResearchUpdateItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Reopen a resolved or dismissed research update queue item",
)
def reopen_update_endpoint(
    update_item_id: str = Path(..., description="Update item ID"),
    service: ResearchService = Depends(get_research_service),
    user: AuthPrincipal = Depends(get_current_user),
):
    user_id = _get_user_id(user)
    try:
        return service.reopen_update_item(update_item_id, user_id=user_id)
    except ResearchUpdateItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResearchUpdateItemAccessDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))



# ---------------------------------------------------------------------------
# Stage 36 Legacy Compatibility Route
# ---------------------------------------------------------------------------

@router.get(
    "/research-documents/{entity_id}",
    response_model=ResearchDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get research document specialization row (Stage 36 legacy)",
)
def get_research_document_legacy(
    entity_id: uuid.UUID = Path(..., description="The research document UUID"),
    session: Session = Depends(get_db_session),
    _user=Depends(get_current_user),
):
    service = ResearchDocumentService(session)
    try:
        return service.get_research_document(entity_id)
    except ResearchDocumentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
