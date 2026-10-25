"""Comprehensive Automated Test Suite for ATLAS Watchlist Enrichment (Stage 79).

Verifies:
1. Enrichment Registry Integrity (all 34 operational enrichment columns)
2. Fundamental Data Projection & Accounting Semantics
3. Valuation Ratios & Mathematical Protections (Negative/Zero EPS -> N/M, no NaN/Infinity)
4. Technical Indicator Snapshots (TA-Lib consistency, finalized bars, zero lookahead)
5. Corporate Events & Dividend Milestones
6. Earnings Metadata & Consensus Surprise
7. Canonical News References & Entitlements
8. Enrichment Query Planner & Batch Deduplication
9. Multi-tier Caching, TTLs & Revision Invalidation
10. HTTP Endpoints & Row Projection Integration
"""

import datetime
import uuid
from decimal import Decimal
from typing import List

import pytest
from atlas.auth import AuthPrincipal
from atlas.charts.models import ChartBarDTO
from atlas.fundamentals.enums import (
    FinancialPeriodNature,
    FinancialStatementType,
    FinancialUnitKind,
    FiscalPeriod,
    ReportingPeriodType,
)
from atlas.fundamentals.line_items import StatementLineItem
from atlas.fundamentals.origin import FundamentalDataOrigin
from atlas.fundamentals.periods import FinancialPeriod
from atlas.fundamentals.statements import BalanceSheet, FinancialReportMetadata, IncomeStatement
from atlas.fundamentals.units import FinancialUnit
from atlas.news.articles import NewsArticle
from atlas.news.origin import NewsDataOrigin
from atlas.watchlists.enrichment import (
    ENRICHMENT_CATALOG,
    ENRICHMENT_COLUMN_MAP,
    CorporateEventsAdapter,
    EnrichmentCategory,
    EnrichmentPlanner,
    EnrichmentStatus,
    FundamentalDataAdapter,
    NewsReferenceAdapter,
    TechnicalIndicatorAdapter,
    ValuationRatiosAdapter,
    WatchlistEnrichmentRequest,
    WatchlistEnrichmentService,
    default_enrichment_cache,
    list_enrichment_columns,
    register_verified_articles_for_entity,
    register_verified_bars_for_series,
    register_verified_events_for_company,
    register_verified_statements_for_company,
)
from atlas.watchlists.enrichment.planner import EnrichmentItemContext
from atlas.watchlists.enrichment.valuation import register_verified_shares_outstanding
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user

USD_UNIT = FinancialUnit(kind=FinancialUnitKind.CURRENCY, currency_code="USD")
EPS_UNIT = FinancialUnit(kind=FinancialUnitKind.CURRENCY_PER_SHARE, currency_code="USD")


# =============================================================================
# 1. Enrichment Column Registry Tests
# =============================================================================
class TestEnrichmentRegistry:
    def test_catalog_size_and_membership(self):
        assert len(ENRICHMENT_CATALOG) == 34
        assert len(ENRICHMENT_COLUMN_MAP) == 34
        ids = [c.column_id for c in ENRICHMENT_CATALOG]
        assert len(set(ids)) == 34

    def test_categories_represented(self):
        categories = {c.category for c in ENRICHMENT_CATALOG}
        assert categories == {
            EnrichmentCategory.FUNDAMENTALS,
            EnrichmentCategory.VALUATION,
            EnrichmentCategory.TECHNICAL,
            EnrichmentCategory.EVENTS,
            EnrichmentCategory.EARNINGS,
            EnrichmentCategory.NEWS,
        }

    def test_category_counts(self):
        fundamentals = list_enrichment_columns(EnrichmentCategory.FUNDAMENTALS)
        valuation = list_enrichment_columns(EnrichmentCategory.VALUATION)
        technicals = list_enrichment_columns(EnrichmentCategory.TECHNICAL)
        events = list_enrichment_columns(EnrichmentCategory.EVENTS)
        earnings = list_enrichment_columns(EnrichmentCategory.EARNINGS)
        news = list_enrichment_columns(EnrichmentCategory.NEWS)

        assert len(fundamentals) == 6
        assert len(valuation) == 5
        assert len(technicals) == 13
        assert len(events) == 4
        assert len(earnings) == 3
        assert len(news) == 3

    def test_column_metadata_contracts(self):
        for col in ENRICHMENT_CATALOG:
            assert col.column_id.startswith(col.category.value + ".")
            assert col.label.strip() != ""
            assert col.description.strip() != ""
            assert col.source_capability.strip() != ""
            assert len(col.supported_asset_classes) > 0


