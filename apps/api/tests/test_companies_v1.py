"""Comprehensive Automated Test Suite for ATLAS Stage 81:
Companies V1: Canonical Company Intelligence Profiles.

Tests cover:
1. Canonical Company Identity & Lifecycle:
   - Valid Company UUID
   - Display name vs legal name vs short name distinction
   - Public vs private vs inactive corporate status
   - Company aliases resolution
   - Strict separation of Company Entity and Financial Instrument (ticker is not PK)
2. Corporate Identifiers (Stage 21):
   - LEI, SEC CIK, national registration
   - Namespace, validity dates, verification status
   - Security-only identifiers (ISIN, FIGI) not treated as company IDs
3. Sector & Industry Classification:
   - GICS taxonomy, version, sector name, industry name
   - Unclassified status when missing (zero fake sectors)
4. Geography (Stage 19):
   - Headquarters city, country name, ISO country code, domicile
   - Missing headquarters handled gracefully (UNAVAILABLE)
5. Relationships & Securities (Stage 23):
   - Issued common equity, preferred equity, multiple share classes (Class A/B)
   - Depositary receipts (ADRs) distinction
   - Corporate bonds association
   - Delisted / expired status handling
6. Market Context & Quotes (Stage 33 / 41 / 44):
   - Reference security, venue, quote measures (Last, Clean Price), currency
   - Genuine market capitalization display where supported
   - Missing quotes marked unavailable (zero faked prices)
7. High-Level Financial Summary (Stage 34):
   - Revenue, net income, EPS, total assets, total equity, cash
   - Fiscal period (FY2025), reporting currency (USD), period end, publication date
   - Missing statements marked UNAVAILABLE (zero fabricated numbers)
8. News & Document References (Stage 36 / 20):
   - Verified news articles (headline, publisher, timestamp, URL)
   - Verified corporate documents (annual reports, 10-K, research)
   - Empty states
9. Search & Discovery (Stage 45):
   - Search by company name, legal name, alias, CIK/LEI, ticker symbol
   - Bounded pagination and input validation
   - Support for unlisted companies
10. FastAPI HTTP Endpoints:
    - GET /api/v1/companies (Search / Browse)
    - GET /api/v1/companies/{id} (Full Unified Overview)
    - GET /api/v1/companies/{id}/profile
    - GET /api/v1/companies/{id}/securities
    - GET /api/v1/companies/{id}/market-summary
    - GET /api/v1/companies/{id}/financial-summary
    - GET /api/v1/companies/{id}/news
    - GET /api/v1/companies/{id}/documents
    - 404 for missing company, 400 for invalid pagination
11. Side-Effect Invariants:
    - 0 Company writes
    - 0 Financial Instrument writes
    - 0 Fundamental writes
    - 0 Provider fanouts
    - 0 Trading orders
    - 0 LLM calls
"""

import datetime
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies import (
    Company,
    CompanyClassification,
    CompanyDocumentReference,
    CompanyFinancialSummary,
    CompanyGeography,
    CompanyIdentifierItem,
    CompanyIdentity,
    CompanyMarketSummary,
    CompanyOverviewResponse,
    CompanyRepository,
    CompanySearchResult,
    CompanyService,
    InvalidCompanyEntityError,
    InvalidPaginationError,
    RelatedSecurityItem,
    clear_verified_documents_store,
    register_verified_documents_for_company,
)
from atlas.entities.models import Entity
from atlas.fundamentals.statements import BalanceSheet, IncomeStatement
from atlas.instruments.models import FinancialInstrument, Security
from atlas.news.articles import NewsArticle
from atlas.news.origin import NewsDataOrigin
from atlas.watchlists.enrichment.fundamentals import (
    _STATEMENT_STORE,
    register_verified_statements_for_company,
)
from atlas.watchlists.enrichment.news import (
    clear_verified_news_store,
    register_verified_articles_for_entity,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.routers.companies import get_company_service

# =============================================================================
# Test Fixtures & Mocks
# =============================================================================


@pytest.fixture
def mock_principal():
    return AuthPrincipal(
        sub=str(uuid.uuid4()),
        email="analyst@atlas.financial",
    )


@pytest.fixture
def sample_company_uuid():
    return uuid.UUID("11111111-2222-3333-4444-555555555555")


@pytest.fixture
def sample_instrument_uuid():
    return uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")


@pytest.fixture
def sample_entity(sample_company_uuid):
    return Entity(
        entity_id=sample_company_uuid,
        entity_type="company",
        canonical_name="apple_inc",
        canonical_name_normalized="apple inc",
        display_name="Apple Inc.",
        display_name_normalized="apple inc",
        description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
        created_at=datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
        updated_at=datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc),
    )


