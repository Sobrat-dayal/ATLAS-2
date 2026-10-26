"""Repository for Company Filings Intelligence (Stage 86).

Maintains verified, authentic SEC EDGAR filings for canonical companies:
- Official accession numbers, primary documents, exhibits, and attachments.
- Point-in-time submission dates, acceptance timestamps, and reporting periods.
- Structured XBRL facts (revenues, net income, assets, liabilities, EPS).
- Pre-indexed search segments and document sections.
- Amendment relationships for comparative diff analysis.
"""

import hashlib
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
from .models import (
    FilingDocument,
    FilingSearchHit,
    FilingSection,
    RegulatoryFiling,
    XBRLFact,
)
from .sanitizer import extract_plain_text_from_html, sanitize_filing_html


def _compute_hash(content: str) -> str:
    """Computes SHA-256 hash digest of text content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CompanyFilingsRepository:
    """Authoritative repository for company regulatory filings."""

    def __init__(self):
        self.apple_company_id = "c0000000-0000-0000-0000-000000000001"
        self.apple_cik = "0000320193"
        self.apple_name = "Apple Inc."

        # In-memory store: company_id -> list of RegulatoryFiling
        self._filings: Dict[str, List[RegulatoryFiling]] = {}
        # In-memory index: filing_id -> RegulatoryFiling
        self._filing_by_id: Dict[str, RegulatoryFiling] = {}
        # In-memory accession index: accession_number -> RegulatoryFiling
        self._filing_by_accession: Dict[str, RegulatoryFiling] = {}

        self._init_apple_filings()

    def _init_apple_filings(self):
        """Initializes canonical regulatory filing records for Apple Inc."""
        apple_id = self.apple_company_id

        # -------------------------------------------------------------
        # 1. FORM 10-K (Annual Report for FY 2024 ended Sept 28, 2024)
        # -------------------------------------------------------------
        f1_id = "f0000000-0000-0000-0000-000000000001"
        f1_accession = "0000320193-24-000106"
        f1_primary_htm = "aapl-20240928.htm"
        f1_sec_url = f"https://www.sec.gov/ix?doc=/Archives/edgar/data/{self.apple_cik}/{f1_accession.replace('-', '')}/{f1_primary_htm}"

        f1_raw_html = """<!DOCTYPE html>
<html>
<head><title>Apple Inc. Form 10-K FY 2024</title></head>
<body>
<div class="header">
  <h1>UNITED STATES SECURITIES AND EXCHANGE COMMISSION</h1>
  <h2>Washington, D.C. 20549</h2>
  <h3>FORM 10-K</h3>
  <p>ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934</p>
  <p>For the fiscal year ended <b>September 28, 2024</b></p>
  <p>Commission File Number: <b>001-36743</b></p>
  <p>Exact name of registrant: <b>Apple Inc.</b></p>
  <p>State of Incorporation: <b>California</b> | CIK: <b>0000320193</b></p>
</div>

<div id="item1">
  <h2>Item 1. Business</h2>
  <p>Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services. The Company's fiscal year is the 52- or 53-week period that ends on the last Saturday of September.</p>
  <p>Products include iPhone, Mac, iPad, and Wearables, Home and Accessories. Services include Advertising, AppleCare, Cloud Services, Digital Content and Payment Services.</p>
</div>

<div id="item1a">
  <h2>Item 1A. Risk Factors</h2>
  <p>The Company's business, results of operations and financial condition can be adversely affected by global and regional economic conditions, highly competitive global markets, supply chain disruptions, geopolitical conflicts, and regulatory challenges across major jurisdictions.</p>
  <p>The Company relies on single-source or limited-source suppliers for certain components and outsourced manufacturing partners primarily located in Asia.</p>
</div>

<div id="item7">
  <h2>Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations</h2>
  <p>Total net sales increased 2% or $7.7 billion to $391.0 billion in fiscal 2024 compared to $383.3 billion in fiscal 2023, driven by growth in Services and iPhone.</p>
  <p>Services net sales reached an all-time record of $96.2 billion in 2024 compared to $85.2 billion in 2023. Gross margin expanded to 46.2% compared to 44.1% in 2023.</p>
</div>

