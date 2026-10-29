"""Research Services for Institutional Financial Research Platform (Stage 104)."""

import datetime
import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Legacy Stage 36 imports and classes
from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.research.analysis.calculations import get_supported_analysis_types
from atlas.research.analysis.engine import (
    CANONICAL_COMPANY_FUNDAMENTALS,
    ResearchAnalysisEngine,
)
from atlas.research.domain import (
    HypothesisTestCriteria,
    QualityGateResult,
    ResearchAccessGrant,
    ResearchAnalysis,
    ResearchAnalysisAssumption,
    ResearchAnalysisSpecification,
    ResearchComment,
    ResearchCommentThread,
    ResearchFinding,
    ResearchInternalCirculation,
    ResearchInvestigation,
    ResearchInvestmentThesis,
    ResearchReport,
    ResearchReportExport,
    ResearchReportSection,
    ResearchReviewAuditEvent,
    ResearchReviewDecision,
    ResearchReviewRequest,
    ResearchScenario,
    ResearchSourceReference,
    ResearchThesisArgument,
)
from atlas.research.enums import (
    AnalysisExecutionStatus,
    AnalysisInputPolicy,
    CirculationStatus,
    CommentAnchorType,
    CommentThreadStatus,
    ExportFormat,
    ExportStatus,
    InvestigationLifecycleStatus,
    ReportLifecycleStatus,
    ReportSectionType,
    ResearchActivityAction,
    ResearchAnalysisType,
    ResearchAuditEventType,
    ResearchFindingReviewStatus,
    ResearchPrincipalType,
    ResearchReportType,
    ResearchResourceType,
    ResearchRole,
    ResearchSourceType,
    ResearchType,
    ReviewDecisionType,
    ReviewScope,
    ReviewStatus,
    ScenarioType,
    SourceAvailabilityStatus,
    ThesisLifecycleStatus,
)
from atlas.research.errors import (
    InvalidResearchDocumentKindError,
    ResearchAccessGrantForbiddenError,
    ResearchAccessGrantNotFoundError,
    ResearchAccessRevokedError,
    ResearchAccessRoleInvalidError,
    ResearchAnalysisAccessDeniedError,
    ResearchAnalysisNotFoundError,
    ResearchAnalysisRunNotFoundError,
    ResearchAnalysisTypeUnsupportedError,
    ResearchAssumptionNotFoundError,
    ResearchCirculationAccessDeniedError,
    ResearchCirculationNotFoundError,
    ResearchCirculationRevokedError,
    ResearchClaimNotFoundError,
    ResearchCommentAccessDeniedError,
    ResearchCommentAnchorInvalidError,
    ResearchCommentNotFoundError,
    ResearchCommentThreadNotFoundError,
    ResearchDocumentDataInconsistentError,
    ResearchDocumentNotFoundError,
    ResearchFindingAccessDeniedError,
    ResearchFindingNotFoundError,
    ResearchHypothesisEvaluationNotFoundError,
    ResearchHypothesisNotFoundError,
    ResearchInvestigationAccessDeniedError,
    ResearchInvestigationNotFoundError,
    ResearchInvestmentThesisAccessDeniedError,
    ResearchInvestmentThesisNotFoundError,
    ResearchNoteAccessDeniedError,
    ResearchNoteNotFoundError,
    ResearchParticipantCrossTenantError,
    ResearchParticipantIneligibleError,
    ResearchQualityGateFailedError,
    ResearchQuestionNotFoundError,
    ResearchReportAccessDeniedError,
    ResearchReportExportAccessDeniedError,
    ResearchReportExportNotFoundError,
    ResearchReportNotFoundError,
    ResearchReportRevisionConflictError,
    ResearchReportTemplateUnavailableError,
    ResearchReviewAccessDeniedError,
    ResearchReviewAlreadyDecidedError,
    ResearchReviewDuplicateActiveRequestError,
    ResearchReviewInvalidTransitionError,
    ResearchReviewNotFoundError,
    ResearchReviewRevisionMismatchError,
    ResearchReviewSelfApprovalForbiddenError,
    ResearchSourceNotFoundError,
)
from atlas.research.reports.exports import render_report_docx, render_report_pdf
from atlas.research.reports.templates import (
    get_report_template,
    list_report_templates,
)
from atlas.research.reports.verification import verify_research_report
from atlas.research.repository import ResearchDocumentRepository, ResearchRepository
from atlas.research.schemas import (
    # Stage 106 Schemas
    AnalysisProvenanceResponseDTO,
    AnalyticalObservationRowDTO,
    AnalyticalSummaryStatisticsDTO,
    # Stage 107 Schemas
    CompareReportRevisionsRequestDTO,
    CompareReportRevisionsResponseDTO,
    # Stage 105 Schemas
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
    DocumentComparisonSectionDiffDTO,
    DocumentSearchHitDTO,
    DocumentSearchRequestDTO,
    DocumentSearchResponseDTO,
    EvaluateResearchHypothesisDTO,
    EvidenceCandidateListResponseDTO,
    ExecuteSensitivityScenarioDTO,
    FinalizeReportRequest,
    FinancialFactComparisonDTO,
    FinancialFactsCompareRequestDTO,
    FinancialFactsCompareResponseDTO,
    HypothesisTestCriteriaDTO,
    LinkResearchSourceDTO,
    ReorderReportSectionsRequest,
    ResearchActivityDTO,
    ResearchAnalysisDTO,
    ResearchAnalysisResultDTO,
    ResearchAnalysisRunDTO,
    ResearchAnalysisSpecificationDTO,
    ResearchAnalysisTypeDTO,
    ResearchAssumptionDTO,
    ResearchCitationDTO,
    ResearchClaimDTO,
    ResearchDocumentOutlineDTO,
    ResearchDocumentProcessingStatusDTO,
    ResearchDocumentResponse,
    ResearchDocumentSectionDTO,
    ResearchDocumentTableDTO,
    ResearchDocumentTableListResponseDTO,
    ResearchEvidenceCandidateDTO,
    ResearchEvidenceDTO,
    ResearchFindingDTO,
    ResearchHypothesisDTO,
    ResearchHypothesisEvaluationDTO,
    ResearchInvestigationDTO,
    ResearchNoteDTO,
    ResearchNoteRevisionDTO,
    ResearchOverviewSummaryDTO,
    ResearchQuestionDTO,
    ResearchReportDetailResponse,
    ResearchReportExportListResponse,
    ResearchReportExportResponse,
    ResearchReportListResponse,
    ResearchReportResponse,
    ResearchReportRevisionDTO,
    ResearchReportRevisionListResponseDTO,
    ResearchReportSectionDTO,
    ResearchReportTemplateDTO,
    ResearchReportTemplateListResponseDTO,
    ResearchReportVerificationResponse,
    ResearchSearchHitDTO,
    ResearchSensitivityResultDTO,
    ResearchSourceDiscoveryQueryDTO,
    ResearchSourceDiscoveryResponseDTO,
    ResearchSourceReferenceDTO,
    ResearchSourceTypeItemDTO,
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
    ResearchReviewAuditEventResponse,
    ResearchReviewDecisionResponse,
    ResearchReviewListResponse,
    ResearchReviewRequestResponse,
    RunQualityGateRequest,
    UpdateAccessGrantRequest,
    UpdateCommentRequest,
    UpdateReviewRequest,
)
from atlas.research.security import (
    sanitize_markdown_text,
    validate_analyst_text,
    validate_and_sanitize_url,
)
from atlas.research.types import ResearchDocumentKind
from atlas.research.validation import validate_abstract_text, validate_language_code

# ---------------------------------------------------------------------------
# Legacy Stage 36 Document Service
# ---------------------------------------------------------------------------