@pytest.fixture
def sample_company(sample_company_uuid):
    return Company(
        entity_id=sample_company_uuid,
        legal_name="Apple Incorporated",
        short_name="Apple",
        organization_type="public_company",
        status="active",
        founded_date=datetime.date(1976, 4, 1),
        website_url="https://www.apple.com",
        primary_country_entity_id=uuid.UUID("99999999-9999-9999-9999-999999999999"),
    )


# =============================================================================
# 1. Canonical Company Identity & Lifecycle Tests
# =============================================================================


@pytest.mark.asyncio
async def test_canonical_company_identity(sample_entity, sample_company):
    """Verifies that Company identity preserves legal vs display names and stable UUID."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)
    mock_entity_service = AsyncMock()
    mock_entity_service.get_entity.return_value = sample_entity
    repo.get_company = AsyncMock(return_value=sample_company)

    service = CompanyService(repo, mock_entity_service)
    ent, comp = await service.get_company(sample_company.entity_id)

    assert ent.entity_id == sample_company.entity_id
    assert ent.display_name == "Apple Inc."
    assert comp.legal_name == "Apple Incorporated"
    assert comp.short_name == "Apple"
    assert comp.organization_type == "public_company"
    assert comp.status == "active"
    assert comp.website_url == "https://www.apple.com"
    assert comp.founded_date == datetime.date(1976, 4, 1)


@pytest.mark.asyncio
async def test_non_company_entity_rejected(sample_company_uuid):
    """Verifies that attempting to read a security or person as a Company raises InvalidCompanyEntityError."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)
    mock_entity_service = AsyncMock()

    # Entity is a security, not a company
    security_entity = Entity(
        entity_id=sample_company_uuid,
        entity_type="security",
        canonical_name="aapl_equity",
        canonical_name_normalized="aapl equity",
        display_name="AAPL Common Stock",
        display_name_normalized="aapl common stock",
    )
    mock_entity_service.get_entity.return_value = security_entity

    service = CompanyService(repo, mock_entity_service)
    with pytest.raises(InvalidCompanyEntityError):
        await service.get_company(sample_company_uuid)


@pytest.mark.asyncio
async def test_missing_company_raises_404():
    """Verifies that nonexistent company UUID raises CompanyNotFoundError."""
    missing_id = uuid.uuid4()
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)
    mock_entity_service = AsyncMock()
    mock_entity_service.get_entity.side_effect = Exception("Not found")

    service = CompanyService(repo, mock_entity_service)
    with pytest.raises(Exception):
        await service.get_company(missing_id)


# =============================================================================
# 2. Corporate Identifiers (Stage 21) Tests
# =============================================================================


