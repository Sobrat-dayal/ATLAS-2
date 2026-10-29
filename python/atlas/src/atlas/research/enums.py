"""Canonical Enums for Institutional Financial Research Platform (Stage 104)."""

from enum import Enum


class ResearchType(str, Enum):
    """Controlled taxonomy of financial research investigations."""
    COMPANY_RESEARCH = "COMPANY_RESEARCH"
    SECURITY_RESEARCH = "SECURITY_RESEARCH"
    INDUSTRY_RESEARCH = "INDUSTRY_RESEARCH"
    MACROECONOMIC_RESEARCH = "MACROECONOMIC_RESEARCH"
    MARKET_RESEARCH = "MARKET_RESEARCH"
    FINANCIAL_EVENT_RESEARCH = "FINANCIAL_EVENT_RESEARCH"
    GENERAL_FINANCIAL_RESEARCH = "GENERAL_FINANCIAL_RESEARCH"


class InvestigationLifecycleStatus(str, Enum):
    """Lifecycle status of a research investigation."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ResearchQuestionStatus(str, Enum):
    """Status of analyst-authored research questions."""
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    ADDRESSED = "ADDRESSED"
    DROPPED = "DROPPED"


class ResearchHypothesisStatus(str, Enum):
    """Status of analyst hypotheses (hypotheses are ideas to investigate, never automatic facts)."""
    PROPOSED = "PROPOSED"
    UNDER_TEST = "UNDER_TEST"
    SUPPORTED_BY_AVAILABLE_EVIDENCE = "SUPPORTED_BY_AVAILABLE_EVIDENCE"
    CONTRADICTED_BY_AVAILABLE_EVIDENCE = "CONTRADICTED_BY_AVAILABLE_EVIDENCE"
    INCONCLUSIVE = "INCONCLUSIVE"
    RETIRED = "RETIRED"


class ResearchNoteType(str, Enum):
    """Classification of analyst notes."""
    OBSERVATION = "OBSERVATION"
    QUESTION = "QUESTION"
    HYPOTHESIS = "HYPOTHESIS"
    ASSUMPTION = "ASSUMPTION"
    ANALYSIS = "ANALYSIS"
    CONCLUSION = "CONCLUSION"
    GENERAL_NOTE = "GENERAL_NOTE"


class ResearchNoteStatus(str, Enum):
    """Status of a structured research note."""
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEWED = "REVIEWED"
    ARCHIVED = "ARCHIVED"


class ResearchClaimCategory(str, Enum):
    """Explicit distinction between source-reported facts, assumptions, and analyst interpretations."""
    SOURCE_REPORTED_FACT = "SOURCE_REPORTED_FACT"
    ANALYST_INTERPRETATION = "ANALYST_INTERPRETATION"
    ASSUMPTION = "ASSUMPTION"
    HYPOTHESIS = "HYPOTHESIS"
    ESTIMATE = "ESTIMATE"
    OPEN_QUESTION = "OPEN_QUESTION"


class ResearchEvidenceStatus(str, Enum):
    """Evidence status of a claim or finding without fabricated probabilities."""
    SUPPORTED_BY_CITED_SOURCE = "SUPPORTED_BY_CITED_SOURCE"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_REVIEWED = "NOT_REVIEWED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_WITHDRAWN = "SOURCE_WITHDRAWN"


class ResearchSourceType(str, Enum):
    """Taxonomy of genuine financial research sources."""
    REGULATORY_FILING = "REGULATORY_FILING"
    CORPORATE_DISCLOSURE = "CORPORATE_DISCLOSURE"
    ANNUAL_REPORT = "ANNUAL_REPORT"
    QUARTERLY_REPORT = "QUARTERLY_REPORT"
    EARNINGS_RELEASE = "EARNINGS_RELEASE"
    FINANCIAL_STATEMENT = "FINANCIAL_STATEMENT"
    MARKET_DATASET = "MARKET_DATASET"
    ECONOMIC_DATASET = "ECONOMIC_DATASET"
    ECONOMIC_RELEASE = "ECONOMIC_RELEASE"
    NEWS_ARTICLE = "NEWS_ARTICLE"
    NEWS_STORY = "NEWS_STORY"
    FINANCIAL_EVENT = "FINANCIAL_EVENT"
    OFFICIAL_STATISTICAL_PUBLICATION = "OFFICIAL_STATISTICAL_PUBLICATION"
    LICENSED_RESEARCH_REPORT = "LICENSED_RESEARCH_REPORT"
    ACADEMIC_PUBLICATION = "ACADEMIC_PUBLICATION"
    USER_AUTHORED_DOCUMENT = "USER_AUTHORED_DOCUMENT"
    AUTHORIZED_EXTERNAL_REFERENCE = "AUTHORIZED_EXTERNAL_REFERENCE"
    UNKNOWN = "UNKNOWN"


class EvidenceLocationType(str, Enum):
    """Granular location of cited evidence in source documents."""
    PAGE = "PAGE"
    SECTION = "SECTION"
    PARAGRAPH = "PARAGRAPH"
    TABLE = "TABLE"
    ROW = "ROW"
    DATA_POINT = "DATA_POINT"
    ARTICLE_REVISION = "ARTICLE_REVISION"


class ClaimEvidenceRelationship(str, Enum):
    """Relationship between a claim and supporting/contradicting evidence."""
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CONTEXT = "CONTEXT"
    UNCLEAR = "UNCLEAR"


class SourceAvailabilityStatus(str, Enum):
    """Availability and entitlement status of a research source reference."""
    AVAILABLE = "AVAILABLE"
    RESTRICTED = "RESTRICTED"
    WITHDRAWN = "WITHDRAWN"
    UNAVAILABLE = "UNAVAILABLE"


class ResearchActivityAction(str, Enum):
    """Auditable actions recorded in research activity history."""
    INVESTIGATION_CREATED = "INVESTIGATION_CREATED"
    INVESTIGATION_UPDATED = "INVESTIGATION_UPDATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    INVESTIGATION_ARCHIVED = "INVESTIGATION_ARCHIVED"
    INVESTIGATION_DELETED = "INVESTIGATION_DELETED"
    QUESTION_ADDED = "QUESTION_ADDED"
    QUESTION_UPDATED = "QUESTION_UPDATED"
    QUESTION_DELETED = "QUESTION_DELETED"
    HYPOTHESIS_ADDED = "HYPOTHESIS_ADDED"
    HYPOTHESIS_UPDATED = "HYPOTHESIS_UPDATED"
    HYPOTHESIS_DELETED = "HYPOTHESIS_DELETED"
    NOTE_CREATED = "NOTE_CREATED"
    NOTE_UPDATED = "NOTE_UPDATED"
    NOTE_DELETED = "NOTE_DELETED"
    CLAIM_CREATED = "CLAIM_CREATED"
    CLAIM_UPDATED = "CLAIM_UPDATED"
    CLAIM_DELETED = "CLAIM_DELETED"
    SOURCE_LINKED = "SOURCE_LINKED"
    SOURCE_UNLINKED = "SOURCE_UNLINKED"
    EVIDENCE_ATTACHED = "EVIDENCE_ATTACHED"
    EVIDENCE_REMOVED = "EVIDENCE_REMOVED"
    DOCUMENT_PROCESSED = "DOCUMENT_PROCESSED"
    EVIDENCE_CANDIDATE_EXTRACTED = "EVIDENCE_CANDIDATE_EXTRACTED"
    DOCUMENTS_COMPARED = "DOCUMENTS_COMPARED"
    ANALYSIS_CREATED = "ANALYSIS_CREATED"
    ANALYSIS_UPDATED = "ANALYSIS_UPDATED"
    ANALYSIS_RUN_EXECUTED = "ANALYSIS_RUN_EXECUTED"
    ANALYSIS_DELETED = "ANALYSIS_DELETED"
    HYPOTHESIS_EVALUATED = "HYPOTHESIS_EVALUATED"
    FINDING_CREATED = "FINDING_CREATED"
    FINDING_UPDATED = "FINDING_UPDATED"
    FINDING_DELETED = "FINDING_DELETED"
    ASSUMPTION_SAVED = "ASSUMPTION_SAVED"
    SCENARIO_EVALUATED = "SCENARIO_EVALUATED"
    REPORT_CREATED = "REPORT_CREATED"
    REPORT_UPDATED = "REPORT_UPDATED"
    REPORT_FINALIZED = "REPORT_FINALIZED"
    REPORT_EXPORTED = "REPORT_EXPORTED"
    REPORT_DELETED = "REPORT_DELETED"
    THESIS_CREATED = "THESIS_CREATED"
    THESIS_UPDATED = "THESIS_UPDATED"
    REPORT_VERIFIED = "REPORT_VERIFIED"


class DocumentProcessingStatus(str, Enum):
    """Status of document parsing, sectioning, and table extraction."""
    NOT_STARTED = "NOT_STARTED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    RESTRICTED = "RESTRICTED"
    UNSUPPORTED = "UNSUPPORTED"


class DocumentFormat(str, Enum):
    """Source media format of financial research documents."""
    HTML = "HTML"
    PDF = "PDF"
    PLAIN_TEXT = "PLAIN_TEXT"
    MARKDOWN = "MARKDOWN"
    DOCX = "DOCX"
    XBRL_DATASET = "XBRL_DATASET"


class SearchMode(str, Enum):
    """Execution mode for research source discovery."""
    KEYWORD = "KEYWORD"
    EXACT_PHRASE = "EXACT_PHRASE"
    HYBRID = "HYBRID"


class DocumentComparisonMode(str, Enum):
    """Comparison scope for two research documents."""
    FULL_TEXT = "FULL_TEXT"
    SECTIONS = "SECTIONS"
    FINANCIAL_TABLES = "FINANCIAL_TABLES"


class UnitScale(str, Enum):
    """Numeric scale of extracted financial tables and disclosures."""
    EXACT = "EXACT"
    THOUSANDS = "THOUSANDS"
    MILLIONS = "MILLIONS"
    BILLIONS = "BILLIONS"
    PERCENTAGE = "PERCENTAGE"
    PER_SHARE = "PER_SHARE"


# ---------------------------------------------------------------------------
# Stage 106 — Research Analysis, Hypothesis & Findings Enums
# ---------------------------------------------------------------------------

class ResearchAnalysisType(str, Enum):
    """Controlled taxonomy of financial research analysis types."""
    COMPANY_FINANCIAL_TREND = "COMPANY_FINANCIAL_TREND"
    COMPANY_RATIO_ANALYSIS = "COMPANY_RATIO_ANALYSIS"
    CASH_FLOW_ANALYSIS = "CASH_FLOW_ANALYSIS"
    CAPITAL_STRUCTURE_ANALYSIS = "CAPITAL_STRUCTURE_ANALYSIS"
    PEER_BENCHMARKING = "PEER_BENCHMARKING"
    INDUSTRY_COMPARISON = "INDUSTRY_COMPARISON"
    MACROECONOMIC_TIME_SERIES = "MACROECONOMIC_TIME_SERIES"
    MULTI_INDICATOR_COMPARISON = "MULTI_INDICATOR_COMPARISON"
    HISTORICAL_MARKET_CONTEXT = "HISTORICAL_MARKET_CONTEXT"
    EVENT_DISCLOSURE_COMPARISON = "EVENT_DISCLOSURE_COMPARISON"
    HYPOTHESIS_EVALUATION = "HYPOTHESIS_EVALUATION"
    DESCRIPTIVE_STATISTICAL_ANALYSIS = "DESCRIPTIVE_STATISTICAL_ANALYSIS"
    ASSUMPTION_SENSITIVITY_ANALYSIS = "ASSUMPTION_SENSITIVITY_ANALYSIS"


class AnalysisExecutionStatus(str, Enum):
    """Lifecycle and execution state of a research analysis or run."""
    DRAFT = "DRAFT"
    CONFIGURED = "CONFIGURED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    OUTDATED = "OUTDATED"
    ARCHIVED = "ARCHIVED"


class AnalysisInputPolicy(str, Enum):
    """Policy for input data versioning and reproduction."""
    PINNED_SOURCE_VERSION = "PINNED_SOURCE_VERSION"
    LATEST_AUTHORIZED_DATA = "LATEST_AUTHORIZED_DATA"


class AnalysisFrequency(str, Enum):
    """Reporting and observation frequency for analytical time series."""
    ANNUAL = "ANNUAL"
    QUARTERLY = "QUARTERLY"
    TTM = "TTM"
    MONTHLY = "MONTHLY"
    DAILY = "DAILY"


class HypothesisEvaluationOutcome(str, Enum):
    """Outcomes for evidence-based hypothesis testing without fabricated proof."""
    CRITERIA_MET = "CRITERIA_MET"
    CRITERIA_NOT_MET = "CRITERIA_NOT_MET"
    MIXED_RESULTS = "MIXED_RESULTS"
    INCONCLUSIVE = "INCONCLUSIVE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INVALID_TEST = "INVALID_TEST"


class ResearchFindingType(str, Enum):
    """Explicit taxonomy distinguishing facts, calculations, and interpretations."""
    OBSERVED_FACT = "OBSERVED_FACT"
    CALCULATED_RESULT = "CALCULATED_RESULT"
    STATISTICAL_OBSERVATION = "STATISTICAL_OBSERVATION"
    ANALYST_INTERPRETATION = "ANALYST_INTERPRETATION"
    INCONCLUSIVE_RESULT = "INCONCLUSIVE_RESULT"


class ResearchFindingReviewStatus(str, Enum):
    """Peer and institutional review states for research findings."""
    DRAFT = "DRAFT"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEWED = "REVIEWED"
    REVISED = "REVISED"
    ARCHIVED = "ARCHIVED"


class AssumptionSourceType(str, Enum):
    """Provenance classification of analytical assumptions."""
    SOURCE_REPORTED = "SOURCE_REPORTED"
    ANALYST_ASSUMED = "ANALYST_ASSUMED"
    DERIVED = "DERIVED"


class ScenarioType(str, Enum):
    """Controlled scenario category for deterministic what-if sensitivity analysis."""
    BASE_ASSUMPTION = "BASE_ASSUMPTION"
    ALTERNATIVE_A = "ALTERNATIVE_A"
    ALTERNATIVE_B = "ALTERNATIVE_B"


class OutlierHandlingPolicy(str, Enum):
    """Explicit policy for handling statistical outliers."""
    INCLUDE_ALL = "INCLUDE_ALL"
    EXCLUDE_OUTLIERS = "EXCLUDE_OUTLIERS"
    WINSORIZE = "WINSORIZE"


class ResearchReportType(str, Enum):
    """Controlled taxonomy of financial research reports and synthesis documents."""
    COMPANY_RESEARCH = "COMPANY_RESEARCH"
    EQUITY_INITIATION_DRAFT = "EQUITY_INITIATION_DRAFT"
    COMPANY_UPDATE = "COMPANY_UPDATE"
    EARNINGS_REVIEW = "EARNINGS_REVIEW"
    INDUSTRY_RESEARCH = "INDUSTRY_RESEARCH"
    MACROECONOMIC_RESEARCH = "MACROECONOMIC_RESEARCH"
    FINANCIAL_EVENT_NOTE = "FINANCIAL_EVENT_NOTE"
    FUNDAMENTAL_ANALYSIS = "FUNDAMENTAL_ANALYSIS"
    PEER_BENCHMARKING = "PEER_BENCHMARKING"
    INVESTMENT_THESIS = "INVESTMENT_THESIS"
    RISK_RESEARCH_NOTE = "RISK_RESEARCH_NOTE"
    GENERAL_RESEARCH_MEMORANDUM = "GENERAL_RESEARCH_MEMORANDUM"


class ReportLifecycleStatus(str, Enum):
    """Lifecycle progression of a research report."""
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEWED = "REVIEWED"
    FINALIZED = "FINALIZED"
    ARCHIVED = "ARCHIVED"


class ReportSectionType(str, Enum):
    """Standardized institutional report section taxonomy."""
    EXECUTIVE_SUMMARY = "EXECUTIVE_SUMMARY"
    COMPANY_OVERVIEW = "COMPANY_OVERVIEW"
    BUSINESS_MODEL = "BUSINESS_MODEL"
    INDUSTRY_CONTEXT = "INDUSTRY_CONTEXT"
    FINANCIAL_PERFORMANCE = "FINANCIAL_PERFORMANCE"
    PROFITABILITY_CASH_FLOW = "PROFITABILITY_CASH_FLOW"
    CAPITAL_STRUCTURE = "CAPITAL_STRUCTURE"
    PEER_BENCHMARKING = "PEER_BENCHMARKING"
    INVESTMENT_THESIS = "INVESTMENT_THESIS"
    BULL_BEAR_CASE = "BULL_BEAR_CASE"
    VALUATION_CONTEXT = "VALUATION_CONTEXT"
    KEY_RISKS = "KEY_RISKS"
    CATALYSTS = "CATALYSTS"
    METHODOLOGY = "METHODOLOGY"
    REFERENCES = "REFERENCES"
    DISCLOSURES = "DISCLOSURES"
    CUSTOM = "CUSTOM"


class ReportBlockType(str, Enum):
    """Rich document content block taxonomy."""
    HEADING = "HEADING"
    PARAGRAPH = "PARAGRAPH"
    BULLET_LIST = "BULLET_LIST"
    NUMBERED_LIST = "NUMBERED_LIST"
    BLOCK_QUOTE = "BLOCK_QUOTE"
    FINANCIAL_TABLE = "FINANCIAL_TABLE"
    ANALYSIS_TABLE = "ANALYSIS_TABLE"
    CHART = "CHART"
    CALCULATION = "CALCULATION"
    CITATION = "CITATION"
    FOOTNOTE = "FOOTNOTE"
    PAGE_BREAK = "PAGE_BREAK"
    REFERENCES = "REFERENCES"


class ReportSnapshotPolicy(str, Enum):
    """Data pinning and historical reproducibility policy for report content."""
    DRAFT_LATEST_AUTHORIZED = "DRAFT_LATEST_AUTHORIZED"
    PINNED_SOURCE_REFERENCES = "PINNED_SOURCE_REFERENCES"
    FINALIZED_IMMUTABLE_SNAPSHOT = "FINALIZED_IMMUTABLE_SNAPSHOT"


class ThesisLifecycleStatus(str, Enum):
    """Analyst thesis lifecycle states."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REVISED = "REVISED"
    INVALIDATED = "INVALIDATED"
    ARCHIVED = "ARCHIVED"


