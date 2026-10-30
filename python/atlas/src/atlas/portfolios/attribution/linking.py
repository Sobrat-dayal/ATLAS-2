"""ATLAS Portfolios V1 — Multi-Period Attribution Linking Engine (Stage 113).

Implements Carino's logarithmic linking methodology to compound single-period
arithmetic attribution effects across multiple historical periods, preserving
exact reconciliation: sum(A_linked + S_linked + I_linked) = R_P_cum - R_B_cum.
"""

import math
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from atlas.portfolios.attribution.enums import MultiPeriodLinkingMethod
from atlas.portfolios.attribution.errors import PortfolioAttributionMultiPeriodLinkingError
from atlas.portfolios.attribution.models import (
    AttributionCategoryResult,
    HistoricalPeriodAttribution,
    MultiPeriodLinkedAttribution,
)


class MultiPeriodLinkingEngine:
    """Compounds single-period attribution effects into multi-period results via Carino's formula."""

    @staticmethod
    def _calculate_period_coefficient(r_p: Decimal, r_b: Decimal) -> Decimal:
        """Calculates Carino coefficient k_t = (ln(1 + R_P) - ln(1 + R_B)) / (R_P - R_B)."""
        r_p_float = float(r_p)
        r_b_float = float(r_b)

        # Domain guardrail: gross return must be positive
        if (1.0 + r_p_float) <= 0.0 or (1.0 + r_b_float) <= 0.0:
            raise PortfolioAttributionMultiPeriodLinkingError(
                f"Gross returns must be positive for Carino linking: 1+R_P={1.0+r_p_float}, 1+R_B={1.0+r_b_float}"
            )

        diff = r_p_float - r_b_float
        if abs(diff) < 1e-7:
            # Limiting case as R_P -> R_B: k = 1 / (1 + R_P)
            coeff = 1.0 / (1.0 + r_p_float)
        else:
            coeff = (math.log(1.0 + r_p_float) - math.log(1.0 + r_b_float)) / diff

        return Decimal(str(coeff))

    def link_periods(
        self,
        periods: List[HistoricalPeriodAttribution],
        period_category_effects: List[List[AttributionCategoryResult]],
        method: MultiPeriodLinkingMethod = MultiPeriodLinkingMethod.CARINO,
    ) -> MultiPeriodLinkedAttribution:
        """Links single-period attribution results into cumulative multi-period attribution."""
        if not periods:
            return MultiPeriodLinkedAttribution(
                linking_method=method,
                cumulative_portfolio_return=Decimal("0.000000"),
                cumulative_benchmark_return=Decimal("0.000000"),
                cumulative_active_return=Decimal("0.000000"),
                total_allocation_effect=Decimal("0.000000"),
                total_selection_effect=Decimal("0.000000"),
                total_interaction_effect=Decimal("0.000000"),
                total_attributed=Decimal("0.000000"),
                reconciliation_residual=Decimal("0.000000"),
                category_results=[],
                periods=[],
            )

        # Step 1: Compute cumulative geometrically compounded returns
        cum_p_factor = 1.0
        cum_b_factor = 1.0
        for p in periods:
            cum_p_factor *= (1.0 + float(p.portfolio_return))
            cum_b_factor *= (1.0 + float(p.benchmark_return))

        cum_r_p = Decimal(str(cum_p_factor - 1.0))
        cum_r_b = Decimal(str(cum_b_factor - 1.0))
        cum_r_a = cum_r_p - cum_r_b

        # Step 2: Calculate cumulative scaling coefficient K
        cum_k = self._calculate_period_coefficient(cum_r_p, cum_r_b)

        # Step 3: Calculate scaling factor s_t = k_t / K for each subperiod
        subperiod_factors: List[Decimal] = []
        for p in periods:
            k_t = self._calculate_period_coefficient(p.portfolio_return, p.benchmark_return)
            s_t = k_t / cum_k
            subperiod_factors.append(s_t)

        # Step 4: Scale and aggregate effects across periods for each category
        category_linked: Dict[str, Dict[str, Any]] = {}

        for p_idx, cat_results in enumerate(period_category_effects):
            s_t = subperiod_factors[p_idx]
            for c in cat_results:
                if c.category_id not in category_linked:
                    category_linked[c.category_id] = {
                        "category_label": c.category_label,
                        "portfolio_weight": Decimal("0.000000"),
                        "benchmark_weight": Decimal("0.000000"),
                        "portfolio_return": Decimal("0.000000"),
                        "benchmark_return": Decimal("0.000000"),
                        "allocation_effect": Decimal("0.000000"),
                        "selection_effect": Decimal("0.000000"),
                        "interaction_effect": Decimal("0.000000"),
                        "total_effect": Decimal("0.000000"),
                        "count": 0,
                    }
                entry = category_linked[c.category_id]
                entry["portfolio_weight"] += c.portfolio_weight
                entry["benchmark_weight"] += c.benchmark_weight
                entry["portfolio_return"] += c.portfolio_return
                entry["benchmark_return"] += c.benchmark_return
                entry["allocation_effect"] += (c.allocation_effect * s_t)
                entry["selection_effect"] += (c.selection_effect * s_t)
                entry["interaction_effect"] += (c.interaction_effect * s_t)
                entry["total_effect"] += (c.total_effect * s_t)
                entry["count"] += 1

        num_periods = len(periods)
        linked_cat_results: List[AttributionCategoryResult] = []
        total_alloc = Decimal("0.000000")
        total_select = Decimal("0.000000")
        total_inter = Decimal("0.000000")

        for cat_id, data in sorted(category_linked.items()):
            # Average weights and returns across periods for display
            avg_w_p = data["portfolio_weight"] / Decimal(str(num_periods))
            avg_w_b = data["benchmark_weight"] / Decimal(str(num_periods))
            avg_r_p = data["portfolio_return"] / Decimal(str(num_periods))
            avg_r_b = data["benchmark_return"] / Decimal(str(num_periods))

            alloc = data["allocation_effect"]
            select = data["selection_effect"]
            inter = data["interaction_effect"]
            tot = alloc + select + inter

            total_alloc += alloc
            total_select += select
            total_inter += inter

            linked_cat_results.append(
                AttributionCategoryResult(
                    category_id=cat_id,
                    category_label=data["category_label"],
                    portfolio_weight=avg_w_p,
                    benchmark_weight=avg_w_b,
                    portfolio_return=avg_r_p,
                    benchmark_return=avg_r_b,
                    allocation_effect=alloc,
                    selection_effect=select,
                    interaction_effect=inter,
                    total_effect=tot,
                )
            )

        total_attributed = total_alloc + total_select + total_inter
        residual = cum_r_a - total_attributed

        return MultiPeriodLinkedAttribution(
            linking_method=method,
            cumulative_portfolio_return=cum_r_p,
            cumulative_benchmark_return=cum_r_b,
            cumulative_active_return=cum_r_a,
            total_allocation_effect=total_alloc,
            total_selection_effect=total_select,
            total_interaction_effect=total_inter,
            total_attributed=total_attributed,
            reconciliation_residual=residual,
            category_results=linked_cat_results,
            periods=periods,
        )