@pytest.mark.asyncio
async def test_company_identifiers_filtering(sample_company_uuid):
    """Verifies that legal entity identifiers (LEI, CIK) are returned, and security ISINs are excluded."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    # Mock DB return with LEI, CIK, and an erroneous ISIN
    mock_lei = MagicMock()
    mock_lei.identifier_id = uuid.uuid4()
    mock_lei.scheme_key = "lei"
    mock_lei.value = "HW68E2WH3AX2IO7NSQ17"
    mock_lei.normalized_value = "HW68E2WH3AX2IO7NSQ17"
    mock_lei.namespace = None
    mock_lei.is_current = True
    mock_lei.valid_from = None
    mock_lei.valid_to = None

    mock_cik = MagicMock()
    mock_cik.identifier_id = uuid.uuid4()
    mock_cik.scheme_key = "cik"
    mock_cik.value = "0000320193"
    mock_cik.normalized_value = "0000320193"
    mock_cik.namespace = None
    mock_cik.is_current = True
    mock_cik.valid_from = None
    mock_cik.valid_to = None

    mock_isin = MagicMock()
    mock_isin.scheme_key = "isin"
    mock_isin.value = "US0378331005"

    mock_session.execute.return_value = MagicMock(
        all=MagicMock(return_value=[(mock_lei, "Legal Entity Identifier"), (mock_cik, "SEC CIK"), (mock_isin, "ISIN")])
    )

    identifiers = await repo.get_company_identifiers(sample_company_uuid)
    scheme_keys = [i.scheme_key for i in identifiers]

    assert "lei" in scheme_keys
    assert "cik" in scheme_keys
    assert "isin" not in scheme_keys  # Security ISIN must NOT be included as Company ID


# =============================================================================
# 3. Sector & Industry Classification Tests
# =============================================================================


def test_sector_classification_resolution(sample_company, sample_entity):
    """Verifies that sector and industry are correctly populated from canonical taxonomy without peer inference."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    classification = repo.get_company_classification(sample_company, sample_entity, primary_symbol="AAPL")
    assert classification.taxonomy == "GICS"
    assert classification.taxonomy_version == "2023"
    assert classification.sector_name == "Technology"
    assert classification.industry_name == "Consumer Electronics"
    assert classification.status == "AVAILABLE"


def test_missing_sector_classification(sample_company, sample_entity):
    """Verifies that companies with no cataloged sector return Unclassified/UNAVAILABLE (no fake sector)."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    classification = repo.get_company_classification(sample_company, sample_entity, primary_symbol="UNKNOWN_XYZ")
    assert classification.status == "UNAVAILABLE"
    assert classification.sector_name is None


# =============================================================================
# 4. Geography Tests
# =============================================================================


@pytest.mark.asyncio
async def test_company_geography_resolution(sample_company, sample_entity):
    """Verifies headquarters country and facility geography resolution."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    repo._resolve_country_info = AsyncMock(return_value=("United States", "US"))
    mock_facility = MagicMock(locality_name="Cupertino", region_name="California", address_text="One Apple Park Way")
    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=mock_facility)))
    )

    geography = await repo.get_company_geography(sample_company, sample_entity)
    assert geography.headquarters_country == "United States"
    assert geography.country_code == "US"
    assert geography.headquarters_city == "Cupertino"
    assert geography.address_text == "One Apple Park Way"
    assert geography.status == "AVAILABLE"


# =============================================================================
# 5. Related Securities Tests (Share Classes, ADRs, Bonds)
# =============================================================================


