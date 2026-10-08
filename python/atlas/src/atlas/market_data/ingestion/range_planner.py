import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.market_data.enums import BarInterval
from atlas.market_data.models import HistoricalMarketDataIngestionRun


class RangePlanner:
    """
    Determines optimal data range requests to avoid redundant historical fetches.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_latest_ingestion_end(
        self, instrument_id: uuid.UUID, interval: BarInterval
    ) -> Optional[datetime]:
        """
        Finds the latest end time of successfully ingested data for this instrument/interval.
        """
        stmt = (
            select(HistoricalMarketDataIngestionRun.end_time)
            .where(
                HistoricalMarketDataIngestionRun.instrument_id == instrument_id,
                HistoricalMarketDataIngestionRun.interval == interval.value,
                HistoricalMarketDataIngestionRun.status == "SUCCESS",
            )
            .order_by(HistoricalMarketDataIngestionRun.end_time.desc())
            .limit(1)
        )
        
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
