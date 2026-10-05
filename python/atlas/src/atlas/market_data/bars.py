from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.market_data.enums import BarInterval, MarketSession
from atlas.market_data.numeric import CanonicalDecimal, NonNegativeCanonicalDecimal
from atlas.market_data.timestamps import CanonicalDatetime


class OHLCVBar(BaseModel):
    """
    Canonical representation of a market data bar/candle over a time interval.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    interval: BarInterval = Field(
        ..., description="The canonical time interval representing the bar."
    )

    start_time: CanonicalDatetime = Field(
        ..., description="The UTC start time of the bar (inclusive typically)."
    )

    end_time: CanonicalDatetime = Field(..., description="The UTC end time of the bar.")

    venue_id: Optional[UUID] = Field(
        default=None, description="The canonical Entity UUID of the exchange/venue, if applicable."
    )

    session: Optional[MarketSession] = Field(
        default=None, description="The trading session this bar represents."
    )

    open: CanonicalDecimal = Field(..., description="The opening price of the interval.")

    high: CanonicalDecimal = Field(..., description="The highest price observed in the interval.")

    low: CanonicalDecimal = Field(..., description="The lowest price observed in the interval.")

    close: CanonicalDecimal = Field(..., description="The closing price of the interval.")

    volume: Optional[NonNegativeCanonicalDecimal] = Field(
        default=None,
        description="The total traded volume during the interval. Missing volume is None, not 0.",
    )

    vwap: Optional[CanonicalDecimal] = Field(
        default=None, description="Volume-Weighted Average Price, if provided by the source."
    )

    trade_count: Optional[int] = Field(
        default=None, ge=0, description="The number of trades that occurred during the interval."
    )

    is_final: bool = Field(
        default=True,
        description="True if the source guarantees this interval is closed and will not change.",
    )

    @model_validator(mode="after")
    def validate_bar(self) -> "OHLCVBar":
        # Time validation
        if self.start_time >= self.end_time:
            raise ValueError("Bar start_time must be strictly before end_time.")

        # Price envelope validation
        if self.high < self.open or self.high < self.low or self.high < self.close:
            raise ValueError("Bar high must be >= open, low, and close.")

        if self.low > self.open or self.low > self.high or self.low > self.close:
            raise ValueError("Bar low must be <= open, high, and close.")

        return self