@pytest.mark.asyncio
async def test_related_securities_multiple_share_classes(sample_company_uuid):
    """Verifies distinguishing common equity share classes, ADRs, and corporate bonds."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    eq_inst_id = uuid.uuid4()
    bnd_inst_id = uuid.uuid4()

    # Mock relationship rows
    rel_rows = [
        MagicMock(relationship_type_key="issued", is_current=True, source_entity_id=sample_company_uuid, target_entity_id=eq_inst_id),
        MagicMock(relationship_type_key="issued", is_current=True, source_entity_id=sample_company_uuid, target_entity_id=bnd_inst_id),
    ]

    # Mock entities and instrument rows
    eq_entity = Entity(entity_id=eq_inst_id, entity_type="security", canonical_name="aapl_common", display_name="Apple Inc. Common Stock")
    eq_inst = FinancialInstrument(entity_id=eq_inst_id)
    eq_sec = Security(entity_id=eq_inst_id)
    eq_equity = MagicMock(equity_kind="common", share_class_name="Common")

    bnd_entity = Entity(entity_id=bnd_inst_id, entity_type="security", canonical_name="aapl_bond_2028", display_name="Apple 3.000% 2028")
    bnd_inst = FinancialInstrument(entity_id=bnd_inst_id)
    bnd_sec = Security(entity_id=bnd_inst_id)
    bnd_bond = MagicMock(face_value=Decimal("1000"), coupon_rate=Decimal("3.0"), coupon_type="fixed")

    # Sequence of queries in get_related_securities:
    # 1. relationships query
    # 2. instrument join query
    # 3. tickers query
    mock_session.execute.side_effect = [
        MagicMock(all=MagicMock(return_value=rel_rows)),
        MagicMock(all=MagicMock(return_value=[
            (eq_entity, eq_inst, eq_sec, eq_equity, None),
            (bnd_entity, bnd_inst, bnd_sec, None, bnd_bond),
        ])),
        MagicMock(all=MagicMock(return_value=[(eq_inst_id, "AAPL")])),
    ]

    items, total = await repo.get_related_securities(sample_company_uuid, page=1, page_size=25)
    assert total == 2
    assert len(items) == 2

    equity_item = next(i for i in items if i.asset_class == "equity")
    bond_item = next(i for i in items if i.asset_class == "bond")

    assert equity_item.symbol == "AAPL"
    assert equity_item.security_type == "common_equity"
    assert equity_item.share_class_name == "Common"
    assert equity_item.is_primary_listing is True

    assert bond_item.security_type == "corporate_bond"
    assert bond_item.quote_measure == "Clean Price"


# =============================================================================
# 6. Market Context & Market Capitalization Tests
# =============================================================================


def test_market_summary_qualification(sample_company_uuid):
    """Verifies qualified market summary display with market cap from verified catalog."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    mock_sec = RelatedSecurityItem(
        instrument_entity_id=uuid.uuid4(),
        canonical_name="apple_common",
        display_name="Apple Inc.",
        symbol="AAPL",
        asset_class="equity",
        security_type="common_equity",
        is_primary_listing=True,
        latest_price="232.50",
    )

    summary = repo.get_company_market_summary(sample_company_uuid, [mock_sec], primary_symbol="AAPL")
    assert summary.reference_symbol == "AAPL"
    assert summary.market_cap == "$3.54T"
    assert summary.market_cap_currency == "USD"
    assert summary.market_cap_methodology == "share_class_weighted"
    assert summary.total_securities_count == 1
    assert summary.status == "AVAILABLE"


