"""Canonical Equities Catalog Configuration for ATLAS Equities Markets V1 (Stage 57)."""

import uuid
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CanonicalEquityConfig(BaseModel):
    """Configuration record for a canonical equity security covered in ATLAS."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID = Field(
        ..., description="Canonical Financial Instrument UUID authority (Stage 17)."
    )
    display_name: str = Field(..., min_length=1, max_length=256)
    display_symbol: str = Field(..., min_length=1, max_length=64)
    equity_subtype: str = Field(
        default="common_stock",
        description="common_stock, preferred_stock, depositary_receipt",
    )
    equity_subtype_label: str = Field(default="Common Equity")
    share_class_name: Optional[str] = Field(default=None, max_length=128)

    exchange_id: Optional[UUID] = Field(default=None)
    exchange_mic: str = Field(..., min_length=2, max_length=16)
    exchange_display_name: str = Field(..., min_length=1, max_length=128)
    listing_market_country: str = Field(..., min_length=1, max_length=128)
    listing_market_country_code: str = Field(..., min_length=2, max_length=8)
    trading_currency: str = Field(default="USD", min_length=3, max_length=16)
    listing_status: str = Field(default="ACTIVE")

    # Authoritative issuer Company link (Stage 18 / Stage 23)
    issuer_company_entity_id: Optional[UUID] = Field(default=None)
    issuer_company_name: Optional[str] = Field(default=None, max_length=256)
    issuer_legal_name: Optional[str] = Field(default=None, max_length=256)
    issuer_organization_type: Optional[str] = Field(default="public_company")
    issuer_website_url: Optional[str] = Field(default=None)
    issuer_country: Optional[str] = Field(default=None)

    provider_hint: Optional[str] = Field(default="openbb")
    enabled: bool = Field(default=True)

    @field_validator(
        "display_name",
        "display_symbol",
        "exchange_mic",
        "exchange_display_name",
        "listing_market_country",
        "listing_market_country_code",
    )
    @classmethod
    def strip_strings(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace.")
        return cleaned


# Canonical Namespaced UUIDs for ATLAS Instruments and Entities
ATLAS_EQUITIES_NAMESPACE = UUID("a1a2a3a4-b1b2-c1c2-d1d2-e1e2e3e4e5e6")

SUPPORTED_EQUITY_SUBTYPES = {
    "common_stock": "Common Equity",
    "preferred_stock": "Preferred Equity",
    "depositary_receipt": "Depositary Receipt",
}

SUPPORTED_LISTING_STATUSES = {
    "ACTIVE": "Active",
    "INACTIVE": "Inactive",
    "DELISTED": "Delisted",
    "SUSPENDED": "Suspended",
}

# -----------------------------------------------------------------------------
# Canonical Covered Equities Catalog (Stage 57 Baseline Universe)
# Demonstrates exchange-awareness, multi-currency, share-classes, ADRs,
# and verified issuer company relationships.
# -----------------------------------------------------------------------------
DEFAULT_EQUITIES_CATALOG: List[CanonicalEquityConfig] = [
    # 1. Apple Inc. (NASDAQ)
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:aapl"),
        display_name="Apple Inc.",
        display_symbol="AAPL",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Common Stock",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:aapl"),
        issuer_company_name="Apple Inc.",
        issuer_legal_name="Apple Inc.",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.apple.com",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 2. Microsoft Corp. (NASDAQ)
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:msft"),
        display_name="Microsoft Corp.",
        display_symbol="MSFT",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Common Stock",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:msft"),
        issuer_company_name="Microsoft Corp.",
        issuer_legal_name="Microsoft Corporation",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.microsoft.com",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 3. NVIDIA Corp. (NASDAQ)
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:nvda"),
        display_name="NVIDIA Corp.",
        display_symbol="NVDA",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Common Stock",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:nvda"),
        issuer_company_name="NVIDIA Corp.",
        issuer_legal_name="NVIDIA Corporation",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.nvidia.com",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 4. Amazon.com Inc. (NASDAQ)
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:amzn"),
        display_name="Amazon.com Inc.",
        display_symbol="AMZN",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Common Stock",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:amzn"),
        issuer_company_name="Amazon.com Inc.",
        issuer_legal_name="Amazon.com, Inc.",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.amazon.com",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 5. Alphabet Inc. Class A (NASDAQ) - Voting Share Class
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:googl"),
        display_name="Alphabet Inc. (Class A)",
        display_symbol="GOOGL",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Class A",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:googl"),
        issuer_company_name="Alphabet Inc.",
        issuer_legal_name="Alphabet Inc.",
        issuer_organization_type="public_company",
        issuer_website_url="https://abc.xyz",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 6. Alphabet Inc. Class C (NASDAQ) - Non-Voting Share Class (Distinct Security UUID)
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:goog"),
        display_name="Alphabet Inc. (Class C)",
        display_symbol="GOOG",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Class C",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:googl"),
        issuer_company_name="Alphabet Inc.",
        issuer_legal_name="Alphabet Inc.",
        issuer_organization_type="public_company",
        issuer_website_url="https://abc.xyz",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 7. Tesla Inc. (NASDAQ)
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:tsla"),
        display_name="Tesla Inc.",
        display_symbol="TSLA",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Common Stock",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnas"),
        exchange_mic="XNAS",
        exchange_display_name="NASDAQ",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:tsla"),
        issuer_company_name="Tesla Inc.",
        issuer_legal_name="Tesla, Inc.",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.tesla.com",
        issuer_country="United States",
        provider_hint="openbb",
    ),
    # 8. Taiwan Semiconductor Manufacturing Co. ADR (NYSE) - Depositary Receipt
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:tsm_adr"),
        display_name="Taiwan Semiconductor Manufacturing Co. (ADR)",
        display_symbol="TSM",
        equity_subtype="depositary_receipt",
        equity_subtype_label="Depositary Receipt",
        share_class_name="ADR",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnys"),
        exchange_mic="XNYS",
        exchange_display_name="New York Stock Exchange",
        listing_market_country="United States",
        listing_market_country_code="US",
        trading_currency="USD",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:tsmc"),
        issuer_company_name="Taiwan Semiconductor Manufacturing Company",
        issuer_legal_name="Taiwan Semiconductor Manufacturing Company Limited",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.tsmc.com",
        issuer_country="Taiwan",
        provider_hint="openbb",
    ),
    # 9. Reliance Industries Ltd. (NSE India) - INR Denomination
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:reliance_nse"),
        display_name="Reliance Industries Ltd.",
        display_symbol="RELIANCE",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Equity Shares",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnse"),
        exchange_mic="XNSE",
        exchange_display_name="National Stock Exchange of India",
        listing_market_country="India",
        listing_market_country_code="IN",
        trading_currency="INR",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:reliance"),
        issuer_company_name="Reliance Industries Limited",
        issuer_legal_name="Reliance Industries Limited",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.ril.com",
        issuer_country="India",
        provider_hint="openbb",
    ),
    # 10. Tata Consultancy Services (NSE India) - INR Denomination
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:tcs_nse"),
        display_name="Tata Consultancy Services Ltd.",
        display_symbol="TCS",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Equity Shares",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xnse"),
        exchange_mic="XNSE",
        exchange_display_name="National Stock Exchange of India",
        listing_market_country="India",
        listing_market_country_code="IN",
        trading_currency="INR",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:tcs"),
        issuer_company_name="Tata Consultancy Services",
        issuer_legal_name="Tata Consultancy Services Limited",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.tcs.com",
        issuer_country="India",
        provider_hint="openbb",
    ),
    # 11. AstraZeneca PLC (London Stock Exchange) - GBP Denomination
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:azn_lse"),
        display_name="AstraZeneca PLC",
        display_symbol="AZN",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Ordinary Shares",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xlon"),
        exchange_mic="XLON",
        exchange_display_name="London Stock Exchange",
        listing_market_country="United Kingdom",
        listing_market_country_code="GB",
        trading_currency="GBP",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:astrazeneca"),
        issuer_company_name="AstraZeneca PLC",
        issuer_legal_name="AstraZeneca PLC",
        issuer_organization_type="public_company",
        issuer_website_url="https://www.astrazeneca.com",
        issuer_country="United Kingdom",
        provider_hint="openbb",
    ),
    # 12. Toyota Motor Corp. (Tokyo Stock Exchange) - JPY Denomination
    CanonicalEquityConfig(
        instrument_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "equity:toyota_tse"),
        display_name="Toyota Motor Corp.",
        display_symbol="7203",
        equity_subtype="common_stock",
        equity_subtype_label="Common Equity",
        share_class_name="Common Stock",
        exchange_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "exchange:xtks"),
        exchange_mic="XTKS",
        exchange_display_name="Tokyo Stock Exchange",
        listing_market_country="Japan",
        listing_market_country_code="JP",
        trading_currency="JPY",
        listing_status="ACTIVE",
        issuer_company_entity_id=uuid.uuid5(ATLAS_EQUITIES_NAMESPACE, "company:toyota"),
        issuer_company_name="Toyota Motor Corporation",
        issuer_legal_name="Toyota Motor Corporation",
        issuer_organization_type="public_company",
        issuer_website_url="https://global.toyota",
        issuer_country="Japan",
        provider_hint="openbb",
    ),
]


def validate_equities_catalog(
    configs: List[CanonicalEquityConfig],
) -> List[CanonicalEquityConfig]:
    """
    Validates canonical equities catalog integrity.
    Ensures:
    - Unique Financial Instrument UUIDs.
    - No duplicate (exchange_mic, display_symbol) pairs.
    - Subtypes and listing statuses belong to supported allowlists.
    """
    seen_ids = set()
    seen_venue_symbols = set()

    for c in configs:
        if c.instrument_entity_id in seen_ids:
            raise ValueError(
                f"Duplicate equity instrument UUID in catalog: {c.instrument_entity_id}"
            )
        seen_ids.add(c.instrument_entity_id)

        venue_sym_key = (c.exchange_mic.upper(), c.display_symbol.upper())
        if venue_sym_key in seen_venue_symbols:
            raise ValueError(
                f"Duplicate (exchange_mic, symbol) pair in catalog: {venue_sym_key}"
            )
        seen_venue_symbols.add(venue_sym_key)

        if c.equity_subtype not in SUPPORTED_EQUITY_SUBTYPES:
            raise ValueError(f"Unsupported equity subtype: {c.equity_subtype}")

        if c.listing_status not in SUPPORTED_LISTING_STATUSES:
            raise ValueError(f"Unsupported listing status: {c.listing_status}")

    return configs
