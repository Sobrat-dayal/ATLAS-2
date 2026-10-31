"""Master QuantLib Calculation Adapter (Stage 142)."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple
import QuantLib as ql

from atlas.options.domain import ExerciseStyle, OptionType
from atlas.options.quant.domain import (
    PricingModelFamily,
    QuantModelGreeks,
    QuantPricingDiagnostics,
)
from atlas.options.quant.errors import (
    QuantEvaluationDateError,
    QuantLibError,
    QuantModelIncompatibleError,
)
from atlas.options.quant.greeks.conventions import (
    rho_unit_to_bp,
    rho_unit_to_point,
    theta_annual_to_per_day,
    vega_unit_to_point,
)
from atlas.options.quant.greeks.numerical import compute_numerical_greeks
from atlas.options.quant.quantlib.context import isolated_quantlib_context
from atlas.options.quant.quantlib.dates import to_ql_date
from atlas.options.quant.quantlib.engine_factory import QuantLibEngineFactory
from atlas.options.quant.quantlib.term_structures import (
    build_bsm_process,
    build_dividend_schedule,
)


class QuantLibAdapter:
    """Master institutional adapter executing derivative pricing and Greek calculations."""

    @classmethod
    def price_vanilla_contract(
        cls,
        option_type: OptionType,
        strike_price: float,
        expiration_date: str,
        evaluation_date: str,
        spot_price: float,
        risk_free_rate: float,
        dividend_yield: float,
        volatility: float,
        exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN,
        model_family: PricingModelFamily = PricingModelFamily.BLACK_SCHOLES_MERTON,
        dividend_items: Optional[List[Dict[str, Any]]] = None,
        numerical_steps: int = 100,
    ) -> Tuple[float, QuantModelGreeks, QuantPricingDiagnostics]:
        """Price a single vanilla option contract and return (NPV, Greeks, Diagnostics)."""
        start_t = time.perf_counter()

        ql_eval = to_ql_date(evaluation_date)
        ql_exp = to_ql_date(expiration_date)

        # Edge case: Evaluation date on or after contract expiration
        if ql_eval >= ql_exp:
            # Terminal intrinsic payoff
            if option_type == OptionType.CALL:
                intrinsic = max(0.0, spot_price - strike_price)
                delta = 1.0 if spot_price > strike_price else 0.0
            else:
                intrinsic = max(0.0, strike_price - spot_price)
                delta = -1.0 if spot_price < strike_price else 0.0

            greeks = QuantModelGreeks(
                delta=delta,
                gamma=0.0,
                theta_per_day=0.0,
                theta_annual=0.0,
                vega_per_point=0.0,
                vega_per_unit=0.0,
                rho_per_point=0.0,
                rho_per_bp=0.0,
                calculation_method="TERMINAL_SETTLEMENT_CUTOFF",
            )
            diag = QuantPricingDiagnostics(
                execution_time_ms=(time.perf_counter() - start_t) * 1000.0,
                converged=True,
                iterations_or_steps=0,
                warnings=["Evaluation date is on or after contract expiration. Returned terminal intrinsic value."],
            )
            return intrinsic, greeks, diag

        with isolated_quantlib_context(ql_eval):
            try:
                # 1. Build underlying process
                process = build_bsm_process(
                    ql_eval,
                    spot_price,
                    risk_free_rate,
                    dividend_yield,
                    volatility,
                )

                # 2. Payoff and exercise
                ql_type = ql.Option.Call if option_type == OptionType.CALL else ql.Option.Put
                payoff = ql.PlainVanillaPayoff(ql_type, strike_price)

                if exercise_style == ExerciseStyle.EUROPEAN:
                    exercise = ql.EuropeanExercise(ql_exp)
                else:
                    exercise = ql.AmericanExercise(ql_eval, ql_exp)

                option = ql.VanillaOption(payoff, exercise)

                # 3. Discrete dividends if specified
                div_schedule = build_dividend_schedule(dividend_items or [])

                # 4. Engine creation
                engine = QuantLibEngineFactory.create_vanilla_engine(
                    model_family=model_family,
                    process=process,
                    exercise_style=exercise_style,
                    dividend_schedule=div_schedule if div_schedule else None,
                    numerical_steps=numerical_steps,
                )
                option.setPricingEngine(engine)

                # 5. Theoretical Price
                npv = option.NPV()

                # 6. Greeks extraction (analytic or fallback to numerical)
                greeks: QuantModelGreeks
                warnings: List[str] = []

                try:
                    delta = option.delta()
                    gamma = option.gamma()
                    vega_raw = option.vega()
                    vega_point = vega_unit_to_point(vega_raw)
                    try:
                        theta_day = option.thetaPerDay()
                        theta_ann = option.theta()
                    except Exception:
                        theta_ann = option.theta()
                        theta_day = theta_annual_to_per_day(theta_ann)
                    rho_raw = option.rho()
                    rho_point = rho_unit_to_point(rho_raw)
                    rho_bp = rho_unit_to_bp(rho_raw)

                    greeks = QuantModelGreeks(
                        delta=round(delta, 5),
                        gamma=round(gamma, 6),
                        theta_per_day=round(theta_day, 5),
                        theta_annual=round(theta_ann, 4),
                        vega_per_point=round(vega_point, 5),
                        vega_per_unit=round(vega_raw, 4),
                        rho_per_point=round(rho_point, 5),
                        rho_per_bp=round(rho_bp, 6),
                        calculation_method="ANALYTIC",
                    )
                except Exception:
                    # Fallback to high-accuracy central finite difference
                    warnings.append(
                        f"Pricing engine '{model_family.value}' does not provide complete analytic Greeks. "
                        "Calculated via high-accuracy central finite differences."
                    )

                    def _pricer(s: float, v: float, r: float, d: ql.Date) -> float:
                        with isolated_quantlib_context(d):
                            p = build_bsm_process(d, s, r, dividend_yield, v)
                            ex = ql.EuropeanExercise(ql_exp) if exercise_style == ExerciseStyle.EUROPEAN else ql.AmericanExercise(d, ql_exp)
                            opt = ql.VanillaOption(payoff, ex)
                            eng = QuantLibEngineFactory.create_vanilla_engine(
                                model_family, p, exercise_style, div_schedule, numerical_steps
                            )
                            opt.setPricingEngine(eng)
                            return opt.NPV()

                    greeks = compute_numerical_greeks(_pricer, spot_price, volatility, risk_free_rate, ql_eval)

                elapsed_ms = (time.perf_counter() - start_t) * 1000.0

                diag = QuantPricingDiagnostics(
                    execution_time_ms=round(elapsed_ms, 2),
                    converged=True,
                    iterations_or_steps=numerical_steps,
                    warnings=warnings,
                )

                return npv, greeks, diag

            except QuantModelIncompatibleError:
                raise
            except Exception as e:
                raise QuantLibError(f"QuantLib valuation failed: {str(e)}") from e
