"""Pydantic Request and Response Schemas for Stage 127: AI Research and RAG.

Enforces strict typed contracts, argument bounds, and server-derived security fields.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from atlas.ai.research.domain import (
    CitationValidationStatus,
    LicensingClass,
    ResearchRunStatus,
    RetrievalStrategy,
)


class ResearchSearchRequest(BaseModel):
    """Client request for hybrid document and passage search."""

    query: str = Field(
        ..., min_length=1, max_length=1000, description="Analytical query or keyword string"
    )
    company_ids: Optional[List[str]] = Field(
        None, description="Optional target canonical company IDs"
    )
    symbols: Optional[List[str]] = Field(
        None, description="Optional target ticker symbols (e.g. ['AAPL', 'TEST_COMPANY'])"
    )
    document_types: Optional[List[str]] = Field(
        None, description="Filing or document types (e.g. ['10-K', 'TRANSCRIPT'])"
    )
    source_ids: Optional[List[str]] = Field(
        None, description="Filter to specific registered source IDs"
    )
    historical_as_of: Optional[str] = Field(
        None, description="ISO timestamp cutoff for historical point-in-time search"
    )
    date_start: Optional[str] = Field(None, description="Earliest publication date filter")
    date_end: Optional[str] = Field(None, description="Latest publication date filter")
    retrieval_strategy: RetrievalStrategy = Field(
        RetrievalStrategy.HYBRID_FUSION, description="Search strategy"
    )
    limit: int = Field(
        5, ge=1, le=25, description="Maximum number of evidence units or passages to retrieve"
    )


class ResearchPassageDTO(BaseModel):
    """Retrieved passage or chunk result."""

    chunk_id: str
    document_id: str
    revision_id: str
    title: str
    symbol: Optional[str] = None
    section_title: str
    page_number: int
    publication_date: str
    snippet: str
    exact_span: str
    relevance_score: float
    licensing_class: LicensingClass
    content_hash: str


class ResearchSearchResponse(BaseModel):
    """Response containing retrieved authorized passages and search metadata."""

    query: str
    total_hits: int
    retrieval_strategy: RetrievalStrategy
    historical_as_of: Optional[str] = None
    passages: List[ResearchPassageDTO]
    execution_time_ms: float


class ResearchQueryRequest(BaseModel):
    """Request to initiate grounded AI research generation."""

    query: str = Field(
        ..., min_length=2, max_length=2000, description="Financial research question"
    )
    symbols: Optional[List[str]] = Field(None, description="Target ticker symbols")
    document_types: Optional[List[str]] = Field(None, description="Allowed document types")
    historical_as_of: Optional[str] = Field(
        None, description="Historical as-of cutoff date (avoids look-ahead bias)"
    )
    date_start: Optional[str] = Field(None, description="Start date")
    date_end: Optional[str] = Field(None, description="End date")
    retrieval_strategy: RetrievalStrategy = Field(
        RetrievalStrategy.HYBRID_FUSION, description="Retrieval strategy"
    )
    max_evidence_units: int = Field(
        5, ge=1, le=15, description="Max evidence units to feed into synthesis"
    )
    token_budget: int = Field(
        4000, ge=500, le=16000, description="Token budget for assembled context"
    )
    conversation_id: Optional[str] = Field(None, description="Existing conversation to link run to")


class ResearchCitationDTO(BaseModel):
    """Citation metadata validating claim grounding."""

    citation_id: str
    evidence_id: str
    document_id: str
    symbol: Optional[str] = None
    title: str
    page_number: int
    section_title: str
    publication_date: str
    claim_text: str
    quote_span: str
    status: CitationValidationStatus
    validation_reason: Optional[str] = None


class ResearchSourceManifestDTO(BaseModel):
    """Source usage, coverage, and exclusion summary."""

    manifest_id: str
    run_id: str
    sources_used: List[Dict[str, Any]]
    total_sources_evaluated: int
    excluded_sources_count: int
    coverage_summary: str
    has_conflicting_sources: bool = False
    conflict_notes: Optional[str] = None


class ResearchAnswerResponse(BaseModel):
    """Grounded AI research answer with claim-level citations and verified evidence."""

    run_id: str
    query: str
    status: ResearchRunStatus
    strategy: RetrievalStrategy
    answer_text: str
    citations: List[ResearchCitationDTO]
    evidence_manifest: Optional[ResearchSourceManifestDTO] = None
    limitations: List[str] = Field(default_factory=list)
    source_count: int
    execution_time_ms: float
    historical_as_of: Optional[str] = None
    generated_at: str


class DocumentComparisonRequest(BaseModel):
    """Structured request to compare two document revisions or filings."""

    document_id_a: str = Field(..., description="First document ID")
    document_id_b: str = Field(..., description="Second document ID")
    aspects: Optional[List[str]] = Field(
        None, description="Specific aspects to compare, e.g. ['CAPEX', 'REVENUE', 'RISKS']"
    )
    historical_as_of: Optional[str] = Field(None, description="Point-in-time cutoff")


class ComparisonDifferenceDTO(BaseModel):
    """Specific variance identified between two documents."""

    aspect: str
    doc_a_value: str
    doc_b_value: str
    difference_text: str
    citation_a: Optional[Dict[str, Any]] = None
    citation_b: Optional[Dict[str, Any]] = None


class DocumentComparisonResponse(BaseModel):
    """Grounded comparison analysis result between two documents."""

    comparison_id: str
    document_a_title: str
    document_b_title: str
    document_a_date: str
    document_b_date: str
    differences: List[ComparisonDifferenceDTO]
    summary_text: str
    citations: List[Dict[str, Any]]
    execution_time_ms: float


class IngestDocumentRequest(BaseModel):
    """Request to ingest and index a document."""

    source_id: str = Field(..., description="Registered source ID")
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., description="e.g. '10-K', 'MEMO'")
    publication_date: str = Field(..., description="Publication ISO timestamp")
    symbol: Optional[str] = None
    company_id: Optional[str] = None
    filing_date: Optional[str] = None
    content_text: str = Field(..., min_length=10, description="Full raw text of document")
    access_tier: str = Field(
        "PUBLIC", description="PUBLIC, INSTITUTIONAL, CONFIDENTIAL, or USER_PRIVATE"
    )


class IngestDocumentResponse(BaseModel):
    """Ingestion job confirmation."""

    job_id: str
    document_id: str
    revision_id: str
    chunks_created: int
    indexing_status: str
    content_hash: str
