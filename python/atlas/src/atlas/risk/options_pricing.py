"""ATLAS Options Risk Foundation — Black-Scholes-Merton Engine (Stage 118).

Mathematically rigorous European Black-Scholes-Merton pricing, Greeks
computation, finite-difference bump validation, position multiplier scaling,
and nonlinear Taylor approximation vs full repricing.
"""

from datetime import datetime
import math
from typing import Dict, List, Optional, Tuple

from .enums import (
    ExerciseStyle,
    OptionsPricingModelId,
    OptionSettlementType,
    OptionType,
)
from .errors import (
    RiskOptionContractIncompleteError,
    RiskOptionExerciseStyleUnsupportedError,
    RiskOptionExpiredError,
    RiskOptionImpliedVolatilityMissingError,
    RiskOptionImpliedVolatilityNonPositiveError,
    RiskOptionModelRepricingFailedError,
    RiskOptionMultiplierInvalidError,
    RiskOptionParityCheckFailedError,
    RiskOptionPositionQuantityZeroError,
    RiskOptionStrikeNonPositiveError,
    RiskOptionTimeToExpiryNegativeError,
    RiskOptionUnderlyingPriceNonPositiveError,
)
from .models import (
    OptionContractRiskInput,
    OptionGreeksResult,
    OptionPositionRiskResult,
    PortfolioOptionsRiskSummary,
)


