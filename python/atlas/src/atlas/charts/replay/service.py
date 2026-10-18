"""Domain Service orchestrating Historical Chart Replay V1 for ATLAS Charts (Stage 75).

Enforces:
- Authenticated user session ownership
- Bounded historical bar qualification from canonical data services
- Strict future-data isolation (bars N+1.. are never exposed in step responses)
- Deterministic forward/backward cursor stepping and seeking
- Replay-aware TA-Lib indicator recalculation strictly bounded to cursor position
- Disclosure of current revised dataset usage vs point-in-time claims
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from ..indicators import (
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    TechnicalIndicatorService,
)
from ..models import ChartBarDTO
from ..service import HistoricalChartService
from .models import (
    ReplayCapabilityResponse,
    ReplaySeekRequest,
    ReplaySeekResponse,
    ReplaySessionDTO,
    ReplaySessionStatus,
    ReplaySourceSnapshot,
    ReplayStartRequest,
    ReplayStartResponse,
    ReplayStepDirection,
    ReplayStepRequest,
    ReplayStepResponse,
)
from .session_manager import (
    ReplaySessionInternal,
    ReplaySessionManager,
    default_replay_session_manager,
)

logger = logging.getLogger(__name__)

METHODOLOGICAL_NOTICE = (
    "Historical playback uses the currently available adjusted/revised dataset and does "
    "not guarantee true historical point-in-time information availability."
)


class HistoricalChartReplayService:
    """Core service for Stage 75 Historical Chart Replay operations."""

    def __init__(
        self,
        chart_service: Optional[HistoricalChartService] = None,
        indicator_service: Optional[TechnicalIndicatorService] = None,
        session_manager: Optional[ReplaySessionManager] = None,
    ) -> None:
        self.chart_service = chart_service or HistoricalChartService()
        self.indicator_service = indicator_service or TechnicalIndicatorService(
            chart_service=self.chart_service
        )
        self.session_manager = session_manager or default_replay_session_manager

    def get_capabilities(
        self, instrument_identifier: str, interval: str = "1d"
    ) -> ReplayCapabilityResponse:
        """Discovers replay capabilities, available interval options, and historical coverage."""
        metadata = self.chart_service.resolve_instrument(instrument_identifier)
        if not metadata:
            raise ValueError(f"Unknown or non-chartable instrument '{instrument_identifier}'.")

        # Discover interval options
        interval_response = self.chart_service.get_available_intervals(metadata.entity_id)
        supported_intervals = [
            opt.interval_id
            for opt in interval_response.intervals
            if opt.availability != "UNAVAILABLE"
        ]

        # Fetch coverage metrics via historical chart service
        history = self.chart_service.get_chart_history(
            instrument_identifier=metadata.entity_id,
            interval=interval,
            limit=2000,
        )

        bars = history.bars
        total_bars = len(bars)
        is_supported = total_bars >= 2

        earliest = (
            datetime.fromtimestamp(bars[0].time_unix, tz=timezone.utc) if bars else None
        )
        latest = (
            datetime.fromtimestamp(bars[-1].time_unix, tz=timezone.utc) if bars else None
        )

        return ReplayCapabilityResponse(
            instrument_id=metadata.entity_id,
            display_symbol=metadata.display_symbol,
            is_replay_supported=is_supported,
            supported_intervals=supported_intervals or [interval],
            earliest_available_bar=earliest,
            latest_available_bar=latest,
            total_bars_available=total_bars,
            point_in_time_guarantee=False,
            methodological_notice=METHODOLOGICAL_NOTICE,
        )

    def start_session(
        self, user_id: UUID, request: ReplayStartRequest
    ) -> ReplayStartResponse:
        """Initializes a new authenticated historical replay session."""
        target_ident = request.instrument_id or request.symbol or "SPY"
        metadata = self.chart_service.resolve_instrument(target_ident)
        if not metadata:
            raise ValueError(f"Unknown instrument '{target_ident}' for historical chart replay.")

        # Retrieve authoritative historical bars (ordered ascending from oldest to latest)
        history = self.chart_service.get_chart_history(
            instrument_identifier=metadata.entity_id,
            interval=request.interval,
            limit=2000,
        )
        bars: List[ChartBarDTO] = history.bars
        if len(bars) < 2:
            raise ValueError(
                f"Insufficient historical data for instrument '{metadata.display_symbol}' "
                f"at interval '{request.interval}'. At least 2 bars are required for replay."
            )

        # Determine starting bar index
        start_index = 0
        if request.start_index is not None:
            start_index = max(0, min(request.start_index, len(bars) - 1))
        elif request.start_time is not None:
            target_ts = int(request.start_time.timestamp())
            # Find closest bar at or before target_ts
            matched_idx = 0
            for idx, bar in enumerate(bars):
                if bar.time_unix <= target_ts:
                    matched_idx = idx
                else:
                    break
            start_index = matched_idx
        else:
            # Default starting point: total_bars - history_window (or middle of history)
            start_index = max(0, len(bars) - request.history_window)

        # Generate unique session ID
        session_id = uuid4()

        # Compute source revision fingerprint
        raw_fingerprint = (
            f"{metadata.entity_id}:{request.interval}:{len(bars)}:{bars[-1].timestamp}"
        )
        revision_fingerprint = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()[:16]


        source_snapshot = ReplaySourceSnapshot(
            instrument_entity_id=metadata.entity_id,
            display_symbol=metadata.display_symbol,
            canonical_market_series_identity={
                "venue": metadata.market_or_venue,
                "asset_class": metadata.asset_class,
                "currency": metadata.price_currency,
            },
            interval=request.interval,
            provider="canonical_clickhouse",
            venue=metadata.market_or_venue,
            price_basis="CLOSE",
            adjustment_basis="SPLIT_ADJUSTED",
            quote_unit=metadata.price_currency,
            source_revision_fingerprint=revision_fingerprint,
        )

        session = ReplaySessionInternal(
            session_id=session_id,
            owner_user_id=user_id,
            target_panel_id=request.panel_id,
            instrument_entity_id=metadata.entity_id,
            display_symbol=metadata.display_symbol,
            interval=request.interval,
            source_snapshot=source_snapshot,
            bars=bars,
            start_index=start_index,
            cursor_index=start_index,
            history_window=request.history_window,
            playback_speed=request.playback_speed,
        )

        created_dto = self.session_manager.create_session(session)
        revealed_bars = session.get_revealed_bars()

        return ReplayStartResponse(session=created_dto, revealed_bars=revealed_bars)

    def get_session_status(self, session_id: UUID, user_id: UUID) -> ReplaySessionDTO:
        """Retrieves session metadata verifying ownership."""
        session = self.session_manager.get_session(session_id=session_id, user_id=user_id)
        if not session:
            raise KeyError(f"Replay session '{session_id}' not found or access denied.")
        return session.to_dto()

    def step_session(
        self, session_id: UUID, user_id: UUID, request: ReplayStepRequest
    ) -> ReplayStepResponse:
        """Advances or steps back the replay cursor by specified count.

        FUTURE DATA ISOLATION:
        - When stepping forward, returns ONLY the newly revealed bar.
        - When stepping backward, returns the removed index and hides subsequent bars.
        - NEVER returns future bars in the response.
        """
        session = self.session_manager.get_session(session_id=session_id, user_id=user_id)
        if not session:
            raise KeyError(f"Replay session '{session_id}' not found or access denied.")

        if (
            request.expected_cursor_index is not None
            and request.expected_cursor_index != session.cursor_index
        ):
            logger.warning(
                f"Replay concurrency warning: expected cursor {request.expected_cursor_index} "
                f"!= current {session.cursor_index}"
            )

        total_bars = len(session.bars)
        direction = request.direction

        if direction == ReplayStepDirection.FORWARD:
            if session.cursor_index >= total_bars - 1:
                session.status = ReplaySessionStatus.END_OF_DATA
                return ReplayStepResponse(
                    session_id=session.session_id,
                    status=session.status,
                    cursor_index=session.cursor_index,
                    cursor_bar=session.get_cursor_bar(),
                    direction="forward",
                    revealed_bar=None,
                    removed_bar_index=None,
                    is_end_of_data=True,
                    is_start_of_data=session.cursor_index == 0,
                    revealed_bars_count=session.cursor_index + 1,
                    total_bars=total_bars,
                )

            # Advance cursor
            new_index = min(session.cursor_index + request.count, total_bars - 1)
            session.cursor_index = new_index
            session.status = (
                ReplaySessionStatus.END_OF_DATA
                if new_index >= total_bars - 1
                else ReplaySessionStatus.READY
            )
            revealed_bar = session.bars[new_index]

            return ReplayStepResponse(
                session_id=session.session_id,
                status=session.status,
                cursor_index=new_index,
                cursor_bar=revealed_bar,
                direction="forward",
                revealed_bar=revealed_bar,
                removed_bar_index=None,
                is_end_of_data=new_index >= total_bars - 1,
                is_start_of_data=new_index == 0,
                revealed_bars_count=new_index + 1,
                total_bars=total_bars,
            )

        else:  # BACKWARD
            if session.cursor_index <= 0:
                return ReplayStepResponse(
                    session_id=session.session_id,
                    status=session.status,
                    cursor_index=0,
                    cursor_bar=session.bars[0] if session.bars else None,
                    direction="backward",
                    revealed_bar=None,
                    removed_bar_index=None,
                    is_end_of_data=False,
                    is_start_of_data=True,
                    revealed_bars_count=1 if session.bars else 0,
                    total_bars=total_bars,
                )

            removed_index = session.cursor_index
            new_index = max(0, session.cursor_index - request.count)
            session.cursor_index = new_index
            session.status = ReplaySessionStatus.READY

            return ReplayStepResponse(
                session_id=session.session_id,
                status=session.status,
                cursor_index=new_index,
                cursor_bar=session.bars[new_index],
                direction="backward",
                revealed_bar=None,
                removed_bar_index=removed_index,
                is_end_of_data=False,
                is_start_of_data=new_index == 0,
                revealed_bars_count=new_index + 1,
                total_bars=total_bars,
            )

    def seek_session(
        self, session_id: UUID, user_id: UUID, request: ReplaySeekRequest
    ) -> ReplaySeekResponse:
        """Relocates the replay cursor to an authorized target index or timestamp."""
        session = self.session_manager.get_session(session_id=session_id, user_id=user_id)
        if not session:
            raise KeyError(f"Replay session '{session_id}' not found or access denied.")

        total_bars = len(session.bars)
        target_index = session.cursor_index

        if request.target_index is not None:
            target_index = max(0, min(request.target_index, total_bars - 1))
        elif request.target_time is not None:
            target_ts = int(request.target_time.timestamp())
            matched_idx = 0
            for idx, bar in enumerate(session.bars):
                if bar.time_unix <= target_ts:
                    matched_idx = idx
                else:
                    break
            target_index = matched_idx

        session.cursor_index = target_index
        session.status = (
            ReplaySessionStatus.END_OF_DATA
            if target_index >= total_bars - 1
            else ReplaySessionStatus.READY
        )

        return ReplaySeekResponse(
            session=session.to_dto(),
            revealed_bars=session.get_revealed_bars(),
        )

    def close_session(self, session_id: UUID, user_id: UUID) -> bool:
        """Terminates an active replay session and releases ephemeral resources."""
        return self.session_manager.delete_session(session_id=session_id, user_id=user_id)

    def calculate_replay_indicators(
        self, session_id: UUID, user_id: UUID, request: IndicatorCalculationRequest
    ) -> IndicatorCalculationResponse:
        """Calculates requested TA-Lib indicators strictly over replay-visible bars.

        CRITICAL FUTURE DATA ISOLATION:
        The input series passed to TA-Lib calculators terminates strictly at cursor_index.
        Bars N+1.. cannot influence calculation outputs or warmup lookbacks.
        """
        session = self.session_manager.get_session(session_id=session_id, user_id=user_id)
        if not session:
            raise KeyError(f"Replay session '{session_id}' not found or access denied.")

        # Extract only revealed bars up to cursor
        revealed_bars = session.bars[: session.cursor_index + 1]
        if not revealed_bars:
            raise ValueError("No historical bars currently revealed in replay session.")

        # Compute each requested indicator instance over the cursor-bounded input series
        results = []
        for inst in request.instances:
            try:
                definition, calculator = self.indicator_service.registry.get(
                    inst.indicator_id, inst.version
                )
                norm_params = calculator.validate_parameters(inst.parameters)
                res = calculator.calculate(
                    instance_id=inst.instance_id,
                    bars=revealed_bars,
                    params=norm_params,
                    requested_start=request.start,
                    requested_end=request.end,
                )
                if inst.color or inst.line_width:
                    for s in res.series:
                        if inst.color:
                            s.color = inst.color
                        if inst.line_width:
                            s.line_width = inst.line_width
                results.append(res)
            except Exception as e:
                logger.error(
                    f"Error calculating replay indicator '{inst.indicator_id}': {e}",
                    exc_info=True,
                )
                from ..indicators.models import IndicatorCalculationResult, IndicatorStatus

                results.append(
                    IndicatorCalculationResult(
                        instance_id=inst.instance_id,
                        indicator_id=inst.indicator_id,
                        version=inst.version,
                        status=IndicatorStatus.ERROR,
                        error_message=str(e),
                        series=[],
                    )
                )

        return IndicatorCalculationResponse(
            instrument_entity_id=str(session.instrument_entity_id),
            symbol=session.display_symbol,
            interval=session.interval,
            calculated_at=datetime.now(timezone.utc).isoformat(),
            results=results,
        )



# Global singleton instance
default_replay_service = HistoricalChartReplayService()
