"""Pricing Engine Factory for QuantLib (Stage 142)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import QuantLib as ql
from atlas.options.domain import ExerciseStyle
from atlas.options.quant.domain import PricingModelFamily
from atlas.options.quant.errors import QuantModelIncompatibleError


class QuantLibEngineFactory:
    """Factory creating appropriate QuantLib pricing engines based on model family and exercise style."""

    @staticmethod
    def create_vanilla_engine(
        model_family: PricingModelFamily,
        process: ql.BlackScholesMertonProcess,
        exercise_style: ExerciseStyle,
        dividend_schedule: Optional[List[ql.FixedDividend]] = None,
        numerical_steps: int = 100,
    ) -> ql.PricingEngine:
        """Create a QuantLib pricing engine for a vanilla option contract."""
        if exercise_style == ExerciseStyle.EUROPEAN:
            if model_family == PricingModelFamily.BLACK_SCHOLES_MERTON:
                return ql.AnalyticEuropeanEngine(process)
            elif model_family == PricingModelFamily.BINOMIAL_CRR:
                return ql.BinomialCRRVanillaEngine(process, numerical_steps)
            elif model_family == PricingModelFamily.FINITE_DIFFERENCE:
                if dividend_schedule:
                    return ql.FdBlackScholesVanillaEngine(process, dividend_schedule, numerical_steps, numerical_steps)
                return ql.FdBlackScholesVanillaEngine(process, numerical_steps, numerical_steps)
            else:
                # Default European to analytic
                return ql.AnalyticEuropeanEngine(process)

        elif exercise_style == ExerciseStyle.AMERICAN:
            if model_family == PricingModelFamily.BARONE_ADESI_WHALEY:
                return ql.BaroneAdesiWhaleyApproximationEngine(process)
            elif model_family == PricingModelFamily.BJERKSUND_STENSLAND:
                return ql.BjerksundStenslandApproximationEngine(process)
            elif model_family == PricingModelFamily.BINOMIAL_CRR:
                return ql.BinomialCRRVanillaEngine(process, numerical_steps)
            elif model_family == PricingModelFamily.FINITE_DIFFERENCE:
                if dividend_schedule:
                    return ql.FdBlackScholesVanillaEngine(process, dividend_schedule, numerical_steps, numerical_steps)
                return ql.FdBlackScholesVanillaEngine(process, numerical_steps, numerical_steps)
            elif model_family == PricingModelFamily.BLACK_SCHOLES_MERTON:
                # Critical check: European-only analytic engine cannot price American options!
                raise QuantModelIncompatibleError(
                    model_id="BLACK_SCHOLES_MERTON",
                    reason="European Analytic Black-Scholes-Merton engine cannot price American-style options with early exercise. Use BARONE_ADESI_WHALEY, BJERKSUND_STENSLAND, BINOMIAL_CRR, or FINITE_DIFFERENCE.",
                )
            else:
                # Default American to Barone-Adesi-Whaley approximation
                return ql.BaroneAdesiWhaleyApproximationEngine(process)

        else:
            raise QuantModelIncompatibleError(
                model_id=str(model_family),
                reason=f"Exercise style '{exercise_style}' is not supported by standard vanilla engine factory.",
            )

