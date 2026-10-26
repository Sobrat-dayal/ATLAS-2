"""Research Services for Institutional Financial Research Platform (Stage 104)."""

import datetime
import uuid
from typing import Any, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Legacy Stage 36 imports and classes
from atlas.entities.repository import EntityRepository
from atlas.entities.service import EntityService
from atlas.entities.types import EntityTypeKey
from atlas.research.domain import (
    ResearchInvestigation,
    ResearchSourceReference,
)
from atlas.research.enums import (
    InvestigationLifecycleStatus,
    ResearchSourceType,
    ResearchType,
    SourceAvailabilityStatus,
)
from atlas.research.errors import (
    InvalidResearchDocumentKindError,
    ResearchClaimNotFoundError,
    ResearchDocumentDataInconsistentError,
    ResearchDocumentNotFoundError,
    ResearchHypothesisNotFoundError,
    ResearchInvestigationAccessDeniedError,
    ResearchInvestigationNotFoundError,
    ResearchNoteAccessDeniedError,
    ResearchNoteNotFoundError,
    ResearchQuestionNotFoundError,
    ResearchSourceNotFoundError,
)
from atlas.research.repository import ResearchDocumentRepository, ResearchRepository
from atlas.research.schemas import (
    # Stage 105 Schemas
    ConvertEvidenceCandidateDTO,
    CreateResearchClaimDTO,
    CreateResearchHypothesisDTO,
    CreateResearchInvestigationDTO,
    CreateResearchNoteDTO,
    CreateResearchQuestionDTO,
    DocumentComparisonRequestDTO,
    DocumentComparisonResultDTO,
    DocumentComparisonSectionDiffDTO,
    DocumentSearchHitDTO,
    DocumentSearchRequestDTO,
    DocumentSearchResponseDTO,
    EvidenceCandidateListResponseDTO,
    FinancialFactComparisonDTO,
    FinancialFactsCompareRequestDTO,
    FinancialFactsCompareResponseDTO,
    LinkResearchSourceDTO,
    ResearchActivityDTO,
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
    ResearchHypothesisDTO,
    ResearchInvestigationDTO,
    ResearchNoteDTO,
    ResearchNoteRevisionDTO,
    ResearchOverviewSummaryDTO,
    ResearchQuestionDTO,
    ResearchSearchHitDTO,
    ResearchSourceDiscoveryQueryDTO,
    ResearchSourceDiscoveryResponseDTO,
    ResearchSourceReferenceDTO,
    ResearchSourceTypeItemDTO,
    ResearchSourceTypeListResponseDTO,
    ResolveEvidenceLocationRequestDTO,
    ResolveEvidenceLocationResponseDTO,
    UpdateResearchClaimDTO,
    UpdateResearchHypothesisDTO,
    UpdateResearchInvestigationDTO,
    UpdateResearchNoteDTO,
    UpdateResearchQuestionDTO,
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
        if investigation.owner_user_id != user_id:
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


# Global singleton instance for injection
_GLOBAL_RESEARCH_SERVICE: Optional[ResearchService] = None


def get_research_service() -> ResearchService:
    """Dependency injection provider for ResearchService."""
    global _GLOBAL_RESEARCH_SERVICE
    if _GLOBAL_RESEARCH_SERVICE is None:
        _GLOBAL_RESEARCH_SERVICE = ResearchService()
    return _GLOBAL_RESEARCH_SERVICE
