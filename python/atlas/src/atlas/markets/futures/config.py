"""Canonical Configuration and Reference Data for ATLAS Futures & Commodities Markets V1 (Stage 62).

Defines deterministic UUID5 identity namespaces, canonical commodities, futures products,
multi-month listed contracts, spot benchmarks, and financial derivatives classification enums.
"""

import uuid
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Deterministic UUID5 Namespaces
# ---------------------------------------------------------------------------
COMMODITY_NAMESPACE = UUID("33333333-3333-5333-a333-000000000001")
FUTURES_PRODUCT_NAMESPACE = UUID("33333333-3333-5333-a333-000000000002")
FUTURES_CONTRACT_NAMESPACE = UUID("33333333-3333-5333-a333-000000000003")
SPOT_BENCHMARK_NAMESPACE = UUID("33333333-3333-5333-a333-000000000004")


def generate_commodity_id(slug: str) -> UUID:
    """Generate deterministic UUID for an underlying economic commodity."""
    return uuid.uuid5(COMMODITY_NAMESPACE, f"commodity:{slug.lower()}")


def generate_futures_product_id(exchange: str, root_symbol: str) -> UUID:
    """Generate deterministic UUID for a standardized futures contract family."""
    return uuid.uuid5(
        FUTURES_PRODUCT_NAMESPACE, f"futures_product:{exchange.upper()}:{root_symbol.upper()}"
    )


def generate_futures_contract_id(exchange: str, symbol: str) -> UUID:
    """Generate deterministic UUID for an individual futures expiration instrument."""
    return uuid.uuid5(
        FUTURES_CONTRACT_NAMESPACE, f"instrument:futures:{exchange.upper()}:{symbol.upper()}"
    )


def generate_spot_benchmark_id(slug: str) -> UUID:
    """Generate deterministic UUID for a physical commodity spot benchmark."""
    return uuid.uuid5(SPOT_BENCHMARK_NAMESPACE, f"spot_benchmark:{slug.lower()}")


# ---------------------------------------------------------------------------
# Standard Month Codes Mapping
# ---------------------------------------------------------------------------
MONTH_CODE_TO_NUM: Dict[str, int] = {
    "F": 1,  # January
    "G": 2,  # February
    "H": 3,  # March
    "J": 4,  # April
    "K": 5,  # May
    "M": 6,  # June
    "N": 7,  # July
    "Q": 8,  # August
    "U": 9,  # September
    "V": 10,  # October
    "X": 11,  # November
    "Z": 12,  # December
}

NUM_TO_MONTH_CODE: Dict[int, str] = {v: k for k, v in MONTH_CODE_TO_NUM.items()}

MONTH_NUM_TO_NAME: Dict[int, str] = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class CommodityCategoryEnum(str, Enum):
    """Classification of underlying commodity asset."""

    ENERGY = "energy"
    PRECIOUS_METALS = "precious_metals"
    INDUSTRIAL_METALS = "industrial_metals"
    AGRICULTURE = "agriculture"
    SOFT_COMMODITIES = "soft_commodities"
    LIVESTOCK = "livestock"
    FINANCIAL_INDEX = "financial_index"


class SettlementTypeEnum(str, Enum):
    """Settlement method of the futures contract upon expiration."""

    PHYSICAL = "physical"
    CASH = "cash"
    OTHER_UNKNOWN = "other_unknown"


class ContractLifecycleEnum(str, Enum):
    """Trading lifecycle status of an individual futures contract."""

    ACTIVE = "active"
    EXPIRED = "expired"
    DELISTED = "delisted"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


class PriceObservationKindEnum(str, Enum):
    """Type of price observation."""

    TRADE_PRICE = "trade_price"
    SETTLEMENT_PRICE = "settlement_price"
    INDICATIVE_QUOTE = "indicative_quote"
    UNKNOWN = "unknown"


class SettlementStatusEnum(str, Enum):
    """Publication status of the official daily settlement."""

    FINAL = "FINAL"
    PRELIMINARY = "PRELIMINARY"


class VolumeWindowEnum(str, Enum):
    """Window duration for trading volume measurement."""

    SESSION = "SESSION"
    DAILY = "DAILY"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Configuration Schemas
# ---------------------------------------------------------------------------
class CommodityUnderlyingConfig(BaseModel):
    """Canonical model for an underlying commodity or index asset."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    commodity_entity_id: UUID
    name: str = Field(..., min_length=2, max_length=128)
    slug: str = Field(..., min_length=2, max_length=64)
    category: CommodityCategoryEnum
    grade_specification: Optional[str] = None
    physical_unit: str = Field(..., min_length=1, max_length=64)
    reference_region: Optional[str] = None
    delivery_characteristics: Optional[str] = None


class FuturesProductConfig(BaseModel):
    """Standardized contract family specification listed on a venue."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    product_entity_id: UUID
    underlying_entity_id: UUID
    root_symbol: str = Field(..., min_length=1, max_length=16)
    name: str = Field(..., min_length=2, max_length=128)
    exchange: str = Field(..., min_length=2, max_length=32)
    exchange_mic: str = Field(..., min_length=4, max_length=4)
    category: CommodityCategoryEnum
    contract_size: Decimal
    size_unit: str = Field(..., min_length=1, max_length=64)
    quote_currency: str = Field(..., min_length=3, max_length=3)
    quote_unit: str = Field(..., min_length=1, max_length=64)
    tick_size: Decimal
    tick_value: Optional[Decimal] = None
    settlement_type: SettlementTypeEnum
    contract_multiplier: Decimal = Decimal("1.0")
    trading_hours: str = "Sunday-Friday 18:00-17:00 ET (with 60-minute break)"