class ThesisArgumentType(str, Enum):
    """Taxonomy of arguments in a structured investment thesis."""
    SUPPORTING = "SUPPORTING"
    OPPOSING = "OPPOSING"
    BULL_CASE = "BULL_CASE"
    BEAR_CASE = "BEAR_CASE"
    BASE_CASE = "BASE_CASE"
    ASSUMPTION = "ASSUMPTION"
    RISK = "RISK"
    CATALYST = "CATALYST"
    OPEN_QUESTION = "OPEN_QUESTION"


class ExportFormat(str, Enum):
    """Supported document export formats."""
    PDF = "PDF"
    DOCX = "DOCX"


class ExportStatus(str, Enum):
    """Background export job lifecycle states."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class VerificationIssueSeverity(str, Enum):
    """Severity tiers for report verification issues."""
    BLOCKING = "BLOCKING"
    WARNING = "WARNING"
    INFORMATIONAL = "INFORMATIONAL"


class VerificationIssueType(str, Enum):
    """Categories of automated verification checks."""
    MISSING_CITATION = "MISSING_CITATION"
    BROKEN_CITATION = "BROKEN_CITATION"
    SOURCE_RESTRICTED = "SOURCE_RESTRICTED"
    SOURCE_WITHDRAWN = "SOURCE_WITHDRAWN"
    SOURCE_REVISED = "SOURCE_REVISED"
    ANALYSIS_RUN_NOT_FOUND = "ANALYSIS_RUN_NOT_FOUND"
    ANALYSIS_RUN_OUTDATED = "ANALYSIS_RUN_OUTDATED"
    UNSUPPORTED_QUANTITATIVE_CLAIM = "UNSUPPORTED_QUANTITATIVE_CLAIM"
    MISSING_METHODOLOGY = "MISSING_METHODOLOGY"
    MISSING_DATA_PERIOD = "MISSING_DATA_PERIOD"
    MISSING_UNIT = "MISSING_UNIT"
    UNDISCLOSED_ASSUMPTION = "UNDISCLOSED_ASSUMPTION"
    POINT_IN_TIME_CONFLICT = "POINT_IN_TIME_CONFLICT"
    UNRESOLVED_CONTRADICTION = "UNRESOLVED_CONTRADICTION"
    STRUCTURE_INCOMPLETE = "STRUCTURE_INCOMPLETE"


# ---------------------------------------------------------------------------
# Stage 108 Collaboration, Review, Comments & Circulation Enums
# ---------------------------------------------------------------------------

class ResearchRole(str, Enum):
    """Institutional roles for collaborative research operations."""
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    REVIEWER = "REVIEWER"
    COMMENTER = "COMMENTER"
    VIEWER = "VIEWER"


class ResearchPrincipalType(str, Enum):
    """Types of principals permitted in research access grants."""
    USER = "USER"
    ORGANIZATION_ROLE = "ORGANIZATION_ROLE"


class ResearchResourceType(str, Enum):
    """Resource domains supporting collaborative research grants."""
    INVESTIGATION = "INVESTIGATION"
    REPORT = "REPORT"
    THESIS = "THESIS"


class ReviewScope(str, Enum):
    """Declared scope for an institutional review request."""
    FULL_REPORT = "FULL_REPORT"
    DOCUMENT_CONTENT = "DOCUMENT_CONTENT"
    SOURCE_EVIDENCE = "SOURCE_EVIDENCE"
    FINANCIAL_ANALYSIS = "FINANCIAL_ANALYSIS"
    EDITORIAL_QUALITY = "EDITORIAL_QUALITY"


class ReviewStatus(str, Enum):
    """Lifecycle state machine for institutional review cycles."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    SUPERSEDED = "SUPERSEDED"


