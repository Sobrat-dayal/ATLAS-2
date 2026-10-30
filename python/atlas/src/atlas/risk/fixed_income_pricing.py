"""ATLAS Fixed-Income Risk Foundation — Bond Cash-Flow Engine (Stage 118).

Cash flow generation, clean vs dirty price reconciliation, accrued interest,
yield-to-maturity numerical solving, Macaulay duration, modified duration,
convexity, DV01/PV01, effective sensitivities, key-rate duration profiles,
and multi-currency portfolio risk aggregation.
"""

from datetime import datetime, timedelta
import math
from typing import Dict, List, Optional, Tuple

from .enums import (
    BondPricingModelId,
    CouponFrequency,
    CouponType,
    DayCountConvention,
    YieldCurveInterpolation,
)
from .errors import (
    RiskBondCashflowIncompleteError,
    RiskBondCleanPriceNonPositiveError,
    RiskBondCouponFrequencyInvalidError,
    RiskBondCurveInsufficientPointsError,
    RiskBondDayCountConventionUnsupportedError,
    RiskBondDirtyPriceNonPositiveError,
    RiskBondFaceValueNonPositiveError,
    RiskBondMaturityBeforeSettlementError,
    RiskBondYieldSolverFailedError,
)
from .models import (
    BondCashFlowItem,
    BondCashFlowSchedule,
    BondPositionRiskResult,
    BondSensitivitiesResult,
    InterestRateCurveDefinition,
    KeyRateSensitivityItem,
    PortfolioFixedIncomeRiskSummary,
    YieldCurvePoint,
)


STANDARD_KEY_RATE_TENORS: List[Tuple[str, float]] = [
    ("6M", 0.5),
    ("1Y", 1.0),
    ("2Y", 2.0),
    ("3Y", 3.0),
    ("5Y", 5.0),
    ("7Y", 7.0),
    ("10Y", 10.0),
    ("20Y", 20.0),
    ("30Y", 30.0),
]


def calculate_year_fraction(
    start_date: datetime,
    end_date: datetime,
    convention: DayCountConvention = DayCountConvention.ACT_ACT,
) -> float:
    """Calculates year fraction between two dates under the specified convention."""
    if end_date <= start_date:
        return 0.0

    days = (end_date - start_date).days

    if convention in (DayCountConvention.ACT_ACT, DayCountConvention.ACT_365F):
        return days / 365.0
    elif convention == DayCountConvention.ACT_360:
        return days / 360.0
    elif convention == DayCountConvention.THIRTY_360:
        d1 = min(start_date.day, 30)
        d2 = min(end_date.day, 30) if d1 == 30 else end_date.day
        year_diff = end_date.year - start_date.year
        month_diff = end_date.month - start_date.month
        day_diff = d2 - d1
        return (360.0 * year_diff + 30.0 * month_diff + day_diff) / 360.0
    return days / 365.0


