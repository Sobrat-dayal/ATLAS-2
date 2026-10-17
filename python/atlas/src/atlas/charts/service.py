"""Domain service orchestrating historical chart market data reads for ATLAS Charts V1 (Stage 66).

Enforces interval validation, time-boundary validation, bounded limits,
cursor pagination, and metadata resolution.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from .config import (
    BASELINE_INTERVAL_CODE,
    DEFAULT_BARS_LIMIT,
    MAX_BARS_LIMIT,
    MIN_BARS_LIMIT,
)
from .models import (
    ChartCoverageDTO,
    ChartHistoryResponse,
    ChartInstrumentMetadata,
    ChartPaginationDTO,
    ChartSearchResponse,
)
from .repository import HistoricalChartRepository

logger = logging.getLogger(__name__)


class HistoricalChartService:
    """Core service for Charting V1 operations.

    Guarantees:
    - 0 writes to canonical database, 0 writes to ClickHouse, 0 upstream provider requests.
    - Validates single baseline interval ('1d') as mandated by Stage 66.
    - Rejects reversed time ranges (start >= end).
    - Enforces strict parameter clamping and typed error messages.
    """

    def __init__(self, repository: Optional[HistoricalChartRepository] = None):
        self._repository = repository or HistoricalChartRepository()

    def search_instruments(
        self, query: Optional[str] = None, asset_class: Optional[str] = None
    ) -> ChartSearchResponse:
        """Finds chartable canonical instruments matching query or asset class filter."""
        results = self._repository.search_instruments(query=query, asset_class=asset_class)
        return ChartSearchResponse(results=results, count=len(results))

    def resolve_instrument(self, identifier: str) -> Optional[ChartInstrumentMetadata]:
        """Resolves an instrument by either canonical UUID or ticker symbol."""
        trimmed = identifier.strip()
        try:
            entity_uuid = UUID(trimmed)
            return self._repository.get_instrument_by_id(entity_uuid)
        except ValueError:
            return self._repository.get_instrument_by_symbol(trimmed)

    def get_chart_history(
        self,
        instrument_identifier: str,
        interval: str = BASELINE_INTERVAL_CODE,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        before_time: Optional[datetime] = None,
        limit: int = DEFAULT_BARS_LIMIT,
    ) -> ChartHistoryResponse:
        """Retrieves verified historical OHLCV chart bars for an instrument.

        Raises:
            ValueError: If instrument is invalid, interval is unsupported,
                or time bounds are reversed.
        """
        # 1. Validate interval policy for Stage 66
        normalized_interval = interval.strip().lower()
        if normalized_interval != BASELINE_INTERVAL_CODE:
            raise ValueError(
                f"Unsupported interval '{interval}'. Stage 66 enforces the baseline '1d' interval. "
                "Expanded intraday and multi-resolution intervals belong to Stage 68."
            )

        # 2. Validate time boundaries
        if start_time and end_time and start_time >= end_time:
            raise ValueError("Invalid time range: start_time must be strictly before end_time.")

        # 3. Resolve canonical instrument
        instrument = self.resolve_instrument(instrument_identifier)
        if not instrument:
            raise ValueError(f"Unknown or non-chartable instrument '{instrument_identifier}'.")

        # 4. Clamp limit
        clamped_limit = max(MIN_BARS_LIMIT, min(limit, MAX_BARS_LIMIT))

        # 5. Fetch bars from repository
        bars, total_count, has_more, earliest_ts, latest_ts = self._repository.get_historical_bars(
            instrument_id=instrument.entity_id,
            interval=normalized_interval,
            start_time=start_time,
            end_time=end_time,
            before_time=before_time,
            limit=clamped_limit,
        )

        # 6. Build Coverage DTO
        coverage = ChartCoverageDTO(
            requested_start=start_time.isoformat() if start_time else None,
            requested_end=end_time.isoformat() if end_time else None,
            earliest_available_bar=earliest_ts,
            latest_available_bar=latest_ts,
            returned_bars_count=len(bars),
            total_bars_available=total_count,
            has_more=has_more,
            known_gaps_count=0,
            source_status="QUALIFIED" if len(bars) > 0 else "NO_DATA",
        )

        # 7. Build Pagination DTO
        next_cursor = bars[0].timestamp if (has_more and len(bars) > 0) else None
        pagination = ChartPaginationDTO(
            limit=clamped_limit,
            has_more=has_more,
            next_cursor=next_cursor,
        )

        return ChartHistoryResponse(
            schema_version="1.0.0",
            instrument=instrument,
            interval=normalized_interval,
            bars=bars,
            coverage=coverage,
            pagination=pagination,
        )
