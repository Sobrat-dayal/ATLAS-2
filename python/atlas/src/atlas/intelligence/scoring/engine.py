"""Core Calculation and Ranking Engine for Intelligence Scoring (Stage 139)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .domain import (
    AtlasIntelligenceScore,
    FactorContribution,
    FactorTransformationMethod,
    RankedItem,
    ScoreLineageRecord,
    ScoreObjectiveId,
    ScoreScale,
    ScoreStatus,
    ScoreUncertaintyMetadata,
)
from .errors import ScoringQuotaExceededError
from .factors import compute_factor_contribution
from .features import CANONICAL_FEATURES, FeatureExtractor
from .models import ModelRegistry
from .objectives import ScoringObjectiveRegistry
from .policies import ScoringPolicyRegistry


class ScoringEngine:
    """Executes deterministic rule-based scoring and exact factor explanations."""

    @classmethod
    def calculate_score(
        cls,
        event_data: Dict[str, Any],
        objective_id: ScoreObjectiveId,
        policy_id: Optional[str] = None,
        model_version: Optional[str] = None,
        known_as_of: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> AtlasIntelligenceScore:
        known_as_of = known_as_of or datetime.now(timezone.utc).isoformat()
        computed_at = datetime.now(timezone.utc).isoformat()
        event_id = event_data.get("event_id", "unknown_event")

        # 1. Verification of Objective
        obj_def = ScoringObjectiveRegistry.get_objective(objective_id.value)

        # 2. Model & Policy Resolution
        # Select matching model
        model_id_map = {
            ScoreObjectiveId.EVENT_REVIEW_PRIORITY: "MOD_EVENT_PRIORITY",
            ScoreObjectiveId.EVENT_ENTITY_RELEVANCE: "MOD_ENTITY_RELEVANCE",
            ScoreObjectiveId.PORTFOLIO_EVENT_ATTENTION: "MOD_PORTFOLIO_ATTENTION",
            ScoreObjectiveId.GEOGRAPHIC_EVENT_RELEVANCE: "MOD_GEOGRAPHIC_RELEVANCE",
            ScoreObjectiveId.SOURCE_EVIDENCE_ASSESSMENT: "MOD_SOURCE_EVIDENCE",
            ScoreObjectiveId.ECONOMIC_EVENT_RELEVANCE: "MOD_EVENT_PRIORITY",
        }
        model_id = model_id_map.get(objective_id, "MOD_EVENT_PRIORITY")
        model_def = ModelRegistry.get_model(model_id, version=model_version)
        selected_version = model_version or model_def.active_version

        chosen_policy_id = policy_id or model_def.default_policy_id
        policy = ScoringPolicyRegistry.get_policy(chosen_policy_id)

        # 3. Check for Retracted Events (Fixture O)
        if event_data.get("status") == "RETRACTED" or event_data.get("verification_status") == "RETRACTED":
            return AtlasIntelligenceScore(
                score_id=f"score_retracted_{event_id}_{int(datetime.now(timezone.utc).timestamp())}",
                score_type=objective_id.value,
                scoring_objective=objective_id,
                subject_reference={"event_id": event_id, "status": "RETRACTED"},
                context_reference=context,
                event_id=event_id,
                model_id=model_id,
                model_version=selected_version,
                score_value=None,
                score_scale=ScoreScale.BOUNDED_INDEX_0_100,
                score_interpretation="Event has been officially retracted by issuing source. Prior scores invalidated.",
                score_status=ScoreStatus.NOT_APPLICABLE,
                factor_contributions=[],
                uncertainty=ScoreUncertaintyMetadata(
                    coverage_ratio=0.0,
                    available_feature_count=0,
                    required_feature_count=len(policy.factor_configs),
                    missing_features=[],
                    has_source_conflicts=False,
                    conflict_notes=["Official source retraction issued."],
                    limitations=["Retracted event not eligible for prioritization."],
                ),
                lineage=ScoreLineageRecord(
                    feature_snapshot_id="snapshot_retracted",
                    model_id=model_id,
                    model_version=selected_version,
                    policy_id=policy.policy_id,
                    source_ids=[s.get("source_id", "src") for s in event_data.get("sources", [])],
                ),
                valid_at=event_data.get("valid_at") or event_data.get("occurrence_time") or known_as_of,
                known_as_of=known_as_of,
                computed_at=computed_at,
                tenant_scope=tenant_id,
            )

        # 4. Point-in-Time Feature Extraction (Guards against look-ahead bias)
        snapshot = FeatureExtractor.extract_event_features(
            event_data=event_data,
            known_as_of=known_as_of,
            context=context,
        )

        # 5. Factor Computations
        contributions: List[FactorContribution] = []
        raw_weighted_sum = 0.0
        total_weight_sum = sum(cfg.weight for cfg in policy.factor_configs)
        available_weight_sum = 0.0
        missing_feats = []

        for cfg in policy.factor_configs:
            feat_id = cfg.factor_id
            feat_def = CANONICAL_FEATURES.get(feat_id)
            feat_name = feat_def.display_name if feat_def else feat_id
            is_miss = feat_id in snapshot.missing_features or feat_id not in snapshot.feature_values

            if is_miss:
                missing_feats.append(feat_id)
                contrib = compute_factor_contribution(
                    factor_id=feat_id,
                    factor_name=feat_name,
                    raw_value=None,
                    transformation_method=feat_def.default_transformation if feat_def else FactorTransformationMethod.BINARY_ELIGIBILITY,
                    weight=cfg.weight,
                    is_missing=True,
                )
            else:
                raw_val = snapshot.feature_values[feat_id]
                contrib = compute_factor_contribution(
                    factor_id=feat_id,
                    factor_name=feat_name,
                    raw_value=raw_val,
                    transformation_method=feat_def.default_transformation if feat_def else FactorTransformationMethod.BINARY_ELIGIBILITY,
                    weight=cfg.weight,
                    is_missing=False,
                    half_life_hours=cfg.half_life_hours or 72.0,
                    max_bound=cfg.max_bound or 100.0,
                )
                available_weight_sum += cfg.weight
                raw_weighted_sum += contrib.transformed_value * cfg.weight

            contributions.append(contrib)

        # 6. Coverage & Score Calculation
        coverage_ratio = available_weight_sum / total_weight_sum if total_weight_sum > 0 else 0.0

        if coverage_ratio < policy.min_coverage_threshold:
            score_status = ScoreStatus.INSUFFICIENT_DATA
            final_value = None
            interpretation = f"Insufficient data: feature coverage {coverage_ratio*100:.1f}% below minimum threshold {policy.min_coverage_threshold*100:.1f}%."
        elif coverage_ratio < 1.0:
            score_status = ScoreStatus.PARTIAL
            final_value = round((raw_weighted_sum / available_weight_sum) * 100.0, 2)
            interpretation = cls._get_interpretation(final_value)
        else:
            score_status = ScoreStatus.AVAILABLE
            final_value = round((raw_weighted_sum / total_weight_sum) * 100.0, 2)
            interpretation = cls._get_interpretation(final_value)

        # 7. Normalize contribution points to exact final sum
        if final_value is not None and available_weight_sum > 0:
            for c in contributions:
                if not c.is_missing:
                    c.contribution_points = round((c.transformed_value * c.weight / available_weight_sum) * 100.0, 2)

        has_conflicts = bool(snapshot.feature_values.get("FEAT_SOURCE_CONFLICT_FLAG", False))

        return AtlasIntelligenceScore(
            score_id=f"score_{event_id}_{int(datetime.now(timezone.utc).timestamp())}",
            score_type=objective_id.value,
            scoring_objective=objective_id,
            subject_reference={"event_id": event_id, "title": event_data.get("title", "")},
            context_reference=context,
            event_id=event_id,
            entity_id=(context or {}).get("selected_entity_id"),
            portfolio_id=((context or {}).get("portfolio_context") or {}).get("portfolio_id"),
            model_id=model_id,
            model_version=selected_version,
            score_value=final_value,
            score_scale=ScoreScale.BOUNDED_INDEX_0_100,
            score_interpretation=interpretation,
            score_status=score_status,
            factor_contributions=contributions,
            uncertainty=ScoreUncertaintyMetadata(
                coverage_ratio=coverage_ratio,
                available_feature_count=len(policy.factor_configs) - len(missing_feats),
                required_feature_count=len(policy.factor_configs),
                missing_features=missing_feats,
                has_source_conflicts=has_conflicts,
                conflict_notes=["Conflicting source claims detected in reporting."] if has_conflicts else [],
                limitations=[
                    "Operational review priority only.",
                    "Does not measure market price direction, volatility, or probability of loss.",
                ],
                is_calibration_applicable=False,
            ),
            lineage=ScoreLineageRecord(
                feature_snapshot_id=snapshot.snapshot_id,
                model_id=model_id,
                model_version=selected_version,
                policy_id=policy.policy_id,
                event_revision=event_data.get("revision", 1),
                graph_revision=event_data.get("graph_revision", 1),
                exposure_run_id=(context or {}).get("exposure_run_id"),
                source_ids=[s.get("source_id", "src") for s in event_data.get("sources", [])],
            ),
            valid_at=event_data.get("valid_at") or event_data.get("occurrence_time") or known_as_of,
            known_as_of=known_as_of,
            computed_at=computed_at,
            tenant_scope=tenant_id,
        )

    @staticmethod
    def _get_interpretation(score_val: float) -> str:
        if score_val >= 80.0:
            return "URGENT_REVIEW_RECOMMENDED: Event shows high direct entity relevance and strong evidence corroboration."
        if score_val >= 60.0:
            return "ELEVATED_REVIEW_PRIORITY: Event exhibits material connection to monitored subjects."
        if score_val >= 35.0:
            return "STANDARD_INVESTIGATION: Relevant background event within active research scope."
        return "ROUTINE_MONITORING: Peripheral observation with low immediate operational priority."


class RankingEngine:
    """Ranks collections of events with deterministic secondary tie-breaking (Fixture Q)."""

    @classmethod
    def rank_events(
        cls,
        candidate_events: List[Dict[str, Any]],
        objective_id: ScoreObjectiveId,
        policy_id: Optional[str] = None,
        model_version: Optional[str] = None,
        known_as_of: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[RankedItem]:
        # Enforce quota protection (Fixture P)
        if len(candidate_events) > 500:
            raise ScoringQuotaExceededError(requested=len(candidate_events), limit=500)

        known_as_of = known_as_of or datetime.now(timezone.utc).isoformat()
        now_asof = datetime.fromisoformat(known_as_of.replace("Z", "+00:00"))

        # Point-in-time filter: omit events published after known_as_of
        eligible_candidates = []
        for ev in candidate_events:
            pub_str = ev.get("published_at") or ev.get("occurrence_time") or known_as_of
            pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            if pub_dt <= now_asof:
                eligible_candidates.append(ev)

        # Score all eligible events
        scored_items: List[AtlasIntelligenceScore] = []
        for ev in eligible_candidates:
            score = ScoringEngine.calculate_score(
                event_data=ev,
                objective_id=objective_id,
                policy_id=policy_id,
                model_version=model_version,
                known_as_of=known_as_of,
                context=context,
                tenant_id=tenant_id,
            )
            scored_items.append(score)

        # Deterministic sorting:
        # Primary: Score value descending (None -> -1.0)
        # Secondary: valid_at descending
        # Tertiary: event_id ascending (ensures strict deterministic tie-breaking)
        def sort_key(item: AtlasIntelligenceScore):
            s_val = item.score_value if item.score_value is not None else -1.0
            return (-s_val, item.valid_at, item.event_id or "")

        # To properly sort:
        # Descending score: -s_val
        # Descending time: we invert or compare
        # In Python tuples, we can sort with a custom comparator or tuple
        scored_items.sort(
            key=lambda x: (
                -(x.score_value if x.score_value is not None else -1.0),
                -(datetime.fromisoformat(x.valid_at.replace("Z", "+00:00")).timestamp()),
                x.event_id or "",
            )
        )

        ranked: List[RankedItem] = []
        for i, item in enumerate(scored_items[:limit], start=1):
            tie_key = f"{item.score_value}_{item.valid_at}_{item.event_id}"
            ranked.append(RankedItem(rank=i, score=item, tie_breaker_key=tie_key))

        return ranked