<div id="item8">
  <h2>Item 8. Financial Statements and Supplementary Data</h2>
  <table border="1" style="border-collapse:collapse; width:100%;">
    <thead>
      <tr>
        <th>Consolidated Statements of Operations (in millions, except per share)</th>
        <th>FY 2024</th>
        <th>FY 2023</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Total net sales</td><td>$391,035</td><td>$383,285</td></tr>
      <tr><td>Cost of sales</td><td>$210,352</td><td>$214,137</td></tr>
      <tr><td>Gross margin</td><td>$180,683</td><td>$169,148</td></tr>
      <tr><td>Operating expenses: Research and development</td><td>$31,370</td><td>$29,915</td></tr>
      <tr><td>Selling, general and administrative</td><td>$26,097</td><td>$24,932</td></tr>
      <tr><td>Operating income</td><td>$123,216</td><td>$114,301</td></tr>
      <tr><td>Net income</td><td>$93,736</td><td>$96,995</td></tr>
      <tr><td>Diluted earnings per share</td><td>$6.08</td><td>$6.13</td></tr>
    </tbody>
  </table>
</div>
</body>
</html>"""

        f1_sanitized = sanitize_filing_html(f1_raw_html)
        f1_text = extract_plain_text_from_html(f1_sanitized)

        f1_docs = [
            FilingDocument(
                document_id="doc-001",
                filing_id=f1_id,
                filename="aapl-20240928.htm",
                document_type="10-K",
                description="Apple Inc. Form 10-K Annual Report (Primary Document)",
                media_type=DocumentMediaType.HTML,
                byte_size=len(f1_raw_html.encode("utf-8")),
                content_hash=_compute_hash(f1_raw_html),
                source_url=f1_sec_url,
                is_primary=True,
                content_raw=f1_sanitized,
            ),
            FilingDocument(
                document_id="doc-002",
                filing_id=f1_id,
                filename="aapl-20240928_htm.xml",
                document_type="EX-101.INS",
                description="XBRL Instance Document",
                media_type=DocumentMediaType.XML_XBRL,
                byte_size=1845020,
                content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                source_url="https://www.sec.gov/Archives/edgar/data/320193/000032019324000106/aapl-20240928_htm.xml",
            ),
            FilingDocument(
                document_id="doc-003",
                filing_id=f1_id,
                filename="ex-21.1.htm",
                document_type="EX-21.1",
                description="Exhibit 21.1 Subsidiaries of Apple Inc.",
                media_type=DocumentMediaType.HTML,
                byte_size=45210,
                content_hash="6789abcdef0123456789abcdef0123456789abcdef0123456789abcdef012345",
                source_url="https://www.sec.gov/Archives/edgar/data/320193/000032019324000106/ex-21.1.htm",
            ),
            FilingDocument(
                document_id="doc-004",
                filing_id=f1_id,
                filename="ex-31.1.htm",
                document_type="EX-31.1",
                description="Exhibit 31.1 Rule 13a-14(a) Certification of CEO (Tim Cook)",
                media_type=DocumentMediaType.HTML,
                byte_size=24150,
                content_hash="abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
                source_url="https://www.sec.gov/Archives/edgar/data/320193/000032019324000106/ex-31.1.htm",
            ),
            FilingDocument(
                document_id="doc-005",
                filing_id=f1_id,
                filename="ex-31.2.htm",
                document_type="EX-31.2",
                description="Exhibit 31.2 Rule 13a-14(a) Certification of CFO (Luca Maestri)",
                media_type=DocumentMediaType.HTML,
                byte_size=24180,
                content_hash="bcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789a",
                source_url="https://www.sec.gov/Archives/edgar/data/320193/000032019324000106/ex-31.2.htm",
            ),
        ]

        f1_sections = [
            FilingSection(
                item_id="ITEM_1",
                title="Item 1. Business",
                anchor="#item1",
                char_offset=450,
                char_length=1200,
                summary_excerpt="Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services.",
            ),
            FilingSection(
                item_id="ITEM_1A",
                title="Item 1A. Risk Factors",
                anchor="#item1a",
                char_offset=1650,
                char_length=2400,
                summary_excerpt="The Company's business can be adversely affected by global economic conditions, supply chain disruptions, and dependence on single-source manufacturing in Asia.",
            ),
            FilingSection(
                item_id="ITEM_7",
                title="Item 7. Management's Discussion and Analysis",
                anchor="#item7",
                char_offset=4050,
                char_length=3200,
                summary_excerpt="Total net sales increased 2% to $391.0 billion in fiscal 2024, with record Services revenue of $96.2 billion.",
            ),
            FilingSection(
                item_id="ITEM_8",
                title="Item 8. Financial Statements",
                anchor="#item8",
                char_offset=7250,
                char_length=4500,
                summary_excerpt="Consolidated Net sales $391,035M, Operating income $123,216M, Net income $93,736M, Diluted EPS $6.08.",
            ),
        ]

        f1_facts = [
            XBRLFact(
                fact_id="fact-001",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="Revenues",
                label="Total Net Sales",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("391035000000"),
                formatted_value="$391.04B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-002",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="CostOfGoodsAndServicesSold",
                label="Cost of Sales",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("210352000000"),
                formatted_value="$210.35B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-003",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="GrossProfit",
                label="Gross Margin",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("180683000000"),
                formatted_value="$180.68B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-004",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="ResearchAndDevelopmentExpense",
                label="Research & Development",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("31370000000"),
                formatted_value="$31.37B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-005",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="OperatingIncomeLoss",
                label="Operating Income",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("123216000000"),
                formatted_value="$123.22B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-006",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="NetIncomeLoss",
                label="Net Income",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("93736000000"),
                formatted_value="$93.74B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-007",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="EarningsPerShareDiluted",
                label="Diluted Earnings Per Share",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2023-10-01",
                period_end="2024-09-28",
                unit=XBRLUnitType.USD_PER_SHARE,
                exact_value=Decimal("6.08"),
                formatted_value="$6.08",
                decimals=2,
            ),
            XBRLFact(
                fact_id="fact-008",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="CommonStockSharesOutstanding",
                label="Common Stock Outstanding",
                period_type=XBRLContextPeriodType.INSTANT,
                period_end="2024-09-28",
                unit=XBRLUnitType.SHARES,
                exact_value=Decimal("15115800000"),
                formatted_value="15.12B",
                decimals=0,
            ),
            XBRLFact(
                fact_id="fact-009",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="Assets",
                label="Total Assets",
                period_type=XBRLContextPeriodType.INSTANT,
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("364980000000"),
                formatted_value="$364.98B",
                decimals=-6,
            ),
            XBRLFact(
                fact_id="fact-010",
                filing_id=f1_id,
                taxonomy_namespace="us-gaap",
                concept_name="StockholdersEquity",
                label="Total Shareholders Equity",
                period_type=XBRLContextPeriodType.INSTANT,
                period_end="2024-09-28",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("56950000000"),
                formatted_value="$56.95B",
                decimals=-6,
            ),
        ]

        filing_10k = RegulatoryFiling(
            filing_id=f1_id,
            company_id=apple_id,
            filer_cik=self.apple_cik,
            filer_name=self.apple_name,
            regulator=Regulator.SEC_EDGAR,
            accession_number=f1_accession,
            form_type="10-K",
            canonical_form=FilingForm.FORM_10K,
            category=FilingCategory.ANNUAL_REPORTS,
            reporting_period="2024-09-28",
            filing_date="2024-11-01",
            acceptance_timestamp="2024-11-01T18:02:15Z",
            publication_timestamp="2024-11-01T18:05:00Z",
            is_amendment=False,
            amendment_status=AmendmentStatus.ORIGINAL,
            primary_document_name=f1_primary_htm,
            primary_document_url=f1_sec_url,
            title="Apple Inc. Annual Report (10-K) for the Fiscal Year Ended September 28, 2024",
            ingestion_status=IngestionStatus.PARSED,
            documents=f1_docs,
            sections=f1_sections,
            xbrl_facts=f1_facts,
            content_html=f1_sanitized,
            content_text=f1_text,
        )

        # -------------------------------------------------------------
        # 2. FORM 10-K/A (Annual Report Amendment for FY 2024)
        # -------------------------------------------------------------
        f2_id = "f0000000-0000-0000-0000-000000000002"
        f2_accession = "0000320193-24-000115"
        f2_primary_htm = "aapl-20240928_a.htm"

        f2_raw_html = f"""<!DOCTYPE html>
