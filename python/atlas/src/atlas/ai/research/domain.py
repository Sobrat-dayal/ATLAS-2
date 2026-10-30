"""ATLAS Stage 127: AI Research and Retrieval-Augmented Generation Domain Models.

Institutional-grade domain entities, enums, and dataclasses for:
- Multi-source document and revision registry
- Structural chunks, pages, and section hierarchies
- Bounded evidence extraction and claim-level grounding
- Server-authoritative citation lifecycle and verification
- Point-in-time historical research and revision lineage
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ResearchSourceType(str, Enum):
    """Canonical categories of research sources."""

    CORPORATE_FILING = "CORPORATE_FILING"  # 10-K, 10-Q, 8-K, 20-F
    EARNINGS_TRANSCRIPT = "EARNINGS_TRANSCRIPT"  # Quarterly earnings call transcripts
    RESEARCH_REPORT = "RESEARCH_REPORT"  # Equity/macro institutional research
    ECONOMIC_PUBLICATION = "ECONOMIC_PUBLICATION"  # Official central bank / statistical releases
    NEWS_ARTICLE = "NEWS_ARTICLE"  # Financial wire / curated press releases
    USER_DOCUMENT = "USER_DOCUMENT"  # Private user notes, memos, or internal presentations


class LicensingClass(str, Enum):
    """Licensing and distribution governance tier."""

    PUBLIC_DOMAIN = "PUBLIC_DOMAIN"  # Freely indexable and citeable (e.g. SEC EDGAR)
    PROPRIETARY_LICENSED = "PROPRIETARY_LICENSED"  # Licensed vendor content (excerpt-bounded)
    INTERNAL_CONFIDENTIAL = "INTERNAL_CONFIDENTIAL"  # Tenant internal research
    USER_PRIVATE = "USER_PRIVATE"  # Strict single-user private document


class ProviderDisclosurePolicy(str, Enum):
    """Governance over sending content to external model providers."""

    ALLOWED = "ALLOWED"  # Full passage text permitted
    REDACTED_ONLY = "REDACTED_ONLY"  # Anonymized / redacted entities permitted
    PROHIBITED = "PROHIBITED"  # Local model / strictly in-tenant only


class DocumentParsingStatus(str, Enum):
    """Document extraction pipeline state."""

    PENDING = "PENDING"
    PARSING = "PARSING"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"
    UNSUPPORTED = "UNSUPPORTED"


class DocumentIndexingStatus(str, Enum):
    """Vector and lexical indexing pipeline state."""

    PENDING = "PENDING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
    RESTRICTED = "RESTRICTED"


class RetrievalStrategy(str, Enum):
    """Search and retrieval execution strategy."""

    LEXICAL = "LEXICAL"  # BM25 / exact token match
    SEMANTIC = "SEMANTIC"  # Vector cosine similarity
    HYBRID_FUSION = "HYBRID_FUSION"  # Reciprocal Rank Fusion (RRF)
    HYBRID_RERANK = "HYBRID_RERANK"  # Fusion with cross-encoder reranking


class ResearchRunStatus(str, Enum):
    """Lifecycle state of an AI research generation run."""

    IDLE = "IDLE"
    PLANNING = "PLANNING"
    RETRIEVING = "RETRIEVING"
    RERANKING = "RERANKING"
    ASSEMBLING_EVIDENCE = "ASSEMBLING_EVIDENCE"
    GENERATING = "GENERATING"
    VALIDATING_CITATIONS = "VALIDATING_CITATIONS"
    COMPLETED = "COMPLETED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CitationValidationStatus(str, Enum):
    """Server-authoritative validation status for generated citations."""

    VERIFIED = "VERIFIED"  # Exactly matches retrieved, authorized evidence
    REJECTED = "REJECTED"  # Fabricated citation ID or unsupported quote
    ACCESS_DENIED = "ACCESS_DENIED"  # User lacks permission to source
    EXPIRED = "EXPIRED"  # Source was revoked after generation
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"  # Claim contradicts or exceeds source span


@dataclass(frozen=True)
class ResearchSource:
    """Canonical registry entry for a research source or repository."""

    source_id: str
    name: str
    category: ResearchSourceType
    licensing_class: LicensingClass
    provider_disclosure: ProviderDisclosurePolicy
    publisher: str
    reliability_tier: str  # "PRIMARY_REGULATORY", "PRIMARY_OFFICIAL", "BROKER_CONSENSUS", "FINANCIAL_WIRE", "USER_INTERNAL"
    owner_user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ResearchDocument:
    """Canonical document record representing an immutable filing, transcript, or memo."""

    document_id: str
    source_id: str
    title: str
    document_type: str  # "10-K", "10-Q", "TRANSCRIPT", "CAPEX_PLAN", "MACRO_REPORT"
    publication_date: str  # ISO 8601 (e.g. "2025-03-01T00:00:00Z")
    company_id: Optional[str] = None
    symbol: Optional[str] = None
    filing_date: Optional[str] = None
    period_end_date: Optional[str] = None
    access_tier: str = "PUBLIC"  # "PUBLIC", "INSTITUTIONAL", "CONFIDENTIAL", "USER_PRIVATE"
    owner_user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    is_revoked: bool = False
    content_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ResearchDocumentRevision:
    """Document revision or restatement representing point-in-time financial truth."""

    revision_id: str
    document_id: str
    revision_number: int
    effective_date: str  # When this revision became effective / published
    as_of_date: str  # Point-in-time accounting cutoff date
    is_restatement: bool = False
    content_hash: str = ""
    summary: Optional[str] = None


@dataclass(frozen=True)
class ResearchChunk:
    """Structurally bounded passage belonging to a single document revision."""

    chunk_id: str
    document_id: str
    revision_id: str
    chunk_index: int
    section_title: str
    page_number: int
    raw_text: str
    clean_text: str
    char_start: int
    char_end: int
    token_estimate: int
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResearchEvidence:
    """Verified, bounded evidence unit extracted from an indexed chunk."""

    evidence_id: str
    chunk_id: str
    document_id: str
    revision_id: str
    title: str
    page_number: int
    section_title: str
    publication_date: str
    effective_date: str
    exact_span: str
    context_snippet: str
    relevance_score: float
    licensing_class: LicensingClass
    content_hash: str
    symbol: Optional[str] = None
    publisher: Optional[str] = None


@dataclass(frozen=True)
class ResearchCitation:
    """Structured citation tying a generated assertion to a verified evidence unit."""

    citation_id: str
    evidence_id: str
    document_id: str
    title: str
    page_number: int
    section_title: str
    publication_date: str
    claim_text: str
    quote_span: str
    status: CitationValidationStatus
    symbol: Optional[str] = None
    validation_reason: Optional[str] = None


@dataclass(frozen=True)
class ResearchQueryPlan:
    """Deterministic retrieval execution plan formulated before search."""

    plan_id: str
    query: str
    target_symbols: List[str]
    document_types: List[str]
    retrieval_strategy: RetrievalStrategy
    max_evidence_units: int = 5
    token_budget: int = 4000
    historical_as_of: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None


@dataclass(frozen=True)
class ResearchSourceManifest:
    """Manifest of all evaluated, used, and filtered sources for auditability."""

    manifest_id: str
    run_id: str
    sources_used: List[Dict[str, Any]]
    total_sources_evaluated: int
    excluded_sources_count: int
    coverage_summary: str
    has_conflicting_sources: bool = False
    conflict_notes: Optional[str] = None


@dataclass
class AiResearchRun:
    """Complete execution record for a grounded financial research workflow."""

    run_id: str
    user_id: str
    tenant_id: str
    query: str
    status: ResearchRunStatus
    strategy: RetrievalStrategy
    answer_text: str = ""
    citations: List[ResearchCitation] = field(default_factory=list)
    evidence_manifest: Optional[ResearchSourceManifest] = None
    limitations: List[str] = field(default_factory=list)
    conversation_id: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    execution_time_ms: float = 0.0
