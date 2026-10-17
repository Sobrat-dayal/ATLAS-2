"""MarketMoverRankingService for ATLAS Market Movers V1 (Stage 63).

Implements institutional qualification, Decimal arithmetic, deterministic sorting,
and transparent coverage reporting across supported financial asset classes.

Guarantees:
- Institutional numerical fidelity using Decimal (no float conversions).
- Zero denominator protection: non-positive reference prices excluded from % return rankings.
- Zero price change excluded from both Top Gainers and Top Losers.
- Missing volume excluded from Most Active (missing is never fabricated as zero).
- Deterministic tie-breaking using canonical instrument UUID.
- Keyset / stable snapshot pagination with bounded limits.
- 100% Read-Only: 0 writes, 0 external provider fanouts.
"""

import base64
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status

from .config import (
    ComparisonWindow,
    CoverageStatus,
    ExclusionReason,
    MoverCategory,
    MoverMetricDefinition,
)
from .models import (
    MarketMoverResponse,
    MoverCoverage,
    MoverMetricOptionsResponse,
    MoverRankedItem,
    MoverUniverseResponse,
)
from .repository import CandidateObservation, MarketMoversRepository

logger = logging.getLogger(__name__)


class MarketMoverRankingService:
    """
    Core ranking and qualification engine for ATLAS Market Movers.
    """

    def __init__(self, repository: Optional[MarketMoversRepository] = None):
        self._repository = repository or MarketMoversRepository()

    def get_supported_universes(self) -> MoverUniverseResponse:
        """Returns all configured, authorized ranking universes."""
        from .config import DEFAULT_MOVER_UNIVERSE_ID, SUPPORTED_MOVER_UNIVERSES

        return MoverUniverseResponse(
            schema_version="v1",
            universes=SUPPORTED_MOVER_UNIVERSES,
            default_universe_id=DEFAULT_MOVER_UNIVERSE_ID,
        )

    def get_metric_options(self, universe_id: str) -> MoverMetricOptionsResponse:
        """Returns valid metric policies, windows, and activity units for the universe."""
        universe = self._repository.get_universe_definition(universe_id)
        if not universe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown mover universe ID '{universe_id}'.",
            )

        metrics: List[MoverMetricDefinition] = []
        for cat in universe.supported_categories:
            if cat == MoverCategory.GAINERS:
                metrics.append(
                    MoverMetricDefinition(
                        metric_id=f"{universe.universe_id}:gainers:{universe.default_window.value}",
                        metric_kind=MoverCategory.GAINERS,
                        asset_class=universe.asset_class,
                        observation_basis="Last Traded Price",
                        reference_basis="Qualified Prior Reference Close",
                        window=universe.default_window,
                        unit="%",
                        sort_direction="DESC",
                        qualification_policy=(
                            "Requires positive price percentage return "
                            "relative to positive reference."
                        ),
                    )
                )
            elif cat == MoverCategory.LOSERS:
                metrics.append(
                    MoverMetricDefinition(
                        metric_id=f"{universe.universe_id}:losers:{universe.default_window.value}",
                        metric_kind=MoverCategory.LOSERS,
                        asset_class=universe.asset_class,
                        observation_basis="Last Traded Price",
                        reference_basis="Qualified Prior Reference Close",
                        window=universe.default_window,
                        unit="%",
                        sort_direction="ASC",
                        qualification_policy=(
                            "Requires negative price percentage return "
                            "relative to positive reference."
                        ),
                    )
                )
            elif cat == MoverCategory.MOST_ACTIVE:
                metrics.append(
                    MoverMetricDefinition(
                        metric_id=(
                            f"{universe.universe_id}:most_active:{universe.default_window.value}"
                        ),
                        metric_kind=MoverCategory.MOST_ACTIVE,
                        asset_class=universe.asset_class,
                        observation_basis=universe.activity_metric_label or "Trading Activity",
                        reference_basis="Trading Session Window",
                        window=universe.default_window,
                        unit=universe.activity_unit or "volume",
                        sort_direction="DESC",
                        qualification_policy=(
                            "Requires verified session trading volume in specified activity unit."
                        ),
                    )
                )

        return MoverMetricOptionsResponse(
            schema_version="v1",
            universe_id=universe.universe_id,
            asset_class=universe.asset_class,
            supported_categories=universe.supported_categories,
            supported_windows=universe.supported_windows,
            activity_metric_label=universe.activity_metric_label,
            activity_unit=universe.activity_unit,
            metrics=metrics,
        )

    async def get_market_movers(
        self,
        universe_id: str = "univ_us_equities",
        category: MoverCategory = MoverCategory.GAINERS,
        window: Optional[ComparisonWindow] = None,
        exchange: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> MarketMoverResponse:
        """
        Executes qualified ranking pipeline:
        1. Resolves and validates ranking universe.
        2. Validates metric and comparison window.
        3. Retrieves raw candidate observations.
        4. Applies qualification rules (prior to sorting).
        5. Performs deterministic sorting with UUID tie-breaking.
        6. Computes comprehensive coverage statistics.
        7. Returns bounded paginated results.
        """
        universe = self._repository.get_universe_definition(universe_id)
        if not universe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or unsupported mover universe ID: '{universe_id}'.",
            )

        if category not in universe.supported_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Category '{category.value}' is not supported for "
                    f"universe '{universe.universe_id}'."
                ),
            )

        active_window = window or universe.default_window
        if active_window not in universe.supported_windows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Comparison window '{active_window.value}' is not supported for "
                    f"universe '{universe.universe_id}'."
                ),
            )

        # 1. Candidate Retrieval
        candidates: List[CandidateObservation] = await (
            self._repository.get_candidates_for_universe(universe)
        )

        # Optional venue filter
        if exchange and exchange.strip() and exchange.lower() != "all":
            filtered_candidates = [
                c for c in candidates if c.exchange_or_venue.upper() == exchange.strip().upper()
            ]
        else:
            filtered_candidates = candidates

        now = datetime.now(timezone.utc)
        exclusion_reasons: Dict[str, int] = {}

        def record_exclusion(reason: ExclusionReason):
            exclusion_reasons[reason.value] = exclusion_reasons.get(reason.value, 0) + 1

        qualified_items: List[Tuple[Decimal, MoverRankedItem]] = []

        # 2. Qualification Pipeline (Evaluated Before Sorting)
        for cand in filtered_candidates:
            if not cand.is_active:
                record_exclusion(ExclusionReason.INSTRUMENT_INACTIVE)
                continue

            if category in (MoverCategory.GAINERS, MoverCategory.LOSERS):
                if cand.current_price is None:
                    record_exclusion(ExclusionReason.NO_CURRENT_QUOTE)
                    continue

                if cand.reference_price is None:
                    record_exclusion(ExclusionReason.NO_REFERENCE)
                    continue

                # Denominator check: Non-positive reference close cannot yield standard % return
                if cand.reference_price <= Decimal("0"):
                    record_exclusion(ExclusionReason.INVALID_DENOMINATOR)
                    continue

                abs_change = cand.current_price - cand.reference_price
                pct_change = (abs_change / cand.reference_price) * Decimal("100")

                # Strictly exclude zero-change items from Gainers and Losers
                if abs_change == Decimal("0"):
                    record_exclusion(ExclusionReason.OTHER)
                    continue

                if category == MoverCategory.GAINERS:
                    if pct_change <= Decimal("0"):
                        # Negative move cannot qualify as a Gainer
                        continue
                    ranking_val = pct_change
                else:  # LOSERS
                    if pct_change >= Decimal("0"):
                        # Positive move cannot qualify as a Loser
                        continue
                    ranking_val = pct_change

                item = MoverRankedItem(
                    rank=1,  # Will be assigned after sort
                    instrument_entity_id=cand.instrument_entity_id,
                    market_series_identity=cand.market_series_identity,
                    display_name=cand.display_name,
                    symbol=cand.symbol,
                    asset_class=cand.asset_class,
                    exchange_or_venue=cand.exchange_or_venue,
                    ranking_value=ranking_val,
                    ranking_unit="%",
                    current_observation=cand.current_price,
                    reference_observation=cand.reference_price,
                    absolute_change=abs_change,
                    percent_change=pct_change,
                    activity_observation=cand.trading_volume,
                    activity_unit=cand.volume_unit,
                    source_timestamp=cand.source_timestamp,
                    reference_timestamp=cand.reference_timestamp,
                    reference_period_label=cand.reference_period_label,
                    provider=cand.provider,
                    freshness_status=cand.freshness_status,
                    delay_status=cand.delay_status,
                    delivery_delay_seconds=cand.delivery_delay_seconds,
                )
                qualified_items.append((ranking_val, item))

            elif category == MoverCategory.MOST_ACTIVE:
                if cand.trading_volume is None:
                    record_exclusion(ExclusionReason.MISSING_VOLUME)
                    continue

                ranking_val = cand.trading_volume

                abs_change = None
                pct_change = None
                if cand.current_price is not None and cand.reference_price is not None:
                    abs_change = cand.current_price - cand.reference_price
                    if cand.reference_price > Decimal("0"):
                        pct_change = (abs_change / cand.reference_price) * Decimal("100")

                item = MoverRankedItem(
                    rank=1,
                    instrument_entity_id=cand.instrument_entity_id,
                    market_series_identity=cand.market_series_identity,
                    display_name=cand.display_name,
                    symbol=cand.symbol,
                    asset_class=cand.asset_class,
                    exchange_or_venue=cand.exchange_or_venue,
                    ranking_value=ranking_val,
                    ranking_unit=cand.volume_unit or universe.activity_unit or "volume",
                    current_observation=cand.current_price,
                    reference_observation=cand.reference_price,
                    absolute_change=abs_change,
                    percent_change=pct_change,
                    activity_observation=cand.trading_volume,
                    activity_unit=cand.volume_unit or universe.activity_unit,
                    source_timestamp=cand.source_timestamp,
                    reference_timestamp=cand.reference_timestamp,
                    reference_period_label=cand.reference_period_label,
                    provider=cand.provider,
                    freshness_status=cand.freshness_status,
                    delay_status=cand.delay_status,
                    delivery_delay_seconds=cand.delivery_delay_seconds,
                )
                qualified_items.append((ranking_val, item))

        # 3. Deterministic Sorting with UUID Tie-Breaking
        if category == MoverCategory.GAINERS:
            # Sort: percent_change DESC, UUID ASC
            qualified_items.sort(key=lambda x: (-x[0], str(x[1].instrument_entity_id)))
        elif category == MoverCategory.LOSERS:
            # Sort: percent_change ASC (most negative first), UUID ASC
            qualified_items.sort(key=lambda x: (x[0], str(x[1].instrument_entity_id)))
        elif category == MoverCategory.MOST_ACTIVE:
            # Sort: trading_volume DESC, UUID ASC
            qualified_items.sort(key=lambda x: (-x[0], str(x[1].instrument_entity_id)))

        # 4. Coverage Metrics
        candidate_count = len(filtered_candidates)
        evaluated_count = candidate_count
        qualified_count = len(qualified_items)
        excluded_count = sum(exclusion_reasons.values())

        if qualified_count == 0:
            coverage_status = CoverageStatus.UNAVAILABLE
        elif excluded_count == 0 and candidate_count == len(candidates):
            coverage_status = CoverageStatus.COMPLETE_FOR_DEFINED_UNIVERSE
        else:
            coverage_status = CoverageStatus.PARTIAL_COVERAGE

        coverage = MoverCoverage(
            universe_size=len(candidates),
            candidate_count=candidate_count,
            evaluated_count=evaluated_count,
            qualified_count=qualified_count,
            excluded_count=excluded_count,
            exclusion_reasons=exclusion_reasons,
            coverage_status=coverage_status,
            ranking_as_of=now,
        )

        # 5. Keyset / Offset Pagination
        offset = 0
        if cursor:
            try:
                decoded = base64.b64decode(cursor).decode("utf-8")
                cursor_data = json.loads(decoded)
                offset = cursor_data.get("offset", 0)
            except Exception:
                offset = 0

        paged_tuples = qualified_items[offset : offset + limit]
        has_more = (offset + limit) < len(qualified_items)
        next_cursor = None
        if has_more:
            next_data = {"offset": offset + limit}
            next_cursor = base64.b64encode(json.dumps(next_data).encode("utf-8")).decode("utf-8")

        # Assign 1-based ranks based on global snapshot position
        ranked_items: List[MoverRankedItem] = []
        for idx, (_, item) in enumerate(paged_tuples):
            # Reconstruct with accurate rank
            ranked_items.append(
                MoverRankedItem(
                    rank=offset + idx + 1,
                    instrument_entity_id=item.instrument_entity_id,
                    market_series_identity=item.market_series_identity,
                    display_name=item.display_name,
                    symbol=item.symbol,
                    asset_class=item.asset_class,
                    exchange_or_venue=item.exchange_or_venue,
                    ranking_value=item.ranking_value,
                    ranking_unit=item.ranking_unit,
                    current_observation=item.current_observation,
                    reference_observation=item.reference_observation,
                    absolute_change=item.absolute_change,
                    percent_change=item.percent_change,
                    activity_observation=item.activity_observation,
                    activity_unit=item.activity_unit,
                    source_timestamp=item.source_timestamp,
                    reference_timestamp=item.reference_timestamp,
                    reference_period_label=item.reference_period_label,
                    provider=item.provider,
                    freshness_status=item.freshness_status,
                    delay_status=item.delay_status,
                    delivery_delay_seconds=item.delivery_delay_seconds,
                    eligibility_notes=item.eligibility_notes,
                )
            )

        snapshot_id = f"snap_{universe.universe_id}_{category.value}_{int(now.timestamp())}"
        metric_id = f"{universe.universe_id}:{category.value}:{active_window.value}"

        return MarketMoverResponse(
            schema_version="v1",
            snapshot_id=snapshot_id,
            universe_id=universe.universe_id,
            universe_display_name=universe.display_name,
            category=category,
            metric_id=metric_id,
            window=active_window,
            asset_class=universe.asset_class,
            calculated_at=now,
            coverage=coverage,
            items=ranked_items,
            next_cursor=next_cursor,
            has_more=has_more,
            source_status="ok",
        )
