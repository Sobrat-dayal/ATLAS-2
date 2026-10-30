"""ATLAS Portfolios V1 — Brinson Performance Attribution Engine (Stage 113).

Implements single-period Brinson-Fachler (BF) and Brinson-Hood-Beebower (BHB)
arithmetic attribution decompositions, with mathematical validation against
the Part XVII (+2.20 percentage points) and Part XVIII reference fixtures.
"""

from decimal import Decimal
from typing import Dict, List, Tuple

from atlas.portfolios.attribution.enums import AttributionMethod
from atlas.portfolios.attribution.models import AttributionCategoryResult


class BrinsonEngine:
    """Calculates single-period Brinson-Fachler and Brinson-Hood-Beebower attribution."""

    @staticmethod
    def calculate_category_attribution(
        category_id: str,
        category_label: str,
        portfolio_weight: Decimal,
        benchmark_weight: Decimal,
        portfolio_return: Decimal,
        benchmark_return: Decimal,
        total_benchmark_return: Decimal,
        method: AttributionMethod = AttributionMethod.BRINSON_FACHLER,
    ) -> AttributionCategoryResult:
        """Calculates allocation, selection, and interaction effects for a single category."""
        w_p = portfolio_weight
        w_b = benchmark_weight
        r_p = portfolio_return
        r_b = benchmark_return
        r_b_total = total_benchmark_return

        # Handle absent category edge cases with documented institutional conventions
        is_absent_in_portfolio = (w_p == Decimal("0.000000"))
        is_absent_in_benchmark = (w_b == Decimal("0.000000"))

        if is_absent_in_portfolio and not is_absent_in_benchmark:
            # Category in benchmark but 0% held in portfolio:
            # Investor made no active stock selection within this sector, so Selection = 0, Interaction = 0.
            # Allocation effect captures the deliberate zero-weighting.
            if method == AttributionMethod.BRINSON_FACHLER:
                alloc = (w_p - w_b) * (r_b - r_b_total)
            else:
                alloc = (w_p - w_b) * r_b
            select = Decimal("0.000000")
            inter = Decimal("0.000000")
            total = alloc

        elif is_absent_in_benchmark and not is_absent_in_portfolio:
            # Off-benchmark category held in portfolio (e.g. Cash or unbenchmarked asset class):
            # Benchmark sector return defaults to benchmark total return (r_b = r_b_total).
            # Allocation effect relative to benchmark total is 0; active return flows to interaction/selection.
            if method == AttributionMethod.BRINSON_FACHLER:
                alloc = (w_p - w_b) * (r_b_total - r_b_total)  # = 0.0
            else:
                alloc = (w_p - w_b) * r_b_total
            select = Decimal("0.000000")
            inter = (w_p - w_b) * (r_p - r_b_total)
            total = alloc + select + inter

        else:
            # Standard category present in both (or standard formula application)
            if method == AttributionMethod.BRINSON_FACHLER:
                # A_i = (w_P,i - w_B,i) * (R_B,i - R_B)
                alloc = (w_p - w_b) * (r_b - r_b_total)
            else:
                # A_i^BHB = (w_P,i - w_B,i) * R_B,i
                alloc = (w_p - w_b) * r_b

            # S_i = w_B,i * (R_P,i - R_B,i)
            select = w_b * (r_p - r_b)

            # I_i = (w_P,i - w_B,i) * (R_P,i - R_B,i)
            inter = (w_p - w_b) * (r_p - r_b)

            total = alloc + select + inter

        return AttributionCategoryResult(
            category_id=category_id,
            category_label=category_label,
            portfolio_weight=w_p,
            benchmark_weight=w_b,
            portfolio_return=r_p,
            benchmark_return=r_b,
            allocation_effect=alloc,
            selection_effect=select,
            interaction_effect=inter,
            total_effect=total,
        )

    def decompose(
        self,
        portfolio_groups: Dict[str, Tuple[Decimal, Decimal]],  # category_id -> (weight, return)
        benchmark_groups: Dict[str, Tuple[Decimal, Decimal]],  # category_id -> (weight, return)
        category_labels: Dict[str, str],
        total_portfolio_return: Decimal,
        total_benchmark_return: Decimal,
        method: AttributionMethod = AttributionMethod.BRINSON_FACHLER,
    ) -> List[AttributionCategoryResult]:
        """Performs full decomposition across all mutually inclusive category keys."""
        all_keys = set(portfolio_groups.keys()).union(set(benchmark_groups.keys()))
        results: List[AttributionCategoryResult] = []

        # Sort keys deterministically
        sorted_keys = sorted(list(all_keys))

        for key in sorted_keys:
            p_weight, p_return = portfolio_groups.get(key, (Decimal("0.000000"), total_benchmark_return))
            b_weight, b_return = benchmark_groups.get(key, (Decimal("0.000000"), total_benchmark_return))
            label = category_labels.get(key, key.replace("_", " ").title())

            cat_result = self.calculate_category_attribution(
                category_id=key,
                category_label=label,
                portfolio_weight=p_weight,
                benchmark_weight=b_weight,
                portfolio_return=p_return,
                benchmark_return=b_return,
                total_benchmark_return=total_benchmark_return,
                method=method,
            )
            results.append(cat_result)

        return results

