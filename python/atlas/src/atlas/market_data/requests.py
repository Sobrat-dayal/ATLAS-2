from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.market_data.enums import BarInterval, PriceAdjustment
from atlas.market_data.timestamps import CanonicalDatetime


class QuoteRequest(BaseModel):
    """
    Request canonical quotes for one or more instruments.
    """

    model_config = ConfigDict(frozen=True)

    instrument_ids: tuple[UUID, ...] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The canonical instrument UUIDs to request quotes for.",
    )

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "QuoteRequest":
        if len(set(self.instrument_ids)) != len(self.instrument_ids):
            raise ValueError("Duplicate instrument IDs are not allowed in QuoteRequest.")
        return self


class HistoricalBarsRequest(BaseModel):
    """
    Request canonical historical OHLCV bars.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    interval: BarInterval = Field(..., description="The canonical bar interval.")

    start: Optional[CanonicalDatetime] = Field(
        default=None, description="The UTC start time (inclusive typically)."
    )

    end: Optional[CanonicalDatetime] = Field(default=None, description="The UTC end time.")

    adjustment: PriceAdjustment = Field(
        default=PriceAdjustment.RAW, description="The requested price adjustment mode."
    )

    limit: Optional[int] = Field(
        default=None, gt=0, le=10_000, description="Maximum number of bars to return."
    )

    @model_validator(mode="after")
    def validate_bounds(self) -> "HistoricalBarsRequest":
        if self.start is not None and self.end is not None:
            if self.start >= self.end:
                raise ValueError("start time must be strictly before end time.")

        # Must have some bounds
        if self.start is None and self.end is None and self.limit is None:
            raise ValueError(
                "HistoricalBarsRequest must specify at least start/end range or a limit."
            )

        return self


class TradesRequest(BaseModel):
    """
    Request canonical historical trades.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    start: Optional[CanonicalDatetime] = Field(default=None, description="The UTC start time.")

    end: Optional[CanonicalDatetime] = Field(default=None, description="The UTC end time.")

    limit: Optional[int] = Field(
        default=None, gt=0, le=10_000, description="Maximum number of trades to return."
    )

    @model_validator(mode="after")
    def validate_bounds(self) -> "TradesRequest":
        if self.start is not None and self.end is not None:
            if self.start >= self.end:
                raise ValueError("start time must be strictly before end time.")

        # Must have some bounds
        if self.start is None and self.end is None and self.limit is None:
            raise ValueError("TradesRequest must specify at least start/end range or a limit.")

        return self


class OrderBookRequest(BaseModel):
    """
    Request an order book snapshot.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    depth: int = Field(
        default=50, ge=1, le=100, description="The number of price levels requested per side."
    )


class MarketSnapshotRequest(BaseModel):
    """
    Request market snapshots for one or more instruments.
    """

    model_config = ConfigDict(frozen=True)

    instrument_ids: tuple[UUID, ...] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The canonical instrument UUIDs to request snapshots for.",
    )

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "MarketSnapshotRequest":
        if len(set(self.instrument_ids)) != len(self.instrument_ids):
            raise ValueError("Duplicate instrument IDs are not allowed in MarketSnapshotRequest.")
        return self


class LiveQuoteSubscriptionRequest(BaseModel):
    """
    Request to subscribe to a live stream of quotes.
    """

    model_config = ConfigDict(frozen=True)

    instrument_ids: tuple[UUID, ...] = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="The canonical instrument UUIDs to subscribe to.",
    )

