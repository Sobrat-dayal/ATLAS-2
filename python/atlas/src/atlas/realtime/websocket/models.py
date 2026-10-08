from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuoteSubscriptionKey(BaseModel):
    """
    Identifies a canonical Quote series.
    """
    model_config = ConfigDict(frozen=True)
    instrument_entity_id: UUID
    variant: Optional[str] = None
    
    def __hash__(self):
        return hash((self.instrument_entity_id, self.variant))
    
    def to_string(self) -> str:
        if self.variant:
            return f"{self.instrument_entity_id}::{self.variant}"
        return str(self.instrument_entity_id)

class BaseClientMessage(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    protocol_version: int = 1
    type: str

class ClientSubscribe(BaseClientMessage):
    type: Literal["subscribe"] = "subscribe"
    request_id: UUID
    series: List[QuoteSubscriptionKey]

class ClientUnsubscribe(BaseClientMessage):
    type: Literal["unsubscribe"] = "unsubscribe"
    request_id: UUID
    series: List[QuoteSubscriptionKey]

class ClientPong(BaseClientMessage):
    type: Literal["pong"] = "pong"
    ping_id: UUID

ClientMessage = Annotated[
    Union[ClientSubscribe, ClientUnsubscribe, ClientPong],
    Field(discriminator="type"),
]

class BaseServerMessage(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    protocol_version: int = 1
    type: str

class ServerConnectionReady(BaseServerMessage):
    type: Literal["connection.ready"] = "connection.ready"
    connection_id: UUID
    server_time: datetime
    heartbeat_interval_seconds: int
    max_series_per_message: int
    max_series_per_connection: int

class SubscriptionAck(BaseServerMessage):
    type: Literal["subscription.ack"] = "subscription.ack"
    request_id: UUID
    accepted: List[QuoteSubscriptionKey]
    rejected: Dict[str, str]  # stringified QuoteSubscriptionKey -> reason

class QuoteSnapshotMessage(BaseServerMessage):
    type: Literal["market.quote.snapshot"] = "market.quote.snapshot"
    series: QuoteSubscriptionKey
    snapshot: Optional[Dict[str, Any]]
    barrier_cursor: str

class LiveEventMessageOut(BaseServerMessage):
    type: Literal["live.event"] = "live.event"
    stream_id: str
    event: Dict[str, Any]

class ServerPing(BaseServerMessage):
    type: Literal["system.ping"] = "system.ping"
    ping_id: UUID
    sent_at: datetime

class SystemResyncRequired(BaseServerMessage):
    type: Literal["system.resync_required"] = "system.resync_required"
    reason: str
    barrier_cursor: Optional[str] = None

class ProtocolErrorResponse(BaseServerMessage):
    type: Literal["error"] = "error"
    error_code: str
    message: str
    request_id: Optional[UUID] = None

ServerMessage = Annotated[
    Union[
        ServerConnectionReady,
        SubscriptionAck,
        QuoteSnapshotMessage,
        LiveEventMessageOut,
        ServerPing,
        SystemResyncRequired,
        ProtocolErrorResponse,
    ],
    Field(discriminator="type"),
]
