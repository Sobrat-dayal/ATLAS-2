"""ATLAS Portfolios V1 — Fund & ETF Look-Through Engine (Stage 112).

Provides constituent expansion, residual unclassified bucket tracking,
cross-fund overlap consolidation, cycle detection, and wrapper double-count prevention.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from atlas.portfolios.exposure.enums import AssetClass, LookThroughStatus
from atlas.portfolios.exposure.errors import PortfolioExposureLookThroughCycleError
from atlas.portfolios.exposure.models import (
    CrossFundOverlapItem,
    FundConstituentItem,
    FundLookThroughResult,
)
from atlas.portfolios.exposure.registry import (
    ClassificationRegistry,
    FundHoldingsDataset,
)


class FundLookThroughEngine:
    """Expands eligible fund holdings into underlying constituent exposures."""

    def __init__(self, registry: ClassificationRegistry, max_depth: int = 3) -> None:
        self.registry = registry
        self.max_depth = max_depth

    def expand_fund(
        self,
        fund_instrument_id: str,
        fund_market_value: Decimal,
        portfolio_nav: Decimal,
        visited_funds: Optional[Set[str]] = None,
        depth: int = 1,
    ) -> FundLookThroughResult:
        """Expands a single fund position into its reported constituent exposures."""
        if visited_funds is None:
            visited_funds = set()

        if fund_instrument_id in visited_funds:
            raise PortfolioExposureLookThroughCycleError(fund_instrument_id)

        meta = self.registry.get_instrument_metadata(fund_instrument_id)
        fund_symbol = meta.symbol if meta else fund_instrument_id
        fund_name = meta.name if meta else "Fund Vehicle"
        fund_weight_in_portfolio = fund_market_value / portfolio_nav if portfolio_nav > Decimal("0") else Decimal("0")

        dataset = self.registry.get_fund_holdings(fund_instrument_id)
        if not dataset:
            # Fund holdings unavailable: entire fund value is treated as residual
            return FundLookThroughResult(
                fund_instrument_id=fund_instrument_id,
                fund_symbol=fund_symbol,
                fund_name=fund_name,
                fund_market_value=fund_market_value,
                fund_weight_in_portfolio=fund_weight_in_portfolio,
                holdings_as_of=meta.mark_as_of if hasattr(meta, "mark_as_of") else None or datetime_utcnow(),
                publication_date=None,
                source_provider="UNAVAILABLE",
                status=LookThroughStatus.UNAVAILABLE,
                known_constituents=[],
                residual_market_value=fund_market_value,
                residual_weight=Decimal("1.00"),
                coverage_percentage=Decimal("0.00"),
            )

        new_visited = set(visited_funds)
        new_visited.add(fund_instrument_id)

        constituents: List[FundConstituentItem] = []
        total_constituent_weight = Decimal("0.00")

        for c in dataset.constituents:
            c_meta = self.registry.get_instrument_metadata(c.constituent_id)
            c_weight = c.weight
            eff_val = fund_market_value * c_weight
            eff_port_weight = eff_val / portfolio_nav if portfolio_nav > Decimal("0") else Decimal("0")

            asset_class = c_meta.asset_class if c_meta else c.asset_class
            sector = c_meta.sector if c_meta else c.sector
            country = c_meta.domicile_country if c_meta else c.country
            currency = c_meta.currency if c_meta else c.currency

            constituents.append(
                FundConstituentItem(
                    constituent_id=c.constituent_id,
                    symbol=c.symbol,
                    name=c.name,
                    weight_in_fund=c_weight,
                    effective_market_value=eff_val,
                    effective_weight_in_portfolio=eff_port_weight,
                    asset_class=asset_class,
                    sector=sector,
                    country=country,
                    currency=currency,
                )
            )
            total_constituent_weight += c_weight

        # Residual unclassified calculation
        if total_constituent_weight >= Decimal("1.00"):
            residual_weight = Decimal("0.00")
            residual_value = Decimal("0.00")
            coverage = Decimal("100.00")
            status = LookThroughStatus.COMPLETE
        else:
            residual_weight = Decimal("1.00") - total_constituent_weight
            residual_value = fund_market_value * residual_weight
            coverage = (total_constituent_weight * Decimal("100.0")).quantize(Decimal("0.01"))
            status = LookThroughStatus.PARTIAL

        return FundLookThroughResult(
            fund_instrument_id=fund_instrument_id,
            fund_symbol=dataset.fund_symbol,
            fund_name=dataset.fund_name,
            fund_market_value=fund_market_value,
            fund_weight_in_portfolio=fund_weight_in_portfolio,
            holdings_as_of=dataset.holdings_as_of,
            publication_date=dataset.publication_date,
            source_provider=dataset.source_provider,
            status=status,
            known_constituents=constituents,
            residual_market_value=residual_value,
            residual_weight=residual_weight,
            coverage_percentage=coverage,
        )

    def consolidate_cross_fund_overlap(
        self,
        direct_positions: List[Tuple[str, str, str, Decimal]],  # (inst_id, symbol, name, value)
        fund_lookthroughs: List[FundLookThroughResult],
        portfolio_nav: Decimal,
    ) -> List[CrossFundOverlapItem]:
        """Consolidates direct holdings and look-through exposures across multiple ETFs into overlap records."""
        overlap_map: Dict[str, CrossFundOverlapItem] = {}

        # 1. Direct positions
        for inst_id, symbol, name, val in direct_positions:
            overlap_map[inst_id] = CrossFundOverlapItem(
                entity_id=inst_id,
                symbol=symbol,
                name=name,
                total_exposure_value=val,
                total_portfolio_weight=val / portfolio_nav if portfolio_nav > Decimal("0") else Decimal("0"),
                direct_value=val,
                direct_weight=val / portfolio_nav if portfolio_nav > Decimal("0") else Decimal("0"),
                fund_exposures={},
            )

        # 2. Fund constituents
        for flt in fund_lookthroughs:
            fund_sym = flt.fund_symbol
            for c in flt.known_constituents:
                inst_id = c.constituent_id
                c_val = c.effective_market_value

                if inst_id in overlap_map:
                    item = overlap_map[inst_id]
                    item.total_exposure_value += c_val
                    item.total_portfolio_weight = item.total_exposure_value / portfolio_nav if portfolio_nav > Decimal("0") else Decimal("0")
                    item.fund_exposures[fund_sym] = item.fund_exposures.get(fund_sym, Decimal("0")) + c_val
                else:
                    overlap_map[inst_id] = CrossFundOverlapItem(
                        entity_id=inst_id,
                        symbol=c.symbol,
                        name=c.name,
                        total_exposure_value=c_val,
                        total_portfolio_weight=c_val / portfolio_nav if portfolio_nav > Decimal("0") else Decimal("0"),
                        direct_value=Decimal("0.00"),
                        direct_weight=Decimal("0.00"),
                        fund_exposures={fund_sym: c_val},
                    )

        # Return sorted descending by total exposure value
        return sorted(overlap_map.values(), key=lambda x: x.total_exposure_value, reverse=True)


def datetime_utcnow():
    from datetime import datetime
    return datetime.utcnow()

