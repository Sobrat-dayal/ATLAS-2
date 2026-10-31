"""Historical Options Data Replay and Contract Integration (Stage 143)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import OptionContract
from nautilus_trader.model.objects import Price, Quantity

from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import AtlasOptionContract
from atlas.trading.backtesting.data.instruments import to_nautilus_option
from atlas.trading.backtesting.errors import BacktestDatasetIneligibleError


def validate_options_dataset_eligibility(
    has_options_quotes: bool,
    dataset_id: str,
    requires_market_replay: bool = True,
) -> None:
    """
    Enforce Rule XIX & Test K:
    Underlying equity OHLC data alone is NOT sufficient to simulate historical options trading.
    Rejects options backtests if genuine historical option bid/ask quotes are missing.
    """
    if requires_market_replay and not has_options_quotes:
        raise BacktestDatasetIneligibleError(
            dataset_id=dataset_id,
            reason=(
                "Underlying stock OHLC data alone cannot simulate historical options execution. "
                "Genuine historical option bid/ask quote series are required. "
                "Fabricating synthetic option fills from stock prices is strictly prohibited."
            ),
        )


def build_nautilus_option_quotes(
    raw_option_quotes: List[Dict[str, Any]],
    nautilus_option: OptionContract,
) -> List[QuoteTick]:
    """
    Convert historical option bid/ask quotes into Nautilus QuoteTick objects.
    Enforces that bids are non-negative and markets are uncrossed.
    """
    quote_ticks: List[QuoteTick] = []

    for item in raw_option_quotes:
        ts_ns = int(item["timestamp_ns"])
        bid = float(item["bid"])
        ask = float(item["ask"])
        bid_size = float(item.get("bid_size", 10))
        ask_size = float(item.get("ask_size", 10))

        if bid < 0:
            raise BacktestDatasetIneligibleError(
                dataset_id=str(nautilus_option.id),
                reason=f"Invalid negative bid quote ${bid:.2f} observed.",
            )

        if bid > ask:
            raise BacktestDatasetIneligibleError(
                dataset_id=str(nautilus_option.id),
                reason=f"Crossed market quote observed: Bid ${bid:.2f} > Ask ${ask:.2f}.",
            )

        tick = QuoteTick(
            instrument_id=nautilus_option.id,
            bid_price=Price.from_str(f"{bid:.2f}"),
            ask_price=Price.from_str(f"{ask:.2f}"),
            bid_size=Quantity.from_int(int(bid_size)),
            ask_size=Quantity.from_int(int(ask_size)),
            ts_event=ts_ns,
            ts_init=ts_ns,
        )
        quote_ticks.append(tick)

    return quote_ticks