class CanonicalFuturesContractConfig(BaseModel):
    """Canonical listed futures contract tied to a specific delivery/expiration period."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    instrument_entity_id: UUID
    product_entity_id: UUID
    underlying_entity_id: UUID
    symbol: str = Field(..., min_length=2, max_length=32)
    name: str = Field(..., min_length=2, max_length=128)
    exchange: str = Field(..., min_length=2, max_length=32)
    exchange_mic: str = Field(..., min_length=4, max_length=4)
    contract_year: int = Field(..., ge=1900, le=2100)
    contract_month_code: str = Field(..., min_length=1, max_length=1)
    contract_month: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    expiration_date: str = Field(..., description="Contract expiration date (YYYY-MM-DD)")
    last_trading_date: str = Field(..., description="Final permitted trading date (YYYY-MM-DD)")
    first_notice_date: Optional[str] = None
    last_notice_date: Optional[str] = None
    delivery_start_date: Optional[str] = None
    delivery_end_date: Optional[str] = None
    settlement_date: str = Field(..., description="Final settlement date (YYYY-MM-DD)")
    lifecycle_status: ContractLifecycleEnum = ContractLifecycleEnum.ACTIVE
    contract_size: Decimal
    size_unit: str
    quote_currency: str
    quote_unit: str
    tick_size: Decimal
    tick_value: Optional[Decimal] = None
    settlement_type: SettlementTypeEnum
    contract_multiplier: Decimal = Decimal("1.0")
    trading_hours: str = "Sunday-Friday 18:00-17:00 ET"

    # Market Observations
    latest_trade_price: Optional[Decimal] = None
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    official_settlement: Optional[Decimal] = None
    previous_settlement: Optional[Decimal] = None
    settlement_status: SettlementStatusEnum = SettlementStatusEnum.FINAL
    settlement_trade_date: Optional[str] = None
    volume: Optional[int] = None
    open_interest: Optional[int] = None
    open_interest_as_of: Optional[str] = None
    source_timestamp: str = "2026-10-15T20:30:00Z"
    received_at: str = "2026-10-15T20:30:01Z"
    freshness_status: str = "REALTIME"
    delay_status: str = "REALTIME"
    provider: str = "OPENBB"


class CommoditySpotBenchmarkConfig(BaseModel):
    """Canonical model for a physical commodity spot price benchmark."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    benchmark_entity_id: UUID
    commodity_entity_id: UUID
    name: str = Field(..., min_length=2, max_length=128)
    grade: str
    location: str
    currency: str = Field(..., min_length=3, max_length=3)
    quote_unit: str
    assessment_methodology: str
    latest_price: Optional[Decimal] = None
    previous_price: Optional[Decimal] = None
    as_of_date: str
    provider: str = "OPENBB"


