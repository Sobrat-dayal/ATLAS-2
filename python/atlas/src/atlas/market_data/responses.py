from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.market_data.bars import OHLCVBar
from atlas.market_data.enums import BarInterval, PriceAdjustment
from atlas.market_data.order_book import OrderBookSnapshot
from atlas.market_data.origin import MarketDataOrigin
from atlas.market_data.quote import Quote
from atlas.market_data.snapshot import MarketSnapshot
from atlas.market_data.trade import Trade


class QuoteResponse(BaseModel):
    """
    Response containing canonical quotes for one or more instruments.
    """

    model_config = ConfigDict(frozen=True)

    origin: MarketDataOrigin = Field(
        ..., description="The source and lineage metadata of this data."
    )

    quotes: tuple[Quote, ...] = Field(
        default_factory=tuple, description="The retrieved canonical quotes."
    )

    unavailable_instrument_ids: tuple[UUID, ...] = Field(
        default_factory=tuple, description="Instrument UUIDs that could not be quoted."
    )


class HistoricalBarsResponse(BaseModel):
    """
    Response containing canonical historical bars for an instrument.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    interval: BarInterval = Field(..., description="The canonical interval returned.")

    adjustment: PriceAdjustment = Field(
        ..., description="The price adjustment semantics applied to the bars."
    )

    origin: MarketDataOrigin = Field(
        ..., description="The source and lineage metadata of this data."
    )

    bars: tuple[OHLCVBar, ...] = Field(
        default_factory=tuple, description="The historical bars, strictly ordered oldest to newest."
    )

    @model_validator(mode="after")
    def validate_bars_ordering(self) -> "HistoricalBarsResponse":
        if self.bars:
            prev_start = self.bars[0].start_time
            for bar in self.bars[1:]:
                if bar.start_time < prev_start:
                    raise ValueError(
                        "Historical bars must be ordered chronologically (oldest to newest)."
                    )
                if bar.start_time == prev_start:
                    raise ValueError("Duplicate bar start times are not allowed in response.")
                prev_start = bar.start_time
        return self


class TradesResponse(BaseModel):
    """
    Response containing canonical historical trades.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    origin: MarketDataOrigin = Field(
        ..., description="The source and lineage metadata of this data."
    )

    trades: tuple[Trade, ...] = Field(
        default_factory=tuple, description="The historical trades, ordered chronologically."
    )

    @model_validator(mode="after")
    def validate_trades_ordering(self) -> "TradesResponse":
        if self.trades:
            # We enforce strictly increasing or equal timestamp.
            # When equal timestamp, if sequence is available, it should increase.
            prev_ts = self.trades[0].timestamp
            prev_seq = self.trades[0].sequence
            for trade in self.trades[1:]:
                if trade.timestamp < prev_ts:
                    raise ValueError("Trades must be ordered chronologically.")
                if (
                    trade.timestamp == prev_ts
                    and prev_seq is not None
                    and trade.sequence is not None
                ):
                    if trade.sequence < prev_seq:
                        raise ValueError(
                            "Trades with identical timestamps must be ordered by sequence if available."
                        )
                prev_ts = trade.timestamp
                prev_seq = trade.sequence
        return self


class OrderBookResponse(BaseModel):
    """
    Response containing a canonical order book snapshot.
    """

    model_config = ConfigDict(frozen=True)

    origin: MarketDataOrigin = Field(
        ..., description="The source and lineage metadata of this data."
    )

    book: OrderBookSnapshot = Field(..., description="The canonical order book snapshot.")


class MarketSnapshotResponse(BaseModel):
    """
    Response containing market snapshots for one or more instruments.
    """

    model_config = ConfigDict(frozen=True)

    origin: MarketDataOrigin = Field(
        ..., description="The source and lineage metadata of this data."
    )

    snapshots: tuple[MarketSnapshot, ...] = Field(
        default_factory=tuple, description="The canonical market snapshots."
    )

    unavailable_instrument_ids: tuple[UUID, ...] = Field(
        default_factory=tuple, description="Instrument UUIDs that could not be summarized."
    )