class ReviewDecisionType(str, Enum):
    """Formal decision outcomes rendered by an authorized reviewer."""
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    REJECT = "REJECT"


class CommentAnchorType(str, Enum):
    """Anchor targets for review comments within research objects."""
    REPORT_SECTION = "REPORT_SECTION"
    REPORT_BLOCK = "REPORT_BLOCK"
    TEXT_RANGE = "TEXT_RANGE"
    CITATION = "CITATION"
    EVIDENCE_REFERENCE = "EVIDENCE_REFERENCE"
    ANALYSIS_RUN = "ANALYSIS_RUN"
    RESEARCH_FINDING = "RESEARCH_FINDING"


class CommentThreadStatus(str, Enum):
    """Resolution lifecycle for review comment threads."""
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    REOPENED = "REOPENED"
    OBSOLETE = "OBSOLETE"


class CirculationStatus(str, Enum):
    """Status of controlled internal research report circulation."""
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class ResearchAuditEventType(str, Enum):
    """Auditable actions in research collaboration and review operations."""
    GRANT_CREATED = "GRANT_CREATED"
    GRANT_UPDATED = "GRANT_UPDATED"
    GRANT_REVOKED = "GRANT_REVOKED"
    REVIEW_SUBMITTED = "REVIEW_SUBMITTED"
    REVIEW_ASSIGNED = "REVIEW_ASSIGNED"
    REVIEW_DECIDED = "REVIEW_DECIDED"
    REVIEW_CANCELED = "REVIEW_CANCELED"
    COMMENT_ADDED = "COMMENT_ADDED"
    COMMENT_RESOLVED = "COMMENT_RESOLVED"
    COMMENT_REOPENED = "COMMENT_REOPENED"
    QUALITY_GATE_RUN = "QUALITY_GATE_RUN"
    REPORT_CIRCULATED = "REPORT_CIRCULATED"
    CIRCULATION_REVOKED = "CIRCULATION_REVOKED"


