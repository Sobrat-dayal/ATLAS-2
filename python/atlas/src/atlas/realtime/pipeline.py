import json
from datetime import datetime, timezone
from typing import Optional

from redis.asyncio import Redis

from atlas.market_data.quote import Quote
from atlas.realtime.enums import LiveEventType
from atlas.realtime.models import (
    LiveEventEnvelope,
    LiveQuoteEventCommitResult,
    MarketQuoteUpdatedPayload,
)
from atlas.realtime.settings import LiveEventPipelineSettings
from atlas.realtime.errors import LiveEventTooLarge


# Extended Lua script to handle both CAS set and XADD atomically
LUA_CAS_QUOTE_AND_EVENT = """
local key = KEYS[1]
local stream_key = KEYS[2]

local new_payload = ARGV[1]
local new_timestamp = tonumber(ARGV[2])
local event_payload = ARGV[3]
local stream_maxlen = tonumber(ARGV[4])

local existing = redis.call('GET', key)
if existing then
    local decoded = cjson.decode(existing)
    -- Compare timestamps. We don't overwrite if new <= existing
    local existing_timestamp = tonumber(decoded['source_timestamp_unix'])
    
    if new_timestamp <= existing_timestamp then
        return {0, ""} -- Did not overwrite, no event emitted
    end
end

-- If we get here, either no existing record or new record is strictly newer
redis.call('SET', key, new_payload)

local stream_id = ""
if stream_key and event_payload then
    -- XADD with approximate MAXLEN
    stream_id = redis.call('XADD', stream_key, 'MAXLEN', '~', stream_maxlen, '*', 'data', event_payload)
end

return {1, stream_id}
"""


class LiveEventPipeline:
    """
    Live Event Pipeline that handles atomic commits of both routed state and event streams.
    """

    def __init__(
        self,
        redis_client: Redis,
        settings: LiveEventPipelineSettings,
    ):
        self.redis = redis_client
        self.settings = settings
        self._cas_script = self.redis.register_script(LUA_CAS_QUOTE_AND_EVENT)

    def _get_routed_key(self, instrument_id) -> str:
        return f"atlas:market_data:live_quote:{instrument_id}"

    def _build_event(
        self,
        quote: Quote,
        received_at: datetime,
        now: datetime,
    ) -> LiveEventEnvelope:
        payload = MarketQuoteUpdatedPayload(
            quote=quote.model_dump(mode="json"),
            received_at=received_at,
            cached_at=now,
            source_timestamp=quote.as_of,
        )

        event = LiveEventEnvelope(
            event_type=LiveEventType.MARKET_QUOTE_UPDATED,
            emitted_at=now,
            instrument_entity_id=quote.instrument_id,
            provider_key=quote.provider,
            payload=payload.model_dump(mode="json")
        )
        return event

    async def commit_quote_update(self, quote: Quote, received_at: datetime) -> LiveQuoteEventCommitResult:
        """
        Attempts to store the given quote and atomically append an event.
        Returns a LiveQuoteEventCommitResult indicating what happened.
        """
        now = datetime.now(timezone.utc)
        
        event = self._build_event(quote, received_at, now)
        event_json = event.model_dump_json()

        if len(event_json.encode('utf-8')) > self.settings.event_max_bytes:
            raise LiveEventTooLarge(f"Event size exceeds maximum of {self.settings.event_max_bytes} bytes")

        # Create QuoteCacheRecord payload for state store
        from atlas.market_data.live.store import QuoteCacheRecord
        record = QuoteCacheRecord(
            quote=quote,
            received_at=received_at,
            cached_at=now,
            source_timestamp=quote.as_of
        )

        state_key = self._get_routed_key(quote.instrument_id)
        
        payload_dict = record.model_dump(mode="json")
        payload_dict["source_timestamp_unix"] = quote.as_of.timestamp()
        
        new_payload = json.dumps(payload_dict)
        new_timestamp = quote.as_of.timestamp()
        
        if self.settings.enabled:
            stream_key = self.settings.stream_key_prefix
            stream_maxlen = self.settings.stream_max_length
            event_payload = event_json
            keys = [state_key, stream_key]
        else:
            # If disabled, we still run the Lua script but don't append to the stream.
            keys = [state_key, ""]
            stream_maxlen = 0
            event_payload = ""

        try:
            result = await self._cas_script(
                keys=keys,
                args=[new_payload, new_timestamp, event_payload, stream_maxlen]
            )
            
            updated, stream_id = result
            
            if updated == 1:
                return LiveQuoteEventCommitResult(
                    provider_state_updated=True,
                    routed_state_updated=True,
                    event_emitted=self.settings.enabled,
                    stream_id=stream_id if stream_id else None,
                    event_id=event.event_id if self.settings.enabled else None
                )
            else:
                return LiveQuoteEventCommitResult(
                    provider_state_updated=True,
                    routed_state_updated=False,
                    event_emitted=False,
                )
        except Exception as e:
            # Re-raise standard Redis connection errors as infrastructure failures if appropriate,
            # or just let them bubble up as they would in Stage 41.
            raise
