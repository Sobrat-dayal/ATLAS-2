"""Reference close resolution and Decimal financial change calculation (Stage 52)."""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID

from .models import MarketSummaryChangeDirection

logger = logging.getLogger(__name__)


def calculate_market_changes(
    last_price: Optional[Decimal],
    reference_close: Optional[Decimal],
) -> Tuple[Optional[Decimal], Optional[Decimal], MarketSummaryChangeDirection]:
    """
    Computes absolute and percentage price change relative to a valid reference close.

    Guarantees:
    - Strictly Decimal precision (no floating-point inaccuracy).
    - Zero denominator protection: if reference_close == 0, percentage_change is None.
    - If either last_price or reference_close is None, returns (None, None, UNKNOWN).
    - Typed direction: UP (> 0), DOWN (< 0), FLAT (== 0), UNKNOWN (missing).
    """
    if last_price is None or reference_close is None:
        return None, None, MarketSummaryChangeDirection.UNKNOWN

    abs_change = last_price - reference_close

    if reference_close == Decimal("0"):
        # Zero denominator safety - cannot divide by zero
        pct_change = None
    else:
        # ((last_price - reference_close) / reference_close) * 100
        pct_change = (abs_change / reference_close) * Decimal("100")

    if abs_change > Decimal("0"):
        direction = MarketSummaryChangeDirection.UP
    elif abs_change < Decimal("0"):
        direction = MarketSummaryChangeDirection.DOWN
    else:
        direction = MarketSummaryChangeDirection.FLAT

    return abs_change, pct_change, direction


class ReferenceCloseResolver:
    """
    Resolves verified prior completed-session close prices without guessing.

    Precedence:
    1. Direct snapshot previous_close if already verified by market feed.
    2. ClickHouse historical daily bar from completed session (interval='1d').
    3. Return None if neither source is reliably available.
    """

    def __init__(self, clickhouse_client_factory: Optional[object] = None):
        self._ch_factory = clickhouse_client_factory

    async def resolve_reference_close(
        self,
        instrument_id: UUID,
        quote_snapshot_prev_close: Optional[Decimal] = None,
        quote_snapshot_session_date: Optional[date] = None,
    ) -> Tuple[Optional[Decimal], Optional[date], Optional[str]]:
        """
        Attempts to find a canonical reference close.
        Returns: (reference_close, session_date, source_identifier)
        """
        # 1. Fast path: feed snapshot provided valid previous_close
        if quote_snapshot_prev_close is not None and quote_snapshot_prev_close > Decimal("0"):
            return (
                quote_snapshot_prev_close,
                quote_snapshot_session_date,
                "feed_snapshot_prior_close",
            )

        # 2. ClickHouse historical query for completed daily bar
        if self._ch_factory and hasattr(self._ch_factory, "get_client"):
            try:
                client = self._ch_factory.get_client()
                if client is not None:
                    # Bounded query: 1 bar, interval '1d', strictly for canonical instrument
                    query = """
                    SELECT close, toDate(timestamp) as session_date
                    FROM historical_market_bars_versions
                    WHERE instrument_id = %(instrument_id)s
                      AND interval = '1d'
                      AND is_deleted = 0
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """
                    result = client.query(query, parameters={"instrument_id": str(instrument_id)})
                    if result.result_rows:
                        raw_close, raw_date = result.result_rows[0]
                        ref_close = Decimal(str(raw_close))
                        if ref_close > Decimal("0"):
                            sess_date = raw_date if isinstance(raw_date, date) else None
                            return ref_close, sess_date, "clickhouse_daily_bar"
            except Exception as e:
                logger.warning(
                    "ClickHouse reference close lookup failed for %s (continuing safely): %s",
                    instrument_id,
                    e,
                )

        # 3. No verified reference available -> return None safely without guessing
        return None, None, None
