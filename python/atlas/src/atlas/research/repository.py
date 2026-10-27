"""Research Repositories for Institutional Financial Research Platform (Stage 104)."""

import copy
import datetime
import threading
import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

# Keep legacy imports for backwards compatibility
from atlas.entities.models import Entity
from atlas.research.analysis.calculations import get_supported_analysis_types
from atlas.research.analysis.engine import ResearchAnalysisEngine
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
    HypothesisTestCriteria,
    ResearchActivity,
    ResearchAnalysis,
    ResearchAnalysisAssumption,
    ResearchAnalysisResult,
    ResearchAnalysisRun,
    ResearchAnalysisSpecification,
    ResearchAnalysisTypeDefinition,
    ResearchCitation,
    ResearchClaim,
    ResearchClaimEvidence,
    ResearchDocumentProcessingRecord,
    ResearchDocumentSection,
    ResearchDocumentTable,
    ResearchEvidence,
    ResearchEvidenceCandidate,
    ResearchFinding,
    ResearchHypothesis,
    ResearchHypothesisEvaluation,
    ResearchInvestigation,
    ResearchInvestmentThesis,
    ResearchNote,
    ResearchNoteRevision,
    ResearchQuestion,
    ResearchReport,
    ResearchReportExport,
    ResearchReportRevision,
    ResearchReportSection,
    ResearchReportVerification,
    ResearchScenario,
    ResearchSearchHit,
    ResearchSourceReference,
    ResearchThesisArgument,
)
from atlas.research.enums import (
    AnalysisExecutionStatus,
    AnalysisFrequency,
    AnalysisInputPolicy,
    AssumptionSourceType,
    DocumentComparisonMode,
    EvidenceLocationType,
    InvestigationLifecycleStatus,
    ReportBlockType,
    ReportLifecycleStatus,
    ReportSectionType,
    ReportSnapshotPolicy,
    ResearchActivityAction,
    ResearchAnalysisType,
    ResearchClaimCategory,
    ResearchEvidenceStatus,
    ResearchFindingReviewStatus,
    ResearchFindingType,
    ResearchHypothesisStatus,
    ResearchNoteStatus,
    ResearchNoteType,
    ResearchQuestionStatus,
    ResearchReportType,
    ResearchSourceType,
    ResearchType,
    SearchMode,
    SourceAvailabilityStatus,
    ThesisArgumentType,
    ThesisLifecycleStatus,
)
from atlas.research.errors import (
    ResearchAnalysisAccessDeniedError,
    ResearchAnalysisNotFoundError,
    ResearchAnalysisRevisionConflictError,
    ResearchAssumptionNotFoundError,
    ResearchClaimNotFoundError,
    ResearchComparisonIncompatibleError,
    ResearchDocumentNotFoundError,
    ResearchDocumentSectionNotFoundError,
    ResearchDocumentTableNotFoundError,
    ResearchEvidenceCandidateNotFoundError,
    ResearchEvidenceNotFoundError,
    ResearchEvidenceSourceMissingError,
    ResearchFindingNotFoundError,
    ResearchFindingRevisionConflictError,
    ResearchHypothesisNotFoundError,
    ResearchInvestigationNotFoundError,
    ResearchInvestigationRevisionConflictError,
    ResearchInvestmentThesisAccessDeniedError,
    ResearchInvestmentThesisNotFoundError,
    ResearchInvestmentThesisRevisionConflictError,
    ResearchNoteNotFoundError,
    ResearchNoteRevisionConflictError,
    ResearchQuestionNotFoundError,
    ResearchReportAccessDeniedError,
    ResearchReportFinalizedImmutableError,
    ResearchReportNotFoundError,
    ResearchReportRevisionConflictError,
    ResearchReportSectionNotFoundError,
    ResearchSourceNotFoundError,
    ResearchThesisArgumentNotFoundError,
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

        # Stage 106 Analysis, Runs, Findings & Hypothesis Stores
        self._analyses: Dict[str, ResearchAnalysis] = {}
        self._analysis_runs: Dict[str, ResearchAnalysisRun] = {}
        self._analysis_results: Dict[str, ResearchAnalysisResult] = {}
        self._findings: Dict[str, ResearchFinding] = {}
        self._hypothesis_evaluations: Dict[str, ResearchHypothesisEvaluation] = {}
        self._assumptions: Dict[str, ResearchAnalysisAssumption] = {}
        self._scenarios: Dict[str, ResearchScenario] = {}

        # Stage 107 Reports, Sections, Theses, Verification & Export Stores
        self._reports: Dict[str, ResearchReport] = {}
        self._report_sections: Dict[str, List[ResearchReportSection]] = {}
        self._report_revisions: Dict[str, List[ResearchReportRevision]] = {}
        self._theses: Dict[str, ResearchInvestmentThesis] = {}
        self._thesis_arguments: Dict[str, List[ResearchThesisArgument]] = {}
        self._verification_runs: Dict[str, List[ResearchReportVerification]] = {}
        self._exports: Dict[str, ResearchReportExport] = {}
        self._export_artifacts: Dict[str, bytes] = {}

        self._seed_baseline_investigations()
        self._seed_initial_evidence_candidates()
        self._seed_baseline_analyses()
        self._seed_baseline_reports()

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
            total_analyses = sum(1 for a in self._analyses.values() if a.owner_user_id == owner_user_id)
            total_findings = sum(1 for f in self._findings.values() if f.author_user_id == owner_user_id)
            total_evaluations = len(self._hypothesis_evaluations)

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
                "total_analyses_count": total_analyses,
                "total_findings_count": total_findings,
                "total_evaluations_count": total_evaluations,
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

    # -----------------------------------------------------------------------
    # Stage 106 — Research Analysis Baseline Seeding
    # -----------------------------------------------------------------------
    def _seed_baseline_analyses(self):
        """Seed verified baseline analyses, runs, findings, and hypothesis evaluations."""
        now = datetime.datetime.now(datetime.timezone.utc)
        user_id = "default-user"

        # 1. Apple Inc. 5-Year Operating & Gross Margin Trajectory (FY2020-FY2024)
        an_id_1 = "an-aapl-margin-trend"
        spec_1 = ResearchAnalysisSpecification(
            analysis_type=ResearchAnalysisType.COMPANY_FINANCIAL_TREND,
            primary_entity_id="AAPL",
            secondary_entity_ids=["MSFT", "NVDA"],
            metric_ids=["operating_income"],
            time_range_start="2020",
            time_range_end="2024",
            frequency=AnalysisFrequency.ANNUAL,
            input_version_policy=AnalysisInputPolicy.PINNED_SOURCE_VERSION,
            currency="USD",
            methodology_version=1,
        )
        an_1 = ResearchAnalysis(
            analysis_id=an_id_1,
            investigation_id="inv-apple-fy24-margins",
            owner_user_id=user_id,
            title="Apple Inc. (AAPL) 5-Year Operating Profit Margin Trajectory (FY2020-FY2024)",
            description="Historical fundamental analysis evaluating operating income and margin consistency across Form 10-K filings from FY2020 through FY2024.",
            analysis_type=ResearchAnalysisType.COMPANY_FINANCIAL_TREND,
            research_objective="Determine whether operating profitability expanded consistently over the last five fiscal years.",
            primary_subject_entity_id="AAPL",
            primary_subject_type="COMPANY",
            secondary_entity_ids=["MSFT", "NVDA"],
            specification=spec_1,
            status=AnalysisExecutionStatus.COMPLETED,
            current_revision=1,
            created_at=now - datetime.timedelta(days=5),
            updated_at=now - datetime.timedelta(hours=1),
            linked_question_ids=["q-aapl-01"],
            linked_hypothesis_ids=["hyp-aapl-01"],
            latest_run_id="run-aapl-margin-01",
            provenance={"created_by": user_id, "source": "ATLAS_RESEARCH_WORKSPACE"},
        )
        self._analyses[an_id_1] = an_1

        # Execute run for an_1
        run_1, res_1 = ResearchAnalysisEngine.execute(an_id_1, "run-aapl-margin-01", spec_1, user_id)
        self._analysis_runs[run_1.run_id] = run_1
        self._analysis_results[run_1.run_id] = res_1

        # 2. Apple vs Mega-Cap Tech Peer Group Operating Margin Benchmarking
        an_id_2 = "an-aapl-peer-benchmark"
        spec_2 = ResearchAnalysisSpecification(
            analysis_type=ResearchAnalysisType.PEER_BENCHMARKING,
            primary_entity_id="AAPL",
            secondary_entity_ids=["MSFT", "GOOGL", "NVDA", "Samsung", "Dell", "HP", "Sony"],
            metric_ids=["profitability.operating_margin"],
            frequency=AnalysisFrequency.ANNUAL,
            input_version_policy=AnalysisInputPolicy.PINNED_SOURCE_VERSION,
            parameters={"peer_group_id": "peer-group-big-tech"},
            methodology_version=1,
        )
        an_2 = ResearchAnalysis(
            analysis_id=an_id_2,
            investigation_id="inv-apple-fy24-margins",
            owner_user_id=user_id,
            title="Apple Inc. vs Global Tech Platforms Operating Margin Benchmarking",
            description="Cross-sectional comparative benchmarking evaluating Apple's operating margin relative to verified Stage 87 peer group medians and bounds.",
            analysis_type=ResearchAnalysisType.PEER_BENCHMARKING,
            research_objective="Assess Apple's operating margin competitiveness against hardware and enterprise platform competitors.",
            primary_subject_entity_id="AAPL",
            primary_subject_type="COMPANY",
            secondary_entity_ids=["MSFT", "GOOGL", "NVDA", "Samsung", "Dell", "HP", "Sony"],
            specification=spec_2,
            status=AnalysisExecutionStatus.COMPLETED,
            current_revision=1,
            created_at=now - datetime.timedelta(days=4),
            updated_at=now - datetime.timedelta(hours=2),
            linked_question_ids=["q-aapl-01"],
            linked_hypothesis_ids=["hyp-aapl-01"],
            latest_run_id="run-aapl-peer-01",
            provenance={"created_by": user_id, "source": "ATLAS_RESEARCH_WORKSPACE"},
        )
        self._analyses[an_id_2] = an_2

        run_2, res_2 = ResearchAnalysisEngine.execute(an_id_2, "run-aapl-peer-01", spec_2, user_id)
        self._analysis_runs[run_2.run_id] = run_2
        self._analysis_results[run_2.run_id] = res_2

        # 3. Macroeconomic CPI vs Federal Funds Policy Rate Alignment
        an_id_3 = "an-macro-rate-inflation"
        spec_3 = ResearchAnalysisSpecification(
            analysis_type=ResearchAnalysisType.MACROECONOMIC_TIME_SERIES,
            primary_entity_id="US",
            secondary_entity_ids=[],
            metric_ids=["US_CPI", "US_FED_FUNDS"],
            time_range_start="2020",
            time_range_end="2024",
            frequency=AnalysisFrequency.ANNUAL,
            methodology_version=1,
        )
        an_3 = ResearchAnalysis(
            analysis_id=an_id_3,
            investigation_id=None,
            owner_user_id=user_id,
            title="United States Consumer Price Index (CPI) vs Federal Funds Rate Alignment (2020-2024)",
            description="Macroeconomic research series analyzing historical inflation shocks and monetary tightening cycles with release date watermarking.",
            analysis_type=ResearchAnalysisType.MACROECONOMIC_TIME_SERIES,
            research_objective="Examine the historical lag between inflation spikes and Federal Reserve monetary policy rate increases.",
            primary_subject_entity_id="US",
            primary_subject_type="ECONOMIC_ENTITY",
            secondary_entity_ids=[],
            specification=spec_3,
            status=AnalysisExecutionStatus.COMPLETED,
            current_revision=1,
            created_at=now - datetime.timedelta(days=3),
            updated_at=now - datetime.timedelta(hours=3),
            latest_run_id="run-macro-cpi-01",
            provenance={"created_by": user_id, "source": "ATLAS_MACRO_SERIES"},
        )
        self._analyses[an_id_3] = an_3

        run_3, res_3 = ResearchAnalysisEngine.execute(an_id_3, "run-macro-cpi-01", spec_3, user_id)
        self._analysis_runs[run_3.run_id] = run_3
        self._analysis_results[run_3.run_id] = res_3

        # 4. Hypothesis Evaluation for hyp-aapl-01
        hyp_criteria = HypothesisTestCriteria(
            metric_id="operating_income",
            operator="GTE",
            threshold_value=60000.0,
            required_periods_count=5,
        )
        hyp_eval = ResearchAnalysisEngine.evaluate_hypothesis(
            evaluation_id="eval-aapl-hyp-01",
            hypothesis_id="hyp-aapl-01",
            run=run_1,
            result=res_1,
            criteria=hyp_criteria,
            user_id=user_id,
        )
        self._hypothesis_evaluations[hyp_eval.evaluation_id] = hyp_eval

        # 5. Baseline Research Findings
        f1 = ResearchFinding(
            finding_id="find-aapl-margin-01",
            investigation_id="inv-apple-fy24-margins",
            analysis_id=an_id_1,
            analysis_run_id="run-aapl-margin-01",
            author_user_id=user_id,
            finding_type=ResearchFindingType.CALCULATED_RESULT,
            statement="Apple Inc. operating income increased from $66.29B in FY2020 to $123.18B in FY2024, representing an overall 5-year CAGR of 16.75% with operating margin expanding from 24.15% to 31.50%.",
            methodology_description="Deterministic period-over-period delta and compound annual growth rate calculation over Form 10-K reported Item 8 financial statement values.",
            supporting_evidence_ids=["ev-aapl-opinc-01", "ev-aapl-10k-risk"],
            contradicting_evidence_ids=[],
            calculated_result_references={"cagr": 16.75, "fy20_val": 66288.0, "fy24_val": 123184.0},
            limitations=[
                "Calculated over annual consolidated reported periods; does not include quarterly seasonality.",
                "Subject to future FASB accounting standard updates or corporate restructuring.",
            ],
            review_status=ResearchFindingReviewStatus.REVIEWED,
            revision=1,
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=2),
        )
        self._findings[f1.finding_id] = f1

        f2 = ResearchFinding(
            finding_id="find-aapl-peers-01",
            investigation_id="inv-apple-fy24-margins",
            analysis_id=an_id_2,
            analysis_run_id="run-aapl-peer-01",
            author_user_id=user_id,
            finding_type=ResearchFindingType.STATISTICAL_OBSERVATION,
            statement="Apple FY2024 operating profit margin of 31.50% substantially exceeds the Stage 87 technology peer group median of 20.70%, placing Apple in the 75th percentile of comparable global platforms.",
            methodology_description="Cross-sectional quartile and median statistical derivation across 8 verified peer companies.",
            supporting_evidence_ids=["ev-aapl-opinc-01"],
            contradicting_evidence_ids=[],
            calculated_result_references={"subject_margin": 31.50, "peer_median": 20.70, "peer_q3": 37.28},
            limitations=[
                "Peer comparisons include companies reporting under U.S. GAAP and IFRS.",
                "Sample size N=8 technology companies.",
            ],
            review_status=ResearchFindingReviewStatus.READY_FOR_REVIEW,
            revision=1,
            created_at=now - datetime.timedelta(days=1),
            updated_at=now - datetime.timedelta(hours=1),
        )
        self._findings[f2.finding_id] = f2

        # 6. Baseline Assumptions for Sensitivity Testing
        assump_1 = ResearchAnalysisAssumption(
            assumption_id="assump-aapl-rev-01",
            analysis_id=an_id_1,
            label="Baseline Revenue Growth Rate",
            parameter_id="revenue_growth_rate",
            value=5.0,
            unit="%",
            source_type=AssumptionSourceType.ANALYST_ASSUMED,
            source_reference_id=None,
            analyst_note="Illustrative baseline revenue expansion assumption based on mid-single digit Services growth.",
            created_at=now - datetime.timedelta(days=2),
        )
        assump_2 = ResearchAnalysisAssumption(
            assumption_id="assump-aapl-margin-01",
            analysis_id=an_id_1,
            label="Target Operating Profit Margin",
            parameter_id="target_operating_margin",
            value=31.5,
            unit="%",
            source_type=AssumptionSourceType.SOURCE_REPORTED,
            source_reference_id="src-filing-aapl-10k-2024",
            analyst_note="Anchored to FY2024 Form 10-K reported operating margin baseline.",
            created_at=now - datetime.timedelta(days=2),
        )
        self._assumptions[assump_1.assumption_id] = assump_1
        self._assumptions[assump_2.assumption_id] = assump_2

    def _log_activity(
        self,
        action: ResearchActivityAction,
        entity_id: str,
        entity_type: str,
        user_id: str,
        details: Dict,
        investigation_id: Optional[str] = None,
    ):
        """Helper to log research activity for stage 106 operations."""
        self.record_activity(
            investigation_id=investigation_id or "inv-global-research",
            action_type=action,
            actor_user_id=user_id,
            object_type=entity_type,
            object_id=entity_id,
            details=details,
        )

    def list_analysis_types(self) -> List[ResearchAnalysisTypeDefinition]:
        """Returns supported analysis types catalog."""
        return get_supported_analysis_types()

    def get_analysis_type(self, type_id: ResearchAnalysisType) -> Optional[ResearchAnalysisTypeDefinition]:
        """Gets metadata for a specific analysis type."""
        for t in get_supported_analysis_types():
            if t.type_id == type_id:
                return t
        return None

    def list_analyses(
        self,
        user_id: str,
        investigation_id: Optional[str] = None,
        analysis_type: Optional[ResearchAnalysisType] = None,
        subject_id: Optional[str] = None,
        status: Optional[AnalysisExecutionStatus] = None,
    ) -> List[ResearchAnalysis]:
        """Lists user-owned research analyses with optional facet filters."""
        with self._lock:
            res: List[ResearchAnalysis] = []
            for an in self._analyses.values():
                # Enforce RLS user ownership isolation (default-user can access seeded)
                if an.owner_user_id != user_id and an.owner_user_id != "default-user":
                    continue
                if investigation_id and an.investigation_id != investigation_id:
                    continue
                if analysis_type and an.analysis_type != analysis_type:
                    continue
                if subject_id and (an.primary_subject_entity_id or "").upper() != subject_id.upper():
                    continue
                if status and an.status != status:
                    continue
                res.append(copy.deepcopy(an))
            return sorted(res, key=lambda a: a.updated_at, reverse=True)

    def create_analysis(self, analysis: ResearchAnalysis) -> ResearchAnalysis:
        """Persists a new user-owned research analysis."""
        with self._lock:
            self._analyses[analysis.analysis_id] = copy.deepcopy(analysis)
            self._log_activity(
                action=ResearchActivityAction.ANALYSIS_CREATED,
                entity_id=analysis.analysis_id,
                entity_type="ANALYSIS",
                user_id=analysis.owner_user_id,
                details={"title": analysis.title, "type": analysis.analysis_type.value},
            )
            return copy.deepcopy(analysis)

    def get_analysis(self, analysis_id: str) -> Optional[ResearchAnalysis]:
        """Retrieves a research analysis by canonical identifier."""
        with self._lock:
            an = self._analyses.get(analysis_id)
            return copy.deepcopy(an) if an else None

    def update_analysis(
        self,
        analysis_id: str,
        expected_revision: int,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        research_objective: Optional[str] = None,
        specification: Optional[ResearchAnalysisSpecification] = None,
        linked_questions: Optional[List[str]] = None,
        linked_hypotheses: Optional[List[str]] = None,
        status: Optional[AnalysisExecutionStatus] = None,
    ) -> ResearchAnalysis:
        """Updates an analysis with optimistic concurrency revision checking."""
        with self._lock:
            an = self._analyses.get(analysis_id)
            if not an:
                raise ResearchAnalysisNotFoundError(f"Analysis '{analysis_id}' not found.")
            if an.owner_user_id != user_id and an.owner_user_id != "default-user":
                raise ResearchAnalysisAccessDeniedError(f"Access denied to analysis '{analysis_id}'.")
            if an.current_revision != expected_revision:
                raise ResearchAnalysisRevisionConflictError(
                    f"Stale analysis write: current revision is {an.current_revision}, expected {expected_revision}."
                )

            now = datetime.datetime.now(datetime.timezone.utc)
            if title is not None:
                an.title = title
            if description is not None:
                an.description = description
            if research_objective is not None:
                an.research_objective = research_objective
            if specification is not None:
                an.specification = specification
            if linked_questions is not None:
                an.linked_question_ids = linked_questions
            if linked_hypotheses is not None:
                an.linked_hypothesis_ids = linked_hypotheses
            if status is not None:
                an.status = status

            an.current_revision += 1
            an.updated_at = now

            self._log_activity(
                action=ResearchActivityAction.ANALYSIS_UPDATED,
                entity_id=an.analysis_id,
                entity_type="ANALYSIS",
                user_id=user_id,
                details={"revision": an.current_revision, "title": an.title},
            )
            return copy.deepcopy(an)

    def delete_analysis(self, analysis_id: str, user_id: str) -> bool:
        """Deletes or archives an analysis and linked runs under policy."""
        with self._lock:
            an = self._analyses.get(analysis_id)
            if not an:
                raise ResearchAnalysisNotFoundError(f"Analysis '{analysis_id}' not found.")
            if an.owner_user_id != user_id and an.owner_user_id != "default-user":
                raise ResearchAnalysisAccessDeniedError(f"Access denied to analysis '{analysis_id}'.")

            del self._analyses[analysis_id]
            self._log_activity(
                action=ResearchActivityAction.ANALYSIS_DELETED,
                entity_id=analysis_id,
                entity_type="ANALYSIS",
                user_id=user_id,
                details={"deleted_analysis_id": analysis_id},
            )
            return True

    def duplicate_analysis(
        self,
        analysis_id: str,
        new_title: Optional[str],
        user_id: str,
    ) -> ResearchAnalysis:
        """Duplicates an existing analysis within user research scope."""
        with self._lock:
            an = self._analyses.get(analysis_id)
            if not an:
                raise ResearchAnalysisNotFoundError(f"Analysis '{analysis_id}' not found.")
            now = datetime.datetime.now(datetime.timezone.utc)
            new_id = f"an-{uuid.uuid4().hex[:12]}"
            dup_title = new_title or f"{an.title} (Copy)"

            new_an = ResearchAnalysis(
                analysis_id=new_id,
                investigation_id=an.investigation_id,
                owner_user_id=user_id,
                title=dup_title,
                description=an.description,
                analysis_type=an.analysis_type,
                research_objective=an.research_objective,
                primary_subject_entity_id=an.primary_subject_entity_id,
                primary_subject_type=an.primary_subject_type,
                secondary_entity_ids=list(an.secondary_entity_ids),
                specification=copy.deepcopy(an.specification),
                status=AnalysisExecutionStatus.CONFIGURED,
                current_revision=1,
                created_at=now,
                updated_at=now,
                linked_question_ids=list(an.linked_question_ids),
                linked_hypothesis_ids=list(an.linked_hypothesis_ids),
                latest_run_id=None,
                provenance={"duplicated_from": analysis_id, "created_by": user_id},
            )
            self._analyses[new_id] = new_an
            return copy.deepcopy(new_an)

    # -----------------------------------------------------------------------
    # Stage 106 — Run & Result Persistence
    # -----------------------------------------------------------------------
    def save_analysis_run(self, run: ResearchAnalysisRun, result: ResearchAnalysisResult):
        """Persists an immutable analysis run and associated results."""
        with self._lock:
            self._analysis_runs[run.run_id] = copy.deepcopy(run)
            self._analysis_results[run.run_id] = copy.deepcopy(result)
            # Update latest_run_id on parent analysis
            if run.analysis_id in self._analyses:
                an = self._analyses[run.analysis_id]
                an.latest_run_id = run.run_id
                an.status = AnalysisExecutionStatus.COMPLETED
                an.updated_at = datetime.datetime.now(datetime.timezone.utc)

            self._log_activity(
                action=ResearchActivityAction.ANALYSIS_RUN_EXECUTED,
                entity_id=run.run_id,
                entity_type="ANALYSIS_RUN",
                user_id=run.owner_user_id,
                details={
                    "analysis_id": run.analysis_id,
                    "observations_count": run.observations_count,
                    "status": run.execution_status.value,
                },
            )

    def get_analysis_run(self, run_id: str) -> Optional[ResearchAnalysisRun]:
        """Retrieves an analysis run record by ID."""
        with self._lock:
            run = self._analysis_runs.get(run_id)
            return copy.deepcopy(run) if run else None

    def get_analysis_run_result(self, run_id: str) -> Optional[ResearchAnalysisResult]:
        """Retrieves analytical results for an execution run."""
        with self._lock:
            res = self._analysis_results.get(run_id)
            return copy.deepcopy(res) if res else None

    def list_analysis_runs(self, analysis_id: str) -> List[ResearchAnalysisRun]:
        """Lists historical execution runs for an analysis in descending order."""
        with self._lock:
            runs = [r for r in self._analysis_runs.values() if r.analysis_id == analysis_id]
            return sorted(copy.deepcopy(runs), key=lambda r: r.started_at, reverse=True)

    # -----------------------------------------------------------------------
    # Stage 106 — Hypothesis Evaluation Repository Methods
    # -----------------------------------------------------------------------
    def save_hypothesis_evaluation(self, eval_record: ResearchHypothesisEvaluation):
        """Persists a deterministic hypothesis evaluation result."""
        with self._lock:
            self._hypothesis_evaluations[eval_record.evaluation_id] = copy.deepcopy(eval_record)
            self._log_activity(
                action=ResearchActivityAction.HYPOTHESIS_EVALUATED,
                entity_id=eval_record.evaluation_id,
                entity_type="HYPOTHESIS_EVALUATION",
                user_id=eval_record.author_user_id,
                details={
                    "hypothesis_id": eval_record.hypothesis_id,
                    "result_status": eval_record.result_status.value,
                },
            )

    def get_hypothesis_evaluation(self, evaluation_id: str) -> Optional[ResearchHypothesisEvaluation]:
        """Retrieves an evaluation record by ID."""
        with self._lock:
            ev = self._hypothesis_evaluations.get(evaluation_id)
            return copy.deepcopy(ev) if ev else None

    def list_hypothesis_evaluations(self, hypothesis_id: str) -> List[ResearchHypothesisEvaluation]:
        """Lists evaluation history for an analyst hypothesis."""
        with self._lock:
            evals = [e for e in self._hypothesis_evaluations.values() if e.hypothesis_id == hypothesis_id]
            return sorted(copy.deepcopy(evals), key=lambda e: e.created_at, reverse=True)

    # -----------------------------------------------------------------------
    # Stage 106 — Research Findings Repository Methods
    # -----------------------------------------------------------------------
    def create_finding(self, finding: ResearchFinding) -> ResearchFinding:
        """Persists a new evidence-grounded research finding."""
        with self._lock:
            self._findings[finding.finding_id] = copy.deepcopy(finding)
            self._log_activity(
                action=ResearchActivityAction.FINDING_CREATED,
                entity_id=finding.finding_id,
                entity_type="FINDING",
                user_id=finding.author_user_id,
                details={
                    "analysis_id": finding.analysis_id,
                    "type": finding.finding_type.value,
                    "statement": finding.statement[:100],
                },
            )
            return copy.deepcopy(finding)

    def get_finding(self, finding_id: str) -> Optional[ResearchFinding]:
        """Retrieves a research finding by ID."""
        with self._lock:
            f = self._findings.get(finding_id)
            return copy.deepcopy(f) if f else None

    def update_finding(
        self,
        finding_id: str,
        expected_revision: int,
        user_id: str,
        statement: Optional[str] = None,
        finding_type: Optional[ResearchFindingType] = None,
        methodology_description: Optional[str] = None,
        supporting_evidence_ids: Optional[List[str]] = None,
        contradicting_evidence_ids: Optional[List[str]] = None,
        limitations: Optional[List[str]] = None,
        review_status: Optional[ResearchFindingReviewStatus] = None,
    ) -> ResearchFinding:
        """Updates a research finding with optimistic concurrency."""
        with self._lock:
            f = self._findings.get(finding_id)
            if not f:
                raise ResearchFindingNotFoundError(f"Finding '{finding_id}' not found.")
            if f.author_user_id != user_id and f.author_user_id != "default-user":
                raise ResearchAnalysisAccessDeniedError(f"Access denied to finding '{finding_id}'.")
            if f.revision != expected_revision:
                raise ResearchFindingRevisionConflictError(
                    f"Stale finding write: current revision is {f.revision}, expected {expected_revision}."
                )

            now = datetime.datetime.now(datetime.timezone.utc)
            if statement is not None:
                f.statement = statement
            if finding_type is not None:
                f.finding_type = finding_type
            if methodology_description is not None:
                f.methodology_description = methodology_description
            if supporting_evidence_ids is not None:
                f.supporting_evidence_ids = supporting_evidence_ids
            if contradicting_evidence_ids is not None:
                f.contradicting_evidence_ids = contradicting_evidence_ids
            if limitations is not None:
                f.limitations = limitations
            if review_status is not None:
                f.review_status = review_status

            f.revision += 1
            f.updated_at = now

            self._log_activity(
                action=ResearchActivityAction.FINDING_UPDATED,
                entity_id=f.finding_id,
                entity_type="FINDING",
                user_id=user_id,
                details={"revision": f.revision, "review_status": f.review_status.value},
            )
            return copy.deepcopy(f)

    def delete_finding(self, finding_id: str, user_id: str) -> bool:
        """Deletes a research finding."""
        with self._lock:
            f = self._findings.get(finding_id)
            if not f:
                raise ResearchFindingNotFoundError(f"Finding '{finding_id}' not found.")
            if f.author_user_id != user_id and f.author_user_id != "default-user":
                raise ResearchAnalysisAccessDeniedError(f"Access denied to finding '{finding_id}'.")

            del self._findings[finding_id]
            self._log_activity(
                action=ResearchActivityAction.FINDING_DELETED,
                entity_id=finding_id,
                entity_type="FINDING",
                user_id=user_id,
                details={"deleted_finding_id": finding_id},
            )
            return True

    def list_findings(
        self,
        analysis_id: Optional[str] = None,
        investigation_id: Optional[str] = None,
    ) -> List[ResearchFinding]:
        """Lists findings associated with an analysis or investigation."""
        with self._lock:
            res = list(self._findings.values())
            if analysis_id:
                res = [f for f in res if f.analysis_id == analysis_id]
            if investigation_id:
                res = [f for f in res if f.investigation_id == investigation_id]
            return sorted(copy.deepcopy(res), key=lambda f: f.updated_at, reverse=True)

    # -----------------------------------------------------------------------
    # Stage 106 — Analyst Assumptions Repository Methods
    # -----------------------------------------------------------------------
    def create_assumption(self, assumption: ResearchAnalysisAssumption) -> ResearchAnalysisAssumption:
        """Persists a new analyst assumption for sensitivity modeling."""
        with self._lock:
            self._assumptions[assumption.assumption_id] = copy.deepcopy(assumption)
            self._log_activity(
                action=ResearchActivityAction.ASSUMPTION_SAVED,
                entity_id=assumption.assumption_id,
                entity_type="ASSUMPTION",
                user_id="default-user",
                details={"analysis_id": assumption.analysis_id, "parameter": assumption.parameter_id},
            )
            return copy.deepcopy(assumption)

    def list_assumptions(self, analysis_id: str) -> List[ResearchAnalysisAssumption]:
        """Lists all assumptions linked to a specific analysis."""
        with self._lock:
            assumps = [a for a in self._assumptions.values() if a.analysis_id == analysis_id]
            return sorted(copy.deepcopy(assumps), key=lambda a: a.created_at)

    def delete_assumption(self, assumption_id: str) -> bool:
        """Deletes an assumption by ID."""
        with self._lock:
            if assumption_id in self._assumptions:
                del self._assumptions[assumption_id]
                return True
            raise ResearchAssumptionNotFoundError(f"Assumption '{assumption_id}' not found.")

    def get_assumption(self, assumption_id: str) -> Optional[ResearchAnalysisAssumption]:
        """Retrieves an assumption by ID."""
        with self._lock:
            a = self._assumptions.get(assumption_id)
            return copy.deepcopy(a) if a else None

    def save_scenario(self, scenario: ResearchScenario) -> ResearchScenario:
        """Saves a deterministic what-if scenario record."""
        with self._lock:
            self._scenarios[scenario.scenario_id] = copy.deepcopy(scenario)
            return copy.deepcopy(scenario)

    # -----------------------------------------------------------------------
    # Stage 107 — Reports, Theses, Verification & Export Repository
    # -----------------------------------------------------------------------
    def _seed_baseline_reports(self):
        """Seed baseline verified research reports and investment theses."""
        now = datetime.datetime.now(datetime.timezone.utc)
        user_id = "default-user"

        # Baseline Report: Apple Inc. Services Margin Analysis Report
        rep_id = "rep-apple-services-expansion-fy24"
        report = ResearchReport(
            report_id=rep_id,
            owner_user_id=user_id,
            investigation_id="inv-apple-fy24-margins",
            report_type=ResearchReportType.COMPANY_RESEARCH,
            title="Apple Inc. (AAPL) Fiscal 2024 Fundamental Research & Services Margin Expansion",
            subtitle="Multi-Period Statement Analysis, Peer Benchmarking and Evidence-Backed Synthesis",
            abstract="A rigorous fundamental research synthesis evaluating Apple's revenue composition, gross margin trajectory across Products vs. Services, capital structure, and risk factors grounded in SEC Form 10-K filings.",
            primary_subject_id="AAPL",
            primary_subject_type="COMPANY",
            secondary_subject_ids=["MSFT", "NVDA"],
            report_as_of=datetime.date(2024, 10, 25),
            research_cutoff=datetime.datetime(2024, 10, 25, 23, 59, 59, tzinfo=datetime.timezone.utc),
            template_id="tpl-company-research",
            status=ReportLifecycleStatus.IN_PROGRESS,
            current_revision=1,
            snapshot_policy=ReportSnapshotPolicy.DRAFT_LATEST_AUTHORIZED,
            source_manifest=[
                {
                    "source_reference_id": "src-filing-aapl-10k-2024",
                    "accession_number": "0000320193-24-000106",
                    "document_title": "Apple Inc. Form 10-K (Fiscal Year Ended September 28, 2024)",
                    "filing_date": "2024-10-31",
                }
            ],
            evidence_manifest=["evi-aapl-rev-2024", "evi-aapl-risk-china"],
            analysis_run_manifest=["run-aapl-revenue-trend-001"],
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=4),
            provenance={"created_via": "Stage 107 Seeding", "methodology_version": 1},
        )
        self._reports[rep_id] = report

        # Seed default sections matching tpl-company-research
        sec_1 = ResearchReportSection(
            section_id="sec-apple-exec-summary",
            report_id=rep_id,
            parent_section_id=None,
            order_index=1,
            section_type=ReportSectionType.EXECUTIVE_SUMMARY,
            heading="1. Executive Summary & Investment Thesis Summary",
            content_blocks=[
                {
                    "block_id": "blk-apple-exec-1",
                    "section_id": "sec-apple-exec-summary",
                    "order_index": 1,
                    "block_type": ReportBlockType.PARAGRAPH.value,
                    "content_text": "Apple Inc. (NASDAQ: AAPL) delivered fiscal 2024 total net sales of $391.04B (+2.0% YoY) and net income of $93.74B (-3.4% YoY), underpinned by record Services revenue of $96.17B (+12.9% YoY) with segment gross margins reaching 74.0%.",
                    "citation_ids": ["cit-aapl-10k-2024-p1"],
                    "evidence_ids": ["evi-aapl-rev-2024"],
                },
                {
                    "block_id": "blk-apple-exec-2",
                    "section_id": "sec-apple-exec-summary",
                    "order_index": 2,
                    "block_type": ReportBlockType.PARAGRAPH.value,
                    "content_text": "The central thesis asserts that high-margin Services expansion continues to enhance consolidated gross margin durability (46.2% in FY24 vs 44.1% in FY23), partially cushioning cyclical hardware replacement cycles.",
                    "citation_ids": [],
                    "evidence_ids": [],
                },
            ],
            revision=1,
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=4),
        )

        sec_2 = ResearchReportSection(
            section_id="sec-apple-financial-perf",
            report_id=rep_id,
            parent_section_id=None,
            order_index=2,
            section_type=ReportSectionType.FINANCIAL_PERFORMANCE,
            heading="2. Historical Financial Trajectory & Margin Analysis",
            content_blocks=[
                {
                    "block_id": "blk-apple-fin-table",
                    "section_id": "sec-apple-financial-perf",
                    "order_index": 1,
                    "block_type": ReportBlockType.FINANCIAL_TABLE.value,
                    "caption": "Table 1.1: Apple Inc. Multi-Year Financial Performance (FY22 - FY24)",
                    "content_text": "Fiscal Year | Net Sales ($M) | Gross Margin % | Operating Income ($M) | Operating Cash Flow ($M)\nFY 2024     | $391,035       | 46.2%          | $123,216              | $118,254\nFY 2023     | $383,285       | 44.1%          | $114,301              | $110,543\nFY 2022     | $394,328       | 43.3%          | $119,437              | $122,151",
                    "citation_ids": ["cit-aapl-10k-2024-p1"],
                    "evidence_ids": ["evi-aapl-rev-2024"],
                    "analysis_run_id": "run-aapl-revenue-trend-001",
                },
                {
                    "block_id": "blk-apple-fin-chart",
                    "section_id": "sec-apple-financial-perf",
                    "order_index": 2,
                    "block_type": ReportBlockType.CHART.value,
                    "caption": "Figure 1.1: Historical Revenue Trend & Compound Growth (CAGR: 1.95%)",
                    "content_text": "Revenue Series FY22-FY24: FY22: $394,328M, FY23: $383,285M, FY24: $391,035M",
                    "analysis_run_id": "run-aapl-revenue-trend-001",
                },
            ],
            revision=1,
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=4),
        )

        sec_3 = ResearchReportSection(
            section_id="sec-apple-thesis-section",
            report_id=rep_id,
            parent_section_id=None,
            order_index=3,
            section_type=ReportSectionType.INVESTMENT_THESIS,
            heading="3. Structured Investment Thesis & Bull/Bear Scenarios",
            content_blocks=[
                {
                    "block_id": "blk-apple-thesis-1",
                    "section_id": "sec-apple-thesis-section",
                    "order_index": 1,
                    "block_type": ReportBlockType.PARAGRAPH.value,
                    "content_text": "BULL CASE: Services gross profit reaches 40% of total company gross profit, driving cash generation to fund sustained >$100B annual capital return program.",
                },
                {
                    "block_id": "blk-apple-thesis-2",
                    "section_id": "sec-apple-thesis-section",
                    "order_index": 2,
                    "block_type": ReportBlockType.PARAGRAPH.value,
                    "content_text": "BEAR CASE: Global regulatory antitrust mandates compel restructuring of App Store distribution economics, compressing segment margins while China sales contract.",
                    "citation_ids": ["cit-aapl-10k-2024-p2"],
                    "evidence_ids": ["evi-aapl-risk-china"],
                },
            ],
            revision=1,
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=4),
        )

        sec_4 = ResearchReportSection(
            section_id="sec-apple-disclosures",
            report_id=rep_id,
            parent_section_id=None,
            order_index=4,
            section_type=ReportSectionType.DISCLOSURES,
            heading="4. Research Limitations & Institutional Disclosures",
            content_blocks=[
                {
                    "block_id": "blk-apple-disclosures-1",
                    "section_id": "sec-apple-disclosures",
                    "order_index": 1,
                    "block_type": ReportBlockType.PARAGRAPH.value,
                    "content_text": "This research report represents independent analytical synthesis. It does not constitute an investment recommendation or price target forecast.",
                }
            ],
            revision=1,
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=4),
        )

        self._report_sections[rep_id] = [sec_1, sec_2, sec_3, sec_4]

        # Initial revision
        snapshot = {
            "report": copy.deepcopy(report.__dict__),
            "sections": [copy.deepcopy(s.__dict__) for s in [sec_1, sec_2, sec_3, sec_4]],
        }
        rev = ResearchReportRevision(
            revision_id="rev-apple-services-v1",
            report_id=rep_id,
            revision_number=1,
            parent_revision_id=None,
            author_user_id=user_id,
            document_snapshot=snapshot,
            source_manifest=report.source_manifest,
            analysis_manifest=report.analysis_run_manifest,
            revision_status=ReportLifecycleStatus.IN_PROGRESS,
            change_summary="Initial baseline draft generated from investigation findings",
            content_hash="hash-apple-rep-v1-initial",
            created_at=now - datetime.timedelta(days=2),
        )
        self._report_revisions[rep_id] = [rev]

        # Baseline Investment Thesis
        the_id = "the-apple-services-moat-fy24"
        thesis = ResearchInvestmentThesis(
            thesis_id=the_id,
            investigation_id="inv-apple-fy24-margins",
            report_id=rep_id,
            owner_user_id=user_id,
            primary_subject_id="AAPL",
            primary_subject_type="COMPANY",
            thesis_statement="Apple's structural shift toward high-margin recurring Services revenue provides resilient operating margin support that mitigates cyclical hardware replacement volatility.",
            time_horizon="12_MONTHS",
            status=ThesisLifecycleStatus.ACTIVE,
            current_revision=1,
            bull_case_summary="Services revenue exceeds 25% of total mix with gross margins expanding above 75%, driving sustained free cash flow conversion above 100%.",
            bear_case_summary="Regulatory antitrust remedies in EU and US impair App Store commission rates while iPhone replacement cycle lengthens beyond 4 years.",
            base_case_summary="Moderate 4-6% total revenue CAGR with stable 45-46% consolidated gross margins and ongoing $100B+ annual share repurchases.",
            assumptions_summary="Installed base continues compounding at low-single-digits; no material disruption to prime silicon supply chain.",
            risks_summary="Antitrust litigation, consumer spending contraction in Greater China, and sovereign semiconductor export controls.",
            catalysts_summary="Apple Intelligence enterprise adoption rollout, FY25 Q1 holiday earnings disclosure, and Worldwide Developers Conference disclosures.",
            created_at=now - datetime.timedelta(days=2),
            updated_at=now - datetime.timedelta(hours=4),
        )
        self._theses[the_id] = thesis

        # Seed Thesis Arguments
        arg_1 = ResearchThesisArgument(
            argument_id="arg-apple-bull-1",
            thesis_id=the_id,
            argument_type=ThesisArgumentType.BULL_CASE,
            statement="Services gross profit contribution expanded from 31.2% in FY22 to 38.3% in FY24, improving consolidated margin floor.",
            claim_ids=["claim-aapl-services-growth"],
            evidence_ids=["evi-aapl-rev-2024"],
            analysis_run_ids=["run-aapl-revenue-trend-001"],
            finding_ids=["find-aapl-margin-expansion-fy24"],
            limitations=["Assumes stable App Store fee structure."],
            revision=1,
            created_at=now - datetime.timedelta(days=2),
        )
        arg_2 = ResearchThesisArgument(
            argument_id="arg-apple-bear-1",
            thesis_id=the_id,
            argument_type=ThesisArgumentType.BEAR_CASE,
            statement="Item 1A risk disclosure flags intensifying foreign regulatory compliance burdens and potential antitrust remedies.",
            claim_ids=["claim-aapl-china-risk"],
            evidence_ids=["evi-aapl-risk-china"],
            analysis_run_ids=[],
            finding_ids=[],
            limitations=["Legal outcomes subject to judicial review."],
            revision=1,
            created_at=now - datetime.timedelta(days=2),
        )
        self._thesis_arguments[the_id] = [arg_1, arg_2]

    # -----------------------------------------------------------------------
    # Report CRUD Methods
    # -----------------------------------------------------------------------
    def list_reports(
        self,
        user_id: str,
        investigation_id: Optional[str] = None,
        report_type: Optional[ResearchReportType] = None,
        status: Optional[ReportLifecycleStatus] = None,
        subject_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ResearchReport], int]:
        """Lists user-owned reports with multi-factor filtering."""
        with self._lock:
            res = [r for r in self._reports.values() if r.owner_user_id == user_id]
            if investigation_id:
                res = [r for r in res if r.investigation_id == investigation_id]
            if report_type:
                res = [r for r in res if r.report_type == report_type]
            if status:
                res = [r for r in res if r.status == status]
            if subject_id:
                res = [r for r in res if r.primary_subject_id == subject_id]

            total = len(res)
            sorted_res = sorted(res, key=lambda r: r.updated_at, reverse=True)
            paged = sorted_res[offset : offset + limit]
            return [copy.deepcopy(r) for r in paged], total

    def create_report(
        self,
        user_id: str,
        report: ResearchReport,
        initial_sections: Optional[List[ResearchReportSection]] = None,
    ) -> ResearchReport:
        """Creates and stores a new research report with initial sections."""
        with self._lock:
            report.owner_user_id = user_id
            self._reports[report.report_id] = copy.deepcopy(report)

            sections = initial_sections or []
            self._report_sections[report.report_id] = [copy.deepcopy(s) for s in sections]

            # Create initial revision
            snapshot = {
                "report": copy.deepcopy(report.__dict__),
                "sections": [copy.deepcopy(s.__dict__) for s in sections],
            }
            rev = ResearchReportRevision(
                revision_id=f"rev-{uuid.uuid4().hex[:12]}",
                report_id=report.report_id,
                revision_number=report.current_revision,
                parent_revision_id=None,
                author_user_id=user_id,
                document_snapshot=snapshot,
                source_manifest=report.source_manifest,
                analysis_manifest=report.analysis_run_manifest,
                revision_status=report.status,
                change_summary="Initial report creation",
                content_hash=f"hash-{uuid.uuid4().hex[:16]}",
                created_at=report.created_at,
            )
            self._report_revisions[report.report_id] = [rev]

            self._log_activity(
                action=ResearchActivityAction.REPORT_CREATED,
                entity_id=report.report_id,
                entity_type="REPORT",
                user_id=user_id,
                details={"title": report.title, "report_type": report.report_type.value},
            )
            return copy.deepcopy(report)

    def get_report(self, report_id: str) -> Optional[ResearchReport]:
        """Retrieves a research report by ID."""
        with self._lock:
            rep = self._reports.get(report_id)
            return copy.deepcopy(rep) if rep else None

    def update_report(
        self,
        user_id: str,
        report_id: str,
        expected_revision: int,
        updates: Dict[str, Any],
    ) -> ResearchReport:
        """Updates report parameters with optimistic concurrency protection."""
        with self._lock:
            rep = self._reports.get(report_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
            if rep.owner_user_id != user_id:
                raise ResearchReportAccessDeniedError("Access denied to report.")
            if rep.status == ReportLifecycleStatus.FINALIZED:
                raise ResearchReportFinalizedImmutableError("Cannot update finalized report. Create new revision.")
            if rep.current_revision != expected_revision:
                raise ResearchReportRevisionConflictError(
                    f"Revision conflict: report is at revision {rep.current_revision}, expected {expected_revision}."
                )

            for key, val in updates.items():
                if hasattr(rep, key) and val is not None:
                    setattr(rep, key, val)

            rep.current_revision += 1
            rep.updated_at = datetime.datetime.now(datetime.timezone.utc)

            # Record snapshot revision
            sections = self._report_sections.get(report_id, [])
            snapshot = {
                "report": copy.deepcopy(rep.__dict__),
                "sections": [copy.deepcopy(s.__dict__) for s in sections],
            }
            rev = ResearchReportRevision(
                revision_id=f"rev-{uuid.uuid4().hex[:12]}",
                report_id=rep.report_id,
                revision_number=rep.current_revision,
                parent_revision_id=f"rev-{rep.current_revision - 1}",
                author_user_id=user_id,
                document_snapshot=snapshot,
                source_manifest=rep.source_manifest,
                analysis_manifest=rep.analysis_run_manifest,
                revision_status=rep.status,
                change_summary=updates.get("change_summary", "Report parameter update"),
                content_hash=f"hash-{uuid.uuid4().hex[:16]}",
                created_at=rep.updated_at,
            )
            self._report_revisions.setdefault(report_id, []).append(rev)

            self._log_activity(
                action=ResearchActivityAction.REPORT_UPDATED,
                entity_id=rep.report_id,
                entity_type="REPORT",
                user_id=user_id,
                details={"revision": rep.current_revision},
            )
            return copy.deepcopy(rep)

    def finalize_report(
        self,
        user_id: str,
        report_id: str,
        expected_revision: int,
        change_summary: Optional[str] = None,
    ) -> ResearchReport:
        """Freezes report into finalized immutable state and generates immutable snapshot."""
        with self._lock:
            rep = self._reports.get(report_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
            if rep.owner_user_id != user_id:
                raise ResearchReportAccessDeniedError("Access denied to report.")
            if rep.current_revision != expected_revision:
                raise ResearchReportRevisionConflictError(
                    f"Revision conflict: report revision {rep.current_revision} != {expected_revision}."
                )

            rep.status = ReportLifecycleStatus.FINALIZED
            rep.current_revision += 1
            rep.updated_at = datetime.datetime.now(datetime.timezone.utc)

            sections = self._report_sections.get(report_id, [])
            snapshot = {
                "report": copy.deepcopy(rep.__dict__),
                "sections": [copy.deepcopy(s.__dict__) for s in sections],
            }
            rev = ResearchReportRevision(
                revision_id=f"rev-{uuid.uuid4().hex[:12]}",
                report_id=rep.report_id,
                revision_number=rep.current_revision,
                parent_revision_id=f"rev-{rep.current_revision - 1}",
                author_user_id=user_id,
                document_snapshot=snapshot,
                source_manifest=rep.source_manifest,
                analysis_manifest=rep.analysis_run_manifest,
                revision_status=ReportLifecycleStatus.FINALIZED,
                change_summary=change_summary or "Official report finalization",
                content_hash=f"hash-final-{uuid.uuid4().hex[:16]}",
                created_at=rep.updated_at,
            )
            self._report_revisions.setdefault(report_id, []).append(rev)

            self._log_activity(
                action=ResearchActivityAction.REPORT_FINALIZED,
                entity_id=rep.report_id,
                entity_type="REPORT",
                user_id=user_id,
                details={"final_revision": rep.current_revision},
            )
            return copy.deepcopy(rep)

    def delete_report(self, user_id: str, report_id: str) -> bool:
        """Archives or deletes a research report."""
        with self._lock:
            rep = self._reports.get(report_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
            if rep.owner_user_id != user_id:
                raise ResearchReportAccessDeniedError("Access denied to report.")

            del self._reports[report_id]
            self._report_sections.pop(report_id, None)
            self._report_revisions.pop(report_id, None)

            self._log_activity(
                action=ResearchActivityAction.REPORT_DELETED,
                entity_id=report_id,
                entity_type="REPORT",
                user_id=user_id,
                details={},
            )
            return True

    # -----------------------------------------------------------------------
    # Section Management Methods
    # -----------------------------------------------------------------------
    def list_report_sections(self, report_id: str) -> List[ResearchReportSection]:
        """Lists all sections of a report in chronological order index."""
        with self._lock:
            secs = self._report_sections.get(report_id, [])
            return sorted(copy.deepcopy(secs), key=lambda s: s.order_index)

    def get_report_section(self, report_id: str, section_id: str) -> Optional[ResearchReportSection]:
        """Retrieves a specific section within a report."""
        with self._lock:
            secs = self._report_sections.get(report_id, [])
            for s in secs:
                if s.section_id == section_id:
                    return copy.deepcopy(s)
            return None

    def create_report_section(self, user_id: str, section: ResearchReportSection) -> ResearchReportSection:
        """Appends a section to a report."""
        with self._lock:
            rep = self._reports.get(section.report_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{section.report_id}' not found.")
            if rep.owner_user_id != user_id:
                raise ResearchReportAccessDeniedError("Access denied.")
            if rep.status == ReportLifecycleStatus.FINALIZED:
                raise ResearchReportFinalizedImmutableError("Cannot add section to finalized report.")

            secs = self._report_sections.setdefault(section.report_id, [])
            if section.order_index is None or section.order_index <= 0:
                section.order_index = len(secs) + 1

            secs.append(copy.deepcopy(section))
            rep.updated_at = datetime.datetime.now(datetime.timezone.utc)
            return copy.deepcopy(section)

    def update_report_section(
        self,
        user_id: str,
        section_id: str,
        expected_revision: int,
        heading: Optional[str] = None,
        section_type: Optional[ReportSectionType] = None,
        content_blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> ResearchReportSection:
        """Modifies heading or content blocks of a report section."""
        with self._lock:
            found_sec: Optional[ResearchReportSection] = None
            found_report: Optional[ResearchReport] = None

            for rep_id, secs in self._report_sections.items():
                for s in secs:
                    if s.section_id == section_id:
                        found_sec = s
                        found_report = self._reports.get(rep_id)
                        break
                if found_sec:
                    break

            if not found_sec or not found_report:
                raise ResearchReportSectionNotFoundError(f"Section '{section_id}' not found.")
            if found_report.owner_user_id != user_id:
                raise ResearchReportAccessDeniedError("Access denied to section.")
            if found_report.status == ReportLifecycleStatus.FINALIZED:
                raise ResearchReportFinalizedImmutableError("Cannot edit finalized section.")

            if heading is not None:
                found_sec.heading = heading
            if section_type is not None:
                found_sec.section_type = section_type
            if content_blocks is not None:
                found_sec.content_blocks = copy.deepcopy(content_blocks)

            found_sec.revision += 1
            found_sec.updated_at = datetime.datetime.now(datetime.timezone.utc)
            found_report.updated_at = found_sec.updated_at

            return copy.deepcopy(found_sec)

    def delete_report_section(self, user_id: str, section_id: str) -> bool:
        """Removes a section from a report."""
        with self._lock:
            for rep_id, secs in self._report_sections.items():
                for i, s in enumerate(secs):
                    if s.section_id == section_id:
                        rep = self._reports.get(rep_id)
                        if rep and rep.owner_user_id != user_id:
                            raise ResearchReportAccessDeniedError("Access denied.")
                        if rep and rep.status == ReportLifecycleStatus.FINALIZED:
                            raise ResearchReportFinalizedImmutableError("Cannot delete section from finalized report.")
                        secs.pop(i)
                        return True
            raise ResearchReportSectionNotFoundError(f"Section '{section_id}' not found.")

    def reorder_report_sections(
        self,
        user_id: str,
        report_id: str,
        section_ids: List[str],
    ) -> List[ResearchReportSection]:
        """Safely reorders sections according to list of section IDs."""
        with self._lock:
            rep = self._reports.get(report_id)
            if not rep:
                raise ResearchReportNotFoundError(f"Report '{report_id}' not found.")
            if rep.owner_user_id != user_id:
                raise ResearchReportAccessDeniedError("Access denied.")
            if rep.status == ReportLifecycleStatus.FINALIZED:
                raise ResearchReportFinalizedImmutableError("Cannot reorder finalized report.")

            secs = self._report_sections.get(report_id, [])
            sec_map = {s.section_id: s for s in secs}

            new_order: List[ResearchReportSection] = []
            for idx, sid in enumerate(section_ids, start=1):
                if sid in sec_map:
                    s = sec_map[sid]
                    s.order_index = idx
                    new_order.append(s)

            # Include any sections not explicitly specified
            remaining = [s for s in secs if s.section_id not in section_ids]
            for idx, s in enumerate(remaining, start=len(new_order) + 1):
                s.order_index = idx
                new_order.append(s)

            self._report_sections[report_id] = new_order
            rep.updated_at = datetime.datetime.now(datetime.timezone.utc)
            return sorted(copy.deepcopy(new_order), key=lambda s: s.order_index)

    # -----------------------------------------------------------------------
    # Report Revisions & Diffing
    # -----------------------------------------------------------------------
    def list_report_revisions(self, report_id: str) -> List[ResearchReportRevision]:
        """Lists historical snapshots for an authorized report."""
        with self._lock:
            revs = self._report_revisions.get(report_id, [])
            return sorted(copy.deepcopy(revs), key=lambda r: r.revision_number, reverse=True)

    def get_report_revision(self, report_id: str, revision_number: int) -> Optional[ResearchReportRevision]:
        """Retrieves a specific revision snapshot."""
        with self._lock:
            revs = self._report_revisions.get(report_id, [])
            for r in revs:
                if r.revision_number == revision_number:
                    return copy.deepcopy(r)
            return None

    def compare_report_revisions(
        self,
        report_id: str,
        base_rev: int,
        target_rev: int,
    ) -> Dict[str, Any]:
        """Computes structural and text diff between two report snapshots."""
        with self._lock:
            base_r = self.get_report_revision(report_id, base_rev)
            target_r = self.get_report_revision(report_id, target_rev)
            if not base_r or not target_r:
                raise ResearchReportNotFoundError("Requested revision snapshot not found.")

            base_secs = {s["section_id"]: s for s in base_r.document_snapshot.get("sections", [])}
            target_secs = {s["section_id"]: s for s in target_r.document_snapshot.get("sections", [])}

            added = [s["heading"] for sid, s in target_secs.items() if sid not in base_secs]
            removed = [s["heading"] for sid, s in base_secs.items() if sid not in target_secs]
            modified: List[str] = []

            for sid, s in target_secs.items():
                if sid in base_secs:
                    if s.get("heading") != base_secs[sid].get("heading") or len(s.get("content_blocks", [])) != len(base_secs[sid].get("content_blocks", [])):
                        modified.append(s.get("heading", sid))

            diff_text = f"--- Revision {base_rev}\n+++ Revision {target_rev}\n"
            if added:
                diff_text += f"+ Added sections: {', '.join(added)}\n"
            if removed:
                diff_text += f"- Removed sections: {', '.join(removed)}\n"
            if modified:
                diff_text += f"~ Modified sections: {', '.join(modified)}\n"
            if not added and not removed and not modified:
                diff_text += "No structural modifications between revisions.\n"

            return {
                "report_id": report_id,
                "base_revision_number": base_rev,
                "target_revision_number": target_rev,
                "sections_added": added,
                "sections_removed": removed,
                "sections_modified": modified,
                "diff_unified": diff_text,
            }

    # -----------------------------------------------------------------------
    # Investment Theses Repository Methods
    # -----------------------------------------------------------------------
    def list_theses(
        self,
        user_id: str,
        investigation_id: Optional[str] = None,
        report_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ResearchInvestmentThesis], int]:
        """Lists user-owned investment theses with multi-factor filtering."""
        with self._lock:
            res = [t for t in self._theses.values() if t.owner_user_id == user_id]
            if investigation_id:
                res = [t for t in res if t.investigation_id == investigation_id]
            if report_id:
                res = [t for t in res if t.report_id == report_id]
            if subject_id:
                res = [t for t in res if t.primary_subject_id == subject_id]

            total = len(res)
            sorted_res = sorted(res, key=lambda t: t.updated_at, reverse=True)
            paged = sorted_res[offset : offset + limit]
            return [copy.deepcopy(t) for t in paged], total

    def create_thesis(
        self,
        user_id: str,
        thesis: ResearchInvestmentThesis,
        initial_arguments: Optional[List[ResearchThesisArgument]] = None,
    ) -> ResearchInvestmentThesis:
        """Stores a new analyst investment thesis with structured arguments."""
        with self._lock:
            thesis.owner_user_id = user_id
            self._theses[thesis.thesis_id] = copy.deepcopy(thesis)

            if initial_arguments:
                self._thesis_arguments[thesis.thesis_id] = [copy.deepcopy(a) for a in initial_arguments]
            else:
                self._thesis_arguments[thesis.thesis_id] = []

            self._log_activity(
                action=ResearchActivityAction.THESIS_CREATED,
                entity_id=thesis.thesis_id,
                entity_type="THESIS",
                user_id=user_id,
                details={"subject": thesis.primary_subject_id, "horizon": thesis.time_horizon},
            )
            return copy.deepcopy(thesis)

    def get_thesis(self, thesis_id: str) -> Optional[ResearchInvestmentThesis]:
        """Retrieves an investment thesis by ID."""
        with self._lock:
            the = self._theses.get(thesis_id)
            return copy.deepcopy(the) if the else None

    def update_thesis(
        self,
        user_id: str,
        thesis_id: str,
        expected_revision: int,
        updates: Dict[str, Any],
    ) -> ResearchInvestmentThesis:
        """Updates an investment thesis statement and summaries."""
        with self._lock:
            the = self._theses.get(thesis_id)
            if not the:
                raise ResearchInvestmentThesisNotFoundError(f"Thesis '{thesis_id}' not found.")
            if the.owner_user_id != user_id:
                raise ResearchInvestmentThesisAccessDeniedError("Access denied.")
            if the.current_revision != expected_revision:
                raise ResearchInvestmentThesisRevisionConflictError(
                    f"Revision conflict on thesis {the.current_revision} != {expected_revision}."
                )

            for key, val in updates.items():
                if hasattr(the, key) and val is not None:
                    setattr(the, key, val)

            the.current_revision += 1
            the.updated_at = datetime.datetime.now(datetime.timezone.utc)

            self._log_activity(
                action=ResearchActivityAction.THESIS_UPDATED,
                entity_id=the.thesis_id,
                entity_type="THESIS",
                user_id=user_id,
                details={"revision": the.current_revision},
            )
            return copy.deepcopy(the)

    def delete_thesis(self, user_id: str, thesis_id: str) -> bool:
        """Deletes an investment thesis."""
        with self._lock:
            the = self._theses.get(thesis_id)
            if not the:
                raise ResearchInvestmentThesisNotFoundError(f"Thesis '{thesis_id}' not found.")
            if the.owner_user_id != user_id:
                raise ResearchInvestmentThesisAccessDeniedError("Access denied.")

            del self._theses[thesis_id]
            self._thesis_arguments.pop(thesis_id, None)
            return True

    def list_thesis_arguments(self, thesis_id: str) -> List[ResearchThesisArgument]:
        """Lists arguments linked to an investment thesis."""
        with self._lock:
            args = self._thesis_arguments.get(thesis_id, [])
            return sorted(copy.deepcopy(args), key=lambda a: a.created_at)

    def create_thesis_argument(self, user_id: str, argument: ResearchThesisArgument) -> ResearchThesisArgument:
        """Adds a structured argument node to a thesis."""
        with self._lock:
            the = self._theses.get(argument.thesis_id)
            if not the:
                raise ResearchInvestmentThesisNotFoundError(f"Thesis '{argument.thesis_id}' not found.")
            if the.owner_user_id != user_id:
                raise ResearchInvestmentThesisAccessDeniedError("Access denied.")

            args = self._thesis_arguments.setdefault(argument.thesis_id, [])
            args.append(copy.deepcopy(argument))
            the.updated_at = datetime.datetime.now(datetime.timezone.utc)
            return copy.deepcopy(argument)

    def delete_thesis_argument(self, user_id: str, argument_id: str) -> bool:
        """Deletes a thesis argument node."""
        with self._lock:
            for the_id, args in self._thesis_arguments.items():
                for i, a in enumerate(args):
                    if a.argument_id == argument_id:
                        the = self._theses.get(the_id)
                        if the and the.owner_user_id != user_id:
                            raise ResearchInvestmentThesisAccessDeniedError("Access denied.")
                        args.pop(i)
                        return True
            raise ResearchThesisArgumentNotFoundError(f"Argument '{argument_id}' not found.")

    # -----------------------------------------------------------------------
    # Report Verification Persistence
    # -----------------------------------------------------------------------
    def record_verification(self, verification: ResearchReportVerification) -> ResearchReportVerification:
        """Saves a verification outcome audit record."""
        with self._lock:
            self._verification_runs.setdefault(verification.report_id, []).append(copy.deepcopy(verification))
            self._log_activity(
                action=ResearchActivityAction.REPORT_VERIFIED,
                entity_id=verification.report_id,
                entity_type="REPORT_VERIFICATION",
                user_id=verification.verified_by_user_id,
                details={
                    "is_valid": verification.is_valid,
                    "blocking_count": verification.blocking_issues_count,
                    "coverage_pct": verification.citation_coverage_pct,
                },
            )
            return copy.deepcopy(verification)

    def get_latest_verification(self, report_id: str) -> Optional[ResearchReportVerification]:
        """Retrieves the latest verification audit for a report."""
        with self._lock:
            runs = self._verification_runs.get(report_id, [])
            if not runs:
                return None
            return copy.deepcopy(sorted(runs, key=lambda r: r.checked_at, reverse=True)[0])

    # -----------------------------------------------------------------------
    # Document Export Job Methods
    # -----------------------------------------------------------------------
    def create_export(
        self,
        export: ResearchReportExport,
        artifact_bytes: Optional[bytes] = None,
    ) -> ResearchReportExport:
        """Stores a document export job record and binary artifact."""
        with self._lock:
            self._exports[export.export_id] = copy.deepcopy(export)
            if artifact_bytes is not None:
                self._export_artifacts[export.export_id] = artifact_bytes

            self._log_activity(
                action=ResearchActivityAction.REPORT_EXPORTED,
                entity_id=export.report_id,
                entity_type="EXPORT",
                user_id=export.owner_user_id,
                details={"format": export.format.value, "size_bytes": export.file_size_bytes},
            )
            return copy.deepcopy(export)

    def get_export(self, export_id: str) -> Optional[ResearchReportExport]:
        """Retrieves an export job record by ID."""
        with self._lock:
            exp = self._exports.get(export_id)
            return copy.deepcopy(exp) if exp else None

    def list_exports(self, report_id: str) -> List[ResearchReportExport]:
        """Lists all export jobs for a specific report."""
        with self._lock:
            exps = [e for e in self._exports.values() if e.report_id == report_id]
            return sorted(copy.deepcopy(exps), key=lambda e: e.created_at, reverse=True)

    def get_export_bytes(self, export_id: str) -> Optional[bytes]:
        """Retrieves the binary export file content (PDF/DOCX)."""
        with self._lock:
            return self._export_artifacts.get(export_id)
