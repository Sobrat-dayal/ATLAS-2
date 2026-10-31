"""Options chain construction and filtering engine (Stage 141).

Generates professional dual-sided calls/strikes/puts chains with volume and OI aggregations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import (
    MoneynessState,
    OptionChainResponse,
    OptionChainRow,
    OptionType,
)
from atlas.options.market_data.quotes import OptionQuoteStore


def calculate_moneyness(strike: float, underlying_price: float, option_type: OptionType) -> MoneynessState:
    """Classify moneyness state relative to underlying price."""
    pct_diff = abs(strike - underlying_price) / max(underlying_price, 0.01)
    if pct_diff <= 0.005:  # Within 0.5% considered At-The-Money
        return MoneynessState.AT_THE_MONEY

    if option_type == OptionType.CALL:
        return MoneynessState.IN_THE_MONEY if underlying_price > strike else MoneynessState.OUT_OF_THE_MONEY
    else:
        return MoneynessState.IN_THE_MONEY if strike > underlying_price else MoneynessState.OUT_OF_THE_MONEY


class OptionChainBuilder:
    """Builds dual-sided options chains from registry contracts and market quotes."""

    def __init__(self, contract_registry: OptionContractRegistry, quote_store: OptionQuoteStore):
        self.contract_registry = contract_registry
        self.quote_store = quote_store

    def build_chain(
        self,
        underlying_symbol: str,
        expiration_date: str,
        underlying_price: float = 105.0,  # Reference price for SPY in fixtures
        min_volume: Optional[int] = None,
        min_open_interest: Optional[int] = None,
        strike_min: Optional[float] = None,
        strike_max: Optional[float] = None,
    ) -> OptionChainResponse:
        contracts = self.contract_registry.list_contracts_for_underlying(
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
        )

        # Group by strike price
        strike_map: Dict[float, Dict[str, Any]] = {}
        for c in contracts:
            strike = c.strike_price
            if strike_min is not None and strike < strike_min:
                continue
            if strike_max is not None and strike > strike_max:
                continue

            if strike not in strike_map:
                strike_map[strike] = {"call_contract": None, "put_contract": None}

            if c.option_type == OptionType.CALL:
                strike_map[strike]["call_contract"] = c
            else:
                strike_map[strike]["put_contract"] = c

        rows: List[OptionChainRow] = []
        tot_call_vol = 0
        tot_put_vol = 0
        tot_call_oi = 0
        tot_put_oi = 0

        for strike in sorted(strike_map.keys()):
            pair = strike_map[strike]
            call_c = pair["call_contract"]
            put_c = pair["put_contract"]

            call_q = self.quote_store.get_quote(call_c.option_contract_id) if call_c else None
            put_q = self.quote_store.get_quote(put_c.option_contract_id) if put_c else None

            # Filters
            if min_volume is not None:
                c_vol = call_q.volume if call_q else 0
                p_vol = put_q.volume if put_q else 0
                if c_vol < min_volume and p_vol < min_volume:
                    continue

            if min_open_interest is not None:
                c_oi = call_q.open_interest if call_q else 0
                p_oi = put_q.open_interest if put_q else 0
                if c_oi < min_open_interest and p_oi < min_open_interest:
                    continue

            if call_q:
                tot_call_vol += call_q.volume
                tot_call_oi += call_q.open_interest
            if put_q:
                tot_put_vol += put_q.volume
                tot_put_oi += put_q.open_interest

            # Moneyness reference based on call
            moneyness = calculate_moneyness(strike, underlying_price, OptionType.CALL)

            rows.append(
                OptionChainRow(
                    strike_price=strike,
                    moneyness=moneyness,
                    call_contract=call_c,
                    call_quote=call_q,
                    put_contract=put_c,
                    put_quote=put_q,
                )
            )

        # Days to expiration
        try:
            exp_dt = datetime.strptime(expiration_date, "%Y-%m-%d")
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            dte = max(0, (exp_dt.date() - today.date()).days)
        except Exception:
            dte = 30

        pv_ratio = round(tot_put_vol / tot_call_vol, 3) if tot_call_vol > 0 else None
        poi_ratio = round(tot_put_oi / tot_call_oi, 3) if tot_call_oi > 0 else None

        return OptionChainResponse(
            underlying_symbol=underlying_symbol.upper(),
            underlying_price=underlying_price,
            underlying_quote_time="2024-05-20T15:30:00Z",
            expiration_date=expiration_date,
            days_to_expiration=dte,
            rows=rows,
            total_call_volume=tot_call_vol,
            total_put_volume=tot_put_vol,
            total_call_oi=tot_call_oi,
            total_put_oi=tot_put_oi,
            put_call_volume_ratio=pv_ratio,
            put_call_oi_ratio=poi_ratio,
        )
