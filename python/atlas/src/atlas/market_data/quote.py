from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.market_data.enums import MarketDataTimestampSource, MarketSession
from atlas.market_data.numeric import CanonicalDecimal, NonNegativeCanonicalDecimal
from atlas.market_data.timestamps import CanonicalDatetime


class Quote(BaseModel):
    """
    Canonical representation of a market quote (bid/ask).
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(
        ..., description="The canonical instrument UUID this quote applies to."
    )

    as_of: CanonicalDatetime = Field(
        ..., description="The UTC timestamp when this quote was observed/published."
    )

    timestamp_source: Optional[MarketDataTimestampSource] = Field(
        default=None, description="The source of the as_of timestamp."
    )

    venue_id: Optional[UUID] = Field(
        default=None, description="The canonical Entity UUID of the exchange/venue, if applicable."
    )

    session: Optional[MarketSession] = Field(
        default=None, description="The trading session this quote belongs to."
    )

    bid_price: Optional[CanonicalDecimal] = Field(
        default=None, description="The highest price a buyer will pay."
    )

    bid_size: Optional[NonNegativeCanonicalDecimal] = Field(
        default=None, description="The quantity available at the bid price."
    )

    ask_price: Optional[CanonicalDecimal] = Field(
        default=None, description="The lowest price a seller will accept."
    )

    ask_size: Optional[NonNegativeCanonicalDecimal] = Field(
        default=None, description="The quantity available at the ask price."
    )

    @model_validator(mode="after")
    def validate_quote(self) -> "Quote":
        # Reject entirely empty quote
        if self.bid_price is None and self.ask_price is None:
            raise ValueError("Quote must have at least one of bid_price or ask_price.")

        # Size without price is invalid
        if self.bid_size is not None and self.bid_price is None:
            raise ValueError("Quote with bid_size must also have bid_price.")

        if self.ask_size is not None and self.ask_price is None:
            raise ValueError("Quote with ask_size must also have ask_price.")

        # Note: Crossed quotes (bid >= ask) are explicitly allowed
        return self
