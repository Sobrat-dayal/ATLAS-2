from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas.market_data.enums import MarketDataTimestampSource
from atlas.market_data.numeric import CanonicalDecimal, NonNegativeCanonicalDecimal
from atlas.market_data.timestamps import CanonicalDatetime


class OrderBookLevel(BaseModel):
    """
    Canonical representation of a single price level in an order book.
    """

    model_config = ConfigDict(frozen=True)

    price: CanonicalDecimal = Field(..., description="The price of this level.")

    size: NonNegativeCanonicalDecimal = Field(
        ..., description="The aggregated quantity available at this price."
    )

    order_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="The number of individual orders contributing to this level, if known.",
    )


class OrderBookSnapshot(BaseModel):
    """
    Canonical point-in-time snapshot of market depth (order book).
    """

    model_config = ConfigDict(frozen=True)

    instrument_id: UUID = Field(..., description="The canonical instrument UUID.")

    as_of: CanonicalDatetime = Field(..., description="The UTC timestamp of this snapshot.")

    timestamp_source: Optional[MarketDataTimestampSource] = Field(
        default=None, description="The source of the as_of timestamp."
    )

    venue_id: Optional[UUID] = Field(
        default=None, description="The canonical Entity UUID of the exchange/venue, if applicable."
    )

    bids: tuple[OrderBookLevel, ...] = Field(
        default_factory=tuple, description="Bid levels sorted descending by price."
    )

    asks: tuple[OrderBookLevel, ...] = Field(
        default_factory=tuple, description="Ask levels sorted ascending by price."
    )

    @model_validator(mode="after")
    def validate_order_book(self) -> "OrderBookSnapshot":
        # Validate Bids sorting (descending) and uniqueness
        if self.bids:
            prev_price = self.bids[0].price
            for bid in self.bids[1:]:
                if bid.price > prev_price:
                    raise ValueError("Bids must be sorted strictly descending by price.")
                if bid.price == prev_price:
                    raise ValueError("Duplicate price levels found in bids.")
                prev_price = bid.price

        # Validate Asks sorting (ascending) and uniqueness
        if self.asks:
            prev_price = self.asks[0].price
            for ask in self.asks[1:]:
                if ask.price < prev_price:
                    raise ValueError("Asks must be sorted strictly ascending by price.")
                if ask.price == prev_price:
                    raise ValueError("Duplicate price levels found in asks.")
                prev_price = ask.price

        # Crossed books (highest bid >= lowest ask) are allowed transiently
        return self