# ---------------------------------------------------------------------------
# Canonical Underlyings Catalog
# ---------------------------------------------------------------------------
CANONICAL_COMMODITIES: List[CommodityUnderlyingConfig] = [
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("wti-crude-oil"),
        name="WTI Light Sweet Crude Oil",
        slug="wti-crude-oil",
        category=CommodityCategoryEnum.ENERGY,
        grade_specification="API gravity 37° to 42°, sulfur content not exceeding 0.42% by weight",
        physical_unit="barrel",
        reference_region="Cushing, Oklahoma, USA",
        delivery_characteristics="Pipeline or storage facility delivery at Cushing, Oklahoma",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("brent-crude-oil"),
        name="Brent Crude Oil",
        slug="brent-crude-oil",
        category=CommodityCategoryEnum.ENERGY,
        grade_specification="Light sweet North Sea blend (Brent, Forties, Oseberg, Ekofisk, Troll)",
        physical_unit="barrel",
        reference_region="North Sea, UK / Norway / Sullom Voe",
        delivery_characteristics="Cash settlement based on ICE Brent Index at contract expiry",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("henry-hub-natural-gas"),
        name="Henry Hub Natural Gas",
        slug="henry-hub-natural-gas",
        category=CommodityCategoryEnum.ENERGY,
        grade_specification=(
            "Pipeline-quality dry methane natural gas complying with Sabine Pipe Line specification"
        ),
        physical_unit="MMBtu",
        reference_region="Erath, Louisiana, USA",
        delivery_characteristics=(
            "Physical delivery through Sabine Pipe Line Company's Henry Hub in Louisiana"
        ),
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("gold"),
        name="Gold",
        slug="gold",
        category=CommodityCategoryEnum.PRECIOUS_METALS,
        grade_specification=(
            "Not less than 0.995 fine gold purity cast in one bar or three 1-kilo bars"
        ),
        physical_unit="troy ounce",
        reference_region="COMEX Depository, New York, USA",
        delivery_characteristics="Physical delivery of warrant at approved COMEX depository",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("silver"),
        name="Silver",
        slug="silver",
        category=CommodityCategoryEnum.PRECIOUS_METALS,
        grade_specification="Not less than 0.999 fine silver cast in 1,000-troy-ounce bars",
        physical_unit="troy ounce",
        reference_region="COMEX Depository, New York, USA",
        delivery_characteristics="Physical delivery of vault receipt at approved COMEX depository",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("copper"),
        name="Grade A Copper",
        slug="copper",
        category=CommodityCategoryEnum.INDUSTRIAL_METALS,
        grade_specification="ASTM B115 electrolytic cathode Grade A copper",
        physical_unit="pound",
        reference_region="Licensed COMEX warehouses in USA",
        delivery_characteristics="Physical delivery of COMEX warehouse warrants",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("corn"),
        name="#2 Yellow Corn",
        slug="corn",
        category=CommodityCategoryEnum.AGRICULTURE,
        grade_specification="USDA Grade #2 Yellow Corn (USDA Grade #1 at a premium)",
        physical_unit="bushel",
        reference_region="Chicago & Illinois Waterway Delivery District",
        delivery_characteristics="Physical delivery by shipping certificate via approved elevators",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("soybeans"),
        name="#1 Yellow Soybeans",
        slug="soybeans",
        category=CommodityCategoryEnum.AGRICULTURE,
        grade_specification="USDA Grade #1 Yellow Soybeans (USDA Grade #2 at differential)",
        physical_unit="bushel",
        reference_region="Chicago, Burns Harbor, Northwest Indiana",
        delivery_characteristics="Physical delivery by shipping certificate via approved elevators",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("wheat"),
        name="Chicago SRW Wheat",
        slug="wheat",
        category=CommodityCategoryEnum.AGRICULTURE,
        grade_specification="USDA Grade #2 Soft Red Winter Wheat",
        physical_unit="bushel",
        reference_region="Chicago & Toledo, Ohio switching districts",
        delivery_characteristics="Physical delivery by shipping certificate via approved elevators",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("live-cattle"),
        name="Live Cattle",
        slug="live-cattle",
        category=CommodityCategoryEnum.LIVESTOCK,
        grade_specification="55% Choice, 45% Select USDA yield grade live steers",
        physical_unit="pound",
        reference_region="Approved livestock yards in Nebraska, Texas, Kansas, Oklahoma",
        delivery_characteristics="Physical delivery at approved CME livestock stockyards",
    ),
    CommodityUnderlyingConfig(
        commodity_entity_id=generate_commodity_id("sp500-index"),
        name="S&P 500 Index",
        slug="sp500-index",
        category=CommodityCategoryEnum.FINANCIAL_INDEX,
        grade_specification="Standard & Poor's 500 Composite Stock Price Index",
        physical_unit="index point",
        reference_region="United States Equity Markets",
        delivery_characteristics="Cash settlement based on Special Opening Quotation (SOQ)",
    ),
]

COMMODITIES_BY_ID: Dict[UUID, CommodityUnderlyingConfig] = {
    c.commodity_entity_id: c for c in CANONICAL_COMMODITIES
}


