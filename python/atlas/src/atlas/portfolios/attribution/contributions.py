"""ATLAS Portfolios V1 — Security Return Contribution Engine (Stage 113).

Calculates security-level return contributions (C_j = w_P,j * R_P,j),
ranks Top Contributors and Detractors, and aggregates contributions to
higher-level sector and industry partitions with full reconciliation to R_P.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from atlas.portfolios.attribution.models import SecurityContributionItem


class SecurityContributionEngine:
    """Calculates and ranks instrument-level return contributions."""

    @staticmethod
    def calculate_contribution(
        instrument_id: str,
        symbol: str,
        name: str,
        beginning_weight: Decimal,
        holding_period_return: Decimal,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        currency: str = "USD",
        is_sold: bool = False,
    ) -> SecurityContributionItem:
        """Calculates single-security return contribution: C_j = w_P,j * R_P,j."""
        contribution = beginning_weight * holding_period_return
        return SecurityContributionItem(
            instrument_id=instrument_id,
            symbol=symbol,
            name=name,
            weight=beginning_weight,
            security_return=holding_period_return,
            contribution=contribution,
            sector=sector,
            industry=industry,
            currency=currency,
            is_sold=is_sold,
        )

    def compute_all_contributions(
        self,
        security_records: List[Tuple[str, str, str, Decimal, Decimal, Optional[str], Optional[str], str, bool]],
        # Tuples of (instrument_id, symbol, name, weight, return, sector, industry, currency, is_sold)
    ) -> Tuple[List[SecurityContributionItem], List[SecurityContributionItem], List[SecurityContributionItem]]:
        """Computes all contributions, sorted items, Top 5 Contributors, and Top 5 Detractors."""
        items: List[SecurityContributionItem] = []

        for rec in security_records:
            inst_id, sym, name, weight, ret, sec, ind, curr, is_sold = rec
            item = self.calculate_contribution(
                instrument_id=inst_id,
                symbol=sym,
                name=name,
                beginning_weight=weight,
                holding_period_return=ret,
                sector=sec,
                industry=ind,
                currency=curr,
                is_sold=is_sold,
            )
            items.append(item)

        # Sort all by contribution descending
        items_sorted = sorted(items, key=lambda x: x.contribution, reverse=True)

        # Top 5 Contributors (most positive contribution)
        top_contributors = [x for x in items_sorted if x.contribution > Decimal("0.000000")][:5]
        if not top_contributors and items_sorted:
            top_contributors = items_sorted[:min(5, len(items_sorted))]

        # Top 5 Detractors (most negative contribution)
        items_by_detractor = sorted(items, key=lambda x: x.contribution)
        top_detractors = [x for x in items_by_detractor if x.contribution < Decimal("0.000000")][:5]
        if not top_detractors and items_by_detractor:
            top_detractors = items_by_detractor[:min(5, len(items_by_detractor))]

        return items_sorted, top_contributors, top_detractors

    @staticmethod
    def aggregate_by_dimension(
        contributions: List[SecurityContributionItem],
        dimension_attr: str = "sector",
    ) -> Dict[str, Decimal]:
        """Aggregates security contributions to sector or industry groups."""
        agg: Dict[str, Decimal] = {}
        for c in contributions:
            key = getattr(c, dimension_attr, None) or "unclassified"
            agg[key] = agg.get(key, Decimal("0.000000")) + c.contribution
        return agg

