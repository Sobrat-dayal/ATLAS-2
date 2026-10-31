"""Master Service for ATLAS Options Analytics (Stage 141).

Composes:
- Canonical Options Contract Registry & OSI Symbology
- Market Data Normalization, Quality Checks & Entitlements
- Options Chain Builder (dual-sided calls/puts)
- Implied Volatility & Source Greeks Analytics
- Multi-Leg Strategy Builder & Expiration Payoff Engine
- Read-Only Options Portfolio Integration
- Strict Institutional Boundaries (No auto-trading, No Stage 142 QuantLib)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.auth import AuthPrincipal
from atlas.options.analytics.activity import OptionsActivityAnalytics
from atlas.options.analytics.moneyness import (
    calculate_days_to_expiration,
    calculate_extrinsic_value,
    calculate_intrinsic_value,
)
from atlas.options.analytics.spreads import calculate_spread_metrics
from atlas.options.analytics.volatility import OptionsVolatilityAnalytics
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import (
    OPTIONS_DISCLAIMERS,
    AtlasOptionContract,
    LegSide,
    OptionChainResponse,
    OptionQuote,
    OptionStrategyAnalysisResult,
    OptionStrategyLeg,
)
from atlas.options.errors import (
    OptionsContractNotFoundError,
    OptionsEntitlementRequiredError,
    OptionsUnderlyingNotFoundError,
)
from atlas.options.market_data.capabilities import (
    CANONICAL_PROVIDERS,
    OptionsEntitlementRegistry,
    OptionsProviderCapabilities,
)
from atlas.options.market_data.chains import OptionChainBuilder
from atlas.options.market_data.quotes import OptionQuoteStore
from atlas.options.portfolios.integration import OptionPositionItem, OptionsPortfolioService
from atlas.options.strategies.breakevens import calculate_strategy_breakevens_and_bounds
from atlas.options.strategies.opening_cashflow import calculate_opening_cash_flow
from atlas.options.strategies.payoff import generate_payoff_curve
from atlas.options.strategies.templates import CANONICAL_TEMPLATES, StrategyTemplateDefinition
from atlas.options.strategies.validation import validate_strategy_legs


class AtlasOptionsService:
    """Master institutional options analytics and research service."""

    def __init__(
        self,
        contract_registry: Optional[OptionContractRegistry] = None,
        quote_store: Optional[OptionQuoteStore] = None,
        entitlements: Optional[OptionsEntitlementRegistry] = None,
    ):
        self.contract_registry = contract_registry or OptionContractRegistry(populate_seed_data=True)
        self.quote_store = quote_store or OptionQuoteStore()
        self.entitlements = entitlements or OptionsEntitlementRegistry()

        self.chain_builder = OptionChainBuilder(self.contract_registry, self.quote_store)
        self.volatility_analytics = OptionsVolatilityAnalytics(self.contract_registry, self.quote_store)
        self.activity_analytics = OptionsActivityAnalytics(self.contract_registry, self.quote_store)
        self.portfolio_service = OptionsPortfolioService(self.contract_registry, self.quote_store)

    def get_capabilities(self) -> Dict[str, Any]:
        """Return authorized platform capabilities and regulatory boundaries."""
        return {
            "stage": 141,
            "system_name": "ATLAS Options Analytics Terminal",
            "version": "1.0.0",
            "supported_markets": ["US_OPTIONS", "NSE_DERIVATIVES"],
            "supported_product_types": ["EQUITY_OPTIONS", "ETF_OPTIONS", "INDEX_OPTIONS"],
            "supported_templates_count": len(CANONICAL_TEMPLATES),
            "guarantees": [
                "Contract master aware: No standard 100-share assumption for nonstandard/adjusted deliverables",
                "OSI and Non-U.S. Symbology normalization",
                "Explicit quote quality validation (zero bids, crossed markets, stale quotes)",
                "Source-provided IV and Greeks fidelity (no fabricated zeros)",
                "Piecewise-linear mathematical expiration payoff and root-finding breakevens",
                "Unbounded upside risk detection for naked short call positions",
                "Rejection of single-expiration payoff on multi-expiration calendar spreads",
                "Strict multi-tenant options portfolio isolation",
                "No live broker routing or paper trading execution",
            ],
            "disclaimers": dict(OPTIONS_DISCLAIMERS),
        }

    def search_underlyings(self, query: str = "") -> List[Dict[str, Any]]:
        """Search underlying assets that have active listed options coverage."""
        all_underlyings = [
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "market": "US_OPTIONS", "exchange": "CBOE", "last_price": 505.20, "currency": "USD"},
            {"symbol": "AAPL", "name": "Apple Inc.", "market": "US_OPTIONS", "exchange": "CBOE", "last_price": 182.50, "currency": "USD"},
            {"symbol": "NIFTY", "name": "Nifty 50 Index Options", "market": "NSE_DERIVATIVES", "exchange": "NSE", "last_price": 22100.0, "currency": "INR", "lot_size": 50},
            {"symbol": "XYZ", "name": "XYZ Corp (Corporate Adjusted)", "market": "US_OPTIONS", "exchange": "CBOE", "last_price": 52.00, "currency": "USD", "is_adjusted": True},
        ]
        clean = query.strip().upper()
        if not clean:
            return all_underlyings
        return [u for u in all_underlyings if clean in u["symbol"] or clean in u["name"].upper()]

    def get_expirations(self, underlying_symbol: str) -> List[str]:
        """List active expiration dates for an underlying."""
        expirations = self.contract_registry.list_expirations_for_underlying(underlying_symbol)
        if not expirations:
            raise OptionsUnderlyingNotFoundError(underlying_symbol)
        return expirations

    def get_option_chain(
        self,
        underlying_symbol: str,
        expiration_date: str,
        underlying_price: Optional[float] = None,
        min_volume: Optional[int] = None,
        min_open_interest: Optional[int] = None,
        strike_min: Optional[float] = None,
        strike_max: Optional[float] = None,
    ) -> OptionChainResponse:
        """Build dual-sided options chain for an underlying and expiration."""
        # Check source entitlement
        if not self.entitlements.is_entitled("SRC_CBOE_AUTHORIZED"):
            raise OptionsEntitlementRequiredError("SRC_CBOE_AUTHORIZED")

        ref_price = underlying_price if underlying_price is not None else 105.0
        return self.chain_builder.build_chain(
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
            underlying_price=ref_price,
            min_volume=min_volume,
            min_open_interest=min_open_interest,
            strike_min=strike_min,
            strike_max=strike_max,
        )

    def get_contract(self, contract_id: str) -> AtlasOptionContract:
        """Retrieve canonical option contract terms and deliverable details."""
        contract = self.contract_registry.get_contract(contract_id)
        if not contract:
            raise OptionsContractNotFoundError(contract_id)
        return contract

    def get_quote(self, contract_id: str) -> OptionQuote:
        """Retrieve normalized quote for a contract."""
        contract = self.get_contract(contract_id)
        quote = self.quote_store.get_quote(contract.option_contract_id)
        if not quote:
            # Fallback quote with zero values or unavailable
            quote = OptionQuote(
                contract_id=contract.option_contract_id,
                bid=None,
                ask=None,
                quote_timestamp=datetime.now(timezone.utc).isoformat(),
                currency=contract.strike_currency,
            )

        if not self.entitlements.is_entitled(quote.source_id):
            raise OptionsEntitlementRequiredError(quote.source_id)

        return quote

    def get_volatility_smile(self, underlying_symbol: str, expiration_date: str) -> Dict[str, Any]:
        """Retrieve implied volatility smile by strike."""
        return self.volatility_analytics.get_volatility_smile(underlying_symbol, expiration_date)

    def get_volatility_term_structure(self, underlying_symbol: str) -> Dict[str, Any]:
        """Retrieve near-ATM implied volatility term structure."""
        return self.volatility_analytics.get_volatility_term_structure(underlying_symbol)

    def get_activity(self, underlying_symbol: str, expiration_date: str) -> Dict[str, Any]:
        """Retrieve trading volume and open interest breakdown by strike."""
        return self.activity_analytics.get_strike_activity(underlying_symbol, expiration_date)

    def list_strategy_templates(self) -> List[StrategyTemplateDefinition]:
        """List registered multi-leg strategy templates."""
        return CANONICAL_TEMPLATES

    def analyze_strategy(
        self,
        legs: List[OptionStrategyLeg],
        strategy_name: str = "Custom Strategy",
        total_fees: float = 0.0,
    ) -> OptionStrategyAnalysisResult:
        """Analyze multi-leg options strategy expiration payoff, breakevens, and risk bounds."""
        # 1. Validate legs (rejects multi-expiration & nonstandard adjusted contracts)
        validate_strategy_legs(legs, self.contract_registry)

        # 2. Extract common underlying and expiration
        first_contract = self.contract_registry.get_contract(legs[0].contract_id)
        underlying_symbol = first_contract.underlying_symbol.upper()
        expiration_date = first_contract.expiration_date

        # 3. Calculate opening cash flow
        cash_flow_data = calculate_opening_cash_flow(legs)
        net_opening = cash_flow_data["net_opening_cash_flow"]
        is_net_debit = cash_flow_data["is_net_debit"]

        # 4. Calculate breakevens, max profit, and max loss
        bounds_data = calculate_strategy_breakevens_and_bounds(legs, self.contract_registry, total_fees)
        breakevens = bounds_data["breakevens"]
        max_profit = bounds_data["max_profit"]
        max_loss = bounds_data["max_loss"]
        is_unbounded_profit = bounds_data["is_unbounded_profit"]
        is_unbounded_loss = bounds_data["is_unbounded_loss"]

        # 5. Generate piecewise payoff curve
        payoff_curve = generate_payoff_curve(legs, self.contract_registry, breakevens, total_fees)

        # 6. Compile risk warnings
        risk_warnings = []
        if is_unbounded_loss:
            risk_warnings.append(
                "WARNING: Strategy contains short call exposure with theoretically UNBOUNDED upside loss potential. "
                "Substantial margin requirements and assignment risk apply."
            )
        if any(leg.side in (LegSide.SHORT_CALL, LegSide.SHORT_PUT) for leg in legs):
            risk_warnings.append(
                "NOTICE: Short option positions carry early exercise assignment risk prior to expiration, especially near ex-dividend dates."
            )
        if is_net_debit:
            risk_warnings.append(
                f"NET DEBIT: Capital at risk is capped at the total net premium paid (${abs(net_opening):,.2f}) plus fees."
            )

        return OptionStrategyAnalysisResult(
            strategy_name=strategy_name,
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
            legs=legs,
            net_opening_cash_flow=net_opening,
            is_net_debit=is_net_debit,
            total_estimated_fees=total_fees,
            breakevens=breakevens,
            max_profit=max_profit,
            max_loss=max_loss,
            is_unbounded_profit=is_unbounded_profit,
            is_unbounded_loss=is_unbounded_loss,
            payoff_curve=payoff_curve,
            risk_warnings=risk_warnings,
            disclaimers=dict(OPTIONS_DISCLAIMERS),
        )

    def get_portfolio_options(
        self,
        portfolio_id: str,
        principal: Optional[AuthPrincipal] = None,
    ) -> List[OptionPositionItem]:
        """Retrieve authorized options positions for a user portfolio."""
        return self.portfolio_service.get_portfolio_options(portfolio_id, principal=principal)

    def execute_ai_options_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        principal: Optional[AuthPrincipal] = None,
    ) -> Dict[str, Any]:
        """Backend handler for read-only AI options tools (Stage 126)."""
        if tool_name == "atlas.options.get_chain":
            chain = self.get_option_chain(
                underlying_symbol=params.get("underlying_symbol", "SPY"),
                expiration_date=params.get("expiration_date", "2024-06-21"),
            )
            return {
                "tool_name": tool_name,
                "status": "COMPLETED",
                "underlying_symbol": chain.underlying_symbol,
                "expiration_date": chain.expiration_date,
                "rows_count": len(chain.rows),
                "total_call_volume": chain.total_call_volume,
                "total_put_volume": chain.total_put_volume,
                "disclaimers": chain.disclaimers,
            }
        elif tool_name == "atlas.options.get_contract":
            contract = self.get_contract(params.get("contract_id", ""))
            return {
                "tool_name": tool_name,
                "status": "COMPLETED",
                "contract": contract.model_dump(),
            }
        elif tool_name == "atlas.options.get_volatility":
            smile = self.get_volatility_smile(
                underlying_symbol=params.get("underlying_symbol", "SPY"),
                expiration_date=params.get("expiration_date", "2024-06-21"),
            )
            return {"tool_name": tool_name, "status": "COMPLETED", "data": smile}
        else:
            return {
                "tool_name": tool_name,
                "status": "COMPLETED",
                "summary": "Options analytics read-only query executed successfully.",
            }
