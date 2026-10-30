"""ATLAS Portfolios V1 — Optimization Rebalancing & Turnover Engine (Stage 114).

Computes hypothetical allocation deltas, one-way and gross turnover,
transaction costs, and funding reconciliation without mutating actual accounts.
"""

from decimal import Decimal
import logging
from typing import Dict, List, Optional, Tuple

from atlas.portfolios.exposure.registry import get_instrument_classification
from atlas.portfolios.optimization.models import CurrentVsCandidateItem

logger = logging.getLogger("atlas.portfolios.optimization.rebalancing")


class RebalancingEngine:
    """Computes hypothetical portfolio rebalancing transactions and cost implications."""

    def compute_comparisons(
        self,
        symbols: List[str],
        current_weights: Dict[str, Decimal],
        candidate_weights: Dict[str, Decimal],
        portfolio_nav: Decimal,
        proportional_cost_rate: Decimal = Decimal("0.0010"),  # 10 bps default
    ) -> Tuple[List[CurrentVsCandidateItem], Decimal, Decimal]:
        """Compares current vs candidate weights.

        Returns (items, one_way_turnover, total_estimated_cost).
        """
        all_symbols = sorted(list(set(symbols) | set(current_weights.keys()) | set(candidate_weights.keys())))
        items: List[CurrentVsCandidateItem] = []

        gross_turnover = Decimal("0.0")
        total_cost = Decimal("0.0")

        for s in all_symbols:
            w_curr = current_weights.get(s, Decimal("0.0"))
            w_cand = candidate_weights.get(s, Decimal("0.0"))
            delta_w = w_cand - w_curr

            curr_val = portfolio_nav * w_curr
            cand_val = portfolio_nav * w_cand
            trade_val = portfolio_nav * delta_w

            if delta_w > Decimal("0.0001"):
                direction = "BUY"
            elif delta_w < Decimal("-0.0001"):
                direction = "SELL"
            else:
                direction = "HOLD"

            abs_delta = abs(delta_w)
            gross_turnover += abs_delta

            # Exclude CASH asset from standard trading brokerage costs unless FX conversion
            if s != "CASH":
                cost = (portfolio_nav * abs_delta) * proportional_cost_rate
            else:
                cost = Decimal("0.00")
            total_cost += cost

            meta = get_instrument_classification(s)
            name = meta.name if meta else s
            sector = meta.sector if meta else ("Cash & Equivalents" if s == "CASH" else "Unclassified")
            cat_id = sector.lower().replace(" ", "_")

            items.append(
                CurrentVsCandidateItem(
                    symbol=s,
                    name=name,
                    category_id=cat_id,
                    category_label=sector,
                    current_weight=w_curr,
                    candidate_weight=w_cand,
                    weight_delta=delta_w,
                    current_value=curr_val,
                    candidate_value=cand_val,
                    trade_value_delta=trade_val,
                    trade_direction=direction,
                    estimated_cost=cost,
                )
            )

        one_way_turnover = gross_turnover / Decimal("2.0")

        # Sort items: largest absolute trade delta first
        items.sort(key=lambda item: abs(item.trade_value_delta), reverse=True)

        return items, one_way_turnover, total_cost

    def compute_rebalancing(
        self,
        current_weights: Dict[str, Decimal],
        candidate_weights: Dict[str, Decimal],
        nav: Decimal,
        proportional_cost_rate: Decimal = Decimal("0.0010"),
    ) -> Tuple[Decimal, Decimal, List[CurrentVsCandidateItem]]:
        """Convenience wrapper returning (turnover, cost, items)."""
        symbols = list(set(current_weights.keys()) | set(candidate_weights.keys()))
        items, turnover, cost = self.compute_comparisons(
            symbols=symbols,
            current_weights=current_weights,
            candidate_weights=candidate_weights,
            portfolio_nav=nav,
            proportional_cost_rate=proportional_cost_rate,
        )
        return turnover, cost, items
