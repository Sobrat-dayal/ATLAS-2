import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.infrastructure.clickhouse.market_data.mapper import HistoricalMarketBarStorageMapper
from atlas.infrastructure.clickhouse.market_data.repository import HistoricalMarketDataRepository
from atlas.market_data.enums import BarInterval
from atlas.market_data.models import HistoricalMarketDataIngestionRun
from atlas.market_data.protocols import HistoricalBarsMarketDataProvider
from atlas.market_data.requests import HistoricalBarsRequest
from atlas.market_data.responses import HistoricalBarsResponse

logger = logging.getLogger(__name__)


class HistoricalMarketDataIngestionService:
    """
    Orchestrates the retrieval and storage of canonical historical market data.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        ch_repository: HistoricalMarketDataRepository,
        provider: HistoricalBarsMarketDataProvider,
    ):
        self._db_session = db_session
        self._ch_repository = ch_repository
        self._provider = provider
        self._mapper = HistoricalMarketBarStorageMapper()

    async def ingest_bars(
        self,
        request: HistoricalBarsRequest,
    ) -> uuid.UUID:
        """
        Executes an ingestion run for historical bars.
        
        Returns the ingestion run ID.
        """
        run_id = uuid.uuid4()
        run_record = HistoricalMarketDataIngestionRun(
            id=run_id,
            instrument_id=request.instrument_id,
            interval=request.interval.value,
            start_time=request.start or datetime.min.replace(tzinfo=timezone.utc),
            end_time=request.end or datetime.now(timezone.utc),
            provider_key="unknown",  # will be updated later
            bars_ingested=0,
            status="RUNNING",
        )
        self._db_session.add(run_record)
        await self._db_session.commit()

        try:
            # 1. Fetch from provider
            response: HistoricalBarsResponse = await self._provider.get_historical_bars(request)
            
            run_record.provider_key = response.origin.provider_key
            run_record.bars_ingested = len(response.bars)

            # 2. Map to ClickHouse format
            if response.bars:
                rows = self._mapper.map_to_clickhouse(response, run_id)
                
                # 3. Insert to ClickHouse
                # We perform this synchronously because clickhouse-connect uses sync HTTP requests
                # in a real high-throughput scenario, we might offload to a thread pool.
                self._ch_repository.insert_bars(rows)
            
            # 4. Mark success
            run_record.status = "SUCCESS"
            await self._db_session.commit()
            
            logger.info(f"Ingestion run {run_id} completed successfully. Ingested {len(response.bars)} bars.")
            return run_id
            
        except Exception as e:
            run_record.status = "FAILED"
            run_record.error_message = str(e)
            await self._db_session.commit()
            logger.error(f"Ingestion run {run_id} failed: {e}")
            raise