# ---------------------------------------------------------------------------
# Stage 109 Knowledge, Dependency Lineage, Monitoring & Lifecycle Enums
# ---------------------------------------------------------------------------

class KnowledgeEntryType(str, Enum):
    """Controlled taxonomy of research artifacts indexed in the knowledge library."""
    RESEARCH_INVESTIGATION = "RESEARCH_INVESTIGATION"
    RESEARCH_NOTE = "RESEARCH_NOTE"
    RESEARCH_QUESTION = "RESEARCH_QUESTION"
    RESEARCH_HYPOTHESIS = "RESEARCH_HYPOTHESIS"
    RESEARCH_CLAIM = "RESEARCH_CLAIM"
    RESEARCH_EVIDENCE = "RESEARCH_EVIDENCE"
    RESEARCH_ANALYSIS = "RESEARCH_ANALYSIS"
    RESEARCH_FINDING = "RESEARCH_FINDING"
    RESEARCH_THESIS = "RESEARCH_THESIS"
    RESEARCH_REPORT = "RESEARCH_REPORT"
    RESEARCH_SOURCE_REFERENCE = "RESEARCH_SOURCE_REFERENCE"


class KnowledgeStatus(str, Enum):
    """Lifecycle status of a research knowledge entry."""
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    UNAVAILABLE = "UNAVAILABLE"


