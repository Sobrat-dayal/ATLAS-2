import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from redis.asyncio import Redis

from atlas.market_data.quote import Quote


class QuoteCacheRecord(BaseModel):
    """
    Internal representation of a cached quote in Valkey.
    """
    schema_version: int = 1
    quote: Quote
    received_at: datetime
    cached_at: datetime
    
    # We use this to determine ordering in the atomic CAS script
    # It corresponds to quote.as_of
    source_timestamp: datetime


LUA_CAS_QUOTE = """
local key = KEYS[1]
local new_payload = ARGV[1]
local new_timestamp = tonumber(ARGV[2])

local existing = redis.call('GET', key)
if existing then
    local decoded = cjson.decode(existing)
    -- Compare timestamps. We don't overwrite if new <= existing
    local existing_timestamp = tonumber(decoded['source_timestamp_unix'])
    
    if new_timestamp <= existing_timestamp then
        return 0 -- Did not overwrite
    end
end

-- If we get here, either no existing record or new record is strictly newer
redis.call('SET', key, new_payload)
return 1 -- Overwrote successfully
"""


class LiveQuoteStateStore:
    """
    Non-authoritative ephemeral store for the latest quote state.
    Backed by Valkey/Redis. Uses a Lua script for atomic Compare-And-Swap (CAS).
    """

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        # Pre-load the script
        self._cas_script = self.redis.register_script(LUA_CAS_QUOTE)

    def _get_key(self, instrument_id: UUID) -> str:
        return f"atlas:market_data:live_quote:{instrument_id}"

    async def put_if_newer(self, quote: Quote, received_at: datetime) -> bool:
        """
        Attempts to store the given quote.
        Returns True if the quote was saved, False if it was rejected because
        a newer or equal quote already exists in the cache.
        """
        now = datetime.now(timezone.utc)
        record = QuoteCacheRecord(
            quote=quote,
            received_at=received_at,
            cached_at=now,
            source_timestamp=quote.as_of
        )

        key = self._get_key(quote.instrument_id)
        
        # Build JSON payload suitable for Lua processing. We need source_timestamp_unix for easy numeric comparison in Lua.
        payload_dict = record.model_dump(mode="json")
        payload_dict["source_timestamp_unix"] = quote.as_of.timestamp()
        
        new_payload = json.dumps(payload_dict)
        new_timestamp = quote.as_of.timestamp()
        
        result = await self._cas_script(
            keys=[key],
            args=[new_payload, new_timestamp]
        )
        return bool(result)

    async def get_latest_quote(self, instrument_id: UUID) -> Optional[QuoteCacheRecord]:
        """
        Retrieves the latest quote for a given instrument.
        """
        key = self._get_key(instrument_id)
        raw = await self.redis.get(key)
        if not raw:
            return None
            
        data = json.loads(raw)
        # Remove the extra field we added for Lua
        data.pop("source_timestamp_unix", None)
        return QuoteCacheRecord.model_validate(data)
