"""Master QuantLib Options Strategy Service Orchestrator (Stage 142)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from atlas.auth import AuthPrincipal
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import (
    AtlasOptionContract,
    ExerciseStyle,
    LegSide,
    OptionType,
)
from atlas.options.strategies.templates import StrategyTemplateDefinition
from atlas.options.market_data.capabilities import OptionsEntitlementRegistry
from atlas.options.market_data.quotes import OptionQuoteStore
from atlas.options.quant.domain import (
    OptionPricingResult,
    PricingModelFamily,
    QuantModelGreeks,
    QuantPricingModelDefinition,
    QuantStrategyLeg,
    STAGE_142_DISCLAIMERS,
)
from atlas.options.quant.errors import (
    QuantContractNotFoundError,
    QuantEntitlementRequiredError,
    QuantModelIncompatibleError,
)
from atlas.options.quant.greeks.aggregator import aggregate_strategy_greeks
from atlas.options.quant.persistence.repository import QuantStrategyRepository
from atlas.options.quant.pricing.registry import ModelRegistry
from atlas.options.quant.pricing.service import OptionPricingService
from atlas.options.quant.risk.diagnostics import RiskDiagnosticsEngine
from atlas.options.quant.scenarios.engine import (
    ScenarioEngine,
    ScenarioMatrixResult,
    ScenarioOutcome,
)
from atlas.options.quant.strategies.breakeven import calculate_breakevens_and_bounds
from atlas.options.quant.strategies.comparison import compare_strategies
from atlas.options.quant.strategies.models import (
    QuantStrategyDefinition,
    StrategyValuationResult,
)
from atlas.options.quant.strategies.payoff import generate_expiration_payoff_curve
from atlas.options.quant.strategies.templates import CANONICAL_25_TEMPLATES
from atlas.options.quant.strategies.valuation import (
    generate_pre_expiration_curve,
    value_strategy_mark_to_market,
)
from atlas.options.quant.volatility.surfaces import (
    ImpliedVolatilitySurface,
    VolatilitySurfaceBuilder,
)


class AtlasQuantOptionsService:
    """Master institutional options quantitative pricing and strategy engine."""

    def __init__(
        self,
        contract_registry: Optional[OptionContractRegistry] = None,
        quote_store: Optional[OptionQuoteStore] = None,
        entitlements: Optional[OptionsEntitlementRegistry] = None,
        model_registry: Optional[ModelRegistry] = None,
        strategy_repository: Optional[QuantStrategyRepository] = None,
    ):
        self.contract_registry = contract_registry or OptionContractRegistry()
        self.quote_store = quote_store or OptionQuoteStore()
        self.entitlements = entitlements or OptionsEntitlementRegistry()
        self.model_registry = model_registry or ModelRegistry()
        self.strategy_repository = strategy_repository or QuantStrategyRepository()

        self.pricing_service = OptionPricingService(
            contract_registry=self.contract_registry,
            quote_store=self.quote_store,
            model_registry=self.model_registry,
        )

    def get_capabilities(self) -> Dict[str, Any]:
        """Expose supported pricing models, strategy templates, calculation boundaries, and disclaimers."""
        return {
            "stage": 142,
            "system_name": "ATLAS QuantLib Derivatives & Strategy Engine",
            "quantlib_version": "1.44",
            "supported_model_families": [m.value for m in PricingModelFamily],
            "registered_models_count": len(self.model_registry.list_models()),
            "strategy_templates_count": len(CANONICAL_25_TEMPLATES),
            "disclaimers": STAGE_142_DISCLAIMERS,
            "security_policies": {
                "tenant_isolation_enforced": True,
                "zero_fabrication_enforced": True,
                "multi_expiration_mark_to_market_supported": True,
                "automated_trading_allowed": False,
                "broker_order_routing_allowed": False,
            },
        }

    def list_pricing_models(self) -> List[QuantPricingModelDefinition]:
        """Return list of all registered QuantLib pricing model definitions."""
        return self.model_registry.list_models()

    def get_pricing_model(self, model_id: str) -> Optional[QuantPricingModelDefinition]:
        """Retrieve single pricing model definition."""
        return self.model_registry.get_model(model_id)

    def list_strategy_templates(self) -> List[StrategyTemplateDefinition]:
        """Return metadata for 25 canonical options strategy templates."""
        return list(CANONICAL_25_TEMPLATES.values())

    def price_contract(
        self,
        contract_id: str,
        evaluation_date: str,
        spot_price: float,
        risk_free_rate: float = 0.05,
        dividend_yield: float = 0.0,
        volatility: Optional[float] = None,
        model_id: Optional[str] = None,
        dividend_items: Optional[List[Dict[str, Any]]] = None,
        numerical_steps: int = 100,
        provider_source_id: str = "SRC_CBOE_AUTHORIZED",
        principal: Optional[AuthPrincipal] = None,
    ) -> OptionPricingResult:
        """Price a single contract with license entitlement verification (Test R)."""
        self.entitlements.check_entitlement(provider_source_id)

        return self.pricing_service.price_contract(
            contract_id=contract_id,
            evaluation_date=evaluation_date,
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
            model_id=model_id,
            dividend_items=dividend_items,
            numerical_steps=numerical_steps,
        )

    def price_batch(
        self,
        contract_ids: List[str],
        evaluation_date: str,
        spot_price: float,
        risk_free_rate: float = 0.05,
        dividend_yield: float = 0.0,
        model_id: Optional[str] = None,
        provider_source_id: str = "SRC_CBOE_AUTHORIZED",
    ) -> List[OptionPricingResult]:
        """Price multiple contracts in batch with entitlement verification."""
        self.entitlements.check_entitlement(provider_source_id)

        return self.pricing_service.price_batch(
            contract_ids=contract_ids,
            evaluation_date=evaluation_date,
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            model_id=model_id,
        )

    def analyze_strategy(
        self,
        legs: List[QuantStrategyLeg],
        strategy_name: str = "Custom Strategy",
        underlying_symbol: str = "SPY",
        evaluation_date: str = "2024-05-20",
        spot_price: float = 500.0,
        risk_free_rate: float = 0.05,
        dividend_yield: float = 0.0,
        volatility: float = 0.20,
        total_fees: float = 0.0,
        model_id: str = "BLACK_SCHOLES_MERTON",
    ) -> StrategyValuationResult:
        """Perform comprehensive quantitative analysis on a multi-leg strategy."""
        if not legs:
            raise QuantModelIncompatibleError(model_id, "Strategy must contain at least one leg.")

        # 1. Calculate net opening cash flow:
        # Long options pay premium (outflow: -1), Short options collect premium (inflow: +1)
        net_opening_cash_flow = 0.0
        for leg in legs:
            sign = -1.0 if leg.side in (LegSide.LONG_CALL, LegSide.LONG_PUT) else 1.0
            net_opening_cash_flow += sign * float(leg.quantity) * float(leg.multiplier) * leg.entry_premium
            net_opening_cash_flow -= leg.custom_fee

        is_net_debit = net_opening_cash_flow < 0

        # 2. Check for multi-expiration structure
        expirations = sorted(list({leg.expiration_date for leg in legs}))
        is_multi_exp = len(expirations) > 1

        # 3. Breakevens and Bounds (Expiration cutoff for compatible single-expiration or primary expiration)
        breakevens, max_profit, max_loss, is_unbounded_profit, is_unbounded_loss = (
            calculate_breakevens_and_bounds(legs, total_fees)
        )

        # 4. Expiration payoff curve (piecewise linear intrinsic value at T=Expiry)
        payoff_curve = generate_expiration_payoff_curve(
            legs=legs,
            breakevens=breakevens,
            total_fees=total_fees,
            steps=100,
        )

        # 5. Pre-expiration mark-to-market curve using QuantLib (solves Test K for multi-expiration calendar spreads!)
        model_family = PricingModelFamily[model_id] if model_id in PricingModelFamily.__members__ else PricingModelFamily.BLACK_SCHOLES_MERTON
        pre_exp_curve = generate_pre_expiration_curve(
            legs=legs,
            evaluation_date=evaluation_date,
            net_opening_cash_flow=net_opening_cash_flow,
            total_fees=total_fees,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
            model_family=model_family,
            steps=50,
        )

        # 6. Aggregate Greeks at current spot price
        _, _, agg_greeks = value_strategy_mark_to_market(
            legs=legs,
            spot_price=spot_price,
            evaluation_date=evaluation_date,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=volatility,
            model_family=model_family,
            net_opening_cash_flow=net_opening_cash_flow,
            total_fees=total_fees,
        )

        # 7. Operational & Assignment Risk Diagnostics
        risk_warnings = RiskDiagnosticsEngine.evaluate_strategy_risks(
            legs=legs,
            current_spot=spot_price,
            is_unbounded_loss=is_unbounded_loss,
        )

        return StrategyValuationResult(
            strategy_name=strategy_name,
            underlying_symbol=underlying_symbol,
            evaluation_date=evaluation_date,
            legs=legs,
            net_opening_cash_flow=round(net_opening_cash_flow, 2),
            is_net_debit=is_net_debit,
            total_estimated_fees=total_fees,
            breakevens=breakevens,
            max_profit=max_profit,
            max_loss=max_loss,
            is_unbounded_profit=is_unbounded_profit,
            is_unbounded_loss=is_unbounded_loss,
            expiration_payoff_curve=payoff_curve,
            pre_expiration_curve=pre_exp_curve,
            aggregate_greeks=agg_greeks,
            risk_warnings=risk_warnings,
            disclaimers=STAGE_142_DISCLAIMERS,
            is_multi_expiration=is_multi_exp,
        )

    def run_scenario_matrix(
        self,
        legs: List[QuantStrategyLeg],
        base_spot: float,
        base_eval_date: str,
        base_vol: float = 0.20,
        base_rate: float = 0.05,
        dividend_yield: float = 0.0,
        net_opening_cash_flow: float = 0.0,
        total_fees: float = 0.0,
        model_id: str = "BLACK_SCHOLES_MERTON",
    ) -> ScenarioMatrixResult:
        """Generate 2D Spot vs Volatility scenario matrix."""
        model_family = PricingModelFamily[model_id] if model_id in PricingModelFamily.__members__ else PricingModelFamily.BLACK_SCHOLES_MERTON
        return ScenarioEngine.generate_spot_vol_matrix(
            legs=legs,
            base_spot=base_spot,
            base_eval_date=base_eval_date,
            base_vol=base_vol,
            base_rate=base_rate,
            dividend_yield=dividend_yield,
            net_opening_cash_flow=net_opening_cash_flow,
            total_fees=total_fees,
            model_family=model_family,
        )

    def compare_strategy_results(
        self,
        results: List[StrategyValuationResult],
    ) -> List[Any]:
        """Perform side-by-side comparison of multiple strategy outcomes."""
        return compare_strategies(results)

    def save_user_strategy(
        self,
        strategy: QuantStrategyDefinition,
        principal: Optional[AuthPrincipal] = None,
    ) -> QuantStrategyDefinition:
        """Persist a strategy definition with tenant isolation."""
        return self.strategy_repository.save_strategy(strategy, principal=principal)

    def get_user_strategy(
        self,
        strategy_id: str,
        principal: Optional[AuthPrincipal] = None,
    ) -> Optional[QuantStrategyDefinition]:
        """Retrieve a private strategy definition enforcing tenant authorization (Test S)."""
        return self.strategy_repository.get_strategy(strategy_id, principal=principal)

    def list_user_strategies(
        self,
        principal: AuthPrincipal,
    ) -> List[QuantStrategyDefinition]:
        """List strategies accessible to principal."""
        return self.strategy_repository.list_strategies_for_user(principal)

    def build_volatility_surface(
        self,
        underlying_symbol: str,
        evaluation_date: str,
        observations: List[Dict[str, Any]],
        strict_validation: bool = False,
    ) -> ImpliedVolatilitySurface:
        """Build and calibrate an implied volatility surface."""
        return VolatilitySurfaceBuilder.build_surface(
            underlying_symbol=underlying_symbol,
            evaluation_date=evaluation_date,
            observations=observations,
            strict_validation=strict_validation,
        )

    def execute_ai_quant_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        principal: Optional[AuthPrincipal] = None,
    ) -> Dict[str, Any]:
        """Execute authorized read-only AI quantitative derivatives tools (Part LXVIII)."""
        if tool_name == "atlas.options.price_contract":
            cid = params.get("contract_id", "")
            eval_d = params.get("evaluation_date", "2024-05-20")
            spot = float(params.get("spot_price", 500.0))
            mid = params.get("model_id", "BLACK_SCHOLES_MERTON")
            res = self.price_contract(cid, eval_d, spot, model_id=mid, principal=principal)
            return {
                "theoretical_price": res.theoretical_price,
                "observed_mark": res.observed_market_mark,
                "model_market_diff": res.model_market_difference,
                "delta": res.greeks.delta,
                "gamma": res.greeks.gamma,
                "theta_per_day": res.greeks.theta_per_day,
                "vega_per_point": res.greeks.vega_per_point,
                "model_used": res.model_id,
            }

        elif tool_name == "atlas.options.get_pricing_model":
            mid = params.get("model_id", "BLACK_SCHOLES_MERTON")
            m = self.get_pricing_model(mid)
            if not m:
                return {"error": f"Model '{mid}' not found."}
            return {
                "model_id": m.model_id,
                "name": m.name,
                "family": m.family.value,
                "description": m.description,
                "supported_exercise_styles": [s.value for s in m.supported_exercise_styles],
                "supports_analytic_greeks": m.supports_analytic_greeks,
            }

        elif tool_name == "atlas.options.get_risk_warnings":
            unbounded = bool(params.get("is_unbounded_loss", False))
            spot = float(params.get("spot_price", 500.0))
            warnings = RiskDiagnosticsEngine.evaluate_strategy_risks([], spot, unbounded)
            return {"warnings": warnings}

        else:
            return {
                "error": f"Tool '{tool_name}' is not recognized or not authorized.",
                "disclaimer": "ATLAS quantitative tools are strictly read-only and execute 0 broker transactions.",
            }