class KnowledgeSourceAvailability(str, Enum):
    """Current availability and entitlement state of underlying referenced source."""
    AVAILABLE = "AVAILABLE"
    RESTRICTED = "RESTRICTED"
    WITHDRAWN = "WITHDRAWN"
    UNKNOWN = "UNKNOWN"


class DependencyType(str, Enum):
    """Taxonomy of explicit dependencies linking research artifacts."""
    SOURCE_TO_EVIDENCE = "SOURCE_TO_EVIDENCE"
    EVIDENCE_TO_CLAIM = "EVIDENCE_TO_CLAIM"
    EVIDENCE_TO_FINDING = "EVIDENCE_TO_FINDING"
    SOURCE_TO_ANALYSIS = "SOURCE_TO_ANALYSIS"
    ANALYSIS_TO_FINDING = "ANALYSIS_TO_FINDING"
    FINDING_TO_THESIS = "FINDING_TO_THESIS"
    CLAIM_TO_THESIS = "CLAIM_TO_THESIS"
    THESIS_TO_REPORT = "THESIS_TO_REPORT"
    ANALYSIS_TO_REPORT = "ANALYSIS_TO_REPORT"
    REPORT_TO_REVISION = "REPORT_TO_REVISION"
    REVISION_TO_APPROVAL = "REVISION_TO_APPROVAL"
    DERIVED_REFERENCE = "DERIVED_REFERENCE"


