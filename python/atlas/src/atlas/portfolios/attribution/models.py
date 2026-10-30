"""ATLAS Portfolios V1 — Performance Attribution Domain Models (Stage 113).

Domain entities for Brinson-Fachler, Brinson-Hood-Beebower, Security Return
Contributions, Multi-Period Carino Linking, Currency Effects, and Reconciliation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from atlas.portfolios.attribution.enums import (
    AttributionCompleteness,
    AttributionDimension,
    AttributionMethod,
    MultiPeriodLinkingMethod,
    ReconciliationStatus,
)


@dataclass
class AttributionCategoryResult:
    """Attribution results for a single partition category (e.g., GICS Sector or Industry)."""
    category_id: str
    category_label: str
    portfolio_weight: Decimal  # w_P,i
    benchmark_weight: Decimal  # w_B,i
    portfolio_return: Decimal  # R_P,i
    benchmark_return: Decimal  # R_B,i
    allocation_effect: Decimal  # A_i
    selection_effect: Decimal   # S_i
    interaction_effect: Decimal # I_i
    total_effect: Decimal       # E_i = A_i + S_i + I_i
    sub_industries: Optional[List["AttributionCategoryResult"]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category_id": self.category_id,
            "category_label": self.category_label,
            "portfolio_weight": str(self.portfolio_weight),
            "benchmark_weight": str(self.benchmark_weight),
            "portfolio_return": str(self.portfolio_return),
            "benchmark_return": str(self.benchmark_return),
            "allocation_effect": str(self.allocation_effect),
            "selection_effect": str(self.selection_effect),
            "interaction_effect": str(self.interaction_effect),
            "total_effect": str(self.total_effect),
            "sub_industries": [s.to_dict() for s in self.sub_industries] if self.sub_industries else None,
        }


@dataclass
class SecurityContributionItem:
    """Return contribution of an individual financial instrument to portfolio return."""
    instrument_id: str
    symbol: str
    name: str
    weight: Decimal          # Beginning portfolio weight w_P,j
    security_return: Decimal # Holding period total return R_P,j
    contribution: Decimal    # Return contribution C_j = w_P,j * R_P,j
    sector: Optional[str] = None
    industry: Optional[str] = None
    currency: str = "USD"
    is_sold: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "name": self.name,
            "weight": str(self.weight),
            "security_return": str(self.security_return),
            "contribution": str(self.contribution),
            "sector": self.sector,
            "industry": self.industry,
            "currency": self.currency,
            "is_sold": self.is_sold,
        }


@dataclass
class CurrencyEffectItem:
    """Decomposition of foreign denomination asset return into local, FX, and interaction."""
    currency: str
    weight: Decimal
    local_return: Decimal
    fx_return: Decimal
    interaction_return: Decimal
    base_currency_return: Decimal
    contribution_to_base: Decimal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "currency": self.currency,
            "weight": str(self.weight),
            "local_return": str(self.local_return),
            "fx_return": str(self.fx_return),
            "interaction_return": str(self.interaction_return),
            "base_currency_return": str(self.base_currency_return),
            "contribution_to_base": str(self.contribution_to_base),
        }


@dataclass
class HistoricalPeriodAttribution:
    """Single discrete historical period (e.g. monthly) attribution result."""
    period_label: str
    period_start: datetime
    period_end: datetime
    portfolio_return: Decimal
    benchmark_return: Decimal
    active_return: Decimal
    allocation_effect: Decimal
    selection_effect: Decimal
    interaction_effect: Decimal
    total_attributed: Decimal
    residual: Decimal
    category_effects: Dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_label": self.period_label,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "portfolio_return": str(self.portfolio_return),
            "benchmark_return": str(self.benchmark_return),
            "active_return": str(self.active_return),
            "allocation_effect": str(self.allocation_effect),
            "selection_effect": str(self.selection_effect),
            "interaction_effect": str(self.interaction_effect),
            "total_attributed": str(self.total_attributed),
            "residual": str(self.residual),
            "category_effects": {k: str(v) for k, v in self.category_effects.items()},
        }


@dataclass
class MultiPeriodLinkedAttribution:
    """Multi-period attribution linked using Carino's exact logarithmic methodology."""
    linking_method: MultiPeriodLinkingMethod
    cumulative_portfolio_return: Decimal
    cumulative_benchmark_return: Decimal
    cumulative_active_return: Decimal
    total_allocation_effect: Decimal
    total_selection_effect: Decimal
    total_interaction_effect: Decimal
    total_attributed: Decimal
    reconciliation_residual: Decimal
    category_results: List[AttributionCategoryResult]
    periods: List[HistoricalPeriodAttribution]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "linking_method": self.linking_method.value,
            "cumulative_portfolio_return": str(self.cumulative_portfolio_return),
            "cumulative_benchmark_return": str(self.cumulative_benchmark_return),
            "cumulative_active_return": str(self.cumulative_active_return),
            "total_allocation_effect": str(self.total_allocation_effect),
            "total_selection_effect": str(self.total_selection_effect),
            "total_interaction_effect": str(self.total_interaction_effect),
            "total_attributed": str(self.total_attributed),
            "reconciliation_residual": str(self.reconciliation_residual),
            "category_results": [c.to_dict() for c in self.category_results],
            "periods": [p.to_dict() for p in self.periods],
        }