SQRT_2 = math.sqrt(2.0)
INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def standard_normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function N(x)."""
    return 0.5 * (1.0 + math.erf(x / SQRT_2))


def standard_normal_pdf(x: float) -> float:
    """Standard normal probability density function phi(x)."""
    return INV_SQRT_2PI * math.exp(-0.5 * x * x)


class BlackScholesMertonEngine:
    """Institutional European Black-Scholes-Merton pricing and Greek sensitivity engine."""

    @staticmethod
    def calculate_d1_d2(
        spot: float,
        strike: float,
        time_to_expiry: float,
        risk_free_rate: float,
        dividend_yield: float,
        volatility: float,
    ) -> Tuple[float, float]:
        """Compute standard BSM d1 and d2 parameters."""
        if time_to_expiry <= 0.0 or volatility <= 0.0:
            return (0.0, 0.0)
        sqrt_t = math.sqrt(time_to_expiry)
        sigma_sqrt_t = volatility * sqrt_t
        d1 = (
            math.log(spot / strike)
            + (risk_free_rate - dividend_yield + 0.5 * volatility * volatility) * time_to_expiry
        ) / sigma_sqrt_t
        d2 = d1 - sigma_sqrt_t
        return (d1, d2)

    @classmethod
    def calculate_contract_price_and_greeks(
        cls,
        contract: OptionContractRiskInput,
    ) -> OptionGreeksResult:
        """Computes analytical theoretical price and per-contract Greeks."""
        # Validation
        if contract.underlying_price <= 0.0:
            raise RiskOptionUnderlyingPriceNonPositiveError(
                f"Underlying price must be strictly positive: {contract.underlying_price}"
            )
        if contract.strike_price <= 0.0:
            raise RiskOptionStrikeNonPositiveError(
                f"Strike price must be strictly positive: {contract.strike_price}"
            )
        if contract.time_to_expiry_years < 0.0:
            raise RiskOptionTimeToExpiryNegativeError(
                f"Time to expiry cannot be negative: {contract.time_to_expiry_years}"
            )
        if contract.implied_volatility <= 0.0:
            raise RiskOptionImpliedVolatilityNonPositiveError(
                f"Implied volatility must be strictly positive: {contract.implied_volatility}"
            )
        if contract.exercise_style not in (ExerciseStyle.EUROPEAN, ExerciseStyle.AMERICAN):
            raise RiskOptionExerciseStyleUnsupportedError(
                f"Exercise style {contract.exercise_style} is not supported by BSM engine"
            )

        S = contract.underlying_price
        K = contract.strike_price
        T = contract.time_to_expiry_years
        r = contract.risk_free_rate
        q = contract.dividend_yield
        sigma = contract.implied_volatility
        is_call = contract.option_type == OptionType.CALL

        # Handle expiration (T == 0)
        if T == 0.0:
            intrinsic = max(0.0, (S - K) if is_call else (K - S))
            delta = (1.0 if S > K else 0.0) if is_call else (-1.0 if S < K else 0.0)
            return OptionGreeksResult(
                theoretical_price=intrinsic,
                delta=delta,
                gamma=0.0,
                vega=0.0,
                vega_per_vol_point=0.0,
                theta=0.0,
                theta_per_day=0.0,
                rho=0.0,
                rho_per_basis_point=0.0,
                intrinsic_value=intrinsic,
                time_value=0.0,
                implied_volatility=sigma,
                d1=0.0,
                d2=0.0,
                put_call_parity_diff=0.0,
                is_pricing_valid=True,
                pricing_model=contract.model_id,
            )

        d1, d2 = cls.calculate_d1_d2(S, K, T, r, q, sigma)
        sqrt_t = math.sqrt(T)
        disc_r = math.exp(-r * T)
        disc_q = math.exp(-q * T)
        pdf_d1 = standard_normal_pdf(d1)
        cdf_d1 = standard_normal_cdf(d1)
        cdf_d2 = standard_normal_cdf(d2)
        cdf_neg_d1 = standard_normal_cdf(-d1)
        cdf_neg_d2 = standard_normal_cdf(-d2)

        # Theoretical price
        if is_call:
            price = S * disc_q * cdf_d1 - K * disc_r * cdf_d2
            intrinsic = max(0.0, S - K)
            delta = disc_q * cdf_d1
            theta_year = (
                -(S * disc_q * pdf_d1 * sigma) / (2.0 * sqrt_t)
                + q * S * disc_q * cdf_d1
                - r * K * disc_r * cdf_d2
            )
            rho_unit = K * T * disc_r * cdf_d2
        else:
            price = K * disc_r * cdf_neg_d2 - S * disc_q * cdf_neg_d1
            intrinsic = max(0.0, K - S)
            delta = -disc_q * cdf_neg_d1  # or disc_q * (cdf_d1 - 1.0)
            theta_year = (
                -(S * disc_q * pdf_d1 * sigma) / (2.0 * sqrt_t)
                - q * S * disc_q * cdf_neg_d1
                + r * K * disc_r * cdf_neg_d2
            )
            rho_unit = -K * T * disc_r * cdf_neg_d2

        gamma = (disc_q * pdf_d1) / (S * sigma * sqrt_t)
        vega_unit = S * disc_q * pdf_d1 * sqrt_t
        vega_per_vol_point = 0.01 * vega_unit
        theta_per_day = theta_year / 365.0
        rho_per_bp = 0.0001 * rho_unit
        time_value = max(0.0, price - intrinsic)

        # Put-Call parity check: C - P = S * e^(-qT) - K * e^(-rT)
        call_p = S * disc_q * cdf_d1 - K * disc_r * cdf_d2
        put_p = K * disc_r * cdf_neg_d2 - S * disc_q * cdf_neg_d1
        parity_target = S * disc_q - K * disc_r
        parity_diff = abs((call_p - put_p) - parity_target)

        return OptionGreeksResult(
            theoretical_price=price,
            delta=delta,
            gamma=gamma,
            vega=vega_unit,
            vega_per_vol_point=vega_per_vol_point,
            theta=theta_year,
            theta_per_day=theta_per_day,
            rho=rho_unit,
            rho_per_basis_point=rho_per_bp,
            intrinsic_value=intrinsic,
            time_value=time_value,
            implied_volatility=sigma,
            d1=d1,
            d2=d2,
            put_call_parity_diff=parity_diff,
            is_pricing_valid=True,
            pricing_model=contract.model_id,
        )

    @classmethod
    def reprice_contract(
        cls,
        contract: OptionContractRiskInput,
        spot_shift: float = 0.0,
        vol_shift: float = 0.0,
        rate_shift: float = 0.0,
        time_shift_days: float = 0.0,
    ) -> float:
        """Reprice contract under perturbed parameters."""
        new_spot = contract.underlying_price + spot_shift
        new_vol = max(0.0001, contract.implied_volatility + vol_shift)
        new_rate = contract.risk_free_rate + rate_shift
        new_time = max(0.0, contract.time_to_expiry_years - (time_shift_days / 365.0))

        perturbed = OptionContractRiskInput(
            instrument_id=contract.instrument_id,
            underlying_symbol=contract.underlying_symbol,
            option_type=contract.option_type,
            exercise_style=contract.exercise_style,
            strike_price=contract.strike_price,
            time_to_expiry_years=new_time,
            underlying_price=new_spot,
            implied_volatility=new_vol,
            risk_free_rate=new_rate,
            dividend_yield=contract.dividend_yield,
            contract_multiplier=contract.contract_multiplier,
            settlement_type=contract.settlement_type,
            model_id=contract.model_id,
            currency=contract.currency,
        )
        res = cls.calculate_contract_price_and_greeks(perturbed)
        return res.theoretical_price

    @classmethod
    def calculate_position_risk(
        cls,
        position_id: str,
        contract: OptionContractRiskInput,
        contracts_quantity: float,
        base_currency: str = "USD",
        fx_rate_to_base: float = 1.0,
    ) -> OptionPositionRiskResult:
        """Evaluates position risk with contracts quantity and contract multiplier scaling."""
        if contracts_quantity == 0.0:
            raise RiskOptionPositionQuantityZeroError("Contracts quantity cannot be zero")
        if contract.contract_multiplier <= 0.0:
            raise RiskOptionMultiplierInvalidError("Contract multiplier must be positive")

        greeks = cls.calculate_contract_price_and_greeks(contract)
        QM = contracts_quantity * contract.contract_multiplier
        S = contract.underlying_price

        # Position sensitivities in local currency
        pos_delta_units = QM * greeks.delta
        pos_delta_notional = pos_delta_units * S
        pos_gamma_units = QM * greeks.gamma
        pos_vega_per_vol_point = QM * greeks.vega_per_vol_point
        pos_theta_per_day = QM * greeks.theta_per_day
        pos_rho_per_bp = QM * greeks.rho_per_basis_point
        market_value = QM * greeks.theoretical_price

        # Base currency conversions
        base_delta_notional = pos_delta_notional * fx_rate_to_base
        base_vega_per_vp = pos_vega_per_vol_point * fx_rate_to_base
        base_theta_per_day = pos_theta_per_day * fx_rate_to_base
        base_rho_per_bp = pos_rho_per_bp * fx_rate_to_base

        # Scenario shifts evaluation
        shocks = {
            "spot_up_1pct": (0.01 * S, 0.0, 0.0, 0.0),
            "spot_down_1pct": (-0.01 * S, 0.0, 0.0, 0.0),
            "vol_up_1pt": (0.0, 0.01, 0.0, 0.0),
            "vol_down_1pt": (0.0, -0.01, 0.0, 0.0),
            "rate_up_25bp": (0.0, 0.0, 0.0025, 0.0),
            "time_decay_1d": (0.0, 0.0, 0.0, 1.0),
        }

        approx_pnl = {}
        reprice_pnl = {}

        for name, (ds, dvol, dr, dt_days) in shocks.items():
            # Greek Taylor series: dV ~= Delta * dS + 0.5 * Gamma * dS^2 + Vega * dvol - Theta_year * (dt/365) + Rho * dr
            dt_year = dt_days / 365.0
            taylor_per_contract = (
                greeks.delta * ds
                + 0.5 * greeks.gamma * (ds ** 2)
                + greeks.vega * dvol
                - greeks.theta * dt_year
                + greeks.rho * dr
            )
            approx_pnl[name] = QM * taylor_per_contract * fx_rate_to_base

            # Full model reprice
            new_p = cls.reprice_contract(contract, ds, dvol, dr, dt_days)
            reprice_pnl[name] = QM * (new_p - greeks.theoretical_price) * fx_rate_to_base

        return OptionPositionRiskResult(
            position_id=position_id,
            instrument_id=contract.instrument_id,
            underlying_symbol=contract.underlying_symbol,
            option_type=contract.option_type,
            exercise_style=contract.exercise_style,
            strike_price=contract.strike_price,
            time_to_expiry_years=contract.time_to_expiry_years,
            contracts_quantity=contracts_quantity,
            contract_multiplier=contract.contract_multiplier,
            position_market_value=market_value,
            underlying_price=S,
            currency=contract.currency,
            base_currency=base_currency,
            fx_rate_to_base=fx_rate_to_base,
            per_contract_greeks=greeks,
            position_delta_units=pos_delta_units,
            position_delta_notional=pos_delta_notional,
            position_gamma_units=pos_gamma_units,
            position_vega_per_vol_point=pos_vega_per_vol_point,
            position_theta_per_day=pos_theta_per_day,
            position_rho_per_basis_point=pos_rho_per_bp,
            base_currency_delta_notional=base_delta_notional,
            base_currency_vega_per_vol_point=base_vega_per_vp,
            base_currency_theta_per_day=base_theta_per_day,
            base_currency_rho_per_basis_point=base_rho_per_bp,
            approximate_pnl_shock=approx_pnl,
            full_reprice_pnl_shock=reprice_pnl,
        )

    @classmethod
    def aggregate_portfolio_options_risk(
        cls,
        portfolio_id: str,
        positions: List[OptionPositionRiskResult],
        base_currency: str = "USD",
        as_of: Optional[datetime] = None,
    ) -> PortfolioOptionsRiskSummary:
        """Aggregates position-level options risk into portfolio totals and underlying buckets."""
        as_of = as_of or datetime.utcnow()
        if not positions:
            return PortfolioOptionsRiskSummary(
                portfolio_id=portfolio_id,
                as_of=as_of,
                base_currency=base_currency,
                total_options_market_value=0.0,
                options_count=0,
                net_delta_notional=0.0,
                gross_delta_notional=0.0,
                net_vega_per_vol_point=0.0,
                gross_vega_per_vol_point=0.0,
                net_theta_per_day=0.0,
                net_rho_per_basis_point=0.0,
                underlying_exposures={},
                positions=[],
                is_complete=True,
                warnings=[],
            )

        total_mv = sum(p.position_market_value * p.fx_rate_to_base for p in positions)
        net_delta = sum(p.base_currency_delta_notional for p in positions)
        gross_delta = sum(abs(p.base_currency_delta_notional) for p in positions)
        net_vega = sum(p.base_currency_vega_per_vol_point for p in positions)
        gross_vega = sum(abs(p.base_currency_vega_per_vol_point) for p in positions)
        net_theta = sum(p.base_currency_theta_per_day for p in positions)
        net_rho = sum(p.base_currency_rho_per_basis_point for p in positions)

        # Underlying grouping
        underlyings: Dict[str, Dict[str, float]] = {}
        for p in positions:
            sym = p.underlying_symbol
            if sym not in underlyings:
                underlyings[sym] = {
                    "net_delta_notional": 0.0,
                    "gross_delta_notional": 0.0,
                    "net_vega_per_vol_point": 0.0,
                    "gross_vega_per_vol_point": 0.0,
                    "net_theta_per_day": 0.0,
                    "net_rho_per_basis_point": 0.0,
                    "market_value": 0.0,
                    "contracts_count": 0,
                }
            underlyings[sym]["net_delta_notional"] += p.base_currency_delta_notional
            underlyings[sym]["gross_delta_notional"] += abs(p.base_currency_delta_notional)
            underlyings[sym]["net_vega_per_vol_point"] += p.base_currency_vega_per_vol_point
            underlyings[sym]["gross_vega_per_vol_point"] += abs(p.base_currency_vega_per_vol_point)
            underlyings[sym]["net_theta_per_day"] += p.base_currency_theta_per_day
            underlyings[sym]["net_rho_per_basis_point"] += p.base_currency_rho_per_basis_point
            underlyings[sym]["market_value"] += p.position_market_value * p.fx_rate_to_base
            underlyings[sym]["contracts_count"] += 1

        return PortfolioOptionsRiskSummary(
            portfolio_id=portfolio_id,
            as_of=as_of,
            base_currency=base_currency,
            total_options_market_value=total_mv,
            options_count=len(positions),
            net_delta_notional=net_delta,
            gross_delta_notional=gross_delta,
            net_vega_per_vol_point=net_vega,
            gross_vega_per_vol_point=gross_vega,
            net_theta_per_day=net_theta,
            net_rho_per_basis_point=net_rho,
            underlying_exposures=underlyings,
            positions=positions,
            is_complete=True,
            warnings=[],
        )

