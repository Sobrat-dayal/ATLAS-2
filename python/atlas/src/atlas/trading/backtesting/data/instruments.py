"""Instrument Mapping from ATLAS Canonical Models to NautilusTrader Models (Stage 143)."""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from nautilus_trader.model.enums import AssetClass, OptionKind
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CurrencyPair, Equity, OptionContract
from nautilus_trader.model.objects import Currency, Price, Quantity

from atlas.options.domain import AtlasOptionContract, OptionType


def to_nautilus_equity(
    symbol_str: str,
    venue_str: str = "SIM",
    currency_str: str = "USD",
    price_precision: int = 2,
    tick_size: str = "0.01",
    lot_size: int = 1,
) -> Equity:
    """Create a NautilusTrader Equity instrument from canonical inputs."""
    venue = Venue(venue_str)
    sym = Symbol(symbol_str)
    inst_id = InstrumentId(symbol=sym, venue=venue)
    curr = Currency.from_str(currency_str)

    return Equity(
        instrument_id=inst_id,
        raw_symbol=sym,
        currency=curr,
        price_precision=price_precision,
        price_increment=Price.from_str(tick_size),
        lot_size=Quantity.from_int(lot_size),
        ts_event=0,
        ts_init=0,
    )


def to_nautilus_option(
    contract: AtlasOptionContract,
    venue_str: str = "SIM",
) -> OptionContract:
    """Map a Stage 141 canonical AtlasOptionContract into a NautilusTrader OptionContract."""
    venue = Venue(venue_str)
    sym = Symbol(contract.option_contract_id)
    inst_id = InstrumentId(symbol=sym, venue=venue)
    curr = Currency.from_str(contract.strike_currency)

    # Convert expiration date string to unix nanoseconds at 20:00:00 UTC (market close cutoff)
    exp_dt = datetime.datetime.strptime(contract.expiration_date, "%Y-%m-%d").replace(
        hour=20, minute=0, second=0, tzinfo=datetime.timezone.utc
    )
    exp_ns = int(exp_dt.timestamp() * 1_000_000_000)

    # Activation 365 days prior
    act_ns = exp_ns - (365 * 86400 * 1_000_000_000)

    opt_kind = OptionKind.CALL if contract.option_type == OptionType.CALL else OptionKind.PUT

    return OptionContract(
        instrument_id=inst_id,
        raw_symbol=sym,
        asset_class=AssetClass.EQUITY,
        currency=curr,
        price_precision=2,
        price_increment=Price.from_str("0.01"),
        multiplier=Quantity.from_int(int(contract.contract_multiplier)),
        lot_size=Quantity.from_int(1),
        underlying=contract.underlying_symbol,
        option_kind=opt_kind,
        strike_price=Price.from_str(f"{contract.strike_price:.2f}"),
        activation_ns=act_ns,
        expiration_ns=exp_ns,
        ts_event=0,
        ts_init=0,
    )
