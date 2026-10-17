"""Configuration, Universe Definitions, and Metric Policies for ATLAS Market Movers V1 (Stage 63).

Defines canonical mover universes, comparison windows, metric policies,
and qualification exclusion enums according to institutional ranking integrity standards.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class MoverCategory(str, Enum):
    """Supported market mover ranking categories."""

    GAINERS = "gainers"
    LOSERS = "losers"
    MOST_ACTIVE = "most_active"


class MoverAssetClass(str, Enum):
    """Financial asset class scopes."""

    EQUITY = "equity"
    CRYPTO = "crypto"
    FUTURES = "futures"
    FX = "fx"
    BOND = "bond"


class ComparisonWindow(str, Enum):
    """Qualified market comparison windows."""

    PREVIOUS_REGULAR_SESSION = "previous_regular_session"
    ROLLING_24H = "rolling_24h"
    CURRENT_SESSION = "current_session"
    PREVIOUS_SESSION_SETTLEMENT = "previous_session_settlement"


class ExclusionReason(str, Enum):
    """Institutional exclusion reasons explaining why an instrument was not ranked."""

    NO_CURRENT_QUOTE = "NO_CURRENT_QUOTE"
    NO_REFERENCE = "NO_REFERENCE"
    STALE_CURRENT = "STALE_CURRENT"
    UNKNOWN_FRESHNESS = "UNKNOWN_FRESHNESS"
    INCOMPATIBLE_SERIES = "INCOMPATIBLE_SERIES"
    INCOMPATIBLE_UNIT = "INCOMPATIBLE_UNIT"
    INCOMPATIBLE_WINDOW = "INCOMPATIBLE_WINDOW"
    UNVERIFIED_ADJUSTMENT = "UNVERIFIED_ADJUSTMENT"
    INVALID_DENOMINATOR = "INVALID_DENOMINATOR"
    MISSING_VOLUME = "MISSING_VOLUME"
    INVALID_ACTIVITY_SCOPE = "INVALID_ACTIVITY_SCOPE"
    INSTRUMENT_INACTIVE = "INSTRUMENT_INACTIVE"
    NOT_ENTITLED = "NOT_ENTITLED"
    DATA_SOURCE_UNAVAILABLE = "DATA_SOURCE_UNAVAILABLE"
    OTHER = "OTHER"


class CoverageStatus(str, Enum):
    """Institutional ranking coverage status for the defined universe."""

    COMPLETE_FOR_DEFINED_UNIVERSE = "COMPLETE_FOR_DEFINED_UNIVERSE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


# ---------------------------------------------------------------------------
# Universe and Metric Definition Models
# ---------------------------------------------------------------------------
class MoverUniverseDefinition(BaseModel):
    """Specification of an authoritative, authorized candidate security universe."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    universe_id: str = Field(..., min_length=2, max_length=64)
    display_name: str = Field(..., min_length=2, max_length=128)
    asset_class: MoverAssetClass
    instrument_types: List[str]
    market_scope: str
    exchange_scope: List[str]
    listing_currency_scope: List[str]
    eligibility_policy: str
    metric_policy: str
    data_entitlement_policy: str
    supported_categories: List[MoverCategory]
    supported_windows: List[ComparisonWindow]
    default_window: ComparisonWindow
    activity_unit: Optional[str] = None
    activity_metric_label: Optional[str] = None
    is_active: bool = True


class MoverMetricDefinition(BaseModel):
    """Specification of a typed financial ranking metric."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric_id: str
    metric_kind: MoverCategory
    asset_class: MoverAssetClass
    observation_basis: str
    reference_basis: str
    window: ComparisonWindow
    unit: str
    sort_direction: str  # "DESC" or "ASC"
    qualification_policy: str


# ---------------------------------------------------------------------------
# Authoritative Supported Universes
# ---------------------------------------------------------------------------
SUPPORTED_MOVER_UNIVERSES: List[MoverUniverseDefinition] = [
    MoverUniverseDefinition(
        universe_id="univ_us_equities",
        display_name="Covered US Equities",
        asset_class=MoverAssetClass.EQUITY,
        instrument_types=["common_stock", "preferred_stock", "depositary_receipt"],
        market_scope="US",
        exchange_scope=["XNAS", "XNYS", "BATS"],
        listing_currency_scope=["USD"],
        eligibility_policy="Active listed US equities with verified prior regular session close.",
        metric_policy=(
            "Percentage and absolute price movement relative to official previous close; "
            "session share volume."
        ),
        data_entitlement_policy="Public and subscriber market data entitlement (Stage 14).",
        supported_categories=[
            MoverCategory.GAINERS,
            MoverCategory.LOSERS,
            MoverCategory.MOST_ACTIVE,
        ],
        supported_windows=[
            ComparisonWindow.PREVIOUS_REGULAR_SESSION,
            ComparisonWindow.CURRENT_SESSION,
        ],
        default_window=ComparisonWindow.PREVIOUS_REGULAR_SESSION,
        activity_unit="shares",
        activity_metric_label="Session Shares Traded",
    ),
    MoverUniverseDefinition(
        universe_id="univ_crypto_spot",
        display_name="Supported Cryptocurrency Spot Markets",
        asset_class=MoverAssetClass.CRYPTO,
        instrument_types=["spot_pair"],
        market_scope="GLOBAL_CRYPTO",
        exchange_scope=["BINANCE", "COINBASE", "KRAKEN"],
        listing_currency_scope=["USDT", "USD"],
        eligibility_policy="Supported digital asset spot pairs with active 24h rolling price feed.",
        metric_policy=(
            "Rolling 24-hour price change percentage; 24h quote volume denominated in USDT."
        ),
        data_entitlement_policy="Standard cryptocurrency market data entitlement.",
        supported_categories=[
            MoverCategory.GAINERS,
            MoverCategory.LOSERS,
            MoverCategory.MOST_ACTIVE,
        ],
        supported_windows=[ComparisonWindow.ROLLING_24H],
        default_window=ComparisonWindow.ROLLING_24H,
        activity_unit="USDT",
        activity_metric_label="24h Quote Turnover (USDT)",
    ),
    MoverUniverseDefinition(
        universe_id="univ_futures",
        display_name="Supported Futures Contracts",
        asset_class=MoverAssetClass.FUTURES,
        instrument_types=["futures_contract"],
        market_scope="COMMODITIES_DERIVATIVES",
        exchange_scope=["NYMEX", "COMEX", "CBOT", "CME", "ICE"],
        listing_currency_scope=["USD"],
        eligibility_policy=(
            "Unexpired exchange-traded commodity futures contracts with prior daily settlement."
        ),
        metric_policy=(
            "Price change relative to prior official settlement; "
            "trading volume in executed contracts."
        ),
        data_entitlement_policy="Exchange-entitled derivatives market feed.",
        supported_categories=[
            MoverCategory.GAINERS,
            MoverCategory.LOSERS,
            MoverCategory.MOST_ACTIVE,
        ],
        supported_windows=[
            ComparisonWindow.PREVIOUS_SESSION_SETTLEMENT,
            ComparisonWindow.CURRENT_SESSION,
        ],
        default_window=ComparisonWindow.PREVIOUS_SESSION_SETTLEMENT,
        activity_unit="contracts",
        activity_metric_label="Session Contracts Traded",
    ),
]

MOVER_UNIVERSES_BY_ID: Dict[str, MoverUniverseDefinition] = {
    u.universe_id: u for u in SUPPORTED_MOVER_UNIVERSES
}

DEFAULT_MOVER_UNIVERSE_ID = "univ_us_equities"