class BondCashFlowEngine:
    """Institutional bond pricing, cash-flow projection, and sensitivity calculation engine."""

    @classmethod
    def generate_cash_flow_schedule(
        cls,
        instrument_id: str,
        face_value: float,
        coupon_rate: float,
        coupon_frequency: CouponFrequency,
        settlement_date: datetime,
        maturity_date: datetime,
        day_count_convention: DayCountConvention = DayCountConvention.ACT_ACT,
        clean_price: Optional[float] = None,
        market_yield: Optional[float] = None,
    ) -> BondCashFlowSchedule:
        """Projects bond cash flow dates, coupons, principal, and accrued interest."""
        if face_value <= 0.0:
            raise RiskBondFaceValueNonPositiveError(f"Face value must be positive: {face_value}")
        if maturity_date <= settlement_date:
            raise RiskBondMaturityBeforeSettlementError(
                f"Maturity {maturity_date} must be strictly after settlement {settlement_date}"
            )

        m = coupon_frequency.periods_per_year
        total_years = (maturity_date - settlement_date).days / 365.0
        num_periods = max(1, int(round(total_years * m)))

        # Build payment dates backward from maturity
        payment_dates: List[datetime] = []
        months_per_period = max(1, 12 // m)

        curr = maturity_date
        while curr > settlement_date:
            payment_dates.append(curr)
            # Step back
            y = curr.year
            mon = curr.month - months_per_period
            while mon <= 0:
                mon += 12
                y -= 1
            day = min(curr.day, 28)
            curr = datetime(y, mon, day)

        payment_dates.reverse()
        if not payment_dates:
            payment_dates = [maturity_date]

        # Calculate accrued interest
        accrued_interest = 0.0
        # If settled between payment dates
        if len(payment_dates) > 0 and payment_dates[0] > settlement_date:
            # Previous coupon date
            first_pay = payment_dates[0]
            # estimate previous date
            prev_y = first_pay.year
            prev_mon = first_pay.month - months_per_period
            while prev_mon <= 0:
                prev_mon += 12
                prev_y -= 1
            prev_day = min(first_pay.day, 28)
            prev_coupon_date = datetime(prev_y, prev_mon, prev_day)
            if prev_coupon_date < settlement_date:
                # If difference is 0 or practically zero (within 2 days due to month end/leap)
                day_gap = (settlement_date - prev_coupon_date).days
                if day_gap > 3:
                    accrual_fraction = calculate_year_fraction(
                        prev_coupon_date, settlement_date, day_count_convention
                    )
                    accrued_interest = face_value * coupon_rate * accrual_fraction
                else:
                    accrued_interest = 0.0

        # Strip time of day from settlement and maturity dates
        settlement_date = datetime(settlement_date.year, settlement_date.month, settlement_date.day)
        maturity_date = datetime(maturity_date.year, maturity_date.month, maturity_date.day)

        # Construct cash flow items
        items: List[BondCashFlowItem] = []
        for idx, pdate in enumerate(payment_dates, start=1):
            t_j = calculate_year_fraction(settlement_date, pdate, day_count_convention)
            # If regular periodic schedule closely matches idx / m, align to exact nominal period fraction
            ideal_t = idx / m
            if abs(t_j - ideal_t) < 0.04:
                t_j = ideal_t
            is_mat = (idx == len(payment_dates))
            coupon_pmt = (face_value * coupon_rate) / m
            principal_pmt = face_value if is_mat else 0.0
            total_cf = coupon_pmt + principal_pmt

            # Discount factor if market yield is supplied
            df = 1.0
            pv = total_cf
            if market_yield is not None:
                df = (1.0 + market_yield / m) ** (-m * t_j)
                pv = total_cf * df

            items.append(
                BondCashFlowItem(
                    period_index=idx,
                    payment_date=pdate,
                    year_fraction=t_j,
                    coupon_amount=coupon_pmt,
                    principal_amount=principal_pmt,
                    total_cash_flow=total_cf,
                    discount_factor=df,
                    present_value=pv,
                )
            )

        # Clean vs dirty price
        if clean_price is not None:
            dirty_price = clean_price + accrued_interest
        elif market_yield is not None:
            dirty_price = sum(item.present_value for item in items)
            clean_price = dirty_price - accrued_interest
        else:
            dirty_price = face_value
            clean_price = dirty_price - accrued_interest

        return BondCashFlowSchedule(
            instrument_id=instrument_id,
            face_value=face_value,
            coupon_rate=coupon_rate,
            coupon_frequency=coupon_frequency,
            day_count_convention=day_count_convention,
            settlement_date=settlement_date,
            maturity_date=maturity_date,
            cash_flows=items,
            accrued_interest=accrued_interest,
            clean_price=clean_price,
            dirty_price=dirty_price,
        )

    @classmethod
    def price_from_yield(
        cls,
        cash_flows: List[Tuple[float, float]],  # list of (t_j in years, total_cf)
        yield_rate: float,
        compounding_freq: int = 1,
    ) -> float:
        """Computes dirty bond price from annual compounding yield."""
        m = compounding_freq
        p = 0.0
        for t_j, cf in cash_flows:
            p += cf / ((1.0 + yield_rate / m) ** (m * t_j))
        return p

    @classmethod
    def price_derivative_wrt_yield(
        cls,
        cash_flows: List[Tuple[float, float]],
        yield_rate: float,
        compounding_freq: int = 1,
    ) -> float:
        """First derivative dP/dy of bond price with respect to annual yield."""
        m = compounding_freq
        dp_dy = 0.0
        for t_j, cf in cash_flows:
            # d/dy [ (1 + y/m)^(-m * t_j) ] = -t_j * (1 + y/m)^(-m * t_j - 1)
            dp_dy -= t_j * cf / ((1.0 + yield_rate / m) ** (m * t_j + 1))
        return dp_dy

    @classmethod
    def solve_yield_to_maturity(
        cls,
        cash_flows: List[Tuple[float, float]],
        target_dirty_price: float,
        compounding_freq: int = 1,
        max_iterations: int = 100,
        tolerance: float = 1e-9,
    ) -> float:
        """Solves for Yield to Maturity (YTM) matching target dirty price using Newton-Raphson / bisection."""
        if target_dirty_price <= 0.0:
            raise RiskBondDirtyPriceNonPositiveError(f"Target dirty price must be positive: {target_dirty_price}")

        # Initial guess based on simple approximation
        y = 0.05
        m = compounding_freq

        # Newton-Raphson loop
        for _ in range(max_iterations):
            p = cls.price_from_yield(cash_flows, y, m)
            diff = p - target_dirty_price
            if abs(diff) < tolerance:
                return y
            dp_dy = cls.price_derivative_wrt_yield(cash_flows, y, m)
            if abs(dp_dy) < 1e-12:
                break
            y_next = y - diff / dp_dy
            # Prevent divergence
            if y_next < -0.20 or y_next > 2.0:
                break
            y = y_next

        # Bisection fallback
        low = -0.15
        high = 1.50
        p_low = cls.price_from_yield(cash_flows, low, m)
        p_high = cls.price_from_yield(cash_flows, high, m)

        # Check bracket
        if (p_low - target_dirty_price) * (p_high - target_dirty_price) > 0:
            # If still not bracketed, widen range
            low = -0.30
            high = 3.0
            p_low = cls.price_from_yield(cash_flows, low, m)
            p_high = cls.price_from_yield(cash_flows, high, m)
            if (p_low - target_dirty_price) * (p_high - target_dirty_price) > 0:
                raise RiskBondYieldSolverFailedError(
                    f"Yield solver could not bracket target dirty price {target_dirty_price}"
                )

        for _ in range(max_iterations):
            mid = 0.5 * (low + high)
            p_mid = cls.price_from_yield(cash_flows, mid, m)
            diff = p_mid - target_dirty_price
            if abs(diff) < tolerance or (high - low) < 1e-10:
                return mid
            # Price is monotonically decreasing with respect to yield
            if p_mid > target_dirty_price:
                low = mid
            else:
                high = mid

        return 0.5 * (low + high)

    @classmethod
    def calculate_sensitivities(
        cls,
        cash_flows: List[Tuple[float, float]],
        yield_rate: float,
        dirty_price: float,
        clean_price: float,
        accrued_interest: float,
        compounding_freq: int = 1,
        face_value: float = 100.0,
    ) -> BondSensitivitiesResult:
        """Calculates Macaulay duration, modified duration, convexity, DV01, and key-rate durations."""
        if dirty_price <= 0.0:
            raise RiskBondDirtyPriceNonPositiveError(f"Dirty price must be positive: {dirty_price}")

        m = compounding_freq
        pv_sum = 0.0
        weighted_t_sum = 0.0
        convexity_sum = 0.0

        for t_j, cf in cash_flows:
            discount = (1.0 + yield_rate / m) ** (-m * t_j)
            pv = cf * discount
            pv_sum += pv
            weighted_t_sum += t_j * pv
            # Convexity numerator term: t_j * (t_j + 1/m) * CF / (1 + y/m)^(m*t_j + 2)
            # Notice (1 + y/m)^(-m*t_j - 2) = discount / (1 + y/m)^2
            term = (t_j * (t_j + 1.0 / m) * cf) / ((1.0 + yield_rate / m) ** (m * t_j + 2))
            convexity_sum += term

        mac_dur = weighted_t_sum / dirty_price
        mod_dur = mac_dur / (1.0 + yield_rate / m)
        convexity = convexity_sum / dirty_price

        # DV01 per 100 face value (positive risk magnitude)
        dv01_per_100 = (dirty_price / (face_value / 100.0)) * mod_dur * 0.0001 if face_value > 0 else dirty_price * mod_dur * 0.0001

        # Effective duration & convexity via bump (+/- 1 bp = 0.0001)
        dy = 0.0001
        p_up = cls.price_from_yield(cash_flows, yield_rate + dy, m)
        p_dn = cls.price_from_yield(cash_flows, yield_rate - dy, m)
        eff_dur = (p_dn - p_up) / (2.0 * dirty_price * dy)
        eff_conv = (p_up + p_dn - 2.0 * dirty_price) / (dirty_price * (dy ** 2))

        # Key-Rate Durations (KRD)
        # Allocate each cash flow sensitivity w_j to standard key-rate tenors
        krd_items: List[KeyRateSensitivityItem] = []
        tenors = STANDARD_KEY_RATE_TENORS
        krd_values = [0.0] * len(tenors)

        for t_j, cf in cash_flows:
            # Contribution to modified duration: (t_j * pv) / (dirty_price * (1 + y/m))
            dur_contrib = (t_j * cf) / (dirty_price * ((1.0 + yield_rate / m) ** (m * t_j + 1)))

            # Bracket
            if t_j <= tenors[0][1]:
                krd_values[0] += dur_contrib
            elif t_j >= tenors[-1][1]:
                krd_values[-1] += dur_contrib
            else:
                for k in range(len(tenors) - 1):
                    t_k = tenors[k][1]
                    t_k1 = tenors[k + 1][1]
                    if t_k <= t_j <= t_k1:
                        w_k1 = (t_j - t_k) / (t_k1 - t_k)
                        w_k = 1.0 - w_k1
                        krd_values[k] += dur_contrib * w_k
                        krd_values[k + 1] += dur_contrib * w_k1
                        break

        for (tname, tyears), val in zip(tenors, krd_values):
            krd_items.append(
                KeyRateSensitivityItem(
                    tenor_name=tname,
                    tenor_years=tyears,
                    key_rate_duration=val,
                    key_rate_dv01=(dirty_price / (face_value / 100.0)) * val * 0.0001,
                )
            )

        return BondSensitivitiesResult(
            clean_price=clean_price,
            accrued_interest=accrued_interest,
            dirty_price=dirty_price,
            yield_to_maturity=yield_rate,
            macaulay_duration=mac_dur,
            modified_duration=mod_dur,
            convexity=convexity,
            dv01_per_100_face=dv01_per_100,
            effective_duration=eff_dur,
            effective_convexity=eff_conv,
            key_rate_durations=krd_items,
            pricing_model=BondPricingModelId.DISCOUNTED_CASHFLOW,
        )

    @classmethod
    def calculate_bond_position_risk(
        cls,
        position_id: str,
        instrument_id: str,
        issuer_name: str,
        face_value: float,
        quantity: float,
        coupon_rate: float,
        coupon_frequency: CouponFrequency,
        settlement_date: datetime,
        maturity_date: datetime,
        clean_price: Optional[float] = None,
        market_yield: Optional[float] = None,
        day_count_convention: DayCountConvention = DayCountConvention.ACT_ACT,
        currency: str = "USD",
        base_currency: str = "USD",
        fx_rate_to_base: float = 1.0,
    ) -> BondPositionRiskResult:
        """Evaluates single bond position risk, duration, convexity, and portfolio DV01."""
        schedule = cls.generate_cash_flow_schedule(
            instrument_id=instrument_id,
            face_value=face_value,
            coupon_rate=coupon_rate,
            coupon_frequency=coupon_frequency,
            settlement_date=settlement_date,
            maturity_date=maturity_date,
            day_count_convention=day_count_convention,
            clean_price=clean_price,
            market_yield=market_yield,
        )

        cf_tuples = [(item.year_fraction, item.total_cash_flow) for item in schedule.cash_flows]
        m = coupon_frequency.periods_per_year

        if market_yield is not None:
            ytm = market_yield
        else:
            ytm = cls.solve_yield_to_maturity(cf_tuples, schedule.dirty_price, compounding_freq=m)

        sensitivities = cls.calculate_sensitivities(
            cash_flows=cf_tuples,
            yield_rate=ytm,
            dirty_price=schedule.dirty_price,
            clean_price=schedule.clean_price,
            accrued_interest=schedule.accrued_interest,
            compounding_freq=m,
            face_value=face_value,
        )

        # Market value of position: quantity * dirty_price
        position_mv = quantity * schedule.dirty_price
        # Position DV01: market_value * modified_duration * 0.0001
        pos_dv01 = position_mv * sensitivities.modified_duration * 0.0001
        base_dv01 = pos_dv01 * fx_rate_to_base

        return BondPositionRiskResult(
            position_id=position_id,
            instrument_id=instrument_id,
            issuer_name=issuer_name,
            face_value=face_value,
            quantity=quantity,
            currency=currency,
            base_currency=base_currency,
            fx_rate_to_base=fx_rate_to_base,
            market_value=position_mv,
            sensitivities=sensitivities,
            position_dv01=pos_dv01,
            base_currency_dv01=base_dv01,
            cash_flow_schedule=schedule,
        )

    @classmethod
    def aggregate_portfolio_fixed_income_risk(
        cls,
        portfolio_id: str,
        positions: List[BondPositionRiskResult],
        base_currency: str = "USD",
        as_of: Optional[datetime] = None,
    ) -> PortfolioFixedIncomeRiskSummary:
        """Aggregates portfolio fixed-income duration, convexity, yield, and key-rate DV01 profile."""
        as_of = as_of or datetime.utcnow()
        if not positions:
            return PortfolioFixedIncomeRiskSummary(
                portfolio_id=portfolio_id,
                as_of=as_of,
                base_currency=base_currency,
                total_fixed_income_market_value=0.0,
                bonds_count=0,
                portfolio_weighted_modified_duration=0.0,
                portfolio_weighted_macaulay_duration=0.0,
                portfolio_weighted_convexity=0.0,
                portfolio_weighted_yield=0.0,
                portfolio_total_dv01=0.0,
                key_rate_dv01_profile={},
                positions=[],
                is_complete=True,
                warnings=[],
            )

        total_mv = sum(p.market_value * p.fx_rate_to_base for p in positions)
        if total_mv <= 0.0:
            total_mv = 1.0  # avoid division by zero

        weighted_mod_dur = sum(
            (p.market_value * p.fx_rate_to_base / total_mv) * p.sensitivities.modified_duration
            for p in positions
        )
        weighted_mac_dur = sum(
            (p.market_value * p.fx_rate_to_base / total_mv) * p.sensitivities.macaulay_duration
            for p in positions
        )
        weighted_conv = sum(
            (p.market_value * p.fx_rate_to_base / total_mv) * p.sensitivities.convexity
            for p in positions
        )
        weighted_yield = sum(
            (p.market_value * p.fx_rate_to_base / total_mv) * p.sensitivities.yield_to_maturity
            for p in positions
        )
        total_dv01 = sum(p.base_currency_dv01 for p in positions)

        # Key-rate profile summation
        kr_profile: Dict[str, float] = {}
        for p in positions:
            for item in p.sensitivities.key_rate_durations:
                # DV01 of position in base currency at this tenor
                krd_dv01 = (p.market_value * p.fx_rate_to_base) * item.key_rate_duration * 0.0001
                kr_profile[item.tenor_name] = kr_profile.get(item.tenor_name, 0.0) + krd_dv01

        return PortfolioFixedIncomeRiskSummary(
            portfolio_id=portfolio_id,
            as_of=as_of,
            base_currency=base_currency,
            total_fixed_income_market_value=total_mv if total_mv != 1.0 else 0.0,
            bonds_count=len(positions),
            portfolio_weighted_modified_duration=weighted_mod_dur,
            portfolio_weighted_macaulay_duration=weighted_mac_dur,
            portfolio_weighted_convexity=weighted_conv,
            portfolio_weighted_yield=weighted_yield,
            portfolio_total_dv01=total_dv01,
            key_rate_dv01_profile=kr_profile,
            positions=positions,
            is_complete=True,
            warnings=[],
        )
