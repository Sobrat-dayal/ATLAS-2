"""Institutional Research Document Processing, Structure Extraction & Comparison Engine (Stage 105).

Provides:
- Canonical document parsing, hierarchy extraction, and span offset indexing.
- Structured financial table extraction preserving periods, units, currency, and numerical matrix.
- In-document lexical search with highlight snippets and exact location anchors.
- Two-document textual comparison with section alignment and unified diffing.
- Financial fact variance calculation (absolute delta and percentage change with zero-base protection).
- Evidence candidate extraction and location validation.
"""

from __future__ import annotations

import datetime
import difflib
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from atlas.research.domain import (
    DocumentComparisonResult,
    DocumentComparisonSectionDiff,
    DocumentSearchHit,
    FinancialFactComparison,
    ResearchDocumentProcessingRecord,
    ResearchDocumentSection,
    ResearchDocumentSpan,
    ResearchDocumentTable,
    ResearchEvidenceCandidate,
)
from atlas.research.enums import (
    DocumentComparisonMode,
    DocumentFormat,
    DocumentProcessingStatus,
    EvidenceLocationType,
    UnitScale,
)


@dataclass
class ParsedDocumentData:
    """Internal container for a fully parsed and indexed research document."""
    document_id: str
    source_reference_id: str
    canonical_entity_id: Optional[str]
    title: str
    reporting_period: Optional[str]
    source_revision: str
    format: DocumentFormat
    full_text: str
    sections: List[ResearchDocumentSection] = field(default_factory=list)
    spans: List[ResearchDocumentSpan] = field(default_factory=list)
    tables: List[ResearchDocumentTable] = field(default_factory=list)
    processing_record: Optional[ResearchDocumentProcessingRecord] = None


def _clean_text(text: str) -> str:
    """Normalize whitespace without removing paragraph boundaries."""
    return re.sub(r"[ \t]+", " ", text).strip()


