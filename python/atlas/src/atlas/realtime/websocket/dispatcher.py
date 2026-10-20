import asyncio
import logging
from typing import Optional

from atlas.realtime.errors import LiveEventDecodeError
from atlas.realtime.reader import LiveEventReader
from atlas.realtime.websocket.models import (
    LiveEventMessageOut,
    QuoteSubscriptionKey,
)
from atlas.realtime.websocket.registry import RealtimeConnectionRegistry

logger = logging.getLogger("atlas.realtime.websocket.dispatcher")


class RealtimeEventDispatcher:
    def __init__(
        self,
        reader: LiveEventReader,
        registry: RealtimeConnectionRegistry,
        grace_seconds: int = 10,
    ):
        self.reader = reader
        self.registry = registry
        self.grace_seconds = grace_seconds
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.last_cursor: Optional[str] = None
        self._gateway = None  # To call resync, or we can just send the event to a channel

    def set_gateway(self, gateway):
        self._gateway = gateway

    def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self):
        while self.running:
            try:
                self.last_cursor = await self.reader.get_tail_cursor()
                break
            except Exception as e:
                logger.error("Failed to get initial tail cursor: %s", e)
                await asyncio.sleep(self.grace_seconds)
                if not self.running:
                    return

        while self.running:
            try:
                if not await self.reader.is_cursor_available(self.last_cursor):
                    if self._gateway:
                        await self._gateway.resync_all("EVENT_CURSOR_EXPIRED")
                    self.last_cursor = await self.reader.get_tail_cursor()
                    continue

                messages = await self.reader.read_after(self.last_cursor, count=100, block_ms=5000)
                if messages:
                    for msg in messages:
                        self._dispatch_event(msg)
                        self.last_cursor = msg.stream_id
            except LiveEventDecodeError as e:
                logger.warning("Skipping corrupt event %s: %s", e.stream_id, e)
                self.last_cursor = e.stream_id
                if self._gateway:
                    await self._gateway.resync_all("CORRUPT_EVENT")
            except Exception as e:
                logger.error("Event reader error: %s", e)
                await asyncio.sleep(self.grace_seconds)

    def _dispatch_event(self, msg):
        env = msg.event
        if env.event_type.value == "market.quote.updated":
            # Extract QuoteSubscriptionKey
            payload = env.payload or {}
            variant = payload.get("variant")
            series = QuoteSubscriptionKey(
                instrument_entity_id=env.instrument_entity_id, variant=variant
            )

            # Need to create the output model.
            # Using model_dump to serialize UUIDs properly
            out_msg = LiveEventMessageOut(
                stream_id=msg.stream_id, event=env.model_dump(mode="json")
            )
            for conn in self.registry.get_subscribers(series):
                conn.outbound.enqueue_quote(series, out_msg)
