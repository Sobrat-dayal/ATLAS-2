"""Research Repositories for Institutional Financial Research Platform (Stage 104)."""

import copy
import datetime
import threading
import uuid
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

# Keep legacy imports for backwards compatibility
from atlas.entities.models import Entity
from atlas.research.documents import (
    ParsedDocumentData,
    build_canonical_documents_registry,
    compute_document_diff,
    extract_evidence_candidates_from_document,
    resolve_source_location_anchor,
    search_within_document,
)
from atlas.research.domain import (
    DocumentComparisonResult,
    DocumentSearchHit,
    FinancialFactComparison,
    ResearchActivity,
    ResearchCitation,
    ResearchClaim,
    ResearchClaimEvidence,
    ResearchDocumentProcessingRecord,
    ResearchDocumentSection,
    ResearchDocumentTable,
    ResearchEvidence,
    ResearchEvidenceCandidate,
    ResearchHypothesis,
    ResearchInvestigation,
    ResearchNote,
    ResearchNoteRevision,
    ResearchQuestion,
    ResearchSearchHit,
    ResearchSourceReference,
)
from atlas.research.enums import (
    DocumentComparisonMode,
    EvidenceLocationType,
    InvestigationLifecycleStatus,
    ResearchActivityAction,
    ResearchClaimCategory,
    ResearchEvidenceStatus,
    ResearchHypothesisStatus,
    ResearchNoteStatus,
    ResearchNoteType,
    ResearchQuestionStatus,
    ResearchSourceType,
    ResearchType,
    SearchMode,
    SourceAvailabilityStatus,
)
from atlas.research.errors import (
    ResearchClaimNotFoundError,
    ResearchComparisonIncompatibleError,
    ResearchDocumentNotFoundError,
    ResearchDocumentSectionNotFoundError,
    ResearchDocumentTableNotFoundError,
    ResearchEvidenceCandidateNotFoundError,
    ResearchEvidenceNotFoundError,
    ResearchEvidenceSourceMissingError,
    ResearchHypothesisNotFoundError,
    ResearchInvestigationNotFoundError,
    ResearchInvestigationRevisionConflictError,
    ResearchNoteNotFoundError,
    ResearchNoteRevisionConflictError,
    ResearchQuestionNotFoundError,
    ResearchSourceNotFoundError,
)
from atlas.research.models import ResearchDocument
from atlas.research.security import sanitize_markdown_text
from atlas.research.sources import build_canonical_sources_catalog, check_source_deduplication


class ResearchDocumentRepository:
    """Legacy Stage 36 Document Specialization Repository."""

    def __init__(self, session: Session):
        self.session = session

    def get_research_document(
        self, entity_id: uuid.UUID
    ) -> Optional[Tuple[Entity, ResearchDocument]]:
        stmt = (
            select(Entity, ResearchDocument)
            .join(ResearchDocument, Entity.entity_id == ResearchDocument.entity_id)
            .where(Entity.entity_id == entity_id)
        )
        return self.session.execute(stmt).first()

    def create_research_document_specialization(
        self,
        entity_id: uuid.UUID,
        document_kind: Optional[str] = None,
        publication_date: Optional[datetime.date] = None,
        language_code: Optional[str] = None,
        abstract_text: Optional[str] = None,
    ) -> ResearchDocument:
        doc = ResearchDocument(
            entity_id=entity_id,
            document_kind=document_kind,
            publication_date=publication_date,
            language_code=language_code,
            abstract_text=abstract_text,
        )
        self.session.add(doc)
        return doc


# ---------------------------------------------------------------------------
# Stage 104 Canonical Research Repository
# ---------------------------------------------------------------------------

