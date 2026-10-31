"""Trading Activity and Open Interest Analytics (Stage 141).

Differentiates trading volume (period activity) from open interest (point-in-time outstanding contracts).
"""

from __future__ import annotations

from typing import Any, Dict, List
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import OptionType
from atlas.options.market_data.quotes import OptionQuoteStore


class OptionsActivityAnalytics:
    """Aggregates options trading volume and open interest by strike and series."""

    def __init__(self, contract_registry: OptionContractRegistry, quote_store: OptionQuoteStore):
        self.contract_registry = contract_registry
        self.quote_store = quote_store

    def get_strike_activity(
        self,
        underlying_symbol: str,
        expiration_date: str,
    ) -> Dict[str, Any]:
        """Return call and put volume & OI by strike."""
        contracts = self.contract_registry.list_contracts_for_underlying(
            underlying_symbol=underlying_symbol,
            expiration_date=expiration_date,
        )

        strike_data: Dict[float, Dict[str, int]] = {}
        for c in contracts:
            s = c.strike_price
            if s not in strike_data:
                strike_data[s] = {"call_volume": 0, "put_volume": 0, "call_oi": 0, "put_oi": 0}

            q = self.quote_store.get_quote(c.option_contract_id)
            if q:
                if c.option_type == OptionType.CALL:
                    strike_data[s]["call_volume"] = q.volume
                    strike_data[s]["call_oi"] = q.open_interest
                else:
                    strike_data[s]["put_volume"] = q.volume
                    strike_data[s]["put_oi"] = q.open_interest

        sorted_strikes = sorted(strike_data.keys())
        activity_bars = [
            {"strike": s, **strike_data[s]}
            for s in sorted_strikes
        ]

        total_call_vol = sum(d["call_volume"] for d in strike_data.values())
        total_put_vol = sum(d["put_volume"] for d in strike_data.values())
        total_call_oi = sum(d["call_oi"] for d in strike_data.values())
        total_put_oi = sum(d["put_oi"] for d in strike_data.values())

        return {
            "underlying_symbol": underlying_symbol.upper(),
            "expiration_date": expiration_date,
            "strikes": activity_bars,
            "total_call_volume": total_call_vol,
            "total_put_volume": total_put_vol,
            "total_call_oi": total_call_oi,
            "total_put_oi": total_put_oi,
            "put_call_volume_ratio": round(total_put_vol / total_call_vol, 3) if total_call_vol > 0 else None,
            "put_call_oi_ratio": round(total_put_oi / total_call_oi, 3) if total_call_oi > 0 else None,
            "interpretation_note": "Volume reflects executed trades over the session; Open Interest reflects end-of-day clearinghouse settlement from the prior reporting date.",
        }