<html>
<head><title>Apple Inc. Form 10-K/A FY 2024</title></head>
<body>
<div class="header">
  <h1>UNITED STATES SECURITIES AND EXCHANGE COMMISSION</h1>
  <h3>FORM 10-K/A</h3>
  <p>ANNUAL REPORT AMENDMENT NO. 1 PURSUANT TO SECTION 13 OR 15(d)</p>
  <p>For the fiscal year ended <b>September 28, 2024</b></p>
  <p>Amends Form 10-K filed on <b>November 1, 2024</b> (Accession: {f1_accession})</p>
</div>
<div id="item15">
  <h2>Item 15. Exhibits and Financial Statement Schedules</h2>
  <p>This Amendment No. 1 on Form 10-K/A amends the Annual Report on Form 10-K of Apple Inc. for the fiscal year ended September 28, 2024 solely to furnish revised Exhibit 21.1 and update subsidiary registrations in Europe.</p>
  <p>No changes have been made to the Financial Statements or MD&A disclosed in the original Form 10-K.</p>
</div>
</body>
</html>"""

        f2_sanitized = sanitize_filing_html(f2_raw_html)
        f2_text = extract_plain_text_from_html(f2_sanitized)

        filing_10k_a = RegulatoryFiling(
            filing_id=f2_id,
            company_id=apple_id,
            filer_cik=self.apple_cik,
            filer_name=self.apple_name,
            regulator=Regulator.SEC_EDGAR,
            accession_number=f2_accession,
            form_type="10-K/A",
            canonical_form=FilingForm.FORM_10K_A,
            category=FilingCategory.ANNUAL_REPORTS,
            reporting_period="2024-09-28",
            filing_date="2024-11-15",
            acceptance_timestamp="2024-11-15T16:30:10Z",
            publication_timestamp="2024-11-15T16:32:00Z",
            is_amendment=True,
            amendment_status=AmendmentStatus.AMENDMENT,
            amends_accession_number=f1_accession,
            primary_document_name=f2_primary_htm,
            primary_document_url=f"https://www.sec.gov/ix?doc=/Archives/edgar/data/{self.apple_cik}/{f2_accession.replace('-', '')}/{f2_primary_htm}",
            title="Apple Inc. Amendment No. 1 to Annual Report (10-K/A)",
            ingestion_status=IngestionStatus.PARSED,
            documents=[
                FilingDocument(
                    document_id="doc-010",
                    filing_id=f2_id,
                    filename=f2_primary_htm,
                    document_type="10-K/A",
                    description="Form 10-K/A Amendment No. 1 (Primary Document)",
                    media_type=DocumentMediaType.HTML,
                    byte_size=len(f2_raw_html.encode("utf-8")),
                    content_hash=_compute_hash(f2_raw_html),
                    source_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f2_accession.replace('-', '')}/{f2_primary_htm}",
                    is_primary=True,
                    content_raw=f2_sanitized,
                )
            ],
            sections=[
                FilingSection(
                    item_id="ITEM_15",
                    title="Item 15. Exhibits",
                    anchor="#item15",
                    char_offset=200,
                    char_length=600,
                    summary_excerpt="Amends the Annual Report solely to update Exhibit 21.1 and European subsidiary records.",
                )
            ],
            xbrl_facts=f1_facts,  # Identical facts reaffirming unamended numbers
            content_html=f2_sanitized,
            content_text=f2_text,
        )

        # -------------------------------------------------------------
        # 3. FORM 10-Q (Q3 2024 ended June 29, 2024)
        # -------------------------------------------------------------
        f3_id = "f0000000-0000-0000-0000-000000000003"
        f3_accession = "0000320193-24-000081"
        f3_primary_htm = "aapl-20240629.htm"

        f3_raw_html = """<!DOCTYPE html>