class ResearchRepository:
    """Thread-safe, revision-aware repository for research investigations, evidence, and notes."""

    def __init__(self):
        self._lock = threading.RLock()
        self._investigations: Dict[str, ResearchInvestigation] = {}
        self._questions: Dict[str, ResearchQuestion] = {}
        self._hypotheses: Dict[str, ResearchHypothesis] = {}
        self._notes: Dict[str, ResearchNote] = {}
        self._note_revisions: Dict[str, List[ResearchNoteRevision]] = {}
        self._claims: Dict[str, ResearchClaim] = {}
        self._claim_evidence: List[ResearchClaimEvidence] = []
        self._source_links: Dict[str, List[str]] = {}  # investigation_id -> list of source_reference_ids
        self._sources: Dict[str, ResearchSourceReference] = build_canonical_sources_catalog()
        self._documents: Dict[str, ParsedDocumentData] = build_canonical_documents_registry()
        self._candidates: Dict[str, ResearchEvidenceCandidate] = {}
        self._evidence: Dict[str, ResearchEvidence] = {}
        self._citations: Dict[str, ResearchCitation] = {}
        self._activity: List[ResearchActivity] = []

        self._seed_baseline_investigations()
        self._seed_initial_evidence_candidates()

    # -----------------------------------------------------------------------
    # Baseline Seeding for Developer and Institutional Workflow
    # -----------------------------------------------------------------------
    def _seed_baseline_investigations(self):
        """Seed verified baseline investigations grounded in genuine SEC filings and facts."""
        now = datetime.datetime.now(datetime.timezone.utc)
        user_id = "default-user"

        # 1. Apple Inc. Hardware & Services Margin Analysis
        inv_id_1 = "inv-apple-fy24-margins"
        inv_1 = ResearchInvestigation(
            investigation_id=inv_id_1,
            owner_user_id=user_id,
            title="Apple Inc. (AAPL) Fiscal 2024 Gross Margin & Services Segment Analysis",
            description="Institutional research investigation examining Apple's gross margin trajectory across Products vs Services, analyzing Item 1A Risk Factors from Form 10-K and reported operating results.",
            primary_subject_entity_id="AAPL",
            primary_subject_type="COMPANY",
            secondary_entity_ids=["MSFT", "NVDA"],
            research_type=ResearchType.COMPANY_RESEARCH,
            research_objective="Determine whether expansion in high-margin Services revenue offsets foreign exchange headwind and consumer hardware replacement cycles.",
            status=InvestigationLifecycleStatus.ACTIVE,
            revision=1,
            created_at=now - datetime.timedelta(days=7),
            updated_at=now - datetime.timedelta(hours=2),
            provenance={"created_by": user_id, "source": "ATLAS_RESEARCH_WORKSPACE"},
        )
        self._investigations[inv_id_1] = inv_1
        self._source_links[inv_id_1] = [
            "src-filing-aapl-10k-2024",
            "src-fact-aapl-revenue-fy24",
            "src-fact-aapl-revenue-fy2024",
            "src-fact-aapl-opinc-fy2024",
            "src-news-reuters-aapl-earnings-20241031",
        ]

        # Questions for Inv 1
        q1 = ResearchQuestion(
            question_id="q-aapl-01",
            investigation_id=inv_id_1,
            question_text="How did Apple's total operating margin change between FY2023 and FY2024?",
            status=ResearchQuestionStatus.ADDRESSED,
            related_entity_ids=["AAPL"],
            related_evidence_ids=["ev-aapl-opinc-01"],
            revision=1,
            created_at=now - datetime.timedelta(days=6),
            updated_at=now - datetime.timedelta(days=4),
        )
        q2 = ResearchQuestion(
            question_id="q-aapl-02",
            investigation_id=inv_id_1,
            question_text="What geopolitical or supply chain risks are newly highlighted in the FY2024 Form 10-K Item 1A?",
            status=ResearchQuestionStatus.UNDER_REVIEW,
            related_entity_ids=["AAPL"],
            related_evidence_ids=["ev-aapl-10k-risk"],
            revision=1,
            created_at=now - datetime.timedelta(days=5),
            updated_at=now - datetime.timedelta(days=2),
        )
        self._questions[q1.question_id] = q1
        self._questions[q2.question_id] = q2

        # Hypothesis for Inv 1
        h1 = ResearchHypothesis(
            hypothesis_id="hyp-aapl-01",
            investigation_id=inv_id_1,
            statement="Services revenue gross margin stability is the dominant contributor to Apple operating margin resilience, dampening cyclical volatility in hardware shipments.",
            status=ResearchHypothesisStatus.SUPPORTED_BY_AVAILABLE_EVIDENCE,
            related_claim_ids=["claim-aapl-01"],
            related_evidence_ids=["ev-aapl-opinc-01"],
            revision=1,
            created_at=now - datetime.timedelta(days=6),
            updated_at=now - datetime.timedelta(days=3),
        )
        self._hypotheses[h1.hypothesis_id] = h1

        # Evidence for Inv 1
        ev1 = ResearchEvidence(
            evidence_id="ev-aapl-10k-risk",
            investigation_id=inv_id_1,
            source_reference_id="src-filing-aapl-10k-2024",
            canonical_source_entity_id="AAPL",
            evidence_type="REGULATORY_DISCLOSURE",
            source_location_type=EvidenceLocationType.SECTION,
            source_location_reference="Item 1A Risk Factors - Global Operations and Component Sourcing",
            page_number=6,
            section_name="Item 1A. Risk Factors",
            source_revision="1",
            observation_time=now - datetime.timedelta(days=5),
            allowed_excerpt="The Company's operations and performance depend significantly on global and regional economic conditions, component supply availability, and trade regulations.",
            linked_claim_ids=["claim-aapl-02"],
            created_by=user_id,
            created_at=now - datetime.timedelta(days=5),
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"form": "10-K", "accession": "0000320193-24-000106"},
        )
        ev2 = ResearchEvidence(
            evidence_id="ev-aapl-opinc-01",
            investigation_id=inv_id_1,
            source_reference_id="src-fact-aapl-opinc-fy2024",
            canonical_source_entity_id="AAPL",
            evidence_type="STRUCTURED_FINANCIAL_FACT",
            source_location_type=EvidenceLocationType.DATA_POINT,
            source_location_reference="Consolidated Statements of Operations - Operating Income FY2024",
            page_number=48,
            section_name="Consolidated Financial Statements",
            source_revision="rev-as-reported",
            observation_time=now - datetime.timedelta(days=6),
            allowed_excerpt="Operating Income for FY2024 was reported as $123,216M USD, compared with $114,301M USD in FY2023.",
            linked_claim_ids=["claim-aapl-01"],
            created_by=user_id,
            created_at=now - datetime.timedelta(days=6),
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"metric": "OperatingIncomeLoss", "unit": "USD"},
        )
        self._evidence[ev1.evidence_id] = ev1
        self._evidence[ev2.evidence_id] = ev2

        # Citations for Inv 1
        cit1 = ResearchCitation(
            citation_id="cit-aapl-10k-01",
            investigation_id=inv_id_1,
            evidence_id=ev1.evidence_id,
            source_reference_id="src-filing-aapl-10k-2024",
            citation_label="[SEC Form 10-K FY2024, Item 1A, p. 6]",
            location_reference=ev1.source_location_reference,
            source_revision=ev1.source_revision,
            created_at=now - datetime.timedelta(days=5),
        )
        cit2 = ResearchCitation(
            citation_id="cit-aapl-fact-01",
            investigation_id=inv_id_1,
            evidence_id=ev2.evidence_id,
            source_reference_id="src-fact-aapl-opinc-fy2024",
            citation_label="[Apple FY2024 Operating Income: $123,216M USD]",
            location_reference=ev2.source_location_reference,
            source_revision=ev2.source_revision,
            created_at=now - datetime.timedelta(days=6),
        )
        self._citations[cit1.citation_id] = cit1
        self._citations[cit2.citation_id] = cit2

        # Claims for Inv 1
        c1 = ResearchClaim(
            claim_id="claim-aapl-01",
            investigation_id=inv_id_1,
            statement="Apple reported FY2024 Operating Income of $123,216 million USD, reflecting year-over-year operational leverage.",
            claim_category=ResearchClaimCategory.SOURCE_REPORTED_FACT,
            evidence_status=ResearchEvidenceStatus.SUPPORTED_BY_CITED_SOURCE,
            supporting_evidence_ids=[ev2.evidence_id],
            contradicting_evidence_ids=[],
            related_entity_ids=["AAPL"],
            author_user_id=user_id,
            revision=1,
            created_at=now - datetime.timedelta(days=6),
            updated_at=now - datetime.timedelta(days=6),
        )
        c2 = ResearchClaim(
            claim_id="claim-aapl-02",
            investigation_id=inv_id_1,
            statement="Analyst assessment: Single-region concentration in critical assembly nodes introduces persistent gross margin variability under sudden trade policy friction.",
            claim_category=ResearchClaimCategory.ANALYST_INTERPRETATION,
            evidence_status=ResearchEvidenceStatus.SUPPORTED_BY_CITED_SOURCE,
            supporting_evidence_ids=[ev1.evidence_id],
            contradicting_evidence_ids=[],
            related_entity_ids=["AAPL"],
            author_user_id=user_id,
            revision=1,
            created_at=now - datetime.timedelta(days=5),
            updated_at=now - datetime.timedelta(days=5),
        )
        self._claims[c1.claim_id] = c1
        self._claims[c2.claim_id] = c2

        # Structured Note for Inv 1
        n1 = ResearchNote(
            note_id="note-aapl-01",
            investigation_id=inv_id_1,
            owner_user_id=user_id,
            title="Analysis of Apple FY2024 Operating Leverage and Services Expansion",
            body_document=(
                "## Executive Summary\n\n"
                "According to official regulatory disclosures in Apple's Form 10-K, consolidated FY2024 Net Sales "
                "reached $391,035M USD with Operating Income of $123,216M USD [Apple FY2024 Operating Income: $123,216M USD].\n\n"
                "### Segment Trajectory\n"
                "- **Hardware Cycles**: Hardware replacement cadences exhibited resilience, reinforced by consumer anticipation of AI software features.\n"
                "- **Services Stability**: Services segment margins expanded, providing structural protection to aggregate operating margins.\n\n"
                "### Risk Factor Attribution\n"
                "As disclosed in Item 1A [SEC Form 10-K FY2024, Item 1A, p. 6], global logistics and component sourcing concentration "
                "remain primary sensitivities for cost of sales."
            ),
            note_type=ResearchNoteType.ANALYSIS,
            status=ResearchNoteStatus.IN_PROGRESS,
            related_entity_ids=["AAPL"],
            linked_source_ids=["src-filing-aapl-10k-2024", "src-fact-aapl-opinc-fy2024"],
            linked_evidence_ids=[ev1.evidence_id, ev2.evidence_id],
            citation_ids=[cit1.citation_id, cit2.citation_id],
            revision=1,
            created_at=now - datetime.timedelta(days=5),
            updated_at=now - datetime.timedelta(hours=3),
        )
        self._notes[n1.note_id] = n1
        self._note_revisions[n1.note_id] = [
            ResearchNoteRevision(
                revision_id=f"rev-{n1.note_id}-1",
                note_id=n1.note_id,
                revision_number=1,
                title=n1.title,
                body_document=n1.body_document,
                author_user_id=user_id,
                created_at=n1.created_at,
            )
        ]

        # Activity log
        self._activity.append(
            ResearchActivity(
                activity_id=f"act-{uuid.uuid4().hex[:8]}",
                investigation_id=inv_id_1,
                action_type=ResearchActivityAction.INVESTIGATION_CREATED,
                actor_user_id=user_id,
                object_type="INVESTIGATION",
                object_id=inv_id_1,
                details={"title": inv_1.title},
                occurred_at=inv_1.created_at,
            )
        )
        self._activity.append(
            ResearchActivity(
                activity_id=f"act-{uuid.uuid4().hex[:8]}",
                investigation_id=inv_id_1,
                action_type=ResearchActivityAction.NOTE_CREATED,
                actor_user_id=user_id,
                object_type="NOTE",
                object_id=n1.note_id,
                details={"title": n1.title},
                occurred_at=n1.created_at,
            )
        )

        # 2. Macroeconomic Federal Reserve Policy Transmission
        inv_id_2 = "inv-macro-fed-yield-2024"
        inv_2 = ResearchInvestigation(
            investigation_id=inv_id_2,
            owner_user_id=user_id,
            title="Macroeconomic Analysis: Federal Reserve Rate Cycle & Inflation Deceleration",
            description="Macroeconomic research investigation tracking the Federal Reserve monetary policy pivot from 5.25%-5.50% to 4.75%-5.00% and corresponding September 2024 CPI prints.",
            primary_subject_entity_id="US_CPI",
            primary_subject_type="MACROECONOMIC",
            secondary_entity_ids=["FED", "SPY"],
            research_type=ResearchType.MACROECONOMIC_RESEARCH,
            research_objective="Trace the lag and magnitude of monetary policy easing transmission into consumer price components.",
            status=InvestigationLifecycleStatus.ACTIVE,
            revision=1,
            created_at=now - datetime.timedelta(days=14),
            updated_at=now - datetime.timedelta(days=1),
            provenance={"created_by": user_id, "source": "ATLAS_RESEARCH_WORKSPACE"},
        )
        self._investigations[inv_id_2] = inv_2
        self._source_links[inv_id_2] = [
            "src-news-bloomberg-fed-rate-20240918",
            "src-econ-bls-cpi-202409",
        ]

    # -----------------------------------------------------------------------
    # Investigation CRUD Operations
    # -----------------------------------------------------------------------
    def create_investigation(
        self,
        owner_user_id: str,
        title: str,
        research_type: ResearchType,
        primary_subject_entity_id: Optional[str] = None,
        primary_subject_type: Optional[str] = None,
        secondary_entity_ids: Optional[List[str]] = None,
        research_objective: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ResearchInvestigation:
        with self._lock:
            now = datetime.datetime.now(datetime.timezone.utc)
            inv_id = f"inv-{uuid.uuid4().hex[:10]}"

            clean_desc = sanitize_markdown_text(description or "", max_length=50000)

            inv = ResearchInvestigation(
                investigation_id=inv_id,
                owner_user_id=owner_user_id,
                title=title.strip(),
                description=clean_desc if clean_desc else None,
                primary_subject_entity_id=primary_subject_entity_id,
                primary_subject_type=primary_subject_type,
                secondary_entity_ids=secondary_entity_ids or [],
                research_type=research_type,
                research_objective=research_objective.strip() if research_objective else None,
                status=InvestigationLifecycleStatus.DRAFT,
                revision=1,
                created_at=now,
                updated_at=now,
                provenance={"created_by": owner_user_id},
            )
            self._investigations[inv_id] = inv
            self._source_links[inv_id] = []

            self.record_activity(
                investigation_id=inv_id,
                action_type=ResearchActivityAction.INVESTIGATION_CREATED,
                actor_user_id=owner_user_id,
                object_type="INVESTIGATION",
                object_id=inv_id,
                details={"title": inv.title, "research_type": inv.research_type.value},
            )
            return copy.deepcopy(inv)

    def get_investigation(self, investigation_id: str) -> Optional[ResearchInvestigation]:
        with self._lock:
            inv = self._investigations.get(investigation_id)
            return copy.deepcopy(inv) if inv else None

    def update_investigation(
        self,
        investigation_id: str,
        expected_revision: int,
        title: Optional[str] = None,
        research_type: Optional[ResearchType] = None,
        primary_subject_entity_id: Optional[str] = None,
        primary_subject_type: Optional[str] = None,
        secondary_entity_ids: Optional[List[str]] = None,
        research_objective: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[InvestigationLifecycleStatus] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchInvestigation:
        with self._lock:
            inv = self._investigations.get(investigation_id)
            if not inv:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            # Optimistic concurrency check
            if inv.revision != expected_revision:
                raise ResearchInvestigationRevisionConflictError(
                    f"Revision conflict on investigation '{investigation_id}': "
                    f"expected revision {expected_revision}, but current revision is {inv.revision}."
                )

            now = datetime.datetime.now(datetime.timezone.utc)
            if title is not None:
                inv.title = title.strip()
            if research_type is not None:
                inv.research_type = research_type
            if primary_subject_entity_id is not None:
                inv.primary_subject_entity_id = primary_subject_entity_id
            if primary_subject_type is not None:
                inv.primary_subject_type = primary_subject_type
            if secondary_entity_ids is not None:
                inv.secondary_entity_ids = secondary_entity_ids
            if research_objective is not None:
                inv.research_objective = research_objective.strip()
            if description is not None:
                inv.description = sanitize_markdown_text(description, max_length=50000)
            if status is not None:
                old_status = inv.status
                inv.status = status
                if status == InvestigationLifecycleStatus.ARCHIVED and not inv.archived_at:
                    inv.archived_at = now
                self.record_activity(
                    investigation_id=investigation_id,
                    action_type=ResearchActivityAction.STATUS_CHANGED,
                    actor_user_id=actor_user_id,
                    object_type="INVESTIGATION",
                    object_id=investigation_id,
                    details={"old_status": old_status.value, "new_status": status.value},
                )

            inv.revision += 1
            inv.updated_at = now

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.INVESTIGATION_UPDATED,
                actor_user_id=actor_user_id,
                object_type="INVESTIGATION",
                object_id=investigation_id,
                details={"revision": inv.revision},
            )
            return copy.deepcopy(inv)

    def archive_investigation(self, investigation_id: str, actor_user_id: str = "default-user") -> ResearchInvestigation:
        with self._lock:
            inv = self._investigations.get(investigation_id)
            if not inv:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
            now = datetime.datetime.now(datetime.timezone.utc)
            inv.status = InvestigationLifecycleStatus.ARCHIVED
            inv.archived_at = now
            inv.revision += 1
            inv.updated_at = now

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.INVESTIGATION_ARCHIVED,
                actor_user_id=actor_user_id,
                object_type="INVESTIGATION",
                object_id=investigation_id,
                details={"status": inv.status.value},
            )
            return copy.deepcopy(inv)

    def delete_investigation(self, investigation_id: str) -> bool:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
            del self._investigations[investigation_id]
            self._source_links.pop(investigation_id, None)
            return True

    def list_investigations(
        self,
        owner_user_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        status: Optional[InvestigationLifecycleStatus] = None,
        research_type: Optional[ResearchType] = None,
        q: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ResearchInvestigation], int]:
        with self._lock:
            results: List[ResearchInvestigation] = []
            for inv in self._investigations.values():
                if owner_user_id and inv.owner_user_id != owner_user_id:
                    continue
                if entity_id:
                    has_entity = (
                        inv.primary_subject_entity_id == entity_id
                        or entity_id in inv.secondary_entity_ids
                    )
                    if not has_entity:
                        continue
                if status and inv.status != status:
                    continue
                if research_type and inv.research_type != research_type:
                    continue
                if q:
                    query_lower = q.lower().strip()
                    title_match = query_lower in inv.title.lower()
                    desc_match = bool(inv.description and query_lower in inv.description.lower())
                    obj_match = bool(inv.research_objective and query_lower in inv.research_objective.lower())
                    if not (title_match or desc_match or obj_match):
                        continue
                results.append(inv)

            results.sort(key=lambda x: x.updated_at, reverse=True)
            total = len(results)
            paginated = results[offset : offset + limit]
            return [copy.deepcopy(x) for x in paginated], total

    # -----------------------------------------------------------------------
    # Question CRUD Operations
    # -----------------------------------------------------------------------
    def add_question(
        self,
        investigation_id: str,
        question_text: str,
        related_entity_ids: Optional[List[str]] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchQuestion:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            q_id = f"q-{uuid.uuid4().hex[:8]}"
            q = ResearchQuestion(
                question_id=q_id,
                investigation_id=investigation_id,
                question_text=question_text.strip(),
                status=ResearchQuestionStatus.OPEN,
                related_entity_ids=related_entity_ids or [],
                related_evidence_ids=[],
                revision=1,
                created_at=now,
                updated_at=now,
            )
            self._questions[q_id] = q
            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.QUESTION_ADDED,
                actor_user_id=actor_user_id,
                object_type="QUESTION",
                object_id=q_id,
                details={"question_text": q.question_text[:100]},
            )
            return copy.deepcopy(q)

    def get_question(self, question_id: str) -> Optional[ResearchQuestion]:
        with self._lock:
            q = self._questions.get(question_id)
            return copy.deepcopy(q) if q else None

    def update_question(
        self,
        question_id: str,
        question_text: Optional[str] = None,
        status: Optional[ResearchQuestionStatus] = None,
        related_entity_ids: Optional[List[str]] = None,
        related_evidence_ids: Optional[List[str]] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchQuestion:
        with self._lock:
            q = self._questions.get(question_id)
            if not q:
                raise ResearchQuestionNotFoundError(f"Question '{question_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            if question_text is not None:
                q.question_text = question_text.strip()
            if status is not None:
                q.status = status
            if related_entity_ids is not None:
                q.related_entity_ids = related_entity_ids
            if related_evidence_ids is not None:
                q.related_evidence_ids = related_evidence_ids

            q.revision += 1
            q.updated_at = now

            self.record_activity(
                investigation_id=q.investigation_id,
                action_type=ResearchActivityAction.QUESTION_UPDATED,
                actor_user_id=actor_user_id,
                object_type="QUESTION",
                object_id=question_id,
                details={"status": q.status.value},
            )
            return copy.deepcopy(q)

    def delete_question(self, question_id: str, actor_user_id: str = "default-user") -> bool:
        with self._lock:
            q = self._questions.get(question_id)
            if not q:
                raise ResearchQuestionNotFoundError(f"Question '{question_id}' not found.")
            investigation_id = q.investigation_id
            del self._questions[question_id]

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.QUESTION_DELETED,
                actor_user_id=actor_user_id,
                object_type="QUESTION",
                object_id=question_id,
                details={},
            )
            return True

    def list_questions_by_investigation(self, investigation_id: str) -> List[ResearchQuestion]:
        with self._lock:
            items = [q for q in self._questions.values() if q.investigation_id == investigation_id]
            items.sort(key=lambda x: x.created_at)
            return [copy.deepcopy(x) for x in items]

    # -----------------------------------------------------------------------
    # Hypothesis CRUD Operations
    # -----------------------------------------------------------------------
    def add_hypothesis(
        self,
        investigation_id: str,
        statement: str,
        related_claim_ids: Optional[List[str]] = None,
        related_evidence_ids: Optional[List[str]] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchHypothesis:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            h_id = f"hyp-{uuid.uuid4().hex[:8]}"
            h = ResearchHypothesis(
                hypothesis_id=h_id,
                investigation_id=investigation_id,
                statement=statement.strip(),
                status=ResearchHypothesisStatus.PROPOSED,
                related_claim_ids=related_claim_ids or [],
                related_evidence_ids=related_evidence_ids or [],
                revision=1,
                created_at=now,
                updated_at=now,
            )
            self._hypotheses[h_id] = h
            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.HYPOTHESIS_ADDED,
                actor_user_id=actor_user_id,
                object_type="HYPOTHESIS",
                object_id=h_id,
                details={"statement": h.statement[:100]},
            )
            return copy.deepcopy(h)

    def get_hypothesis(self, hypothesis_id: str) -> Optional[ResearchHypothesis]:
        with self._lock:
            h = self._hypotheses.get(hypothesis_id)
            return copy.deepcopy(h) if h else None

    def update_hypothesis(
        self,
        hypothesis_id: str,
        statement: Optional[str] = None,
        status: Optional[ResearchHypothesisStatus] = None,
        related_claim_ids: Optional[List[str]] = None,
        related_evidence_ids: Optional[List[str]] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchHypothesis:
        with self._lock:
            h = self._hypotheses.get(hypothesis_id)
            if not h:
                raise ResearchHypothesisNotFoundError(f"Hypothesis '{hypothesis_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            if statement is not None:
                h.statement = statement.strip()
            if status is not None:
                h.status = status
            if related_claim_ids is not None:
                h.related_claim_ids = related_claim_ids
            if related_evidence_ids is not None:
                h.related_evidence_ids = related_evidence_ids

            h.revision += 1
            h.updated_at = now

            self.record_activity(
                investigation_id=h.investigation_id,
                action_type=ResearchActivityAction.HYPOTHESIS_UPDATED,
                actor_user_id=actor_user_id,
                object_type="HYPOTHESIS",
                object_id=hypothesis_id,
                details={"status": h.status.value},
            )
            return copy.deepcopy(h)

    def delete_hypothesis(self, hypothesis_id: str, actor_user_id: str = "default-user") -> bool:
        with self._lock:
            h = self._hypotheses.get(hypothesis_id)
            if not h:
                raise ResearchHypothesisNotFoundError(f"Hypothesis '{hypothesis_id}' not found.")
            investigation_id = h.investigation_id
            del self._hypotheses[hypothesis_id]

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.HYPOTHESIS_DELETED,
                actor_user_id=actor_user_id,
                object_type="HYPOTHESIS",
                object_id=hypothesis_id,
                details={},
            )
            return True

    def list_hypotheses_by_investigation(self, investigation_id: str) -> List[ResearchHypothesis]:
        with self._lock:
            items = [h for h in self._hypotheses.values() if h.investigation_id == investigation_id]
            items.sort(key=lambda x: x.created_at)
            return [copy.deepcopy(x) for x in items]

    # -----------------------------------------------------------------------
    # Research Note CRUD & Revisioning Operations
    # -----------------------------------------------------------------------
    def create_note(
        self,
        investigation_id: str,
        owner_user_id: str,
        title: str,
        body_document: str = "",
        note_type: ResearchNoteType = ResearchNoteType.GENERAL_NOTE,
        related_entity_ids: Optional[List[str]] = None,
        linked_source_ids: Optional[List[str]] = None,
        linked_evidence_ids: Optional[List[str]] = None,
    ) -> ResearchNote:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            note_id = f"note-{uuid.uuid4().hex[:8]}"
            clean_body = sanitize_markdown_text(body_document)

            note = ResearchNote(
                note_id=note_id,
                investigation_id=investigation_id,
                owner_user_id=owner_user_id,
                title=title.strip(),
                body_document=clean_body,
                note_type=note_type,
                status=ResearchNoteStatus.DRAFT,
                related_entity_ids=related_entity_ids or [],
                linked_source_ids=linked_source_ids or [],
                linked_evidence_ids=linked_evidence_ids or [],
                citation_ids=[],
                revision=1,
                created_at=now,
                updated_at=now,
            )
            self._notes[note_id] = note

            # Save initial revision
            self._note_revisions[note_id] = [
                ResearchNoteRevision(
                    revision_id=f"rev-{note_id}-1",
                    note_id=note_id,
                    revision_number=1,
                    title=note.title,
                    body_document=note.body_document,
                    author_user_id=owner_user_id,
                    created_at=now,
                )
            ]

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.NOTE_CREATED,
                actor_user_id=owner_user_id,
                object_type="NOTE",
                object_id=note_id,
                details={"title": note.title, "note_type": note.note_type.value},
            )
            return copy.deepcopy(note)

    def get_note(self, note_id: str) -> Optional[ResearchNote]:
        with self._lock:
            n = self._notes.get(note_id)
            return copy.deepcopy(n) if n else None

    def update_note(
        self,
        note_id: str,
        expected_revision: int,
        title: Optional[str] = None,
        body_document: Optional[str] = None,
        note_type: Optional[ResearchNoteType] = None,
        status: Optional[ResearchNoteStatus] = None,
        related_entity_ids: Optional[List[str]] = None,
        linked_source_ids: Optional[List[str]] = None,
        linked_evidence_ids: Optional[List[str]] = None,
        citation_ids: Optional[List[str]] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchNote:
        with self._lock:
            note = self._notes.get(note_id)
            if not note:
                raise ResearchNoteNotFoundError(f"Research note '{note_id}' not found.")

            # Concurrency conflict check
            if note.revision != expected_revision:
                raise ResearchNoteRevisionConflictError(
                    f"Revision conflict on note '{note_id}': "
                    f"expected revision {expected_revision}, but current revision is {note.revision}."
                )

            now = datetime.datetime.now(datetime.timezone.utc)
            if title is not None:
                note.title = title.strip()
            if body_document is not None:
                note.body_document = sanitize_markdown_text(body_document)
            if note_type is not None:
                note.note_type = note_type
            if status is not None:
                note.status = status
            if related_entity_ids is not None:
                note.related_entity_ids = related_entity_ids
            if linked_source_ids is not None:
                note.linked_source_ids = linked_source_ids
            if linked_evidence_ids is not None:
                note.linked_evidence_ids = linked_evidence_ids
            if citation_ids is not None:
                note.citation_ids = citation_ids

            note.revision += 1
            note.updated_at = now

            # Record point-in-time snapshot
            rev = ResearchNoteRevision(
                revision_id=f"rev-{note_id}-{note.revision}",
                note_id=note_id,
                revision_number=note.revision,
                title=note.title,
                body_document=note.body_document,
                author_user_id=actor_user_id,
                created_at=now,
            )
            if note_id not in self._note_revisions:
                self._note_revisions[note_id] = []
            self._note_revisions[note_id].append(rev)

            self.record_activity(
                investigation_id=note.investigation_id,
                action_type=ResearchActivityAction.NOTE_UPDATED,
                actor_user_id=actor_user_id,
                object_type="NOTE",
                object_id=note_id,
                details={"revision": note.revision},
            )
            return copy.deepcopy(note)

    def delete_note(self, note_id: str, actor_user_id: str = "default-user") -> bool:
        with self._lock:
            note = self._notes.get(note_id)
            if not note:
                raise ResearchNoteNotFoundError(f"Research note '{note_id}' not found.")
            investigation_id = note.investigation_id
            del self._notes[note_id]
            self._note_revisions.pop(note_id, None)

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.NOTE_DELETED,
                actor_user_id=actor_user_id,
                object_type="NOTE",
                object_id=note_id,
                details={},
            )
            return True

    def list_notes_by_investigation(self, investigation_id: str) -> List[ResearchNote]:
        with self._lock:
            items = [n for n in self._notes.values() if n.investigation_id == investigation_id]
            items.sort(key=lambda x: x.updated_at, reverse=True)
            return [copy.deepcopy(x) for x in items]

    def get_note_revisions(self, note_id: str) -> List[ResearchNoteRevision]:
        with self._lock:
            revs = self._note_revisions.get(note_id, [])
            return [copy.deepcopy(r) for r in revs]

    # -----------------------------------------------------------------------
    # Research Claim Operations
    # -----------------------------------------------------------------------
    def create_claim(
        self,
        investigation_id: str,
        statement: str,
        claim_category: ResearchClaimCategory = ResearchClaimCategory.ANALYST_INTERPRETATION,
        evidence_status: ResearchEvidenceStatus = ResearchEvidenceStatus.NOT_REVIEWED,
        supporting_evidence_ids: Optional[List[str]] = None,
        contradicting_evidence_ids: Optional[List[str]] = None,
        related_entity_ids: Optional[List[str]] = None,
        author_user_id: str = "default-user",
    ) -> ResearchClaim:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            claim_id = f"claim-{uuid.uuid4().hex[:8]}"
            claim = ResearchClaim(
                claim_id=claim_id,
                investigation_id=investigation_id,
                statement=statement.strip(),
                claim_category=claim_category,
                evidence_status=evidence_status,
                supporting_evidence_ids=supporting_evidence_ids or [],
                contradicting_evidence_ids=contradicting_evidence_ids or [],
                related_entity_ids=related_entity_ids or [],
                author_user_id=author_user_id,
                revision=1,
                created_at=now,
                updated_at=now,
            )
            self._claims[claim_id] = claim

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.CLAIM_CREATED,
                actor_user_id=author_user_id,
                object_type="CLAIM",
                object_id=claim_id,
                details={"claim_category": claim.claim_category.value},
            )
            return copy.deepcopy(claim)

    def get_claim(self, claim_id: str) -> Optional[ResearchClaim]:
        with self._lock:
            c = self._claims.get(claim_id)
            return copy.deepcopy(c) if c else None

    def update_claim(
        self,
        claim_id: str,
        statement: Optional[str] = None,
        claim_category: Optional[ResearchClaimCategory] = None,
        evidence_status: Optional[ResearchEvidenceStatus] = None,
        supporting_evidence_ids: Optional[List[str]] = None,
        contradicting_evidence_ids: Optional[List[str]] = None,
        related_entity_ids: Optional[List[str]] = None,
        actor_user_id: str = "default-user",
    ) -> ResearchClaim:
        with self._lock:
            c = self._claims.get(claim_id)
            if not c:
                raise ResearchClaimNotFoundError(f"Claim '{claim_id}' not found.")

            now = datetime.datetime.now(datetime.timezone.utc)
            if statement is not None:
                c.statement = statement.strip()
            if claim_category is not None:
                c.claim_category = claim_category
            if evidence_status is not None:
                c.evidence_status = evidence_status
            if supporting_evidence_ids is not None:
                c.supporting_evidence_ids = supporting_evidence_ids
            if contradicting_evidence_ids is not None:
                c.contradicting_evidence_ids = contradicting_evidence_ids
            if related_entity_ids is not None:
                c.related_entity_ids = related_entity_ids

            c.revision += 1
            c.updated_at = now

            self.record_activity(
                investigation_id=c.investigation_id,
                action_type=ResearchActivityAction.CLAIM_UPDATED,
                actor_user_id=actor_user_id,
                object_type="CLAIM",
                object_id=claim_id,
                details={"evidence_status": c.evidence_status.value},
            )
            return copy.deepcopy(c)

    def delete_claim(self, claim_id: str, actor_user_id: str = "default-user") -> bool:
        with self._lock:
            c = self._claims.get(claim_id)
            if not c:
                raise ResearchClaimNotFoundError(f"Claim '{claim_id}' not found.")
            investigation_id = c.investigation_id
            del self._claims[claim_id]

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.CLAIM_DELETED,
                actor_user_id=actor_user_id,
                object_type="CLAIM",
                object_id=claim_id,
                details={},
            )
            return True

    def list_claims_by_investigation(self, investigation_id: str) -> List[ResearchClaim]:
        with self._lock:
            items = [c for c in self._claims.values() if c.investigation_id == investigation_id]
            items.sort(key=lambda x: x.created_at)
            return [copy.deepcopy(x) for x in items]

    # -----------------------------------------------------------------------
    # Source Reference & Linking Operations
    # -----------------------------------------------------------------------
    def get_source(self, source_reference_id: str) -> Optional[ResearchSourceReference]:
        with self._lock:
            src = self._sources.get(source_reference_id)
            if src:
                return copy.deepcopy(src)
            for s in self._sources.values():
                if s.canonical_document_id == source_reference_id:
                    return copy.deepcopy(s)
            return None

    def list_sources(
        self,
        source_type: Optional[ResearchSourceType] = None,
        entity_id: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List[ResearchSourceReference]:
        with self._lock:
            results = []
            for src in self._sources.values():
                if source_type and src.source_type != source_type:
                    continue
                if entity_id and src.canonical_entity_id != entity_id:
                    continue
                if q:
                    ql = q.lower().strip()
                    title_match = ql in src.source_title.lower()
                    pub_match = bool(src.publisher_id and ql in src.publisher_id.lower())
                    doc_match = bool(src.canonical_document_id and ql in src.canonical_document_id.lower())
                    if not (title_match or pub_match or doc_match):
                        continue
                results.append(src)

            results.sort(key=lambda s: s.published_at or s.registered_at, reverse=True)
            return [copy.deepcopy(x) for x in results]

    def register_custom_source(
        self,
        source: ResearchSourceReference,
    ) -> ResearchSourceReference:
        with self._lock:
            # Check deduplication
            existing = check_source_deduplication(
                list(self._sources.values()),
                candidate_doc_id=source.canonical_document_id,
                candidate_url=source.source_url,
            )
            if existing:
                return copy.deepcopy(existing)

            self._sources[source.source_reference_id] = source
            return copy.deepcopy(source)

    def link_source_to_investigation(
        self,
        investigation_id: str,
        source_reference_id: str,
        actor_user_id: str = "default-user",
    ) -> bool:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
            if source_reference_id not in self._sources:
                raise ResearchSourceNotFoundError(f"Source '{source_reference_id}' not found.")

            links = self._source_links.setdefault(investigation_id, [])
            if source_reference_id in links:
                return False  # Already linked (idempotent)

            links.append(source_reference_id)
            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.SOURCE_LINKED,
                actor_user_id=actor_user_id,
                object_type="SOURCE",
                object_id=source_reference_id,
                details={"source_reference_id": source_reference_id},
            )
            return True

    def unlink_source_from_investigation(
        self,
        investigation_id: str,
        source_reference_id: str,
        actor_user_id: str = "default-user",
    ) -> bool:
        with self._lock:
            links = self._source_links.get(investigation_id, [])
            if source_reference_id in links:
                links.remove(source_reference_id)
                self.record_activity(
                    investigation_id=investigation_id,
                    action_type=ResearchActivityAction.SOURCE_UNLINKED,
                    actor_user_id=actor_user_id,
                    object_type="SOURCE",
                    object_id=source_reference_id,
                    details={},
                )
                return True
            return False

    def list_sources_by_investigation(self, investigation_id: str) -> List[ResearchSourceReference]:
        with self._lock:
            links = self._source_links.get(investigation_id, [])
            results = [self._sources[sid] for sid in links if sid in self._sources]
            return [copy.deepcopy(x) for x in results]

    # -----------------------------------------------------------------------
    # Evidence & Citation Operations
    # -----------------------------------------------------------------------
    def attach_evidence(
        self,
        investigation_id: str,
        source_reference_id: str,
        source_location_reference: str,
        evidence_type: str = "QUALITATIVE_QUOTE",
        source_location_type: EvidenceLocationType = EvidenceLocationType.SECTION,
        page_number: Optional[int] = None,
        section_name: Optional[str] = None,
        allowed_excerpt: Optional[str] = None,
        linked_claim_ids: Optional[List[str]] = None,
        created_by: str = "default-user",
    ) -> ResearchEvidence:
        with self._lock:
            if investigation_id not in self._investigations:
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
            source = self._sources.get(source_reference_id)
            if not source:
                raise ResearchEvidenceSourceMissingError(
                    f"Referenced source '{source_reference_id}' does not exist in catalog."
                )

            now = datetime.datetime.now(datetime.timezone.utc)
            ev_id = f"ev-{uuid.uuid4().hex[:8]}"

            clean_excerpt = sanitize_markdown_text(allowed_excerpt or "", max_length=5000)

            ev = ResearchEvidence(
                evidence_id=ev_id,
                investigation_id=investigation_id,
                source_reference_id=source_reference_id,
                canonical_source_entity_id=source.canonical_entity_id,
                evidence_type=evidence_type,
                source_location_type=source_location_type,
                source_location_reference=source_location_reference.strip(),
                page_number=page_number,
                section_name=section_name.strip() if section_name else None,
                source_revision=source.source_revision,
                observation_time=now,
                allowed_excerpt=clean_excerpt if clean_excerpt else None,
                linked_claim_ids=linked_claim_ids or [],
                created_by=created_by,
                created_at=now,
                availability_status=source.availability_status,
                provenance={"source_type": source.source_type.value, "provider": source.provider_id},
            )
            self._evidence[ev_id] = ev

            # Auto-link source to investigation if not already linked
            self.link_source_to_investigation(investigation_id, source_reference_id, actor_user_id=created_by)

            # Generate and register a Citation
            page_text = f", p. {page_number}" if page_number else ""
            cit_label = f"[{source.publisher_id or source.provider_id}: {source.source_title[:40]}...{page_text}]"
            cit_id = f"cit-{uuid.uuid4().hex[:8]}"
            cit = ResearchCitation(
                citation_id=cit_id,
                investigation_id=investigation_id,
                evidence_id=ev_id,
                source_reference_id=source_reference_id,
                citation_label=cit_label,
                location_reference=ev.source_location_reference,
                source_revision=ev.source_revision,
                created_at=now,
                is_broken=(source.availability_status in (SourceAvailabilityStatus.WITHDRAWN, SourceAvailabilityStatus.UNAVAILABLE)),
            )
            self._citations[cit_id] = cit

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.EVIDENCE_ATTACHED,
                actor_user_id=created_by,
                object_type="EVIDENCE",
                object_id=ev_id,
                details={"location": ev.source_location_reference},
            )
            return copy.deepcopy(ev)

    def get_evidence(self, evidence_id: str) -> Optional[ResearchEvidence]:
        with self._lock:
            ev = self._evidence.get(evidence_id)
            return copy.deepcopy(ev) if ev else None

    def remove_evidence(self, evidence_id: str, actor_user_id: str = "default-user") -> bool:
        with self._lock:
            ev = self._evidence.get(evidence_id)
            if not ev:
                raise ResearchEvidenceNotFoundError(f"Evidence '{evidence_id}' not found.")
            investigation_id = ev.investigation_id
            del self._evidence[evidence_id]

            # Mark associated citations as broken
            for cit in self._citations.values():
                if cit.evidence_id == evidence_id:
                    cit.is_broken = True
                    cit.status_reason = "Underlying evidence record was deleted."

            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.EVIDENCE_REMOVED,
                actor_user_id=actor_user_id,
                object_type="EVIDENCE",
                object_id=evidence_id,
                details={},
            )
            return True

    def list_evidence_by_investigation(self, investigation_id: str) -> List[ResearchEvidence]:
        with self._lock:
            items = [e for e in self._evidence.values() if e.investigation_id == investigation_id]
            items.sort(key=lambda x: x.created_at)
            return [copy.deepcopy(x) for x in items]

    def list_citations_by_investigation(self, investigation_id: str) -> List[ResearchCitation]:
        with self._lock:
            items = [c for c in self._citations.values() if c.investigation_id == investigation_id]
            items.sort(key=lambda x: x.created_at)
            return [copy.deepcopy(x) for x in items]

    # -----------------------------------------------------------------------
    # Activity Logging & Overview Summary
    # -----------------------------------------------------------------------
    def record_activity(
        self,
        investigation_id: str,
        action_type: ResearchActivityAction,
        actor_user_id: str,
        object_type: str,
        object_id: str,
        details: Dict,
    ):
        act_id = f"act-{uuid.uuid4().hex[:10]}"
        act = ResearchActivity(
            activity_id=act_id,
            investigation_id=investigation_id,
            action_type=action_type,
            actor_user_id=actor_user_id,
            object_type=object_type,
            object_id=object_id,
            details=details,
            occurred_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self._activity.append(act)

    def list_activity_by_investigation(self, investigation_id: str) -> List[ResearchActivity]:
        with self._lock:
            items = [a for a in self._activity if a.investigation_id == investigation_id]
            items.sort(key=lambda x: x.occurred_at, reverse=True)
            return [copy.deepcopy(x) for x in items]

    def get_overview_summary(self, owner_user_id: str) -> Dict:
        with self._lock:
            user_invs = [i for i in self._investigations.values() if i.owner_user_id == owner_user_id]
            active_count = sum(1 for i in user_invs if i.status == InvestigationLifecycleStatus.ACTIVE)
            draft_count = sum(1 for i in user_invs if i.status == InvestigationLifecycleStatus.DRAFT)
            completed_count = sum(1 for i in user_invs if i.status == InvestigationLifecycleStatus.COMPLETED)
            archived_count = sum(1 for i in user_invs if i.status == InvestigationLifecycleStatus.ARCHIVED)

            user_notes = [n for n in self._notes.values() if n.owner_user_id == owner_user_id]
            total_notes = len(user_notes)
            total_sources = sum(len(self._source_links.get(i.investigation_id, [])) for i in user_invs)
            user_inv_ids = {i.investigation_id for i in user_invs}
            total_evidence = sum(1 for e in self._evidence.values() if e.investigation_id in user_inv_ids)

            sorted_invs = sorted(user_invs, key=lambda x: x.updated_at, reverse=True)[:5]
            recent_activities = [a for a in self._activity if a.actor_user_id == owner_user_id]
            recent_activities.sort(key=lambda x: x.occurred_at, reverse=True)

            return {
                "active_investigations_count": active_count,
                "draft_investigations_count": draft_count,
                "completed_investigations_count": completed_count,
                "archived_investigations_count": archived_count,
                "total_notes_count": total_notes,
                "total_sources_count": total_sources,
                "total_evidence_count": total_evidence,
                "recent_investigations": [copy.deepcopy(x) for x in sorted_invs],
                "recent_activities": [copy.deepcopy(x) for x in recent_activities[:10]],
            }

    # -----------------------------------------------------------------------
    # Stage 105 Candidate Seeding & Candidate Management
    # -----------------------------------------------------------------------
    def _seed_initial_evidence_candidates(self):
        """Pre-populate candidate evidence snippets from parsed canonical documents."""
        for doc in self._documents.values():
            # Avoid duplicate seeding for alias keys
            if doc.document_id in self._documents and doc.source_reference_id in self._documents:
                if self._documents[doc.document_id] is not doc:
                    continue
            cands = extract_evidence_candidates_from_document(doc, limit=8)
            for c in cands:
                self._candidates[c.candidate_id] = c

    # -----------------------------------------------------------------------
    # Stage 105 Research Source Discovery
    # -----------------------------------------------------------------------
    def discover_sources(
        self,
        text_query: Optional[str] = None,
        entity_ids: Optional[List[str]] = None,
        instrument_ids: Optional[List[str]] = None,
        source_type_ids: Optional[List[ResearchSourceType]] = None,
        publisher_ids: Optional[List[str]] = None,
        filing_types: Optional[List[str]] = None,
        reporting_period_range: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        availability_statuses: Optional[List[SourceAvailabilityStatus]] = None,
        search_mode: SearchMode = SearchMode.KEYWORD,
        sort_by: str = "RELEVANCE",
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> Tuple[List[ResearchSearchHit], int, Optional[str], Dict]:
        """Multi-facet research source discovery and ranking across canonical financial sources."""
        with self._lock:
            # Deduplicate canonical sources
            seen_ids = set()
            all_sources: List[ResearchSourceReference] = []
            for s in self._sources.values():
                if s.source_reference_id not in seen_ids:
                    seen_ids.add(s.source_reference_id)
                    all_sources.append(s)

            filtered_hits: List[Tuple[ResearchSourceReference, float, str, List[Dict]]] = []

            q_clean = (text_query or "").strip().lower()

            for src in all_sources:
                # 1. Entity Filter
                if entity_ids:
                    src_ent = (src.canonical_entity_id or "").upper()
                    if not any(e.upper() == src_ent for e in entity_ids):
                        continue

                # 2. Source Type Filter
                if source_type_ids:
                    if src.source_type not in source_type_ids:
                        continue

                # 3. Publisher Filter
                if publisher_ids:
                    src_pub = (src.publisher_id or "").lower()
                    if not any(p.lower() in src_pub for p in publisher_ids):
                        continue

                # 4. Filing Type Filter (e.g. "10-K", "10-Q")
                if filing_types:
                    src_title_upper = src.source_title.upper()
                    src_form = (src.provenance.get("form_type") or "").upper()
                    if not any(ft.upper() in src_title_upper or ft.upper() == src_form for ft in filing_types):
                        continue

                # 5. Availability Status Filter
                if availability_statuses:
                    if src.availability_status not in availability_statuses:
                        continue

                # 6. Reporting Period Filter
                if reporting_period_range:
                    src_period = (src.reporting_period or "").upper()
                    if reporting_period_range.upper() not in src_period:
                        continue

                # 7. Date Filter
                if date_from and src.published_at:
                    try:
                        df = datetime.datetime.fromisoformat(date_from.replace("Z", "+00:00"))
                        if src.published_at < df:
                            continue
                    except Exception:
                        pass
                if date_to and src.published_at:
                    try:
                        dt = datetime.datetime.fromisoformat(date_to.replace("Z", "+00:00"))
                        if src.published_at > dt:
                            continue
                    except Exception:
                        pass

                # 8. Text Match & Scoring
                score = 1.0
                snippet = ""
                matched_spans: List[Dict] = []

                if q_clean:
                    title_lower = src.source_title.lower()
                    ent_lower = (src.canonical_entity_id or "").lower()
                    period_lower = (src.reporting_period or "").lower()
                    pub_lower = (src.publisher_id or "").lower()

                    # Exact matches
                    if q_clean == ent_lower:
                        score = 2.0
                        snippet = f"Canonical issuer symbol: {src.canonical_entity_id}"
                    elif q_clean in title_lower:
                        score = 1.8
                        idx = title_lower.find(q_clean)
                        snippet = src.source_title[max(0, idx - 30):min(len(src.source_title), idx + len(q_clean) + 40)]
                    elif q_clean in period_lower:
                        score = 1.5
                        snippet = f"Reporting period: {src.reporting_period}"
                    elif q_clean in pub_lower:
                        score = 1.4
                        snippet = f"Publisher: {src.publisher_id}"
                    else:
                        # Search in associated document text if available
                        doc = None
                        if src.canonical_document_id and src.canonical_document_id in self._documents:
                            doc = self._documents[src.canonical_document_id]
                        elif src.source_reference_id in self._documents:
                            doc = self._documents[src.source_reference_id]

                        if doc:
                            in_doc_hits = search_within_document(doc, q_clean, limit=2)
                            if in_doc_hits:
                                score = 1.2
                                snippet = in_doc_hits[0].snippet
                                matched_spans = [
                                    {
                                        "span_id": h.span_id,
                                        "section_heading": h.section_heading,
                                        "page_number": h.page_number,
                                    }
                                    for h in in_doc_hits
                                ]
                            else:
                                continue
                        else:
                            continue
                else:
                    snippet = src.source_title

                filtered_hits.append((src, score, snippet, matched_spans))

            # Sort results
            if sort_by == "DATE_DESC":
                filtered_hits.sort(key=lambda x: x[0].published_at or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), reverse=True)
            elif sort_by == "DATE_ASC":
                filtered_hits.sort(key=lambda x: x[0].published_at or datetime.datetime.max.replace(tzinfo=datetime.timezone.utc))
            elif sort_by == "TITLE":
                filtered_hits.sort(key=lambda x: x[0].source_title.lower())
            else:  # RELEVANCE
                filtered_hits.sort(key=lambda x: (x[1], x[0].published_at or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)), reverse=True)

            total_count = len(filtered_hits)

            # Pagination
            start_idx = 0
            if cursor:
                try:
                    start_idx = int(cursor)
                except ValueError:
                    start_idx = 0

            page_slice = filtered_hits[start_idx : start_idx + limit]
            next_cursor = str(start_idx + limit) if (start_idx + limit) < total_count else None

            hit_dtos = [
                ResearchSearchHit(
                    hit_id=f"hit-{src.source_reference_id}-{idx}",
                    source_reference_id=src.source_reference_id,
                    canonical_document_id=src.canonical_document_id,
                    canonical_entity_id=src.canonical_entity_id,
                    source_type=src.source_type,
                    source_title=src.source_title,
                    publisher_id=src.publisher_id,
                    published_at=src.published_at,
                    reporting_period=src.reporting_period,
                    matched_snippet=snip,
                    matched_spans=spans,
                    score=sc,
                    availability_status=src.availability_status,
                    rights_policy=src.rights_policy,
                )
                for idx, (src, sc, snip, spans) in enumerate(page_slice)
            ]

            summary = {
                "text_query": text_query,
                "applied_filters_count": sum(bool(x) for x in [entity_ids, source_type_ids, publisher_ids, filing_types, reporting_period_range, date_from, date_to]),
                "total_matched": total_count,
            }

            return hit_dtos, total_count, next_cursor, summary

    # -----------------------------------------------------------------------
    # Stage 105 Source Types Taxonomy
    # -----------------------------------------------------------------------
    def get_source_types(self) -> List[Dict]:
        """Return taxonomic descriptions and rights policies of supported research sources."""
        return [
            {
                "source_type": ResearchSourceType.ANNUAL_REPORT,
                "display_name": "Annual Report (Form 10-K / 20-F)",
                "description": "Audited comprehensive financial reporting and regulatory disclosures for full fiscal year.",
                "rights_classification": "PUBLIC_DOMAIN_REGULATORY",
                "is_searchable": True,
            },
            {
                "source_type": ResearchSourceType.QUARTERLY_REPORT,
                "display_name": "Quarterly Report (Form 10-Q)",
                "description": "Unaudited quarterly financial statements and MD&A progress updates.",
                "rights_classification": "PUBLIC_DOMAIN_REGULATORY",
                "is_searchable": True,
            },
            {
                "source_type": ResearchSourceType.REGULATORY_FILING,
                "display_name": "Current Regulatory Report (Form 8-K / Disclosures)",
                "description": "Material corporate events, leadership appointments, earnings presentations, and governance filings.",
                "rights_classification": "PUBLIC_DOMAIN_REGULATORY",
                "is_searchable": True,
            },
            {
                "source_type": ResearchSourceType.FINANCIAL_STATEMENT,
                "display_name": "Canonical Financial Statements",
                "description": "Standardized Income Statement, Balance Sheet, and Cash Flow metrics derived from XBRL filings.",
                "rights_classification": "LICENSED_FUNDAMENTAL_DATA",
                "is_searchable": True,
            },
            {
                "source_type": ResearchSourceType.ECONOMIC_RELEASE,
                "display_name": "Official Economic Release",
                "description": "Macroeconomic indicator publications (CPI, PPI, Employment, Central Bank Policy Decisions).",
                "rights_classification": "PUBLIC_DOMAIN_GOV",
                "is_searchable": True,
            },
            {
                "source_type": ResearchSourceType.NEWS_ARTICLE,
                "display_name": "Verified Financial News",
                "description": "Licensed financial news reporting from Bloomberg, Reuters, and verified financial wire services.",
                "rights_classification": "LICENSED_EXCERPT_ONLY",
                "is_searchable": True,
            },
            {
                "source_type": ResearchSourceType.MARKET_DATASET,
                "display_name": "Market & Instrument Dataset",
                "description": "Exchange-reported trade volumes, price histories, and security master references.",
                "rights_classification": "LICENSED_MARKET_DATA",
                "is_searchable": True,
            },
        ]

    # -----------------------------------------------------------------------
    # Stage 105 Document Inspection, Outline, Sections & Tables
    # -----------------------------------------------------------------------
    def _resolve_document(self, doc_id_or_src_id: str) -> Optional[ParsedDocumentData]:
        """Resolve a ParsedDocumentData by document_id or source_reference_id."""
        with self._lock:
            if doc_id_or_src_id in self._documents:
                return self._documents[doc_id_or_src_id]
            # Try finding by source_reference_id
            for d in self._documents.values():
                if d.source_reference_id == doc_id_or_src_id:
                    return d
            return None

    def get_document_metadata(self, doc_id: str) -> Optional[ParsedDocumentData]:
        doc = self._resolve_document(doc_id)
        return copy.deepcopy(doc) if doc else None

    def get_document_processing_status(self, doc_id: str) -> Optional[ResearchDocumentProcessingRecord]:
        doc = self._resolve_document(doc_id)
        if not doc or not doc.processing_record:
            return None
        return copy.deepcopy(doc.processing_record)

    def get_document_sections(self, doc_id: str) -> List[ResearchDocumentSection]:
        doc = self._resolve_document(doc_id)
        if not doc:
            raise ResearchDocumentNotFoundError(f"Document '{doc_id}' not found.")
        return [copy.deepcopy(s) for s in doc.sections]

    def get_document_section(self, doc_id: str, section_id: str) -> ResearchDocumentSection:
        doc = self._resolve_document(doc_id)
        if not doc:
            raise ResearchDocumentNotFoundError(f"Document '{doc_id}' not found.")
        for s in doc.sections:
            if s.section_id == section_id:
                return copy.deepcopy(s)
        raise ResearchDocumentSectionNotFoundError(f"Section '{section_id}' not found in document '{doc_id}'.")

    def search_document(
        self,
        doc_id: str,
        query: str,
        section_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[DocumentSearchHit]:
        doc = self._resolve_document(doc_id)
        if not doc:
            raise ResearchDocumentNotFoundError(f"Document '{doc_id}' not found.")
        hits = search_within_document(doc, query=query, section_id=section_id, limit=limit)
        return hits

    def get_document_tables(self, doc_id: str) -> List[ResearchDocumentTable]:
        doc = self._resolve_document(doc_id)
        if not doc:
            raise ResearchDocumentNotFoundError(f"Document '{doc_id}' not found.")
        return [copy.deepcopy(t) for t in doc.tables]

    def get_document_table(self, doc_id: str, table_id: str) -> ResearchDocumentTable:
        doc = self._resolve_document(doc_id)
        if not doc:
            raise ResearchDocumentNotFoundError(f"Document '{doc_id}' not found.")
        for t in doc.tables:
            if t.table_id == table_id:
                return copy.deepcopy(t)
        raise ResearchDocumentTableNotFoundError(f"Table '{table_id}' not found in document '{doc_id}'.")

    # -----------------------------------------------------------------------
    # Stage 105 Evidence Candidates & Location Validation
    # -----------------------------------------------------------------------
    def get_evidence_candidates(
        self,
        investigation_id: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[ResearchEvidenceCandidate]:
        with self._lock:
            items = list(self._candidates.values())
            if source_id:
                items = [c for c in items if c.source_reference_id == source_id or c.canonical_document_id == source_id]
            return [copy.deepcopy(c) for c in items[:limit]]

    def resolve_evidence_location(
        self,
        source_reference_id: str,
        location_type: EvidenceLocationType,
        location_reference: str,
        page_number: Optional[int] = None,
        section_name: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[str], Optional[str]]:
        doc = self._resolve_document(source_reference_id)
        if not doc:
            return (
                False,
                location_reference,
                None,
                f"Source document '{source_reference_id}' is unavailable or has not been processed.",
            )
        return resolve_source_location_anchor(
            doc=doc,
            location_type=location_type,
            location_reference=location_reference,
            page_number=page_number,
            section_name=section_name,
        )

    def convert_evidence_candidate(
        self,
        candidate_id: str,
        investigation_id: str,
        actor_user_id: str,
        claim_id: Optional[str] = None,
        relationship_type: Optional[str] = None,
    ) -> ResearchEvidence:
        with self._lock:
            if candidate_id not in self._candidates:
                raise ResearchEvidenceCandidateNotFoundError(f"Evidence candidate '{candidate_id}' not found.")

            cand = self._candidates[candidate_id]
            if not self.get_investigation(investigation_id):
                raise ResearchInvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")

            # Auto-link source to investigation if not already present
            linked_sources = self._source_links.get(investigation_id, [])
            if cand.source_reference_id not in linked_sources:
                linked_sources.append(cand.source_reference_id)
                self._source_links[investigation_id] = linked_sources

            # Create persistent ResearchEvidence
            ev_id = f"ev-{uuid.uuid4().hex[:10]}"
            ev = ResearchEvidence(
                evidence_id=ev_id,
                investigation_id=investigation_id,
                source_reference_id=cand.source_reference_id,
                canonical_source_entity_id=cand.canonical_entity_id,
                evidence_type=cand.evidence_type,
                source_location_type=EvidenceLocationType.SECTION if cand.section_heading else EvidenceLocationType.PAGE,
                source_location_reference=cand.location_reference,
                page_number=cand.page_number,
                section_name=cand.section_heading,
                source_revision=cand.source_revision or "1",
                observation_time=datetime.datetime.now(datetime.timezone.utc),
                allowed_excerpt=cand.extracted_text,
                linked_claim_ids=[claim_id] if claim_id else [],
                created_by=actor_user_id,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                availability_status=SourceAvailabilityStatus.AVAILABLE,
                provenance=cand.provenance,
            )
            self._evidence[ev_id] = ev

            # Link Claim if supplied
            if claim_id:
                from atlas.research.enums import ClaimEvidenceRelationship
                rel_enum = ClaimEvidenceRelationship.SUPPORTS
                if relationship_type:
                    try:
                        rel_enum = ClaimEvidenceRelationship(relationship_type)
                    except ValueError:
                        pass
                self.link_evidence_to_claim(claim_id=claim_id, evidence_id=ev_id, relationship_type=rel_enum, linked_by=actor_user_id)

            # Log activity
            self.record_activity(
                investigation_id=investigation_id,
                action_type=ResearchActivityAction.EVIDENCE_CANDIDATE_EXTRACTED,
                actor_user_id=actor_user_id,
                object_type="EVIDENCE",
                object_id=ev_id,
                details={
                    "candidate_id": candidate_id,
                    "source_reference_id": cand.source_reference_id,
                    "location_reference": cand.location_reference,
                },
            )

            # Remove from candidate pool once converted
            del self._candidates[candidate_id]

            return copy.deepcopy(ev)

    # -----------------------------------------------------------------------
    # Stage 105 Two-Document & Financial Fact Comparison
    # -----------------------------------------------------------------------
    def compare_documents(
        self,
        left_doc_id: str,
        right_doc_id: str,
        mode: DocumentComparisonMode = DocumentComparisonMode.FULL_TEXT,
    ) -> DocumentComparisonResult:
        with self._lock:
            left_doc = self._resolve_document(left_doc_id)
            if not left_doc:
                raise ResearchDocumentNotFoundError(f"Left document '{left_doc_id}' not found.")
            right_doc = self._resolve_document(right_doc_id)
            if not right_doc:
                raise ResearchDocumentNotFoundError(f"Right document '{right_doc_id}' not found.")

            res = compute_document_diff(left_doc, right_doc, mode=mode)
            return res

    def compare_financial_facts(
        self,
        entity_id: str,
        left_period: str,
        right_period: str,
        concepts: Optional[List[str]] = None,
    ) -> List[FinancialFactComparison]:
        """Compare financial statement facts for an issuer across two reporting periods."""
        with self._lock:
            # Locate parsed filings for this issuer matching left_period and right_period
            issuer_docs = [
                d for d in self._documents.values()
                if (d.canonical_entity_id or "").upper() == entity_id.upper()
            ]

            left_norm = left_period.replace(" ", "").replace("-", "").upper()
            right_norm = right_period.replace(" ", "").replace("-", "").upper()

            left_doc = next((d for d in issuer_docs if (d.reporting_period or "").replace(" ", "").replace("-", "").upper() == left_norm), None)
            right_doc = next((d for d in issuer_docs if (d.reporting_period or "").replace(" ", "").replace("-", "").upper() == right_norm), None)

            if not left_doc or not right_doc:
                raise ResearchComparisonIncompatibleError(
                    f"Could not locate comparable filings for {entity_id} across {left_period} and {right_period}."
                )

            diff_result = compute_document_diff(left_doc, right_doc, mode=DocumentComparisonMode.FINANCIAL_TABLES)
            facts = diff_result.financial_fact_diffs

            if concepts:
                concepts_lower = [c.lower() for c in concepts]
                facts = [f for f in facts if any(c in f.fact_key.lower() or c in f.label.lower() for c in concepts_lower)]

            return facts
