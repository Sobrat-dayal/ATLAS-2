import time
from typing import Set
from uuid import UUID

from fastapi import WebSocket

from atlas.auth.principal import AuthPrincipal
from atlas.realtime.websocket.backpressure import OutboundBuffer
from atlas.realtime.websocket.models import QuoteSubscriptionKey


class RealtimeConnection:
    def __init__(self, connection_id: UUID, websocket: WebSocket, principal: AuthPrincipal, max_control_messages: int = 256):
        self.connection_id = connection_id
        self.websocket = websocket
        self.principal = principal
        self.subscriptions: Set[QuoteSubscriptionKey] = set()
        self.outbound = OutboundBuffer(max_control_messages)
        self.last_pong_at: float = time.time()
        self.closed = False

    def close(self):
        self.closed = True
        self.outbound.close()