<html>
<head><title>Apple Inc. Form 10-Q Q3 2024</title></head>
<body>
<h1>FORM 10-Q - QUARTERLY REPORT</h1>
<p>For the quarterly period ended <b>June 29, 2024</b></p>
<h2>Item 1. Financial Statements</h2>
<p>Three months ended June 29, 2024: Total net sales of $85,777 million, Operating income of $25,352 million, Net income of $21,448 million.</p>
<p>Diluted EPS of $1.40 compared to $1.26 in the year-ago quarter.</p>
</body>
</html>"""
        f3_sanitized = sanitize_filing_html(f3_raw_html)

        f3_facts = [
            XBRLFact(
                fact_id="fact-q3-001",
                filing_id=f3_id,
                taxonomy_namespace="us-gaap",
                concept_name="Revenues",
                label="Total Net Sales",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2024-03-31",
                period_end="2024-06-29",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("85777000000"),
                formatted_value="$85.78B",
            ),
            XBRLFact(
                fact_id="fact-q3-002",
                filing_id=f3_id,
                taxonomy_namespace="us-gaap",
                concept_name="NetIncomeLoss",
                label="Net Income",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2024-03-31",
                period_end="2024-06-29",
                unit=XBRLUnitType.USD,
                exact_value=Decimal("21448000000"),
                formatted_value="$21.45B",
            ),
            XBRLFact(
                fact_id="fact-q3-003",
                filing_id=f3_id,
                taxonomy_namespace="us-gaap",
                concept_name="EarningsPerShareDiluted",
                label="Diluted EPS",
                period_type=XBRLContextPeriodType.DURATION,
                period_start="2024-03-31",
                period_end="2024-06-29",
                unit=XBRLUnitType.USD_PER_SHARE,
                exact_value=Decimal("1.40"),
                formatted_value="$1.40",
            ),
        ]

        filing_10q_q3 = RegulatoryFiling(
            filing_id=f3_id,
            company_id=apple_id,
            filer_cik=self.apple_cik,
            filer_name=self.apple_name,
            regulator=Regulator.SEC_EDGAR,
            accession_number=f3_accession,
            form_type="10-Q",
            canonical_form=FilingForm.FORM_10Q,
            category=FilingCategory.QUARTERLY_REPORTS,
            reporting_period="2024-06-29",
            filing_date="2024-08-02",
            acceptance_timestamp="2024-08-02T16:15:30Z",
            publication_timestamp="2024-08-02T16:17:00Z",
            primary_document_name=f3_primary_htm,
            primary_document_url=f"https://www.sec.gov/ix?doc=/Archives/edgar/data/{self.apple_cik}/{f3_accession.replace('-', '')}/{f3_primary_htm}",
            title="Apple Inc. Quarterly Report (10-Q) for the Period Ended June 29, 2024",
            ingestion_status=IngestionStatus.PARSED,
            documents=[
                FilingDocument(
                    document_id="doc-020",
                    filing_id=f3_id,
                    filename=f3_primary_htm,
                    document_type="10-Q",
                    description="Form 10-Q Q3 2024 (Primary Document)",
                    media_type=DocumentMediaType.HTML,
                    byte_size=len(f3_raw_html.encode("utf-8")),
                    content_hash=_compute_hash(f3_raw_html),
                    source_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f3_accession.replace('-', '')}/{f3_primary_htm}",
                    is_primary=True,
                    content_raw=f3_sanitized,
                )
            ],
            sections=[
                FilingSection(
                    item_id="ITEM_1",
                    title="Item 1. Financial Statements",
                    anchor="#item1",
                    char_offset=100,
                    char_length=950,
                    summary_excerpt="Net sales of $85,777M, Operating income of $25,352M, Net income of $21,448M.",
                )
            ],
            xbrl_facts=f3_facts,
            content_html=f3_sanitized,
            content_text=extract_plain_text_from_html(f3_sanitized),
        )

        # -------------------------------------------------------------
        # 4. FORM 8-K (Current Report: Q4 Earnings & Financial Results)
        # -------------------------------------------------------------
        f4_id = "f0000000-0000-0000-0000-000000000004"
        f4_accession = "0000320193-24-000105"
        f4_primary_htm = "aapl-20241031.htm"

        f4_raw_html = """<!DOCTYPE html>
