"""Curated Server-Owned Instrument Configuration for Home Market Summary (Stage 52)."""

import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MarketSummaryInstrumentConfig(BaseModel):
    """Configuration record for an instrument monitored on the Home Market Summary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: uuid.UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority."
    )
    display_name: str = Field(..., min_length=1, max_length=128)
    display_symbol: str = Field(..., min_length=1, max_length=32)
    instrument_category: str = Field(
        ..., description="Category: market_index, etf, currency, crypto_asset, commodity, equity"
    )
    value_kind: str = Field(default="price", description="price, points, rate")
    quote_currency: Optional[str] = Field(default=None, max_length=16)
    quote_unit: Optional[str] = Field(default=None, max_length=32)
    display_order: int = Field(ge=0, le=100)
    enabled: bool = Field(default=True)
    is_index: bool = Field(
        default=False, description="True for benchmark indices, False for ETFs or securities."
    )
    provider_hint: Optional[str] = Field(default=None)

    @field_validator("display_name", "display_symbol")
    @classmethod
    def strip_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace.")
        return cleaned


# Canonical Namespaced UUIDs for Curated ATLAS Market Instruments
# Generated deterministically using standard UUID5 namespace for ATLAS instruments
ATLAS_INSTRUMENT_NAMESPACE = uuid.UUID("a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6")

DEFAULT_MARKET_SUMMARY_INSTRUMENTS: List[MarketSummaryInstrumentConfig] = [
    # 1. Equity Benchmark Index: S&P 500
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:sp500"),
        display_name="S&P 500",
        display_symbol="^GSPC",
        instrument_category="market_index",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=1,
        enabled=True,
        is_index=True,
        provider_hint="openbb",
    ),
    # 2. Equity Benchmark Index: NASDAQ 100
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:nasdaq100"),
        display_name="NASDAQ 100",
        display_symbol="^NDX",
        instrument_category="market_index",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=2,
        enabled=True,
        is_index=True,
        provider_hint="openbb",
    ),
    # 3. Equity Benchmark Index: Dow Jones Industrial Average
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "market_index:dow_jones"),
        display_name="Dow Jones Industrial",
        display_symbol="^DJI",
        instrument_category="market_index",
        value_kind="points",
        quote_currency="USD",
        quote_unit="pts",
        display_order=3,
        enabled=True,
        is_index=True,
        provider_hint="openbb",
    ),
    # 4. Equity ETF: SPDR S&P 500 ETF Trust (Distinct from S&P 500 Index)
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "etf:spy"),
        display_name="SPDR S&P 500 ETF",
        display_symbol="SPY",
        instrument_category="etf",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=4,
        enabled=True,
        is_index=False,
        provider_hint="openbb",
    ),
    # 5. Foreign Exchange: EUR / USD
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "currency:eurusd"),
        display_name="EUR / USD",
        display_symbol="EUR/USD",
        instrument_category="currency",
        value_kind="rate",
        quote_currency="USD",
        quote_unit="USD per EUR",
        display_order=5,
        enabled=True,
        is_index=False,
        provider_hint="openbb",
    ),
    # 6. Foreign Exchange: USD / JPY
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "currency:usdjpy"),
        display_name="USD / JPY",
        display_symbol="USD/JPY",
        instrument_category="currency",
        value_kind="rate",
        quote_currency="JPY",
        quote_unit="JPY per USD",
        display_order=6,
        enabled=True,
        is_index=False,
        provider_hint="openbb",
    ),
    # 7. Crypto Asset: Bitcoin
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "crypto:btc_usd"),
        display_name="Bitcoin",
        display_symbol="BTC/USD",
        instrument_category="crypto_asset",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD",
        display_order=7,
        enabled=True,
        is_index=False,
        provider_hint="openbb",
    ),
    # 8. Commodity: Brent Crude Oil
    MarketSummaryInstrumentConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_INSTRUMENT_NAMESPACE, "commodity:brent_crude"),
        display_name="Brent Crude",
        display_symbol="BZ=F",
        instrument_category="commodity",
        value_kind="price",
        quote_currency="USD",
        quote_unit="USD/bbl",
        display_order=8,
        enabled=True,
        is_index=False,
        provider_hint="openbb",
    ),
]


def validate_market_summary_config(
    configs: List[MarketSummaryInstrumentConfig],
) -> List[MarketSummaryInstrumentConfig]:
    """
    Validates instrument configurations ensuring strict Stage 52 requirements:
    - Bounded count (max 20)
    - No duplicate UUIDs
    - No duplicate display orders
    - Strict sorting by display_order
    """
    if len(configs) > 20:
        raise ValueError(f"Market Summary config exceeds max 20 items (got {len(configs)}).")

    seen_ids = set()
    seen_orders = set()

    for item in configs:
        if item.instrument_entity_id in seen_ids:
            raise ValueError(f"Duplicate instrument UUID in config: {item.instrument_entity_id}")
        seen_ids.add(item.instrument_entity_id)

        if item.display_order in seen_orders:
            raise ValueError(
                f"Duplicate display_order found in Market Summary config: {item.display_order}"
            )
        seen_orders.add(item.display_order)

    # Return stable sorted list
    return sorted(configs, key=lambda x: x.display_order)
