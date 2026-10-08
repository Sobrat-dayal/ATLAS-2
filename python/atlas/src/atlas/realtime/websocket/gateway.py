import asyncio
import logging
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import LiveQuoteStateStore
from atlas.realtime.reader import LiveEventReader
from atlas.realtime.settings import LiveEventPipelineSettings
from atlas.realtime.websocket.connection import RealtimeConnection
from atlas.realtime.websocket.dispatcher import RealtimeEventDispatcher
from atlas.realtime.websocket.errors import WebSocketProtocolError
from atlas.realtime.websocket.models import (
    ClientPong,
    ClientSubscribe,
    ClientUnsubscribe,
    ProtocolErrorResponse,
    QuoteSnapshotMessage,
    ServerConnectionReady,
    ServerPing,
    SubscriptionAck,
    SystemResyncRequired,
)
from atlas.realtime.websocket.protocol import receive_message, send_message
from atlas.realtime.websocket.registry import RealtimeConnectionRegistry
from atlas.realtime.websocket.settings import RealtimeWebSocketSettings

logger = logging.getLogger("atlas.realtime.websocket.gateway")

class RealtimeGateway:
    def __init__(self, redis: Redis, ws_settings: RealtimeWebSocketSettings, pipeline_settings: LiveEventPipelineSettings):
        self.redis = redis
        self.ws_settings = ws_settings
        self.pipeline_settings = pipeline_settings
        self.registry = RealtimeConnectionRegistry()
        
        self.reader = LiveEventReader(redis, pipeline_settings)
        self.dispatcher = RealtimeEventDispatcher(self.reader, self.registry, grace_seconds=ws_settings.event_backend_grace_seconds)
        self.dispatcher.set_gateway(self)
        
        self.quote_store = LiveQuoteStateStore(redis)
        self.quote_service = LiveQuoteService(self.quote_store)
        
        self.freshness_query_service = None

    async def start(self):
        self.dispatcher.start()

    async def stop(self):
        await self.dispatcher.stop()
        self.registry.clear()

    async def handle_websocket(self, websocket: WebSocket, principal):
        await websocket.accept()
        
        conn_id = uuid4()
        conn = RealtimeConnection(
            connection_id=conn_id, 
            websocket=websocket, 
            principal=principal,
            max_control_messages=self.ws_settings.outbound_control_queue_max_messages
        )
        self.registry.add_connection(conn)
        
        ready_msg = ServerConnectionReady(
            connection_id=conn_id,
            server_time=datetime.now(timezone.utc),
            heartbeat_interval_seconds=self.ws_settings.heartbeat_interval_seconds,
            max_series_per_message=self.ws_settings.max_series_per_message,
            max_series_per_connection=self.ws_settings.max_series_per_connection
        )
        conn.outbound.enqueue_control(ready_msg)
        
        # Start read/write tasks
        read_task = asyncio.create_task(self._read_loop(conn))
        write_task = asyncio.create_task(self._write_loop(conn))
        ping_task = asyncio.create_task(self._ping_loop(conn))
        
        done, pending = await asyncio.wait(
            [read_task, write_task, ping_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for t in pending:
            t.cancel()
            
        self.registry.remove_connection(conn_id)
        try:
            await websocket.close()
        except Exception:
            pass

    async def _read_loop(self, conn: RealtimeConnection):
        try:
            while not conn.closed:
                msg = await receive_message(conn.websocket)
                if isinstance(msg, ClientSubscribe):
                    await self._handle_subscribe(conn, msg)
                elif isinstance(msg, ClientUnsubscribe):
                    await self._handle_unsubscribe(conn, msg)
                elif isinstance(msg, ClientPong):
                    conn.last_pong_at = time.time()
        except WebSocketDisconnect:
            pass
        except WebSocketProtocolError as e:
            err = ProtocolErrorResponse(error_code="PROTOCOL_ERROR", message=str(e))
            conn.outbound.enqueue_control(err)
            await asyncio.sleep(0.5)
        finally:
            conn.close()

    async def _write_loop(self, conn: RealtimeConnection):
        try:
            while not conn.closed:
                messages = await conn.outbound.wait_for_messages()
                for msg in messages:
                    if conn.closed: break
                    await send_message(conn.websocket, msg)
        except WebSocketDisconnect:
            pass
        finally:
            conn.close()

    async def _ping_loop(self, conn: RealtimeConnection):
        try:
            while not conn.closed:
                await asyncio.sleep(self.ws_settings.heartbeat_interval_seconds)
                if conn.closed: break
                
                # Check timeout
                now = time.time()
                if now - conn.last_pong_at > self.ws_settings.heartbeat_timeout_seconds + self.ws_settings.heartbeat_interval_seconds:
                    logger.warning("Connection %s timed out", conn.connection_id)
                    break
                    
                ping_msg = ServerPing(ping_id=uuid4(), sent_at=datetime.now(timezone.utc))
                conn.outbound.enqueue_control(ping_msg)
        finally:
            conn.close()

    async def _handle_subscribe(self, conn: RealtimeConnection, msg: ClientSubscribe):
        if len(msg.series) > self.ws_settings.max_series_per_message:
            err = ProtocolErrorResponse(
                error_code="TOO_MANY_SERIES", 
                message=f"Max {self.ws_settings.max_series_per_message} per request",
                request_id=msg.request_id
            )
            conn.outbound.enqueue_control(err)
            return

        if len(conn.subscriptions) + len(msg.series) > self.ws_settings.max_series_per_connection:
            err = ProtocolErrorResponse(
                error_code="SUBSCRIPTION_LIMIT", 
                message=f"Max {self.ws_settings.max_series_per_connection} per connection",
                request_id=msg.request_id
            )
            conn.outbound.enqueue_control(err)
            return

        accepted = []
        rejected = {}
        
        # 1. Capture barrier
        barrier = self.dispatcher.last_cursor or await self.reader.get_tail_cursor()
        
        # 2. Add subscriptions
        for series in msg.series:
            self.registry.add_subscription(conn.connection_id, series)
            accepted.append(series)

        # 3. Send ACK
        ack = SubscriptionAck(request_id=msg.request_id, accepted=accepted, rejected=rejected)
        conn.outbound.enqueue_control(ack)

        # 4. Fetch Snapshots & Enqueue
        for series in accepted:
            quote_record = await self.quote_service.get_latest_quote(series.instrument_entity_id)
            snapshot = quote_record.model_dump(mode="json") if quote_record else None
            
            freshness_state = None
            if self.freshness_query_service:
                fresh_state_obj = await self.freshness_query_service.get_freshness(series, fallback_evaluation=True)
                if fresh_state_obj:
                    freshness_state = fresh_state_obj.model_dump(mode="json")
            
            snap_msg = QuoteSnapshotMessage(
                series=series,
                snapshot=snapshot,
                freshness=freshness_state,
                barrier_cursor=barrier
            )
            conn.outbound.enqueue_control(snap_msg)

    async def _handle_unsubscribe(self, conn: RealtimeConnection, msg: ClientUnsubscribe):
        for series in msg.series:
            self.registry.remove_subscription(conn.connection_id, series)

    async def resync_all(self, reason: str):
        # 1. Capture barrier
        barrier = await self.reader.get_tail_cursor()
        
        resync_msg = SystemResyncRequired(reason=reason, barrier_cursor=barrier)
        
        for conn in self.registry.get_all_connections():
            try:
                conn.outbound.enqueue_control(resync_msg)
                
                # Send snapshots for all active subscriptions
                for series in list(conn.subscriptions):
                    quote_record = await self.quote_service.get_latest_quote(series.instrument_entity_id)
                    snapshot = quote_record.model_dump(mode="json") if quote_record else None
                    
                    freshness_state = None
                    if self.freshness_query_service:
                        fresh_state_obj = await self.freshness_query_service.get_freshness(series, fallback_evaluation=True)
                        if fresh_state_obj:
                            freshness_state = fresh_state_obj.model_dump(mode="json")
                            
                    snap_msg = QuoteSnapshotMessage(
                        series=series,
                        snapshot=snapshot,
                        freshness=freshness_state,
                        barrier_cursor=barrier
                    )
                    conn.outbound.enqueue_control(snap_msg)
            except Exception:
                pass