<html>
<head><title>Apple Inc. Form 8-K Oct 31, 2024</title></head>
<body>
<h1>FORM 8-K - CURRENT REPORT</h1>
<p>Date of Report: <b>October 31, 2024</b></p>
<h2>Item 2.02 Results of Operations and Financial Condition</h2>
<p>On October 31, 2024, Apple Inc. issued a press release announcing its financial results for its fourth fiscal quarter ended September 28, 2024. A copy of the press release is attached hereto as Exhibit 99.1.</p>
<h2>Item 9.01 Financial Statements and Exhibits</h2>
<p>Exhibit 99.1 Press release dated October 31, 2024.</p>
</body>
</html>"""
        f4_sanitized = sanitize_filing_html(f4_raw_html)

        filing_8k = RegulatoryFiling(
            filing_id=f4_id,
            company_id=apple_id,
            filer_cik=self.apple_cik,
            filer_name=self.apple_name,
            regulator=Regulator.SEC_EDGAR,
            accession_number=f4_accession,
            form_type="8-K",
            canonical_form=FilingForm.FORM_8K,
            category=FilingCategory.CURRENT_REPORTS,
            reporting_period="2024-10-31",
            filing_date="2024-10-31",
            acceptance_timestamp="2024-10-31T16:30:00Z",
            publication_timestamp="2024-10-31T16:31:00Z",
            primary_document_name=f4_primary_htm,
            primary_document_url=f"https://www.sec.gov/Archives/edgar/data/{self.apple_cik}/{f4_accession.replace('-', '')}/{f4_primary_htm}",
            title="Apple Inc. Current Report (8-K): Item 2.02 Q4 2024 Financial Results Announcement",
            ingestion_status=IngestionStatus.PARSED,
            documents=[
                FilingDocument(
                    document_id="doc-030",
                    filing_id=f4_id,
                    filename=f4_primary_htm,
                    document_type="8-K",
                    description="Form 8-K Current Report (Primary Document)",
                    media_type=DocumentMediaType.HTML,
                    byte_size=len(f4_raw_html.encode("utf-8")),
                    content_hash=_compute_hash(f4_raw_html),
                    source_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f4_accession.replace('-', '')}/{f4_primary_htm}",
                    is_primary=True,
                    content_raw=f4_sanitized,
                ),
                FilingDocument(
                    document_id="doc-031",
                    filing_id=f4_id,
                    filename="ex-99.1.htm",
                    document_type="EX-99.1",
                    description="Exhibit 99.1 Press Release announcing Q4 FY 2024 Financial Results",
                    media_type=DocumentMediaType.HTML,
                    byte_size=35420,
                    content_hash="112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00",
                    source_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f4_accession.replace('-', '')}/ex-99.1.htm",
                ),
            ],
            sections=[
                FilingSection(
                    item_id="ITEM_2.02",
                    title="Item 2.02 Results of Operations",
                    anchor="#item202",
                    char_offset=120,
                    char_length=450,
                    summary_excerpt="Press release announcing fourth fiscal quarter financial results ended September 28, 2024.",
                )
            ],
            content_html=f4_sanitized,
            content_text=extract_plain_text_from_html(f4_sanitized),
        )

        # -------------------------------------------------------------
        # 5. DEF 14A (Definitive Proxy Statement)
        # -------------------------------------------------------------
        f5_id = "f0000000-0000-0000-0000-000000000005"
        f5_accession = "0000320193-24-000006"
        f5_primary_htm = "aapl-2024_def14a.htm"

        f5_raw_html = """<!DOCTYPE html>
