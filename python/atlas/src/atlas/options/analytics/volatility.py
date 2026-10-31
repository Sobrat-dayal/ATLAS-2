"""Implied Volatility Smile, Skew and Term Structure Analytics (Stage 141).

Displays source-provided implied volatility observations without artificial interpolation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import OptionType
from atlas.options.market_data.quotes import OptionQuoteStore


class OptionsVolatilityAnalytics:
    """Computes empirical volatility curves from available source quotes."""

    def __init__(self, contract_registry: OptionContractRegistry, quote_store: OptionQuoteStore):
        self.contract_registry = contract_registry
        self.quote_store = quote_store

    def get_volatility_smile(
        self,
        underlying_symbol: str,
        expiration_date: str,
    ) -> Dict[str, Any]:
        """Return observed IV smile across strikes for calls and puts."""
        contracts = self.contract_registry.list_contracts_for_underlying(
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
        )

        calls_iv: List[Dict[str, Any]] = []
        puts_iv: List[Dict[str, Any]] = []

        for c in contracts:
            quote = self.quote_store.get_quote(c.option_contract_id)
            if quote and quote.implied_volatility is not None:
                item = {
                    "strike": c.strike_price,
                    "implied_volatility": quote.implied_volatility,
                    "delta": quote.greeks.delta if quote.greeks else None,
                    "is_delayed": quote.is_delayed,
                }
                if c.option_type == OptionType.CALL:
                    calls_iv.append(item)
                else:
                    puts_iv.append(item)

        calls_iv.sort(key=lambda x: x["strike"])
        puts_iv.sort(key=lambda x: x["strike"])

        return {
            "underlying_symbol": underlying_symbol.upper(),
            "expiration_date": expiration_date,
            "calls_smile": calls_iv,
            "puts_smile": puts_iv,
            "data_source": "SRC_CBOE_AUTHORIZED",
            "disclaimer": "Implied volatility reflects model-dependent market observations, not future realized volatility forecasts.",
        }

    def get_volatility_term_structure(
        self,
        underlying_symbol: str,
        atm_strike: float = 100.0,
    ) -> Dict[str, Any]:
        """Return observed near-ATM IV across expirations."""
        expirations = self.contract_registry.list_expirations_for_underlying(underlying_symbol)
        term_structure: List[Dict[str, Any]] = []

        for exp in expirations:
            contracts = self.contract_registry.list_contracts_for_underlying(
                underlying_symbol=underlying_symbol,
                expiration_date=exp,
                option_type=OptionType.CALL,
            )
            # Find closest strike to atm_strike
            if not contracts:
                continue
            closest_contract = min(contracts, key=lambda c: abs(c.strike_price - atm_strike))
            quote = self.quote_store.get_quote(closest_contract.option_contract_id)

            if quote and quote.implied_volatility is not None:
                term_structure.append({
                    "expiration_date": exp,
                    "strike_price": closest_contract.strike_price,
                    "implied_volatility": quote.implied_volatility,
                    "days_to_expiration": 30,  # approximate
                })

        return {
            "underlying_symbol": underlying_symbol.upper(),
            "atm_strike": atm_strike,
            "term_structure": term_structure,
        }
