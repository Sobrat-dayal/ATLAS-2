from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from atlas.market_data.enums import MarketDataTimestampSource, MarketSession, TradeSide
from atlas.market_data.numeric import CanonicalDecimal, PositiveCanonicalDecimal
from atlas.market_data.timestamps import CanonicalDatetime


class Trade(BaseModel):
    """
    Canonical representation of an executed trade.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(
        ..., description="The canonical instrument UUID this trade applies to."
    )

    timestamp: CanonicalDatetime = Field(
        ..., description="The UTC timestamp when this trade occurred or was published."
    )

    timestamp_source: Optional[MarketDataTimestampSource] = Field(
        default=None, description="The source of the timestamp."
    )

    venue_id: Optional[UUID] = Field(
        default=None, description="The canonical Entity UUID of the exchange/venue, if applicable."
    )

    session: Optional[MarketSession] = Field(
        default=None, description="The trading session this trade occurred in."
    )

    price: CanonicalDecimal = Field(
        ..., description="The executed price. Note: Can be negative in specific markets."
    )

    size: PositiveCanonicalDecimal = Field(
        ..., description="The executed quantity. Must be strictly positive."
    )

    trade_id: Optional[str] = Field(
        default=None, max_length=128, description="Provider or source-local trade identifier."
    )

    sequence: Optional[int] = Field(
        default=None, ge=0, description="Optional monotonically increasing sequence number."
    )

    side: Optional[TradeSide] = Field(default=None, description="The aggressor side, if known.")