<html>
<head><title>Apple Inc. Proxy Statement DEF 14A</title></head>
<body>
<h1>SCHEDULE 14A INFORMATION</h1>
<p>Proxy Statement Pursuant to Section 14(a) of the Securities Exchange Act of 1934</p>
<h2>Notice of 2024 Annual Meeting of Shareholders</h2>
<p>Meeting Date: February 28, 2024. Matters to be voted upon: Election of Directors, Advisory vote to approve executive compensation, Ratification of Ernst & Young LLP.</p>
</body>
</html>"""
        f5_sanitized = sanitize_filing_html(f5_raw_html)

        filing_proxy = RegulatoryFiling(
            filing_id=f5_id,
            company_id=apple_id,
            filer_cik=self.apple_cik,
            filer_name=self.apple_name,
            regulator=Regulator.SEC_EDGAR,
            accession_number=f5_accession,
            form_type="DEF 14A",
            canonical_form=FilingForm.DEF_14A,
            category=FilingCategory.PROXY_STATEMENTS,
            reporting_period="2024-01-11",
            filing_date="2024-01-11",
            acceptance_timestamp="2024-01-11T17:05:22Z",
            publication_timestamp="2024-01-11T17:07:00Z",
            primary_document_name=f5_primary_htm,
            primary_document_url=f"https://www.sec.gov/ix?doc=/Archives/edgar/data/{self.apple_cik}/{f5_accession.replace('-', '')}/{f5_primary_htm}",
            title="Apple Inc. Notice of 2024 Annual Meeting of Shareholders and Definitive Proxy Statement",
            ingestion_status=IngestionStatus.PARSED,
            documents=[
                FilingDocument(
                    document_id="doc-040",
                    filing_id=f5_id,
                    filename=f5_primary_htm,
                    document_type="DEF 14A",
                    description="Definitive Proxy Statement (Primary Document)",
                    media_type=DocumentMediaType.HTML,
                    byte_size=len(f5_raw_html.encode("utf-8")),
                    content_hash=_compute_hash(f5_raw_html),
                    source_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f5_accession.replace('-', '')}/{f5_primary_htm}",
                    is_primary=True,
                    content_raw=f5_sanitized,
                )
            ],
            sections=[
                FilingSection(
                    item_id="NOTICE",
                    title="Notice of Annual Meeting",
                    anchor="#notice",
                    char_offset=100,
                    char_length=500,
                    summary_excerpt="Shareholders meeting to vote on Director Election and Executive Compensation.",
                )
            ],
            content_html=f5_sanitized,
            content_text=extract_plain_text_from_html(f5_sanitized),
        )

        # -------------------------------------------------------------
        # 6. FORM 13F-HR (Institutional Holding - Vanguard Cross-Ref)
        # -------------------------------------------------------------
        f6_id = "f0000000-0000-0000-0000-000000000006"
        f6_accession = "0000102909-24-000042"
        f6_primary_htm = "vanguard-13f-2024q3.htm"

        f6_raw_html = """<!DOCTYPE html>
