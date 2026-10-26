"""Pydantic DTOs for Regulatory Company Filings Intelligence (Stage 86)."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .enums import (
    AmendmentStatus,
    DocumentMediaType,
    FilingCategory,
    Regulator,
    XBRLContextPeriodType,
    XBRLUnitType,
)


class FilingDocumentDTO(BaseModel):
    """Document or attachment exhibit in a filing."""

    document_id: str
    filename: str
    document_type: str
    description: str
    media_type: DocumentMediaType
    byte_size: int
    content_hash: str
    source_url: str
    is_primary: bool = False


class FilingSectionDTO(BaseModel):
    """Structural item or chapter section."""

    item_id: str
    title: str
    anchor: str
    char_offset: int
    char_length: int
    summary_excerpt: Optional[str] = None


class XBRLFactDTO(BaseModel):
    """Normalized XBRL financial fact."""

    fact_id: str
    concept_name: str
    label: str
    period_type: XBRLContextPeriodType
    period_end: str
    period_start: Optional[str] = None
    unit: XBRLUnitType
    exact_value: float
    formatted_value: str
    decimals: Optional[int] = None
    dimensions: Dict[str, str] = Field(default_factory=dict)


class XBRLFactsResponseDTO(BaseModel):
    """Extracted XBRL facts response container."""

    filing_id: str
    accession_number: str
    total_count: int
    items: List[XBRLFactDTO] = Field(default_factory=list)


class FilingSummaryDTO(BaseModel):
    """Summary item for filing catalog and lists."""

    filing_id: str
    company_id: str
    filer_cik: str
    filer_name: str
    regulator: Regulator
    accession_number: str
    form_type: str
    category: FilingCategory
    reporting_period: str
    filing_date: str
    acceptance_timestamp: Optional[str] = None
    publication_timestamp: Optional[str] = None
    is_amendment: bool = False
    amendment_status: AmendmentStatus = AmendmentStatus.ORIGINAL
    amends_accession_number: Optional[str] = None
    primary_document_name: str = ""
    title: str = ""
    document_count: int = 0
    fact_count: int = 0


class FilingCatalogResponseDTO(BaseModel):
    """Paginated catalog response of regulatory filings."""

    company_id: str
    total_count: int
    limit: int
    offset: int
    items: List[FilingSummaryDTO] = Field(default_factory=list)


class FilingDetailDTO(BaseModel):
    """Comprehensive filing record with document catalog and sections."""

    filing_id: str
    company_id: str
    filer_cik: str
    filer_name: str
    regulator: Regulator
    accession_number: str
    form_type: str
    category: FilingCategory
    reporting_period: str
    filing_date: str
    acceptance_timestamp: Optional[str] = None
    publication_timestamp: Optional[str] = None
    is_amendment: bool = False
    amendment_status: AmendmentStatus = AmendmentStatus.ORIGINAL
    amends_accession_number: Optional[str] = None
    primary_document_name: str
    primary_document_url: str
    title: str
    documents: List[FilingDocumentDTO] = Field(default_factory=list)
    sections: List[FilingSectionDTO] = Field(default_factory=list)
    fact_count: int = 0
    full_text_indexed: bool = True


class FilingContentDTO(BaseModel):
    """Sanitized document content payload for viewing."""

    filing_id: str
    document_id: str
    accession_number: str
    filename: str
    media_type: DocumentMediaType
    content_html: Optional[str] = None
    content_text: Optional[str] = None


class FilingSearchHitDTO(BaseModel):
    """Search match snippet with filing metadata."""

    filing_id: str
    document_id: str
    accession_number: str
    form_type: str
    reporting_period: str
    filing_date: str
    section_name: Optional[str] = None
    matched_snippet: str
    char_offset: int
    score: float


class FilingSearchResponseDTO(BaseModel):
    """Search results response container."""

    company_id: str
    query: str
    total_hits: int
    hits: List[FilingSearchHitDTO] = Field(default_factory=list)


class SectionDiffDTO(BaseModel):
    """Section level line difference."""

    section_name: str
    added_lines_count: int
    removed_lines_count: int
    diff_text: str


class XBRLFactDiffDTO(BaseModel):
    """XBRL fact variance item."""

    concept_name: str
    label: str
    period_label: str
    unit: str
    prior_value: float
    current_value: float
    absolute_difference: float
    percentage_difference: Optional[float] = None
    is_restatement: bool = False


class FilingComparisonResponseDTO(BaseModel):
    """Comparison response comparing two filings."""

    left_filing_id: str
    right_filing_id: str
    left_accession: str
    right_accession: str
    comparison_type: str
    left_filing_date: str
    right_filing_date: str
    text_diff_sections: List[SectionDiffDTO] = Field(default_factory=list)
    xbrl_fact_diffs: List[XBRLFactDiffDTO] = Field(default_factory=list)
    total_text_changes: int = 0
    total_fact_adjustments: int = 0


class FilingCoverageDTO(BaseModel):
    """Regulatory coverage and availability metadata."""

    company_id: str
    company_name: str
    regulator: Regulator
    filer_cik: str
    total_filings: int
    forms_available: List[str]
    latest_filing_date: Optional[str] = None
    oldest_filing_date: Optional[str] = None
    source_policy: str
    user_agent_configured: str


class FilingSourceReferenceDTO(BaseModel):
    """Official regulatory source provenance reference."""

    filing_id: str
    regulator: Regulator
    accession_number: str
    filer_cik: str
    official_url: str
    primary_document_url: str
    content_hash: str
    retrieved_timestamp: str
    source_attribution: str
    license_tier: str