@dataclass
class AttributionReconciliation:
    """Mathematical audit verification for attribution decomposition."""
    portfolio_return: Decimal
    reconstructed_portfolio_return: Decimal
    portfolio_return_reconciled: bool
    benchmark_return: Decimal
    reconstructed_benchmark_return: Decimal
    benchmark_return_reconciled: bool
    active_return: Decimal
    total_attributed: Decimal
    attribution_reconciled: bool
    residual: Decimal
    security_contributions_sum: Decimal
    security_contributions_reconciled: bool
    status: ReconciliationStatus
    tolerance: Decimal = Decimal("0.0001")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "portfolio_return": str(self.portfolio_return),
            "reconstructed_portfolio_return": str(self.reconstructed_portfolio_return),
            "portfolio_return_reconciled": self.portfolio_return_reconciled,
            "benchmark_return": str(self.benchmark_return),
            "reconstructed_benchmark_return": str(self.reconstructed_benchmark_return),
            "benchmark_return_reconciled": self.benchmark_return_reconciled,
            "active_return": str(self.active_return),
            "total_attributed": str(self.total_attributed),
            "attribution_reconciled": self.attribution_reconciled,
            "residual": str(self.residual),
            "security_contributions_sum": str(self.security_contributions_sum),
            "security_contributions_reconciled": self.security_contributions_reconciled,
            "status": self.status.value,
            "tolerance": str(self.tolerance),
        }


@dataclass
class AttributionDataQuality:
    """Data completeness, taxonomy coverage, and cryptographic provenance."""
    completeness: AttributionCompleteness
    portfolio_holdings_coverage_ratio: Decimal
    benchmark_constituent_coverage_ratio: Decimal
    taxonomy_coverage_ratio: Decimal
    missing_securities_count: int
    unmapped_sector_weight: Decimal
    input_hash: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "completeness": self.completeness.value,
            "portfolio_holdings_coverage_ratio": str(self.portfolio_holdings_coverage_ratio),
            "benchmark_constituent_coverage_ratio": str(self.benchmark_constituent_coverage_ratio),
            "taxonomy_coverage_ratio": str(self.taxonomy_coverage_ratio),
            "missing_securities_count": self.missing_securities_count,
            "unmapped_sector_weight": str(self.unmapped_sector_weight),
            "input_hash": self.input_hash,
            "warnings": self.warnings,
        }


@dataclass
class PortfolioAttributionRun:
    """Comprehensive performance attribution run execution record."""
    id: str
    portfolio_id: str
    account_id: Optional[str]
    benchmark_id: str
    benchmark_name: str
    period_start: datetime
    period_end: datetime
    reporting_currency: str
    attribution_method: AttributionMethod
    methodology_version: str
    classification_dimension: AttributionDimension
    taxonomy_id: str
    taxonomy_version: str
    portfolio_return: Decimal
    benchmark_return: Decimal
    active_return: Decimal
    total_allocation_effect: Decimal
    total_selection_effect: Decimal
    total_interaction_effect: Decimal
    total_attributed: Decimal
    reconciliation_residual: Decimal
    category_results: List[AttributionCategoryResult]
    security_contributions: List[SecurityContributionItem]
    top_contributors: List[SecurityContributionItem]
    top_detractors: List[SecurityContributionItem]
    currency_effects: List[CurrencyEffectItem]
    reconciliation: AttributionReconciliation
    data_quality: AttributionDataQuality
    multi_period: Optional[MultiPeriodLinkedAttribution] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "account_id": self.account_id,
            "benchmark_id": self.benchmark_id,
            "benchmark_name": self.benchmark_name,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "reporting_currency": self.reporting_currency,
            "attribution_method": self.attribution_method.value,
            "methodology_version": self.methodology_version,
            "classification_dimension": self.classification_dimension.value,
            "taxonomy_id": self.taxonomy_id,
            "taxonomy_version": self.taxonomy_version,
            "portfolio_return": str(self.portfolio_return),
            "benchmark_return": str(self.benchmark_return),
            "active_return": str(self.active_return),
            "total_allocation_effect": str(self.total_allocation_effect),
            "total_selection_effect": str(self.total_selection_effect),
            "total_interaction_effect": str(self.total_interaction_effect),
            "total_attributed": str(self.total_attributed),
            "reconciliation_residual": str(self.reconciliation_residual),
            "category_results": [c.to_dict() for c in self.category_results],
            "security_contributions": [s.to_dict() for s in self.security_contributions],
            "top_contributors": [s.to_dict() for s in self.top_contributors],
            "top_detractors": [s.to_dict() for s in self.top_detractors],
            "currency_effects": [c.to_dict() for c in self.currency_effects],
            "reconciliation": self.reconciliation.to_dict(),
            "data_quality": self.data_quality.to_dict(),
            "multi_period": self.multi_period.to_dict() if self.multi_period else None,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
        }

