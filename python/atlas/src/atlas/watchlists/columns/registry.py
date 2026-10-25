"""Typed Column Registry for Watchlists V1 (Stage 77).

Defines stable column identifiers, versioned column definitions, source capabilities,
asset-class compatibility, formatting, and sorting policies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .errors import (
    ColumnLimitExceededError,
    ColumnNotFoundError,
    InvalidColumnOrderError,
    InvalidColumnWidthError,
    InvalidPinConfigurationError,
    RequiredColumnHiddenError,
)

MAX_VISIBLE_COLUMNS = 20
MAX_PINNED_COLUMNS = 5
REQUIRED_COLUMN_ID = "instrument.symbol"

ALL_ASSET_CLASSES = [
    "equity",
    "etf",
    "fund",
    "crypto",
    "currency",
    "fx",
    "bond",
    "future",
    "commodity",
    "index",
    "security",
]


@dataclass(frozen=True)
class WatchlistColumnDefinition:
    """Typed definition of an authorized watchlist financial column."""

    id: str
    version: int
    label: str
    description: str
    category: str  # "identity" | "market" | "quote" | "quality"
    value_type: (
        str  # "TEXT" | "IDENTIFIER" | "ENUM" | "MONETARY" | "PERCENTAGE" | "TIMESTAMP" | "STATUS"
    )
    source_capability: str
    supported_asset_classes: List[str] = field(default_factory=lambda: list(ALL_ASSET_CLASSES))
    formatter_id: str = "text"
    sort_policy: str = "alpha"  # "alpha" | "numeric" | "chronological" | "none"
    default_visible: bool = False
    default_width: int = 120
    min_width: int = 80
    max_width: int = 300
    can_hide: bool = True
    can_resize: bool = True
    can_pin: bool = False
    can_sort: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "label": self.label,
            "description": self.description,
            "category": self.category,
            "value_type": self.value_type,
            "source_capability": self.source_capability,
            "supported_asset_classes": self.supported_asset_classes,
            "formatter_id": self.formatter_id,
            "sort_policy": self.sort_policy,
            "default_visible": self.default_visible,
            "default_width": self.default_width,
            "min_width": self.min_width,
            "max_width": self.max_width,
            "can_hide": self.can_hide,
            "can_resize": self.can_resize,
            "can_pin": self.can_pin,
            "can_sort": self.can_sort,
        }


# =============================================================================
# Baseline Operational Column Catalog (14 Operational Columns)
# =============================================================================

COLUMN_CATALOG: List[WatchlistColumnDefinition] = [
    # Category 1: Instrument Identity
    WatchlistColumnDefinition(
        id="instrument.symbol",
        version=1,
        label="Symbol",
        description="Canonical financial instrument display symbol and ticker identifier.",
        category="identity",
        value_type="IDENTIFIER",
        source_capability="canonical_instrument",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="identifier",
        sort_policy="alpha",
        default_visible=True,
        default_width=130,
        min_width=90,
        max_width=260,
        can_hide=False,  # Required column - cannot be hidden
        can_resize=True,
        can_pin=True,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="instrument.name",
        version=1,
        label="Name",
        description="Verified canonical display name of the financial instrument or issuer.",
        category="identity",
        value_type="TEXT",
        source_capability="canonical_instrument",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=True,
        default_width=220,
        min_width=140,
        max_width=400,
        can_hide=True,
        can_resize=True,
        can_pin=True,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="instrument.asset_class",
        version=1,
        label="Asset Class",
        description="Canonical asset class (Equity, ETF, Fund, Crypto, FX, Bond, Futures).",
        category="identity",
        value_type="ENUM",
        source_capability="canonical_instrument",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="badge",
        sort_policy="alpha",
        default_visible=True,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="instrument.subtype",
        version=1,
        label="Subtype",
        description="Instrument subtype (Common Stock, Preferred, ADR, Spot, Sovereign).",
        category="identity",
        value_type="TEXT",
        source_capability="canonical_instrument",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="instrument.identifier",
        version=1,
        label="Identifier",
        description="Primary verified identifier (FIGI, ISIN, CUSIP, SEDOL, or exchange ticker).",
        category="identity",
        value_type="IDENTIFIER",
        source_capability="entity_identifiers",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="identifier",
        sort_policy="alpha",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=240,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    # Category 2: Trading Market
    WatchlistColumnDefinition(
        id="market.venue",
        version=1,
        label="Venue / Market",
        description="Primary listing exchange, OTC marketplace, or spot trading venue.",
        category="market",
        value_type="TEXT",
        source_capability="market_series",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=True,
        default_width=120,
        min_width=80,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="market.currency",
        version=1,
        label="Currency",
        description="ISO quotation currency or quote denomination (e.g. USD, EUR, INR, USDT).",
        category="market",
        value_type="TEXT",
        source_capability="market_series",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=False,
        default_width=100,
        min_width=70,
        max_width=150,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="market.listing_country",
        version=1,
        label="Country",
        description="ISO country code or operating jurisdiction of primary trading venue.",
        category="market",
        value_type="TEXT",
        source_capability="canonical_instrument",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=False,
        default_width=90,
        min_width=60,
        max_width=140,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    # Category 3: Available Quote Snapshot
    WatchlistColumnDefinition(
        id="quote.latest_measure",
        version=1,
        label="Latest Measure",
        description="Latest market observation (Last trade, indicative Mid, NAV, bond price).",
        category="quote",
        value_type="MONETARY",
        source_capability="latest_quote",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="price",
        sort_policy="numeric",
        default_visible=True,
        default_width=130,
        min_width=100,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="quote.change",
        version=1,
        label="Change",
        description="Net price change and percentage change relative to prior reference session.",
        category="quote",
        value_type="PERCENTAGE",
        source_capability="latest_quote",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="change",
        sort_policy="numeric",
        default_visible=True,
        default_width=130,
        min_width=100,
        max_width=220,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="quote.kind",
        version=1,
        label="Quote Kind",
        description="Measure classification (Last, Mid, Fixing, NAV, Clean Price, Yield).",
        category="quote",
        value_type="TEXT",
        source_capability="latest_quote",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="badge",
        sort_policy="alpha",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=160,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="quote.as_of",
        version=1,
        label="As Of",
        description="Exact UTC observation timestamp or official valuation date of quote snapshot.",
        category="quote",
        value_type="TIMESTAMP",
        source_capability="latest_quote",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="timestamp",
        sort_policy="chronological",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    # Category 4: Source and Data Quality
    WatchlistColumnDefinition(
        id="quality.freshness",
        version=1,
        label="Freshness",
        description="Freshness and delivery delay status (Fresh, Delayed 15m, Stale, Unavailable).",
        category="quality",
        value_type="STATUS",
        source_capability="freshness_monitor",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="status",
        sort_policy="alpha",
        default_visible=True,
        default_width=120,
        min_width=90,
        max_width=170,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="quality.source",
        version=1,
        label="Source",
        description="Authoritative upstream provider, marketplace, or valuation agent provenance.",
        category="quality",
        value_type="TEXT",
        source_capability="provenance",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    # =========================================================================
    # Stage 79: Enrichment Columns
    # =========================================================================
    # Category 5: Company Fundamentals
    WatchlistColumnDefinition(
        id="fundamentals.revenue",
        version=1,
        label="Revenue",
        description="Total top-line corporate revenue for the latest verified fiscal period.",
        category="fundamentals",
        value_type="MONETARY",
        source_capability="canonical_fundamental",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=250,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="fundamentals.net_income",
        version=1,
        label="Net Income",
        description="Consolidated net profit/loss attributable to shareholders for latest period.",
        category="fundamentals",
        value_type="MONETARY",
        source_capability="canonical_fundamental",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=250,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="fundamentals.eps",
        version=1,
        label="EPS (Diluted)",
        description="Diluted earnings per share for the latest verified period.",
        category="fundamentals",
        value_type="MONETARY",
        source_capability="canonical_fundamental",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=85,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="fundamentals.total_assets",
        version=1,
        label="Total Assets",
        description="Total economic assets reported on the latest verified balance sheet.",
        category="fundamentals",
        value_type="MONETARY",
        source_capability="canonical_fundamental",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=250,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="fundamentals.total_liabilities",
        version=1,
        label="Total Liabilities",
        description="Total corporate liabilities reported on the balance sheet.",
        category="fundamentals",
        value_type="MONETARY",
        source_capability="canonical_fundamental",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=250,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="fundamentals.total_equity",
        version=1,
        label="Stockholders' Equity",
        description="Total book value of shareholders' equity on balance sheet.",
        category="fundamentals",
        value_type="MONETARY",
        source_capability="canonical_fundamental",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=250,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),

    # Category 6: Valuation Ratios
    WatchlistColumnDefinition(
        id="valuation.market_cap",
        version=1,
        label="Market Cap",
        description="Total company market capitalization based on verified shares and price.",
        category="valuation",
        value_type="MONETARY",
        source_capability="valuation_ratios",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=140,
        min_width=100,
        max_width=250,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="valuation.pe_ratio",
        version=1,
        label="P/E Ratio",
        description="Price-to-Earnings ratio based on latest price and diluted EPS.",
        category="valuation",
        value_type="NUMBER",
        source_capability="valuation_ratios",
        supported_asset_classes=["equity"],
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="valuation.pb_ratio",
        version=1,
        label="P/B Ratio",
        description="Price-to-Book ratio comparing market cap to stockholders' equity.",
        category="valuation",
        value_type="NUMBER",
        source_capability="valuation_ratios",
        supported_asset_classes=["equity"],
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="valuation.ps_ratio",
        version=1,
        label="P/S Ratio",
        description="Price-to-Sales valuation ratio comparing market cap to annual revenue.",
        category="valuation",
        value_type="NUMBER",
        source_capability="valuation_ratios",
        supported_asset_classes=["equity"],
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="valuation.dividend_yield",
        version=1,
        label="Div Yield",
        description="Indicated dividend yield as a percentage of current share price.",
        category="valuation",
        value_type="PERCENTAGE",
        source_capability="valuation_ratios",
        supported_asset_classes=["equity", "etf", "fund"],
        formatter_id="percentage",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),

    # Category 7: Technical Indicators (1D Finalized Bars)
    WatchlistColumnDefinition(
        id="technical.sma_20_1d",
        version=1,
        label="SMA (20, 1D)",
        description="20-day Simple Moving Average calculated on finalized daily close prices.",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.sma_50_1d",
        version=1,
        label="SMA (50, 1D)",
        description="50-day Simple Moving Average calculated on finalized daily close prices.",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.ema_20_1d",
        version=1,
        label="EMA (20, 1D)",
        description="20-day Exponential Moving Average on finalized daily close prices.",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.ema_50_1d",
        version=1,
        label="EMA (50, 1D)",
        description="50-day Exponential Moving Average on finalized daily close prices.",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.rsi_14_1d",
        version=1,
        label="RSI (14, 1D)",
        description="14-period Relative Strength Index on daily finalized close bars.",
        category="technical",
        value_type="NUMBER",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.macd_line_1d",
        version=1,
        label="MACD (1D)",
        description="MACD line (12, 26) calculated from finalized daily close prices.",
        category="technical",
        value_type="NUMBER",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.macd_signal_1d",
        version=1,
        label="MACD Signal",
        description="9-period signal line of MACD on finalized daily close prices.",
        category="technical",
        value_type="NUMBER",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.macd_histogram_1d",
        version=1,
        label="MACD Hist",
        description="MACD histogram divergence between MACD line and signal line.",
        category="technical",
        value_type="NUMBER",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.bbands_upper_1d",
        version=1,
        label="BB Upper (20, 2)",
        description="Bollinger Bands upper band (20-period, 2 standard deviations).",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.bbands_middle_1d",
        version=1,
        label="BB Mid (20)",
        description="Bollinger Bands middle 20-period moving average band.",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.bbands_lower_1d",
        version=1,
        label="BB Lower (20, 2)",
        description="Bollinger Bands lower band (20-period, 2 standard deviations).",
        category="technical",
        value_type="MONETARY",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.atr_14_1d",
        version=1,
        label="ATR (14, 1D)",
        description="14-period Average True Range measuring market volatility.",
        category="technical",
        value_type="NUMBER",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=110,
        min_width=80,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="technical.obv_1d",
        version=1,
        label="OBV (1D)",
        description="On-Balance Volume snapshot requiring genuine compatible trading volume.",
        category="technical",
        value_type="NUMBER",
        source_capability="technical_indicators",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="number",
        sort_policy="numeric",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=220,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),

    # Category 8: Corporate Events
    WatchlistColumnDefinition(
        id="events.next_earnings_date",
        version=1,
        label="Next Earnings",
        description="Upcoming scheduled or estimated corporate earnings announcement date.",
        category="events",
        value_type="TIMESTAMP",
        source_capability="corporate_events",
        supported_asset_classes=["equity"],
        formatter_id="timestamp",
        sort_policy="chronological",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="events.last_earnings_date",
        version=1,
        label="Last Earnings",
        description="Date of the most recent prior earnings announcement.",
        category="events",
        value_type="TIMESTAMP",
        source_capability="corporate_events",
        supported_asset_classes=["equity"],
        formatter_id="timestamp",
        sort_policy="chronological",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="events.next_ex_dividend_date",
        version=1,
        label="Next Ex-Div",
        description="Upcoming ex-dividend cutoff date for distribution entitlement.",
        category="events",
        value_type="TIMESTAMP",
        source_capability="corporate_events",
        supported_asset_classes=["equity", "etf", "fund"],
        formatter_id="timestamp",
        sort_policy="chronological",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="events.dividend_payment_date",
        version=1,
        label="Div Pay Date",
        description="Scheduled dividend distribution payment date.",
        category="events",
        value_type="TIMESTAMP",
        source_capability="corporate_events",
        supported_asset_classes=["equity", "etf", "fund"],
        formatter_id="timestamp",
        sort_policy="chronological",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),

    # Category 9: Earnings Metadata
    WatchlistColumnDefinition(
        id="earnings.reported_eps",
        version=1,
        label="Reported EPS",
        description="Official reported diluted EPS for the most recent earnings report.",
        category="earnings",
        value_type="MONETARY",
        source_capability="earnings_metadata",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=85,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="earnings.estimated_eps",
        version=1,
        label="Est EPS",
        description="Consensus earnings estimate EPS prior to the announcement date.",
        category="earnings",
        value_type="MONETARY",
        source_capability="earnings_metadata",
        supported_asset_classes=["equity"],
        formatter_id="monetary",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=85,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="earnings.eps_surprise_pct",
        version=1,
        label="EPS Surprise",
        description=(
            "Percentage earnings surprise between actual reported EPS and consensus estimate."
        ),
        category="earnings",
        value_type="PERCENTAGE",
        source_capability="earnings_metadata",
        supported_asset_classes=["equity"],
        formatter_id="percentage",
        sort_policy="numeric",
        default_visible=False,
        default_width=120,
        min_width=85,
        max_width=180,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),

    # Category 10: Canonical News References
    WatchlistColumnDefinition(
        id="news.latest_headline",
        version=1,
        label="Headline",
        description="Most recent verified news headline associated with this canonical entity.",
        category="news",
        value_type="TEXT",
        source_capability="canonical_news",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=False,
        default_width=240,
        min_width=140,
        max_width=450,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="news.latest_publication_time",
        version=1,
        label="News Time",
        description="Original publication timestamp of the most recent relevant news article.",
        category="news",
        value_type="TIMESTAMP",
        source_capability="canonical_news",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="timestamp",
        sort_policy="chronological",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
    WatchlistColumnDefinition(
        id="news.publisher",
        version=1,
        label="Publisher",
        description="Attributed journalistic publisher or authorized disclosure source.",
        category="news",
        value_type="TEXT",
        source_capability="canonical_news",
        supported_asset_classes=ALL_ASSET_CLASSES,
        formatter_id="text",
        sort_policy="alpha",
        default_visible=False,
        default_width=130,
        min_width=90,
        max_width=200,
        can_hide=True,
        can_resize=True,
        can_pin=False,
        can_sort=True,
    ),
]

COLUMN_MAP: Dict[str, WatchlistColumnDefinition] = {col.id: col for col in COLUMN_CATALOG}
COLUMN_REGISTRY: Dict[str, WatchlistColumnDefinition] = COLUMN_MAP

WatchlistColumnCategory = str
WatchlistColumnValueType = str


def get_column_definition(column_id: str) -> Optional[WatchlistColumnDefinition]:
    """Retrieves definition for given column ID or None if not registered."""
    return COLUMN_MAP.get(column_id)


def list_column_definitions() -> List[WatchlistColumnDefinition]:
    """Returns all 14 authorized operational column definitions."""
    return list(COLUMN_CATALOG)


list_all_column_definitions = list_column_definitions


def get_default_column_config() -> dict:
    """Returns canonical default column configuration for a new watchlist."""
    visible_cols = [c.id for c in COLUMN_CATALOG if c.default_visible]
    # Default ordering places default visible columns first, followed by available optional columns
    ordered_cols = visible_cols + [c.id for c in COLUMN_CATALOG if not c.default_visible]
    widths = {c.id: c.default_width for c in COLUMN_CATALOG}

    return {
        "schema_version": 1,
        "ordered_column_ids": ordered_cols,
        "visible_column_ids": visible_cols,
        "widths": widths,
        "pinned_left_column_ids": [REQUIRED_COLUMN_ID],
        "sort": {"column_id": None, "direction": None},
    }


def normalize_and_validate_column_config(config_dict: dict) -> dict:
    """
    Validates and normalizes column configuration against the Column Registry.
    Guarantees:
    - schema_version == 1
    - REQUIRED_COLUMN_ID is present in ordered_column_ids and visible_column_ids
    - All column IDs exist in COLUMN_MAP (no unknown IDs)
    - No duplicate IDs in ordered_column_ids or visible_column_ids
    - visible_column_ids <= MAX_VISIBLE_COLUMNS (20)
    - pinned_left_column_ids <= MAX_PINNED_COLUMNS (5) and columns have can_pin == True
    - Widths are clamped to [min_width, max_width] bounds
    - Sort parameters are validated against sort_policy
    """
    if not isinstance(config_dict, dict):
        raise InvalidColumnOrderError("Configuration payload must be an object.")

    # 1. Check schema_version
    schema_ver = config_dict.get("schema_version", 1)
    if schema_ver != 1:
        from .errors import UnsupportedConfigVersionError

        raise UnsupportedConfigVersionError(f"Unsupported schema version: {schema_ver}")

    # 2. Validate ordered_column_ids
    ordered_ids = config_dict.get("ordered_column_ids")
    if not isinstance(ordered_ids, list):
        raise InvalidColumnOrderError("ordered_column_ids must be a list of column ID strings.")

    # Check for duplicates & unknown IDs
    seen_ordered = set()
    for col_id in ordered_ids:
        if not isinstance(col_id, str):
            raise InvalidColumnOrderError("All column IDs must be strings.")
        if col_id not in COLUMN_MAP:
            raise ColumnNotFoundError(f"Column '{col_id}' is not in the Column Registry.")
        if col_id in seen_ordered:
            raise InvalidColumnOrderError(f"Duplicate column ID in ordering: '{col_id}'.")
        seen_ordered.add(col_id)

    # Ensure REQUIRED_COLUMN_ID is present in ordering
    if REQUIRED_COLUMN_ID not in seen_ordered:
        ordered_ids.insert(0, REQUIRED_COLUMN_ID)
        seen_ordered.add(REQUIRED_COLUMN_ID)

    # Append any catalog columns missing from ordered_ids
    for cat_col in COLUMN_CATALOG:
        if cat_col.id not in seen_ordered:
            ordered_ids.append(cat_col.id)
            seen_ordered.add(cat_col.id)

    # 3. Validate visible_column_ids
    visible_ids = config_dict.get("visible_column_ids")
    if not isinstance(visible_ids, list):
        raise InvalidColumnOrderError("visible_column_ids must be a list of column ID strings.")

    seen_visible = set()
    for col_id in visible_ids:
        if not isinstance(col_id, str):
            raise InvalidColumnOrderError("All visible column IDs must be strings.")
        if col_id not in COLUMN_MAP:
            raise ColumnNotFoundError(f"Visible column '{col_id}' is not registered.")
        if col_id in seen_visible:
            raise InvalidColumnOrderError(f"Duplicate column ID in visible list: '{col_id}'.")
        seen_visible.add(col_id)

    # Required column must NEVER be hidden
    if REQUIRED_COLUMN_ID not in seen_visible:
        raise RequiredColumnHiddenError(
            f"Mandatory column '{REQUIRED_COLUMN_ID}' cannot be hidden."
        )

    # Bounded visible column limit (max 20)
    if len(visible_ids) > MAX_VISIBLE_COLUMNS:
        raise ColumnLimitExceededError(
            f"Visible column count ({len(visible_ids)}) exceeds limit ({MAX_VISIBLE_COLUMNS})."
        )

    # 4. Validate pinned_left_column_ids
    pinned_ids = config_dict.get("pinned_left_column_ids", [REQUIRED_COLUMN_ID])
    if not isinstance(pinned_ids, list):
        raise InvalidPinConfigurationError("pinned_left_column_ids must be a list.")

    if len(pinned_ids) > MAX_PINNED_COLUMNS:
        raise InvalidPinConfigurationError(
            f"Pinned column count ({len(pinned_ids)}) exceeds maximum limit ({MAX_PINNED_COLUMNS})."
        )

    validated_pinned = []
    seen_pinned = set()
    for p_id in pinned_ids:
        if p_id not in COLUMN_MAP:
            raise ColumnNotFoundError(f"Pinned column '{p_id}' is not registered.")
        col_def = COLUMN_MAP[p_id]
        if not col_def.can_pin:
            raise InvalidPinConfigurationError(f"Column '{p_id}' cannot be pinned.")
        if p_id not in seen_visible:
            # Pinned column must be visible
            continue
        if p_id not in seen_pinned:
            validated_pinned.append(p_id)
            seen_pinned.add(p_id)

    # Ensure required symbol column is pinned if it's pinnable and wasn't specified
    if (
        REQUIRED_COLUMN_ID in seen_visible
        and REQUIRED_COLUMN_ID not in seen_pinned
        and len(validated_pinned) < MAX_PINNED_COLUMNS
    ):
        validated_pinned.insert(0, REQUIRED_COLUMN_ID)

    # 5. Validate widths
    raw_widths = config_dict.get("widths", {})
    if not isinstance(raw_widths, dict):
        raise InvalidColumnWidthError(
            "widths must be a dictionary mapping column ID to pixel width."
        )

    normalized_widths = {}
    for col_def in COLUMN_CATALOG:
        user_w = raw_widths.get(col_def.id, col_def.default_width)
        if not isinstance(user_w, (int, float)):
            user_w = col_def.default_width
        user_w = int(user_w)
        # Clamp to bounds
        clamped_w = max(col_def.min_width, min(user_w, col_def.max_width))
        normalized_widths[col_def.id] = clamped_w

    # 6. Validate sort config
    raw_sort = config_dict.get("sort", {})
    sort_col = raw_sort.get("column_id") if isinstance(raw_sort, dict) else None
    sort_dir = raw_sort.get("direction") if isinstance(raw_sort, dict) else None

    normalized_sort = {"column_id": None, "direction": None}
    if sort_col is not None:
        if sort_col not in COLUMN_MAP:
            raise ColumnNotFoundError(f"Sort target column '{sort_col}' is not registered.")
        target_def = COLUMN_MAP[sort_col]
        if not target_def.can_sort or target_def.sort_policy == "none":
            from .errors import ColumnNotSortableError

            raise ColumnNotSortableError(f"Column '{sort_col}' does not support sorting.")
        if sort_dir not in ("asc", "desc"):
            sort_dir = "asc"
        normalized_sort = {"column_id": sort_col, "direction": sort_dir}

    return {
        "schema_version": 1,
        "ordered_column_ids": ordered_ids,
        "visible_column_ids": visible_ids,
        "widths": normalized_widths,
        "pinned_left_column_ids": validated_pinned,
        "sort": normalized_sort,
    }
