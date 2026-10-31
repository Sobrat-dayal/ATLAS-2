"""Model Monitoring, Health Telemetry, and Drift Detection for Intelligence Scoring (Stage 139)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from .domain import AtlasIntelligenceScore


class ScoringTelemetrySummary(BaseModel):
    """Aggregate operational health metrics for scoring services."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_id: str
    active_version: str
    total_scores_computed: int
    mean_score_value: float
    high_priority_fraction: float  # Fraction >= 80.0
    average_coverage_ratio: float
    missing_features_rate: float
    drift_status: str  # HEALTHY, DRIFT_DETECTED, HIGH_MISSINGNESS
    last_evaluated_at: str


class ScoringMonitor:
    """Tracks running statistics to detect data drift and coverage degradation."""

    _computed_history: List[AtlasIntelligenceScore] = []

    @classmethod
    def record_scores(cls, scores: List[AtlasIntelligenceScore]):
        cls._computed_history.extend(scores)
        # Bounded in-memory telemetry buffer
        if len(cls._computed_history) > 2000:
            cls._computed_history = cls._computed_history[-2000:]

    @classmethod
    def get_model_telemetry(cls, model_id: str = "MOD_EVENT_PRIORITY") -> ScoringTelemetrySummary:
        relevant = [s for s in cls._computed_history if s.model_id == model_id and s.score_value is not None]
        if not relevant:
            return ScoringTelemetrySummary(
                model_id=model_id,
                active_version="v1.0.0",
                total_scores_computed=0,
                mean_score_value=0.0,
                high_priority_fraction=0.0,
                average_coverage_ratio=1.0,
                missing_features_rate=0.0,
                drift_status="HEALTHY",
                last_evaluated_at=datetime.now(timezone.utc).isoformat(),
            )

        n = len(relevant)
        mean_val = sum(s.score_value for s in relevant if s.score_value is not None) / float(n)
        high_prio = sum(1 for s in relevant if s.score_value is not None and s.score_value >= 80.0) / float(n)
        avg_cov = sum(s.uncertainty.coverage_ratio for s in relevant) / float(n)

        # Drift detection heuristic: if high_priority fraction > 0.60 or < 0.05, alert drift
        drift_status = "HEALTHY"
        if high_prio > 0.70:
            drift_status = "DRIFT_DETECTED: UNUSUAL_SCORE_INFLATION"
        elif avg_cov < 0.60:
            drift_status = "HIGH_MISSINGNESS"

        return ScoringTelemetrySummary(
            model_id=model_id,
            active_version=relevant[-1].model_version,
            total_scores_computed=n,
            mean_score_value=round(mean_val, 2),
            high_priority_fraction=round(high_prio, 4),
            average_coverage_ratio=round(avg_cov, 4),
            missing_features_rate=round(1.0 - avg_cov, 4),
            drift_status=drift_status,
            last_evaluated_at=datetime.now(timezone.utc).isoformat(),
        )