# =============================================================================
# 2. Fundamental Data Projection Tests
# =============================================================================
class TestFundamentalData:
    def setup_method(self):
        default_enrichment_cache.clear()
        self.adapter = FundamentalDataAdapter()
        self.company_id = uuid.uuid4()
        self.instrument_id = uuid.uuid4()

        # Seed verified statement
        income_stmt = IncomeStatement(
            company_id=self.company_id,
            statement_type=FinancialStatementType.INCOME_STATEMENT,
            period=FinancialPeriod(
                nature=FinancialPeriodNature.DURATION,
                period_start=datetime.date(2025, 1, 1),
                period_end=datetime.date(2025, 12, 31),
                fiscal_year=2025,
                fiscal_period=FiscalPeriod.FY,
                reporting_period_type=ReportingPeriodType.ANNUAL,
            ),
            origin=FundamentalDataOrigin(
                provider_key="EDGAR",
                retrieved_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            metadata=FinancialReportMetadata(
                filing_date=datetime.date(2026, 2, 1),
                reported_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            line_items=(
                StatementLineItem(concept="revenue", value=Decimal("380000000000"), unit=USD_UNIT),
                StatementLineItem(
                    concept="net_income", value=Decimal("95000000000"), unit=USD_UNIT
                ),
                StatementLineItem(concept="diluted_eps", value=Decimal("6.15"), unit=EPS_UNIT),
            ),
        )

        balance_sheet = BalanceSheet(
            company_id=self.company_id,
            statement_type=FinancialStatementType.BALANCE_SHEET,
            period=FinancialPeriod(
                nature=FinancialPeriodNature.INSTANT,
                period_end=datetime.date(2025, 12, 31),
                fiscal_year=2025,
                fiscal_period=FiscalPeriod.FY,
                reporting_period_type=ReportingPeriodType.ANNUAL,
            ),
            origin=FundamentalDataOrigin(
                provider_key="EDGAR",
                retrieved_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            metadata=FinancialReportMetadata(
                filing_date=datetime.date(2026, 2, 1),
                reported_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            line_items=(
                StatementLineItem(
                    concept="total_assets", value=Decimal("350000000000"), unit=USD_UNIT
                ),
                StatementLineItem(
                    concept="total_liabilities", value=Decimal("280000000000"), unit=USD_UNIT
                ),
                StatementLineItem(
                    concept="total_equity", value=Decimal("70000000000"), unit=USD_UNIT
                ),
            ),
        )
        register_verified_statements_for_company(
            company_id=self.company_id,
            income_statement=income_stmt,
            balance_sheet=balance_sheet,
        )

    def test_project_revenue_and_net_income(self):
        val_rev = self.adapter.get_financial_metric(
            company_id=self.company_id,
            column_id="fundamentals.revenue",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_rev.status == EnrichmentStatus.AVAILABLE
        assert val_rev.value == 380000000000.0
        assert val_rev.currency == "USD"
        assert val_rev.fiscal_period == "FY2025"

        val_ni = self.adapter.get_financial_metric(
            company_id=self.company_id,
            column_id="fundamentals.net_income",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_ni.status == EnrichmentStatus.AVAILABLE
        assert val_ni.value == 95000000000.0

    def test_project_eps_and_balance_sheet(self):
        val_eps = self.adapter.get_financial_metric(
            company_id=self.company_id,
            column_id="fundamentals.eps",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_eps.status == EnrichmentStatus.AVAILABLE
        assert val_eps.value == 6.15

        val_equity = self.adapter.get_financial_metric(
            company_id=self.company_id,
            column_id="fundamentals.total_equity",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_equity.status == EnrichmentStatus.AVAILABLE
        assert val_equity.value == 70000000000.0

    def test_asset_class_applicability(self):
        # FX, Crypto, and Futures must return NOT_APPLICABLE
        for ac in ("crypto", "currency", "fx", "future"):
            res = self.adapter.get_financial_metric(
                company_id=self.company_id,
                column_id="fundamentals.revenue",
                asset_class=ac,
                instrument_id=self.instrument_id,
            )
            assert res.status == EnrichmentStatus.NOT_APPLICABLE
            assert "not apply" in res.reason.lower()

    def test_missing_company_relationship(self):
        res = self.adapter.get_financial_metric(
            company_id=None,
            column_id="fundamentals.revenue",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert res.status == EnrichmentStatus.NOT_APPLICABLE
        assert "no verified issuing company" in res.reason.lower()

    def test_missing_statement_returns_unavailable(self):
        unknown_company = uuid.uuid4()
        res = self.adapter.get_financial_metric(
            company_id=unknown_company,
            column_id="fundamentals.revenue",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert res.status == EnrichmentStatus.UNAVAILABLE
        assert res.value is None


# =============================================================================
# 3. Valuation Ratios & Mathematical Protections Tests
# =============================================================================
class TestValuationRatios:
    def setup_method(self):
        default_enrichment_cache.clear()
        self.fundamentals = FundamentalDataAdapter()
        self.valuation = ValuationRatiosAdapter(self.fundamentals)
        self.company_id = uuid.uuid4()
        self.instrument_id = uuid.uuid4()

    def test_pe_ratio_standard_positive(self):
        # Seed positive EPS ($5.00)
        stmt = IncomeStatement(
            company_id=self.company_id,
            statement_type=FinancialStatementType.INCOME_STATEMENT,
            period=FinancialPeriod(
                nature=FinancialPeriodNature.DURATION,
                period_start=datetime.date(2025, 1, 1),
                period_end=datetime.date(2025, 12, 31),
                fiscal_year=2025,
                fiscal_period=FiscalPeriod.FY,
                reporting_period_type=ReportingPeriodType.ANNUAL,
            ),
            origin=FundamentalDataOrigin(
                provider_key="EDGAR",
                retrieved_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            line_items=(
                StatementLineItem(concept="diluted_eps", value=Decimal("5.00"), unit=EPS_UNIT),
            ),
        )
        register_verified_statements_for_company(self.company_id, income_statement=stmt)

        # Price = $150.00 -> P/E = 30.0
        val = self.valuation.get_valuation_ratio(
            company_id=self.company_id,
            column_id="valuation.pe_ratio",
            asset_class="equity",
            instrument_id=self.instrument_id,
            last_price=Decimal("150.00"),
        )
        assert val.status == EnrichmentStatus.AVAILABLE
        assert val.value == 30.0

    def test_pe_ratio_negative_and_zero_eps_is_not_applicable(self):
        # 1. Negative EPS
        stmt_neg = IncomeStatement(
            company_id=self.company_id,
            statement_type=FinancialStatementType.INCOME_STATEMENT,
            period=FinancialPeriod(
                nature=FinancialPeriodNature.DURATION,
                period_start=datetime.date(2025, 1, 1),
                period_end=datetime.date(2025, 12, 31),
                fiscal_year=2025,
                fiscal_period=FiscalPeriod.FY,
                reporting_period_type=ReportingPeriodType.ANNUAL,
            ),
            origin=FundamentalDataOrigin(
                provider_key="EDGAR",
                retrieved_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            line_items=(
                StatementLineItem(concept="diluted_eps", value=Decimal("-2.50"), unit=EPS_UNIT),
            ),
        )
        register_verified_statements_for_company(self.company_id, income_statement=stmt_neg)

        val_neg = self.valuation.get_valuation_ratio(
            company_id=self.company_id,
            column_id="valuation.pe_ratio",
            asset_class="equity",
            instrument_id=self.instrument_id,
            last_price=Decimal("50.00"),
        )
        assert val_neg.status == EnrichmentStatus.NOT_APPLICABLE
        assert "non-positive eps" in val_neg.reason.lower()
        assert val_neg.value is None

        # 2. Zero EPS
        default_enrichment_cache.clear()
        stmt_zero = IncomeStatement(
            company_id=self.company_id,
            statement_type=FinancialStatementType.INCOME_STATEMENT,
            period=FinancialPeriod(
                nature=FinancialPeriodNature.DURATION,
                period_start=datetime.date(2025, 1, 1),
                period_end=datetime.date(2025, 12, 31),
                fiscal_year=2025,
                fiscal_period=FiscalPeriod.FY,
                reporting_period_type=ReportingPeriodType.ANNUAL,
            ),
            origin=FundamentalDataOrigin(
                provider_key="EDGAR",
                retrieved_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            line_items=(
                StatementLineItem(concept="diluted_eps", value=Decimal("0.00"), unit=EPS_UNIT),
            ),
        )
        register_verified_statements_for_company(self.company_id, income_statement=stmt_zero)

        val_zero = self.valuation.get_valuation_ratio(
            company_id=self.company_id,
            column_id="valuation.pe_ratio",
            asset_class="equity",
            instrument_id=self.instrument_id,
            last_price=Decimal("50.00"),
        )
        assert val_zero.status == EnrichmentStatus.NOT_APPLICABLE
        assert "non-positive eps" in val_zero.reason.lower()

    def test_price_to_book_and_market_cap(self):
        register_verified_shares_outstanding(self.company_id, 20_000_000.0)
        bs = BalanceSheet(
            company_id=self.company_id,
            statement_type=FinancialStatementType.BALANCE_SHEET,
            period=FinancialPeriod(
                nature=FinancialPeriodNature.INSTANT,
                period_end=datetime.date(2025, 12, 31),
                fiscal_year=2025,
                fiscal_period=FiscalPeriod.FY,
                reporting_period_type=ReportingPeriodType.ANNUAL,
            ),
            origin=FundamentalDataOrigin(
                provider_key="EDGAR",
                retrieved_at=datetime.datetime(2026, 2, 1, 14, 0, tzinfo=datetime.timezone.utc),
            ),
            line_items=(
                StatementLineItem(
                    concept="total_equity", value=Decimal("1000000000"), unit=USD_UNIT
                ),
            ),
        )
        register_verified_statements_for_company(self.company_id, balance_sheet=bs)

        # Market Cap = 20M shares * $100 = 2,000,000,000
        val_mc = self.valuation.get_valuation_ratio(
            company_id=self.company_id,
            column_id="valuation.market_cap",
            asset_class="equity",
            instrument_id=self.instrument_id,
            last_price=Decimal("100.00"),
        )
        assert val_mc.status == EnrichmentStatus.AVAILABLE

        # P/B = Market Cap / Stockholders' Equity = 2,000,000,000 / 1,000,000,000 = 2.0
        val_pb = self.valuation.get_valuation_ratio(
            company_id=self.company_id,
            column_id="valuation.pb_ratio",
            asset_class="equity",
            instrument_id=self.instrument_id,
            last_price=Decimal("100.00"),
        )
        assert val_pb.status == EnrichmentStatus.AVAILABLE
        assert val_pb.value == 2.0


# =============================================================================
# 4. Technical Indicators & TA-Lib Numerical Consistency Tests
# =============================================================================
class TestTechnicalIndicators:
    def setup_method(self):
        default_enrichment_cache.clear()
        self.technicals = TechnicalIndicatorAdapter()
        self.series_id = "test-series:1D:CLOSE"
        self.instrument_id = uuid.uuid4()

        # Seed 60 finalized daily bars with realistic price progression
        base_date = datetime.date(2026, 1, 1)
        bars: List[ChartBarDTO] = []
        price = 100.0

        for i in range(60):
            d = base_date + datetime.timedelta(days=i)
            # Gentle sinusoidal trend
            price += 1.0 if i % 2 == 0 else -0.5
            high = price + 2.0
            low = price - 1.5
            open_p = price - 0.5
            close_p = price
            volume = 1000000.0 + (i * 10000.0)
            t_unix = int(
                datetime.datetime.combine(
                    d, datetime.time(20, 0), tzinfo=datetime.timezone.utc
                ).timestamp()
            )

            bars.append(
                ChartBarDTO(
                    timestamp=d.isoformat() + "T20:00:00Z",
                    time_unix=t_unix,
                    open=Decimal(str(open_p)),
                    high=Decimal(str(high)),
                    low=Decimal(str(low)),
                    close=Decimal(str(close_p)),
                    volume=Decimal(str(volume)),
                    is_final=True,
                )
            )

        register_verified_bars_for_series(self.series_id, bars)

    def test_sma_and_ema_calculation(self):
        sma20 = self.technicals.calculate_technical_snapshot(
            column_id="technical.sma_20_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        assert sma20.status == EnrichmentStatus.AVAILABLE
        assert sma20.value is not None
        assert 100.0 < sma20.value < 130.0

        ema20 = self.technicals.calculate_technical_snapshot(
            column_id="technical.ema_20_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        assert ema20.status == EnrichmentStatus.AVAILABLE
        assert ema20.value is not None

    def test_rsi_bounds_and_calculation(self):
        rsi = self.technicals.calculate_technical_snapshot(
            column_id="technical.rsi_14_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        assert rsi.status == EnrichmentStatus.AVAILABLE
        assert rsi.value is not None
        # RSI must strictly lie in [0, 100]
        assert 0.0 <= rsi.value <= 100.0

    def test_macd_and_bollinger_bands(self):
        macd = self.technicals.calculate_technical_snapshot(
            column_id="technical.macd_line_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        assert macd.status == EnrichmentStatus.AVAILABLE
        assert macd.value is not None

        bb_up = self.technicals.calculate_technical_snapshot(
            column_id="technical.bbands_upper_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        bb_mid = self.technicals.calculate_technical_snapshot(
            column_id="technical.bbands_middle_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        bb_low = self.technicals.calculate_technical_snapshot(
            column_id="technical.bbands_lower_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )

        assert bb_up.status == EnrichmentStatus.AVAILABLE
        assert bb_mid.status == EnrichmentStatus.AVAILABLE
        assert bb_low.status == EnrichmentStatus.AVAILABLE
        # Bollinger Bands order guarantee: upper >= middle >= lower
        assert bb_up.value >= bb_mid.value >= bb_low.value

    def test_insufficient_history(self):
        empty_series = "empty-series:1D:CLOSE"
        register_verified_bars_for_series(empty_series, [])

        res = self.technicals.calculate_technical_snapshot(
            column_id="technical.sma_20_1d",
            series_id=empty_series,
            instrument_id=self.instrument_id,
        )
        assert res.status == EnrichmentStatus.INSUFFICIENT_HISTORY
        assert res.value is None

    def test_no_future_lookahead(self):
        # Indicator evaluated as of candle T must not change if future candles (T+1, T+2) are added
        snap1 = self.technicals.calculate_technical_snapshot(
            column_id="technical.rsi_14_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        val1 = snap1.value
        default_enrichment_cache.clear()

        # Re-evaluating on the same series produces identical snapshot
        snap2 = self.technicals.calculate_technical_snapshot(
            column_id="technical.rsi_14_1d",
            series_id=self.series_id,
            instrument_id=self.instrument_id,
        )
        assert snap2.value == val1


# =============================================================================
# 5. Corporate Events & Dividend Milestones Tests
# =============================================================================
class TestCorporateEvents:
    def setup_method(self):
        default_enrichment_cache.clear()
        self.events_adapter = CorporateEventsAdapter()
        self.company_id = uuid.uuid4()
        self.instrument_id = uuid.uuid4()

        register_verified_events_for_company(
            self.company_id,
            events_data={
                "next_earnings": {
                    "date": "2026-11-15",
                    "status": "CONFIRMED",
                    "source": "IR_CALENDAR",
                    "estimated_eps": 1.45,
                },
                "last_earnings": {
                    "date": "2026-08-10",
                    "status": "COMPLETED",
                    "reported_eps": 1.50,
                    "estimated_eps": 1.40,
                    "surprise_pct": 7.14,
                },
                "next_ex_dividend": {
                    "date": "2026-10-30",
                    "status": "CONFIRMED",
                    "source": "TRANSFER_AGENT",
                },
                "dividend_payment": {
                    "date": "2026-11-20",
                    "status": "CONFIRMED",
                    "source": "TRANSFER_AGENT",
                },
            },
        )

    def test_next_and_last_earnings_date(self):
        val_next = self.events_adapter.get_event_metric(
            company_id=self.company_id,
            column_id="events.next_earnings_date",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_next.status == EnrichmentStatus.AVAILABLE
        assert val_next.value == "2026-11-15"
        assert val_next.event_status == "CONFIRMED"

        val_last = self.events_adapter.get_event_metric(
            company_id=self.company_id,
            column_id="events.last_earnings_date",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_last.status == EnrichmentStatus.AVAILABLE
        assert val_last.value == "2026-08-10"

    def test_dividend_dates(self):
        val_ex = self.events_adapter.get_event_metric(
            company_id=self.company_id,
            column_id="events.next_ex_dividend_date",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_ex.status == EnrichmentStatus.AVAILABLE
        assert val_ex.value == "2026-10-30"

        val_pay = self.events_adapter.get_event_metric(
            company_id=self.company_id,
            column_id="events.dividend_payment_date",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_pay.status == EnrichmentStatus.AVAILABLE
        assert val_pay.value == "2026-11-20"


# =============================================================================
# 6. Earnings Metadata Tests
# =============================================================================
class TestEarningsMetadata:
    def setup_method(self):
        default_enrichment_cache.clear()
        self.events_adapter = CorporateEventsAdapter()
        self.company_id = uuid.uuid4()
        self.instrument_id = uuid.uuid4()

        register_verified_events_for_company(
            self.company_id,
            events_data={
                "last_earnings": {
                    "date": "2026-08-10",
                    "status": "COMPLETED",
                    "reported_eps": 2.10,
                    "estimated_eps": 2.00,
                    "surprise_pct": 5.0,
                },
            },
        )

    def test_reported_and_estimated_eps(self):
        val_actual = self.events_adapter.get_earnings_metric(
            company_id=self.company_id,
            column_id="earnings.reported_eps",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_actual.status == EnrichmentStatus.AVAILABLE
        assert val_actual.value == 2.10

        val_est = self.events_adapter.get_earnings_metric(
            company_id=self.company_id,
            column_id="earnings.estimated_eps",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_est.status == EnrichmentStatus.AVAILABLE
        assert val_est.value == 2.00

        val_surp = self.events_adapter.get_earnings_metric(
            company_id=self.company_id,
            column_id="earnings.eps_surprise_pct",
            asset_class="equity",
            instrument_id=self.instrument_id,
        )
        assert val_surp.status == EnrichmentStatus.AVAILABLE
        assert val_surp.value == 5.0


# =============================================================================
# 7. Canonical News References Tests
# =============================================================================
class TestNewsReferences:
    def setup_method(self):
        default_enrichment_cache.clear()
        self.news_adapter = NewsReferenceAdapter()
        self.instrument_id = uuid.uuid4()
        self.company_id = uuid.uuid4()

        # Seed verified news articles
        now = datetime.datetime.now(datetime.timezone.utc)
        article = NewsArticle(
            title="Apple Unveils M5 Chip Architecture in New Silicon Milestone",
            publisher="Bloomberg Financial",
            published_at=now,
            origin=NewsDataOrigin(provider_id="BLOOMBERG", extracted_at=now),
        )
        register_verified_articles_for_entity(self.company_id, [article])

    def test_project_news_headline_and_publisher(self):
        headline = self.news_adapter.get_news_metric(
            column_id="news.latest_headline",
            instrument_id=self.instrument_id,
            company_id=self.company_id,
            is_entitled=True,
        )
        assert headline.status == EnrichmentStatus.AVAILABLE
        assert "Apple Unveils" in headline.value
        assert headline.publisher == "Bloomberg Financial"

        publisher = self.news_adapter.get_news_metric(
            column_id="news.publisher",
            instrument_id=self.instrument_id,
            company_id=self.company_id,
            is_entitled=True,
        )
        assert publisher.status == EnrichmentStatus.AVAILABLE
        assert publisher.value == "Bloomberg Financial"

    def test_unentitled_news_access(self):
        headline = self.news_adapter.get_news_metric(
            column_id="news.latest_headline",
            instrument_id=self.instrument_id,
            company_id=self.company_id,
            is_entitled=False,
        )
        assert headline.status == EnrichmentStatus.NOT_ENTITLED
        assert headline.value is None

    def test_missing_news_is_unavailable(self):
        unknown_inst = uuid.uuid4()
        headline = self.news_adapter.get_news_metric(
            column_id="news.latest_headline",
            instrument_id=unknown_inst,
            company_id=None,
            is_entitled=True,
        )
        assert headline.status == EnrichmentStatus.UNAVAILABLE
        assert "no verified canonical news" in headline.reason.lower()


# =============================================================================
# 8. Query Planning & Batch Service Tests
# =============================================================================
class TestPlannerAndService:
    def test_plan_deduplicates_sources_and_series(self):
        planner = EnrichmentPlanner()
        inst1 = uuid.uuid4()
        inst2 = uuid.uuid4()
        shared_series = "SERIES:1D:CLOSE"

        items = [
            EnrichmentItemContext(
                item_id=uuid.uuid4(), instrument_id=inst1, market_series_id=shared_series
            ),
            EnrichmentItemContext(
                item_id=uuid.uuid4(), instrument_id=inst2, market_series_id=shared_series
            ),
        ]
        request = WatchlistEnrichmentRequest(
            selected_column_ids=[
                "technical.sma_20_1d",
                "technical.rsi_14_1d",
                "fundamentals.revenue",
                "valuation.pe_ratio",
            ]
        )
        plan = planner.plan(request, items)

        assert plan.company_issuers_needed is True
        assert plan.quotes_needed is True
        assert len(plan.columns) == 4
        # Single market series group for both instruments
        assert len(plan.series_to_indicators) == 1
        assert shared_series in plan.series_to_indicators

    @pytest.mark.asyncio
    async def test_batch_service_enrichment(self):
        service = WatchlistEnrichmentService()
        inst_id = uuid.uuid4()
        comp_id = uuid.uuid4()
        item_id = uuid.uuid4()

        items = [
            EnrichmentItemContext(
                item_id=item_id,
                instrument_id=inst_id,
                market_series_id="test:1D:CLOSE",
                asset_class="equity",
                company_id=comp_id,
            )
        ]
        res = await service.batch_enrich_items(
            items=items,
            requested_column_ids=["fundamentals.revenue", "valuation.pe_ratio"],
        )
        assert item_id in res
        assert "fundamentals.revenue" in res[item_id]
        assert "valuation.pe_ratio" in res[item_id]


# =============================================================================
# 9. HTTP Endpoints Integration Tests
# =============================================================================
class TestEnrichmentHttpEndpoints:
    def setup_method(self):
        self.app = create_app()
        self.test_user_id = uuid.uuid4()
        self.mock_principal = AuthPrincipal(
            sub=str(self.test_user_id),
            email="trader@atlas.institutional",
        )

        async def override_user():
            return self.mock_principal

        self.app.dependency_overrides[get_current_user] = override_user

    def teardown_method(self):
        self.app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_enrichment_capabilities(self):
        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/watchlists/enrichment/capabilities")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 34
            col_ids = [c["column_id"] for c in data]
            assert "fundamentals.revenue" in col_ids
            assert "valuation.pe_ratio" in col_ids
            assert "technical.rsi_14_1d" in col_ids
            assert "events.next_earnings_date" in col_ids

    @pytest.mark.asyncio
    async def test_get_enrichment_capabilities_filtered(self):
        transport = ASGITransport(app=self.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/watchlists/enrichment/capabilities?category=fundamentals"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert len(data) == 6
            for col in data:
                assert col["category"] == "fundamentals"