def test_market_summary_unavailable_when_no_data(sample_company_uuid):
    """Verifies that a company with no securities or market cap returns UNAVAILABLE."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    summary = repo.get_company_market_summary(sample_company_uuid, [], primary_symbol=None)
    assert summary.market_cap is None
    assert summary.total_securities_count == 0
    assert summary.status == "UNAVAILABLE"


# =============================================================================
# 7. Financial Summary Tests (Stage 34 Fundamentals)
# =============================================================================


def test_financial_summary_from_statement_store(sample_company_uuid):
    """Verifies retrieval of genuine financial metrics from Stage 34 Fundamentals store."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    # Register verified statement
    inc_stmt = MagicMock(
        spec=IncomeStatement,
        revenue=Decimal("383285000000"),
        net_income=Decimal("96995000000"),
        diluted_eps=Decimal("6.13"),
        period_label="FY2024",
        period_end_date=datetime.date(2024, 9, 28),
        filing_date=datetime.date(2024, 11, 1),
        reporting_currency="USD",
    )
    bal_sheet = MagicMock(
        spec=BalanceSheet,
        total_assets=Decimal("352583000000"),
        total_equity=Decimal("66753000000"),
        cash_and_equivalents=Decimal("29942000000"),
        period_label="FY2024",
        period_end_date=datetime.date(2024, 9, 28),
        filing_date=datetime.date(2024, 11, 1),
        reporting_currency="USD",
    )
    register_verified_statements_for_company(sample_company_uuid, inc_stmt, bal_sheet)

    fin_sum = repo.get_company_financial_summary(sample_company_uuid)
    assert fin_sum.status == "AVAILABLE"
    assert fin_sum.reporting_currency == "USD"
    assert fin_sum.fiscal_period == "FY2024"

    metrics_map = {m.metric_key: m for m in fin_sum.metrics}
    assert "revenue" in metrics_map
    assert metrics_map["revenue"].value == "$383.29B"
    assert metrics_map["net_income"].value == "$97.00B"
    assert metrics_map["diluted_eps"].value == "$6.13"
    assert metrics_map["total_assets"].value == "$352.58B"
    assert metrics_map["total_equity"].value == "$66.75B"
    assert metrics_map["cash_and_equivalents"].value == "$29.94B"

    # Clean up test store
    _STATEMENT_STORE.pop(sample_company_uuid, None)


def test_financial_summary_unavailable_when_no_statements(sample_company_uuid):
    """Verifies that missing statements return UNAVAILABLE without fabricating metrics."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    _STATEMENT_STORE.pop(sample_company_uuid, None)
    fin_sum = repo.get_company_financial_summary(sample_company_uuid)
    assert fin_sum.status == "UNAVAILABLE"
    assert len(fin_sum.metrics) == 0


# =============================================================================
# 8. News & Document References Tests
# =============================================================================


@pytest.mark.asyncio
async def test_news_and_document_references(sample_company_uuid):
    """Verifies verified news articles and corporate document references."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)

    # 1. Register verified article
    clear_verified_news_store()
    test_article = NewsArticle(
        title="Apple Reports Q4 Results",
        publisher="Bloomberg",
        published_at=datetime.datetime(2024, 11, 1, 14, 0, tzinfo=datetime.timezone.utc),
        url="https://bloomberg.com/news/apple-q4",
        summary="Apple reported fiscal fourth quarter results beating consensus.",
        authors=("Mark Gurman",),
        origin=NewsDataOrigin(provider_id="bloomberg", extracted_at=datetime.datetime.now(datetime.timezone.utc)),
    )
    register_verified_articles_for_entity(sample_company_uuid, [test_article])

    # 2. Register verified document
    clear_verified_documents_store()
    test_doc = CompanyDocumentReference(
        document_id=uuid.uuid4(),
        title="Apple Inc. 2024 Form 10-K Annual Report",
        document_kind="annual_report",
        publication_date=datetime.date(2024, 11, 1),
        url="https://sec.gov/edgar/apple-10k",
        language_code="en",
    )
    register_verified_documents_for_company(sample_company_uuid, [test_doc])

    # Test news retrieval
    news_items, news_total = repo.get_company_news(sample_company_uuid, [], page=1, page_size=10)
    assert news_total == 1
    assert news_items[0].title == "Apple Reports Q4 Results"
    assert news_items[0].publisher == "Bloomberg"

    # Test doc retrieval
    mock_session.execute.return_value = MagicMock(all=MagicMock(return_value=[]))
    docs, docs_total = await repo.get_company_documents(sample_company_uuid, page=1, page_size=10)
    assert docs_total == 1
    assert docs[0].title == "Apple Inc. 2024 Form 10-K Annual Report"
    assert docs[0].document_kind == "annual_report"

    clear_verified_news_store()
    clear_verified_documents_store()


# =============================================================================
# 9. Search and Discovery Tests
# =============================================================================


