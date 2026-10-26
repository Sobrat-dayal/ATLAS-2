"""Quantitative Factor Ranking Engine (Stage 97).

Provides transparent cross-sectional factor ranking, percentile computation,
sample Z-score normalization, composite weighted scoring, and strict missing-data policies.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from atlas.screeners.enums import (
    RankingDirection,
    RankingMethod,
    RankingMode,
    RankingTransformation,
)
from atlas.screeners.errors import (
    ScreenerRankingFactorInvalidError,
    ScreenerRankingInsufficientSampleError,
    ScreenerRankingWeightInvalidError,
)
from atlas.screeners.schemas import (
    ScreenerRankingResponseDTO,
    ScreenerRankingResultRowDTO,
    ScreenerRankingSpecDTO,
)


class FactorRankingEngine:
    """Institutional quantitative factor ranking and normalization engine."""

    METHODOLOGY_VERSION = "1.0.0"

    @classmethod
    def evaluate(
        cls,
        candidates: List[Dict[str, Any]],
        ranking_spec: ScreenerRankingSpecDTO,
        metric_extractor: Callable[[Dict[str, Any], str], Optional[float]],
    ) -> ScreenerRankingResponseDTO:
        """
        Evaluates factor ranking over eligible candidates.

        Args:
            candidates: List of candidate security records.
            ranking_spec: User-configured ranking specification.
            metric_extractor: Function mapping (candidate, factor_id) -> Optional[float].
        """
        if not ranking_spec.factors:
            raise ScreenerRankingFactorInvalidError(
                factor_id="none",
                message="At least one factor must be specified for ranking.",
            )

        total_candidate_count = len(candidates)
        if total_candidate_count < 2:
            raise ScreenerRankingInsufficientSampleError(
                eligible_count=total_candidate_count,
                min_required=2,
            )

        # 1. Validate weights for composite mode
        active_factors = ranking_spec.factors
        if ranking_spec.mode == RankingMode.MULTI_FACTOR_COMPOSITE:
            cls._validate_and_normalize_weights(active_factors)

        # 2. Extract values and filter eligible sample (Complete-Case Policy)
        eligible_items: List[Tuple[Dict[str, Any], Dict[str, float]]] = []
        excluded_count = 0

        for cand in candidates:
            cand_values: Dict[str, float] = {}
            has_all_factors = True

            for fw in active_factors:
                val = metric_extractor(cand, fw.factor_id)
                if val is None or not math.isfinite(val):
                    has_all_factors = False
                    break
                cand_values[fw.factor_id] = float(val)

            if has_all_factors:
                eligible_items.append((cand, cand_values))
            else:
                excluded_count += 1

        eligible_count = len(eligible_items)
        if eligible_count < 2:
            raise ScreenerRankingInsufficientSampleError(
                eligible_count=eligible_count,
                min_required=2,
            )

        # 3. Compute factor-level statistics & transformations
        # Map: factor_id -> {instrument_id -> normalized_score}
        factor_scores: Dict[str, Dict[UUID, float]] = {}
        factor_percentiles: Dict[str, Dict[UUID, float]] = {}
        factor_z_scores: Dict[str, Dict[UUID, float]] = {}
        factor_raw_ranks: Dict[str, Dict[UUID, int]] = {}

        for fw in active_factors:
            fid = fw.factor_id
            direction = fw.direction
            transformation = fw.transformation

            # Extract list of (instrument_id, raw_value)
            pairs: List[Tuple[UUID, float]] = [
                (item[0]["instrument_entity_id"], item[1][fid])
                for item in eligible_items
            ]

            # Compute ranks for this factor
            ranks, pcts, zs = cls._compute_single_factor_stats(
                pairs=pairs,
                direction=direction,
                method=ranking_spec.method,
            )

            factor_raw_ranks[fid] = ranks
            factor_percentiles[fid] = pcts
            factor_z_scores[fid] = zs

            if transformation == RankingTransformation.Z_SCORE:
                factor_scores[fid] = zs
            elif transformation == RankingTransformation.PERCENTILE:
                factor_scores[fid] = pcts
            else:  # RAW_RANK (negated so higher is better for composite)
                max_rank = eligible_count
                factor_scores[fid] = {
                    iid: float(max_rank - r + 1) for iid, r in ranks.items()
                }

        # 4. Compute composite scores and final ranks
        # In single factor mode, primary score is factor_scores of the single factor
        primary_factor_id = active_factors[0].factor_id
        final_scores: List[Tuple[UUID, Dict[str, Any], float, Dict[str, float]]] = []

        if ranking_spec.mode == RankingMode.SINGLE_FACTOR:
            final_ranks = factor_raw_ranks[primary_factor_id]
            final_percentiles = factor_percentiles[primary_factor_id]
            for item in eligible_items:
                cand = item[0]
                iid = cand["instrument_entity_id"]
                score = factor_scores[primary_factor_id][iid]
                contributions = {primary_factor_id: score}
                final_scores.append((iid, cand, score, contributions))
        else:
            # Composite weighted sum: S_i = sum(w_j * score_ij)
            weights = {fw.factor_id: fw.weight for fw in active_factors}
            sum_weights = sum(weights.values()) or 1.0
            norm_weights = {fid: w / sum_weights for fid, w in weights.items()}

            for item in eligible_items:
                cand = item[0]
                iid = cand["instrument_entity_id"]
                composite_score = 0.0
                contributions: Dict[str, float] = {}

                for fw in active_factors:
                    fid = fw.factor_id
                    w = norm_weights[fid]
                    s = factor_scores[fid][iid]
                    contrib = w * s
                    composite_score += contrib
                    contributions[fid] = round(contrib, 6)

                final_scores.append((iid, cand, composite_score, contributions))

            # 5. Assign Final Overall Rank based on composite score descending (highest score = Rank 1)
            # Stable tie-breaker: instrument_entity_id string
            final_scores.sort(
                key=lambda x: (-x[2], str(x[0]))
            )

            final_ranks = cls._assign_ranks(
                ordered_items=[(x[0], x[2]) for x in final_scores],
                method=ranking_spec.method,
            )

            # Compute final overall percentiles
            final_percentiles = cls._ranks_to_percentiles(final_ranks, eligible_count)

        # 6. Build Result Rows
        results: List[ScreenerRankingResultRowDTO] = []
        for iid, cand, score, contribs in final_scores:
            rank = final_ranks[iid]
            pct = final_percentiles[iid]
            z_sc = factor_z_scores[primary_factor_id].get(iid) if ranking_spec.mode == RankingMode.SINGLE_FACTOR else None

            # Collect raw values for inspection
            raw_vals = {
                fw.factor_id: cand_values_map[fw.factor_id]
                for item in eligible_items
                if item[0]["instrument_entity_id"] == iid
                for cand_values_map in [item[1]]
            }

            results.append(
                ScreenerRankingResultRowDTO(
                    instrument_entity_id=iid,
                    ticker=cand.get("ticker", ""),
                    canonical_security_name=cand.get("canonical_security_name", ""),
                    rank=rank,
                    percentile=round(pct, 2),
                    z_score=round(z_sc, 4) if z_sc is not None else None,
                    composite_score=round(score, 4) if ranking_spec.mode == RankingMode.MULTI_FACTOR_COMPOSITE else None,
                    factor_contributions=contribs,
                    raw_factor_values=raw_vals,
                )
            )

        # Sort results by final rank ascending, then ticker
        results.sort(key=lambda r: (r.rank, r.ticker))

        return ScreenerRankingResponseDTO(
            ranking_evaluation_id=uuid4(),
            mode=ranking_spec.mode,
            method=ranking_spec.method,
            cohort_policy=ranking_spec.cohort_policy,
            methodology_version=cls.METHODOLOGY_VERSION,
            total_candidate_count=total_candidate_count,
            eligible_count=eligible_count,
            excluded_count=excluded_count,
            evaluated_as_of=datetime.now(timezone.utc),
            results=results,
        )

    @classmethod
    def _validate_and_normalize_weights(cls, factors: List[Any]) -> None:
        """Ensures weights are positive, finite, and normalizeable."""
        if not factors:
            raise ScreenerRankingWeightInvalidError("No factors provided for composite weighting.")

        total_weight = 0.0
        for f in factors:
            w = getattr(f, "weight", None)
            if w is None or not math.isfinite(w) or w <= 0.0:
                raise ScreenerRankingWeightInvalidError(
                    f"Factor weight for '{f.factor_id}' must be a strictly positive finite number; got {w}."
                )
            total_weight += w

        if total_weight <= 0.0:
            raise ScreenerRankingWeightInvalidError("Sum of factor weights must be strictly positive.")

    @classmethod
    def _compute_single_factor_stats(
        cls,
        pairs: List[Tuple[UUID, float]],
        direction: RankingDirection,
        method: RankingMethod,
    ) -> Tuple[Dict[UUID, int], Dict[UUID, float], Dict[UUID, float]]:
        """
        Computes ranks, percentiles (0-100), and Z-scores for a single factor.
        """
        n = len(pairs)
        # Direction: HIGHER_VALUE_FIRST sorts by value descending
        # LOWER_VALUE_FIRST sorts by value ascending (e.g. lowest P/E is rank 1)
        if direction == RankingDirection.HIGHER_VALUE_FIRST:
            sorted_pairs = sorted(pairs, key=lambda x: (-x[1], str(x[0])))
        else:
            sorted_pairs = sorted(pairs, key=lambda x: (x[1], str(x[0])))

        # Assign ranks
        ranks = cls._assign_ranks(sorted_pairs, method)

        # Compute percentiles
        percentiles = cls._ranks_to_percentiles(ranks, n)

        # Compute sample Z-Scores: (x - mean) / std_dev
        values = [p[1] for p in pairs]
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
        std_dev = math.sqrt(variance)

        z_scores: Dict[UUID, float] = {}
        for iid, val in pairs:
            if std_dev == 0.0:
                z = 0.0
            else:
                z = (val - mean) / std_dev
                # If LOWER_VALUE_FIRST, invert Z so lower value maps to positive Z score
                if direction == RankingDirection.LOWER_VALUE_FIRST:
                    z = -z
            z_scores[iid] = round(z, 6)

        return ranks, percentiles, z_scores

    @classmethod
    def _assign_ranks(
        cls,
        ordered_items: List[Tuple[UUID, float]],
        method: RankingMethod,
    ) -> Dict[UUID, int]:
        """
        Assigns ranks based on DENSE_RANK or COMPETITION_RANK (1224).
        Expects items already ordered from best to worst.
        """
        ranks: Dict[UUID, int] = {}
        if not ordered_items:
            return ranks

        current_rank = 1
        previous_val: Optional[float] = None
        dense_rank = 1

        for idx, (iid, val) in enumerate(ordered_items):
            if idx == 0:
                ranks[iid] = 1
                previous_val = val
                continue

            is_tie = math.isclose(val, previous_val, rel_tol=1e-9, abs_tol=1e-9) if previous_val is not None else False
            if is_tie:
                if method == RankingMethod.DENSE_RANK:
                    ranks[iid] = dense_rank
                else:  # COMPETITION_RANK
                    ranks[iid] = current_rank
            else:
                dense_rank += 1
                current_rank = idx + 1
                ranks[iid] = dense_rank if method == RankingMethod.DENSE_RANK else current_rank
                previous_val = val

        return ranks

    @classmethod
    def _ranks_to_percentiles(cls, ranks: Dict[UUID, int], n: int) -> Dict[UUID, float]:
        """
        Converts ordinal ranks (1 is best) into percentile scores from 0.0% to 100.0%.
        Rank 1 receives 100.0%, Rank N receives 0.0% (for N > 1).
        """
        percentiles: Dict[UUID, float] = {}
        if n <= 1:
            return {iid: 100.0 for iid in ranks}

        for iid, r in ranks.items():
            pct = ((n - r) / (n - 1)) * 100.0
            percentiles[iid] = max(0.0, min(100.0, pct))
        return percentiles
