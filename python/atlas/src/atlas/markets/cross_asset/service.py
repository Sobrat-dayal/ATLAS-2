"""Service layer for ATLAS Cross-Asset Markets V1 (Stage 65).

Coordinates multi-asset observation retrieval, temporal alignment verification,
no-look-ahead validation, Decimal percentage price return calculation,
native metric presentation, benchmark/proxy distinction, and coverage auditing.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .config import (
    DEFAULT_ALIGNMENT_TOLERANCE_SECONDS,
    DEFAULT_CURRENCY_POLICY,
    MAX_SELECTION_COUNT,
    SUPPORTED_CROSS_ASSET_UNIVERSES,
    WINDOW_DURATIONS_HOURS,
    AssetClassEnum,
    CrossAssetCoverageStatus,
    CrossAssetExclusionReason,
    CrossAssetMode,
    CrossAssetUniverseDefinition,
    CrossAssetWindow,
)
from .models import (
    AlignedPricePerformance,
    AssetClassSummarySection,
    CrossAssetCoverage,
    CrossAssetMember,
    CrossAssetOptionsResponse,
    CrossAssetOverviewResponse,
    CrossAssetUniverseResponse,
    NativeMetricObservation,
)
from .repository import CrossAssetMarketRepository


class CrossAssetMarketService:
    """Service providing institutional multi-market intelligence and aligned performance."""

    def __init__(
        self,
        repository: Optional[CrossAssetMarketRepository] = None,
        anchor_time: Optional[datetime] = None,
    ) -> None:
        self._anchor_time = anchor_time or datetime(2026, 10, 17, 18, 0, 0, tzinfo=timezone.utc)
        self._repository = repository or CrossAssetMarketRepository(anchor_time=self._anchor_time)

    def get_universes(self) -> CrossAssetUniverseResponse:
        """Returns supported cross-asset candidate universes."""
        return CrossAssetUniverseResponse(
            universes=SUPPORTED_CROSS_ASSET_UNIVERSES,
            count=len(SUPPORTED_CROSS_ASSET_UNIVERSES),
        )

    def get_options(self) -> CrossAssetOptionsResponse:
        """Returns supported analytical modes, observation windows, and policies."""
        return CrossAssetOptionsResponse(
            modes=list(CrossAssetMode),
            windows=list(CrossAssetWindow),
            asset_classes=list(AssetClassEnum),
            max_selection_count=MAX_SELECTION_COUNT,
            currency_policy=DEFAULT_CURRENCY_POLICY,
            alignment_tolerance_seconds=DEFAULT_ALIGNMENT_TOLERANCE_SECONDS,
        )

    def get_cross_asset_overview(
        self,
        universe_id: str = "univ_cross_asset_macro",
        mode: CrossAssetMode = CrossAssetMode.NATIVE_OVERVIEW,
        window: CrossAssetWindow = CrossAssetWindow.LAST_24H,
        selected_symbols: Optional[List[str]] = None,
    ) -> CrossAssetOverviewResponse:
        """Computes and returns a verified Cross-Asset Market Snapshot."""
        # 1. Resolve Universe Definition
        universe_def: Optional[CrossAssetUniverseDefinition] = next(
            (u for u in SUPPORTED_CROSS_ASSET_UNIVERSES if u.universe_id == universe_id),
            None,
        )
        if universe_def is None:
            universe_def = SUPPORTED_CROSS_ASSET_UNIVERSES[0]

        # 2. Resolve Candidate Symbols (Enforce bounded selection max 12)
        if selected_symbols:
            symbols = [s.strip().upper() for s in selected_symbols if s.strip()]
            if len(symbols) > MAX_SELECTION_COUNT:
                symbols = symbols[:MAX_SELECTION_COUNT]
        else:
            symbols = universe_def.default_symbols

        candidates = self._repository.get_candidates_by_symbols(symbols)

        # 3. Resolve Common Comparison Window (UTC)
        requested_end = self._anchor_time
        hours = WINDOW_DURATIONS_HOURS.get(window, 24)
        requested_start = requested_end - timedelta(hours=hours)

        members: List[CrossAssetMember] = []
        exclusions: List[Dict[str, Any]] = []
        exclusions_by_reason: Dict[str, int] = {}

        # 4. Process Each Candidate Instrument
        for cand in candidates:
            # A. Native Metric Observation
            native_obs = NativeMetricObservation(
                metric_kind=cand.native_metric_kind,
                display_label=cand.native_display_label,
                current_value=cand.current_value,
                reference_value=cand.reference_value,
                change_value=cand.change_value,
                change_percent=cand.change_percent,
                unit=cand.native_unit,
                as_of_time=cand.as_of_time,
                session_status=cand.session_status,
            )

            # B. Aligned Price Performance Evaluation
            aligned_perf: AlignedPricePerformance
            if not cand.is_price_series:
                # E.g. Bond Yield series without evaluated price series
                reason = CrossAssetExclusionReason.UNSUPPORTED_METRIC
                detail = (
                    "Bond yield level and basis points are not a price return series. "
                    "Cannot be mathematically converted to percentage price return "
                    "without an evaluated price series."
                )
                aligned_perf = AlignedPricePerformance(
                    eligible=False,
                    quote_currency=cand.quote_currency,
                    quote_unit=cand.quote_unit,
                    currency_interpretation=DEFAULT_CURRENCY_POLICY,
                    is_common_currency_converted=False,
                    exclusion_reason=reason,
                    exclusion_detail=detail,
                )
                exclusions_by_reason[reason.value] = exclusions_by_reason.get(reason.value, 0) + 1
                exclusions.append(
                    {
                        "symbol": cand.symbol,
                        "display_name": cand.display_name,
                        "asset_class": cand.asset_class.value,
                        "reason": reason.value,
                        "detail": detail,
                    }
                )
            elif window not in cand.window_start_prices:
                reason = CrossAssetExclusionReason.NO_START_REFERENCE
                detail = (
                    "No historical reference price found at or before requested window start "
                    f"({requested_start.isoformat()})."
                )
                aligned_perf = AlignedPricePerformance(
                    eligible=False,
                    quote_currency=cand.quote_currency,
                    quote_unit=cand.quote_unit,
                    currency_interpretation=DEFAULT_CURRENCY_POLICY,
                    is_common_currency_converted=False,
                    exclusion_reason=reason,
                    exclusion_detail=detail,
                )
                exclusions_by_reason[reason.value] = exclusions_by_reason.get(reason.value, 0) + 1
                exclusions.append(
                    {
                        "symbol": cand.symbol,
                        "display_name": cand.display_name,
                        "asset_class": cand.asset_class.value,
                        "reason": reason.value,
                        "detail": detail,
                    }
                )
            else:
                start_p = cand.window_start_prices[window]
                end_p = cand.current_value

                if start_p <= Decimal("0"):
                    reason = CrossAssetExclusionReason.INVALID_DENOMINATOR
                    detail = (
                        f"Start reference price ({start_p}) is non-positive; "
                        "percentage return undefined."
                    )
                    aligned_perf = AlignedPricePerformance(
                        eligible=False,
                        quote_currency=cand.quote_currency,
                        quote_unit=cand.quote_unit,
                        currency_interpretation=DEFAULT_CURRENCY_POLICY,
                        is_common_currency_converted=False,
                        exclusion_reason=reason,
                        exclusion_detail=detail,
                    )
                    exclusions_by_reason[reason.value] = (
                        exclusions_by_reason.get(reason.value, 0) + 1
                    )
                    exclusions.append(
                        {
                            "symbol": cand.symbol,
                            "display_name": cand.display_name,
                            "asset_class": cand.asset_class.value,
                            "reason": reason.value,
                            "detail": detail,
                        }
                    )
                else:
                    offset_sec = cand.window_start_offsets_sec.get(window, 0)
                    if offset_sec > DEFAULT_ALIGNMENT_TOLERANCE_SECONDS:
                        reason = CrossAssetExclusionReason.WINDOW_MISALIGNED
                        detail = (
                            f"Start observation offset ({offset_sec}s) exceeds maximum "
                            f"tolerance ({DEFAULT_ALIGNMENT_TOLERANCE_SECONDS}s)."
                        )
                        aligned_perf = AlignedPricePerformance(
                            eligible=False,
                            quote_currency=cand.quote_currency,
                            quote_unit=cand.quote_unit,
                            currency_interpretation=DEFAULT_CURRENCY_POLICY,
                            is_common_currency_converted=False,
                            exclusion_reason=reason,
                            exclusion_detail=detail,
                        )
                        exclusions_by_reason[reason.value] = (
                            exclusions_by_reason.get(reason.value, 0) + 1
                        )
                        exclusions.append(
                            {
                                "symbol": cand.symbol,
                                "display_name": cand.display_name,
                                "asset_class": cand.asset_class.value,
                                "reason": reason.value,
                                "detail": detail,
                            }
                        )
                    else:
                        # Strictly qualified aligned price return
                        # Effective start time is strictly at or before requested_start
                        effective_start = requested_start - timedelta(seconds=offset_sec)
                        effective_end = cand.as_of_time
                        end_offset_sec = int(abs((effective_end - requested_end).total_seconds()))

                        # Formula: ((end_price - start_price) / start_price) * 100
                        price_return = round(((end_p - start_p) / start_p) * Decimal("100"), 4)
                        indexed_val = round((end_p / start_p) * Decimal("100"), 4)

                        aligned_perf = AlignedPricePerformance(
                            eligible=True,
                            price_return_percent=price_return,
                            indexed_value=indexed_val,
                            start_price=start_p,
                            end_price=end_p,
                            quote_currency=cand.quote_currency,
                            quote_unit=cand.quote_unit,
                            effective_start_time=effective_start,
                            effective_end_time=effective_end,
                            start_time_offset_seconds=offset_sec,
                            end_time_offset_seconds=end_offset_sec,
                            currency_interpretation=DEFAULT_CURRENCY_POLICY,
                            is_common_currency_converted=False,
                        )

            member = CrossAssetMember(
                instrument_entity_id=cand.instrument_entity_id,
                market_series_identity=cand.market_series_identity,
                display_name=cand.display_name,
                symbol=cand.symbol,
                asset_class=cand.asset_class,
                market_or_venue=cand.market_or_venue,
                is_benchmark=cand.is_benchmark,
                is_proxy=cand.is_proxy,
                proxy_kind=cand.proxy_kind,
                proxy_benchmark_target=cand.proxy_benchmark_target,
                native_metric=native_obs,
                aligned_performance=aligned_perf,
                freshness_status=cand.freshness_status,
                is_delayed=cand.is_delayed,
                delay_minutes=cand.delay_minutes,
                provider=cand.provider,
            )
            members.append(member)

        # 5. Group by Asset Class for Summary Sections
        asset_class_sections: List[AssetClassSummarySection] = []
        asset_class_labels: Dict[AssetClassEnum, str] = {
            AssetClassEnum.EQUITIES: "Equities Markets",
            AssetClassEnum.ETFS: "ETFs & Funds Proxies",
            AssetClassEnum.FX: "Foreign Exchange (FX)",
            AssetClassEnum.CRYPTO: "Cryptocurrency Spot",
            AssetClassEnum.BONDS: "Government Bonds & Sovereign Debt",
            AssetClassEnum.FUTURES: "Commodities & Futures Contracts",
        }
        native_desc_map: Dict[AssetClassEnum, str] = {
            AssetClassEnum.EQUITIES: (
                "Regular-session traded price and % change vs previous official close."
            ),
            AssetClassEnum.ETFS: (
                "Exchange-traded market price % change (distinguished from NAV)."
            ),
            AssetClassEnum.FX: (
                "Spot exchange rate change % preserving directional pair orientation."
            ),
            AssetClassEnum.CRYPTO: (
                "Continuous 24/7 rolling 24-hour price change in quoted denomination."
            ),
            AssetClassEnum.BONDS: (
                "Benchmark yield level in % and yield change in basis points (bps)."
            ),
            AssetClassEnum.FUTURES: (
                "Last traded contract price and change against prior settlement."
            ),
        }

        for ac in AssetClassEnum:
            ac_members = [m for m in members if m.asset_class == ac]
            if ac_members:
                ac_qualified = sum(1 for m in ac_members if m.aligned_performance.eligible)
                ac_cov_status = (
                    CrossAssetCoverageStatus.COMPLETE_FOR_DEFINED_SET
                    if (ac_qualified == len(ac_members) or mode == CrossAssetMode.NATIVE_OVERVIEW)
                    else (
                        CrossAssetCoverageStatus.PARTIAL
                        if ac_qualified > 0
                        else CrossAssetCoverageStatus.UNAVAILABLE
                    )
                )
                asset_class_sections.append(
                    AssetClassSummarySection(
                        asset_class=ac,
                        display_title=asset_class_labels.get(ac, ac.value.title()),
                        native_metric_description=native_desc_map.get(
                            ac, "Native market observation."
                        ),
                        representative_members=ac_members,
                        total_members=len(ac_members),
                        qualified_members=ac_qualified,
                        coverage_status=ac_cov_status,
                    )
                )

        # 6. Compute Coverage & Completeness Status
        qualified_count = sum(1 for m in members if m.aligned_performance.eligible)
        excluded_count = len(members) - qualified_count

        if mode == CrossAssetMode.NATIVE_OVERVIEW:
            completeness = (
                CrossAssetCoverageStatus.COMPLETE_FOR_DEFINED_SET
                if members
                else CrossAssetCoverageStatus.UNAVAILABLE
            )
        else:
            if qualified_count == len(members) and len(members) > 0:
                completeness = CrossAssetCoverageStatus.COMPLETE_FOR_DEFINED_SET
            elif qualified_count > 0:
                completeness = CrossAssetCoverageStatus.PARTIAL
            else:
                completeness = CrossAssetCoverageStatus.UNAVAILABLE

        included_classes = list({m.asset_class for m in members})
        all_classes = list(AssetClassEnum)
        unavailable_classes = [ac for ac in all_classes if ac not in included_classes]

        coverage = CrossAssetCoverage(
            requested_members=len(candidates),
            authorized_members=len(candidates),
            evaluated_members=len(candidates),
            qualified_members=qualified_count,
            excluded_members=excluded_count,
            exclusions_by_reason=exclusions_by_reason,
            included_asset_classes=included_classes,
            unavailable_asset_classes=unavailable_classes,
            completeness_status=completeness,
        )

        # 7. Deterministic Sorting
        if mode == CrossAssetMode.ALIGNED_PERFORMANCE:
            # Sort qualified items by price_return_percent descending; excluded items at end
            comparison_members = sorted(
                members,
                key=lambda m: (
                    0 if m.aligned_performance.eligible else 1,
                    -(m.aligned_performance.price_return_percent or Decimal("-999999"))
                    if m.aligned_performance.eligible
                    else Decimal("0"),
                    m.symbol,
                ),
            )
        else:
            # Grouped by asset class order then symbol
            comparison_members = sorted(
                members,
                key=lambda m: (list(AssetClassEnum).index(m.asset_class), m.symbol),
            )

        snapshot_id = f"cross_asset_snap_{uuid4().hex[:12]}"
        methodology = (
            "Native Market Overview: Preserves individual asset-class quotation conventions, "
            "bond yields in basis points, and futures settlement changes. "
            "Aligned Price Performance: Evaluates strict common-window UTC start/end price "
            "observations with zero look-ahead bias and maximum tolerance enforcement. "
            "Bond yields excluded."
        )

        return CrossAssetOverviewResponse(
            schema_version="1.0.0",
            snapshot_id=snapshot_id,
            universe_id=universe_def.universe_id,
            universe_name=universe_def.display_name,
            mode=mode,
            comparison_window=window,
            requested_start=requested_start,
            requested_end=requested_end,
            calculated_at=self._anchor_time,
            alignment_methodology=methodology,
            currency_policy_label=DEFAULT_CURRENCY_POLICY,
            coverage=coverage,
            asset_class_sections=asset_class_sections,
            comparison_members=comparison_members,
            exclusions=exclusions,
        )