def build_canonical_documents_registry() -> Dict[str, ParsedDocumentData]:
    """Construct verified, pre-indexed document data models for canonical research sources."""
    registry: Dict[str, ParsedDocumentData] = {}

    # =========================================================================
    # 1. Apple Inc. Form 10-K (FY2024 ended Sept 28, 2024)
    # =========================================================================
    aapl_2024_text = (
        "UNITED STATES SECURITIES AND EXCHANGE COMMISSION\n"
        "Washington, D.C. 20549\n"
        "FORM 10-K\n"
        "ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934\n"
        "For the fiscal year ended September 28, 2024\n"
        "Commission File Number: 001-36743\n"
        "Apple Inc.\n\n"
        "Item 1. Business\n"
        "Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, "
        "wearables and accessories, and sells a variety of related services. The Company's fiscal "
        "year is the 52- or 53-week period that ends on the last Saturday of September.\n"
        "Products include iPhone, Mac, iPad, and Wearables, Home and Accessories. "
        "Services include Advertising, AppleCare, Cloud Services, Digital Content and Payment Services.\n\n"
        "Item 1A. Risk Factors\n"
        "The Company's business, results of operations and financial condition can be adversely affected by "
        "global and regional economic conditions, highly competitive global markets, supply chain disruptions, "
        "geopolitical conflicts, rapid technological changes, and complex regulatory challenges across major jurisdictions. "
        "The Company relies on single-source or limited-source suppliers for certain key components, and outsourced "
        "manufacturing partners primarily located in Asia. Semiconductor supply constraints and trade tensions could "
        "materially impact production schedules and margins.\n\n"
        "Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations\n"
        "Total net sales increased 2% or $7.7 billion to $391.0 billion in fiscal 2024 compared to $383.3 billion in fiscal 2023, "
        "driven by growth in Services and iPhone. Services net sales reached an all-time record of $96.2 billion in 2024 compared to "
        "$85.2 billion in 2023. Products net sales were $294.9 billion compared to $298.1 billion in 2023. "
        "Gross margin expanded to 46.2% compared to 44.1% in 2023, reflecting favorable product mix and Services strength. "
        "Operating expenses were $57.5 billion, representing 14.7% of total net sales.\n\n"
        "Item 8. Financial Statements and Supplementary Data\n"
        "Consolidated Statements of Operations (in millions, except per share amounts):\n"
        "Total net sales: $391,035 in FY2024, $383,285 in FY2023.\n"
        "Cost of sales: $210,352 in FY2024, $214,137 in FY2023.\n"
        "Gross margin: $180,683 in FY2024, $169,148 in FY2023.\n"
        "Research and development: $31,370 in FY2024, $29,915 in FY2023.\n"
        "Selling, general and administrative: $26,097 in FY2024, $24,932 in FY2023.\n"
        "Total operating expenses: $57,467 in FY2024, $54,847 in FY2023.\n"
        "Operating income: $123,216 in FY2024, $114,301 in FY2023.\n"
        "Net income: $93,736 in FY2024, $96,995 in FY2023.\n"
        "Diluted earnings per share: $6.08 in FY2024, $6.13 in FY2023.\n"
    )

    aapl_2024_doc = ParsedDocumentData(
        document_id="0000320193-24-000106",
        source_reference_id="src-filing-aapl-10k-2024",
        canonical_entity_id="AAPL",
        title="Apple Inc. Form 10-K Annual Report (Fiscal Year ended September 28, 2024)",
        reporting_period="FY2024",
        source_revision="1",
        format=DocumentFormat.HTML,
        full_text=aapl_2024_text,
    )

    # Sections
    aapl_2024_doc.sections = [
        ResearchDocumentSection(
            section_id="sec-aapl-2024-item1",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            heading="Item 1. Business",
            section_path="Part I > Item 1. Business",
            level=1,
            page_number=1,
            start_char_offset=aapl_2024_text.find("Item 1. Business"),
            end_char_offset=aapl_2024_text.find("Item 1A. Risk Factors"),
            text_preview="Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets...",
        ),
        ResearchDocumentSection(
            section_id="sec-aapl-2024-item1a",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            heading="Item 1A. Risk Factors",
            section_path="Part I > Item 1A. Risk Factors",
            level=1,
            page_number=6,
            start_char_offset=aapl_2024_text.find("Item 1A. Risk Factors"),
            end_char_offset=aapl_2024_text.find("Item 7. Management's Discussion"),
            text_preview="The Company's business, results of operations and financial condition can be adversely affected by...",
        ),
        ResearchDocumentSection(
            section_id="sec-aapl-2024-item7",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            heading="Item 7. Management's Discussion and Analysis",
            section_path="Part II > Item 7. MD&A",
            level=1,
            page_number=22,
            start_char_offset=aapl_2024_text.find("Item 7. Management's Discussion"),
            end_char_offset=aapl_2024_text.find("Item 8. Financial Statements"),
            text_preview="Total net sales increased 2% or $7.7 billion to $391.0 billion in fiscal 2024...",
        ),
        ResearchDocumentSection(
            section_id="sec-aapl-2024-item8",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            heading="Item 8. Financial Statements and Supplementary Data",
            section_path="Part II > Item 8. Financial Statements",
            level=1,
            page_number=45,
            start_char_offset=aapl_2024_text.find("Item 8. Financial Statements"),
            end_char_offset=len(aapl_2024_text),
            text_preview="Consolidated Statements of Operations (in millions, except per share amounts)...",
        ),
    ]

    # Spans
    aapl_2024_doc.spans = [
        ResearchDocumentSpan(
            span_id="span-aapl-2024-001",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            section_id="sec-aapl-2024-item1",
            page_number=1,
            paragraph_number=1,
            start_char_offset=aapl_2024_text.find("Apple Inc. designs, manufactures"),
            end_char_offset=aapl_2024_text.find("Services include Advertising") + len("Services include Advertising, AppleCare, Cloud Services, Digital Content and Payment Services."),
            text="Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services.",
        ),
        ResearchDocumentSpan(
            span_id="span-aapl-2024-002",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            section_id="sec-aapl-2024-item1a",
            page_number=6,
            paragraph_number=1,
            start_char_offset=aapl_2024_text.find("The Company relies on single-source"),
            end_char_offset=aapl_2024_text.find("production schedules and margins.") + len("production schedules and margins."),
            text="The Company relies on single-source or limited-source suppliers for certain key components, and outsourced manufacturing partners primarily located in Asia.",
        ),
        ResearchDocumentSpan(
            span_id="span-aapl-2024-003",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            section_id="sec-aapl-2024-item7",
            page_number=22,
            paragraph_number=1,
            start_char_offset=aapl_2024_text.find("Total net sales increased 2%"),
            end_char_offset=aapl_2024_text.find("Services and iPhone.") + len("Services and iPhone."),
            text="Total net sales increased 2% or $7.7 billion to $391.0 billion in fiscal 2024 compared to $383.3 billion in fiscal 2023, driven by growth in Services and iPhone.",
        ),
        ResearchDocumentSpan(
            span_id="span-aapl-2024-004",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            section_id="sec-aapl-2024-item7",
            page_number=22,
            paragraph_number=2,
            start_char_offset=aapl_2024_text.find("Services net sales reached an all-time record"),
            end_char_offset=aapl_2024_text.find("Services strength.") + len("Services strength."),
            text="Services net sales reached an all-time record of $96.2 billion in 2024 compared to $85.2 billion in 2023. Gross margin expanded to 46.2% compared to 44.1% in 2023.",
        ),
    ]

    # Extracted Tables
    aapl_2024_doc.tables = [
        ResearchDocumentTable(
            table_id="tbl-aapl-2024-operations",
            canonical_document_id="0000320193-24-000106",
            source_reference_id="src-filing-aapl-10k-2024",
            source_revision="1",
            title="Consolidated Statements of Operations",
            period_label="FY2024 vs FY2023",
            currency="USD",
            unit_scale=UnitScale.MILLIONS,
            headers=["Consolidated Statements of Operations", "FY 2024", "FY 2023"],
            row_labels=[
                "Total net sales",
                "Cost of sales",
                "Gross margin",
                "Research and development",
                "Selling, general and administrative",
                "Total operating expenses",
                "Operating income",
                "Net income",
                "Diluted earnings per share (in USD)",
            ],
            cells=[
                ["Total net sales", "$391,035", "$383,285"],
                ["Cost of sales", "$210,352", "$214,137"],
                ["Gross margin", "$180,683", "$169,148"],
                ["Research and development", "$31,370", "$29,915"],
                ["Selling, general and administrative", "$26,097", "$24,932"],
                ["Total operating expenses", "$57,467", "$54,847"],
                ["Operating income", "$123,216", "$114,301"],
                ["Net income", "$93,736", "$96,995"],
                ["Diluted earnings per share (in USD)", "$6.08", "$6.13"],
            ],
            raw_values=[
                [391035.0, 383285.0],
                [210352.0, 214137.0],
                [180683.0, 169148.0],
                [31370.0, 29915.0],
                [26097.0, 24932.0],
                [57467.0, 54847.0],
                [123216.0, 114301.0],
                [93736.0, 96995.0],
                [6.08, 6.13],
            ],
            section_id="sec-aapl-2024-item8",
            footnotes=["As reported under US GAAP. Net sales include Product and Services revenue."],
            associated_fact_ids=["fact-aapl-total-net-sales-fy2024", "fact-aapl-operating-income-fy2024"],
        )
    ]

    aapl_2024_doc.processing_record = ResearchDocumentProcessingRecord(
        processing_id="proc-aapl-2024-10k",
        canonical_document_id="0000320193-24-000106",
        source_reference_id="src-filing-aapl-10k-2024",
        source_revision="1",
        source_format=DocumentFormat.HTML,
        processor_version="v105.0-institutional",
        processing_status=DocumentProcessingStatus.COMPLETED,
        started_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
        completed_at=datetime.datetime(2024, 11, 1, 16, 14, tzinfo=datetime.timezone.utc),
        extracted_section_count=len(aapl_2024_doc.sections),
        extracted_table_count=len(aapl_2024_doc.tables),
        extracted_span_count=len(aapl_2024_doc.spans),
        content_rights_status="PUBLIC_DOMAIN_REGULATORY",
    )

    registry["0000320193-24-000106"] = aapl_2024_doc
    registry["src-filing-aapl-10k-2024"] = aapl_2024_doc

    # =========================================================================
    # 2. Apple Inc. Form 10-K (FY2023 ended Sept 30, 2023)
    # =========================================================================
    aapl_2023_text = (
        "UNITED STATES SECURITIES AND EXCHANGE COMMISSION\n"
        "Washington, D.C. 20549\n"
        "FORM 10-K\n"
        "ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934\n"
        "For the fiscal year ended September 30, 2023\n"
        "Commission File Number: 001-36743\n"
        "Apple Inc.\n\n"
        "Item 1. Business\n"
        "Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, "
        "wearables and accessories, and sells a variety of related services. The Company's fiscal "
        "year is the 52- or 53-week period that ends on the last Saturday of September.\n"
        "Products include iPhone, Mac, iPad, and Wearables, Home and Accessories. "
        "Services include Advertising, AppleCare, Cloud Services, Digital Content and Payment Services.\n\n"
        "Item 1A. Risk Factors\n"
        "The Company's business, results of operations and financial condition can be adversely affected by "
        "global and regional economic conditions, highly competitive global markets, supply chain disruptions, "
        "and volatile currency exchange rates. The Company relies on manufacturing partners in China for a substantial "
        "majority of final assembly.\n\n"
        "Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations\n"
        "Total net sales decreased 3% or $11.0 billion to $383.3 billion in fiscal 2023 compared to $394.3 billion in fiscal 2022, "
        "primarily due to lower net sales of Mac and iPad, partially offset by an increase in Services net sales. "
        "Services net sales reached $85.2 billion in 2023 compared to $78.1 billion in 2022. "
        "Gross margin was 44.1% in 2023 compared to 43.3% in 2022.\n\n"
        "Item 8. Financial Statements and Supplementary Data\n"
        "Consolidated Statements of Operations (in millions, except per share amounts):\n"
        "Total net sales: $383,285 in FY2023, $394,328 in FY2022.\n"
        "Cost of sales: $214,137 in FY2023, $223,546 in FY2022.\n"
        "Gross margin: $169,148 in FY2023, $170,782 in FY2022.\n"
        "Research and development: $29,915 in FY2023, $26,251 in FY2022.\n"
        "Selling, general and administrative: $24,932 in FY2023, $25,094 in FY2022.\n"
        "Total operating expenses: $54,847 in FY2023, $51,345 in FY2022.\n"
        "Operating income: $114,301 in FY2023, $119,437 in FY2022.\n"
        "Net income: $96,995 in FY2023, $99,803 in FY2022.\n"
        "Diluted earnings per share: $6.13 in FY2023, $6.11 in FY2022.\n"
    )

    aapl_2023_doc = ParsedDocumentData(
        document_id="0000320193-23-000106",
        source_reference_id="src-filing-aapl-10k-2023",
        canonical_entity_id="AAPL",
        title="Apple Inc. Form 10-K Annual Report (Fiscal Year ended September 30, 2023)",
        reporting_period="FY2023",
        source_revision="1",
        format=DocumentFormat.HTML,
        full_text=aapl_2023_text,
    )

    aapl_2023_doc.sections = [
        ResearchDocumentSection(
            section_id="sec-aapl-2023-item1",
            canonical_document_id="0000320193-23-000106",
            source_reference_id="src-filing-aapl-10k-2023",
            source_revision="1",
            heading="Item 1. Business",
            section_path="Part I > Item 1. Business",
            level=1,
            page_number=1,
            start_char_offset=aapl_2023_text.find("Item 1. Business"),
            end_char_offset=aapl_2023_text.find("Item 1A. Risk Factors"),
            text_preview="Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets...",
        ),
        ResearchDocumentSection(
            section_id="sec-aapl-2023-item1a",
            canonical_document_id="0000320193-23-000106",
            source_reference_id="src-filing-aapl-10k-2023",
            source_revision="1",
            heading="Item 1A. Risk Factors",
            section_path="Part I > Item 1A. Risk Factors",
            level=1,
            page_number=6,
            start_char_offset=aapl_2023_text.find("Item 1A. Risk Factors"),
            end_char_offset=aapl_2023_text.find("Item 7. Management's Discussion"),
            text_preview="The Company's business, results of operations and financial condition can be adversely affected by...",
        ),
        ResearchDocumentSection(
            section_id="sec-aapl-2023-item7",
            canonical_document_id="0000320193-23-000106",
            source_reference_id="src-filing-aapl-10k-2023",
            source_revision="1",
            heading="Item 7. Management's Discussion and Analysis",
            section_path="Part II > Item 7. MD&A",
            level=1,
            page_number=20,
            start_char_offset=aapl_2023_text.find("Item 7. Management's Discussion"),
            end_char_offset=aapl_2023_text.find("Item 8. Financial Statements"),
            text_preview="Total net sales decreased 3% or $11.0 billion to $383.3 billion in fiscal 2023...",
        ),
        ResearchDocumentSection(
            section_id="sec-aapl-2023-item8",
            canonical_document_id="0000320193-23-000106",
            source_reference_id="src-filing-aapl-10k-2023",
            source_revision="1",
            heading="Item 8. Financial Statements and Supplementary Data",
            section_path="Part II > Item 8. Financial Statements",
            level=1,
            page_number=42,
            start_char_offset=aapl_2023_text.find("Item 8. Financial Statements"),
            end_char_offset=len(aapl_2023_text),
            text_preview="Consolidated Statements of Operations (in millions, except per share amounts)...",
        ),
    ]

    aapl_2023_doc.spans = [
        ResearchDocumentSpan(
            span_id="span-aapl-2023-001",
            canonical_document_id="0000320193-23-000106",
            source_reference_id="src-filing-aapl-10k-2023",
            source_revision="1",
            section_id="sec-aapl-2023-item7",
            page_number=20,
            paragraph_number=1,
            start_char_offset=aapl_2023_text.find("Total net sales decreased 3%"),
            end_char_offset=aapl_2023_text.find("increase in Services net sales.") + len("increase in Services net sales."),
            text="Total net sales decreased 3% or $11.0 billion to $383.3 billion in fiscal 2023 compared to $394.3 billion in fiscal 2022, primarily due to lower net sales of Mac and iPad, partially offset by an increase in Services net sales.",
        )
    ]

    aapl_2023_doc.tables = [
        ResearchDocumentTable(
            table_id="tbl-aapl-2023-operations",
            canonical_document_id="0000320193-23-000106",
            source_reference_id="src-filing-aapl-10k-2023",
            source_revision="1",
            title="Consolidated Statements of Operations",
            period_label="FY2023 vs FY2022",
            currency="USD",
            unit_scale=UnitScale.MILLIONS,
            headers=["Consolidated Statements of Operations", "FY 2023", "FY 2022"],
            row_labels=[
                "Total net sales",
                "Cost of sales",
                "Gross margin",
                "Research and development",
                "Selling, general and administrative",
                "Total operating expenses",
                "Operating income",
                "Net income",
                "Diluted earnings per share (in USD)",
            ],
            cells=[
                ["Total net sales", "$383,285", "$394,328"],
                ["Cost of sales", "$214,137", "$223,546"],
                ["Gross margin", "$169,148", "$170,782"],
                ["Research and development", "$29,915", "$26,251"],
                ["Selling, general and administrative", "$24,932", "$25,094"],
                ["Total operating expenses", "$54,847", "$51,345"],
                ["Operating income", "$114,301", "$119,437"],
                ["Net income", "$96,995", "$99,803"],
                ["Diluted earnings per share (in USD)", "$6.13", "$6.11"],
            ],
            raw_values=[
                [383285.0, 394328.0],
                [214137.0, 223546.0],
                [169148.0, 170782.0],
                [29915.0, 26251.0],
                [24932.0, 25094.0],
                [54847.0, 51345.0],
                [114301.0, 119437.0],
                [96995.0, 99803.0],
                [6.13, 6.11],
            ],
            section_id="sec-aapl-2023-item8",
            footnotes=["As reported under US GAAP."],
        )
    ]

    aapl_2023_doc.processing_record = ResearchDocumentProcessingRecord(
        processing_id="proc-aapl-2023-10k",
        canonical_document_id="0000320193-23-000106",
        source_reference_id="src-filing-aapl-10k-2023",
        source_revision="1",
        source_format=DocumentFormat.HTML,
        processor_version="v105.0-institutional",
        processing_status=DocumentProcessingStatus.COMPLETED,
        started_at=datetime.datetime(2023, 11, 3, 16, 10, tzinfo=datetime.timezone.utc),
        completed_at=datetime.datetime(2023, 11, 3, 16, 12, tzinfo=datetime.timezone.utc),
        extracted_section_count=len(aapl_2023_doc.sections),
        extracted_table_count=len(aapl_2023_doc.tables),
        extracted_span_count=len(aapl_2023_doc.spans),
        content_rights_status="PUBLIC_DOMAIN_REGULATORY",
    )

    registry["0000320193-23-000106"] = aapl_2023_doc
    registry["src-filing-aapl-10k-2023"] = aapl_2023_doc

    # =========================================================================
    # 3. Microsoft Corporation Form 10-K (FY2024 ended June 30, 2024)
    # =========================================================================
    msft_2024_text = (
        "UNITED STATES SECURITIES AND EXCHANGE COMMISSION\n"
        "Washington, D.C. 20549\n"
        "FORM 10-K\n"
        "ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934\n"
        "For the fiscal year ended June 30, 2024\n"
        "Microsoft Corporation\n\n"
        "Item 1. Business\n"
        "Microsoft enables digital transformation for the era of an intelligent cloud and an intelligent edge. "
        "Our mission is to empower every person and every organization on the planet to achieve more. "
        "We develop and support software, services, devices, and solutions. Our three reportable segments are: "
        "Productivity and Business Processes, Intelligent Cloud, and More Personal Computing.\n\n"
        "Item 1A. Risk Factors\n"
        "We face intense competition across all markets for our products and services. "
        "We make significant investments in artificial intelligence, cloud platforms, and data center infrastructure "
        "that may not achieve anticipated returns. Cybersecurity attacks and system vulnerabilities could disrupt operations.\n\n"
        "Item 7. Management's Discussion and Analysis\n"
        "Revenue increased 16% to $245.1 billion for fiscal year 2024, driven by growth in Microsoft Cloud. "
        "Microsoft Cloud revenue reached $137.4 billion, up 23% year-over-year. Operating income was $109.4 billion, up 24%.\n\n"
        "Item 8. Financial Statements\n"
        "Income Statements (in millions):\n"
        "Revenue: $245,123 in FY2024, $211,915 in FY2023.\n"
        "Operating income: $109,433 in FY2024, $88,523 in FY2023.\n"
        "Net income: $88,136 in FY2024, $72,361 in FY2023.\n"
    )

    msft_2024_doc = ParsedDocumentData(
        document_id="0000789019-24-000055",
        source_reference_id="src-filing-msft-10k-2024",
        canonical_entity_id="MSFT",
        title="Microsoft Corporation Form 10-K Annual Report (Fiscal Year ended June 30, 2024)",
        reporting_period="FY2024",
        source_revision="1",
        format=DocumentFormat.HTML,
        full_text=msft_2024_text,
    )

    msft_2024_doc.sections = [
        ResearchDocumentSection(
            section_id="sec-msft-2024-item1",
            canonical_document_id="0000789019-24-000055",
            source_reference_id="src-filing-msft-10k-2024",
            source_revision="1",
            heading="Item 1. Business",
            section_path="Part I > Item 1. Business",
            level=1,
            page_number=1,
            start_char_offset=msft_2024_text.find("Item 1. Business"),
            end_char_offset=msft_2024_text.find("Item 1A. Risk Factors"),
            text_preview="Microsoft enables digital transformation for the era of an intelligent cloud...",
        ),
        ResearchDocumentSection(
            section_id="sec-msft-2024-item1a",
            canonical_document_id="0000789019-24-000055",
            source_reference_id="src-filing-msft-10k-2024",
            source_revision="1",
            heading="Item 1A. Risk Factors",
            section_path="Part I > Item 1A. Risk Factors",
            level=1,
            page_number=7,
            start_char_offset=msft_2024_text.find("Item 1A. Risk Factors"),
            end_char_offset=msft_2024_text.find("Item 7. Management's Discussion"),
            text_preview="We face intense competition across all markets for our products and services...",
        ),
        ResearchDocumentSection(
            section_id="sec-msft-2024-item7",
            canonical_document_id="0000789019-24-000055",
            source_reference_id="src-filing-msft-10k-2024",
            source_revision="1",
            heading="Item 7. Management's Discussion and Analysis",
            section_path="Part II > Item 7. MD&A",
            level=1,
            page_number=28,
            start_char_offset=msft_2024_text.find("Item 7. Management's Discussion"),
            end_char_offset=msft_2024_text.find("Item 8. Financial Statements"),
            text_preview="Revenue increased 16% to $245.1 billion for fiscal year 2024...",
        ),
    ]

    msft_2024_doc.spans = [
        ResearchDocumentSpan(
            span_id="span-msft-2024-001",
            canonical_document_id="0000789019-24-000055",
            source_reference_id="src-filing-msft-10k-2024",
            source_revision="1",
            section_id="sec-msft-2024-item7",
            page_number=28,
            paragraph_number=1,
            start_char_offset=msft_2024_text.find("Revenue increased 16% to $245.1 billion"),
            end_char_offset=msft_2024_text.find("up 24%.") + len("up 24%."),
            text="Revenue increased 16% to $245.1 billion for fiscal year 2024, driven by growth in Microsoft Cloud. Operating income was $109.4 billion, up 24%.",
        )
    ]

    msft_2024_doc.tables = [
        ResearchDocumentTable(
            table_id="tbl-msft-2024-income",
            canonical_document_id="0000789019-24-000055",
            source_reference_id="src-filing-msft-10k-2024",
            source_revision="1",
            title="Income Statements Summary",
            period_label="FY2024 vs FY2023",
            currency="USD",
            unit_scale=UnitScale.MILLIONS,
            headers=["Income Statements", "FY 2024", "FY 2023"],
            row_labels=["Revenue", "Operating income", "Net income"],
            cells=[
                ["Revenue", "$245,123", "$211,915"],
                ["Operating income", "$109,433", "$88,523"],
                ["Net income", "$88,136", "$72,361"],
            ],
            raw_values=[
                [245123.0, 211915.0],
                [109433.0, 88523.0],
                [88136.0, 72361.0],
            ],
            section_id="sec-msft-2024-item7",
            footnotes=["In millions of USD."],
        )
    ]

    msft_2024_doc.processing_record = ResearchDocumentProcessingRecord(
        processing_id="proc-msft-2024-10k",
        canonical_document_id="0000789019-24-000055",
        source_reference_id="src-filing-msft-10k-2024",
        source_revision="1",
        source_format=DocumentFormat.HTML,
        processor_version="v105.0-institutional",
        processing_status=DocumentProcessingStatus.COMPLETED,
        started_at=datetime.datetime(2024, 7, 30, 16, 30, tzinfo=datetime.timezone.utc),
        completed_at=datetime.datetime(2024, 7, 30, 16, 32, tzinfo=datetime.timezone.utc),
        extracted_section_count=len(msft_2024_doc.sections),
        extracted_table_count=len(msft_2024_doc.tables),
        extracted_span_count=len(msft_2024_doc.spans),
        content_rights_status="PUBLIC_DOMAIN_REGULATORY",
    )

    registry["0000789019-24-000055"] = msft_2024_doc
    registry["src-filing-msft-10k-2024"] = msft_2024_doc

    # =========================================================================
    # 4. Bureau of Labor Statistics CPI News Release (Sept 2024)
    # =========================================================================
    cpi_text = (
        "BUREAU OF LABOR STATISTICS - DEPARTMENT OF LABOR\n"
        "CONSUMER PRICE INDEX - SEPTEMBER 2024\n"
        "Transmission of material in this release is embargoed until 8:30 A.M. (ET) Thursday, October 10, 2024\n\n"
        "Summary Findings\n"
        "The Consumer Price Index for All Urban Consumers (CPI-U) increased 0.2 percent in September on a "
        "seasonally adjusted basis, the same increase as in August, the U.S. Bureau of Labor Statistics reported today. "
        "Over the last 12 months, the all items index increased 2.4 percent before seasonal adjustment.\n\n"
        "Core Inflation\n"
        "The index for all items less food and energy rose 0.3 percent in September, after rising 0.3 percent in August. "
        "Over the last 12 months, the core index increased 3.3 percent. The shelter index increased 0.2 percent in September.\n\n"
        "Table A. Percent changes in CPI for All Urban Consumers (CPI-U)\n"
        "All Items: Sep 2024 YoY +2.4%, Aug 2024 YoY +2.5%\n"
        "Food: Sep 2024 YoY +2.3%, Aug 2024 YoY +2.1%\n"
        "Energy: Sep 2024 YoY -6.8%, Aug 2024 YoY -4.0%\n"
        "All items less food and energy: Sep 2024 YoY +3.3%, Aug 2024 YoY +3.2%\n"
    )

    cpi_doc = ParsedDocumentData(
        document_id="cpi-u-202409-release",
        source_reference_id="src-econ-bls-cpi-202409",
        canonical_entity_id="US_CPI",
        title="U.S. Consumer Price Index (CPI-U) September 2024 News Release",
        reporting_period="September 2024",
        source_revision="first-release-vintage-20241010",
        format=DocumentFormat.PLAIN_TEXT,
        full_text=cpi_text,
    )

    cpi_doc.sections = [
        ResearchDocumentSection(
            section_id="sec-cpi-202409-summary",
            canonical_document_id="cpi-u-202409-release",
            source_reference_id="src-econ-bls-cpi-202409",
            source_revision="first-release-vintage-20241010",
            heading="Summary Findings",
            section_path="CPI Release > Summary Findings",
            level=1,
            page_number=1,
            start_char_offset=cpi_text.find("Summary Findings"),
            end_char_offset=cpi_text.find("Core Inflation"),
            text_preview="The Consumer Price Index for All Urban Consumers (CPI-U) increased 0.2 percent in September...",
        ),
        ResearchDocumentSection(
            section_id="sec-cpi-202409-core",
            canonical_document_id="cpi-u-202409-release",
            source_reference_id="src-econ-bls-cpi-202409",
            source_revision="first-release-vintage-20241010",
            heading="Core Inflation",
            section_path="CPI Release > Core Inflation",
            level=1,
            page_number=1,
            start_char_offset=cpi_text.find("Core Inflation"),
            end_char_offset=cpi_text.find("Table A."),
            text_preview="The index for all items less food and energy rose 0.3 percent in September...",
        ),
    ]

    cpi_doc.spans = [
        ResearchDocumentSpan(
            span_id="span-cpi-202409-001",
            canonical_document_id="cpi-u-202409-release",
            source_reference_id="src-econ-bls-cpi-202409",
            source_revision="first-release-vintage-20241010",
            section_id="sec-cpi-202409-summary",
            page_number=1,
            paragraph_number=1,
            start_char_offset=cpi_text.find("Over the last 12 months, the all items index increased 2.4 percent"),
            end_char_offset=cpi_text.find("before seasonal adjustment.") + len("before seasonal adjustment."),
            text="Over the last 12 months, the all items index increased 2.4 percent before seasonal adjustment.",
        )
    ]

    cpi_doc.tables = [
        ResearchDocumentTable(
            table_id="tbl-cpi-202409-changes",
            canonical_document_id="cpi-u-202409-release",
            source_reference_id="src-econ-bls-cpi-202409",
            source_revision="first-release-vintage-20241010",
            title="Table A. Percent changes in CPI-U (12-Month Percent Change)",
            period_label="Sep 2024 vs Aug 2024",
            currency="PERCENT",
            unit_scale=UnitScale.PERCENTAGE,
            headers=["Expenditure Category", "Sep 2024 YoY", "Aug 2024 YoY"],
            row_labels=["All Items", "Food", "Energy", "All items less food and energy"],
            cells=[
                ["All Items", "2.4%", "2.5%"],
                ["Food", "2.3%", "2.1%"],
                ["Energy", "-6.8%", "-4.0%"],
                ["All items less food and energy", "3.3%", "3.2%"],
            ],
            raw_values=[
                [2.4, 2.5],
                [2.3, 2.1],
                [-6.8, -4.0],
                [3.3, 3.2],
            ],
            section_id="sec-cpi-202409-core",
            footnotes=["12-month unadjusted change reported by Bureau of Labor Statistics."],
            associated_fact_ids=["cpi-u-202409-release"],
        )
    ]

    cpi_doc.processing_record = ResearchDocumentProcessingRecord(
        processing_id="proc-cpi-202409",
        canonical_document_id="cpi-u-202409-release",
        source_reference_id="src-econ-bls-cpi-202409",
        source_revision="first-release-vintage-20241010",
        source_format=DocumentFormat.PLAIN_TEXT,
        processor_version="v105.0-institutional",
        processing_status=DocumentProcessingStatus.COMPLETED,
        started_at=datetime.datetime(2024, 10, 10, 12, 30, tzinfo=datetime.timezone.utc),
        completed_at=datetime.datetime(2024, 10, 10, 12, 31, tzinfo=datetime.timezone.utc),
        extracted_section_count=len(cpi_doc.sections),
        extracted_table_count=len(cpi_doc.tables),
        extracted_span_count=len(cpi_doc.spans),
        content_rights_status="PUBLIC_DOMAIN_GOV",
    )

    registry["cpi-u-202409-release"] = cpi_doc
    registry["src-econ-bls-cpi-202409"] = cpi_doc

    # =========================================================================
    # 5. Bloomberg News Article: Fed Rate Cut (2024-09-18)
    # =========================================================================
    fed_news_text = (
        "Federal Reserve Lowers Benchmark Policy Rate by 50 Basis Points to 4.75%-5.00%\n"
        "By Craig Torres and Catarina Saraiva | Bloomberg News\n"
        "Published: September 18, 2024 at 2:00 PM EDT\n\n"
        "Key Decisions\n"
        "The Federal Reserve cut its benchmark interest rate by half a percentage point on Wednesday, "
        "kicking off an aggressive shift to preserve the strength of the US labor market as inflation cools. "
        "The Federal Open Market Committee voted 11 to 1 to lower the federal funds rate to a range of 4.75% to 5.0%, "
        "in its first policy reduction in more than four years.\n\n"
        "Economic Projections\n"
        "Policymakers projected another 50 basis points of easing across their remaining two meetings this year, "
        "according to the median projection in the Summary of Economic Projections (SEP). Fed Governor Michelle Bowman "
        "dissented in favor of a quarter-point cut.\n"
    )

    fed_news_doc = ParsedDocumentData(
        document_id="art-bloomberg-20240918-001",
        source_reference_id="src-news-bloomberg-fed-rate-20240918",
        canonical_entity_id="FED",
        title="Federal Reserve Lowers Benchmark Policy Rate by 50 Basis Points to 4.75%-5.00%",
        reporting_period="2024-09-18",
        source_revision="rev-1",
        format=DocumentFormat.PLAIN_TEXT,
        full_text=fed_news_text,
    )

    fed_news_doc.sections = [
        ResearchDocumentSection(
            section_id="sec-fed-news-001",
            canonical_document_id="art-bloomberg-20240918-001",
            source_reference_id="src-news-bloomberg-fed-rate-20240918",
            source_revision="rev-1",
            heading="Key Decisions",
            section_path="Article > Key Decisions",
            level=1,
            page_number=1,
            start_char_offset=fed_news_text.find("Key Decisions"),
            end_char_offset=fed_news_text.find("Economic Projections"),
            text_preview="The Federal Reserve cut its benchmark interest rate by half a percentage point on Wednesday...",
        ),
        ResearchDocumentSection(
            section_id="sec-fed-news-002",
            canonical_document_id="art-bloomberg-20240918-001",
            source_reference_id="src-news-bloomberg-fed-rate-20240918",
            source_revision="rev-1",
            heading="Economic Projections",
            section_path="Article > Economic Projections",
            level=1,
            page_number=1,
            start_char_offset=fed_news_text.find("Economic Projections"),
            end_char_offset=len(fed_news_text),
            text_preview="Policymakers projected another 50 basis points of easing across their remaining meetings...",
        ),
    ]

    fed_news_doc.spans = [
        ResearchDocumentSpan(
            span_id="span-fed-news-001",
            canonical_document_id="art-bloomberg-20240918-001",
            source_reference_id="src-news-bloomberg-fed-rate-20240918",
            source_revision="rev-1",
            section_id="sec-fed-news-001",
            page_number=1,
            paragraph_number=1,
            start_char_offset=fed_news_text.find("The Federal Open Market Committee voted 11 to 1"),
            end_char_offset=fed_news_text.find("four years.") + len("four years."),
            text="The Federal Open Market Committee voted 11 to 1 to lower the federal funds rate to a range of 4.75% to 5.0%, in its first policy reduction in more than four years.",
        )
    ]

    fed_news_doc.processing_record = ResearchDocumentProcessingRecord(
        processing_id="proc-news-fed-rate",
        canonical_document_id="art-bloomberg-20240918-001",
        source_reference_id="src-news-bloomberg-fed-rate-20240918",
        source_revision="rev-1",
        source_format=DocumentFormat.PLAIN_TEXT,
        processor_version="v105.0-institutional",
        processing_status=DocumentProcessingStatus.COMPLETED,
        started_at=datetime.datetime(2024, 9, 18, 18, 1, tzinfo=datetime.timezone.utc),
        completed_at=datetime.datetime(2024, 9, 18, 18, 2, tzinfo=datetime.timezone.utc),
        extracted_section_count=len(fed_news_doc.sections),
        extracted_table_count=0,
        extracted_span_count=len(fed_news_doc.spans),
        content_rights_status="LICENSED_EXCERPT_ONLY",
    )

    registry["art-bloomberg-20240918-001"] = fed_news_doc
    registry["src-news-bloomberg-fed-rate-20240918"] = fed_news_doc

    return registry