class SourceChangeType(str, Enum):
    """Canonical source-change categories detected by continuous monitoring."""
    DOCUMENT_REVISED = "DOCUMENT_REVISED"
    DOCUMENT_AMENDED = "DOCUMENT_AMENDED"
    DOCUMENT_WITHDRAWN = "DOCUMENT_WITHDRAWN"
    DOCUMENT_ACCESS_RESTRICTED = "DOCUMENT_ACCESS_RESTRICTED"
    DOCUMENT_ACCESS_RESTORED = "DOCUMENT_ACCESS_RESTORED"
    FINANCIAL_FACT_RESTATED = "FINANCIAL_FACT_RESTATED"
    FINANCIAL_FACT_CORRECTED = "FINANCIAL_FACT_CORRECTED"
    FINANCIAL_FACT_WITHDRAWN = "FINANCIAL_FACT_WITHDRAWN"
    ECONOMIC_OBSERVATION_REVISED = "ECONOMIC_OBSERVATION_REVISED"
    ECONOMIC_RELEASE_CORRECTED = "ECONOMIC_RELEASE_CORRECTED"
    NEWS_ARTICLE_CORRECTED = "NEWS_ARTICLE_CORRECTED"
    NEWS_ARTICLE_WITHDRAWN = "NEWS_ARTICLE_WITHDRAWN"
    FINANCIAL_EVENT_STATUS_CHANGED = "FINANCIAL_EVENT_STATUS_CHANGED"
    SOURCE_RELATIONSHIP_CORRECTED = "SOURCE_RELATIONSHIP_CORRECTED"


