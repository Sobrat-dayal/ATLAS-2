import json
from typing import Optional

from redis.asyncio import Redis

from atlas.market_data.freshness.models import MarketDataFreshnessState
from atlas.realtime.websocket.models import QuoteSubscriptionKey


LUA_CAS_FRESHNESS = """
local key = KEYS[1]
local new_payload = ARGV[1]
local new_timestamp = tonumber(ARGV[2])
local ttl = tonumber(ARGV[3])

local existing = redis.call('GET', key)
if existing then
    local decoded = cjson.decode(existing)
    local existing_timestamp = tonumber(decoded['evaluated_at_unix'])
    
    if new_timestamp < existing_timestamp then
        return 0 -- Did not overwrite (older evaluation)
    end
end

redis.call('SETEX', key, ttl, new_payload)
return 1
"""


class MarketDataFreshnessStateStore:
    def __init__(self, redis_client: Redis, state_ttl_seconds: int = 3600):
        self.redis = redis_client
        self.state_ttl_seconds = state_ttl_seconds
        self._cas_script = self.redis.register_script(LUA_CAS_FRESHNESS)

    def _get_key(self, series_key: QuoteSubscriptionKey) -> str:
        return f"atlas:market_data:freshness:{series_key.to_string()}"

    async def put_if_newer(self, state: MarketDataFreshnessState) -> bool:
        """
        Attempts to store the given freshness state.
        Returns True if the state was saved, False if a newer state already exists.
        """
        key = self._get_key(state.series_key)
        
        payload_dict = state.model_dump(mode="json")
        payload_dict["evaluated_at_unix"] = state.evaluated_at.timestamp()
        
        new_payload = json.dumps(payload_dict)
        new_timestamp = state.evaluated_at.timestamp()
        
        result = await self._cas_script(
            keys=[key],
            args=[new_payload, new_timestamp, self.state_ttl_seconds]
        )
        return bool(result)

    async def get_state(self, series_key: QuoteSubscriptionKey) -> Optional[MarketDataFreshnessState]:
        key = self._get_key(series_key)
        raw = await self.redis.get(key)
        if not raw:
            return None
            
        data = json.loads(raw)
        data.pop("evaluated_at_unix", None)
        return MarketDataFreshnessState.model_validate(data)

    async def delete_state(self, series_key: QuoteSubscriptionKey) -> None:
        key = self._get_key(series_key)
        await self.redis.delete(key)