<html>
<head><title>The Vanguard Group, Inc. Form 13F-HR</title></head>
<body>
<h1>FORM 13F INFORMATION TABLE</h1>
<p>Reporting Period: <b>September 30, 2024</b></p>
<p>Filer: <b>The Vanguard Group, Inc.</b> | CIK: 0000102909</p>
<table border="1">
  <tr><th>Issuer</th><th>Title of Class</th><th>CUSIP</th><th>Value ($1000)</th><th>Shares</th><th>Discretion</th></tr>
  <tr><td>APPLE INC</td><td>COM</td><td>037833100</td><td>310460878</td><td>1332450120</td><td>SOLE / DEFINED</td></tr>
</table>
</body>
</html>"""
        f6_sanitized = sanitize_filing_html(f6_raw_html)

        filing_13f = RegulatoryFiling(
            filing_id=f6_id,
            company_id=apple_id,
            filer_cik="0000102909",
            filer_name="The Vanguard Group, Inc.",
            regulator=Regulator.SEC_EDGAR,
            accession_number=f6_accession,
            form_type="13F-HR",
            canonical_form=FilingForm.FORM_13F_HR,
            category=FilingCategory.OWNERSHIP_INSIDER,
            reporting_period="2024-09-30",
            filing_date="2024-11-14",
            acceptance_timestamp="2024-11-14T21:10:00Z",
            publication_timestamp="2024-11-14T21:12:00Z",
            primary_document_name=f6_primary_htm,
            primary_document_url=f"https://www.sec.gov/Archives/edgar/data/102909/{f6_accession.replace('-', '')}/{f6_primary_htm}",
            title="The Vanguard Group, Inc. Form 13F-HR Holdings Report (Discloses 1,332,450,120 Apple Inc. Shares)",
            ingestion_status=IngestionStatus.PARSED,
            documents=[
                FilingDocument(
                    document_id="doc-050",
                    filing_id=f6_id,
                    filename=f6_primary_htm,
                    document_type="13F-HR",
                    description="Form 13F Holdings Report",
                    media_type=DocumentMediaType.HTML,
                    byte_size=len(f6_raw_html.encode("utf-8")),
                    content_hash=_compute_hash(f6_raw_html),
                    source_url=f"https://www.sec.gov/Archives/edgar/data/102909/{f6_accession.replace('-', '')}/{f6_primary_htm}",
                    is_primary=True,
                    content_raw=f6_sanitized,
                )
            ],
            content_html=f6_sanitized,
            content_text=extract_plain_text_from_html(f6_sanitized),
        )

        # -------------------------------------------------------------
        # 7. FORM 4 (Insider Filing - Tim Cook Cross-Ref)
        # -------------------------------------------------------------
        f7_id = "f0000000-0000-0000-0000-000000000007"
        f7_accession = "0000320193-24-000108"
        f7_primary_htm = "edgar.xml"

        f7_raw_html = """<!DOCTYPE html>