# ---------------------------------------------------------------------------
# Canonical Futures Products Catalog
# ---------------------------------------------------------------------------
CANONICAL_FUTURES_PRODUCTS: List[FuturesProductConfig] = [
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("NYMEX", "CL"),
        underlying_entity_id=generate_commodity_id("wti-crude-oil"),
        root_symbol="CL",
        name="Light Sweet Crude Oil Futures",
        exchange="NYMEX",
        exchange_mic="XNYM",
        category=CommodityCategoryEnum.ENERGY,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("ICE", "BZ"),
        underlying_entity_id=generate_commodity_id("brent-crude-oil"),
        root_symbol="BZ",
        name="Brent Crude Futures",
        exchange="ICE",
        exchange_mic="IFEU",
        category=CommodityCategoryEnum.ENERGY,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.CASH,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("NYMEX", "NG"),
        underlying_entity_id=generate_commodity_id("henry-hub-natural-gas"),
        root_symbol="NG",
        name="Henry Hub Natural Gas Futures",
        exchange="NYMEX",
        exchange_mic="XNYM",
        category=CommodityCategoryEnum.ENERGY,
        contract_size=Decimal("10000.0"),
        size_unit="MMBtu",
        quote_currency="USD",
        quote_unit="USD per MMBtu",
        tick_size=Decimal("0.001"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("COMEX", "GC"),
        underlying_entity_id=generate_commodity_id("gold"),
        root_symbol="GC",
        name="Gold Futures",
        exchange="COMEX",
        exchange_mic="XCEC",
        category=CommodityCategoryEnum.PRECIOUS_METALS,
        contract_size=Decimal("100.0"),
        size_unit="troy ounces",
        quote_currency="USD",
        quote_unit="USD per troy oz",
        tick_size=Decimal("0.10"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("COMEX", "SI"),
        underlying_entity_id=generate_commodity_id("silver"),
        root_symbol="SI",
        name="Silver Futures",
        exchange="COMEX",
        exchange_mic="XCEC",
        category=CommodityCategoryEnum.PRECIOUS_METALS,
        contract_size=Decimal("5000.0"),
        size_unit="troy ounces",
        quote_currency="USD",
        quote_unit="USD per troy oz",
        tick_size=Decimal("0.005"),
        tick_value=Decimal("25.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("COMEX", "HG"),
        underlying_entity_id=generate_commodity_id("copper"),
        root_symbol="HG",
        name="Copper Futures",
        exchange="COMEX",
        exchange_mic="XCEC",
        category=CommodityCategoryEnum.INDUSTRIAL_METALS,
        contract_size=Decimal("25000.0"),
        size_unit="pounds",
        quote_currency="USD",
        quote_unit="USD per pound",
        tick_size=Decimal("0.0005"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("CBOT", "ZC"),
        underlying_entity_id=generate_commodity_id("corn"),
        root_symbol="ZC",
        name="Corn Futures",
        exchange="CBOT",
        exchange_mic="XCBT",
        category=CommodityCategoryEnum.AGRICULTURE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("CBOT", "ZS"),
        underlying_entity_id=generate_commodity_id("soybeans"),
        root_symbol="ZS",
        name="Soybean Futures",
        exchange="CBOT",
        exchange_mic="XCBT",
        category=CommodityCategoryEnum.AGRICULTURE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("CBOT", "ZW"),
        underlying_entity_id=generate_commodity_id("wheat"),
        root_symbol="ZW",
        name="Wheat Futures",
        exchange="CBOT",
        exchange_mic="XCBT",
        category=CommodityCategoryEnum.AGRICULTURE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("CME", "LE"),
        underlying_entity_id=generate_commodity_id("live-cattle"),
        root_symbol="LE",
        name="Live Cattle Futures",
        exchange="CME",
        exchange_mic="XCME",
        category=CommodityCategoryEnum.LIVESTOCK,
        contract_size=Decimal("40000.0"),
        size_unit="pounds",
        quote_currency="USD",
        quote_unit="US cents per pound",
        tick_size=Decimal("0.025"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        contract_multiplier=Decimal("1.0"),
    ),
    FuturesProductConfig(
        product_entity_id=generate_futures_product_id("CME", "ES"),
        underlying_entity_id=generate_commodity_id("sp500-index"),
        root_symbol="ES",
        name="E-mini S&P 500 Futures",
        exchange="CME",
        exchange_mic="XCME",
        category=CommodityCategoryEnum.FINANCIAL_INDEX,
        contract_size=Decimal("50.0"),
        size_unit="50 x Index",
        quote_currency="USD",
        quote_unit="Index points",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.CASH,
        contract_multiplier=Decimal("50.0"),
    ),
]

FUTURES_PRODUCTS_BY_ID: Dict[UUID, FuturesProductConfig] = {
    p.product_entity_id: p for p in CANONICAL_FUTURES_PRODUCTS
}


# ---------------------------------------------------------------------------
# Canonical Individual Futures Contracts Catalog
# ---------------------------------------------------------------------------
CANONICAL_FUTURES_CONTRACTS: List[CanonicalFuturesContractConfig] = [
    # ---------------- WTI Crude Oil (NYMEX: CL) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("NYMEX", "CLZ26"),
        product_entity_id=generate_futures_product_id("NYMEX", "CL"),
        underlying_entity_id=generate_commodity_id("wti-crude-oil"),
        symbol="CLZ26",
        name="WTI Crude Oil Dec 2026",
        exchange="NYMEX",
        exchange_mic="XNYM",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-11-20",
        last_trading_date="2026-11-20",
        first_notice_date="2026-11-23",
        last_notice_date="2026-11-25",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-11-20",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("69.45"),
        bid=Decimal("69.44"),
        ask=Decimal("69.46"),
        official_settlement=Decimal("69.50"),
        previous_settlement=Decimal("70.15"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=284500,
        open_interest=412300,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("NYMEX", "CLF27"),
        product_entity_id=generate_futures_product_id("NYMEX", "CL"),
        underlying_entity_id=generate_commodity_id("wti-crude-oil"),
        symbol="CLF27",
        name="WTI Crude Oil Jan 2027",
        exchange="NYMEX",
        exchange_mic="XNYM",
        contract_year=2027,
        contract_month_code="F",
        contract_month="2027-01",
        expiration_date="2026-12-21",
        last_trading_date="2026-12-21",
        first_notice_date="2026-12-22",
        last_notice_date="2026-12-28",
        delivery_start_date="2027-01-01",
        delivery_end_date="2027-01-31",
        settlement_date="2026-12-21",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("69.80"),
        bid=Decimal("69.79"),
        ask=Decimal("69.81"),
        official_settlement=Decimal("69.85"),
        previous_settlement=Decimal("70.40"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=178200,
        open_interest=298400,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("NYMEX", "CLG27"),
        product_entity_id=generate_futures_product_id("NYMEX", "CL"),
        underlying_entity_id=generate_commodity_id("wti-crude-oil"),
        symbol="CLG27",
        name="WTI Crude Oil Feb 2027",
        exchange="NYMEX",
        exchange_mic="XNYM",
        contract_year=2027,
        contract_month_code="G",
        contract_month="2027-02",
        expiration_date="2027-01-20",
        last_trading_date="2027-01-20",
        first_notice_date="2027-01-21",
        last_notice_date="2027-01-26",
        delivery_start_date="2027-02-01",
        delivery_end_date="2027-02-28",
        settlement_date="2027-01-20",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("70.12"),
        bid=Decimal("70.10"),
        ask=Decimal("70.14"),
        official_settlement=Decimal("70.18"),
        previous_settlement=Decimal("70.65"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=92400,
        open_interest=184100,
        open_interest_as_of="2026-10-14",
    ),
    # Historical Negative Pricing Benchmark (May 2020 WTI Crude)
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("NYMEX", "CLK20"),
        product_entity_id=generate_futures_product_id("NYMEX", "CL"),
        underlying_entity_id=generate_commodity_id("wti-crude-oil"),
        symbol="CLK20",
        name="WTI Crude Oil May 2020 (Historical Expired)",
        exchange="NYMEX",
        exchange_mic="XNYM",
        contract_year=2020,
        contract_month_code="K",
        contract_month="2020-05",
        expiration_date="2020-04-21",
        last_trading_date="2020-04-21",
        first_notice_date="2020-04-22",
        last_notice_date="2020-04-24",
        delivery_start_date="2020-05-01",
        delivery_end_date="2020-05-31",
        settlement_date="2020-04-21",
        lifecycle_status=ContractLifecycleEnum.EXPIRED,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("-37.63"),
        bid=Decimal("-38.00"),
        ask=Decimal("-37.50"),
        official_settlement=Decimal("-37.63"),
        previous_settlement=Decimal("18.27"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2020-04-20",
        volume=248911,
        open_interest=10923,
        open_interest_as_of="2020-04-20",
    ),
    # ---------------- Brent Crude Oil (ICE: BZ) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("ICE", "BZF27"),
        product_entity_id=generate_futures_product_id("ICE", "BZ"),
        underlying_entity_id=generate_commodity_id("brent-crude-oil"),
        symbol="BZF27",
        name="Brent Crude Oil Jan 2027",
        exchange="ICE",
        exchange_mic="IFEU",
        contract_year=2027,
        contract_month_code="F",
        contract_month="2027-01",
        expiration_date="2026-11-30",
        last_trading_date="2026-11-30",
        settlement_date="2026-11-30",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.CASH,
        latest_trade_price=Decimal("74.22"),
        bid=Decimal("74.21"),
        ask=Decimal("74.23"),
        official_settlement=Decimal("74.28"),
        previous_settlement=Decimal("74.92"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=212400,
        open_interest=341200,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("ICE", "BZG27"),
        product_entity_id=generate_futures_product_id("ICE", "BZ"),
        underlying_entity_id=generate_commodity_id("brent-crude-oil"),
        symbol="BZG27",
        name="Brent Crude Oil Feb 2027",
        exchange="ICE",
        exchange_mic="IFEU",
        contract_year=2027,
        contract_month_code="G",
        contract_month="2027-02",
        expiration_date="2026-12-31",
        last_trading_date="2026-12-31",
        settlement_date="2026-12-31",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("1000.0"),
        size_unit="barrels",
        quote_currency="USD",
        quote_unit="USD per barrel",
        tick_size=Decimal("0.01"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.CASH,
        latest_trade_price=Decimal("74.55"),
        bid=Decimal("74.54"),
        ask=Decimal("74.56"),
        official_settlement=Decimal("74.60"),
        previous_settlement=Decimal("75.18"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=132800,
        open_interest=245000,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Natural Gas (NYMEX: NG) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("NYMEX", "NGZ26"),
        product_entity_id=generate_futures_product_id("NYMEX", "NG"),
        underlying_entity_id=generate_commodity_id("henry-hub-natural-gas"),
        symbol="NGZ26",
        name="Natural Gas Dec 2026",
        exchange="NYMEX",
        exchange_mic="XNYM",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-11-25",
        last_trading_date="2026-11-25",
        first_notice_date="2026-11-27",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-11-25",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("10000.0"),
        size_unit="MMBtu",
        quote_currency="USD",
        quote_unit="USD per MMBtu",
        tick_size=Decimal("0.001"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("3.142"),
        bid=Decimal("3.140"),
        ask=Decimal("3.144"),
        official_settlement=Decimal("3.148"),
        previous_settlement=Decimal("3.085"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=154300,
        open_interest=265400,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("NYMEX", "NGF27"),
        product_entity_id=generate_futures_product_id("NYMEX", "NG"),
        underlying_entity_id=generate_commodity_id("henry-hub-natural-gas"),
        symbol="NGF27",
        name="Natural Gas Jan 2027",
        exchange="NYMEX",
        exchange_mic="XNYM",
        contract_year=2027,
        contract_month_code="F",
        contract_month="2027-01",
        expiration_date="2026-12-29",
        last_trading_date="2026-12-29",
        first_notice_date="2026-12-30",
        delivery_start_date="2027-01-01",
        delivery_end_date="2027-01-31",
        settlement_date="2026-12-29",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("10000.0"),
        size_unit="MMBtu",
        quote_currency="USD",
        quote_unit="USD per MMBtu",
        tick_size=Decimal("0.001"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("3.385"),
        bid=Decimal("3.382"),
        ask=Decimal("3.388"),
        official_settlement=Decimal("3.390"),
        previous_settlement=Decimal("3.315"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=98100,
        open_interest=178900,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Gold (COMEX: GC) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("COMEX", "GCZ26"),
        product_entity_id=generate_futures_product_id("COMEX", "GC"),
        underlying_entity_id=generate_commodity_id("gold"),
        symbol="GCZ26",
        name="Gold Dec 2026",
        exchange="COMEX",
        exchange_mic="XCEC",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-29",
        last_trading_date="2026-12-29",
        first_notice_date="2026-11-30",
        last_notice_date="2026-12-29",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-12-29",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("100.0"),
        size_unit="troy ounces",
        quote_currency="USD",
        quote_unit="USD per troy oz",
        tick_size=Decimal("0.10"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("2685.40"),
        bid=Decimal("2685.20"),
        ask=Decimal("2685.60"),
        official_settlement=Decimal("2684.90"),
        previous_settlement=Decimal("2671.30"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=298500,
        open_interest=487200,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("COMEX", "GCG27"),
        product_entity_id=generate_futures_product_id("COMEX", "GC"),
        underlying_entity_id=generate_commodity_id("gold"),
        symbol="GCG27",
        name="Gold Feb 2027",
        exchange="COMEX",
        exchange_mic="XCEC",
        contract_year=2027,
        contract_month_code="G",
        contract_month="2027-02",
        expiration_date="2027-02-25",
        last_trading_date="2027-02-25",
        first_notice_date="2027-01-29",
        last_notice_date="2027-02-25",
        delivery_start_date="2027-02-01",
        delivery_end_date="2027-02-28",
        settlement_date="2027-02-25",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("100.0"),
        size_unit="troy ounces",
        quote_currency="USD",
        quote_unit="USD per troy oz",
        tick_size=Decimal("0.10"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("2701.20"),
        bid=Decimal("2700.90"),
        ask=Decimal("2701.50"),
        official_settlement=Decimal("2700.50"),
        previous_settlement=Decimal("2686.80"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=142000,
        open_interest=215000,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Silver (COMEX: SI) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("COMEX", "SIZ26"),
        product_entity_id=generate_futures_product_id("COMEX", "SI"),
        underlying_entity_id=generate_commodity_id("silver"),
        symbol="SIZ26",
        name="Silver Dec 2026",
        exchange="COMEX",
        exchange_mic="XCEC",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-29",
        last_trading_date="2026-12-29",
        first_notice_date="2026-11-30",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-12-29",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("5000.0"),
        size_unit="troy ounces",
        quote_currency="USD",
        quote_unit="USD per troy oz",
        tick_size=Decimal("0.005"),
        tick_value=Decimal("25.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("31.855"),
        bid=Decimal("31.850"),
        ask=Decimal("31.860"),
        official_settlement=Decimal("31.840"),
        previous_settlement=Decimal("31.420"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=89200,
        open_interest=142800,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Copper (COMEX: HG) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("COMEX", "HGZ26"),
        product_entity_id=generate_futures_product_id("COMEX", "HG"),
        underlying_entity_id=generate_commodity_id("copper"),
        symbol="HGZ26",
        name="Copper Dec 2026",
        exchange="COMEX",
        exchange_mic="XCEC",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-29",
        last_trading_date="2026-12-29",
        first_notice_date="2026-11-30",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-12-29",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("25000.0"),
        size_unit="pounds",
        quote_currency="USD",
        quote_unit="USD per pound",
        tick_size=Decimal("0.0005"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("4.3820"),
        bid=Decimal("4.3815"),
        ask=Decimal("4.3825"),
        official_settlement=Decimal("4.3810"),
        previous_settlement=Decimal("4.4150"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=62400,
        open_interest=98500,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Corn (CBOT: ZC) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CBOT", "ZCZ26"),
        product_entity_id=generate_futures_product_id("CBOT", "ZC"),
        underlying_entity_id=generate_commodity_id("corn"),
        symbol="ZCZ26",
        name="Corn Dec 2026",
        exchange="CBOT",
        exchange_mic="XCBT",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-14",
        last_trading_date="2026-12-14",
        first_notice_date="2026-11-30",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-12-14",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("426.50"),
        bid=Decimal("426.25"),
        ask=Decimal("426.75"),
        official_settlement=Decimal("426.25"),
        previous_settlement=Decimal("422.00"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=184500,
        open_interest=325100,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CBOT", "ZCH27"),
        product_entity_id=generate_futures_product_id("CBOT", "ZC"),
        underlying_entity_id=generate_commodity_id("corn"),
        symbol="ZCH27",
        name="Corn Mar 2027",
        exchange="CBOT",
        exchange_mic="XCBT",
        contract_year=2027,
        contract_month_code="H",
        contract_month="2027-03",
        expiration_date="2027-03-12",
        last_trading_date="2027-03-12",
        first_notice_date="2027-02-26",
        delivery_start_date="2027-03-01",
        delivery_end_date="2027-03-31",
        settlement_date="2027-03-12",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("438.75"),
        bid=Decimal("438.50"),
        ask=Decimal("439.00"),
        official_settlement=Decimal("438.50"),
        previous_settlement=Decimal("434.25"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=92100,
        open_interest=184500,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Soybeans (CBOT: ZS) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CBOT", "ZSF27"),
        product_entity_id=generate_futures_product_id("CBOT", "ZS"),
        underlying_entity_id=generate_commodity_id("soybeans"),
        symbol="ZSF27",
        name="Soybeans Jan 2027",
        exchange="CBOT",
        exchange_mic="XCBT",
        contract_year=2027,
        contract_month_code="F",
        contract_month="2027-01",
        expiration_date="2027-01-14",
        last_trading_date="2027-01-14",
        first_notice_date="2026-12-31",
        delivery_start_date="2027-01-02",
        delivery_end_date="2027-01-31",
        settlement_date="2027-01-14",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("1012.25"),
        bid=Decimal("1012.00"),
        ask=Decimal("1012.50"),
        official_settlement=Decimal("1011.75"),
        previous_settlement=Decimal("1004.50"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=124000,
        open_interest=218000,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Wheat (CBOT: ZW) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CBOT", "ZWZ26"),
        product_entity_id=generate_futures_product_id("CBOT", "ZW"),
        underlying_entity_id=generate_commodity_id("wheat"),
        symbol="ZWZ26",
        name="Wheat Dec 2026",
        exchange="CBOT",
        exchange_mic="XCBT",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-14",
        last_trading_date="2026-12-14",
        first_notice_date="2026-11-30",
        delivery_start_date="2026-12-01",
        delivery_end_date="2026-12-31",
        settlement_date="2026-12-14",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("5000.0"),
        size_unit="bushels",
        quote_currency="USD",
        quote_unit="US cents per bushel",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("588.50"),
        bid=Decimal("588.25"),
        ask=Decimal("588.75"),
        official_settlement=Decimal("588.00"),
        previous_settlement=Decimal("594.25"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=74200,
        open_interest=119000,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- Live Cattle (CME: LE) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CME", "LEZ26"),
        product_entity_id=generate_futures_product_id("CME", "LE"),
        underlying_entity_id=generate_commodity_id("live-cattle"),
        symbol="LEZ26",
        name="Live Cattle Dec 2026",
        exchange="CME",
        exchange_mic="XCME",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-31",
        last_trading_date="2026-12-31",
        first_notice_date="2026-12-07",
        delivery_start_date="2026-12-08",
        delivery_end_date="2027-01-05",
        settlement_date="2026-12-31",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("40000.0"),
        size_unit="pounds",
        quote_currency="USD",
        quote_unit="US cents per pound",
        tick_size=Decimal("0.025"),
        tick_value=Decimal("10.00"),
        settlement_type=SettlementTypeEnum.PHYSICAL,
        latest_trade_price=Decimal("187.425"),
        bid=Decimal("187.400"),
        ask=Decimal("187.450"),
        official_settlement=Decimal("187.375"),
        previous_settlement=Decimal("186.950"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=48300,
        open_interest=79400,
        open_interest_as_of="2026-10-14",
    ),
    # ---------------- E-mini S&P 500 (CME: ES) ----------------
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CME", "ESZ26"),
        product_entity_id=generate_futures_product_id("CME", "ES"),
        underlying_entity_id=generate_commodity_id("sp500-index"),
        symbol="ESZ26",
        name="E-mini S&P 500 Dec 2026",
        exchange="CME",
        exchange_mic="XCME",
        contract_year=2026,
        contract_month_code="Z",
        contract_month="2026-12",
        expiration_date="2026-12-18",
        last_trading_date="2026-12-18",
        settlement_date="2026-12-18",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("50.0"),
        size_unit="50 x Index",
        quote_currency="USD",
        quote_unit="Index points",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.CASH,
        contract_multiplier=Decimal("50.0"),
        latest_trade_price=Decimal("5872.25"),
        bid=Decimal("5872.00"),
        ask=Decimal("5872.50"),
        official_settlement=Decimal("5871.75"),
        previous_settlement=Decimal("5848.50"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=1480000,
        open_interest=2150000,
        open_interest_as_of="2026-10-14",
    ),
    CanonicalFuturesContractConfig(
        instrument_entity_id=generate_futures_contract_id("CME", "ESH27"),
        product_entity_id=generate_futures_product_id("CME", "ES"),
        underlying_entity_id=generate_commodity_id("sp500-index"),
        symbol="ESH27",
        name="E-mini S&P 500 Mar 2027",
        exchange="CME",
        exchange_mic="XCME",
        contract_year=2027,
        contract_month_code="H",
        contract_month="2027-03",
        expiration_date="2027-03-19",
        last_trading_date="2027-03-19",
        settlement_date="2027-03-19",
        lifecycle_status=ContractLifecycleEnum.ACTIVE,
        contract_size=Decimal("50.0"),
        size_unit="50 x Index",
        quote_currency="USD",
        quote_unit="Index points",
        tick_size=Decimal("0.25"),
        tick_value=Decimal("12.50"),
        settlement_type=SettlementTypeEnum.CASH,
        contract_multiplier=Decimal("50.0"),
        latest_trade_price=Decimal("5910.50"),
        bid=Decimal("5910.25"),
        ask=Decimal("5910.75"),
        official_settlement=Decimal("5909.50"),
        previous_settlement=Decimal("5886.00"),
        settlement_status=SettlementStatusEnum.FINAL,
        settlement_trade_date="2026-10-15",
        volume=380000,
        open_interest=780000,
        open_interest_as_of="2026-10-14",
    ),
]

FUTURES_CONTRACTS_BY_ID: Dict[UUID, CanonicalFuturesContractConfig] = {
    c.instrument_entity_id: c for c in CANONICAL_FUTURES_CONTRACTS
}


# ---------------------------------------------------------------------------
# Canonical Spot Benchmarks Catalog
# ---------------------------------------------------------------------------
CANONICAL_SPOT_BENCHMARKS: List[CommoditySpotBenchmarkConfig] = [
    CommoditySpotBenchmarkConfig(
        benchmark_entity_id=generate_spot_benchmark_id("wti-spot-cushing"),
        commodity_entity_id=generate_commodity_id("wti-crude-oil"),
        name="WTI Spot FOB Cushing",
        grade="Domestic Sweet Crude Oil (API 37-42°)",
        location="Cushing, Oklahoma, USA",
        currency="USD",
        quote_unit="USD per barrel",
        assessment_methodology="Daily physical pipeline transfer assessment",
        latest_price=Decimal("69.85"),
        previous_price=Decimal("70.50"),
        as_of_date="2026-10-15",
        provider="OPENBB",
    ),
    CommoditySpotBenchmarkConfig(
        benchmark_entity_id=generate_spot_benchmark_id("brent-dated-spot"),
        commodity_entity_id=generate_commodity_id("brent-crude-oil"),
        name="Brent Dated Spot",
        grade="North Sea Light Sweet Blend (BFOET)",
        location="Sullom Voe / North Sea, UK",
        currency="USD",
        quote_unit="USD per barrel",
        assessment_methodology="Platts / Argus Dated Brent physical cargo assessment",
        latest_price=Decimal("74.65"),
        previous_price=Decimal("75.30"),
        as_of_date="2026-10-15",
        provider="OPENBB",
    ),
    CommoditySpotBenchmarkConfig(
        benchmark_entity_id=generate_spot_benchmark_id("henry-hub-spot"),
        commodity_entity_id=generate_commodity_id("henry-hub-natural-gas"),
        name="Henry Hub Natural Gas Spot",
        grade="Pipeline dry gas (1,000 BTU/scf)",
        location="Erath, Louisiana, USA",
        currency="USD",
        quote_unit="USD per MMBtu",
        assessment_methodology="Next-day gas flow physical transaction index",
        latest_price=Decimal("2.985"),
        previous_price=Decimal("2.920"),
        as_of_date="2026-10-15",
        provider="OPENBB",
    ),
    CommoditySpotBenchmarkConfig(
        benchmark_entity_id=generate_spot_benchmark_id("gold-london-pm-fix"),
        commodity_entity_id=generate_commodity_id("gold"),
        name="LBMA Gold Price PM",
        grade="Loco London 0.995 fine gold",
        location="London Bullion Market, UK",
        currency="USD",
        quote_unit="USD per troy oz",
        assessment_methodology="Electronic auction overseen by ICE Benchmark Administration",
        latest_price=Decimal("2682.75"),
        previous_price=Decimal("2668.50"),
        as_of_date="2026-10-15",
        provider="OPENBB",
    ),
    CommoditySpotBenchmarkConfig(
        benchmark_entity_id=generate_spot_benchmark_id("silver-london-fix"),
        commodity_entity_id=generate_commodity_id("silver"),
        name="LBMA Silver Price",
        grade="Loco London 0.999 fine silver",
        location="London Bullion Market, UK",
        currency="USD",
        quote_unit="USD per troy oz",
        assessment_methodology="Electronic auction operated by CME Group / Thomson Reuters",
        latest_price=Decimal("31.780"),
        previous_price=Decimal("31.350"),
        as_of_date="2026-10-15",
        provider="OPENBB",
    ),
]

SPOT_BENCHMARKS_BY_ID: Dict[UUID, CommoditySpotBenchmarkConfig] = {
    b.benchmark_entity_id: b for b in CANONICAL_SPOT_BENCHMARKS
}
