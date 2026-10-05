from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.market_data.enums import MarketSession
from atlas.market_data.numeric import CanonicalDecimal, NonNegativeCanonicalDecimal
from atlas.market_data.quote import Quote
from atlas.market_data.timestamps import CanonicalDatetime
from atlas.market_data.trade import Trade


class MarketSnapshot(BaseModel):
    """
    Compact point-in-time summary of a market.
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    as_of: CanonicalDatetime = Field(
        ..., description="The UTC timestamp when this snapshot was created/retrieved."
    )

    venue_id: Optional[UUID] = Field(
        default=None, description="The canonical Entity UUID of the exchange/venue, if applicable."
    )

    session: Optional[MarketSession] = Field(
        default=None, description="The trading session this snapshot summarizes."
    )

    quote: Optional[Quote] = Field(default=None, description="The current/latest quote.")

    last_trade: Optional[Trade] = Field(default=None, description="The last executed trade.")

    session_open: Optional[CanonicalDecimal] = Field(
        default=None, description="The opening price of the current session."
    )

    session_high: Optional[CanonicalDecimal] = Field(
        default=None, description="The highest price of the current session."
    )

    session_low: Optional[CanonicalDecimal] = Field(
        default=None, description="The lowest price of the current session."
    )

    previous_close: Optional[CanonicalDecimal] = Field(
        default=None, description="The closing price of the previous session."
    )

    session_volume: Optional[NonNegativeCanonicalDecimal] = Field(
        default=None, description="The total traded volume in the current session."
    )

    vwap: Optional[CanonicalDecimal] = Field(
        default=None, description="The Volume-Weighted Average Price of the current session."
    )

    @model_validator(mode="after")
    def validate_snapshot(self) -> "MarketSnapshot":
        # Reject an entirely empty snapshot
        if all(
            x is None
            for x in [
                self.quote,
                self.last_trade,
                self.session_open,
                self.session_high,
                self.session_low,
                self.previous_close,
                self.session_volume,
                self.vwap,
            ]
        ):
            raise ValueError("MarketSnapshot must contain at least one piece of market data.")

        # Validate nested ID consistency
        if self.quote is not None and self.quote.instrument_id != self.instrument_id:
            raise ValueError("Nested Quote instrument_id must match Snapshot instrument_id.")

        if self.last_trade is not None and self.last_trade.instrument_id != self.instrument_id:
            raise ValueError("Nested Trade instrument_id must match Snapshot instrument_id.")

        return self