class ImpactCategory(str, Enum):
    """Classification of impact exerted by a source change on research artifacts."""
    DIRECT_SOURCE_REFERENCE_CHANGED = "DIRECT_SOURCE_REFERENCE_CHANGED"
    DIRECT_DATA_INPUT_REVISED = "DIRECT_DATA_INPUT_REVISED"
    CITATION_LOCATION_STALE = "CITATION_LOCATION_STALE"
    SOURCE_ACCESS_RESTRICTED = "SOURCE_ACCESS_RESTRICTED"
    INDIRECT_DEPENDENCY_CHANGED = "INDIRECT_DEPENDENCY_CHANGED"
    POSSIBLE_INTERPRETATION_IMPACT = "POSSIBLE_INTERPRETATION_IMPACT"
    REVIEW_RECOMMENDED = "REVIEW_RECOMMENDED"
    NO_ACTION_REQUIRED = "NO_ACTION_REQUIRED"


class RevalidationStatus(str, Enum):
    """Execution lifecycle of an automated research revalidation request."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class RevalidationOutcome(str, Enum):
    """Outcome classification of an evidence revalidation run."""
    VALID_REFERENCES = "VALID_REFERENCES"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    REQUIRES_DATA_REFRESH = "REQUIRES_DATA_REFRESH"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_ACCESS_RESTRICTED = "SOURCE_ACCESS_RESTRICTED"
    REFERENCE_BROKEN = "REFERENCE_BROKEN"
    HISTORICALLY_VALID_AS_KNOWN_AT = "HISTORICALLY_VALID_AS_KNOWN_AT"
    FAILED = "FAILED"


class UpdateItemType(str, Enum):
    """Categories of actionable items in the research update queue."""
    SOURCE_CHANGE_REVIEW = "SOURCE_CHANGE_REVIEW"
    EVIDENCE_REVALIDATION = "EVIDENCE_REVALIDATION"
    ANALYSIS_REFRESH_SUGGESTED = "ANALYSIS_REFRESH_SUGGESTED"
    FINDING_REVIEW = "FINDING_REVIEW"
    THESIS_REVIEW = "THESIS_REVIEW"
    REPORT_REVIEW_REQUIRED = "REPORT_REVIEW_REQUIRED"
    SOURCE_ACCESS_ISSUE = "SOURCE_ACCESS_ISSUE"


class UpdateItemStatus(str, Enum):
    """Lifecycle status of a research update queue item."""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"
    SUPERSEDED = "SUPERSEDED"


class UpdateItemPriority(str, Enum):
    """Priority tiers for research update queue maintenance."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"



