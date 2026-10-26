"""Domain dataclasses for Regulatory Company Filings Intelligence (Stage 86)."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional

from .enums import (
    AmendmentStatus,
    DocumentMediaType,
    FilingCategory,
    FilingForm,
    IngestionStatus,
    Regulator,
    XBRLContextPeriodType,
    XBRLUnitType,
)


@dataclass
class FilingDocument:
    """A specific document or exhibit file attached to a regulatory submission."""

    document_id: str
    filing_id: str
    filename: str
    document_type: str  # e.g. "10-K", "EX-99.1", "EX-31.1", "EX-101.INS"
    description: str
    media_type: DocumentMediaType
    byte_size: int
    content_hash: str  # SHA-256
    source_url: str
    is_primary: bool = False
    content_raw: Optional[str] = None


@dataclass
class XBRLFact:
    """A normalized, context-qualified XBRL financial fact extracted from a filing."""

    fact_id: str
    filing_id: str
    taxonomy_namespace: str  # e.g. "us-gaap", "dei"
    concept_name: str  # e.g. "Revenues", "NetIncomeLoss", "CommonStockSharesOutstanding"
    label: str  # Human readable label
    period_type: XBRLContextPeriodType  # INSTANT or DURATION
    period_end: str  # ISO date YYYY-MM-DD
    period_start: Optional[str] = None  # None for INSTANT
    unit: XBRLUnitType = XBRLUnitType.USD
    exact_value: Decimal = Decimal("0")
    formatted_value: str = ""
    decimals: Optional[int] = None
    dimensions: Dict[str, str] = field(default_factory=dict)  # e.g. {"Segment": "Services"}
    source_document_id: Optional[str] = None


@dataclass
class FilingSection:
    """A verified structural item or section within a regulatory filing."""

    item_id: str  # e.g. "ITEM_1", "ITEM_1A", "ITEM_7", "ITEM_8"
    title: str  # e.g. "Item 1. Business", "Item 1A. Risk Factors", "Item 7. MD&A"
    anchor: str  # DOM anchor or heading offset
    char_offset: int
    char_length: int
    summary_excerpt: Optional[str] = None


@dataclass
class RegulatoryFiling:
    """Canonical representation of a verified regulatory submission."""

    filing_id: str
    company_id: str
    filer_cik: str
    filer_name: str
    regulator: Regulator
    accession_number: str  # Official SEC accession format: 0000320193-24-000106
    form_type: str  # 10-K, 10-Q, 8-K, DEF 14A, etc.
    canonical_form: FilingForm
    category: FilingCategory
    reporting_period: str  # Date of period end, e.g. "2024-09-28"
    filing_date: str  # Date submitted to regulator, e.g. "2024-11-01"
    acceptance_timestamp: Optional[str] = None  # Exact timestamp e.g. "2024-11-01T18:02:15Z"
    publication_timestamp: Optional[str] = None
    is_amendment: bool = False
    amendment_status: AmendmentStatus = AmendmentStatus.ORIGINAL
    amends_accession_number: Optional[str] = None
    primary_document_name: str = ""
    primary_document_url: str = ""
    title: str = ""
    ingestion_status: IngestionStatus = IngestionStatus.PARSED
    documents: List[FilingDocument] = field(default_factory=list)
    sections: List[FilingSection] = field(default_factory=list)
    xbrl_facts: List[XBRLFact] = field(default_factory=list)
    full_text_indexed: bool = True
    content_html: Optional[str] = None
    content_text: Optional[str] = None


@dataclass
class FilingSearchHit:
    """Full-text search hit within a regulatory filing."""

    filing_id: str
    document_id: str
    accession_number: str
    form_type: str
    reporting_period: str
    filing_date: str
    section_name: Optional[str]
    matched_snippet: str
    char_offset: int
    score: float


@dataclass
class SectionDiff:
    """Textual diff for a specific document section."""

    section_name: str
    added_lines_count: int
    removed_lines_count: int
    diff_text: str  # Unified diff representation


@dataclass
class XBRLFactDiff:
    """Differential analysis between identical XBRL concepts across filings."""

    concept_name: str
    label: str
    period_label: str
    unit: str
    prior_value: Decimal
    current_value: Decimal
    absolute_difference: Decimal
    percentage_difference: Optional[Decimal]
    is_restatement: bool = False


@dataclass
class FilingComparisonResult:
    """Comparison results between two filings (amendment or period-over-period)."""

    left_filing_id: str
    right_filing_id: str
    left_accession: str
    right_accession: str
    comparison_type: str  # "AMENDMENT" or "PERIOD_OVER_PERIOD"
    left_filing_date: str
    right_filing_date: str
    text_diff_sections: List[SectionDiff] = field(default_factory=list)
    xbrl_fact_diffs: List[XBRLFactDiff] = field(default_factory=list)
    total_text_changes: int = 0
    total_fact_adjustments: int = 0