# ---------------------------------------------------------------------------
# In-Document Search Engine
# ---------------------------------------------------------------------------

def search_within_document(
    doc: ParsedDocumentData,
    query: str,
    section_id: Optional[str] = None,
    limit: int = 20,
) -> List[DocumentSearchHit]:
    """Execute keyword or exact-phrase search within a document's extracted sections and text spans.

    Returns:
        Ranked list of DocumentSearchHit instances with highlighted snippets.
    """
    clean_q = query.strip()
    if not clean_q:
        return []

    hits: List[DocumentSearchHit] = []
    q_lower = clean_q.lower()

    # Search spans
    for sp in doc.spans:
        if section_id and sp.section_id != section_id:
            continue
        text_lower = sp.text.lower()
        idx = text_lower.find(q_lower)
        if idx != -1:
            # Construct highlighted snippet
            snippet_start = max(0, idx - 40)
            snippet_end = min(len(sp.text), idx + len(clean_q) + 60)
            prefix = "..." if snippet_start > 0 else ""
            suffix = "..." if snippet_end < len(sp.text) else ""

            matched_token = sp.text[idx : idx + len(clean_q)]
            snippet = f"{prefix}{sp.text[snippet_start:idx]}<mark>{matched_token}</mark>{sp.text[idx + len(clean_q):snippet_end]}{suffix}"

            # Look up section heading
            sec_heading = None
            if sp.section_id:
                for sec in doc.sections:
                    if sec.section_id == sp.section_id:
                        sec_heading = sec.heading
                        break

            hits.append(
                DocumentSearchHit(
                    span_id=sp.span_id,
                    snippet=snippet,
                    match_start=idx,
                    match_end=idx + len(clean_q),
                    section_id=sp.section_id,
                    section_heading=sec_heading,
                    page_number=sp.page_number,
                    paragraph_number=sp.paragraph_number,
                )
            )
            if len(hits) >= limit:
                break

    # If hits < limit, search broader sections text
    if len(hits) < limit:
        for sec in doc.sections:
            if section_id and sec.section_id != section_id:
                continue
            sec_text = doc.full_text[sec.start_char_offset : sec.end_char_offset]
            text_lower = sec_text.lower()
            pos = 0
            while len(hits) < limit:
                found_idx = text_lower.find(q_lower, pos)
                if found_idx == -1:
                    break

                # Avoid duplicate if already covered by span
                abs_offset = sec.start_char_offset + found_idx
                already_covered = any(
                    abs(h.match_start - abs_offset) < 20 for h in hits
                )
                if not already_covered:
                    snip_s = max(0, found_idx - 40)
                    snip_e = min(len(sec_text), found_idx + len(clean_q) + 60)
                    prefix = "..." if snip_s > 0 else ""
                    suffix = "..." if snip_e < len(sec_text) else ""
                    token = sec_text[found_idx : found_idx + len(clean_q)]
                    snippet = f"{prefix}{sec_text[snip_s:found_idx]}<mark>{token}</mark>{sec_text[found_idx + len(clean_q):snip_e]}{suffix}"

                    hits.append(
                        DocumentSearchHit(
                            span_id=f"span-gen-{sec.section_id}-{found_idx}",
                            snippet=snippet,
                            match_start=abs_offset,
                            match_end=abs_offset + len(clean_q),
                            section_id=sec.section_id,
                            section_heading=sec.heading,
                            page_number=sec.page_number,
                        )
                    )

                pos = found_idx + len(clean_q) + 1

    return hits


