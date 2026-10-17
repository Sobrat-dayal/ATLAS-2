"""FastAPI router exposing historical chart endpoints for ATLAS Charts V1 (Stage 66).

Provides:
- GET /charts/history: Historical OHLCV bars with coverage and cursor pagination
- GET /charts/instruments: Search and discovery of canonical chartable instruments
- GET /charts/instruments/{identifier}: Specific instrument metadata lookup
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from .config import BASELINE_INTERVAL_CODE, DEFAULT_BARS_LIMIT, MAX_BARS_LIMIT, MIN_BARS_LIMIT
from .live_service import LiveChartService
from .models import (
    ChartHistoryResponse,
    ChartInstrumentMetadata,
    ChartLiveStateResponse,
    ChartSearchResponse,
)
from .service import HistoricalChartService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/charts", tags=["charts"])
_chart_service = HistoricalChartService()
_live_chart_service = LiveChartService()


@router.get(
    "/instruments",
    response_model=ChartSearchResponse,
    summary="Search canonical chartable instruments",
    description=(
        "Discovers chartable instruments across Equities, ETFs, FX, Crypto, Bonds, and Futures."
    ),
)
async def search_chart_instruments(
    q: Optional[str] = Query(None, description="Search query string matching symbol or name"),
    asset_class: Optional[str] = Query(None, description="Optional asset class filter"),
) -> ChartSearchResponse:
    return _chart_service.search_instruments(query=q, asset_class=asset_class)


@router.get(
    "/instruments/{identifier}",
    response_model=ChartInstrumentMetadata,
    summary="Get canonical chart instrument metadata",
    description="Resolves an instrument by canonical UUID or ticker symbol.",
)
async def get_chart_instrument(
    identifier: str,
) -> ChartInstrumentMetadata:
    meta = _chart_service.resolve_instrument(identifier)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument '{identifier}' not found in canonical chart catalog.",
        )
    return meta


@router.get(
    "/history",
    response_model=ChartHistoryResponse,
    summary="Retrieve canonical historical OHLCV chart bars",
    description=(
        "Returns verified chronological ascending OHLCV bars for an instrument "
        "at the baseline '1d' interval, with coverage metrics and cursor pagination."
    ),
)
async def get_chart_history(
    instrument_id: Optional[str] = Query(None, description="Canonical instrument UUID or symbol"),
    symbol: Optional[str] = Query(None, description="Alternative symbol parameter for convenience"),
    interval: str = Query(
        BASELINE_INTERVAL_CODE,
        description="Bar interval code. Stage 66 enforces baseline '1d'.",
    ),
    start: Optional[datetime] = Query(None, description="UTC start time boundary (inclusive)"),
    end: Optional[datetime] = Query(None, description="UTC end time boundary (exclusive)"),
    before: Optional[datetime] = Query(
        None, description="Cursor timestamp for fetching older bars before this time"
    ),
    limit: int = Query(
        DEFAULT_BARS_LIMIT,
        ge=MIN_BARS_LIMIT,
        le=MAX_BARS_LIMIT,
        description="Maximum number of bars to return (10-2000)",
    ),
) -> ChartHistoryResponse:
    target_ident = instrument_id or symbol
    if not target_ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'instrument_id' or 'symbol' query parameter must be provided.",
        )

    try:
        return _chart_service.get_chart_history(
            instrument_identifier=target_ident,
            interval=interval,
            start_time=start,
            end_time=end,
            before_time=before,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_chart_history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chart history.",
        )


@router.get(
    "/live-state",
    response_model=ChartLiveStateResponse,
    summary="Get initial authorized live quote state for chart streaming (Stage 67)",
    description=(
        "Returns the latest accepted canonical market quote state, source timestamp, "
        "delay status, freshness classification, and live capability without "
        "mutating historical data."
    ),
)
async def get_chart_live_state(
    instrument_id: Optional[str] = Query(None, description="Canonical instrument UUID"),
    symbol: Optional[str] = Query(None, description="Symbol (e.g. SPY, BTCUSDT, CLZ26)"),
) -> ChartLiveStateResponse:
    target_ident = instrument_id or symbol
    if not target_ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'instrument_id' or 'symbol' query parameter must be provided.",
        )

    live_state = _live_chart_service.get_live_state(target_ident)
    if not live_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument '{target_ident}' not found in canonical chart catalog.",
        )
    return live_state
