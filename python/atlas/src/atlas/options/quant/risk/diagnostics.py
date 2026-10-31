"""Risk and Assignment Diagnostics Engine (Stage 142)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from atlas.options.domain import ExerciseStyle, LegSide, OptionType, SettlementMethod
from atlas.options.quant.domain import QuantStrategyLeg


class RiskDiagnosticsEngine:
    """Evaluates multi-leg options strategies for operational, market, and assignment risks."""

    @staticmethod
    def evaluate_strategy_risks(
        legs: List[QuantStrategyLeg],
        current_spot: float,
        is_unbounded_loss: bool,
        quote_age_seconds: Optional[float] = None,
        stale_threshold_seconds: float = 900.0,
        dividend_items: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Generate structured risk warnings for an options strategy."""
        warnings: List[str] = []

        # 1. Unbounded upside risk
        if is_unbounded_loss:
            warnings.append(
                "UNBOUNDED_UPSIDE_RISK: Strategy contains uncovered short call exposure. "
                "Losses increase without theoretical limit if the underlying price rallies."
            )

        # 2. Early Assignment Risk on American options
        for i, leg in enumerate(legs):
            if leg.exercise_style == ExerciseStyle.AMERICAN:
                if leg.side == LegSide.SHORT_CALL:
                    if current_spot > leg.strike_price:
                        warnings.append(
                            f"EARLY_ASSIGNMENT_RISK: Leg #{i+1} (Short Call Strike {leg.strike_price}) is in-the-money. "
                            "American option holders may exercise early to capture dividends or underlying shares."
                        )
                    if dividend_items:
                        warnings.append(
                            f"EX_DIVIDEND_ASSIGNMENT_RISK: Upcoming discrete dividend on record. Short calls carry "
                            "severe early assignment risk immediately prior to the ex-dividend date."
                        )

                elif leg.side == LegSide.SHORT_PUT:
                    if current_spot < leg.strike_price:
                        warnings.append(
                            f"EARLY_ASSIGNMENT_RISK: Leg #{i+1} (Short Put Strike {leg.strike_price}) is in-the-money. "
                            "Holders may exercise early to reinvest cash principal at prevailing risk-free interest rates."
                        )

        # 3. Pin Risk near expiration
        for i, leg in enumerate(legs):
            if leg.side in (LegSide.SHORT_CALL, LegSide.SHORT_PUT):
                distance_pct = abs(current_spot - leg.strike_price) / max(1.0, current_spot)
                if distance_pct < 0.015:  # within 1.5% of strike
                    warnings.append(
                        f"PIN_RISK: Underlying spot is within 1.5% of short strike {leg.strike_price}. "
                        "Uncertainty around after-hours closing prices may result in unexpected assignment."
                    )

        # 4. Multi-Expiration Complexity
        expirations = list({leg.expiration_date for leg in legs})
        if len(expirations) > 1:
            warnings.append(
                f"MULTI_EXPIRATION_STRUCTURE: Strategy spans multiple expiration dates ({', '.join(sorted(expirations))}). "
                "Terminal payoff is evaluated via pre-expiration QuantLib mark-to-market pricing at near-term expiration."
            )

        # 5. Stale Quote Warning
        if quote_age_seconds is not None and quote_age_seconds > stale_threshold_seconds:
            warnings.append(
                f"STALE_QUOTE_DATA: Options quote timestamp is {quote_age_seconds:.0f}s old "
                f"(exceeds threshold of {stale_threshold_seconds:.0f}s). Revaluation may not reflect current market conditions."
            )

        # 6. Margin Notice
        warnings.append(
            "MARGIN_LIMITATION_NOTICE: Margin requirements displayed are preliminary analytical approximations "
            "based on maximum theoretical risk. Actual broker maintenance margin varies by clearing firm, account type, "
            "and portfolio margin (TIMS) methodologies."
        )

        return warnings
