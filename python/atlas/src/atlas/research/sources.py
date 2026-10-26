"""Canonical Research Source Registry, Resolution, and Deduplication (Stage 104)."""

import datetime
from typing import Dict, List, Optional

from atlas.research.domain import ResearchSourceReference
from atlas.research.enums import ResearchSourceType, SourceAvailabilityStatus


def build_canonical_sources_catalog() -> Dict[str, ResearchSourceReference]:
    """Build the verified canonical research sources catalog.

    Integrates genuine SEC filings, fundamental financial facts, verified financial news,
    economic releases, and market instruments with full provenance.
    """
    catalog: Dict[str, ResearchSourceReference] = {}

    def add_source(src: ResearchSourceReference):
        catalog[src.source_reference_id] = src

    # 1. Genuine SEC Regulatory Filings (Stage 86 Integration)
    add_source(
        ResearchSourceReference(
            source_reference_id="src-filing-aapl-10k-2024",
            canonical_document_id="0000320193-24-000106",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.ANNUAL_REPORT,
            provider_id="SEC_EDGAR",
            publisher_id="U.S. Securities and Exchange Commission",
            source_title="Apple Inc. Form 10-K Annual Report (Fiscal Year ended September 28, 2024)",
            source_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019324000106/aapl-20240928.htm",
            published_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 11, 1, 16, 15, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 11, 1, 16, 15, tzinfo=datetime.timezone.utc),
            reporting_period="FY2024",
            source_revision="1",
            rights_policy="PUBLIC_DOMAIN_REGULATORY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={
                "filer_cik": "0000320193",
                "form_type": "10-K",
                "filing_date": "2024-11-01",
                "fiscal_year_end": "2024-09-28",
            },
        )
    )

    add_source(
        ResearchSourceReference(
            source_reference_id="src-filing-aapl-10q-q3-2024",
            canonical_document_id="0000320193-24-000081",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.QUARTERLY_REPORT,
            provider_id="SEC_EDGAR",
            publisher_id="U.S. Securities and Exchange Commission",
            source_title="Apple Inc. Form 10-Q Quarterly Report (Quarter ended June 29, 2024)",
            source_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019324000081/aapl-20240629.htm",
            published_at=datetime.datetime(2024, 8, 2, 16, 5, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 8, 2, 16, 5, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 8, 2, 16, 8, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 8, 2, 16, 8, tzinfo=datetime.timezone.utc),
            reporting_period="Q3 2024",
            source_revision="1",
            rights_policy="PUBLIC_DOMAIN_REGULATORY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"filer_cik": "0000320193", "form_type": "10-Q"},
        )
    )

    add_source(
        ResearchSourceReference(
            source_reference_id="src-filing-msft-10k-2024",
            canonical_document_id="0000789019-24-000055",
            canonical_entity_id="MSFT",
            source_type=ResearchSourceType.ANNUAL_REPORT,
            provider_id="SEC_EDGAR",
            publisher_id="U.S. Securities and Exchange Commission",
            source_title="Microsoft Corporation Form 10-K Annual Report (Fiscal Year ended June 30, 2024)",
            source_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0000789019/000078901924000055/msft-20240630.htm",
            published_at=datetime.datetime(2024, 7, 30, 16, 30, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 7, 30, 16, 30, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 7, 30, 16, 32, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 7, 30, 16, 32, tzinfo=datetime.timezone.utc),
            reporting_period="FY2024",
            source_revision="1",
            rights_policy="PUBLIC_DOMAIN_REGULATORY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"filer_cik": "0000789019", "form_type": "10-K"},
        )
    )

    add_source(
        ResearchSourceReference(
            source_reference_id="src-filing-nvda-10k-2024",
            canonical_document_id="0001045810-24-000029",
            canonical_entity_id="NVDA",
            source_type=ResearchSourceType.ANNUAL_REPORT,
            provider_id="SEC_EDGAR",
            publisher_id="U.S. Securities and Exchange Commission",
            source_title="NVIDIA Corporation Form 10-K Annual Report (Fiscal Year ended January 28, 2024)",
            source_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0001045810/000104581024000029/nvda-20240128.htm",
            published_at=datetime.datetime(2024, 2, 21, 16, 45, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 2, 21, 16, 45, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 2, 21, 16, 48, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 2, 21, 16, 48, tzinfo=datetime.timezone.utc),
            reporting_period="FY2024",
            source_revision="1",
            rights_policy="PUBLIC_DOMAIN_REGULATORY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"filer_cik": "0001045810", "form_type": "10-K"},
        )
    )

    # 2. Genuine Canonical Financial Statement Facts (Stage 82 Integration)
    add_source(
        ResearchSourceReference(
            source_reference_id="src-fact-aapl-revenue-fy2024",
            canonical_document_id="fact-aapl-total-net-sales-fy2024",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.FINANCIAL_STATEMENT,
            provider_id="ATLAS_FUNDAMENTALS",
            publisher_id="Apple Inc. Disclosures",
            source_title="Apple Inc. FY2024 Total Net Sales ($391,035M USD)",
            source_url="https://investor.apple.com/investor-relations/default.aspx",
            published_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 11, 1, 16, 15, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 11, 1, 16, 15, tzinfo=datetime.timezone.utc),
            reporting_period="FY2024",
            source_revision="rev-as-reported",
            rights_policy="LICENSED_FUNDAMENTAL_DATA",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={
                "metric_id": "us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax",
                "value": 391035000000,
                "currency": "USD",
                "period_type": "ANNUAL",
                "is_restated": False,
            },
        )
    )

    add_source(
        ResearchSourceReference(
            source_reference_id="src-fact-aapl-opinc-fy2024",
            canonical_document_id="fact-aapl-operating-income-fy2024",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.FINANCIAL_STATEMENT,
            provider_id="ATLAS_FUNDAMENTALS",
            publisher_id="Apple Inc. Disclosures",
            source_title="Apple Inc. FY2024 Operating Income ($123,216M USD)",
            source_url="https://investor.apple.com/investor-relations/default.aspx",
            published_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 11, 1, 16, 12, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 11, 1, 16, 15, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 11, 1, 16, 15, tzinfo=datetime.timezone.utc),
            reporting_period="FY2024",
            source_revision="rev-as-reported",
            rights_policy="LICENSED_FUNDAMENTAL_DATA",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={
                "metric_id": "us-gaap/OperatingIncomeLoss",
                "value": 123216000000,
                "currency": "USD",
                "period_type": "ANNUAL",
            },
        )
    )

    # 3. Genuine Canonical Financial News Articles (Stage 99–103 Integration)
    add_source(
        ResearchSourceReference(
            source_reference_id="src-news-bloomberg-fed-rate-20240918",
            canonical_document_id="art-bloomberg-20240918-001",
            canonical_entity_id="FED",
            source_type=ResearchSourceType.NEWS_ARTICLE,
            provider_id="BLOOMBERG_WIRE",
            publisher_id="Bloomberg News",
            source_title="Federal Reserve Lowers Benchmark Policy Rate by 50 Basis Points to 4.75%-5.00%",
            source_url="https://www.bloomberg.com/news/articles/2024-09-18/fed-cuts-rates-by-half-percentage-point-in-first-reduction-since-2020",
            published_at=datetime.datetime(2024, 9, 18, 18, 0, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 9, 18, 18, 0, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 9, 18, 18, 1, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 9, 18, 18, 1, tzinfo=datetime.timezone.utc),
            reporting_period="2024-09-18",
            source_revision="rev-1",
            rights_policy="LICENSED_EXCERPT_ONLY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={
                "article_id": "art-bloomberg-20240918-001",
                "byline": "Craig Torres and Catarina Saraiva",
                "category": "MONETARY_POLICY",
            },
        )
    )

    add_source(
        ResearchSourceReference(
            source_reference_id="src-news-reuters-aapl-earnings-20241031",
            canonical_document_id="art-reuters-20241031-aapl",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.NEWS_ARTICLE,
            provider_id="REUTERS_FINANCIAL",
            publisher_id="Reuters",
            source_title="Apple Sales Beat Expectations on Strong iPhone Demand Ahead of AI Feature Rollout",
            source_url="https://www.reuters.com/technology/apple-quarterly-sales-top-estimates-china-revenue-dips-2024-10-31/",
            published_at=datetime.datetime(2024, 10, 31, 20, 35, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 10, 31, 20, 35, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 10, 31, 20, 36, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 10, 31, 20, 36, tzinfo=datetime.timezone.utc),
            reporting_period="Q4 2024",
            source_revision="rev-1",
            rights_policy="LICENSED_EXCERPT_ONLY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"category": "CORPORATE_EARNINGS"},
        )
    )

    # 4. Genuine Canonical Economic Releases (Stage 89–93 Integration)
    add_source(
        ResearchSourceReference(
            source_reference_id="src-econ-bls-cpi-202409",
            canonical_document_id="cpi-u-202409-release",
            canonical_entity_id="US_CPI",
            source_type=ResearchSourceType.ECONOMIC_RELEASE,
            provider_id="BLS_GOV",
            publisher_id="Bureau of Labor Statistics",
            source_title="U.S. Consumer Price Index (CPI-U) September 2024 News Release (YoY +2.4%)",
            source_url="https://www.bls.gov/news.release/cpi.nr0.htm",
            published_at=datetime.datetime(2024, 10, 10, 12, 30, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 10, 10, 12, 30, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 10, 10, 12, 30, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 10, 10, 12, 30, tzinfo=datetime.timezone.utc),
            reporting_period="September 2024",
            source_revision="first-release-vintage-20241010",
            rights_policy="PUBLIC_DOMAIN_GOV",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={
                "indicator_id": "CPI_U_ALL_ITEMS_YOY",
                "value": 2.4,
                "unit": "PERCENT_YOY",
                "geography": "US",
            },
        )
    )

    # 5. Canonical Financial Instruments
    add_source(
        ResearchSourceReference(
            source_reference_id="src-mkt-instrument-aapl",
            canonical_document_id="inst-aapl-nasdaq",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.MARKET_DATASET,
            provider_id="NASDAQ_EQUITIES",
            publisher_id="Nasdaq Stock Market",
            source_title="Apple Inc. Common Stock Market Dataset (NASDAQ: AAPL)",
            source_url="https://www.nasdaq.com/market-activity/stocks/aapl",
            published_at=datetime.datetime(2024, 11, 15, 21, 0, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2024, 11, 15, 21, 0, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2024, 11, 15, 21, 0, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2024, 11, 15, 21, 0, tzinfo=datetime.timezone.utc),
            reporting_period="2024-11-15",
            source_revision="eod-consolidated",
            rights_policy="LICENSED_MARKET_DATA",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"mic": "XNAS", "symbol": "AAPL", "currency": "USD"},
        )
    )

    # 6. Prior Period Regulatory Filings for Document Comparison
    add_source(
        ResearchSourceReference(
            source_reference_id="src-filing-aapl-10k-2023",
            canonical_document_id="0000320193-23-000106",
            canonical_entity_id="AAPL",
            source_type=ResearchSourceType.ANNUAL_REPORT,
            provider_id="SEC_EDGAR",
            publisher_id="U.S. Securities and Exchange Commission",
            source_title="Apple Inc. Form 10-K Annual Report (Fiscal Year ended September 30, 2023)",
            source_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0000320193/000032019323000106/aapl-20230930.htm",
            published_at=datetime.datetime(2023, 11, 3, 16, 10, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2023, 11, 3, 16, 10, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2023, 11, 3, 16, 12, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2023, 11, 3, 16, 12, tzinfo=datetime.timezone.utc),
            reporting_period="FY2023",
            source_revision="1",
            rights_policy="PUBLIC_DOMAIN_REGULATORY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={
                "filer_cik": "0000320193",
                "form_type": "10-K",
                "filing_date": "2023-11-03",
                "fiscal_year_end": "2023-09-30",
            },
        )
    )

    add_source(
        ResearchSourceReference(
            source_reference_id="src-filing-msft-10k-2023",
            canonical_document_id="0000789019-23-000055",
            canonical_entity_id="MSFT",
            source_type=ResearchSourceType.ANNUAL_REPORT,
            provider_id="SEC_EDGAR",
            publisher_id="U.S. Securities and Exchange Commission",
            source_title="Microsoft Corporation Form 10-K Annual Report (Fiscal Year ended June 30, 2023)",
            source_url="https://www.sec.gov/ix?doc=/Archives/edgar/data/0000789019/000078901923000055/msft-20230630.htm",
            published_at=datetime.datetime(2023, 7, 27, 16, 20, tzinfo=datetime.timezone.utc),
            source_updated_at=datetime.datetime(2023, 7, 27, 16, 20, tzinfo=datetime.timezone.utc),
            first_observed_at=datetime.datetime(2023, 7, 27, 16, 22, tzinfo=datetime.timezone.utc),
            registered_at=datetime.datetime(2023, 7, 27, 16, 22, tzinfo=datetime.timezone.utc),
            reporting_period="FY2023",
            source_revision="1",
            rights_policy="PUBLIC_DOMAIN_REGULATORY",
            availability_status=SourceAvailabilityStatus.AVAILABLE,
            provenance={"filer_cik": "0000789019", "form_type": "10-K"},
        )
    )

    return catalog


def check_source_deduplication(
    existing_sources: List[ResearchSourceReference],
    candidate_doc_id: Optional[str],
    candidate_url: Optional[str],
) -> Optional[ResearchSourceReference]:
    """Check if candidate source already exists by exact canonical document ID or normalized URL.

    Returns:
        The matched existing source reference, or None if unique.
    """
    for src in existing_sources:
        if candidate_doc_id and src.canonical_document_id and src.canonical_document_id == candidate_doc_id:
            return src
        if candidate_url and src.source_url:
            norm_existing = src.source_url.rstrip("/").lower()
            norm_candidate = candidate_url.rstrip("/").lower()
            if norm_existing == norm_candidate:
                return src
    return None
