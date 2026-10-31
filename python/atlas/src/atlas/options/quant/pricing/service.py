"""Option Pricing Service integrating QuantLib and Canonical Contracts (Stage 142)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import AtlasOptionContract, ExerciseStyle, OptionType
from atlas.options.market_data.quotes import OptionQuoteStore
from atlas.options.quant.domain import (
    MarketInputSnapshot,
    OptionPricingResult,
    PricingModelFamily,
)
from atlas.options.quant.errors import (
    QuantContractNotFoundError,
    QuantModelIncompatibleError,
    QuantResourceQuotaExceededError,
)
from atlas.options.quant.pricing.registry import ModelRegistry
from atlas.options.quant.quantlib.adapter import QuantLibAdapter


class OptionPricingService:
    """Service orchestrating theoretical derivative pricing and market comparison."""

    def __init__(
        self,
        contract_registry: OptionContractRegistry,
        quote_store: OptionQuoteStore,
        model_registry: Optional[ModelRegistry] = None,
    ):
        self.contract_registry = contract_registry
        self.quote_store = quote_store
        self.model_registry = model_registry or ModelRegistry()

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
        snapshot_id: Optional[str] = None,
    ) -> OptionPricingResult:
        """Price a single canonical option contract."""
        contract = self.contract_registry.get_contract(contract_id)
        if not contract:
            raise QuantContractNotFoundError(contract_id)

        # 1. Fetch available quote
        quote = self.quote_store.get_quote(contract_id)
        obs_bid = quote.bid if quote else None
        obs_ask = quote.ask if quote else None
        obs_mark = None
        if obs_bid is not None and obs_ask is not None:
            obs_mark = round((obs_bid + obs_ask) / 2.0, 2)
        elif quote and quote.last_price is not None:
            obs_mark = quote.last_price

        # 2. Determine volatility
        vol = volatility
        if vol is None:
            if quote and quote.implied_volatility:
                vol = quote.implied_volatility
            else:
                vol = 0.20  # Baseline 20% analytical default if not in quote

        # 3. Model validation
        effective_model_id = model_id
        if effective_model_id is None:
            if contract.exercise_style == ExerciseStyle.AMERICAN:
                effective_model_id = "BARONE_ADESI_WHALEY"
            else:
                effective_model_id = "BLACK_SCHOLES_MERTON"

        has_divs = bool(dividend_items and len(dividend_items) > 0)
        model_def = self.model_registry.validate_model_compatibility(
            effective_model_id,
            contract.exercise_style,
            has_discrete_dividends=has_divs,
        )

        # 4. Invoke QuantLib adapter
        npv, greeks, diag = QuantLibAdapter.price_vanilla_contract(
            option_type=contract.option_type,
            strike_price=contract.strike_price,
            expiration_date=contract.expiration_date,
            evaluation_date=evaluation_date,
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            dividend_yield=dividend_yield,
            volatility=vol,
            exercise_style=contract.exercise_style,
            model_family=model_def.family,
            dividend_items=dividend_items,
            numerical_steps=numerical_steps,
        )

        theo_price = round(npv, 4)
        model_market_diff = None
        if obs_mark is not None:
            model_market_diff = round(theo_price - obs_mark, 4)

        return OptionPricingResult(
            pricing_run_id=f"run_{uuid.uuid4().hex[:12]}",
            contract_id=contract.option_contract_id,
            underlying_symbol=contract.underlying_symbol,
            strike_price=contract.strike_price,
            expiration_date=contract.expiration_date,
            exercise_style=contract.exercise_style,
            model_id=effective_model_id,
            theoretical_price=theo_price,
            observed_market_bid=obs_bid,
            observed_market_ask=obs_ask,
            observed_market_mark=obs_mark,
            model_market_difference=model_market_diff,
            contract_multiplier=contract.contract_multiplier,
            currency=contract.strike_currency,
            greeks=greeks,
            diagnostics=diag,
            valuation_date=evaluation_date,
            market_snapshot_id=snapshot_id or f"snap_{uuid.uuid4().hex[:8]}",
        )

    def price_batch(
        self,
        contract_ids: List[str],
        evaluation_date: str,
        spot_price: float,
        risk_free_rate: float = 0.05,
        dividend_yield: float = 0.0,
        model_id: str = "BLACK_SCHOLES_MERTON",
        max_batch_size: int = 100,
    ) -> List[OptionPricingResult]:
        """Price a batch of option contracts with resource quota enforcement."""
        if len(contract_ids) > max_batch_size:
            raise QuantResourceQuotaExceededError("batch_pricing", len(contract_ids), max_batch_size)

        results: List[OptionPricingResult] = []
        for cid in contract_ids:
            res = self.price_contract(
                contract_id=cid,
                evaluation_date=evaluation_date,
                spot_price=spot_price,
                risk_free_rate=risk_free_rate,
                dividend_yield=dividend_yield,
                model_id=model_id,
            )
            results.append(res)
        return results
