"""ATLAS Portfolios V1 — Domain Models for Portfolio Allocation & Exposure (Stage 112)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from atlas.portfolios.exposure.enums import (
    AssetClass,
    ConcentrationScope,
    ExposureBasis,
    ExposureDataCompleteness,
    ExposureDimension,
    GeographyPolicy,
    LookThroughStatus,
    SectorTaxonomy,
)


@dataclass
class ExposureCategoryRow:
    """Aggregated allocation row for a specific category within an exposure dimension."""
    category_id: str
    category_name: str
    market_value: Decimal
    weight: Decimal
    percentage: Decimal
    direct_value: Decimal
    lookthrough_value: Decimal
    constituent_count: int
    coverage_status: str = "CLASSIFIED"
    subcategories: List[ExposureCategoryRow] = field(default_factory=list)

    @property
    def base_value(self) -> Decimal:
        return self.market_value

    @property
    def category_label(self) -> str:
        return self.category_name

    @property
    def position_count(self) -> int:
        return self.constituent_count

    @property
    def look_through_value(self) -> Decimal:
        return self.lookthrough_value

    @property
    def is_residual(self) -> bool:
        return self.category_id == "RESIDUAL_UNCLASSIFIED"

    @property
    def is_unclassified(self) -> bool:
        return "UNKNOWN" in self.category_id.upper()

    @property
    def parent_category_id(self) -> Optional[str]:
        return None


@dataclass
class ExposureDimensionResult:
    """Complete allocation result across a single aggregation dimension."""
    dimension: ExposureDimension
    taxonomy: str
    taxonomy_version: str
    total_market_value: Decimal
    classified_value: Decimal
    unclassified_value: Decimal
    coverage_percentage: Decimal
    categories: List[ExposureCategoryRow] = field(default_factory=list)

    @property
    def total_base_value(self) -> Decimal:
        return self.total_market_value

    @property
    def total_weight(self) -> Decimal:
        return (sum(c.weight for c in self.categories)).quantize(Decimal("0.000001"))

    @property
    def reconciled(self) -> bool:
        return abs(self.total_weight - Decimal("1.000000")) <= Decimal("0.001000")

    @property
    def reconciliation_discrepancy(self) -> Decimal:
        return abs(self.total_weight - Decimal("1.000000"))


@dataclass
class SecurityWeightItem:
    """Security-level holding with portfolio weight."""
    instrument_id: str
    symbol: str
    company_name: Optional[str]
    quantity: Decimal
    market_value: Decimal
    weight: Decimal
    percentage: Decimal
    currency: str
    account_ids: List[str] = field(default_factory=list)
    _direct_weight: Optional[Decimal] = None
    _look_through_weight: Optional[Decimal] = None
    _asset_class: str = "EQUITY"
    _rank: int = 1

    @property
    def base_value(self) -> Decimal:
        return self.market_value

    @property
    def name(self) -> str:
        return self.company_name or self.symbol

    @property
    def effective_shares(self) -> Decimal:
        return self.quantity

    @property
    def direct_weight(self) -> Decimal:
        return self._direct_weight if self._direct_weight is not None else self.weight

    @direct_weight.setter
    def direct_weight(self, val: Decimal) -> None:
        self._direct_weight = val

    @property
    def look_through_weight(self) -> Decimal:
        return self._look_through_weight if self._look_through_weight is not None else Decimal("0.000000")

    @look_through_weight.setter
    def look_through_weight(self, val: Decimal) -> None:
        self._look_through_weight = val

    @property
    def asset_class(self) -> str:
        return self._asset_class

    @asset_class.setter
    def asset_class(self, val: str) -> None:
        self._asset_class = val

    @property
    def rank(self) -> int:
        return self._rank

    @rank.setter
    def rank(self, val: int) -> None:
        self._rank = val


@dataclass
class IssuerWeightItem:
    """Consolidated economic issuer holding across instruments and accounts."""
    issuer_id: str
    issuer_name: str
    total_market_value: Decimal
    weight: Decimal
    percentage: Decimal
    instruments: List[str] = field(default_factory=list)
    symbols: List[str] = field(default_factory=list)
    account_ids: List[str] = field(default_factory=list)
    _country_code: str = "US"
    _rank: int = 1

    @property
    def base_value(self) -> Decimal:
        return self.total_market_value

    @property
    def constituent_instruments(self) -> List[str]:
        return self.instruments or self.symbols

    @property
    def country_code(self) -> str:
        return self._country_code

    @country_code.setter
    def country_code(self, val: str) -> None:
        self._country_code = val

    @property
    def rank(self) -> int:
        return self._rank

    @rank.setter
    def rank(self, val: int) -> None:
        self._rank = val


@dataclass
class ConcentrationSummary:
    """Portfolio concentration metrics and Herfindahl-Hirschman Index (HHI)."""
    scope: ConcentrationScope
    top_1_weight: Decimal
    top_3_weight: Decimal
    top_5_weight: Decimal
    top_10_weight: Decimal
    hhi: Decimal                 # Decimal fraction scale (0.0 to 1.0)
    hhi_conventional: Decimal    # Standard index scale (0 to 10,000)
    effective_n: Optional[Decimal]  # 1 / HHI
    holdings_count: int
    is_cash_included: bool
    top_20_weight: Optional[Decimal] = None

    @property
    def top1_weight(self) -> Decimal:
        return self.top_1_weight

    @property
    def top3_weight(self) -> Decimal:
        return self.top_3_weight

    @property
    def top5_weight(self) -> Decimal:
        return self.top_5_weight

    @property
    def top10_weight(self) -> Decimal:
        return self.top_10_weight

    @property
    def top20_weight(self) -> Decimal:
        return self.top_20_weight if self.top_20_weight is not None else self.top_10_weight

    @property
    def herfindahl_index(self) -> Decimal:
        return self.hhi

    @property
    def herfindahl_index_normalized(self) -> Decimal:
        return self.hhi_conventional

    @property
    def effective_number_of_holdings(self) -> Decimal:
        return self.effective_n or Decimal("0.0")

    @property
    def total_positions(self) -> int:
        return self.holdings_count

    @property
    def direct_holdings_count(self) -> int:
        return self.holdings_count

    @property
    def look_through_holdings_count(self) -> int:
        return 0


@dataclass
class FundConstituentItem:
    """Reported constituent holding within an ETF or mutual fund."""
    constituent_id: str
    symbol: str
    name: str
    weight_in_fund: Decimal
    effective_market_value: Decimal
    effective_weight_in_portfolio: Decimal
    asset_class: AssetClass
    sector: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None
    _parent_fund_id: str = ""

    @property
    def parent_fund_id(self) -> str:
        return self._parent_fund_id

    @parent_fund_id.setter
    def parent_fund_id(self, val: str) -> None:
        self._parent_fund_id = val

    @property
    def constituent_instrument_id(self) -> str:
        return self.constituent_id

    @property
    def constituent_symbol(self) -> str:
        return self.symbol

    @property
    def constituent_name(self) -> str:
        return self.name

    @property
    def constituent_weight_in_fund(self) -> Decimal:
        return self.weight_in_fund

    @property
    def effective_base_value(self) -> Decimal:
        return self.effective_market_value

    @property
    def effective_portfolio_weight(self) -> Decimal:
        return self.effective_weight_in_portfolio

    @property
    def constituent_asset_class(self) -> str:
        return self.asset_class.value if isinstance(self.asset_class, AssetClass) else str(self.asset_class)

    @property
    def constituent_sector(self) -> str:
        return self.sector or "Unknown Sector"

    @property
    def constituent_country(self) -> str:
        return self.country or "Unknown Country"

    @property
    def constituent_currency(self) -> str:
        return self.currency or "USD"

    @property
    def is_residual(self) -> bool:
        return self.constituent_id == "RESIDUAL_UNCLASSIFIED"


@dataclass
class FundLookThroughResult:
    """Look-through expansion breakdown for an individual fund."""
    fund_instrument_id: str
    fund_symbol: str
    fund_name: str
    fund_market_value: Decimal
    fund_weight_in_portfolio: Decimal
    holdings_as_of: datetime
    publication_date: Optional[datetime]
    source_provider: str
    status: LookThroughStatus
    known_constituents: List[FundConstituentItem] = field(default_factory=list)
    residual_market_value: Decimal = Decimal("0.00")
    residual_weight: Decimal = Decimal("0.00")
    coverage_percentage: Decimal = Decimal("100.00")

    @property
    def fund_base_value(self) -> Decimal:
        return self.fund_market_value

    @property
    def residual_base_value(self) -> Decimal:
        return self.residual_market_value

    @property
    def constituents(self) -> List[FundConstituentItem]:
        return self.known_constituents

    @property
    def coverage_ratio(self) -> Decimal:
        return self.coverage_percentage / Decimal("100.0")

    @property
    def as_of_date(self) -> date:
        return self.holdings_as_of.date() if isinstance(self.holdings_as_of, datetime) else self.holdings_as_of


@dataclass
class CrossFundOverlapItem:
    """Consolidated underlying security/issuer held across multiple funds or directly."""
    entity_id: str
    symbol: str
    name: str
    total_exposure_value: Decimal
    total_portfolio_weight: Decimal
    direct_value: Decimal
    direct_weight: Decimal
    fund_exposures: Dict[str, Decimal] = field(default_factory=dict)  # fund_symbol -> value

    @property
    def constituent_symbol(self) -> str:
        return self.symbol

    @property
    def constituent_name(self) -> str:
        return self.name

    @property
    def total_effective_weight(self) -> Decimal:
        return self.total_portfolio_weight

    @property
    def total_effective_value(self) -> Decimal:
        return self.total_exposure_value

    @property
    def funds_involved(self) -> List[str]:
        return list(self.fund_exposures.keys())

    @property
    def weights_by_fund(self) -> Dict[str, Decimal]:
        return {
            k: (v / self.total_exposure_value if self.total_exposure_value > Decimal("0") else Decimal("0.0"))
            for k, v in self.fund_exposures.items()
        }


@dataclass
class HistoricalAllocationPoint:
    """Historical composition snapshot at a discrete date."""
    as_of: datetime
    total_nav: Decimal
    dimension: ExposureDimension
    category_weights: Dict[str, Decimal] = field(default_factory=dict)
    category_values: Dict[str, Decimal] = field(default_factory=dict)
    _category_id: str = ""
    _category_label: str = ""
    _weight: Decimal = Decimal("0.000000")
    _base_value: Decimal = Decimal("0.00")
    _base_currency: str = "USD"

    @property
    def as_of_date(self) -> date:
        return self.as_of.date() if isinstance(self.as_of, datetime) else self.as_of

    @property
    def category_id(self) -> str:
        return self._category_id

    @category_id.setter
    def category_id(self, val: str) -> None:
        self._category_id = val

    @property
    def category_label(self) -> str:
        return self._category_label or self._category_id

    @category_label.setter
    def category_label(self, val: str) -> None:
        self._category_label = val

    @property
    def weight(self) -> Decimal:
        return self._weight

    @weight.setter
    def weight(self, val: Decimal) -> None:
        self._weight = val

    @property
    def base_value(self) -> Decimal:
        return self._base_value

    @base_value.setter
    def base_value(self, val: Decimal) -> None:
        self._base_value = val

    @property
    def base_currency(self) -> str:
        return self._base_currency

    @base_currency.setter
    def base_currency(self, val: str) -> None:
        self._base_currency = val


@dataclass
class AllocationChangeItem:
    """Change in category allocation between two historical dates."""
    category_id: str
    category_label: str
    start_weight: Decimal
    end_weight: Decimal
    weight_change_pct: Decimal
    start_value: Decimal
    end_value: Decimal
    value_change: Decimal
    dimension: ExposureDimension = ExposureDimension.ASSET_CLASS
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    weight_change_bps: int = 0

    @property
    def category_name(self) -> str:
        return self.category_label

    @property
    def change_percentage_points(self) -> Decimal:
        return self.weight_change_pct

    @property
    def change_value(self) -> Decimal:
        return self.value_change


@dataclass
class ExposureDataQuality:
    """Audit of data completeness, quote freshness, and classification coverage."""
    completeness: ExposureDataCompleteness
    total_nav: Decimal
    securities_value: Decimal
    cash_value: Decimal
    classified_value: Decimal
    unclassified_value: Decimal
    coverage_percentage: Decimal
    missing_prices_count: int
    missing_fx_count: int
    missing_classifications_count: int
    fund_lookthrough_residuals_count: int
    warnings: List[str] = field(default_factory=list)
    source_manifest: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_positions(self) -> int:
        return self.source_manifest.get("positions_count", 0)

    @property
    def classified_positions(self) -> int:
        return max(0, self.total_positions - self.missing_classifications_count)

    @property
    def unclassified_positions(self) -> int:
        return self.missing_classifications_count

    @property
    def classification_coverage_ratio(self) -> Decimal:
        return self.coverage_percentage / Decimal("100.0")

    @property
    def valuation_coverage_ratio(self) -> Decimal:
        return Decimal("1.000000") if self.missing_prices_count == 0 else Decimal("0.000000")

    @property
    def fx_coverage_ratio(self) -> Decimal:
        return Decimal("1.000000") if self.missing_fx_count == 0 else Decimal("0.000000")

    @property
    def errors(self) -> List[str]:
        return []

    @property
    def reconciled(self) -> bool:
        return True

    @property
    def reconciliation_discrepancy(self) -> Decimal:
        return Decimal("0.000000")


@dataclass
class PortfolioExposureRun:
    """Master immutable record of a portfolio allocation and exposure calculation run."""
    run_id: str
    portfolio_id: str
    account_id: Optional[str]
    owner_user_id: str
    as_of: datetime
    base_currency: str
    exposure_basis: ExposureBasis
    geography_policy: GeographyPolicy
    total_nav: Decimal
    securities_value: Decimal
    cash_value: Decimal
    asset_classes: ExposureDimensionResult
    sectors: ExposureDimensionResult
    industries: ExposureDimensionResult
    countries: ExposureDimensionResult
    currencies: ExposureDimensionResult
    security_concentration: ConcentrationSummary
    issuer_concentration: ConcentrationSummary
    top_securities: List[SecurityWeightItem] = field(default_factory=list)
    top_issuers: List[IssuerWeightItem] = field(default_factory=list)
    fund_lookthroughs: List[FundLookThroughResult] = field(default_factory=list)
    cross_fund_overlaps: List[CrossFundOverlapItem] = field(default_factory=list)
    data_quality: ExposureDataQuality = field(default_factory=lambda: ExposureDataQuality(
        completeness=ExposureDataCompleteness.EMPTY,
        total_nav=Decimal("0.00"),
        securities_value=Decimal("0.00"),
        cash_value=Decimal("0.00"),
        classified_value=Decimal("0.00"),
        unclassified_value=Decimal("0.00"),
        coverage_percentage=Decimal("0.00"),
        missing_prices_count=0,
        missing_fx_count=0,
        missing_classifications_count=0,
        fund_lookthrough_residuals_count=0,
    ))
    calculation_version: str = "1.0.0"
    input_hash: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def reconciled(self) -> bool:
        return (
            self.asset_classes.reconciled
            and self.sectors.reconciled
            and self.countries.reconciled
            and self.currencies.reconciled
        )

    @property
    def cash_weight(self) -> Decimal:
        if self.total_nav > Decimal("0"):
            return (self.cash_value / self.total_nav).quantize(Decimal("0.000001"))
        return Decimal("0.000000")

    @property
    def gross_exposure(self) -> Decimal:
        return self.total_nav

    @property
    def account_ids(self) -> List[str]:
        return [self.account_id] if self.account_id else []

    @property
    def as_of_date(self) -> date:
        return self.as_of.date() if isinstance(self.as_of, datetime) else self.as_of

    @property
    def calculated_at(self) -> datetime:
        return self.created_at

    @property
    def concentration(self) -> ConcentrationSummary:
        return self.security_concentration

    @property
    def security_weights(self) -> List[SecurityWeightItem]:
        return self.top_securities

    @property
    def issuer_weights(self) -> List[IssuerWeightItem]:
        return self.top_issuers

    @property
    def funds(self) -> List[FundLookThroughResult]:
        return self.fund_lookthroughs

    @property
    def cross_fund_overlap(self) -> List[CrossFundOverlapItem]:
        return self.cross_fund_overlaps

    @property
    def look_through_applied(self) -> bool:
        return self.exposure_basis == ExposureBasis.LOOK_THROUGH
