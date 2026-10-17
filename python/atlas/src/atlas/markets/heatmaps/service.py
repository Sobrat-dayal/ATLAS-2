"""MarketHeatmapService for ATLAS Market Heatmaps V1 (Stage 64).

Implements institutional qualification, whole-universe evaluation, verified weighting
normalization, GICS sector/industry hierarchical aggregation, and coverage transparency.

Guarantees:
- Never uses Top N mover ranking as a proxy for the entire market universe.
- Missing returns are never colored or represented as zero percent.
- Market-cap weighting strictly requires verified positive weights.
- Equal-size mode operates independently of market capitalization.
- Group aggregates explicitly label their calculation method (equal-weight vs cap-weighted).
"""

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Optional

from .config import (
    HeatmapComparisonWindow,
    HeatmapCoverageStatus,
    HeatmapExclusionReason,
    HeatmapHierarchyMode,
    HeatmapVisualizationMode,
)
from .models import (
    HeatmapCoverage,
    HeatmapGroupNode,
    HeatmapLeafNode,
    MarketHeatmapResponse,
)
from .repository import HeatmapCandidateObservation, MarketHeatmapRepository


class MarketHeatmapService:
    """Institutional calculation and aggregation service for ATLAS Market Heatmaps."""

    def __init__(self, repository: Optional[MarketHeatmapRepository] = None):
        self._repo = repository or MarketHeatmapRepository()

    async def get_heatmap_snapshot(
        self,
        universe_id: str = "univ_us_equities",
        visualization_mode: Optional[HeatmapVisualizationMode] = None,
        hierarchy_mode: Optional[HeatmapHierarchyMode] = None,
        comparison_window: Optional[HeatmapComparisonWindow] = None,
        sector_filter: Optional[str] = None,
        max_nodes: Optional[int] = None,
    ) -> MarketHeatmapResponse:
        """
        Generates a coherent, qualified market heatmap calculation snapshot.
        """
        universe = self._repo.get_universe_definition(universe_id)
        if universe is None:
            raise ValueError(f"Unknown heatmap universe: '{universe_id}'")

        # Resolve mode, hierarchy, and window defaults
        mode = visualization_mode or universe.default_mode
        hierarchy = hierarchy_mode or universe.default_hierarchy
        window = comparison_window or universe.default_window

        # Validate mode support
        if mode not in universe.supported_modes:
            supported_m = [m.value for m in universe.supported_modes]
            raise ValueError(
                f"Visualization mode '{mode.value}' is not supported by universe "
                f"'{universe.universe_id}'. Supported modes: {supported_m}"
            )

        # Validate hierarchy support
        if hierarchy not in universe.supported_hierarchies:
            supported_h = [h.value for h in universe.supported_hierarchies]
            raise ValueError(
                f"Hierarchy mode '{hierarchy.value}' is not supported by universe "
                f"'{universe.universe_id}'. Supported hierarchies: {supported_h}"
            )

        # Fetch candidate observations
        candidates = await self._repo.get_candidates_for_universe(universe)
        universe_size = len(candidates)

        # Optional sector filter
        if sector_filter and sector_filter.strip():
            target_sec = sector_filter.strip().lower()
            candidates = [
                c
                for c in candidates
                if (c.sector and c.sector.lower() == target_sec)
                or (not c.sector and target_sec == "unclassified")
            ]

        candidate_count = len(candidates)
        now = datetime.now(timezone.utc)
        snapshot_id = str(uuid.uuid4())

        leaves: List[HeatmapLeafNode] = []
        exclusion_breakdown: Dict[str, int] = defaultdict(int)
        missing_returns = 0
        missing_weights = 0
        unclassified_count = 0

        # Step 1: Evaluate candidate qualification and financial returns
        for c in candidates:
            sector_label = c.sector if c.sector and c.sector.strip() else "Unclassified"
            if sector_label == "Unclassified":
                unclassified_count += 1

            if not c.is_active:
                exclusion_breakdown[HeatmapExclusionReason.INACTIVE_SECURITY.value] += 1
                leaves.append(
                    self._create_leaf_node(
                        c=c,
                        sector_label=sector_label,
                        is_qualified=False,
                        exclusion=HeatmapExclusionReason.INACTIVE_SECURITY,
                    )
                )
                continue

            if c.current_price is None:
                missing_returns += 1
                exclusion_breakdown[HeatmapExclusionReason.NO_CURRENT_QUOTE.value] += 1
                leaves.append(
                    self._create_leaf_node(
                        c=c,
                        sector_label=sector_label,
                        is_qualified=False,
                        exclusion=HeatmapExclusionReason.NO_CURRENT_QUOTE,
                    )
                )
                continue

            if c.reference_price is None:
                missing_returns += 1
                exclusion_breakdown[HeatmapExclusionReason.NO_REFERENCE.value] += 1
                leaves.append(
                    self._create_leaf_node(
                        c=c,
                        sector_label=sector_label,
                        is_qualified=False,
                        exclusion=HeatmapExclusionReason.NO_REFERENCE,
                    )
                )
                continue

            if c.reference_price <= Decimal("0"):
                missing_returns += 1
                exclusion_breakdown[HeatmapExclusionReason.INVALID_DENOMINATOR.value] += 1
                leaves.append(
                    self._create_leaf_node(
                        c=c,
                        sector_label=sector_label,
                        is_qualified=False,
                        exclusion=HeatmapExclusionReason.INVALID_DENOMINATOR,
                    )
                )
                continue

            # Return calculation using Decimal precision
            abs_change = c.current_price - c.reference_price
            pct_change = (abs_change / c.reference_price) * Decimal("100")
            pct_change = pct_change.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

            # Check weighting validity if mode is MARKET_CAP_WEIGHTED
            if mode == HeatmapVisualizationMode.MARKET_CAP_WEIGHTED:
                if c.weight_value is None:
                    missing_weights += 1
                    exclusion_breakdown[HeatmapExclusionReason.MISSING_WEIGHT.value] += 1
                    leaves.append(
                        self._create_leaf_node(
                            c=c,
                            sector_label=sector_label,
                            is_qualified=False,
                            exclusion=HeatmapExclusionReason.MISSING_WEIGHT,
                            abs_change=abs_change,
                            pct_change=pct_change,
                        )
                    )
                    continue

                if c.weight_value <= Decimal("0"):
                    missing_weights += 1
                    exclusion_breakdown[HeatmapExclusionReason.INVALID_WEIGHT.value] += 1
                    leaves.append(
                        self._create_leaf_node(
                            c=c,
                            sector_label=sector_label,
                            is_qualified=False,
                            exclusion=HeatmapExclusionReason.INVALID_WEIGHT,
                            abs_change=abs_change,
                            pct_change=pct_change,
                        )
                    )
                    continue

            # If all checks pass, leaf is qualified
            leaves.append(
                self._create_leaf_node(
                    c=c,
                    sector_label=sector_label,
                    is_qualified=True,
                    exclusion=None,
                    abs_change=abs_change,
                    pct_change=pct_change,
                    weight_value=c.weight_value,
                    weight_unit=c.weight_unit or universe.weight_unit,
                )
            )

        qualified_leaves = [leaf for leaf in leaves if leaf.is_qualified]
        qualified_count = len(qualified_leaves)

        # Step 2: Calculate Normalized Weights
        total_qualified_weight: Optional[Decimal] = None
        normalized_leaves: List[HeatmapLeafNode] = []

        if mode == HeatmapVisualizationMode.MARKET_CAP_WEIGHTED:
            weights = [
                item.weight_value for item in qualified_leaves if item.weight_value is not None
            ]
            total_qualified_weight = sum(weights) if weights else Decimal("0")

            for leaf in leaves:
                if (
                    leaf.is_qualified
                    and leaf.weight_value is not None
                    and total_qualified_weight > Decimal("0")
                ):
                    norm = (leaf.weight_value / total_qualified_weight).quantize(
                        Decimal("0.000001"), rounding=ROUND_HALF_UP
                    )
                    normalized_leaves.append(leaf.model_copy(update={"normalized_weight": norm}))
                else:
                    normalized_leaves.append(leaf)

        elif mode == HeatmapVisualizationMode.EQUAL_SIZE:
            equal_fraction = (
                (Decimal("1.0") / Decimal(qualified_count)).quantize(
                    Decimal("0.000001"), rounding=ROUND_HALF_UP
                )
                if qualified_count > 0
                else None
            )
            for leaf in leaves:
                if leaf.is_qualified and equal_fraction is not None:
                    normalized_leaves.append(
                        leaf.model_copy(update={"normalized_weight": equal_fraction})
                    )
                else:
                    normalized_leaves.append(leaf)

        # Apply max_nodes truncation if requested (preserves coverage transparency)
        rendered_leaves = normalized_leaves
        if max_nodes and max_nodes > 0 and len(rendered_leaves) > max_nodes:
            # Sort qualified items first by weight or symbol deterministically
            rendered_leaves = sorted(
                rendered_leaves,
                key=lambda x: (not x.is_qualified, -(x.weight_value or Decimal("0")), x.symbol),
            )[:max_nodes]

        # Step 3: Hierarchy Grouping
        groups: List[HeatmapGroupNode] = []
        if hierarchy in (HeatmapHierarchyMode.SECTOR, HeatmapHierarchyMode.INDUSTRY):
            groups = self._build_sector_groups(
                leaves=rendered_leaves,
                mode=mode,
                taxonomy=universe.taxonomy or "GICS",
                total_universe_weight=total_qualified_weight,
            )

        # Step 4: Coverage classification
        if qualified_count == universe_size and universe_size > 0:
            coverage_status = HeatmapCoverageStatus.COMPLETE_FOR_DEFINED_UNIVERSE
        elif qualified_count > 0:
            coverage_status = HeatmapCoverageStatus.PARTIAL_COVERAGE
        else:
            coverage_status = HeatmapCoverageStatus.UNAVAILABLE

        coverage = HeatmapCoverage(
            universe_size=universe_size,
            candidate_count=candidate_count,
            qualified_count=qualified_count,
            missing_returns=missing_returns,
            missing_weights=missing_weights,
            unclassified_count=unclassified_count,
            coverage_status=coverage_status,
            total_qualified_weight=total_qualified_weight,
            exclusion_breakdown=dict(exclusion_breakdown),
        )

        return MarketHeatmapResponse(
            schema_version="1.0.0",
            snapshot_id=snapshot_id,
            universe_id=universe.universe_id,
            universe_name=universe.display_name,
            asset_class=universe.asset_class,
            comparison_window=window,
            visualization_mode=mode,
            hierarchy_mode=hierarchy,
            calculated_at=now,
            weight_metric_label=universe.weight_metric_label,
            weight_unit=universe.weight_unit,
            color_domain_min=Decimal("-5.0"),
            color_domain_max=Decimal("5.0"),
            coverage=coverage,
            nodes=rendered_leaves if hierarchy == HeatmapHierarchyMode.NONE else [],
            groups=groups
            if hierarchy in (HeatmapHierarchyMode.SECTOR, HeatmapHierarchyMode.INDUSTRY)
            else [],
            notes="ATLAS Institutional Market Heatmap V1 calculation snapshot.",
        )

    def _create_leaf_node(
        self,
        c: HeatmapCandidateObservation,
        sector_label: str,
        is_qualified: bool,
        exclusion: Optional[HeatmapExclusionReason],
        abs_change: Optional[Decimal] = None,
        pct_change: Optional[Decimal] = None,
        weight_value: Optional[Decimal] = None,
        weight_unit: Optional[str] = None,
    ) -> HeatmapLeafNode:
        """Helper to create an immutable HeatmapLeafNode."""
        return HeatmapLeafNode(
            node_id=f"leaf:{c.exchange_or_venue.lower()}:{c.symbol.lower()}",
            node_kind="instrument",
            instrument_entity_id=c.instrument_entity_id,
            market_series_identity=c.market_series_identity,
            symbol=c.symbol,
            display_name=c.display_name,
            asset_class=c.asset_class,
            exchange_or_venue=c.exchange_or_venue,
            sector=sector_label,
            industry=c.industry,
            current_price=c.current_price,
            reference_price=c.reference_price,
            percent_change=pct_change,
            absolute_change=abs_change,
            weight_value=weight_value,
            weight_unit=weight_unit,
            normalized_weight=None,
            currency=c.listing_currency,
            freshness_status=c.freshness_status,
            delay_status=c.delay_status,
            delivery_delay_seconds=c.delivery_delay_seconds,
            provider=c.provider,
            source_timestamp=c.source_timestamp,
            reference_timestamp=c.reference_timestamp,
            reference_period_label=c.reference_period_label,
            is_qualified=is_qualified,
            exclusion_reason=exclusion,
        )

    def _build_sector_groups(
        self,
        leaves: List[HeatmapLeafNode],
        mode: HeatmapVisualizationMode,
        taxonomy: str,
        total_universe_weight: Optional[Decimal],
    ) -> List[HeatmapGroupNode]:
        """
        Builds sector group nodes from constituent leaves.
        Calculates aggregate returns (equal-weight or cap-weighted) and group area weights.
        """
        sector_map: Dict[str, List[HeatmapLeafNode]] = defaultdict(list)
        for leaf in leaves:
            sector_name = leaf.sector or "Unclassified"
            sector_map[sector_name].append(leaf)

        groups: List[HeatmapGroupNode] = []

        for sector_name, items in sector_map.items():
            constituent_count = len(items)
            qualified_items = [
                item for item in items if item.is_qualified and item.percent_change is not None
            ]
            qualified_count = len(qualified_items)

            aggregate_return: Optional[Decimal] = None
            aggregate_method = "equal_weight_mean"

            group_weight: Optional[Decimal] = None
            group_normalized_weight: Optional[Decimal] = None

            if mode == HeatmapVisualizationMode.MARKET_CAP_WEIGHTED:
                # Calculate cap-weighted aggregate return: sum(w_i * r_i) / sum(w_i)
                qualified_weights = [
                    item.weight_value for item in qualified_items if item.weight_value is not None
                ]
                sum_weight = sum(qualified_weights) if qualified_weights else Decimal("0")
                group_weight = sum_weight

                if sum_weight > Decimal("0"):
                    weighted_sum = sum(
                        item.weight_value * item.percent_change  # type: ignore
                        for item in qualified_items
                        if item.weight_value is not None and item.percent_change is not None
                    )
                    aggregate_return = (weighted_sum / sum_weight).quantize(
                        Decimal("0.0001"), rounding=ROUND_HALF_UP
                    )
                    aggregate_method = "cap_weighted_return"

                if (
                    total_universe_weight
                    and total_universe_weight > Decimal("0")
                    and group_weight is not None
                ):
                    group_normalized_weight = (group_weight / total_universe_weight).quantize(
                        Decimal("0.000001"), rounding=ROUND_HALF_UP
                    )

            else:
                # EQUAL_SIZE mode: equal-weight mean return: sum(r_i) / N
                if qualified_count > 0:
                    sum_return = sum(
                        item.percent_change
                        for item in qualified_items
                        if item.percent_change is not None
                    )  # type: ignore
                    aggregate_return = (sum_return / Decimal(qualified_count)).quantize(
                        Decimal("0.0001"), rounding=ROUND_HALF_UP
                    )
                    aggregate_method = "equal_weight_mean"

                # In equal-size mode, group area reflects proportion of qualified constituent count
                total_qualified_all = sum(1 for leaf in leaves if leaf.is_qualified)
                if total_qualified_all > 0:
                    group_normalized_weight = (
                        Decimal(qualified_count) / Decimal(total_qualified_all)
                    ).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)

            # Sort children deterministically by weight (or symbol)
            sorted_children = sorted(
                items,
                key=lambda x: (not x.is_qualified, -(x.weight_value or Decimal("0")), x.symbol),
            )

            groups.append(
                HeatmapGroupNode(
                    group_id=f"sector:{sector_name.lower().replace(' ', '_')}",
                    group_kind="sector",
                    label=sector_name,
                    taxonomy=taxonomy,
                    constituent_count=constituent_count,
                    qualified_count=qualified_count,
                    aggregate_return=aggregate_return,
                    aggregate_method=aggregate_method,
                    total_weight=group_weight,
                    normalized_weight=group_normalized_weight,
                    children=sorted_children,
                )
            )

        # Sort groups deterministically: highest weight first, with "Unclassified" at the end
        def group_sort_key(g: HeatmapGroupNode):
            is_unclassified = g.label.lower() == "unclassified"
            weight_val = -(g.total_weight or Decimal("0")) if g.total_weight else Decimal("0")
            count_val = -g.qualified_count
            return (is_unclassified, weight_val, count_val, g.label)

        groups.sort(key=group_sort_key)
        return groups
