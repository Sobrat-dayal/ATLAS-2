from typing import List, Optional
from uuid import UUID

from atlas.market_data.live.store import LiveQuoteStateStore, QuoteCacheRecord


class LiveQuoteService:
    """
    Service for querying the latest live quotes.
    Reads exclusively from the non-authoritative ephemeral store (Valkey/Redis).
    """

    def __init__(self, store: LiveQuoteStateStore):
        self._store = store

    async def get_latest_quote(self, instrument_id: UUID) -> Optional[QuoteCacheRecord]:
        """
        Fetch the latest quote for a single instrument.
        """
        return await self._store.get_latest_quote(instrument_id)

    async def get_latest_quotes(self, instrument_ids: List[UUID]) -> List[Optional[QuoteCacheRecord]]:
        """
        Fetch the latest quotes for a batch of instruments.
        """
        # In a real implementation we could use redis.mget or pipeline here
        # For simplicity, we just use a loop since get_latest_quote is async
        results = []
        for instrument_id in instrument_ids:
            results.append(await self.get_latest_quote(instrument_id))
        return results
