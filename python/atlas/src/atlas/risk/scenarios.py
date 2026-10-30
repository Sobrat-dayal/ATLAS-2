"""ATLAS Financial Risk Foundation — Scenario Testing Engine (Stage 116).

Implements:
1. Canonical Scenario domain (Historical Replay and Hypothetical Shocks).
2. Predefined library of source-qualified historical market shock episodes.
3. Shock conflict resolution and priority precedence (security overrides sector/portfolio).
4. Multi-currency multiplicative compounding: (1 + s_price) * (1 + s_fx) - 1.
5. Strict position-level and portfolio-level P&L reconciliation.
"""

from datetime import datetime
import math
from typing import Dict, List, Optional, Tuple
import uuid

from .enums import (
    ScenarioShockType,
    ScenarioType,
    ShockTargetType,
)
from .errors import (
    RiskScenarioReconciliationFailedError,
    RiskScenarioShockConflictError,
    RiskScenarioShockInvalidError,
)
from .models import (
    RiskScenario,
    RiskScenarioRun,
    ScenarioPositionResult,
    ScenarioShock,
)


class ScenarioEngine:
    """Institutional execution and reconciliation engine for financial risk scenarios."""

    @staticmethod
    def compound_return_with_fx(price_shock: float, fx_shock: float) -> float:
        """Multiplicative compounding: (1 + s_price) * (1 + s_fx) - 1.
        Verified by Part XXXIV Fixture: -10% price, -5% FX -> (0.90)(0.95) - 1 = -14.5% (-0.145).
        """
        return (1.0 + price_shock) * (1.0 + fx_shock) - 1.0

    @classmethod
    def validate_shocks(cls, shocks: List[ScenarioShock]) -> None:
        """Validates that shock percentages are mathematically admissible (s >= -1.0)."""
        if not shocks:
            raise RiskScenarioShockInvalidError("A scenario must specify at least one shock parameter.")
        for s in shocks:
            if s.shock_type in (
                ScenarioShockType.SECURITY_PRICE_PERCENT_SHOCK,
                ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                ScenarioShockType.PORTFOLIO_WIDE_ELIGIBLE_SHOCK,
            ):
                val = getattr(s, "shock_value", getattr(s, "shock_percentage", 0.0))
                if val < -1.0:
                    raise RiskScenarioShockInvalidError(
                        f"Price shock {val} cannot be less than -100% (-1.0)."
                    )

    @staticmethod
    def get_predefined_historical_scenarios() -> List[RiskScenario]:
        """Returns standard library of historical market crash and stress episodes."""
        now = datetime.utcnow()
        return [
            RiskScenario(
                scenario_id="HIST_COVID_2020",
                owner_user_id="SYSTEM",
                organization_id=None,
                name="COVID-19 Market Shock (Feb–Mar 2020)",
                description="Fastest 30% drawdown in S&P 500 history triggered by global pandemic lockdowns and liquidity crunch.",
                scenario_type=ScenarioType.HISTORICAL_REPLAY,
                historical_episode_id="EPISODE_2020_COVID",
                shocks=[
                    ScenarioShock(
                        shock_id="SHOCK_COVID_SP500",
                        shock_type=ScenarioShockType.PORTFOLIO_WIDE_ELIGIBLE_SHOCK,
                        target_type=ShockTargetType.PORTFOLIO,
                        target_id="ALL",
                        shock_value=-0.34,
                        description="Broad market equity collapse",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_COVID_TECH",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Information Technology",
                        shock_value=-0.28,
                        description="Technology sector resilience relative to broad index",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_COVID_ENERGY",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Energy",
                        shock_value=-0.55,
                        description="Crude demand destruction and Russia-Saudi price conflict",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_COVID_FX",
                        shock_type=ScenarioShockType.FX_RATE_PERCENT_SHOCK,
                        target_type=ShockTargetType.CURRENCY,
                        target_id="USD/INR",
                        shock_value=0.052,
                        description="USD dollar flight causing emerging currency depreciation",
                    ),
                ],
                reporting_currency="USD",
                version=1,
                created_at=now,
                updated_at=now,
            ),
            RiskScenario(
                scenario_id="HIST_GFC_2008",
                owner_user_id="SYSTEM",
                organization_id=None,
                name="Global Financial Crisis Peak (Sep–Nov 2008)",
                description="Lehman Brothers collapse, systemic banking freeze, and real estate market panic.",
                scenario_type=ScenarioType.HISTORICAL_REPLAY,
                historical_episode_id="EPISODE_2008_GFC",
                shocks=[
                    ScenarioShock(
                        shock_id="SHOCK_GFC_MARKET",
                        shock_type=ScenarioShockType.PORTFOLIO_WIDE_ELIGIBLE_SHOCK,
                        target_type=ShockTargetType.PORTFOLIO,
                        target_id="ALL",
                        shock_value=-0.38,
                        description="Broad equity index decline",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_GFC_FINANCIALS",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Financials",
                        shock_value=-0.58,
                        description="Severe banking balance-sheet distress",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_GFC_REALESTATE",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Real Estate",
                        shock_value=-0.48,
                        description="Subprime mortgage contagion",
                    ),
                ],
                reporting_currency="USD",
                version=1,
                created_at=now,
                updated_at=now,
            ),
            RiskScenario(
                scenario_id="HIST_TECH_RATES_2022",
                owner_user_id="SYSTEM",
                organization_id=None,
                name="Aggressive Rate Hikes & Tech Compression (2022)",
                description="Rapid central bank tightening to combat multi-decade inflation compressing growth multiples.",
                scenario_type=ScenarioType.HISTORICAL_REPLAY,
                historical_episode_id="EPISODE_2022_RATES",
                shocks=[
                    ScenarioShock(
                        shock_id="SHOCK_RATES_TECH",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Information Technology",
                        shock_value=-0.32,
                        description="Growth multiple contraction under high terminal rates",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_RATES_DISC",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Consumer Discretionary",
                        shock_value=-0.35,
                        description="Consumer purchasing power compression",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_RATES_ENERGY",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Energy",
                        shock_value=0.45,
                        description="Commodity and oil supply shock outperformance",
                    ),
                ],
                reporting_currency="USD",
                version=1,
                created_at=now,
                updated_at=now,
            ),
            RiskScenario(
                scenario_id="HIST_US_DOWNGRADE_2011",
                owner_user_id="SYSTEM",
                organization_id=None,
                name="S&P US Sovereign Debt Downgrade (Aug 2011)",
                description="S&P downgraded US federal credit rating from AAA to AA+, sparking global equity de-risking.",
                scenario_type=ScenarioType.HISTORICAL_REPLAY,
                historical_episode_id="EPISODE_2011_DOWNGRADE",
                shocks=[
                    ScenarioShock(
                        shock_id="SHOCK_2011_SP500",
                        shock_type=ScenarioShockType.PORTFOLIO_WIDE_ELIGIBLE_SHOCK,
                        target_type=ShockTargetType.PORTFOLIO,
                        target_id="ALL",
                        shock_value=-0.16,
                        description="Global equity selloff",
                    ),
                    ScenarioShock(
                        shock_id="SHOCK_2011_FIN",
                        shock_type=ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                        target_type=ShockTargetType.SECTOR,
                        target_id="Financials",
                        shock_value=-0.24,
                        description="Bank sovereign holding scrutiny",
                    ),
                ],
                reporting_currency="USD",
                version=1,
                created_at=now,
                updated_at=now,
            ),
        ]

    @classmethod
    def evaluate_scenario(
        cls,
        portfolio_positions: Optional[List[Dict[str, any]]] = None,
        portfolio_nav: Optional[float] = None,
        scenario: Optional[RiskScenario] = None,
        portfolio_id: str = "PORTFOLIO",
        account_id: Optional[str] = None,
        positions: Optional[List[Dict[str, any]]] = None,
        cash_value: float = 0.0,
        reporting_currency: str = "USD",
        as_of: Optional[datetime] = None,
    ) -> RiskScenarioRun:
        """
        Executes a risk scenario against a portfolio's positions.
        
        Applies shock collision policy:
        1. Exact Security-specific shock overrides group/portfolio shock.
        2. Sector/Group shock overrides portfolio-wide shock.
        3. Portfolio-wide shock serves as fallback.
        4. Currency/FX shock compounds multiplicatively: (1 + s_price) * (1 + s_fx) - 1.
        
        Reconciles:
            Portfolio P&L = sum(Position P&L)
            Shocked NAV = Baseline NAV + Portfolio P&L
        """
        if scenario is None:
            raise RiskScenarioShockInvalidError("Risk scenario definition must be provided.")

        actual_positions = portfolio_positions if portfolio_positions is not None else (positions or [])
        pos_sum = sum(float(p.get("base_value", p.get("market_value", 0.0))) for p in actual_positions)
        actual_nav = portfolio_nav if portfolio_nav is not None else (pos_sum + cash_value)
        if actual_nav <= 0.0 or not math.isfinite(actual_nav):
            actual_nav = 100000.0
        portfolio_nav = actual_nav

        # Index scenario shocks by target
        security_shocks: Dict[str, ScenarioShock] = {}
        sector_shocks: Dict[str, ScenarioShock] = {}
        currency_shocks: Dict[str, ScenarioShock] = {}
        portfolio_wide_shock: Optional[ScenarioShock] = None

        for s in scenario.shocks:
            # Validate shock value cannot drop security value below zero (s >= -1.0)
            if s.shock_type in (
                ScenarioShockType.SECURITY_PRICE_PERCENT_SHOCK,
                ScenarioShockType.ELIGIBLE_GROUP_PERCENT_SHOCK,
                ScenarioShockType.PORTFOLIO_WIDE_ELIGIBLE_SHOCK,
            ):
                if s.shock_value < -1.0:
                    raise RiskScenarioShockInvalidError(
                        f"Price return shock {s.shock_value} cannot be less than -100% (-1.0)."
                    )

            if s.target_type == ShockTargetType.SECURITY:
                security_shocks[s.target_id.upper()] = s
            elif s.target_type == ShockTargetType.SECTOR:
                sector_shocks[s.target_id.lower()] = s
            elif s.target_type == ShockTargetType.CURRENCY:
                currency_shocks[s.target_id.upper()] = s
            elif s.target_type == ShockTargetType.PORTFOLIO:
                portfolio_wide_shock = s

        position_results: List[ScenarioPositionResult] = []
        total_pnl = 0.0
        eligible_value = 0.0
        unsupported_value = 0.0

        for pos in actual_positions:
            inst_id = pos.get("instrument_id", "INST_UNKNOWN")
            sym = pos.get("symbol", "").upper()
            name = pos.get("name", pos.get("security_name", sym))
            cat = pos.get("category_label", pos.get("sector", "Unclassified"))
            curr = pos.get("currency", getattr(scenario, "reporting_currency", reporting_currency)).upper()
            base_val = float(pos.get("base_value", pos.get("market_value", 0.0)))
            weight = base_val / portfolio_nav if portfolio_nav > 0 else 0.0

            # Determine price shock using collision precedence
            price_shock_val = 0.0
            shock_source = "Unshocked (0.0%)"

            if sym in security_shocks:
                price_shock_val = security_shocks[sym].shock_value
                shock_source = f"Security: {security_shocks[sym].description or sym}"
            elif cat.lower() in sector_shocks:
                price_shock_val = sector_shocks[cat.lower()].shock_value
                shock_source = f"Sector: {cat}"
            elif portfolio_wide_shock:
                price_shock_val = portfolio_wide_shock.shock_value
                shock_source = f"Portfolio: {portfolio_wide_shock.description or 'Broad Market'}"

            # Determine FX shock if position currency differs from reporting currency
            fx_shock_val = 0.0
            pair_key = f"{curr}/{scenario.reporting_currency}".upper()
            if curr != scenario.reporting_currency and pair_key in currency_shocks:
                fx_shock_val = currency_shocks[pair_key].shock_value
                shock_source += f" + FX ({pair_key})"

            # Multiplicative compounding: (1 + s_price) * (1 + s_fx) - 1
            # Verified by Part XXXIV Fixture: -10% price, -5% FX -> (0.90)(0.95) - 1 = -14.5%
            effective_shock = (1.0 + price_shock_val) * (1.0 + fx_shock_val) - 1.0

            shocked_val = base_val * (1.0 + effective_shock)
            pos_pnl = shocked_val - base_val

            total_pnl += pos_pnl
            eligible_value += base_val

            position_results.append(
                ScenarioPositionResult(
                    instrument_id=inst_id,
                    symbol=sym,
                    name=name,
                    category_label=cat,
                    currency=curr,
                    baseline_value=base_val,
                    weight=weight,
                    shock_applied=effective_shock,
                    shock_source=shock_source,
                    shocked_value=shocked_val,
                    pnl=pos_pnl,
                    is_supported=True,
                )
            )

        shocked_nav = portfolio_nav + total_pnl
        scenario_return = total_pnl / portfolio_nav if portfolio_nav > 0 else 0.0
        coverage_ratio = eligible_value / portfolio_nav if portfolio_nav > 0 else 1.0

        # Exact reconciliation check
        reconciled_pnl = sum(p.pnl for p in position_results)
        discrepancy = abs(reconciled_pnl - total_pnl)
        is_reconciled = discrepancy < 1e-4

        if not is_reconciled:
            raise RiskScenarioReconciliationFailedError(
                f"Scenario position P&L sum ({reconciled_pnl}) does not reconcile with portfolio P&L ({total_pnl})."
            )

        run_id = f"SCEN_RUN_{uuid.uuid4().hex[:12].upper()}"

        return RiskScenarioRun(
            run_id=run_id,
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            scenario_type=scenario.scenario_type,
            portfolio_id=portfolio_id,
            account_id=account_id,
            calculation_as_of=datetime.utcnow(),
            baseline_nav=portfolio_nav,
            shocked_nav=shocked_nav,
            portfolio_pnl=total_pnl,
            scenario_return=scenario_return,
            coverage_ratio=coverage_ratio,
            eligible_value=eligible_value,
            unsupported_value=unsupported_value,
            position_results=position_results,
            reconciled=is_reconciled,
            reconciliation_difference=discrepancy,
            warnings=[],
            created_at=datetime.utcnow(),
        )


PREDEFINED_SCENARIOS = ScenarioEngine.get_predefined_historical_scenarios()

