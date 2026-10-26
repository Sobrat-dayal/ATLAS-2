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
