"""Canonical Funds Catalog Configuration for ATLAS ETFs & Funds Markets V1 (Stage 58)."""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CanonicalFundConfig(BaseModel):
    """Configuration record for a canonical fund or ETF covered in ATLAS."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority (Stage 17)."
    )
    fund_name: str = Field(..., min_length=1, max_length=256)
    display_symbol: str = Field(..., min_length=1, max_length=64)
    fund_type: str = Field(
        ...,
        description="ETF, OPEN_END_MUTUAL_FUND, CLOSED_END_FUND, or OTHER_SUPPORTED_FUND",
    )
    is_exchange_traded: bool = Field(
        default=True,
        description="True for listed ETFs and CEFs; False for traditional mutual funds.",
    )

    # Listing context (None for unlisted open-end mutual funds)
    exchange_id: Optional[UUID] = Field(default=None)
    exchange_mic: Optional[str] = Field(default=None, max_length=16)
    exchange_display_name: Optional[str] = Field(default=None, max_length=128)
    listing_market_country: Optional[str] = Field(default=None, max_length=128)
    listing_market_country_code: Optional[str] = Field(default=None, max_length=8)
    trading_currency: Optional[str] = Field(default="USD", max_length=16)
    listing_status: Optional[str] = Field(default="ACTIVE")

    # Fund Product & Share Class Metadata
    domicile: Optional[str] = Field(default="United States", max_length=64)
    inception_date: Optional[date] = Field(default=None)
    investment_category: Optional[str] = Field(default="Equity", max_length=128)
    distribution_policy: Optional[str] = Field(default="Distributing", max_length=64)
    base_currency: str = Field(default="USD", min_length=3, max_length=16)
    share_class_currency: str = Field(default="USD", min_length=3, max_length=16)

    # Benchmark & Manager Relationships
    benchmark_entity_id: Optional[UUID] = Field(default=None)
    benchmark_name: Optional[str] = Field(default=None, max_length=256)
    manager_entity_id: Optional[UUID] = Field(default=None)
    manager_name: Optional[str] = Field(default=None, max_length=256)
    sponsor_name: Optional[str] = Field(default=None, max_length=256)
    fund_objective: Optional[str] = Field(default=None)

    # Fee Metrics (Net/Gross Expense Ratio)
    net_expense_ratio: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    gross_expense_ratio: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fee_metric_type: Optional[str] = Field(default="Net Expense Ratio")
    fee_effective_date: Optional[date] = Field(default=None)

    # Assets Under Management (AUM)
    total_aum: Optional[float] = Field(default=None, ge=0.0)
    aum_currency: Optional[str] = Field(default="USD")
    aum_as_of_date: Optional[date] = Field(default=None)
    aum_scope: Optional[str] = Field(default="Fund Total")

    # Official Net Asset Value (NAV)
    initial_nav: Optional[float] = Field(default=None, gt=0.0)
    nav_currency: Optional[str] = Field(default="USD")
    nav_valuation_date: Optional[date] = Field(default=None)
    nav_published_at: Optional[datetime] = Field(default=None)
    nav_valuation_method: Optional[str] = Field(default="OFFICIAL_CLOSE_NAV")

    # Identifiers (ISIN, FIGI, CUSIP)
    isin: Optional[str] = Field(default=None, max_length=32)
    figi: Optional[str] = Field(default=None, max_length=32)

    provider_hint: Optional[str] = Field(default="openbb")
    enabled: bool = Field(default=True)

    @field_validator("fund_name", "display_symbol")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace.")
        return cleaned


# Canonical Namespaced UUID for ATLAS Funds & Share Classes
ATLAS_FUNDS_NAMESPACE = UUID("b1b2b3b4-c1c2-d1d2-e1e2-f1f2f3f4f5f6")

SUPPORTED_FUND_TYPES = {
    "ETF": "Exchange-Traded Fund",
    "OPEN_END_MUTUAL_FUND": "Open-End Mutual Fund",
    "CLOSED_END_FUND": "Closed-End Fund",
    "OTHER_SUPPORTED_FUND": "Other Investment Fund",
}

SUPPORTED_INVESTMENT_CATEGORIES = {
    "Equity": "Equity",
    "Fixed Income": "Fixed Income",
    "Multi-Asset": "Multi-Asset / Balanced",
    "Commodity": "Commodity-Linked",
    "Real Estate": "Real Estate",
}


def validate_funds_catalog(configs: List[CanonicalFundConfig]) -> List[CanonicalFundConfig]:
    """Validates uniqueness of canonical instrument UUIDs and symbols within exchange scope."""
    seen_ids = set()
    seen_listings = set()

    for c in configs:
        if c.instrument_entity_id in seen_ids:
            raise ValueError(
                "Duplicate canonical instrument_entity_id in funds catalog: "
                f"{c.instrument_entity_id}"
            )
        seen_ids.add(c.instrument_entity_id)

        if c.is_exchange_traded:
            listing_key = (c.exchange_mic, c.display_symbol.upper())
            if listing_key in seen_listings:
                raise ValueError(f"Duplicate exchange listing in funds catalog: {listing_key}")
            seen_listings.add(listing_key)

    return configs


# -----------------------------------------------------------------------------
# Canonical Covered Funds Catalog (Stage 58 Baseline Universe)
# Covers ETFs, Mutual Funds, and Closed-End Funds with strict identity,
# exchange-awareness, separate NAV and Quotes, fees, AUM, and benchmarks.
# -----------------------------------------------------------------------------
DEFAULT_FUNDS_CATALOG: List[CanonicalFundConfig] = [
    # -------------------------------------------------------------------------
    # 1. SPY: SPDR S&P 500 ETF Trust (Flagship US Equity ETF)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:spy"),
        fund_name="SPDR S&P 500 ETF Trust",
        display_symbol="SPY",
        fund_type="ETF",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:arcx"),
        exchange_mic="ARCX",
        exchange_display_name="NYSE Arca",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(1993, 1, 22),
        investment_category="Equity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:sp500"),
        benchmark_name="S&P 500 Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:ssga"),
        manager_name="State Street Global Advisors",
        sponsor_name="State Street Global Advisors",
        fund_objective=(
            "The SPDR S&P 500 ETF Trust seeks to provide investment results "
            "that correspond generally to the price and yield performance of the S&P 500 Index."
        ),
        net_expense_ratio=0.000945,  # 0.0945%
        gross_expense_ratio=0.000945,
        fee_metric_type="Gross Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=550000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=585.40,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US78462F1030",
        figi="BBG000BDTBL9",
    ),
    # -------------------------------------------------------------------------
    # 2. QQQ: Invesco QQQ Trust (NASDAQ 100 Tech/Large-Cap Growth ETF)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:qqq"),
        fund_name="Invesco QQQ Trust",
        display_symbol="QQQ",
        fund_type="ETF",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(1999, 3, 10),
        investment_category="Equity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:ndx"),
        benchmark_name="NASDAQ-100 Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:invesco"),
        manager_name="Invesco Capital Management LLC",
        sponsor_name="Invesco Ltd.",
        fund_objective=(
            "Invesco QQQ is an exchange-traded fund based on the Nasdaq-100 Index. "
            "The Fund will invest at least 90% of its total assets in securities in the Index."
        ),
        net_expense_ratio=0.0020,  # 0.20%
        gross_expense_ratio=0.0020,
        fee_metric_type="Net Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=290000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=492.20,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US46090E1038",
        figi="BBG000BDY5D0",
    ),
    # -------------------------------------------------------------------------
    # 3. VOO: Vanguard S&P 500 ETF (Low Cost US Broad Market ETF)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:voo"),
        fund_name="Vanguard S&P 500 ETF",
        display_symbol="VOO",
        fund_type="ETF",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:arcx"),
        exchange_mic="ARCX",
        exchange_display_name="NYSE Arca",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(2010, 9, 7),
        investment_category="Equity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:sp500"),
        benchmark_name="S&P 500 Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:vanguard"),
        manager_name="The Vanguard Group, Inc.",
        sponsor_name="The Vanguard Group, Inc.",
        fund_objective=(
            "The fund employs an indexing investment approach designed to track "
            "the performance of the Standard & Poor's 500 Index."
        ),
        net_expense_ratio=0.0003,  # 0.03%
        gross_expense_ratio=0.0003,
        fee_metric_type="Net Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=480000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Share Class",
        initial_nav=536.85,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US9229083632",
        figi="BBG000BHTMY2",
    ),
    # -------------------------------------------------------------------------
    # 4. AGG: iShares Core U.S. Aggregate Bond ETF (Fixed Income ETF)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:agg"),
        fund_name="iShares Core U.S. Aggregate Bond ETF",
        display_symbol="AGG",
        fund_type="ETF",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:arcx"),
        exchange_mic="ARCX",
        exchange_display_name="NYSE Arca",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(2003, 9, 22),
        investment_category="Fixed Income",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:usagg"),
        benchmark_name="Bloomberg U.S. Aggregate Bond Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:blackrock"),
        manager_name="BlackRock Fund Advisors",
        sponsor_name="BlackRock, Inc.",
        fund_objective=(
            "The iShares Core U.S. Aggregate Bond ETF seeks to track the investment results "
            "of an index composed of the total U.S. investment-grade bond market."
        ),
        net_expense_ratio=0.0003,  # 0.03%
        gross_expense_ratio=0.0003,
        fee_metric_type="Net Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=115000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=98.50,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US4642872270",
        figi="BBG000BCK8J6",
    ),
    # -------------------------------------------------------------------------
    # 5. GLD: SPDR Gold Shares (Commodity-backed ETF)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:gld"),
        fund_name="SPDR Gold Shares",
        display_symbol="GLD",
        fund_type="ETF",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:arcx"),
        exchange_mic="ARCX",
        exchange_display_name="NYSE Arca",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(2004, 11, 18),
        investment_category="Commodity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:lbma_gold"),
        benchmark_name="LBMA Gold Price PM",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:ssga"),
        manager_name="World Gold Trust Services, LLC",
        sponsor_name="State Street Global Advisors",
        fund_objective=(
            "The investment objective of the Trust is for the Shares to reflect the performance "
            "of the price of gold bullion, less the Trust's expenses."
        ),
        net_expense_ratio=0.0040,  # 0.40%
        gross_expense_ratio=0.0040,
        fee_metric_type="Gross Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=72000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=245.10,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US78463V1070",
        figi="BBG000BCVP16",
    ),
    # -------------------------------------------------------------------------
    # 6. VTSAX: Vanguard Total Stock Market Index Fund Admiral (Mutual Fund - Unlisted)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:vtsax"),
        fund_name="Vanguard Total Stock Market Index Fund Admiral Shares",
        display_symbol="VTSAX",
        fund_type="OPEN_END_MUTUAL_FUND",
        is_exchange_traded=False,  # Unlisted traditional mutual fund!
        exchange_id=None,
        exchange_mic=None,
        exchange_display_name=None,
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency=None,  # No exchange trading currency
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(2000, 11, 13),
        investment_category="Equity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:crsp_us_total"),
        benchmark_name="CRSP US Total Market Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:vanguard"),
        manager_name="The Vanguard Group, Inc.",
        sponsor_name="The Vanguard Group, Inc.",
        fund_objective=(
            "The fund employs an indexing investment approach designed to track the performance "
            "of the CRSP US Total Market Index, representing ~100% of the investable US market."
        ),
        net_expense_ratio=0.0004,  # 0.04%
        gross_expense_ratio=0.0004,
        fee_metric_type="Net Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=1600000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=138.62,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 22, 30, 0, tzinfo=timezone.utc),
        isin="US9229087286",
        figi="BBG000BC6P98",
    ),
    # -------------------------------------------------------------------------
    # 7. SWPPX: Schwab S&P 500 Index Fund (Mutual Fund - Unlisted)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:swppx"),
        fund_name="Schwab S&P 500 Index Fund",
        display_symbol="SWPPX",
        fund_type="OPEN_END_MUTUAL_FUND",
        is_exchange_traded=False,  # Unlisted traditional mutual fund!
        exchange_id=None,
        exchange_mic=None,
        exchange_display_name=None,
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency=None,
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(1997, 5, 19),
        investment_category="Equity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:sp500"),
        benchmark_name="S&P 500 Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:schwab"),
        manager_name="Charles Schwab Investment Management, Inc.",
        sponsor_name="Charles Schwab & Co., Inc.",
        fund_objective=(
            "The fund's goal is to track the total return of the S&P 500 Index. "
            "It generally invests at least 80% of its net assets in stocks in the index."
        ),
        net_expense_ratio=0.0002,  # 0.02%
        gross_expense_ratio=0.0002,
        fee_metric_type="Net Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=98000000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=86.15,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 22, 15, 0, tzinfo=timezone.utc),
        isin="US8085098551",
        figi="BBG000BF1T44",
    ),
    # -------------------------------------------------------------------------
    # 8. BST: BlackRock Science and Technology Trust (Closed-End Fund on NYSE)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:bst"),
        fund_name="BlackRock Science and Technology Trust",
        display_symbol="BST",
        fund_type="CLOSED_END_FUND",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:xnys"),
        exchange_mic="XNYS",
        exchange_display_name="New York Stock Exchange",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(2014, 10, 29),
        investment_category="Equity",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:msci_world_it"),
        benchmark_name="MSCI World Information Technology Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:blackrock"),
        manager_name="BlackRock Advisors, LLC",
        sponsor_name="BlackRock, Inc.",
        fund_objective=(
            "Perpetual closed-end equity fund that invests in equity securities of science "
            "and technology companies with an options overlay strategy."
        ),
        net_expense_ratio=0.0108,  # 1.08%
        gross_expense_ratio=0.0108,
        fee_metric_type="Total Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=1400000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=37.20,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US09258G1090",
        figi="BBG0077D70M5",
    ),
    # -------------------------------------------------------------------------
    # 9. UTF: Cohen & Steers Infrastructure Fund (Closed-End Fund on NYSE)
    # -------------------------------------------------------------------------
    CanonicalFundConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "fund:utf"),
        fund_name="Cohen & Steers Infrastructure Fund, Inc.",
        display_symbol="UTF",
        fund_type="CLOSED_END_FUND",
        is_exchange_traded=True,
        exchange_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "exchange:xnys"),
        exchange_mic="XNYS",
        exchange_display_name="New York Stock Exchange",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        domicile="United States",
        inception_date=date(2004, 3, 30),
        investment_category="Multi-Asset",
        distribution_policy="Distributing",
        base_currency="USD",
        share_class_currency="USD",
        benchmark_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "benchmark:sp_global_infra"),
        benchmark_name="S&P Global Infrastructure Index",
        manager_entity_id=uuid.uuid5(ATLAS_FUNDS_NAMESPACE, "company:cohen_steers"),
        manager_name="Cohen & Steers Capital Management, Inc.",
        sponsor_name="Cohen & Steers, Inc.",
        fund_objective=(
            "The primary objective is total return, with an emphasis on high current income "
            "through investment in securities of infrastructure companies."
        ),
        net_expense_ratio=0.0132,  # 1.32%
        gross_expense_ratio=0.0132,
        fee_metric_type="Total Expense Ratio",
        fee_effective_date=date(2026, 1, 1),
        total_aum=3100000000.0,
        aum_currency="USD",
        aum_as_of_date=date(2026, 10, 1),
        aum_scope="Fund Total",
        initial_nav=26.40,
        nav_currency="USD",
        nav_valuation_date=date(2026, 10, 14),
        nav_published_at=datetime(2026, 10, 14, 21, 0, 0, tzinfo=timezone.utc),
        isin="US19248A1097",
        figi="BBG000BNW251",
    ),
]