# ---------------------------------------------------------------------------
# Two-Document Text Diff & Section Alignment
# ---------------------------------------------------------------------------

def compute_document_diff(
    left_doc: ParsedDocumentData,
    right_doc: ParsedDocumentData,
    mode: DocumentComparisonMode = DocumentComparisonMode.FULL_TEXT,
) -> DocumentComparisonResult:
    """Compare two documents line-by-line with structural section alignment.

    Args:
        left_doc: Earlier/prior period document (baseline).
        right_doc: Later/current period document (comparison target).
        mode: Comparison scope (FULL_TEXT, SECTIONS, FINANCIAL_TABLES).

    Returns:
        DocumentComparisonResult with aligned section diffs, financial facts, and statistics.
    """
    section_diffs: List[DocumentComparisonSectionDiff] = []
    total_added = 0
    total_removed = 0
    warnings: List[str] = []

    # Check basic compatibility
    if left_doc.canonical_entity_id and right_doc.canonical_entity_id:
        if left_doc.canonical_entity_id != right_doc.canonical_entity_id:
            warnings.append(
                f"Cross-entity comparison: comparing {left_doc.canonical_entity_id} with {right_doc.canonical_entity_id}. "
                "Ensure operational models and reporting currencies are compatible."
            )

    # 1. Align Sections
    left_sections_by_name = {s.heading.lower().strip(): s for s in left_doc.sections}
    right_sections_by_name = {s.heading.lower().strip(): s for s in right_doc.sections}

    all_keys = list(dict.fromkeys(list(left_sections_by_name.keys()) + list(right_sections_by_name.keys())))

    for k in all_keys:
        l_sec = left_sections_by_name.get(k)
        r_sec = right_sections_by_name.get(k)

        if l_sec and r_sec:
            # Aligned match
            l_text = left_doc.full_text[l_sec.start_char_offset : l_sec.end_char_offset]
            r_text = right_doc.full_text[r_sec.start_char_offset : r_sec.end_char_offset]

            l_lines = l_text.splitlines(keepends=True)
            r_lines = r_text.splitlines(keepends=True)

            diff_lines = list(
                difflib.unified_diff(
                    l_lines,
                    r_lines,
                    fromfile=f"{left_doc.reporting_period or 'Left'} - {l_sec.heading}",
                    tofile=f"{right_doc.reporting_period or 'Right'} - {r_sec.heading}",
                    n=2,
                )
            )

            added = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
            removed = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
            total_added += added
            total_removed += removed

            section_diffs.append(
                DocumentComparisonSectionDiff(
                    section_name=r_sec.heading,
                    alignment_status="MATCHED",
                    added_lines_count=added,
                    removed_lines_count=removed,
                    diff_unified="".join(diff_lines),
                    left_section_heading=l_sec.heading,
                    right_section_heading=r_sec.heading,
                    left_location_ref=f"Section {l_sec.heading} (p. {l_sec.page_number or '?'})",
                    right_location_ref=f"Section {r_sec.heading} (p. {r_sec.page_number or '?'})",
                )
            )

        elif l_sec and not r_sec:
            # Removed in right document
            l_text = left_doc.full_text[l_sec.start_char_offset : l_sec.end_char_offset]
            lines = l_text.splitlines()
            removed = len(lines)
            total_removed += removed

            section_diffs.append(
                DocumentComparisonSectionDiff(
                    section_name=l_sec.heading,
                    alignment_status="REMOVED_IN_RIGHT",
                    added_lines_count=0,
                    removed_lines_count=removed,
                    diff_unified=f"--- {l_sec.heading} (Removed in {right_doc.reporting_period or 'Right'})\n",
                    left_section_heading=l_sec.heading,
                    left_location_ref=f"Section {l_sec.heading} (p. {l_sec.page_number or '?'})",
                )
            )

        elif r_sec and not l_sec:
            # Added in right document
            r_text = right_doc.full_text[r_sec.start_char_offset : r_sec.end_char_offset]
            lines = r_text.splitlines()
            added = len(lines)
            total_added += added

            section_diffs.append(
                DocumentComparisonSectionDiff(
                    section_name=r_sec.heading,
                    alignment_status="ADDED_IN_RIGHT",
                    added_lines_count=added,
                    removed_lines_count=0,
                    diff_unified=f"+++ {r_sec.heading} (Newly added in {right_doc.reporting_period or 'Right'})\n",
                    right_section_heading=r_sec.heading,
                    right_location_ref=f"Section {r_sec.heading} (p. {r_sec.page_number or '?'})",
                )
            )

    # 2. Financial Fact Variance Comparison (if tables present)
    fact_diffs: List[FinancialFactComparison] = []
    if left_doc.tables and right_doc.tables:
        l_tbl = left_doc.tables[0]
        r_tbl = right_doc.tables[0]

        # Map by row label
        l_map = {lbl.lower().strip(): (lbl, vals) for lbl, vals in zip(l_tbl.row_labels, l_tbl.raw_values)}
        for r_lbl, r_vals in zip(r_tbl.row_labels, r_tbl.raw_values):
            k = r_lbl.lower().strip()
            if k in l_map and r_vals and l_map[k][1]:
                orig_lbl = r_lbl
                val_left = l_map[k][1][0]  # prior period value
                val_right = r_vals[0]      # current period value

                if val_left is not None and val_right is not None:
                    abs_delta = round(val_right - val_left, 4)
                    pct_delta: Optional[float] = None
                    compat_status = "COMPATIBLE"

                    if abs(val_left) > 1e-9:
                        pct_delta = round(((val_right - val_left) / abs(val_left)) * 100.0, 2)
                    else:
                        compat_status = "ZERO_BASE"
                        warnings.append(f"Percentage growth for '{orig_lbl}' is undefined due to zero baseline in {left_doc.reporting_period}.")

                    fact_diffs.append(
                        FinancialFactComparison(
                            fact_key=re.sub(r"[^a-zA-Z0-9]+", "_", orig_lbl.lower()),
                            label=orig_lbl,
                            left_period=left_doc.reporting_period or "Prior",
                            right_period=right_doc.reporting_period or "Current",
                            currency=r_tbl.currency,
                            unit_scale=r_tbl.unit_scale,
                            left_value=val_left,
                            right_value=val_right,
                            absolute_delta=abs_delta,
                            percentage_delta=pct_delta,
                            is_restated=False,
                            compatibility_status=compat_status,
                        )
                    )

    return DocumentComparisonResult(
        comparison_id=f"cmp-{uuid.uuid4().hex[:12]}",
        left_document_id=left_doc.document_id,
        right_document_id=right_doc.document_id,
        left_title=left_doc.title,
        right_title=right_doc.title,
        left_period=left_doc.reporting_period,
        right_period=right_doc.reporting_period,
        total_added_lines=total_added,
        total_removed_lines=total_removed,
        section_diffs=section_diffs,
        financial_fact_diffs=fact_diffs,
        compared_at=datetime.datetime.now(datetime.timezone.utc),
        comparison_mode=mode,
        compatibility_warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Location Anchor Resolver & Candidate Extractor
# ---------------------------------------------------------------------------

def resolve_source_location_anchor(
    doc: ParsedDocumentData,
    location_type: EvidenceLocationType,
    location_reference: str,
    page_number: Optional[int] = None,
    section_name: Optional[str] = None,
) -> Tuple[bool, str, Optional[str], Optional[str]]:
    """Validate whether an evidence location anchor maps to verified text in the document.

    Returns:
        (is_valid, resolved_anchor, context_snippet, error_message)
    """
    # 1. Section validation
    if location_type == EvidenceLocationType.SECTION or section_name:
        target_sec = section_name or location_reference
        matched_sec = None
        for sec in doc.sections:
            if target_sec.lower() in sec.heading.lower() or target_sec.lower() in sec.section_path.lower():
                matched_sec = sec
                break
        if not matched_sec:
            return (
                False,
                location_reference,
                None,
                f"Section '{target_sec}' could not be resolved in document {doc.document_id}.",
            )
        return (
            True,
            f"{matched_sec.heading} (p. {matched_sec.page_number or '?'})",
            matched_sec.text_preview,
            None,
        )

    # 2. Page validation
    if location_type == EvidenceLocationType.PAGE or page_number is not None:
        target_page = page_number
        if target_page is None:
            m = re.search(r"\d+", location_reference)
            if m:
                target_page = int(m.group(0))

        if target_page is not None:
            # Check if any span or section matches this page
            matching_spans = [s for s in doc.spans if s.page_number == target_page]
            if matching_spans:
                return (
                    True,
                    f"Page {target_page}",
                    matching_spans[0].text[:120] + "...",
                    None,
                )
            matching_sections = [s for s in doc.sections if s.page_number == target_page]
            if matching_sections:
                return (
                    True,
                    f"Page {target_page} ({matching_sections[0].heading})",
                    matching_sections[0].text_preview,
                    None,
                )
            return (
                False,
                location_reference,
                None,
                f"Page {target_page} exceeds document page bounds or has no verified selectable content.",
            )

    # 3. Text / span match
    clean_ref = location_reference.strip().lower()
    for sp in doc.spans:
        if clean_ref in sp.text.lower():
            return (
                True,
                f"Paragraph in {sp.section_id or 'Body'} (p. {sp.page_number or '?'})",
                sp.text[:120] + "...",
                None,
            )

    if clean_ref in doc.full_text.lower():
        idx = doc.full_text.lower().find(clean_ref)
        snip = doc.full_text[max(0, idx - 20) : min(len(doc.full_text), idx + len(clean_ref) + 40)]
        return (
            True,
            f"Offset {idx}-{idx + len(clean_ref)}",
            snip.strip(),
            None,
        )

    return (
        False,
        location_reference,
        None,
        f"Location anchor '{location_reference}' could not be verified in original source text.",
    )


def extract_evidence_candidates_from_document(
    doc: ParsedDocumentData,
    query: Optional[str] = None,
    limit: int = 15,
) -> List[ResearchEvidenceCandidate]:
    """Extract candidate evidence snippets from document spans and tables eligible for research linking."""
    candidates: List[ResearchEvidenceCandidate] = []

    # 1. From Spans
    for sp in doc.spans:
        if query and query.lower() not in sp.text.lower():
            continue

        sec_heading = None
        if sp.section_id:
            for sec in doc.sections:
                if sec.section_id == sp.section_id:
                    sec_heading = sec.heading
                    break

        candidates.append(
            ResearchEvidenceCandidate(
                candidate_id=f"cand-{uuid.uuid4().hex[:10]}",
                source_reference_id=doc.source_reference_id,
                source_title=doc.title,
                extracted_text=sp.text,
                evidence_type="QUOTATION",
                location_reference=f"Section {sec_heading or 'General'} (p. {sp.page_number or '?'})",
                canonical_document_id=doc.document_id,
                canonical_entity_id=doc.canonical_entity_id,
                section_heading=sec_heading,
                page_number=sp.page_number,
                paragraph_number=sp.paragraph_number,
                reporting_period=doc.reporting_period,
                source_revision=doc.source_revision,
                provenance={
                    "span_id": sp.span_id,
                    "offsets": [sp.start_char_offset, sp.end_char_offset],
                },
            )
        )
        if len(candidates) >= limit:
            break

    # 2. From Tables
    for tbl in doc.tables:
        if len(candidates) >= limit:
            break
        for row_lbl, raw_row in zip(tbl.row_labels, tbl.raw_values):
            if not raw_row or raw_row[0] is None:
                continue
            val = raw_row[0]
            candidates.append(
                ResearchEvidenceCandidate(
                    candidate_id=f"cand-{uuid.uuid4().hex[:10]}",
                    source_reference_id=doc.source_reference_id,
                    source_title=doc.title,
                    extracted_text=f"{tbl.title}: {row_lbl} was {tbl.currency} {val:,.2f} ({tbl.unit_scale.value}) in {tbl.period_label}.",
                    evidence_type="FINANCIAL_FACT",
                    location_reference=f"Table: {tbl.title} > {row_lbl}",
                    canonical_document_id=doc.document_id,
                    canonical_entity_id=doc.canonical_entity_id,
                    reporting_period=doc.reporting_period,
                    unit=tbl.unit_scale.value,
                    currency=tbl.currency,
                    numeric_value=val,
                    source_revision=doc.source_revision,
                    provenance={
                        "table_id": tbl.table_id,
                        "row_label": row_lbl,
                    },
                )
            )
            if len(candidates) >= limit:
                break

    return candidates
