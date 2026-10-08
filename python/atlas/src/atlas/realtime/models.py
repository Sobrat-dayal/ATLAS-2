from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from atlas.realtime.enums import LiveEventType


class MarketQuoteUpdatedPayload(BaseModel):
    """
    The typed payload for market.quote.updated events.
    Matches the QuoteCacheRecord fields.
    """
    model_config = ConfigDict(
        # We reject inf/nan to ensure clean JSON serialization
        json_schema_extra={"allow_inf_nan": False}
    )
    quote: Dict[str, Any]  # Using dictionary equivalent of Quote to avoid circular dependencies if we don't import Quote
    received_at: datetime
    cached_at: datetime
    source_timestamp: datetime


class LiveEventEnvelope(BaseModel):
    """
    The typed, immutable envelope for Live Events published to the Redis Stream.
    """
    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={"allow_inf_nan": False}
    )

    schema_version: int = 1
    event_id: UUID = Field(default_factory=uuid4)
    event_type: LiveEventType
    emitted_at: datetime
    instrument_entity_id: UUID
    provider_key: str
    
    # We use a generic dict here but in the pipeline we will enforce type
    payload: Dict[str, Any]


class LiveEventMessage(BaseModel):
    """
    Represents an event retrieved from the live stream.
    Combines the stream cursor ID with the deserialized event envelope.
    """
    stream_id: str
    event: LiveEventEnvelope


class LiveQuoteEventCommitResult(BaseModel):
    """
    Result of an atomic routed-state/event-stream commit operation.
    """
    provider_state_updated: bool = False
    routed_state_updated: bool = False
    event_emitted: bool = False
    stream_id: Optional[str] = None
    event_id: Optional[UUID] = None