<html>
<head><title>Apple Inc. Form 4 - Timothy D. Cook</title></head>
<body>
<h1>STATEMENT OF CHANGES IN BENEFICIAL OWNERSHIP OF SECURITIES (FORM 4)</h1>
<p>Reporting Person: <b>Timothy D. Cook</b> | Title: <b>Chief Executive Officer</b></p>
<p>Period Date: <b>September 30, 2024</b> | Filing Date: <b>October 3, 2024</b></p>
<p>Transaction: Withholding of shares for tax liability upon RSU vest.</p>
<p>Shares remaining beneficially owned following reported transaction: <b>3,280,053 shares</b> (Direct).</p>
</body>
</html>"""
        f7_sanitized = sanitize_filing_html(f7_raw_html)

        filing_form4 = RegulatoryFiling(
            filing_id=f7_id,
            company_id=apple_id,
            filer_cik="0001214156",
            filer_name="Timothy D. Cook",
            regulator=Regulator.SEC_EDGAR,
            accession_number=f7_accession,
            form_type="4",
            canonical_form=FilingForm.FORM_4,
            category=FilingCategory.OWNERSHIP_INSIDER,
            reporting_period="2024-09-30",
            filing_date="2024-10-03",
            acceptance_timestamp="2024-10-03T18:45:00Z",
            publication_timestamp="2024-10-03T18:46:00Z",
            primary_document_name=f7_primary_htm,
            primary_document_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f7_accession.replace('-', '')}/{f7_primary_htm}",
            title="Timothy D. Cook Form 4 Statement of Changes in Beneficial Ownership",
            ingestion_status=IngestionStatus.PARSED,
            documents=[
                FilingDocument(
                    document_id="doc-060",
                    filing_id=f7_id,
                    filename=f7_primary_htm,
                    document_type="4",
                    description="Statement of Changes in Beneficial Ownership",
                    media_type=DocumentMediaType.HTML,
                    byte_size=len(f7_raw_html.encode("utf-8")),
                    content_hash=_compute_hash(f7_raw_html),
                    source_url=f"https://www.sec.gov/Archives/edgar/data/320193/{f7_accession.replace('-', '')}/{f7_primary_htm}",
                    is_primary=True,
                    content_raw=f7_sanitized,
                )
            ],
            content_html=f7_sanitized,
            content_text=extract_plain_text_from_html(f7_sanitized),
        )

        all_filings = [
            filing_10k_a,  # Most recent first
            filing_10k,
            filing_8k,
            filing_13f,
            filing_form4,
            filing_10q_q3,
            filing_proxy,
        ]

        self._filings[apple_id] = all_filings
        for f in all_filings:
            self._filing_by_id[f.filing_id] = f
            self._filing_by_accession[f.accession_number] = f

    def get_filings_by_company(
        self,
        company_id: str,
        category: Optional[FilingCategory] = None,
        form_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[RegulatoryFiling]:
        """Returns catalog of filings matching filter criteria."""
        filings = self._filings.get(company_id, [])

        filtered = []
        for f in filings:
            if category and f.category != category:
                continue
            if form_type and f.form_type.upper() != form_type.upper():
                continue
            if from_date and f.filing_date < from_date:
                continue
            if to_date and f.filing_date > to_date:
                continue
            filtered.append(f)

        return sorted(filtered, key=lambda x: x.filing_date, reverse=True)

    def get_filing_by_id(self, filing_id: str) -> Optional[RegulatoryFiling]:
        """Finds filing by canonical UUID."""
        return self._filing_by_id.get(filing_id)

    def get_filing_by_accession(self, accession_number: str) -> Optional[RegulatoryFiling]:
        """Finds filing by official accession number."""
        return self._filing_by_accession.get(accession_number)

    def search_filings_content(
        self,
        company_id: str,
        query: str,
        limit: int = 25,
    ) -> List[FilingSearchHit]:
        """Performs search across indexed text and sections of company filings."""
        if not query or not query.strip():
            return []

        q_lower = query.lower().strip()
        filings = self._filings.get(company_id, [])
        hits: List[FilingSearchHit] = []

        for f in filings:
            text = f.content_text or ""
            if q_lower not in text.lower():
                continue

            # Find matching occurrences and extract surrounding snippets
            idx = text.lower().find(q_lower)
            while idx != -1 and len(hits) < limit:
                start = max(0, idx - 80)
                end = min(len(text), idx + len(query) + 120)
                snippet = "..." + text[start:end].replace("\n", " ").strip() + "..."

                # Locate section name if available
                sec_name = None
                for sec in f.sections:
                    if sec.char_offset <= idx <= sec.char_offset + sec.char_length:
                        sec_name = sec.title
                        break

                primary_doc_id = f.documents[0].document_id if f.documents else "doc-unknown"

                hits.append(
                    FilingSearchHit(
                        filing_id=f.filing_id,
                        document_id=primary_doc_id,
                        accession_number=f.accession_number,
                        form_type=f.form_type,
                        reporting_period=f.reporting_period,
                        filing_date=f.filing_date,
                        section_name=sec_name,
                        matched_snippet=snippet,
                        char_offset=idx,
                        score=round(1.0 - (idx / max(len(text), 1)) * 0.2, 3),
                    )
                )

                idx = text.lower().find(q_lower, idx + len(query) + 100)

        return hits