class ResearchDocumentService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ResearchDocumentRepository(session)
        self.entity_service = EntityService(session)
        self.entity_repository = EntityRepository(session)

    def create_research_document(
        self,
        canonical_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        document_kind: Optional[str] = None,
        publication_date: Optional[datetime.date] = None,
        language_code: Optional[str] = None,
        abstract_text: Optional[str] = None,
    ) -> ResearchDocumentResponse:

        if document_kind is not None:
            try:
                ResearchDocumentKind(document_kind)
            except ValueError:
                raise InvalidResearchDocumentKindError(f"Invalid document_kind: {document_kind}")

        language_code = validate_language_code(language_code)
        abstract_text = validate_abstract_text(abstract_text)

        entity = self.entity_service.create_entity(
            entity_type_key=EntityTypeKey.RESEARCH_DOCUMENT,
            canonical_name=canonical_name,
            display_name=display_name,
            description=description,
        )

        try:
            doc = self.repository.create_research_document_specialization(
                entity_id=entity.entity_id,
                document_kind=document_kind,
                publication_date=publication_date,
                language_code=language_code,
                abstract_text=abstract_text,
            )
            self.session.flush()
        except IntegrityError:
            self.session.rollback()
            raise

        return ResearchDocumentResponse(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            display_name=entity.display_name,
            description=entity.description,
            document_kind=doc.document_kind,
            publication_date=doc.publication_date,
            language_code=doc.language_code,
            abstract_text=doc.abstract_text,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def get_research_document(self, entity_id: uuid.UUID) -> ResearchDocumentResponse:
        entity = self.entity_repository.get_entity(entity_id)
        if not entity:
            raise ResearchDocumentNotFoundError(f"Research Document {entity_id} not found.")

        if entity.entity_type != EntityTypeKey.RESEARCH_DOCUMENT:
            raise ResearchDocumentNotFoundError(f"Entity {entity_id} is not a Research Document.")

        doc_tuple = self.repository.get_research_document(entity_id)
        if not doc_tuple:
            raise ResearchDocumentDataInconsistentError(
                f"Research Document {entity_id} missing specialization row."
            )

        _, doc = doc_tuple

        return ResearchDocumentResponse.model_validate(
            {
                **entity.__dict__,
                "document_kind": doc.document_kind,
                "publication_date": doc.publication_date,
                "language_code": doc.language_code,
                "abstract_text": doc.abstract_text,
            }
        )


# ---------------------------------------------------------------------------
# Stage 104 Canonical Research Platform Service
# ---------------------------------------------------------------------------

class ResearchService:
    """Institutional Financial Research Service orchestrating investigations, evidence, and notes."""

    def __init__(self, repository: Optional[ResearchRepository] = None):
        self.repository = repository or ResearchRepository()

    # -----------------------------------------------------------------------
    # Helper & Access Control Methods
    # -----------------------------------------------------------------------
    def _check_investigation_access(self, investigation: ResearchInvestigation, user_id: str):
        """Enforce strict user ownership and privacy boundaries."""
        if investigation.owner_user_id != user_id and investigation.owner_user_id != "default-user":
            raise ResearchInvestigationAccessDeniedError(
                f"Principal '{user_id}' does not have authorized access to investigation '{investigation.investigation_id}'."
            )

    def _enrich_investigation_dto(self, inv: ResearchInvestigation) -> ResearchInvestigationDTO:
        notes = self.repository.list_notes_by_investigation(inv.investigation_id)
        sources = self.repository.list_sources_by_investigation(inv.investigation_id)
        questions = self.repository.list_questions_by_investigation(inv.investigation_id)
        hypotheses = self.repository.list_hypotheses_by_investigation(inv.investigation_id)
        claims = self.repository.list_claims_by_investigation(inv.investigation_id)
        evidence = self.repository.list_evidence_by_investigation(inv.investigation_id)

        return ResearchInvestigationDTO(
            investigation_id=inv.investigation_id,
            owner_user_id=inv.owner_user_id,
            title=inv.title,
            description=inv.description,
            primary_subject_entity_id=inv.primary_subject_entity_id,
            primary_subject_type=inv.primary_subject_type,
            secondary_entity_ids=inv.secondary_entity_ids,
            research_type=inv.research_type,
            research_objective=inv.research_objective,
            status=inv.status,
            revision=inv.revision,
            created_at=inv.created_at,
            updated_at=inv.updated_at,
            archived_at=inv.archived_at,
            provenance=inv.provenance,
            notes_count=len(notes),
            sources_count=len(sources),
            questions_count=len(questions),
            hypotheses_count=len(hypotheses),
            claims_count=len(claims),
            evidence_count=len(evidence),
        )

    def _check_analysis_access(self, analysis: ResearchAnalysis, user_id: str):
        """Enforce strict user ownership and privacy boundaries for analyses."""
        if analysis.owner_user_id != user_id and analysis.owner_user_id != "default-user":
            raise ResearchAnalysisAccessDeniedError(
                f"Principal '{user_id}' does not have authorized access to analysis '{analysis.analysis_id}'."
            )

    def _check_finding_access(self, finding: ResearchFinding, user_id: str):
        """Enforce strict user ownership and privacy boundaries for research findings."""
        if finding.author_user_id != user_id and finding.author_user_id != "default-user":
            raise ResearchFindingAccessDeniedError(
                f"Principal '{user_id}' does not have authorized access to finding '{finding.finding_id}'."
            )

    def _enrich_analysis_dto(self, a: ResearchAnalysis) -> ResearchAnalysisDTO:
        runs = self.repository.list_analysis_runs(a.analysis_id)
        findings = self.repository.list_findings(analysis_id=a.analysis_id)

        spec_dto = ResearchAnalysisSpecificationDTO(
            analysis_type=a.specification.analysis_type,
            primary_entity_id=a.specification.primary_entity_id,
            secondary_entity_ids=a.specification.secondary_entity_ids,
            metric_ids=a.specification.metric_ids,
            time_range_start=a.specification.time_range_start,
            time_range_end=a.specification.time_range_end,
            frequency=a.specification.frequency,
            input_version_policy=a.specification.input_version_policy,
            outlier_policy=a.specification.outlier_policy,
            currency=a.specification.currency,
            as_known_at_cutoff=a.specification.as_known_at_cutoff,
            parameters=a.specification.parameters,
            methodology_version=a.specification.methodology_version,
        )

        return ResearchAnalysisDTO(
            analysis_id=a.analysis_id,
            investigation_id=a.investigation_id,
            owner_user_id=a.owner_user_id,
            title=a.title,
            description=a.description,
            analysis_type=a.analysis_type,
            research_objective=a.research_objective,
            primary_subject_entity_id=a.primary_subject_entity_id,
            primary_subject_type=a.primary_subject_type,
            secondary_entity_ids=a.secondary_entity_ids,
            specification=spec_dto,
            status=a.status,
            current_revision=a.current_revision,
            created_at=a.created_at,
            updated_at=a.updated_at,
            archived_at=a.archived_at,
            linked_question_ids=a.linked_question_ids,
            linked_hypothesis_ids=a.linked_hypothesis_ids,
            latest_run_id=runs[0].run_id if runs else None,
            runs_count=len(runs),
            findings_count=len(findings),
            provenance=a.provenance,
        )

    # -----------------------------------------------------------------------
    # Investigation Operations
    # -----------------------------------------------------------------------
    def create_investigation(
        self,
        data: CreateResearchInvestigationDTO,
        user_id: str,
    ) -> ResearchInvestigationDTO:
        clean_title = validate_analyst_text("title", data.title, max_length=500, required=True)
        clean_desc = sanitize_markdown_text(data.description or "", max_length=50000)
        clean_obj = validate_analyst_text("research_objective", data.research_objective, max_length=5000, required=False)

        inv = self.repository.create_investigation(
            owner_user_id=user_id,
            title=clean_title,
            research_type=data.research_type,
            primary_subject_entity_id=data.primary_subject_entity_id,
            primary_subject_type=data.primary_subject_type,
            secondary_entity_ids=data.secondary_entity_ids,
            research_objective=clean_obj,
            description=clean_desc,
        )
        return self._enrich_investigation_dto(inv)

    def get_investigation(self, investigation_id: str, user_id: str) -> ResearchInvestigationDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return self._enrich_investigation_dto(inv)

    def update_investigation(
        self,
        investigation_id: str,
        data: UpdateResearchInvestigationDTO,
        user_id: str,
    ) -> ResearchInvestigationDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        clean_title = validate_analyst_text("title", data.title, max_length=500, required=True) if data.title is not None else None
        clean_obj = validate_analyst_text("research_objective", data.research_objective, max_length=5000, required=False) if data.research_objective is not None else None
        clean_desc = sanitize_markdown_text(data.description or "", max_length=50000) if data.description is not None else None

        updated = self.repository.update_investigation(
            investigation_id=investigation_id,
            expected_revision=data.expected_revision,
            title=clean_title,
            research_type=data.research_type,
            primary_subject_entity_id=data.primary_subject_entity_id,
            primary_subject_type=data.primary_subject_type,
            secondary_entity_ids=data.secondary_entity_ids,
            research_objective=clean_obj,
            description=clean_desc,
            status=data.status,
            actor_user_id=user_id,
        )
        return self._enrich_investigation_dto(updated)

    def archive_investigation(self, investigation_id: str, user_id: str) -> ResearchInvestigationDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        archived = self.repository.archive_investigation(investigation_id, actor_user_id=user_id)
        return self._enrich_investigation_dto(archived)

    def delete_investigation(self, investigation_id: str, user_id: str) -> bool:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return self.repository.delete_investigation(investigation_id)

    def list_investigations(
        self,
        user_id: str,
        entity_id: Optional[str] = None,
        status: Optional[InvestigationLifecycleStatus] = None,
        research_type: Optional[ResearchType] = None,
        q: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ResearchInvestigationDTO], int]:
        items, total = self.repository.list_investigations(
            owner_user_id=user_id,
            entity_id=entity_id,
            status=status,
            research_type=research_type,
            q=q,
            limit=limit,
            offset=offset,
        )
        return [self._enrich_investigation_dto(x) for x in items], total

    # -----------------------------------------------------------------------
    # Research Question Operations
    # -----------------------------------------------------------------------
    def add_question(
        self,
        investigation_id: str,
        data: CreateResearchQuestionDTO,
        user_id: str,
    ) -> ResearchQuestionDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        clean_text = validate_analyst_text("question_text", data.question_text, max_length=2000, required=True)
        q = self.repository.add_question(
            investigation_id=investigation_id,
            question_text=clean_text,
            related_entity_ids=data.related_entity_ids,
            actor_user_id=user_id,
        )
        return ResearchQuestionDTO(**q.__dict__)

    def update_question(
        self,
        question_id: str,
        data: UpdateResearchQuestionDTO,
        user_id: str,
    ) -> ResearchQuestionDTO:
        q = self.repository.get_question(question_id)
        if not q:
            raise ResearchQuestionNotFoundError(f"Question '{question_id}' not found.")
        inv = self.repository.get_investigation(q.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)

        clean_text = validate_analyst_text("question_text", data.question_text, max_length=2000, required=True) if data.question_text is not None else None

        updated = self.repository.update_question(
            question_id=question_id,
            question_text=clean_text,
            status=data.status,
            related_entity_ids=data.related_entity_ids,
            related_evidence_ids=data.related_evidence_ids,
            actor_user_id=user_id,
        )
        return ResearchQuestionDTO(**updated.__dict__)

    def delete_question(self, question_id: str, user_id: str) -> bool:
        q = self.repository.get_question(question_id)
        if not q:
            raise ResearchQuestionNotFoundError(f"Question '{question_id}' not found.")
        inv = self.repository.get_investigation(q.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)
        return self.repository.delete_question(question_id, actor_user_id=user_id)

    def list_questions(self, investigation_id: str, user_id: str) -> List[ResearchQuestionDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return [ResearchQuestionDTO(**x.__dict__) for x in self.repository.list_questions_by_investigation(investigation_id)]

    # -----------------------------------------------------------------------
    # Research Hypothesis Operations
    # -----------------------------------------------------------------------
    def add_hypothesis(
        self,
        investigation_id: str,
        data: CreateResearchHypothesisDTO,
        user_id: str,
    ) -> ResearchHypothesisDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        clean_stmt = validate_analyst_text("statement", data.statement, max_length=5000, required=True)
        h = self.repository.add_hypothesis(
            investigation_id=investigation_id,
            statement=clean_stmt,
            related_claim_ids=data.related_claim_ids,
            related_evidence_ids=data.related_evidence_ids,
            actor_user_id=user_id,
        )
        return ResearchHypothesisDTO(**h.__dict__)

    def update_hypothesis(
        self,
        hypothesis_id: str,
        data: UpdateResearchHypothesisDTO,
        user_id: str,
    ) -> ResearchHypothesisDTO:
        h = self.repository.get_hypothesis(hypothesis_id)
        if not h:
            raise ResearchHypothesisNotFoundError(f"Hypothesis '{hypothesis_id}' not found.")
        inv = self.repository.get_investigation(h.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)

        clean_stmt = validate_analyst_text("statement", data.statement, max_length=5000, required=True) if data.statement is not None else None

        updated = self.repository.update_hypothesis(
            hypothesis_id=hypothesis_id,
            statement=clean_stmt,
            status=data.status,
            related_claim_ids=data.related_claim_ids,
            related_evidence_ids=data.related_evidence_ids,
            actor_user_id=user_id,
        )
        return ResearchHypothesisDTO(**updated.__dict__)

    def delete_hypothesis(self, hypothesis_id: str, user_id: str) -> bool:
        h = self.repository.get_hypothesis(hypothesis_id)
        if not h:
            raise ResearchHypothesisNotFoundError(f"Hypothesis '{hypothesis_id}' not found.")
        inv = self.repository.get_investigation(h.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)
        return self.repository.delete_hypothesis(hypothesis_id, actor_user_id=user_id)

    def list_hypotheses(self, investigation_id: str, user_id: str) -> List[ResearchHypothesisDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return [ResearchHypothesisDTO(**x.__dict__) for x in self.repository.list_hypotheses_by_investigation(investigation_id)]

    # -----------------------------------------------------------------------
    # Research Note Operations
    # -----------------------------------------------------------------------
    def create_note(
        self,
        investigation_id: str,
        data: CreateResearchNoteDTO,
        user_id: str,
    ) -> ResearchNoteDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        clean_title = validate_analyst_text("title", data.title, max_length=500, required=True)
        clean_body = sanitize_markdown_text(data.body_document)

        note = self.repository.create_note(
            investigation_id=investigation_id,
            owner_user_id=user_id,
            title=clean_title,
            body_document=clean_body,
            note_type=data.note_type,
            related_entity_ids=data.related_entity_ids,
            linked_source_ids=data.linked_source_ids,
            linked_evidence_ids=data.linked_evidence_ids,
        )
        return ResearchNoteDTO(**note.__dict__)

    def get_note(self, note_id: str, user_id: str) -> ResearchNoteDTO:
        note = self.repository.get_note(note_id)
        if not note:
            raise ResearchNoteNotFoundError(f"Research note '{note_id}' not found.")
        if note.owner_user_id != user_id:
            raise ResearchNoteAccessDeniedError(f"Principal '{user_id}' does not have access to note '{note_id}'.")
        return ResearchNoteDTO(**note.__dict__)

    def update_note(
        self,
        note_id: str,
        data: UpdateResearchNoteDTO,
        user_id: str,
    ) -> ResearchNoteDTO:
        note = self.repository.get_note(note_id)
        if not note:
            raise ResearchNoteNotFoundError(f"Research note '{note_id}' not found.")
        if note.owner_user_id != user_id:
            raise ResearchNoteAccessDeniedError(f"Principal '{user_id}' does not have access to note '{note_id}'.")

        clean_title = validate_analyst_text("title", data.title, max_length=500, required=True) if data.title is not None else None
        clean_body = sanitize_markdown_text(data.body_document) if data.body_document is not None else None

        updated = self.repository.update_note(
            note_id=note_id,
            expected_revision=data.expected_revision,
            title=clean_title,
            body_document=clean_body,
            note_type=data.note_type,
            status=data.status,
            related_entity_ids=data.related_entity_ids,
            linked_source_ids=data.linked_source_ids,
            linked_evidence_ids=data.linked_evidence_ids,
            citation_ids=data.citation_ids,
            actor_user_id=user_id,
        )
        return ResearchNoteDTO(**updated.__dict__)

    def delete_note(self, note_id: str, user_id: str) -> bool:
        note = self.repository.get_note(note_id)
        if not note:
            raise ResearchNoteNotFoundError(f"Research note '{note_id}' not found.")
        if note.owner_user_id != user_id:
            raise ResearchNoteAccessDeniedError(f"Principal '{user_id}' does not have access to note '{note_id}'.")
        return self.repository.delete_note(note_id, actor_user_id=user_id)

    def list_notes(self, investigation_id: str, user_id: str) -> List[ResearchNoteDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return [ResearchNoteDTO(**x.__dict__) for x in self.repository.list_notes_by_investigation(investigation_id)]

    def get_note_revisions(self, note_id: str, user_id: str) -> List[ResearchNoteRevisionDTO]:
        note = self.repository.get_note(note_id)
        if not note:
            raise ResearchNoteNotFoundError(f"Research note '{note_id}' not found.")
        if note.owner_user_id != user_id:
            raise ResearchNoteAccessDeniedError(f"Principal '{user_id}' does not have access to note '{note_id}'.")
        return [ResearchNoteRevisionDTO(**r.__dict__) for r in self.repository.get_note_revisions(note_id)]

    # -----------------------------------------------------------------------
    # Research Claim Operations
    # -----------------------------------------------------------------------
    def create_claim(
        self,
        investigation_id: str,
        data: CreateResearchClaimDTO,
        user_id: str,
    ) -> ResearchClaimDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        clean_stmt = validate_analyst_text("statement", data.statement, max_length=5000, required=True)
        claim = self.repository.create_claim(
            investigation_id=investigation_id,
            statement=clean_stmt,
            claim_category=data.claim_category,
            evidence_status=data.evidence_status,
            supporting_evidence_ids=data.supporting_evidence_ids,
            contradicting_evidence_ids=data.contradicting_evidence_ids,
            related_entity_ids=data.related_entity_ids,
            author_user_id=user_id,
        )
        return ResearchClaimDTO(**claim.__dict__)

    def update_claim(
        self,
        claim_id: str,
        data: UpdateResearchClaimDTO,
        user_id: str,
    ) -> ResearchClaimDTO:
        c = self.repository.get_claim(claim_id)
        if not c:
            raise ResearchClaimNotFoundError(f"Claim '{claim_id}' not found.")
        inv = self.repository.get_investigation(c.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)

        clean_stmt = validate_analyst_text("statement", data.statement, max_length=5000, required=True) if data.statement is not None else None

        updated = self.repository.update_claim(
            claim_id=claim_id,
            statement=clean_stmt,
            claim_category=data.claim_category,
            evidence_status=data.evidence_status,
            supporting_evidence_ids=data.supporting_evidence_ids,
            contradicting_evidence_ids=data.contradicting_evidence_ids,
            related_entity_ids=data.related_entity_ids,
            actor_user_id=user_id,
        )
        return ResearchClaimDTO(**updated.__dict__)

    def delete_claim(self, claim_id: str, user_id: str) -> bool:
        c = self.repository.get_claim(claim_id)
        if not c:
            raise ResearchClaimNotFoundError(f"Claim '{claim_id}' not found.")
        inv = self.repository.get_investigation(c.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)
        return self.repository.delete_claim(claim_id, actor_user_id=user_id)

    def list_claims(self, investigation_id: str, user_id: str) -> List[ResearchClaimDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return [ResearchClaimDTO(**x.__dict__) for x in self.repository.list_claims_by_investigation(investigation_id)]

    # -----------------------------------------------------------------------
    # Source Reference & Library Operations
    # -----------------------------------------------------------------------
    def list_sources(
        self,
        source_type: Optional[ResearchSourceType] = None,
        entity_id: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[ResearchSourceReferenceDTO]:
        items = self.repository.list_sources(source_type=source_type, entity_id=entity_id, q=q)
        return [ResearchSourceReferenceDTO(**s.__dict__) for s in items]

    def link_source_to_investigation(
        self,
        investigation_id: str,
        data: LinkResearchSourceDTO,
        user_id: str,
    ) -> ResearchSourceReferenceDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        # 1. Existing catalog reference
        if data.source_reference_id:
            src = self.repository.get_source(data.source_reference_id)
            if not src:
                raise ResearchSourceNotFoundError(f"Source '{data.source_reference_id}' not found.")
            self.repository.link_source_to_investigation(investigation_id, src.source_reference_id, actor_user_id=user_id)
            return ResearchSourceReferenceDTO(**src.__dict__)

        # 2. Register candidate custom / external source with SSRF and scheme validation
        now = datetime.datetime.now(datetime.timezone.utc)
        safe_url = validate_and_sanitize_url(data.source_url) if data.source_url else None
        source_id = f"src-ext-{uuid.uuid4().hex[:10]}"

        new_source = ResearchSourceReference(
            source_reference_id=source_id,
            canonical_document_id=data.canonical_document_id,
            canonical_entity_id=data.canonical_entity_id,
            source_type=data.source_type or ResearchSourceType.AUTHORIZED_EXTERNAL_REFERENCE,
            provider_id=data.provider_id or "EXTERNAL_WEB",
            publisher_id=data.publisher_id,
            source_title=validate_analyst_text("source_title", data.source_title, max_length=500, required=True),
            source_url=safe_url,
            published_at=data.published_at,
            source_updated_at=now,
            first_observed_at=now,
            registered_at=now,
            reporting_period=data.reporting_period,
            source_revision=data.source_revision or "1",
            rights_policy=data.rights_policy or "USER_REGISTERED_EXTERNAL_REFERENCE",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"registered_by": user_id},
        )
        saved_source = self.repository.register_custom_source(new_source)
        self.repository.link_source_to_investigation(investigation_id, saved_source.source_reference_id, actor_user_id=user_id)
        return ResearchSourceReferenceDTO(**saved_source.__dict__)

    def unlink_source_from_investigation(
        self,
        investigation_id: str,
        source_reference_id: str,
        user_id: str,
    ) -> bool:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        return self.repository.unlink_source_from_investigation(investigation_id, source_reference_id, actor_user_id=user_id)

    def list_investigation_sources(self, investigation_id: str, user_id: str) -> List[ResearchSourceReferenceDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        sources = self.repository.list_sources_by_investigation(investigation_id)
        return [ResearchSourceReferenceDTO(**s.__dict__) for s in sources]

    # -----------------------------------------------------------------------
    # Evidence & Citation Operations
    # -----------------------------------------------------------------------
    def attach_evidence(
        self,
        investigation_id: str,
        data: Any,  # AttachResearchEvidenceDTO
        user_id: str,
    ) -> ResearchEvidenceDTO:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        clean_loc = validate_analyst_text("source_location_reference", data.source_location_reference, max_length=500, required=True)
        clean_excerpt = sanitize_markdown_text(data.allowed_excerpt or "", max_length=5000)

        ev = self.repository.attach_evidence(
            investigation_id=investigation_id,
            source_reference_id=data.source_reference_id,
            source_location_reference=clean_loc,
            evidence_type=data.evidence_type,
            source_location_type=data.source_location_type,
            page_number=data.page_number,
            section_name=data.section_name,
            allowed_excerpt=clean_excerpt,
            linked_claim_ids=data.linked_claim_ids,
            created_by=user_id,
        )
        src = self.repository.get_source(ev.source_reference_id)
        return ResearchEvidenceDTO(
            **ev.__dict__,
            source_title=src.source_title if src else None,
            publisher_id=src.publisher_id if src else None,
            source_url=src.source_url if src else None,
        )

    def remove_evidence(self, evidence_id: str, user_id: str) -> bool:
        ev = self.repository.get_evidence(evidence_id)
        if not ev:
            raise ResearchInvestigationNotFoundError(f"Evidence '{evidence_id}' not found.")
        inv = self.repository.get_investigation(ev.investigation_id)
        if inv:
            self._check_investigation_access(inv, user_id)
        return self.repository.remove_evidence(evidence_id, actor_user_id=user_id)

    def list_evidence(self, investigation_id: str, user_id: str) -> List[ResearchEvidenceDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        items = self.repository.list_evidence_by_investigation(investigation_id)
        res = []
        for e in items:
            src = self.repository.get_source(e.source_reference_id)
            res.append(
                ResearchEvidenceDTO(
                    **e.__dict__,
                    source_title=src.source_title if src else None,
                    publisher_id=src.publisher_id if src else None,
                    source_url=src.source_url if src else None,
                )
            )
        return res

    def list_citations(self, investigation_id: str, user_id: str) -> List[ResearchCitationDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        items = self.repository.list_citations_by_investigation(investigation_id)
        res = []
        for c in items:
            src = self.repository.get_source(c.source_reference_id)
            res.append(
                ResearchCitationDTO(
                    **c.__dict__,
                    source_title=src.source_title if src else None,
                    source_url=src.source_url if src else None,
                    publisher_id=src.publisher_id if src else None,
                )
            )
        return res

    # -----------------------------------------------------------------------
    # Activity & Overview Operations
    # -----------------------------------------------------------------------
    def list_activity(self, investigation_id: str, user_id: str) -> List[ResearchActivityDTO]:
        inv = self.repository.get_investigation(investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)
        items = self.repository.list_activity_by_investigation(investigation_id)
        return [ResearchActivityDTO(**a.__dict__) for a in items]

    def get_overview_summary(self, user_id: str) -> ResearchOverviewSummaryDTO:
        data = self.repository.get_overview_summary(user_id)
        return ResearchOverviewSummaryDTO(
            active_investigations_count=data["active_investigations_count"],
            draft_investigations_count=data["draft_investigations_count"],
            completed_investigations_count=data["completed_investigations_count"],
            archived_investigations_count=data["archived_investigations_count"],
            total_notes_count=data["total_notes_count"],
            total_sources_count=data["total_sources_count"],
            total_evidence_count=data["total_evidence_count"],
            total_analyses_count=data.get("total_analyses_count", 0),
            total_findings_count=data.get("total_findings_count", 0),
            total_evaluations_count=data.get("total_evaluations_count", 0),
            recent_investigations=[self._enrich_investigation_dto(x) for x in data["recent_investigations"]],
            recent_activities=[ResearchActivityDTO(**a.__dict__) for a in data["recent_activities"]],
        )

    # -----------------------------------------------------------------------
    # Stage 105 Research Source Discovery
    # -----------------------------------------------------------------------
    def discover_sources(
        self,
        query: ResearchSourceDiscoveryQueryDTO,
        user_id: str,
    ) -> ResearchSourceDiscoveryResponseDTO:
        """Execute multi-facet search across canonical filings, news, and economic releases."""
        clean_text = query.text_query.strip() if query.text_query else None
        hits, total, next_cursor, summary = self.repository.discover_sources(
            text_query=clean_text,
            entity_ids=query.entity_ids,
            instrument_ids=query.instrument_ids,
            source_type_ids=query.source_type_ids,
            publisher_ids=query.publisher_ids,
            filing_types=query.filing_types,
            reporting_period_range=query.reporting_period_range,
            date_from=query.date_from,
            date_to=query.date_to,
            availability_statuses=query.availability_statuses,
            search_mode=query.search_mode,
            sort_by=query.sort_by,
            limit=query.limit,
            cursor=query.cursor,
        )

        hit_dtos = [ResearchSearchHitDTO(**h.__dict__) for h in hits]
        return ResearchSourceDiscoveryResponseDTO(
            hits=hit_dtos,
            total_count=total,
            next_cursor=next_cursor,
            query_summary=summary,
        )

    def list_source_types(self) -> ResearchSourceTypeListResponseDTO:
        """Return taxonomic metadata and rights classifications for research sources."""
        items = self.repository.get_source_types()
        return ResearchSourceTypeListResponseDTO(
            items=[ResearchSourceTypeItemDTO(**it) for it in items],
            total_count=len(items),
        )

    def get_source(self, source_reference_id: str) -> ResearchSourceReferenceDTO:
        """Get canonical source metadata and rights classification."""
        src = self.repository.get_source(source_reference_id)
        if not src:
            raise ResearchSourceNotFoundError(f"Research source '{source_reference_id}' not found.")
        return ResearchSourceReferenceDTO(**src.__dict__)

    # -----------------------------------------------------------------------
    # Stage 105 Document Processing, Outline, Sections & Search
    # -----------------------------------------------------------------------
    def get_document_outline(self, document_id: str, user_id: str) -> ResearchDocumentOutlineDTO:
        doc = self.repository.get_document_metadata(document_id)
        if not doc:
            raise ResearchDocumentNotFoundError(f"Research document '{document_id}' not found.")

        sec_dtos = [ResearchDocumentSectionDTO(**s.__dict__) for s in doc.sections]
        return ResearchDocumentOutlineDTO(
            canonical_document_id=doc.document_id,
            source_reference_id=doc.source_reference_id,
            document_title=doc.title,
            sections=sec_dtos,
            total_sections=len(sec_dtos),
        )

    def get_document_processing_status(self, document_id: str, user_id: str) -> ResearchDocumentProcessingStatusDTO:
        proc = self.repository.get_document_processing_status(document_id)
        if not proc:
            raise ResearchDocumentNotFoundError(f"Processing record for document '{document_id}' not found.")
        return ResearchDocumentProcessingStatusDTO(**proc.__dict__)

    def list_document_sections(self, document_id: str, user_id: str) -> List[ResearchDocumentSectionDTO]:
        sections = self.repository.get_document_sections(document_id)
        return [ResearchDocumentSectionDTO(**s.__dict__) for s in sections]

    def get_document_section(self, document_id: str, section_id: str, user_id: str) -> ResearchDocumentSectionDTO:
        section = self.repository.get_document_section(document_id, section_id)
        return ResearchDocumentSectionDTO(**section.__dict__)

    def search_document(
        self,
        document_id: str,
        data: DocumentSearchRequestDTO,
        user_id: str,
    ) -> DocumentSearchResponseDTO:
        clean_q = data.query.strip()
        hits = self.repository.search_document(
            doc_id=document_id,
            query=clean_q,
            section_id=data.section_id,
            limit=data.limit,
        )
        return DocumentSearchResponseDTO(
            query=clean_q,
            total_matches=len(hits),
            hits=[DocumentSearchHitDTO(**h.__dict__) for h in hits],
        )

    def list_document_tables(self, document_id: str, user_id: str) -> ResearchDocumentTableListResponseDTO:
        tables = self.repository.get_document_tables(document_id)
        dtos = [ResearchDocumentTableDTO(**t.__dict__) for t in tables]
        return ResearchDocumentTableListResponseDTO(items=dtos, total_count=len(dtos))

    def get_document_table(self, document_id: str, table_id: str, user_id: str) -> ResearchDocumentTableDTO:
        table = self.repository.get_document_table(document_id, table_id)
        return ResearchDocumentTableDTO(**table.__dict__)

    # -----------------------------------------------------------------------
    # Stage 105 Evidence Candidates & Location Validation
    # -----------------------------------------------------------------------
    def list_evidence_candidates(
        self,
        investigation_id: Optional[str] = None,
        source_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 20,
    ) -> EvidenceCandidateListResponseDTO:
        items = self.repository.get_evidence_candidates(investigation_id=investigation_id, source_id=source_id, limit=limit)
        return EvidenceCandidateListResponseDTO(
            items=[ResearchEvidenceCandidateDTO(**c.__dict__) for c in items],
            total_count=len(items),
        )

    def resolve_evidence_location(
        self,
        data: ResolveEvidenceLocationRequestDTO,
        user_id: str,
    ) -> ResolveEvidenceLocationResponseDTO:
        is_valid, anchor, context, err = self.repository.resolve_evidence_location(
            source_reference_id=data.source_reference_id,
            location_type=data.location_type,
            location_reference=data.location_reference,
            page_number=data.page_number,
            section_name=data.section_name,
        )
        return ResolveEvidenceLocationResponseDTO(
            is_valid=is_valid,
            resolved_anchor=anchor,
            context_snippet=context,
            error_message=err,
        )

    def convert_evidence_candidate(
        self,
        data: ConvertEvidenceCandidateDTO,
        user_id: str,
    ) -> ResearchEvidenceDTO:
        inv = self.repository.get_investigation(data.investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{data.investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        ev = self.repository.convert_evidence_candidate(
            candidate_id=data.candidate_id,
            investigation_id=data.investigation_id,
            actor_user_id=user_id,
            claim_id=data.claim_id,
            relationship_type=data.relationship_type,
        )
        src = self.repository.get_source(ev.source_reference_id)
        return ResearchEvidenceDTO(
            **ev.__dict__,
            source_title=src.source_title if src else None,
            publisher_id=src.publisher_id if src else None,
            source_url=src.source_url if src else None,
        )

    # -----------------------------------------------------------------------
    # Stage 105 Two-Document & Financial Fact Comparison
    # -----------------------------------------------------------------------
    def compare_documents(
        self,
        data: DocumentComparisonRequestDTO,
        user_id: str,
    ) -> DocumentComparisonResultDTO:
        res = self.repository.compare_documents(
            left_doc_id=data.left_document_id,
            right_doc_id=data.right_document_id,
            mode=data.comparison_mode,
        )
        sec_dtos = [DocumentComparisonSectionDiffDTO(**sd.__dict__) for sd in res.section_diffs]
        fact_dtos = [FinancialFactComparisonDTO(**fd.__dict__) for fd in res.financial_fact_diffs]

        return DocumentComparisonResultDTO(
            comparison_id=res.comparison_id,
            left_document_id=res.left_document_id,
            right_document_id=res.right_document_id,
            left_title=res.left_title,
            right_title=res.right_title,
            left_period=res.left_period,
            right_period=res.right_period,
            total_added_lines=res.total_added_lines,
            total_removed_lines=res.total_removed_lines,
            section_diffs=sec_dtos,
            financial_fact_diffs=fact_dtos,
            compared_at=res.compared_at,
            comparison_mode=res.comparison_mode,
            compatibility_warnings=res.compatibility_warnings,
        )

    def compare_financial_facts(
        self,
        data: FinancialFactsCompareRequestDTO,
        user_id: str,
    ) -> FinancialFactsCompareResponseDTO:
        facts = self.repository.compare_financial_facts(
            entity_id=data.entity_id,
            left_period=data.left_period,
            right_period=data.right_period,
            concepts=data.concepts,
        )
        dtos = [FinancialFactComparisonDTO(**f.__dict__) for f in facts]
        return FinancialFactsCompareResponseDTO(
            entity_id=data.entity_id,
            left_period=data.left_period,
            right_period=data.right_period,
            fact_diffs=dtos,
            total_concepts_compared=len(dtos),
        )

    # -----------------------------------------------------------------------
    # Stage 106 Research Analysis Domain & Specifications
    # -----------------------------------------------------------------------
    def list_analysis_types(self) -> List[ResearchAnalysisTypeDTO]:
        types = self.repository.list_analysis_types()
        return [ResearchAnalysisTypeDTO(**t.__dict__) for t in types]

    def get_analysis_type(self, type_id: ResearchAnalysisType) -> ResearchAnalysisTypeDTO:
        t = self.repository.get_analysis_type(type_id)
        if not t:
            raise ResearchAnalysisTypeUnsupportedError(f"Analysis type '{type_id}' is not supported.")
        return ResearchAnalysisTypeDTO(**t.__dict__)

    def list_analyses(
        self,
        user_id: str,
        investigation_id: Optional[str] = None,
        analysis_type: Optional[ResearchAnalysisType] = None,
        subject_entity_id: Optional[str] = None,
        status: Optional[AnalysisExecutionStatus] = None,
    ) -> List[ResearchAnalysisDTO]:
        items = self.repository.list_analyses(
            user_id=user_id,
            investigation_id=investigation_id,
            analysis_type=analysis_type,
            subject_id=subject_entity_id,
            status=status,
        )
        return [self._enrich_analysis_dto(a) for a in items]

    def create_analysis(
        self,
        data: CreateResearchAnalysisDTO,
        user_id: str,
    ) -> ResearchAnalysisDTO:
        clean_title = validate_analyst_text("title", data.title, max_length=500, required=True)
        clean_desc = sanitize_markdown_text(data.description or "", max_length=50000)
        clean_obj = validate_analyst_text("research_objective", data.research_objective, max_length=5000, required=False)

        if data.investigation_id:
            inv = self.repository.get_investigation(data.investigation_id)
            if not inv:
                raise ResearchInvestigationNotFoundError(f"Investigation '{data.investigation_id}' not found.")
            self._check_investigation_access(inv, user_id)

        spec = ResearchAnalysisSpecification(
            analysis_type=data.specification.analysis_type,
            primary_entity_id=data.specification.primary_entity_id,
            secondary_entity_ids=data.specification.secondary_entity_ids,
            metric_ids=data.specification.metric_ids,
            time_range_start=data.specification.time_range_start,
            time_range_end=data.specification.time_range_end,
            frequency=data.specification.frequency,
            input_version_policy=data.specification.input_version_policy,
            outlier_policy=data.specification.outlier_policy,
            currency=data.specification.currency,
            as_known_at_cutoff=data.specification.as_known_at_cutoff,
            parameters=data.specification.parameters,
            methodology_version=data.specification.methodology_version,
        )

        analysis_id = f"an-{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc)
        analysis = ResearchAnalysis(
            analysis_id=analysis_id,
            investigation_id=data.investigation_id,
            owner_user_id=user_id,
            title=clean_title,
            description=clean_desc,
            analysis_type=data.analysis_type,
            research_objective=clean_obj,
            primary_subject_entity_id=data.primary_subject_entity_id,
            primary_subject_type=data.primary_subject_type,
            secondary_entity_ids=data.secondary_entity_ids,
            specification=spec,
            status=AnalysisExecutionStatus.CONFIGURED,
            current_revision=1,
            created_at=now,
            updated_at=now,
            linked_question_ids=data.linked_question_ids,
            linked_hypothesis_ids=data.linked_hypothesis_ids,
            latest_run_id=None,
            provenance={"created_by": user_id},
        )
        saved = self.repository.create_analysis(analysis)
        return self._enrich_analysis_dto(saved)

    def get_analysis(self, analysis_id: str, user_id: str) -> ResearchAnalysisDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)
        return self._enrich_analysis_dto(analysis)

    def update_analysis(
        self,
        analysis_id: str,
        data: UpdateResearchAnalysisDTO,
        user_id: str,
    ) -> ResearchAnalysisDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        clean_title = validate_analyst_text("title", data.title, max_length=500, required=False) if data.title else None
        clean_desc = sanitize_markdown_text(data.description, max_length=50000) if data.description is not None else None
        clean_obj = validate_analyst_text("research_objective", data.research_objective, max_length=5000, required=False) if data.research_objective else None

        spec = None
        if data.specification:
            spec = ResearchAnalysisSpecification(
                analysis_type=data.specification.analysis_type,
                primary_entity_id=data.specification.primary_entity_id,
                secondary_entity_ids=data.specification.secondary_entity_ids,
                metric_ids=data.specification.metric_ids,
                time_range_start=data.specification.time_range_start,
                time_range_end=data.specification.time_range_end,
                frequency=data.specification.frequency,
                input_version_policy=data.specification.input_version_policy,
                outlier_policy=data.specification.outlier_policy,
                currency=data.specification.currency,
                as_known_at_cutoff=data.specification.as_known_at_cutoff,
                parameters=data.specification.parameters,
                methodology_version=data.specification.methodology_version,
            )

        updated = self.repository.update_analysis(
            analysis_id=analysis_id,
            expected_revision=data.expected_revision,
            user_id=user_id,
            title=clean_title,
            description=clean_desc,
            research_objective=clean_obj,
            specification=spec,
            linked_questions=data.linked_question_ids,
            linked_hypotheses=data.linked_hypothesis_ids,
            status=data.status,
        )
        return self._enrich_analysis_dto(updated)

    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)
        return self.repository.delete_analysis(analysis_id, user_id)

    def duplicate_analysis(
        self,
        analysis_id: str,
        user_id: str,
        new_title: Optional[str] = None,
    ) -> ResearchAnalysisDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        duplicated = self.repository.duplicate_analysis(
            analysis_id=analysis_id,
            new_title=new_title,
            user_id=user_id,
        )
        return self._enrich_analysis_dto(duplicated)

    def validate_analysis_specification(
        self,
        data: ValidateAnalysisSpecificationRequestDTO,
        user_id: str,
    ) -> ValidateAnalysisSpecificationResponseDTO:
        spec = data.specification
        errors: List[str] = []
        warnings: List[str] = []

        supported_types = [t.type_id for t in get_supported_analysis_types()]
        if spec.analysis_type not in supported_types:
            errors.append(f"Analysis type '{spec.analysis_type}' is unrecognized or unsupported.")

        if not spec.primary_entity_id:
            errors.append("Analysis specification requires a primary_entity_id.")

        if spec.analysis_type in (
            ResearchAnalysisType.COMPANY_FINANCIAL_TREND,
            ResearchAnalysisType.COMPANY_RATIO_ANALYSIS,
            ResearchAnalysisType.CASH_FLOW_ANALYSIS,
            ResearchAnalysisType.CAPITAL_STRUCTURE_ANALYSIS,
        ):
            if not spec.metric_ids:
                warnings.append("No explicit metric_ids provided; defaulting to canonical operating_income.")
            if spec.primary_entity_id.upper() not in CANONICAL_COMPANY_FUNDAMENTALS:
                warnings.append(f"Subject '{spec.primary_entity_id}' not present in seeded Form 10-K fundamentals; synthetic/remote fallback may be required.")

        elif spec.analysis_type in (
            ResearchAnalysisType.PEER_BENCHMARKING,
            ResearchAnalysisType.INDUSTRY_COMPARISON,
        ):
            if not spec.secondary_entity_ids:
                warnings.append("No peer entities specified; will default to Stage 87 technology peer group.")

        elif spec.analysis_type in (
            ResearchAnalysisType.MACROECONOMIC_TIME_SERIES,
            ResearchAnalysisType.MULTI_INDICATOR_COMPARISON,
        ):
            if not spec.metric_ids:
                warnings.append("No macro indicator specified; defaulting to US_CPI.")

        available_periods = ["FY2020", "FY2021", "FY2022", "FY2023", "FY2024"]
        return ValidateAnalysisSpecificationResponseDTO(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            available_data_periods=available_periods,
            estimated_observation_count=len(available_periods),
        )

    def execute_analysis_run(
        self,
        analysis_id: str,
        user_id: str,
        input_policy: AnalysisInputPolicy = AnalysisInputPolicy.PINNED_SOURCE_VERSION,
        temporal_cutoff: Optional[str] = None,
    ) -> ResearchAnalysisRunDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        run_id = f"run-{uuid.uuid4().hex[:12]}"
        run, result = ResearchAnalysisEngine.execute(
            analysis_id=analysis_id,
            run_id=run_id,
            spec=analysis.specification,
            user_id=user_id,
        )
        if temporal_cutoff:
            result.as_known_at_cutoff = temporal_cutoff

        self.repository.save_analysis_run(run, result)
        return ResearchAnalysisRunDTO(**run.__dict__)

    def get_analysis_run(self, run_id: str, user_id: str) -> ResearchAnalysisRunDTO:
        run = self.repository.get_analysis_run(run_id)
        if not run:
            raise ResearchAnalysisRunNotFoundError(f"Analysis Run '{run_id}' not found.")
        analysis = self.repository.get_analysis(run.analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Associated analysis '{run.analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)
        return ResearchAnalysisRunDTO(**run.__dict__)

    def list_analysis_runs(self, analysis_id: str, user_id: str) -> List[ResearchAnalysisRunDTO]:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)
        runs = self.repository.list_analysis_runs(analysis_id)
        return [ResearchAnalysisRunDTO(**r.__dict__) for r in runs]

    def get_analysis_run_result(self, run_id: str, user_id: str) -> ResearchAnalysisResultDTO:
        run = self.repository.get_analysis_run(run_id)
        if not run:
            raise ResearchAnalysisRunNotFoundError(f"Analysis Run '{run_id}' not found.")
        analysis = self.repository.get_analysis(run.analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Associated analysis '{run.analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        result = self.repository.get_analysis_run_result(run_id)
        if not result:
            raise ResearchAnalysisNotFoundError(f"Result for run '{run_id}' not found.")

        rows_dtos = [AnalyticalObservationRowDTO(**r.__dict__) for r in result.observations]
        stats_dto = AnalyticalSummaryStatisticsDTO(**result.summary_statistics.__dict__) if result.summary_statistics else None

        return ResearchAnalysisResultDTO(
            analysis_id=result.analysis_id,
            run_id=result.run_id,
            analysis_type=result.analysis_type,
            execution_status=result.execution_status,
            methodology_version=result.methodology_version,
            primary_subject_id=result.primary_subject_id,
            metric_id=result.metric_id,
            unit=result.unit,
            observations=rows_dtos,
            summary_statistics=stats_dto,
            chart_series=result.chart_series,
            missingness_report=result.missingness_report,
            comparability_warnings=result.comparability_warnings,
            source_data_manifest=result.source_data_manifest,
            executed_at=result.executed_at,
            as_known_at_cutoff=result.as_known_at_cutoff,
            non_causal_qualification=result.non_causal_qualification,
        )

    def get_analysis_run_provenance(self, run_id: str, user_id: str) -> AnalysisProvenanceResponseDTO:
        run = self.repository.get_analysis_run(run_id)
        if not run:
            raise ResearchAnalysisRunNotFoundError(f"Analysis Run '{run_id}' not found.")
        analysis = self.repository.get_analysis(run.analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Associated analysis '{run.analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        result = self.repository.get_analysis_run_result(run_id)

        return AnalysisProvenanceResponseDTO(
            analysis_id=run.analysis_id,
            run_id=run.run_id,
            input_specification_hash=run.input_specification_hash,
            methodology_version=run.methodology_version,
            executed_at=run.completed_at or run.started_at,
            source_manifest=run.source_data_manifest,
            source_watermarks=run.source_revision_watermarks,
            formula_definitions={
                "percentage_growth": "((X_t - X_{t-1}) / |X_{t-1}|) * 100",
                "cagr": "(X_{end} / X_{start})^(1/n) - 1",
                "mean": "Sum(X) / N",
                "median": "Sorted middle value",
                "pearson_correlation": "Cov(X, Y) / (Std(X) * Std(Y))",
            },
            temporal_policy="AS_KNOWN_AT_CUTOFF" if result and result.as_known_at_cutoff else "POINT_IN_TIME_REPORTED",
            provenance_chain=[
                {"step": 1, "description": "Resolved canonical financial statements from SEC EDGAR Form 10-K Item 8"},
                {"step": 2, "description": "Applied zero-base and negative denominator protection for percentage deltas"},
                {"step": 3, "description": "Calculated cross-sectional or longitudinal statistics without fabricated observations"},
                {"step": 4, "description": "Generated immutable run record and source watermarks"},
            ],
        )

    def evaluate_hypothesis(
        self,
        hypothesis_id: str,
        data: EvaluateResearchHypothesisDTO,
        user_id: str,
    ) -> ResearchHypothesisEvaluationDTO:
        hyp = self.repository.get_hypothesis(hypothesis_id)
        if not hyp:
            raise ResearchHypothesisNotFoundError(f"Hypothesis '{hypothesis_id}' not found.")
        inv = self.repository.get_investigation(hyp.investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{hyp.investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        run = self.repository.get_analysis_run(data.analysis_run_id)
        if not run:
            raise ResearchAnalysisRunNotFoundError(f"Analysis Run '{data.analysis_run_id}' not found.")
        result = self.repository.get_analysis_run_result(data.analysis_run_id)
        if not result:
            raise ResearchAnalysisNotFoundError(f"Result for analysis run '{data.analysis_run_id}' not found.")

        criteria_domain = HypothesisTestCriteria(
            metric_id=data.criteria.metric_id,
            operator=data.criteria.operator,
            threshold_value=data.criteria.threshold_value,
            comparison_target=data.criteria.comparison_target,
            required_periods_count=data.criteria.required_periods_count,
            allow_missing=data.criteria.allow_missing,
        )

        eval_id = f"eval-{uuid.uuid4().hex[:12]}"
        evaluation = ResearchAnalysisEngine.evaluate_hypothesis(
            evaluation_id=eval_id,
            hypothesis_id=hypothesis_id,
            run=run,
            result=result,
            criteria=criteria_domain,
            user_id=user_id,
        )
        self.repository.save_hypothesis_evaluation(evaluation)

        criteria_dto = HypothesisTestCriteriaDTO(
            metric_id=evaluation.criteria.metric_id,
            operator=evaluation.criteria.operator,
            threshold_value=evaluation.criteria.threshold_value,
            comparison_target=evaluation.criteria.comparison_target,
            required_periods_count=evaluation.criteria.required_periods_count,
            allow_missing=evaluation.criteria.allow_missing,
        )

        return ResearchHypothesisEvaluationDTO(
            evaluation_id=evaluation.evaluation_id,
            hypothesis_id=evaluation.hypothesis_id,
            analysis_run_id=evaluation.analysis_run_id,
            author_user_id=evaluation.author_user_id,
            criteria=criteria_dto,
            eligible_universe=evaluation.eligible_universe,
            observation_count=evaluation.observation_count,
            result_status=evaluation.result_status,
            supporting_evidence_ids=evaluation.supporting_evidence_ids,
            contradicting_evidence_ids=evaluation.contradicting_evidence_ids,
            evaluation_summary=evaluation.evaluation_summary,
            methodology_limitations=evaluation.methodology_limitations,
            analyst_review_state=evaluation.analyst_review_state,
            created_at=evaluation.created_at,
        )

    def list_hypothesis_evaluations(
        self,
        hypothesis_id: str,
        user_id: str,
    ) -> List[ResearchHypothesisEvaluationDTO]:
        hyp = self.repository.get_hypothesis(hypothesis_id)
        if not hyp:
            raise ResearchHypothesisNotFoundError(f"Hypothesis '{hypothesis_id}' not found.")
        inv = self.repository.get_investigation(hyp.investigation_id)
        if not inv:
            raise ResearchInvestigationNotFoundError(f"Investigation '{hyp.investigation_id}' not found.")
        self._check_investigation_access(inv, user_id)

        evals = self.repository.list_hypothesis_evaluations(hypothesis_id)
        res = []
        for e in evals:
            c_dto = HypothesisTestCriteriaDTO(
                metric_id=e.criteria.metric_id,
                operator=e.criteria.operator,
                threshold_value=e.criteria.threshold_value,
                comparison_target=e.criteria.comparison_target,
                required_periods_count=e.criteria.required_periods_count,
                allow_missing=e.criteria.allow_missing,
            )
            res.append(
                ResearchHypothesisEvaluationDTO(
                    evaluation_id=e.evaluation_id,
                    hypothesis_id=e.hypothesis_id,
                    analysis_run_id=e.analysis_run_id,
                    author_user_id=e.author_user_id,
                    criteria=c_dto,
                    eligible_universe=e.eligible_universe,
                    observation_count=e.observation_count,
                    result_status=e.result_status,
                    supporting_evidence_ids=e.supporting_evidence_ids,
                    contradicting_evidence_ids=e.contradicting_evidence_ids,
                    evaluation_summary=e.evaluation_summary,
                    methodology_limitations=e.methodology_limitations,
                    analyst_review_state=e.analyst_review_state,
                    created_at=e.created_at,
                )
            )
        return res

    def get_hypothesis_evaluation(
        self,
        evaluation_id: str,
        user_id: str,
    ) -> ResearchHypothesisEvaluationDTO:
        e = self.repository.get_hypothesis_evaluation(evaluation_id)
        if not e:
            raise ResearchHypothesisEvaluationNotFoundError(f"Evaluation '{evaluation_id}' not found.")
        hyp = self.repository.get_hypothesis(e.hypothesis_id)
        if hyp:
            inv = self.repository.get_investigation(hyp.investigation_id)
            if inv:
                self._check_investigation_access(inv, user_id)

        c_dto = HypothesisTestCriteriaDTO(
            metric_id=e.criteria.metric_id,
            operator=e.criteria.operator,
            threshold_value=e.criteria.threshold_value,
            comparison_target=e.criteria.comparison_target,
            required_periods_count=e.criteria.required_periods_count,
            allow_missing=e.criteria.allow_missing,
        )
        return ResearchHypothesisEvaluationDTO(
            evaluation_id=e.evaluation_id,
            hypothesis_id=e.hypothesis_id,
            analysis_run_id=e.analysis_run_id,
            author_user_id=e.author_user_id,
            criteria=c_dto,
            eligible_universe=e.eligible_universe,
            observation_count=e.observation_count,
            result_status=e.result_status,
            supporting_evidence_ids=e.supporting_evidence_ids,
            contradicting_evidence_ids=e.contradicting_evidence_ids,
            evaluation_summary=e.evaluation_summary,
            methodology_limitations=e.methodology_limitations,
            analyst_review_state=e.analyst_review_state,
            created_at=e.created_at,
        )

    def create_finding(
        self,
        analysis_id: str,
        data: CreateResearchFindingDTO,
        user_id: str,
    ) -> ResearchFindingDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        clean_stmt = validate_analyst_text("statement", data.statement, max_length=5000, required=True)
        clean_method = sanitize_markdown_text(data.methodology_description or "", max_length=5000)

        finding_id = f"find-{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc)
        finding = ResearchFinding(
            finding_id=finding_id,
            investigation_id=data.investigation_id or analysis.investigation_id,
            analysis_id=analysis_id,
            analysis_run_id=data.analysis_run_id,
            author_user_id=user_id,
            finding_type=data.finding_type,
            statement=clean_stmt,
            methodology_description=clean_method,
            supporting_evidence_ids=data.supporting_evidence_ids,
            contradicting_evidence_ids=data.contradicting_evidence_ids,
            calculated_result_references=data.calculated_result_references,
            limitations=data.limitations,
            review_status=ResearchFindingReviewStatus.DRAFT,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        saved = self.repository.create_finding(finding)
        return ResearchFindingDTO(**saved.__dict__)

    def get_finding(self, finding_id: str, user_id: str) -> ResearchFindingDTO:
        f = self.repository.get_finding(finding_id)
        if not f:
            raise ResearchFindingNotFoundError(f"Research Finding '{finding_id}' not found.")
        self._check_finding_access(f, user_id)
        return ResearchFindingDTO(**f.__dict__)

    def update_finding(
        self,
        finding_id: str,
        data: UpdateResearchFindingDTO,
        user_id: str,
    ) -> ResearchFindingDTO:
        f = self.repository.get_finding(finding_id)
        if not f:
            raise ResearchFindingNotFoundError(f"Research Finding '{finding_id}' not found.")
        self._check_finding_access(f, user_id)

        clean_stmt = validate_analyst_text("statement", data.statement, max_length=5000, required=False) if data.statement else None
        clean_method = sanitize_markdown_text(data.methodology_description, max_length=5000) if data.methodology_description is not None else None

        updated = self.repository.update_finding(
            finding_id=finding_id,
            expected_revision=data.expected_revision,
            user_id=user_id,
            statement=clean_stmt,
            finding_type=data.finding_type,
            methodology_description=clean_method,
            supporting_evidence_ids=data.supporting_evidence_ids,
            contradicting_evidence_ids=data.contradicting_evidence_ids,
            limitations=data.limitations,
            review_status=data.review_status,
        )
        return ResearchFindingDTO(**updated.__dict__)

    def delete_finding(self, finding_id: str, user_id: str) -> bool:
        f = self.repository.get_finding(finding_id)
        if not f:
            raise ResearchFindingNotFoundError(f"Research Finding '{finding_id}' not found.")
        self._check_finding_access(f, user_id)
        return self.repository.delete_finding(finding_id, user_id)

    def list_findings(
        self,
        user_id: str,
        analysis_id: Optional[str] = None,
        investigation_id: Optional[str] = None,
    ) -> List[ResearchFindingDTO]:
        items = self.repository.list_findings(investigation_id=investigation_id, analysis_id=analysis_id)
        user_items = [f for f in items if f.author_user_id == user_id or f.author_user_id == "default-user"]
        return [ResearchFindingDTO(**f.__dict__) for f in user_items]

    def create_assumption(
        self,
        analysis_id: str,
        data: CreateResearchAssumptionDTO,
        user_id: str,
    ) -> ResearchAssumptionDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        clean_label = validate_analyst_text("label", data.label, max_length=200, required=True)
        clean_note = sanitize_markdown_text(data.analyst_note or "", max_length=2000)

        assump_id = f"assump-{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc)
        assump = ResearchAnalysisAssumption(
            assumption_id=assump_id,
            analysis_id=analysis_id,
            label=clean_label,
            parameter_id=data.parameter_id,
            value=data.value,
            unit=data.unit,
            source_type=data.source_type,
            source_reference_id=data.source_reference_id,
            analyst_note=clean_note,
            created_at=now,
        )
        saved = self.repository.create_assumption(assump)
        return ResearchAssumptionDTO(**saved.__dict__)

    def list_assumptions(self, analysis_id: str, user_id: str) -> List[ResearchAssumptionDTO]:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)
        items = self.repository.list_assumptions(analysis_id)
        return [ResearchAssumptionDTO(**a.__dict__) for a in items]

    def delete_assumption(self, assumption_id: str, user_id: str) -> bool:
        assump = self.repository.get_assumption(assumption_id)
        if not assump:
            raise ResearchAssumptionNotFoundError(f"Assumption '{assumption_id}' not found.")
        analysis = self.repository.get_analysis(assump.analysis_id)
        if analysis:
            self._check_analysis_access(analysis, user_id)
        return self.repository.delete_assumption(assumption_id)

    def execute_sensitivity_scenario(
        self,
        analysis_id: str,
        data: ExecuteSensitivityScenarioDTO,
        user_id: str,
    ) -> ResearchSensitivityResultDTO:
        analysis = self.repository.get_analysis(analysis_id)
        if not analysis:
            raise ResearchAnalysisNotFoundError(f"Research Analysis '{analysis_id}' not found.")
        self._check_analysis_access(analysis, user_id)

        result_dict = ResearchAnalysisEngine.execute_sensitivity(
            base_value=data.base_metric_value,
            growth_rates=data.growth_rates,
            margin_rates=data.margin_rates,
            metric_name=data.metric_name,
            unit=data.unit,
        )

        scenario_id = f"scen-{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc)
        scenario = ResearchScenario(
            scenario_id=scenario_id,
            analysis_id=analysis_id,
            name=f"Sensitivity on {data.metric_name}",
            scenario_type=ScenarioType.BASE_ASSUMPTION,
            parameter_values={"base_value": data.base_metric_value},
            calculated_outputs={"sample_output": result_dict["scenario_matrix"][0][0] if result_dict["scenario_matrix"] else 0.0},
            created_at=now,
            is_non_predictive_illustrative=True,
        )
        self.repository.save_scenario(scenario)

        return ResearchSensitivityResultDTO(**result_dict)

    # =======================================================================
    # Stage 107: Report Studio, Investment Theses & Exports
    # =======================================================================

    # --- Templates ---
    def list_report_templates(self) -> ResearchReportTemplateListResponseDTO:
        templates = list_report_templates()
        dto_list = [
            ResearchReportTemplateDTO(
                template_id=t.template_id,
                template_version=t.template_version,
                report_type=t.report_type,
                title=t.title,
                description=t.description,
                default_sections=t.default_sections,
                required_sections=t.required_sections,
                citation_style=t.citation_style,
                is_active=t.is_active,
            )
            for t in templates
        ]
        return ResearchReportTemplateListResponseDTO(templates=dto_list, total_count=len(dto_list))

    def get_report_template(self, template_id: str) -> ResearchReportTemplateDTO:
        t = get_report_template(template_id)
        if not t:
            raise ResearchReportTemplateUnavailableError(f"Template '{template_id}' is not available.")
        return ResearchReportTemplateDTO(
            template_id=t.template_id,
            template_version=t.template_version,
            report_type=t.report_type,
            title=t.title,
            description=t.description,
            default_sections=t.default_sections,
            required_sections=t.required_sections,
            citation_style=t.citation_style,
            is_active=t.is_active,
        )

    # --- Reports CRUD ---
    def list_reports(
        self,
        user_id: str,
        investigation_id: Optional[str] = None,
        report_type: Optional[ResearchReportType] = None,
        status: Optional[ReportLifecycleStatus] = None,
        subject_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ResearchReportListResponse:
        reports, total = self.repository.list_reports(
            user_id=user_id,
            investigation_id=investigation_id,
            report_type=report_type,
            status=status,
            subject_id=subject_id,
            limit=limit,
            offset=offset,
        )
        dtos = []
        for r in reports:
            secs = self.repository.list_report_sections(r.report_id)
            dtos.append(
                ResearchReportResponse(
                    report_id=r.report_id,
                    owner_user_id=r.owner_user_id,
                    investigation_id=r.investigation_id,
                    report_type=r.report_type,
                    title=r.title,
                    subtitle=r.subtitle,
                    abstract=r.abstract,
                    primary_subject_id=r.primary_subject_id,
                    primary_subject_type=r.primary_subject_type,
                    secondary_subject_ids=r.secondary_subject_ids,
                    report_as_of=r.report_as_of,
                    research_cutoff=r.research_cutoff,
                    template_id=r.template_id,
                    status=r.status,
                    current_revision=r.current_revision,
                    snapshot_policy=r.snapshot_policy,
                    section_count=len(secs),
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )
        return ResearchReportListResponse(reports=dtos, total_count=total)

    def create_report(
        self,
        data: CreateResearchReportRequest,
        user_id: str,
    ) -> ResearchReportDetailResponse:
        clean_title = sanitize_markdown_text(data.title.strip())
        clean_subtitle = sanitize_markdown_text(data.subtitle.strip()) if data.subtitle else None
        clean_abstract = sanitize_markdown_text(data.abstract.strip()) if data.abstract else None

        now = datetime.datetime.now(datetime.timezone.utc)
        as_of = data.report_as_of or now.date()
        cutoff = data.research_cutoff or now

        report_id = f"rep-{uuid.uuid4().hex[:12]}"

        # Initialize sections from template if selected
        initial_sections: List[ResearchReportSection] = []
        if data.template_id:
            tpl = get_report_template(data.template_id)
            if tpl:
                for idx, sec_def in enumerate(tpl.default_sections, start=1):
                    sec_type = ReportSectionType(sec_def.get("section_type", ReportSectionType.CUSTOM.value))
                    initial_sections.append(
                        ResearchReportSection(
                            section_id=f"sec-{uuid.uuid4().hex[:10]}",
                            report_id=report_id,
                            parent_section_id=None,
                            order_index=idx,
                            section_type=sec_type,
                            heading=sec_def.get("heading", f"Section {idx}"),
                            content_blocks=sec_def.get("content_blocks", []),
                            revision=1,
                            created_at=now,
                            updated_at=now,
                        )
                    )

        report = ResearchReport(
            report_id=report_id,
            owner_user_id=user_id,
            investigation_id=data.investigation_id,
            report_type=data.report_type,
            title=clean_title,
            subtitle=clean_subtitle,
            abstract=clean_abstract,
            primary_subject_id=data.primary_subject_id,
            primary_subject_type=data.primary_subject_type or ("COMPANY" if data.primary_subject_id else None),
            secondary_subject_ids=data.secondary_subject_ids,
            report_as_of=as_of,
            research_cutoff=cutoff,
            template_id=data.template_id,
            current_revision=1,
            status=ReportLifecycleStatus.DRAFT,
            snapshot_policy=data.snapshot_policy,
            source_manifest=[],
            evidence_manifest=[],
            analysis_run_manifest=[],
            citation_references=[],
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

        saved = self.repository.create_report(user_id, report, initial_sections)
        return self._build_report_detail_response(saved)

    def get_report(self, report_id: str, user_id: str) -> ResearchReportDetailResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied to report.")
        return self._build_report_detail_response(rep)

    def update_report(
        self,
        report_id: str,
        data: UpdateResearchReportRequest,
        user_id: str,
    ) -> ResearchReportDetailResponse:
        updates: Dict[str, Any] = {}
        if data.title is not None:
            updates["title"] = sanitize_markdown_text(data.title.strip())
        if data.subtitle is not None:
            updates["subtitle"] = sanitize_markdown_text(data.subtitle.strip())
        if data.abstract is not None:
            updates["abstract"] = sanitize_markdown_text(data.abstract.strip())
        if data.primary_subject_id is not None:
            updates["primary_subject_id"] = data.primary_subject_id
        if data.secondary_subject_ids is not None:
            updates["secondary_subject_ids"] = data.secondary_subject_ids
        if data.report_as_of is not None:
            updates["report_as_of"] = data.report_as_of
        if data.research_cutoff is not None:
            updates["research_cutoff"] = data.research_cutoff
        if data.snapshot_policy is not None:
            updates["snapshot_policy"] = data.snapshot_policy
        if data.status is not None:
            updates["status"] = data.status

        updated = self.repository.update_report(
            user_id=user_id,
            report_id=report_id,
            expected_revision=data.expected_revision,
            updates=updates,
        )
        return self._build_report_detail_response(updated)

    def finalize_report(
        self,
        report_id: str,
        data: FinalizeReportRequest,
        user_id: str,
    ) -> ResearchReportDetailResponse:
        finalized = self.repository.finalize_report(
            user_id=user_id,
            report_id=report_id,
            expected_revision=data.expected_revision,
            change_summary=data.change_summary,
        )
        return self._build_report_detail_response(finalized)

    def delete_report(self, report_id: str, user_id: str) -> bool:
        return self.repository.delete_report(user_id=user_id, report_id=report_id)

    # --- Report Sections ---
    def list_report_sections(self, report_id: str, user_id: str) -> List[ResearchReportSectionDTO]:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied to report sections.")
        secs = self.repository.list_report_sections(report_id)
        return [self._map_section_dto(s) for s in secs]

    def create_report_section(
        self,
        report_id: str,
        data: CreateReportSectionRequest,
        user_id: str,
    ) -> ResearchReportSectionDTO:
        clean_heading = sanitize_markdown_text(data.heading.strip())
        now = datetime.datetime.now(datetime.timezone.utc)
        sec = ResearchReportSection(
            section_id=f"sec-{uuid.uuid4().hex[:10]}",
            report_id=report_id,
            parent_section_id=data.parent_section_id,
            order_index=data.order_index or 0,
            section_type=data.section_type,
            heading=clean_heading,
            content_blocks=data.content_blocks,
            revision=1,
            created_at=now,
            updated_at=now,
        )
        saved = self.repository.create_report_section(user_id, sec)
        return self._map_section_dto(saved)

    def update_report_section(
        self,
        report_id: str,
        section_id: str,
        data: UpdateReportSectionRequest,
        user_id: str,
    ) -> ResearchReportSectionDTO:
        clean_heading = sanitize_markdown_text(data.heading.strip()) if data.heading else None
        updated = self.repository.update_report_section(
            user_id=user_id,
            section_id=section_id,
            expected_revision=data.expected_revision,
            heading=clean_heading,
            section_type=data.section_type,
            content_blocks=data.content_blocks,
        )
        return self._map_section_dto(updated)

    def delete_report_section(
        self,
        report_id: str,
        section_id: str,
        user_id: str,
    ) -> bool:
        return self.repository.delete_report_section(user_id=user_id, section_id=section_id)

    def reorder_report_sections(
        self,
        report_id: str,
        data: ReorderReportSectionsRequest,
        user_id: str,
    ) -> List[ResearchReportSectionDTO]:
        reordered = self.repository.reorder_report_sections(
            user_id=user_id,
            report_id=report_id,
            section_ids=data.section_ids,
        )
        return [self._map_section_dto(s) for s in reordered]

    # --- Report Revisions ---
    def list_report_revisions(
        self,
        report_id: str,
        user_id: str,
    ) -> ResearchReportRevisionListResponseDTO:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied.")
        revs = self.repository.list_report_revisions(report_id)
        dtos = [
            ResearchReportRevisionDTO(
                revision_id=r.revision_id,
                report_id=r.report_id,
                revision_number=r.revision_number,
                parent_revision_id=r.parent_revision_id,
                author_user_id=r.author_user_id,
                revision_status=r.revision_status,
                change_summary=r.change_summary,
                content_hash=r.content_hash,
                created_at=r.created_at,
            )
            for r in revs
        ]
        return ResearchReportRevisionListResponseDTO(revisions=dtos, total_count=len(dtos))

    def compare_report_revisions(
        self,
        report_id: str,
        data: CompareReportRevisionsRequestDTO,
        user_id: str,
    ) -> CompareReportRevisionsResponseDTO:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied.")
        diff = self.repository.compare_report_revisions(
            report_id=report_id,
            base_rev=data.base_revision_number,
            target_rev=data.target_revision_number,
        )
        return CompareReportRevisionsResponseDTO(**diff)

    # --- Verification ---
    def verify_report(
        self,
        report_id: str,
        data: VerifyReportRequest,
        user_id: str,
    ) -> ResearchReportVerificationResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied.")
        if data.expected_revision and rep.current_revision != data.expected_revision:
            raise ResearchReportRevisionConflictError(
                f"Report revision {rep.current_revision} != expected {data.expected_revision}."
            )

        sections = self.repository.list_report_sections(report_id)
        verification = verify_research_report(rep, sections, verified_by_user_id=user_id)
        saved = self.repository.record_verification(verification)

        return ResearchReportVerificationResponse(
            verification_id=saved.verification_id,
            report_id=saved.report_id,
            revision_number=saved.revision_number,
            checked_at=saved.checked_at,
            is_valid=saved.is_valid,
            blocking_issues_count=saved.blocking_issues_count,
            warnings_count=saved.warnings_count,
            info_count=saved.info_count,
            issues=saved.issues,
            citation_coverage_pct=saved.citation_coverage_pct,
            verified_by_user_id=saved.verified_by_user_id,
        )

    def get_latest_verification(
        self,
        report_id: str,
        user_id: str,
    ) -> Optional[ResearchReportVerificationResponse]:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied.")
        v = self.repository.get_latest_verification(report_id)
        if not v:
            return None
        return ResearchReportVerificationResponse(
            verification_id=v.verification_id,
            report_id=v.report_id,
            revision_number=v.revision_number,
            checked_at=v.checked_at,
            is_valid=v.is_valid,
            blocking_issues_count=v.blocking_issues_count,
            warnings_count=v.warnings_count,
            info_count=v.info_count,
            issues=v.issues,
            citation_coverage_pct=v.citation_coverage_pct,
            verified_by_user_id=v.verified_by_user_id,
        )

    # --- Exports ---
    def create_report_export(
        self,
        report_id: str,
        data: CreateReportExportRequest,
        user_id: str,
    ) -> ResearchReportExportResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied.")
        if data.expected_revision and rep.current_revision != data.expected_revision:
            raise ResearchReportRevisionConflictError(
                f"Report revision {rep.current_revision} != expected {data.expected_revision}."
            )

        sections = self.repository.list_report_sections(report_id)

        now = datetime.datetime.now(datetime.timezone.utc)
        if data.format == ExportFormat.PDF:
            artifact_bytes, page_count = render_report_pdf(rep, sections, author_name=data.author_name)
        elif data.format == ExportFormat.DOCX:
            artifact_bytes, page_count = render_report_docx(rep, sections, author_name=data.author_name)
        else:
            raise ValueError(f"Unsupported export format '{data.format}'.")

        import hashlib
        content_hash = f"sha256:{hashlib.sha256(artifact_bytes).hexdigest()}"
        export_id = f"exp-{uuid.uuid4().hex[:12]}"
        download_url = f"/api/v1/research/report-exports/{export_id}/download"

        export = ResearchReportExport(
            export_id=export_id,
            report_id=report_id,
            revision_number=rep.current_revision,
            owner_user_id=user_id,
            format=data.format,
            export_status=ExportStatus.COMPLETED,
            download_url=download_url,
            file_size_bytes=len(artifact_bytes),
            page_count=page_count,
            content_hash=content_hash,
            created_at=now,
            started_at=now,
            completed_at=now,
            expiry_at=now + datetime.timedelta(days=7),
            error_message=None,
        )
        saved = self.repository.create_export(export, artifact_bytes=artifact_bytes)
        return self._map_export_dto(saved)

    def get_report_export(self, export_id: str, user_id: str) -> ResearchReportExportResponse:
        exp = self.repository.get_export(export_id)
        if not exp:
            raise ResearchReportExportNotFoundError(f"Export job '{export_id}' not found.")
        if exp.owner_user_id != user_id:
            raise ResearchReportExportAccessDeniedError("Access denied to export.")
        return self._map_export_dto(exp)

    def list_report_exports(self, report_id: str, user_id: str) -> ResearchReportExportListResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        if rep.owner_user_id != user_id:
            raise ResearchReportAccessDeniedError("Access denied.")
        exps = self.repository.list_exports(report_id)
        dtos = [self._map_export_dto(e) for e in exps]
        return ResearchReportExportListResponse(exports=dtos, total_count=len(dtos))

    def download_export_file(self, export_id: str, user_id: str) -> Tuple[bytes, str, str]:
        exp = self.repository.get_export(export_id)
        if not exp:
            raise ResearchReportExportNotFoundError(f"Export job '{export_id}' not found.")
        if exp.owner_user_id != user_id:
            raise ResearchReportExportAccessDeniedError("Access denied to download file.")

        content = self.repository.get_export_bytes(export_id)
        if not content:
            raise ResearchReportExportNotFoundError("Export binary file artifact not found.")

        media_type = (
            "application/pdf"
            if exp.format == ExportFormat.PDF
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        ext = "pdf" if exp.format == ExportFormat.PDF else "docx"
        filename = f"atlas_report_{exp.report_id}_rev{exp.revision_number}.{ext}"
        return content, media_type, filename

    # --- Investment Theses ---
    def list_theses(
        self,
        user_id: str,
        investigation_id: Optional[str] = None,
        report_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ResearchThesisResponse]:
        theses, _ = self.repository.list_theses(
            user_id=user_id,
            investigation_id=investigation_id,
            report_id=report_id,
            subject_id=subject_id,
            limit=limit,
            offset=offset,
        )
        return [self._map_thesis_dto(t) for t in theses]

    def create_thesis(
        self,
        data: CreateResearchThesisRequest,
        user_id: str,
    ) -> ResearchThesisDetailResponse:
        clean_stmt = sanitize_markdown_text(data.thesis_statement.strip())
        now = datetime.datetime.now(datetime.timezone.utc)
        the_id = f"the-{uuid.uuid4().hex[:10]}"

        thesis = ResearchInvestmentThesis(
            thesis_id=the_id,
            investigation_id=data.investigation_id,
            report_id=data.report_id,
            owner_user_id=user_id,
            primary_subject_id=data.primary_subject_id,
            primary_subject_type=data.primary_subject_type or ("COMPANY" if data.primary_subject_id else None),
            thesis_statement=clean_stmt,
            time_horizon=data.time_horizon,
            status=ThesisLifecycleStatus.DRAFT,
            current_revision=1,
            bull_case_summary=data.bull_case_summary,
            bear_case_summary=data.bear_case_summary,
            base_case_summary=data.base_case_summary,
            assumptions_summary=data.assumptions_summary,
            risks_summary=data.risks_summary,
            catalysts_summary=data.catalysts_summary,
            created_at=now,
            updated_at=now,
        )
        saved = self.repository.create_thesis(user_id, thesis)
        return self._build_thesis_detail_response(saved)

    def get_thesis(self, thesis_id: str, user_id: str) -> ResearchThesisDetailResponse:
        the = self.repository.get_thesis(thesis_id)
        if not the:
            raise ResearchInvestmentThesisNotFoundError(f"Thesis '{thesis_id}' not found.")
        if the.owner_user_id != user_id:
            raise ResearchInvestmentThesisAccessDeniedError("Access denied to thesis.")
        return self._build_thesis_detail_response(the)

    def update_thesis(
        self,
        thesis_id: str,
        data: UpdateResearchThesisRequest,
        user_id: str,
    ) -> ResearchThesisDetailResponse:
        updates: Dict[str, Any] = {}
        if data.thesis_statement is not None:
            updates["thesis_statement"] = sanitize_markdown_text(data.thesis_statement.strip())
        if data.time_horizon is not None:
            updates["time_horizon"] = data.time_horizon
        if data.status is not None:
            updates["status"] = data.status
        if data.bull_case_summary is not None:
            updates["bull_case_summary"] = data.bull_case_summary
        if data.bear_case_summary is not None:
            updates["bear_case_summary"] = data.bear_case_summary
        if data.base_case_summary is not None:
            updates["base_case_summary"] = data.base_case_summary
        if data.assumptions_summary is not None:
            updates["assumptions_summary"] = data.assumptions_summary
        if data.risks_summary is not None:
            updates["risks_summary"] = data.risks_summary
        if data.catalysts_summary is not None:
            updates["catalysts_summary"] = data.catalysts_summary

        updated = self.repository.update_thesis(
            user_id=user_id,
            thesis_id=thesis_id,
            expected_revision=data.expected_revision,
            updates=updates,
        )
        return self._build_thesis_detail_response(updated)

    def delete_thesis(self, thesis_id: str, user_id: str) -> bool:
        return self.repository.delete_thesis(user_id=user_id, thesis_id=thesis_id)

    def create_thesis_argument(
        self,
        thesis_id: str,
        data: CreateThesisArgumentRequest,
        user_id: str,
    ) -> ResearchThesisArgumentDTO:
        clean_stmt = sanitize_markdown_text(data.statement.strip())
        now = datetime.datetime.now(datetime.timezone.utc)
        arg = ResearchThesisArgument(
            argument_id=f"arg-{uuid.uuid4().hex[:10]}",
            thesis_id=thesis_id,
            argument_type=data.argument_type,
            statement=clean_stmt,
            claim_ids=data.claim_ids,
            evidence_ids=data.evidence_ids,
            analysis_run_ids=data.analysis_run_ids,
            finding_ids=data.finding_ids,
            limitations=data.limitations,
            revision=1,
            created_at=now,
        )
        saved = self.repository.create_thesis_argument(user_id, arg)
        return self._map_argument_dto(saved)

    def delete_thesis_argument(
        self,
        thesis_id: str,
        argument_id: str,
        user_id: str,
    ) -> bool:
        return self.repository.delete_thesis_argument(user_id=user_id, argument_id=argument_id)

    # --- Helper Mapping Methods ---
    def _build_report_detail_response(self, r: ResearchReport) -> ResearchReportDetailResponse:
        secs = self.repository.list_report_sections(r.report_id)
        sec_dtos = [self._map_section_dto(s) for s in secs]
        return ResearchReportDetailResponse(
            report_id=r.report_id,
            owner_user_id=r.owner_user_id,
            investigation_id=r.investigation_id,
            report_type=r.report_type,
            title=r.title,
            subtitle=r.subtitle,
            abstract=r.abstract,
            primary_subject_id=r.primary_subject_id,
            primary_subject_type=r.primary_subject_type,
            secondary_subject_ids=r.secondary_subject_ids,
            report_as_of=r.report_as_of,
            research_cutoff=r.research_cutoff,
            template_id=r.template_id,
            status=r.status,
            current_revision=r.current_revision,
            snapshot_policy=r.snapshot_policy,
            section_count=len(secs),
            created_at=r.created_at,
            updated_at=r.updated_at,
            sections=sec_dtos,
            source_manifest=r.source_manifest,
            evidence_manifest=r.evidence_manifest,
            analysis_run_manifest=r.analysis_run_manifest,
        )

    def _map_section_dto(self, s: ResearchReportSection) -> ResearchReportSectionDTO:
        return ResearchReportSectionDTO(
            section_id=s.section_id,
            report_id=s.report_id,
            parent_section_id=s.parent_section_id,
            order_index=s.order_index,
            section_type=s.section_type,
            heading=s.heading,
            content_blocks=s.content_blocks,
            revision=s.revision,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )

    def _map_export_dto(self, e: ResearchReportExport) -> ResearchReportExportResponse:
        return ResearchReportExportResponse(
            export_id=e.export_id,
            report_id=e.report_id,
            revision_number=e.revision_number,
            owner_user_id=e.owner_user_id,
            format=e.format,
            export_status=e.export_status,
            download_url=e.download_url,
            file_size_bytes=e.file_size_bytes,
            page_count=e.page_count,
            content_hash=e.content_hash,
            created_at=e.created_at,
            started_at=e.started_at,
            completed_at=e.completed_at,
            expiry_at=e.expiry_at,
            error_message=e.error_message,
        )

    def _map_thesis_dto(self, t: ResearchInvestmentThesis) -> ResearchThesisResponse:
        return ResearchThesisResponse(
            thesis_id=t.thesis_id,
            investigation_id=t.investigation_id,
            report_id=t.report_id,
            owner_user_id=t.owner_user_id,
            primary_subject_id=t.primary_subject_id,
            primary_subject_type=t.primary_subject_type,
            thesis_statement=t.thesis_statement,
            time_horizon=t.time_horizon,
            status=t.status,
            current_revision=t.current_revision,
            bull_case_summary=t.bull_case_summary,
            bear_case_summary=t.bear_case_summary,
            base_case_summary=t.base_case_summary,
            assumptions_summary=t.assumptions_summary,
            risks_summary=t.risks_summary,
            catalysts_summary=t.catalysts_summary,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    def _build_thesis_detail_response(self, t: ResearchInvestmentThesis) -> ResearchThesisDetailResponse:
        args = self.repository.list_thesis_arguments(t.thesis_id)
        arg_dtos = [self._map_argument_dto(a) for a in args]
        return ResearchThesisDetailResponse(
            thesis_id=t.thesis_id,
            investigation_id=t.investigation_id,
            report_id=t.report_id,
            owner_user_id=t.owner_user_id,
            primary_subject_id=t.primary_subject_id,
            primary_subject_type=t.primary_subject_type,
            thesis_statement=t.thesis_statement,
            time_horizon=t.time_horizon,
            status=t.status,
            current_revision=t.current_revision,
            bull_case_summary=t.bull_case_summary,
            bear_case_summary=t.bear_case_summary,
            base_case_summary=t.base_case_summary,
            assumptions_summary=t.assumptions_summary,
            risks_summary=t.risks_summary,
            catalysts_summary=t.catalysts_summary,
            created_at=t.created_at,
            updated_at=t.updated_at,
            arguments=arg_dtos,
        )

    def _map_argument_dto(self, a: ResearchThesisArgument) -> ResearchThesisArgumentDTO:
        return ResearchThesisArgumentDTO(
            argument_id=a.argument_id,
            thesis_id=a.thesis_id,
            argument_type=a.argument_type,
            statement=a.statement,
            claim_ids=a.claim_ids,
            evidence_ids=a.evidence_ids,
            analysis_run_ids=a.analysis_run_ids,
            finding_ids=a.finding_ids,
            limitations=a.limitations,
            revision=a.revision,
            created_at=a.created_at,
        )

    # ---------------------------------------------------------------------------
    # Stage 108 — Access Grants & Collaboration
    # ---------------------------------------------------------------------------
    def _verify_resource_ownership(self, resource_type: ResearchResourceType, resource_id: str, actor_id: str) -> None:
        """Verifies that the actor has owner permissions on the resource."""
        if resource_type == ResearchResourceType.INVESTIGATION:
            inv = self.repository.get_investigation(resource_id)
            if not inv:
                raise ResearchInvestigationNotFoundError(f"Investigation '{resource_id}' not found.")
            if inv.owner_user_id != actor_id and actor_id != "default-user":
                raise ResearchAccessGrantForbiddenError(f"User '{actor_id}' is not the owner of investigation '{resource_id}'.")
        elif resource_type == ResearchResourceType.REPORT:
            rep = self.repository.get_report(resource_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{resource_id}' not found.")
            if rep.owner_user_id != actor_id and actor_id != "default-user":
                raise ResearchAccessGrantForbiddenError(f"User '{actor_id}' is not the owner of report '{resource_id}'.")
        elif resource_type == ResearchResourceType.THESIS:
            th = self.repository.get_thesis(resource_id)
            if not th:
                raise ResearchInvestmentThesisNotFoundError(f"Thesis '{resource_id}' not found.")
            if th.owner_user_id != actor_id and actor_id != "default-user":
                raise ResearchAccessGrantForbiddenError(f"User '{actor_id}' is not the owner of thesis '{resource_id}'.")

    def _verify_resource_access(
        self, resource_type: ResearchResourceType, resource_id: str, actor_id: str, min_role: ResearchRole = ResearchRole.VIEWER
    ) -> None:
        """Verifies that the actor has at least min_role access on the resource."""
        owner_id = "default-user"
        if resource_type == ResearchResourceType.INVESTIGATION:
            inv = self.repository.get_investigation(resource_id)
            if not inv:
                raise ResearchInvestigationNotFoundError(f"Investigation '{resource_id}' not found.")
            owner_id = inv.owner_user_id
        elif resource_type == ResearchResourceType.REPORT:
            rep = self.repository.get_report(resource_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{resource_id}' not found.")
            owner_id = rep.owner_user_id
        elif resource_type == ResearchResourceType.THESIS:
            th = self.repository.get_thesis(resource_id)
            if not th:
                raise ResearchInvestmentThesisNotFoundError(f"Thesis '{resource_id}' not found.")
            owner_id = th.owner_user_id

        role = self.repository.resolve_user_role(resource_type, resource_id, actor_id, owner_id)
        if not role:
            if actor_id == "default-user":
                return
            raise ResearchReviewAccessDeniedError(f"User '{actor_id}' has no access to {resource_type.value} '{resource_id}'.")

    def create_access_grant(
        self,
        resource_type: ResearchResourceType,
        resource_id: str,
        data: CreateAccessGrantRequest,
        actor_id: str,
    ) -> ResearchAccessGrantResponse:
        self._verify_resource_ownership(resource_type, resource_id, actor_id)

        grant = ResearchAccessGrant(
            grant_id=f"grant-{uuid.uuid4().hex[:12]}",
            resource_type=resource_type,
            resource_id=resource_id,
            principal_type=data.principal_type,
            principal_id=data.principal_id,
            role=data.role,
            granted_by=actor_id,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            expires_at=data.expires_at,
        )
        saved = self.repository.create_access_grant(grant)
        return self._map_access_grant_response(saved)

    def list_access_grants(
        self,
        resource_type: ResearchResourceType,
        resource_id: str,
        actor_id: str,
    ) -> ResearchAccessGrantListResponse:
        self._verify_resource_access(resource_type, resource_id, actor_id, min_role=ResearchRole.VIEWER)
        grants = self.repository.list_access_grants(resource_type, resource_id)
        return ResearchAccessGrantListResponse(
            grants=[self._map_access_grant_response(g) for g in grants],
            total_count=len(grants),
        )

    def update_access_grant(
        self,
        grant_id: str,
        data: UpdateAccessGrantRequest,
        actor_id: str,
    ) -> ResearchAccessGrantResponse:
        g = self.repository.get_access_grant(grant_id)
        if not g:
            raise ResearchAccessGrantNotFoundError(f"Access grant '{grant_id}' not found.")
        self._verify_resource_ownership(g.resource_type, g.resource_id, actor_id)
        updated = self.repository.update_access_grant(grant_id, data.role, actor_id)
        if not updated:
            raise ResearchAccessGrantNotFoundError(f"Access grant '{grant_id}' not found.")
        return self._map_access_grant_response(updated)

    def revoke_access_grant(
        self,
        grant_id: str,
        actor_id: str,
    ) -> ResearchAccessGrantResponse:
        g = self.repository.get_access_grant(grant_id)
        if not g:
            raise ResearchAccessGrantNotFoundError(f"Access grant '{grant_id}' not found.")
        self._verify_resource_ownership(g.resource_type, g.resource_id, actor_id)
        revoked = self.repository.revoke_access_grant(grant_id, actor_id)
        if not revoked:
            raise ResearchAccessGrantNotFoundError(f"Access grant '{grant_id}' not found.")
        return self._map_access_grant_response(revoked)

    def _map_access_grant_response(self, g: ResearchAccessGrant) -> ResearchAccessGrantResponse:
        return ResearchAccessGrantResponse(
            grant_id=g.grant_id,
            resource_type=g.resource_type,
            resource_id=g.resource_id,
            principal_type=g.principal_type,
            principal_id=g.principal_id,
            role=g.role,
            granted_by=g.granted_by,
            organization_id=g.organization_id,
            created_at=g.created_at,
            expires_at=g.expires_at,
            revoked_at=g.revoked_at,
        )

    # ---------------------------------------------------------------------------
    # Stage 108 — Review Workflows & State Machine
    # ---------------------------------------------------------------------------
    def submit_review_request(
        self,
        data: CreateReviewRequest,
        actor_id: str,
    ) -> ResearchReviewRequestResponse:
        target_rev = data.target_revision_number
        content_hash = ""

        if data.target_type == "REPORT":
            rep = self.repository.get_report(data.target_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{data.target_id}' not found.")
            if target_rev is None:
                target_rev = rep.current_revision
            elif target_rev != rep.current_revision:
                raise ResearchReviewRevisionMismatchError(
                    f"Report current revision is {rep.current_revision}, requested {target_rev}."
                )
            import hashlib
            content_hash = hashlib.sha256(f"{rep.report_id}:r{target_rev}:{rep.title}".encode()).hexdigest()[:16]
        else:
            if target_rev is None:
                target_rev = 1
            content_hash = f"hash-{data.target_id}-v{target_rev}"

        # Prevent duplicate active review requests for the same target and revision
        existing_reviews = self.repository.list_review_requests(target_id=data.target_id)
        for r in existing_reviews:
            if (
                r.target_revision_number == target_rev
                and r.status in (ReviewStatus.SUBMITTED, ReviewStatus.IN_REVIEW)
            ):
                raise ResearchReviewDuplicateActiveRequestError(
                    f"An active review request ({r.review_request_id}) is already pending for revision {target_rev}."
                )

        now = datetime.datetime.now(datetime.timezone.utc)
        req = ResearchReviewRequest(
            review_request_id=f"revreq-{uuid.uuid4().hex[:12]}",
            target_type=data.target_type,
            target_id=data.target_id,
            target_revision_number=target_rev,
            target_content_hash=content_hash,
            requested_by=actor_id,
            assigned_reviewer_id=data.assigned_reviewer_id,
            review_scope=data.review_scope,
            review_round=len(existing_reviews) + 1,
            status=ReviewStatus.SUBMITTED,
            due_date=data.due_date,
            instructions=data.instructions,
            created_at=now,
            updated_at=now,
        )

        saved = self.repository.create_review_request(req)

        # Update report status to READY_FOR_REVIEW if currently in DRAFT
        if data.target_type == "REPORT":
            rep = self.repository.get_report(data.target_id)
            if rep and rep.status == ReportLifecycleStatus.DRAFT:
                rep.status = ReportLifecycleStatus.READY_FOR_REVIEW
                self.repository.save_report(rep)

        return self._map_review_request_response(saved)

    def list_review_requests(
        self,
        target_id: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        requested_by: Optional[str] = None,
        status: Optional[ReviewStatus] = None,
    ) -> ResearchReviewListResponse:
        reqs = self.repository.list_review_requests(
            target_id=target_id,
            reviewer_id=reviewer_id,
            requested_by=requested_by,
            status=status,
        )
        items = [self._map_review_request_response(r) for r in reqs]
        return ResearchReviewListResponse(reviews=items, total_count=len(items))

    def get_review_request(self, review_request_id: str, actor_id: str) -> ResearchReviewRequestResponse:
        r = self.repository.get_review_request(review_request_id)
        if not r:
            raise ResearchReviewNotFoundError(f"Review request '{review_request_id}' not found.")
        return self._map_review_request_response(r)

    def update_review_request(
        self,
        review_request_id: str,
        data: UpdateReviewRequest,
        actor_id: str,
    ) -> ResearchReviewRequestResponse:
        r = self.repository.get_review_request(review_request_id)
        if not r:
            raise ResearchReviewNotFoundError(f"Review request '{review_request_id}' not found.")
        if r.requested_by != actor_id and r.assigned_reviewer_id != actor_id and actor_id != "default-user":
            raise ResearchReviewAccessDeniedError(f"User '{actor_id}' cannot update review request '{review_request_id}'.")

        if data.assigned_reviewer_id is not None:
            r.assigned_reviewer_id = data.assigned_reviewer_id
        if data.due_date is not None:
            r.due_date = data.due_date
        if data.instructions is not None:
            r.instructions = data.instructions

        saved = self.repository.update_review_request(r)
        return self._map_review_request_response(saved)

    def cancel_review_request(self, review_request_id: str, actor_id: str) -> ResearchReviewRequestResponse:
        r = self.repository.get_review_request(review_request_id)
        if not r:
            raise ResearchReviewNotFoundError(f"Review request '{review_request_id}' not found.")
        if r.requested_by != actor_id and actor_id != "default-user":
            raise ResearchReviewAccessDeniedError(f"User '{actor_id}' cannot cancel review request '{review_request_id}'.")
        if r.status in (ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.CANCELED):
            raise ResearchReviewInvalidTransitionError(f"Review request is in {r.status.value} and cannot be canceled.")

        r.status = ReviewStatus.CANCELED
        saved = self.repository.update_review_request(r)
        return self._map_review_request_response(saved)

    def decide_review(
        self,
        review_request_id: str,
        data: CreateReviewDecisionRequest,
        actor_id: str,
    ) -> ResearchReviewDecisionResponse:
        r = self.repository.get_review_request(review_request_id)
        if not r:
            raise ResearchReviewNotFoundError(f"Review request '{review_request_id}' not found.")
        if r.status not in (ReviewStatus.SUBMITTED, ReviewStatus.IN_REVIEW):
            raise ResearchReviewAlreadyDecidedError(f"Review request '{review_request_id}' is already {r.status.value}.")

        if r.target_type == "REPORT":
            rep = self.repository.get_report(r.target_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{r.target_id}' not found.")

            # Separation of duties: author cannot approve own report
            if rep.owner_user_id == actor_id and data.decision == ReviewDecisionType.APPROVE:
                raise ResearchReviewSelfApprovalForbiddenError(
                    "Separation of duties violation: Report author cannot approve their own report."
                )

            # Exact revision binding check
            if data.expected_revision_number and data.expected_revision_number != r.target_revision_number:
                raise ResearchReviewRevisionMismatchError(
                    f"Decision expected revision {data.expected_revision_number} does not match review revision {r.target_revision_number}."
                )
            if rep.current_revision != r.target_revision_number:
                raise ResearchReviewRevisionMismatchError(
                    f"Report was updated to revision {rep.current_revision} after review was requested for revision {r.target_revision_number}."
                )

        now = datetime.datetime.now(datetime.timezone.utc)
        decision = ResearchReviewDecision(
            decision_id=f"revdec-{uuid.uuid4().hex[:12]}",
            review_request_id=review_request_id,
            reviewer_user_id=actor_id,
            target_revision_number=r.target_revision_number,
            target_content_hash=r.target_content_hash,
            decision=data.decision,
            decision_comment=data.decision_comment,
            decided_at=now,
        )
        saved_dec = self.repository.create_review_decision(decision)

        # State transitions
        if data.decision == ReviewDecisionType.APPROVE:
            r.status = ReviewStatus.APPROVED
            if r.target_type == "REPORT":
                rep = self.repository.get_report(r.target_id)
                if rep:
                    rep.status = ReportLifecycleStatus.REVIEWED
                    self.repository.save_report(rep)
        elif data.decision == ReviewDecisionType.REJECT:
            r.status = ReviewStatus.REJECTED
            if r.target_type == "REPORT":
                rep = self.repository.get_report(r.target_id)
                if rep:
                    rep.status = ReportLifecycleStatus.DRAFT
                    self.repository.save_report(rep)
        elif data.decision == ReviewDecisionType.REQUEST_CHANGES:
            r.status = ReviewStatus.CHANGES_REQUESTED
            if r.target_type == "REPORT":
                rep = self.repository.get_report(r.target_id)
                if rep:
                    rep.status = ReportLifecycleStatus.DRAFT
                    self.repository.save_report(rep)

        r.completed_at = now
        self.repository.update_review_request(r)

        return ResearchReviewDecisionResponse(
            decision_id=saved_dec.decision_id,
            review_request_id=saved_dec.review_request_id,
            reviewer_user_id=saved_dec.reviewer_user_id,
            target_revision_number=saved_dec.target_revision_number,
            target_content_hash=saved_dec.target_content_hash,
            decision=saved_dec.decision,
            decision_comment=saved_dec.decision_comment,
            decided_at=saved_dec.decided_at,
        )

    def get_report_approval_status(
        self,
        report_id: str,
        revision_number: Optional[int],
        actor_id: str,
    ) -> ResearchApprovalStatusResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        rev = revision_number if revision_number is not None else rep.current_revision

        is_approved, decision = self.repository.get_report_approval_status(report_id, rev)
        return ResearchApprovalStatusResponse(
            report_id=report_id,
            revision_number=rev,
            is_approved=is_approved,
            status_message="Revision is formally approved." if is_approved else "Revision has not received formal review approval.",
            approval_id=decision.decision_id if decision else None,
            approved_by=decision.reviewer_user_id if decision else None,
            approved_at=decision.decided_at if decision else None,
            target_content_hash=decision.target_content_hash if decision else None,
        )

    def _map_review_request_response(self, r: ResearchReviewRequest) -> ResearchReviewRequestResponse:
        decs = self.repository.list_review_decisions(r.review_request_id)
        latest_dec_dto = None
        if decs:
            latest = decs[0]
            latest_dec_dto = ResearchReviewDecisionResponse(
                decision_id=latest.decision_id,
                review_request_id=latest.review_request_id,
                reviewer_user_id=latest.reviewer_user_id,
                target_revision_number=latest.target_revision_number,
                target_content_hash=latest.target_content_hash,
                decision=latest.decision,
                decision_comment=latest.decision_comment,
                decided_at=latest.decided_at,
            )

        return ResearchReviewRequestResponse(
            review_request_id=r.review_request_id,
            target_type=r.target_type,
            target_id=r.target_id,
            target_revision_number=r.target_revision_number,
            target_content_hash=r.target_content_hash,
            requested_by=r.requested_by,
            assigned_reviewer_id=r.assigned_reviewer_id,
            review_scope=r.review_scope,
            review_round=r.review_round,
            status=r.status,
            organization_id=r.organization_id,
            due_date=r.due_date,
            instructions=r.instructions,
            created_at=r.created_at,
            updated_at=r.updated_at,
            completed_at=r.completed_at,
            latest_decision=latest_dec_dto,
        )

    # ---------------------------------------------------------------------------
    # Stage 108 — Anchored Comments & Discussions
    # ---------------------------------------------------------------------------
    def create_comment_thread(
        self,
        resource_type: str,
        resource_id: str,
        data: CreateCommentThreadRequest,
        actor_id: str,
    ) -> ResearchCommentThreadResponse:
        target_rev = data.target_revision_number
        if resource_type == "REPORT":
            rep = self.repository.get_report(resource_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{resource_id}' not found.")
            if target_rev is None:
                target_rev = rep.current_revision
        elif target_rev is None:
            target_rev = 1

        now = datetime.datetime.now(datetime.timezone.utc)
        thread_id = f"cthr-{uuid.uuid4().hex[:12]}"
        thread = ResearchCommentThread(
            thread_id=thread_id,
            resource_type=resource_type,
            resource_id=resource_id,
            target_revision_number=target_rev,
            anchor_type=data.anchor_type,
            anchor_reference=data.anchor_reference,
            anchor_text=data.anchor_text,
            created_by=actor_id,
            created_at=now,
            resolution_status=CommentThreadStatus.OPEN,
            comments_count=1,
        )

        initial_comment = ResearchComment(
            comment_id=f"cmt-{uuid.uuid4().hex[:12]}",
            thread_id=thread_id,
            author_user_id=actor_id,
            body=data.initial_comment,
            created_at=now,
            updated_at=now,
        )

        saved_thread, comments = self.repository.create_comment_thread(thread, initial_comment)
        return self._map_comment_thread_response(saved_thread, comments)

    def list_comment_threads(
        self,
        resource_type: str,
        resource_id: str,
        revision_number: Optional[int],
        actor_id: str,
    ) -> ResearchCommentThreadListResponse:
        pairs = self.repository.list_comment_threads(resource_type, resource_id, revision_number)
        threads = [self._map_comment_thread_response(t, cmts) for t, cmts in pairs]
        return ResearchCommentThreadListResponse(threads=threads, total_count=len(threads))

    def add_comment_reply(
        self,
        thread_id: str,
        data: CreateCommentReplyRequest,
        actor_id: str,
    ) -> ResearchCommentResponse:
        t = self.repository.get_comment_thread(thread_id)
        if not t:
            raise ResearchCommentThreadNotFoundError(f"Comment thread '{thread_id}' not found.")

        now = datetime.datetime.now(datetime.timezone.utc)
        cmt = ResearchComment(
            comment_id=f"cmt-{uuid.uuid4().hex[:12]}",
            thread_id=thread_id,
            author_user_id=actor_id,
            body=data.body,
            created_at=now,
            updated_at=now,
        )
        saved = self.repository.add_comment_reply(cmt)
        return ResearchCommentResponse(
            comment_id=saved.comment_id,
            thread_id=saved.thread_id,
            author_user_id=saved.author_user_id,
            body=saved.body,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
            edit_revision=saved.edit_revision,
        )

    def update_comment(
        self,
        comment_id: str,
        data: UpdateCommentRequest,
        actor_id: str,
    ) -> ResearchCommentResponse:
        updated = self.repository.update_comment(comment_id, data.body, actor_id)
        if not updated:
            raise ResearchCommentAccessDeniedError(f"Cannot edit comment '{comment_id}'. Not found or not authorized.")
        return ResearchCommentResponse(
            comment_id=updated.comment_id,
            thread_id=updated.thread_id,
            author_user_id=updated.author_user_id,
            body=updated.body,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
            edit_revision=updated.edit_revision,
        )

    def resolve_comment_thread(self, thread_id: str, actor_id: str) -> ResearchCommentThreadResponse:
        t = self.repository.resolve_comment_thread(thread_id, actor_id)
        if not t:
            raise ResearchCommentThreadNotFoundError(f"Comment thread '{thread_id}' not found.")
        pairs = self.repository.list_comment_threads(t.resource_type, t.resource_id)
        cmts = []
        for pair_t, pair_cmts in pairs:
            if pair_t.thread_id == thread_id:
                cmts = pair_cmts
                break
        return self._map_comment_thread_response(t, cmts)

    def reopen_comment_thread(self, thread_id: str, actor_id: str) -> ResearchCommentThreadResponse:
        t = self.repository.reopen_comment_thread(thread_id, actor_id)
        if not t:
            raise ResearchCommentThreadNotFoundError(f"Comment thread '{thread_id}' not found.")
        pairs = self.repository.list_comment_threads(t.resource_type, t.resource_id)
        cmts = []
        for pair_t, pair_cmts in pairs:
            if pair_t.thread_id == thread_id:
                cmts = pair_cmts
                break
        return self._map_comment_thread_response(t, cmts)

    def _map_comment_thread_response(
        self, t: ResearchCommentThread, comments: List[ResearchComment]
    ) -> ResearchCommentThreadResponse:
        return ResearchCommentThreadResponse(
            thread_id=t.thread_id,
            resource_type=t.resource_type,
            resource_id=t.resource_id,
            target_revision_number=t.target_revision_number,
            anchor_type=t.anchor_type,
            anchor_reference=t.anchor_reference,
            anchor_text=t.anchor_text,
            created_by=t.created_by,
            created_at=t.created_at,
            resolution_status=t.resolution_status,
            resolved_by=t.resolved_by,
            resolved_at=t.resolved_at,
            is_stale=t.is_stale,
            comments=[
                ResearchCommentResponse(
                    comment_id=c.comment_id,
                    thread_id=c.thread_id,
                    author_user_id=c.author_user_id,
                    body=c.body,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                    edit_revision=c.edit_revision,
                )
                for c in comments
            ],
        )

    # ---------------------------------------------------------------------------
    # Stage 108 — Research Quality Gates & Issue Tracking
    # ---------------------------------------------------------------------------
    def run_quality_gate(
        self,
        report_id: str,
        data: RunQualityGateRequest,
        actor_id: str,
    ) -> QualityGateResultResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        rev = data.revision_number if data.revision_number is not None else rep.current_revision

        sections = self.repository.list_report_sections(report_id)
        verification = verify_research_report(rep, sections, verified_by_user_id=actor_id)

        # Unresolved comments check
        threads_data = self.repository.list_comment_threads("REPORT", report_id, rev)
        unresolved_threads = [
            t for t, _ in threads_data if t.resolution_status in (CommentThreadStatus.OPEN, CommentThreadStatus.REOPENED)
        ]

        issues = list(verification.issues)
        if unresolved_threads:
            issues.append({
                "issue_type": "UNRESOLVED_COMMENTS",
                "severity": "WARNING",
                "message": f"There are {len(unresolved_threads)} unresolved comment thread(s) on revision {rev}.",
            })

        checklist = [
            {
                "check_id": "CHK-01",
                "title": "Report Structural Integrity",
                "passed": verification.blocking_issues_count == 0,
                "detail": f"{verification.blocking_issues_count} blocking structural issues found.",
            },
            {
                "check_id": "CHK-02",
                "title": "Citation & Evidence Coverage",
                "passed": verification.citation_coverage_pct >= 60.0,
                "detail": f"Observed citation coverage: {verification.citation_coverage_pct:.1f}% (target >= 60.0%).",
            },
            {
                "check_id": "CHK-03",
                "title": "Review Comments Resolution",
                "passed": len(unresolved_threads) == 0,
                "detail": f"{len(unresolved_threads)} comment threads remain open.",
            },
            {
                "check_id": "CHK-04",
                "title": "Disclosures & Methodological Limitations",
                "passed": any("limitation" in (s.heading or "").lower() or "methodology" in (s.heading or "").lower() for s in sections),
                "detail": "Methodology or limitations section present in report outline.",
            },
        ]

        eligible_for_review = verification.blocking_issues_count == 0
        eligible_for_finalization = (
            verification.blocking_issues_count == 0
            and len(unresolved_threads) == 0
            and verification.citation_coverage_pct >= 60.0
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        gate_res = QualityGateResult(
            gate_run_id=f"gate-{uuid.uuid4().hex[:12]}",
            report_id=report_id,
            revision_number=rev,
            executed_at=now,
            eligible_for_review=eligible_for_review,
            eligible_for_finalization=eligible_for_finalization,
            blocking_issues_count=verification.blocking_issues_count,
            warnings_count=len([i for i in issues if i.get("severity") == "WARNING"]),
            issues=issues,
            checklist=checklist,
        )
        saved = self.repository.record_quality_gate_result(gate_res)

        return QualityGateResultResponse(
            gate_run_id=saved.gate_run_id,
            report_id=saved.report_id,
            revision_number=saved.revision_number,
            executed_at=saved.executed_at,
            eligible_for_review=saved.eligible_for_review,
            eligible_for_finalization=saved.eligible_for_finalization,
            blocking_issues_count=saved.blocking_issues_count,
            warnings_count=saved.warnings_count,
            issues=saved.issues,
            checklist=saved.checklist,
        )

    # ---------------------------------------------------------------------------
    # Stage 108 — Internal Circulation & Governance
    # ---------------------------------------------------------------------------
    def circulate_report_internally(
        self,
        report_id: str,
        data: CreateCirculationRequest,
        actor_id: str,
    ) -> ResearchInternalCirculationResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        rev = data.revision_number if data.revision_number is not None else rep.current_revision

        is_approved, _ = self.repository.get_report_approval_status(report_id, rev)
        if not is_approved and rep.status not in (ReportLifecycleStatus.REVIEWED, ReportLifecycleStatus.FINALIZED):
            raise ResearchQualityGateFailedError(
                f"Report revision {rev} cannot be circulated internally because it has not been approved."
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        circ = ResearchInternalCirculation(
            circulation_id=f"circ-{uuid.uuid4().hex[:12]}",
            report_id=report_id,
            revision_number=rev,
            initiated_by=actor_id,
            recipient_user_ids=list(data.recipient_user_ids),
            status=CirculationStatus.ACTIVE,
            notes=data.notes,
            created_at=now,
        )
        saved = self.repository.create_internal_circulation(circ)

        return ResearchInternalCirculationResponse(
            circulation_id=saved.circulation_id,
            report_id=saved.report_id,
            revision_number=saved.revision_number,
            initiated_by=saved.initiated_by,
            recipient_user_ids=saved.recipient_user_ids,
            organization_id=saved.organization_id,
            status=saved.status,
            notes=saved.notes,
            created_at=saved.created_at,
            revoked_at=saved.revoked_at,
        )

    def list_internal_circulations(
        self,
        report_id: str,
        actor_id: str,
    ) -> ResearchInternalCirculationListResponse:
        rep = self.repository.get_report(report_id)
        if not rep:
            raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
        circs = self.repository.list_internal_circulations(report_id)
        items = [
            ResearchInternalCirculationResponse(
                circulation_id=c.circulation_id,
                report_id=c.report_id,
                revision_number=c.revision_number,
                initiated_by=c.initiated_by,
                recipient_user_ids=c.recipient_user_ids,
                organization_id=c.organization_id,
                status=c.status,
                notes=c.notes,
                created_at=c.created_at,
                revoked_at=c.revoked_at,
            )
            for c in circs
        ]
        return ResearchInternalCirculationListResponse(circulations=items, total_count=len(items))

    def revoke_internal_circulation(
        self,
        circulation_id: str,
        actor_id: str,
    ) -> ResearchInternalCirculationResponse:
        c = self.repository.revoke_internal_circulation(circulation_id, actor_id)
        if not c:
            raise ResearchCirculationNotFoundError(f"Circulation grant '{circulation_id}' not found.")
        return ResearchInternalCirculationResponse(
            circulation_id=c.circulation_id,
            report_id=c.report_id,
            revision_number=c.revision_number,
            initiated_by=c.initiated_by,
            recipient_user_ids=c.recipient_user_ids,
            organization_id=c.organization_id,
            status=c.status,
            notes=c.notes,
            created_at=c.created_at,
            revoked_at=c.revoked_at,
        )

    # ---------------------------------------------------------------------------
    # Stage 108 — Review Audit Trail
    # ---------------------------------------------------------------------------
    def list_review_audit_events(
        self,
        resource_id: str,
        actor_id: str,
    ) -> ResearchReviewAuditEventListResponse:
        evts = self.repository.list_review_audit_events(resource_id)
        items = [
            ResearchReviewAuditEventResponse(
                audit_event_id=e.audit_event_id,
                actor_user_id=e.actor_user_id,
                resource_type=e.resource_type,
                resource_id=e.resource_id,
                action=e.action,
                occurred_at=e.occurred_at,
                organization_id=e.organization_id,
                target_revision_number=e.target_revision_number,
                details=e.details,
            )
            for e in evts
        ]
        return ResearchReviewAuditEventListResponse(events=items, total_count=len(items))


# Global singleton instance for injection
_GLOBAL_RESEARCH_SERVICE: Optional[ResearchService] = None


def get_research_service() -> ResearchService:
    """Dependency injection provider for ResearchService."""
    global _GLOBAL_RESEARCH_SERVICE
    if _GLOBAL_RESEARCH_SERVICE is None:
        _GLOBAL_RESEARCH_SERVICE = ResearchService()
    return _GLOBAL_RESEARCH_SERVICE
