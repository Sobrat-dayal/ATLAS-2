import hashlib
import uuid
from typing import Any

from atlas.market_data.responses import HistoricalBarsResponse


class HistoricalMarketBarStorageMapper:
    """
    Maps canonical Stage 33 Market Data models to ClickHouse insertion format.
    """

    @staticmethod
    def map_to_clickhouse(
        response: HistoricalBarsResponse, run_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        rows = []
        origin = response.origin

        for bar in response.bars:
            # Create deterministic content hash
            # We hash the combination of identity + timestamp + price + volume
            # to detect true content differences if needed.
            hash_input = (
                f"{response.instrument_id}:{response.interval.value}:{response.adjustment.value}:"
                f"{bar.start_time.isoformat()}:{origin.provider_key}:{bar.close}"
            ).encode("utf-8")
            content_hash = hashlib.sha256(hash_input).hexdigest()

            row = {
                "instrument_entity_id": response.instrument_id,
                "interval_code": response.interval.value,
                "adjustment_code": response.adjustment.value,
                "session_code": bar.session.value if bar.session else None,
                "venue_id": bar.venue_id,
                "bar_start": bar.start_time,
                "bar_end": bar.end_time,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
                "vwap": bar.vwap,
                "trade_count": bar.trade_count,
                "is_final": 1 if bar.is_final else 0,
                "provider_key": origin.provider_key,
                "upstream_source": origin.upstream_source,
                "source_retrieved_at": origin.retrieved_at,
                "timeliness_code": origin.timeliness.value,
                "delay_seconds": origin.delay_seconds,
                "source_timestamp": origin.source_timestamp,
                "ingested_at": origin.retrieved_at,  # Or time of ingestion
                "ingestion_run_id": run_id,
                "content_hash": content_hash,
            }
            rows.append(row)

        return rows
