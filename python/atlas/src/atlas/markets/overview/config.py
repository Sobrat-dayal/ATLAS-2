"""Curated Server-Owned Instrument Configuration for Markets Overview V1 (Stage 56)."""

import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MarketsOverviewInstrumentConfig(BaseModel):
    """Configuration record for an instrument monitored on the Markets Overview."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: uuid.UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    display_name: str = Field(..., min_length=1, max_length=128)
    display_symbol: str = Field(..., min_length=1, max_length=32)
    instrument_category: str = Field(
        ...,
        description=(
            "Canonical category: market_index, equity, etf, "
            "currency, crypto_asset, commodity, bond"
        ),
    )
    market_group: str = Field(
        ...,
        description=(
            "Presentation group: benchmarks, equities, etfs, "
            "fx, crypto, commodities, bonds"
        ),
    )
    venue: Optional[str] = Field(
        default=None, max_length=64, description="Exchange or trading venue."
    )
    value_kind: str = Field(default="price", description="price, points, rate, yield")
    quote_currency: Optional[str] = Field(default=None, max_length=16)
    quote_unit: Optional[str] = Field(default=None, max_length=32)
    display_order: int = Field(ge=0, le=100)
    enabled: bool = Field(default=True)
    featured: bool = Field(
        default=False, description="True for high-visibility featured benchmark/market instruments."
    )
    is_index: bool = Field(
        default=False, description="True for benchmark indices, False for ETFs or securities."
    )
    provider_hint: Optional[str] = Field(default=None)

    @field_validator("display_name", "display_symbol", "market_group")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace.")
        return cleaned


# Canonical Namespaced UUIDs for Curated ATLAS Market Instruments
# Generated deterministically using standard UUID5 namespace for ATLAS instruments
ATLAS_INSTRUMENT_NAMESPACE = uuid.UUID("a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6")

MARKET_GROUPS_ALLOWLIST = {
    "benchmarks",
    "equities",
    "etfs",
    "fx",
    "crypto",
    "commodities",
    "bonds",
}

DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS: List[MarketsOverviewInstrumentConfig] = [
    # ─── 1. BENCHMARKS (Display orders 1-6) ──────────────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:sp500"),
        display_name="S&P 500",
        display_symbol="^GSPC",
        instrument_category="market_index",
        market_group="benchmarks",
        venue="CBOE",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=1,
        enabled=True,
        featured=True,
        is_index=True,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:nasdaq100"),
        display_name="NASDAQ 100",
        display_symbol="^NDX",
        instrument_category="market_index",
        market_group="benchmarks",
        venue="NASDAQ",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=2,
        enabled=True,
        featured=True,
        is_index=True,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:dow_jones"),
        display_name="Dow Jones Industrial",
        display_symbol="^DJI",
        instrument_category="market_index",
        market_group="benchmarks",
        venue="NYSE",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=3,
        enabled=True,
        featured=True,
        is_index=True,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:russell2000"),
        display_name="Russell 2000",
        display_symbol="^RUT",
        instrument_category="market_index",
        market_group="benchmarks",
        venue="FTSE Russell",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=4,
        enabled=True,
        featured=False,
        is_index=True,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:ftse100"),
        display_name="FTSE 100",
        display_symbol="^FTSE",
        instrument_category="market_index",
        market_group="benchmarks",
        venue="LSE",
        value_kind="points",
        quote_currency="GBP",
        quote_unit="pts",
        display_order=5,
        enabled=True,
        featured=False,
        is_index=True,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:nikkei225"),
        display_name="Nikkei 225",
        display_symbol="^N225",
        instrument_category="market_index",
        market_group="benchmarks",
        venue="TSE",
        value_kind="points",
        quote_currency="JPY",
        quote_unit="pts",
        display_order=6,
        enabled=True,
        featured=False,
        is_index=True,
        provider_hint="openbb",
    ),

    # ─── 2. EQUITIES (Display orders 10-15) ──────────────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "equity:aapl"),
        display_name="Apple Inc.",
        display_symbol="AAPL",
        instrument_category="equity",
        market_group="equities",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=10,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "equity:msft"),
        display_name="Microsoft Corp.",
        display_symbol="MSFT",
        instrument_category="equity",
        market_group="equities",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=11,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "equity:nvda"),
        display_name="NVIDIA Corp.",
        display_symbol="NVDA",
        instrument_category="equity",
        market_group="equities",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=12,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "equity:amzn"),
        display_name="Amazon.com Inc.",
        display_symbol="AMZN",
        instrument_category="equity",
        market_group="equities",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=13,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "equity:googl"),
        display_name="Alphabet Inc.",
        display_symbol="GOOGL",
        instrument_category="equity",
        market_group="equities",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=14,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "equity:tsla"),
        display_name="Tesla Inc.",
        display_symbol="TSLA",
        instrument_category="equity",
        market_group="equities",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=15,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),

    # ─── 3. ETFS & FUNDS (Display orders 20-23) ──────────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "etf:spy"),
        display_name="SPDR S&P 500 ETF",
        display_symbol="SPY",
        instrument_category="etf",
        market_group="etfs",
        venue="NYSE Arca",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=20,
        enabled=True,
        featured=True,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "etf:qqq"),
        display_name="Invesco QQQ Trust",
        display_symbol="QQQ",
        instrument_category="etf",
        market_group="etfs",
        venue="NASDAQ",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=21,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "etf:iwm"),
        display_name="iShares Russell 2000 ETF",
        display_symbol="IWM",
        instrument_category="etf",
        market_group="etfs",
        venue="NYSE Arca",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=22,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "etf:vti"),
        display_name="Vanguard Total Stock Market",
        display_symbol="VTI",
        instrument_category="etf",
        market_group="etfs",
        venue="NYSE Arca",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=23,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),

    # ─── 4. FOREIGN EXCHANGE (Display orders 30-33) ──────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "currency:eurusd"),
        display_name="EUR / USD",
        display_symbol="EUR/USD",
        instrument_category="currency",
        market_group="fx",
        venue="FX Spot",
        value_kind="rate",
        quote_currency="USD",
        quote_unit="USD per EUR",
        display_order=30,
        enabled=True,
        featured=True,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "currency:usdjpy"),
        display_name="USD / JPY",
        display_symbol="USD/JPY",
        instrument_category="currency",
        market_group="fx",
        venue="FX Spot",
        value_kind="rate",
        quote_currency="JPY",
        quote_unit="JPY per USD",
        display_order=31,
        enabled=True,
        featured=True,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "currency:gbpusd"),
        display_name="GBP / USD",
        display_symbol="GBP/USD",
        instrument_category="currency",
        market_group="fx",
        venue="FX Spot",
        value_kind="rate",
        quote_currency="USD",
        quote_unit="USD per GBP",
        display_order=32,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "currency:usdchf"),
        display_name="USD / CHF",
        display_symbol="USD/CHF",
        instrument_category="currency",
        market_group="fx",
        venue="FX Spot",
        value_kind="rate",
        quote_currency="CHF",
        quote_unit="CHF per USD",
        display_order=33,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),

    # ─── 5. CRYPTO ASSETS (Display orders 40-42) ─────────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "crypto:btc_usd"),
        display_name="Bitcoin",
        display_symbol="BTC/USD",
        instrument_category="crypto_asset",
        market_group="crypto",
        venue="Spot",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=40,
        enabled=True,
        featured=True,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "crypto:eth_usd"),
        display_name="Ethereum",
        display_symbol="ETH/USD",
        instrument_category="crypto_asset",
        market_group="crypto",
        venue="Spot",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=41,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "crypto:sol_usd"),
        display_name="Solana",
        display_symbol="SOL/USD",
        instrument_category="crypto_asset",
        market_group="crypto",
        venue="Spot",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=42,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),

    # ─── 6. COMMODITIES (Display orders 50-53) ───────────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "commodity:brent_crude"),
        display_name="Brent Crude",
        display_symbol="BZ=F",
        instrument_category="commodity",
        market_group="commodities",
        venue="ICE",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD/bbl",
        display_order=50,
        enabled=True,
        featured=True,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "commodity:wti_crude"),
        display_name="WTI Crude Oil",
        display_symbol="CL=F",
        instrument_category="commodity",
        market_group="commodities",
        venue="NYMEX",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD/bbl",
        display_order=51,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "commodity:gold"),
        display_name="Gold",
        display_symbol="GC=F",
        instrument_category="commodity",
        market_group="commodities",
        venue="COMEX",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD/oz",
        display_order=52,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "commodity:silver"),
        display_name="Silver",
        display_symbol="SI=F",
        instrument_category="commodity",
        market_group="commodities",
        venue="COMEX",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD/oz",
        display_order=53,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),

    # ─── 7. BONDS & RATES (Display orders 60-61) ─────────────────────────────
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "bond:us10y"),
        display_name="US 10-Year Yield",
        display_symbol="^TNX",
        instrument_category="bond",
        market_group="bonds",
        venue="CBOE",
        value_kind="yield",
        quote_currency="USD",
        quote_unit="% yield",
        display_order=60,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
    MarketsOverviewInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "bond:us2y"),
        display_name="US 2-Year Yield",
        display_symbol="^IRX",
        instrument_category="bond",
        market_group="bonds",
        venue="CBOE",
        value_kind="yield",
        quote_currency="USD",
        quote_unit="% yield",
        display_order=61,
        enabled=True,
        featured=False,
        is_index=False,
        provider_hint="openbb",
    ),
]


def validate_markets_overview_config(
    configs: List[MarketsOverviewInstrumentConfig],
) -> List[MarketsOverviewInstrumentConfig]:
    """
    Validates instrument configurations ensuring strict Stage 56 requirements:
    - Bounded count (max 100)
    - No duplicate UUIDs
    - No duplicate display orders
    - Valid market groups
    - Strict sorting by display_order
    """
    if len(configs) > 100:
        raise ValueError(f"Markets Overview config exceeds max 100 items (got {len(configs)}).")

    seen_ids = set()
    seen_orders = set()

    for item in configs:
        if item.instrument_entity_id in seen_ids:
            raise ValueError(f"Duplicate instrument UUID in config: {item.instrument_entity_id}")
        seen_ids.add(item.instrument_entity_id)

        if item.display_order in seen_orders:
            raise ValueError(
                f"Duplicate display_order found in Markets Overview config: {item.display_order}"
            )
        seen_orders.add(item.display_order)

        if item.market_group not in MARKET_GROUPS_ALLOWLIST:
            allowed_groups = sorted(MARKET_GROUPS_ALLOWLIST)
            raise ValueError(
                f"Invalid market_group '{item.market_group}'. Must be one of {allowed_groups}"
            )

    return sorted(configs, key=lambda x: x.display_order)
