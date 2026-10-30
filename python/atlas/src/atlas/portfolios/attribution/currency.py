"""ATLAS Portfolios V1 — Currency Effect Attribution Engine (Stage 113).

Decomposes foreign currency investment returns into:
1. Local Market Return: R_local
2. Currency Translation Return: R_FX
3. Local/FX Interaction Cross-Term: R_local * R_FX
Reconciling exactly to 1 + R_base = (1 + R_local) * (1 + R_FX),
validated against the Part XXXVI (+23.75%) reference fixture.
"""

from decimal import Decimal
from typing import List, Tuple

from atlas.portfolios.attribution.models import CurrencyEffectItem


class CurrencyAttributionEngine:
    """Calculates currency translation decomposition and local/FX interaction effects."""

    @staticmethod
    def decompose_currency_return(
        currency: str,
        portfolio_weight: Decimal,
        local_return: Decimal,
        fx_start_rate: Decimal,  # Base per local (e.g. 80.0 INR/USD)
        fx_end_rate: Decimal,    # Base per local (e.g. 90.0 INR/USD)
    ) -> CurrencyEffectItem:
        """Decomposes a foreign currency position's return into local, FX, and cross-term."""
        if fx_start_rate <= Decimal("0.000000"):
            fx_return = Decimal("0.000000")
        else:
            # R_FX = (S_end - S_start) / S_start
            fx_return = (fx_end_rate - fx_start_rate) / fx_start_rate

        # Interaction = R_local * R_FX
        interaction = local_return * fx_return

        # R_base = R_local + R_FX + Interaction
        base_return = local_return + fx_return + interaction

        # Contribution = Weight * R_base
        contribution = portfolio_weight * base_return

        return CurrencyEffectItem(
            currency=currency,
            weight=portfolio_weight,
            local_return=local_return,
            fx_return=fx_return,
            interaction_return=interaction,
            base_currency_return=base_return,
            contribution_to_base=contribution,
        )

    def decompose_all_currencies(
        self,
        currency_records: List[Tuple[str, Decimal, Decimal, Decimal, Decimal]],
        # Tuples of (currency, weight, local_return, fx_start, fx_end)
    ) -> List[CurrencyEffectItem]:
        """Calculates currency decomposition across all held denomination currencies."""
        items: List[CurrencyEffectItem] = []
        for rec in currency_records:
            curr, weight, local_ret, fx_s, fx_e = rec
            item = self.decompose_currency_return(
                currency=curr,
                portfolio_weight=weight,
                local_return=local_ret,
                fx_start_rate=fx_s,
                fx_end_rate=fx_e,
            )
            items.append(item)
        return items

