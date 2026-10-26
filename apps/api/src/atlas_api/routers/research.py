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
    InvestigationLifecycleStatus,
    ResearchSourceType,
    ResearchType,
)
from atlas.research.errors import (
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
    ResearchHypothesisNotFoundError,
    ResearchInvestigationAccessDeniedError,
    ResearchInvestigationNotFoundError,
    ResearchInvestigationRevisionConflictError,
    ResearchNoteAccessDeniedError,
    ResearchNoteContentInvalidError,
    ResearchNoteNotFoundError,
    ResearchNoteRevisionConflictError,
    ResearchQuestionNotFoundError,
    ResearchSemanticSearchUnavailableError,
    ResearchSourceNotFoundError,
    ResearchSourceUrlUnsafeError,
)
from atlas.research.schemas import (
    AttachResearchEvidenceDTO,
    ConvertEvidenceCandidateDTO,
    CreateResearchClaimDTO,
    CreateResearchHypothesisDTO,
    CreateResearchInvestigationDTO,
    CreateResearchNoteDTO,
    CreateResearchQuestionDTO,
    DocumentComparisonRequestDTO,
    DocumentComparisonResultDTO,
    DocumentSearchRequestDTO,
    DocumentSearchResponseDTO,
    EvidenceCandidateListResponseDTO,
    FinancialFactsCompareRequestDTO,
    FinancialFactsCompareResponseDTO,
    LinkResearchSourceDTO,
    ResearchActivityTimelineResponseDTO,
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
    ResearchHypothesisDTO,
    ResearchHypothesisListResponseDTO,
    ResearchInvestigationDTO,
    ResearchInvestigationListResponseDTO,
    ResearchNoteDTO,
    ResearchNoteListResponseDTO,
    ResearchNoteRevisionDTO,
    ResearchOverviewSummaryDTO,
    ResearchQuestionDTO,
    ResearchQuestionListResponseDTO,
    ResearchSourceDiscoveryQueryDTO,
    ResearchSourceDiscoveryResponseDTO,
    ResearchSourceListResponseDTO,
    ResearchSourceReferenceDTO,
    ResearchSourceTypeListResponseDTO,
    ResolveEvidenceLocationRequestDTO,
    ResolveEvidenceLocationResponseDTO,
    UpdateResearchClaimDTO,
    UpdateResearchHypothesisDTO,
    UpdateResearchInvestigationDTO,
    UpdateResearchNoteDTO,
    UpdateResearchQuestionDTO,
)
from atlas.research.service import (
    ResearchDocumentService,
    ResearchService,
    get_research_service,
)
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
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
