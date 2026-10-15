"""Canonical FX Catalog Configuration for ATLAS FX Markets V1 (Stage 59)."""

import uuid
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CurrencyMetadata(BaseModel):
    """Metadata record for a validated ISO 4217 fiat currency."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(
        ..., min_length=3, max_length=3, description="ISO 4217 three-letter currency code."
    )
    name: str = Field(..., min_length=1, max_length=128)
    symbol: str = Field(..., min_length=1, max_length=8)
    minor_units: int = Field(
        default=2, ge=0, le=4, description="Standard ISO minor units (decimal places for cash)."
    )
    country_or_region: str = Field(..., max_length=128)


ISO_4217_REGISTRY: Dict[str, CurrencyMetadata] = {
    "USD": CurrencyMetadata(
        code="USD",
        name="United States Dollar",
        symbol="$",
        minor_units=2,
        country_or_region="United States",
    ),
    "EUR": CurrencyMetadata(
        code="EUR", name="Euro", symbol="€", minor_units=2, country_or_region="Eurozone"
    ),
    "GBP": CurrencyMetadata(
        code="GBP",
        name="British Pound Sterling",
        symbol="£",
        minor_units=2,
        country_or_region="United Kingdom",
    ),
    "JPY": CurrencyMetadata(
        code="JPY", name="Japanese Yen", symbol="¥", minor_units=0, country_or_region="Japan"
    ),
    "CHF": CurrencyMetadata(
        code="CHF", name="Swiss Franc", symbol="CHF", minor_units=2, country_or_region="Switzerland"
    ),
    "CAD": CurrencyMetadata(
        code="CAD", name="Canadian Dollar", symbol="C$", minor_units=2, country_or_region="Canada"
    ),
    "AUD": CurrencyMetadata(
        code="AUD",
        name="Australian Dollar",
        symbol="A$",
        minor_units=2,
        country_or_region="Australia",
    ),
    "NZD": CurrencyMetadata(
        code="NZD",
        name="New Zealand Dollar",
        symbol="NZ$",
        minor_units=2,
        country_or_region="New Zealand",
    ),
    "INR": CurrencyMetadata(
        code="INR", name="Indian Rupee", symbol="₹", minor_units=2, country_or_region="India"
    ),
    "CNY": CurrencyMetadata(
        code="CNY", name="Chinese Yuan", symbol="¥", minor_units=2, country_or_region="China"
    ),
    "SGD": CurrencyMetadata(
        code="SGD",
        name="Singapore Dollar",
        symbol="S$",
        minor_units=2,
        country_or_region="Singapore",
    ),
    "HKD": CurrencyMetadata(
        code="HKD",
        name="Hong Kong Dollar",
        symbol="HK$",
        minor_units=2,
        country_or_region="Hong Kong",
    ),
    "SEK": CurrencyMetadata(
        code="SEK", name="Swedish Krona", symbol="kr", minor_units=2, country_or_region="Sweden"
    ),
    "NOK": CurrencyMetadata(
        code="NOK", name="Norwegian Krone", symbol="kr", minor_units=2, country_or_region="Norway"
    ),
}


class CanonicalFxPairConfig(BaseModel):
    """Configuration record for a canonical spot currency pair in ATLAS."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority (Stage 17)."
    )
    display_pair: str = Field(
        ..., min_length=7, max_length=15, description="Conventional BASE/QUOTE notation."
    )
    base_currency: str = Field(..., min_length=3, max_length=3)
    quote_currency: str = Field(..., min_length=3, max_length=3)
    instrument_kind: str = Field(default="SPOT_FX", description="SPOT_FX only in Stage 59.")
    pip_size: Decimal = Field(
        default=Decimal("0.0001"),
        description="Conventional pip size (0.01 for JPY pairs, 0.0001 for non-JPY).",
    )
    rate_precision: int = Field(
        default=4, ge=0, le=8, description="Standard quotation decimal places."
    )
    default_bid: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_ask: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    default_rate_kind: str = Field(default="SPOT_BID_ASK")
    default_provider: str = Field(default="OPENBB")
    provider_aliases: List[str] = Field(default_factory=list)

    @field_validator("base_currency", "quote_currency")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        code = v.upper().strip()
        if code not in ISO_4217_REGISTRY:
            raise ValueError(f"Currency code '{code}' is not in validated ISO 4217 fiat registry.")
        return code

    @field_validator("display_pair")
    @classmethod
    def validate_display_pair_format(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError(f"Display pair '{v}' must be formatted as BASE/QUOTE.")
        parts = v.split("/")
        if len(parts) != 2 or len(parts[0]) != 3 or len(parts[1]) != 3:
            raise ValueError(f"Display pair '{v}' must have 3-letter codes separated by slash.")
        return v.upper()


FX_NAMESPACE = uuid.UUID("33333333-3333-5959-8888-000000000000")


def generate_fx_instrument_uuid(base: str, quote: str) -> UUID:
    """Generate deterministic UUID5 for a canonical currency pair."""
    return uuid.uuid5(FX_NAMESPACE, f"SPOT_FX:{base.upper()}/{quote.upper()}")


# Pre-defined curated canonical spot FX catalog
DEFAULT_FX_CATALOG: List[CanonicalFxPairConfig] = [
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("EUR", "USD"),
        display_pair="EUR/USD",
        base_currency="EUR",
        quote_currency="USD",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("1.0848"),
        default_ask=Decimal("1.0850"),
        provider_aliases=["EURUSD", "EUR_USD", "EUR-USD"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("GBP", "USD"),
        display_pair="GBP/USD",
        base_currency="GBP",
        quote_currency="USD",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("1.2642"),
        default_ask=Decimal("1.2645"),
        provider_aliases=["GBPUSD", "GBP_USD", "GBP-USD"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("USD", "JPY"),
        display_pair="USD/JPY",
        base_currency="USD",
        quote_currency="JPY",
        pip_size=Decimal("0.01"),
        rate_precision=2,
        default_bid=Decimal("153.25"),
        default_ask=Decimal("153.28"),
        provider_aliases=["USDJPY", "USD_JPY", "USD-JPY"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("USD", "CHF"),
        display_pair="USD/CHF",
        base_currency="USD",
        quote_currency="CHF",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("0.8870"),
        default_ask=Decimal("0.8873"),
        provider_aliases=["USDCHF", "USD_CHF", "USD-CHF"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("AUD", "USD"),
        display_pair="AUD/USD",
        base_currency="AUD",
        quote_currency="USD",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("0.6515"),
        default_ask=Decimal("0.6518"),
        provider_aliases=["AUDUSD", "AUD_USD", "AUD-USD"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("USD", "CAD"),
        display_pair="USD/CAD",
        base_currency="USD",
        quote_currency="CAD",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("1.3920"),
        default_ask=Decimal("1.3923"),
        provider_aliases=["USDCAD", "USD_CAD", "USD-CAD"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("USD", "INR"),
        display_pair="USD/INR",
        base_currency="USD",
        quote_currency="INR",
        pip_size=Decimal("0.01"),
        rate_precision=2,
        default_bid=Decimal("84.38"),
        default_ask=Decimal("84.42"),
        provider_aliases=["USDINR", "USD_INR", "USD-INR"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("EUR", "GBP"),
        display_pair="EUR/GBP",
        base_currency="EUR",
        quote_currency="GBP",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("0.8578"),
        default_ask=Decimal("0.8581"),
        provider_aliases=["EURGBP", "EUR_GBP", "EUR-GBP"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("EUR", "JPY"),
        display_pair="EUR/JPY",
        base_currency="EUR",
        quote_currency="JPY",
        pip_size=Decimal("0.01"),
        rate_precision=2,
        default_bid=Decimal("166.24"),
        default_ask=Decimal("166.28"),
        provider_aliases=["EURJPY", "EUR_JPY", "EUR-JPY"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("NZD", "USD"),
        display_pair="NZD/USD",
        base_currency="NZD",
        quote_currency="USD",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("0.5925"),
        default_ask=Decimal("0.5928"),
        provider_aliases=["NZDUSD", "NZD_USD", "NZD-USD"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("USD", "CNY"),
        display_pair="USD/CNY",
        base_currency="USD",
        quote_currency="CNY",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("7.2340"),
        default_ask=Decimal("7.2355"),
        provider_aliases=["USDCNY", "USD_CNY", "USD-CNY"],
    ),
    CanonicalFxPairConfig(
        instrument_entity_id=generate_fx_instrument_uuid("USD", "SGD"),
        display_pair="USD/SGD",
        base_currency="USD",
        quote_currency="SGD",
        pip_size=Decimal("0.0001"),
        rate_precision=4,
        default_bid=Decimal("1.3390"),
        default_ask=Decimal("1.3393"),
        provider_aliases=["USDSGD", "USD_SGD", "USD-SGD"],
    ),
]


def validate_fx_catalog(catalog: List[CanonicalFxPairConfig]) -> None:
    """Validate that the FX catalog contains unique canonical IDs and distinct base/quote pairs."""
    seen_ids = set()
    seen_pairs = set()

    for item in catalog:
        if item.instrument_entity_id in seen_ids:
            raise ValueError(
                f"Duplicate canonical instrument_entity_id: {item.instrument_entity_id}"
            )
        seen_ids.add(item.instrument_entity_id)

        pair_key = (item.base_currency, item.quote_currency)
        if pair_key in seen_pairs:
            raise ValueError(f"Duplicate currency pair listing: {item.display_pair}")
        seen_pairs.add(pair_key)

        if item.base_currency == item.quote_currency:
            raise ValueError(
                f"Base currency and quote currency cannot be identical: {item.display_pair}"
            )