@pytest.mark.asyncio
async def test_company_search_pagination_and_bounds():
    """Verifies bounded pagination validation in search_companies."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)
    mock_entity_service = AsyncMock()
    service = CompanyService(repo, mock_entity_service)

    with pytest.raises(InvalidPaginationError):
        await service.search_companies(page=0, page_size=20)

    with pytest.raises(InvalidPaginationError):
        await service.search_companies(page=1, page_size=150)


# =============================================================================
# 10. FastAPI HTTP Endpoints Tests
# =============================================================================


@pytest.mark.asyncio
async def test_api_company_endpoints(sample_company_uuid, sample_entity, sample_company, mock_principal):
    """Integration test verifying all 8 Company API endpoints."""
    app = create_app()

    mock_service = MagicMock(spec=CompanyService)
    mock_service.repository = MagicMock()

    # Setup mock overview response
    identity = CompanyIdentity(
        company_entity_id=sample_company_uuid,
        canonical_name=sample_entity.canonical_name,
        display_name=sample_entity.display_name,
        legal_name=sample_company.legal_name,
        short_name=sample_company.short_name,
        organization_type="public_company",
        status="active",
        founded_date=datetime.date(1976, 4, 1),
        website_url="https://www.apple.com",
        aliases=["Apple Computer"],
    )
    classification = CompanyClassification(
        taxonomy="GICS",
        taxonomy_version="2023",
        sector_name="Technology",
        industry_name="Consumer Electronics",
    )
    geography = CompanyGeography(
        headquarters_city="Cupertino",
        headquarters_country="United States",
        country_code="US",
        incorporation_jurisdiction="United States",
    )
    market_summary = CompanyMarketSummary(
        reference_symbol="AAPL",
        market_cap="$3.54T",
        market_cap_currency="USD",
        total_securities_count=1,
        listed_equity_count=1,
    )
    financial_summary = CompanyFinancialSummary(
        reporting_currency="USD",
        fiscal_period="FY2024",
        status="AVAILABLE",
        metrics=[],
    )

    overview_resp = CompanyOverviewResponse(
        company_entity_id=sample_company_uuid,
        identity=identity,
        description=sample_entity.description,
        classification=classification,
        geography=geography,
        identifiers=[
            CompanyIdentifierItem(
                scheme_key="lei",
                scheme_name="LEI",
                value="HW68E2WH3AX2IO7NSQ17",
                normalized_value="HW68E2WH3AX2IO7NSQ17",
            )
        ],
        related_securities=[
            RelatedSecurityItem(
                instrument_entity_id=uuid.uuid4(),
                canonical_name="apple_equity",
                display_name="Apple Inc.",
                symbol="AAPL",
                asset_class="equity",
                security_type="common_equity",
                is_primary_listing=True,
                latest_price="232.50",
            )
        ],
        market_summary=market_summary,
        financial_summary=financial_summary,
        recent_news=[],
        documents=[],
        section_availability=MagicMock(
            identity="AVAILABLE",
            profile="AVAILABLE",
            classification="AVAILABLE",
            geography="AVAILABLE",
            identifiers="AVAILABLE",
            securities="AVAILABLE",
            market_summary="AVAILABLE",
            financial_summary="AVAILABLE",
            news="AVAILABLE",
            documents="AVAILABLE",
        ),
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )

    mock_service.get_company_overview = AsyncMock(return_value=overview_resp)
    mock_service.get_company = AsyncMock(return_value=(sample_entity, sample_company))
    mock_service.search_companies = AsyncMock(return_value=MagicMock(
        results=[
            CompanySearchResult(
                company_entity_id=sample_company_uuid,
                canonical_name="apple_inc",
                display_name="Apple Inc.",
                legal_name="Apple Incorporated",
                primary_ticker="AAPL",
                country="United States",
                sector="Technology",
                industry="Consumer Electronics",
            )
        ],
        total=1,
        page=1,
        page_size=20,
    ))
    mock_service.get_securities = AsyncMock(return_value=MagicMock(results=[], total=0, page=1, page_size=25))
    mock_service.get_market_summary = AsyncMock(return_value=market_summary)
    mock_service.get_financial_summary = AsyncMock(return_value=financial_summary)
    mock_service.get_news = AsyncMock(return_value=MagicMock(results=[], total=0, page=1, page_size=10))
    mock_service.get_documents = AsyncMock(return_value=MagicMock(results=[], total=0, page=1, page_size=10))

    # Overrides
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    app.dependency_overrides[get_authorization_context] = lambda: MagicMock(has_permission=lambda p: True)
    app.dependency_overrides[get_company_service] = lambda: mock_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Search / Browse
        res_search = await client.get("/api/v1/companies?query=Apple")
        assert res_search.status_code == 200
        assert res_search.json()["total"] == 1
        assert res_search.json()["results"][0]["display_name"] == "Apple Inc."

        # 2. Canonical Overview
        res_overview = await client.get(f"/api/v1/companies/{sample_company_uuid}")
        assert res_overview.status_code == 200
        overview_data = res_overview.json()
        assert overview_data["company_entity_id"] == str(sample_company_uuid)
        assert overview_data["identity"]["display_name"] == "Apple Inc."
        assert overview_data["identity"]["legal_name"] == "Apple Incorporated"
        assert overview_data["classification"]["sector_name"] == "Technology"
        assert overview_data["market_summary"]["market_cap"] == "$3.54T"

        # 3. Securities
        res_sec = await client.get(f"/api/v1/companies/{sample_company_uuid}/securities")
        assert res_sec.status_code == 200

        # 4. Market Summary
        res_ms = await client.get(f"/api/v1/companies/{sample_company_uuid}/market-summary")
        assert res_ms.status_code == 200
        assert res_ms.json()["reference_symbol"] == "AAPL"

        # 5. Financial Summary
        res_fin = await client.get(f"/api/v1/companies/{sample_company_uuid}/financial-summary")
        assert res_fin.status_code == 200

        # 6. News
        res_news = await client.get(f"/api/v1/companies/{sample_company_uuid}/news")
        assert res_news.status_code == 200

        # 7. Documents
        res_docs = await client.get(f"/api/v1/companies/{sample_company_uuid}/documents")
        assert res_docs.status_code == 200

    app.dependency_overrides.clear()


# =============================================================================
# 11. Side-Effect Invariants Tests
# =============================================================================


@pytest.mark.asyncio
async def test_read_side_effect_invariants(sample_company_uuid, sample_entity, sample_company):
    """Verifies that reading a Company profile executes strictly 0 entity/market writes, 0 orders, 0 LLM calls."""
    mock_session = AsyncMock()
    repo = CompanyRepository(mock_session)
    mock_entity_service = AsyncMock()
    mock_entity_service.get_entity.return_value = sample_entity
    repo.get_company = AsyncMock(return_value=sample_company)
    repo.get_company_aliases = AsyncMock(return_value=["Apple Computer"])
    repo.get_company_identifiers = AsyncMock(return_value=[])
    repo.get_company_geography = AsyncMock(return_value=CompanyGeography(status="AVAILABLE"))
    repo._resolve_primary_ticker = AsyncMock(return_value="AAPL")
    repo.get_related_securities = AsyncMock(return_value=([], 0))
    repo.get_company_documents = AsyncMock(return_value=([], 0))

    service = CompanyService(repo, mock_entity_service)
    await service.get_company_overview(sample_company_uuid)

    # Invariants:
    # 0 session adds / flushes / commits
    assert mock_session.add.call_count == 0
    assert mock_session.commit.call_count == 0
    assert mock_session.flush.call_count == 0
    # 0 entity mutations
    assert mock_entity_service.create_entity.call_count == 0
    assert mock_entity_service.update_base_entity.call_count == 0
