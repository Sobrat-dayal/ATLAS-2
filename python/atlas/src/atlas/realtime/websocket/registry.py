import logging
from typing import Dict, List, Optional, Set
from uuid import UUID

from atlas.realtime.websocket.connection import RealtimeConnection
from atlas.realtime.websocket.models import QuoteSubscriptionKey

logger = logging.getLogger("atlas.realtime.websocket.registry")

class RealtimeConnectionRegistry:
    def __init__(self):
        self._connections: Dict[UUID, RealtimeConnection] = {}
        # index mapping series -> connected clients
        self._index: Dict[QuoteSubscriptionKey, Set[UUID]] = {}

    def add_connection(self, connection: RealtimeConnection):
        self._connections[connection.connection_id] = connection
        
    def remove_connection(self, connection_id: UUID):
        conn = self._connections.pop(connection_id, None)
        if not conn:
            return
            
        conn.close()
        for series in list(conn.subscriptions):
            self.remove_subscription(connection_id, series)

    def get_connection(self, connection_id: UUID) -> Optional[RealtimeConnection]:
        return self._connections.get(connection_id)
        
    def get_all_connections(self) -> List[RealtimeConnection]:
        return list(self._connections.values())

    def add_subscription(self, connection_id: UUID, series: QuoteSubscriptionKey):
        conn = self.get_connection(connection_id)
        if not conn:
            return
            
        conn.subscriptions.add(series)
        
        if series not in self._index:
            self._index[series] = set()
        self._index[series].add(connection_id)
        
    def remove_subscription(self, connection_id: UUID, series: QuoteSubscriptionKey):
        conn = self.get_connection(connection_id)
        if conn and series in conn.subscriptions:
            conn.subscriptions.remove(series)
            
        if series in self._index:
            self._index[series].discard(connection_id)
            if not self._index[series]:
                del self._index[series]

    def get_subscribers(self, series: QuoteSubscriptionKey) -> List[RealtimeConnection]:
        conn_ids = self._index.get(series, set())
        return [self._connections[cid] for cid in conn_ids if cid in self._connections]

    def clear(self):
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()
        self._index.clear()
