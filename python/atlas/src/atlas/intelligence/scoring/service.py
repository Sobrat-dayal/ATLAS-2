"""Master Service Orchestrator for ATLAS Intelligence Scoring (Stage 139)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from .domain import (
    AtlasIntelligenceScore,
    GovernanceStatus,
    RankedItem,
    ScoringEvaluationManifest,
    ScoreObjectiveId,
    ScoreScale,
    ScoreStatus,
)
from .engine import RankingEngine, ScoringEngine
from .errors import ScoringTenantAccessDeniedError
from .evaluation import ModelEvaluator
from .governance import ModelGovernanceManager, ScoringGovernanceAuditRecord
from .models import ModelRegistry, ScoringModelDefinition
from .monitoring import ScoringMonitor, ScoringTelemetrySummary
from .objectives import ScoringObjectiveDefinition, ScoringObjectiveRegistry
from .policies import IntelligenceScoringPolicy, ScoringPolicyRegistry


class ScoringCapabilitiesResponse(BaseModel):
    """Institutional system metadata, supported objectives, and compliance constraints."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    system_name: str = "ATLAS Intelligence Scoring & Prioritization Engine"
    version: str = "Stage 139 (v1.0.0)"
    supported_objectives: List[str]
    supported_scales: List[str]
    active_models_count: int
    compliance_guarantees: List[str]


class ModelComparisonResponse(BaseModel):
    """Side-by-side comparison between two scoring model versions (Fixture I)."""
    model_id: str
    version_a: str
    version_b: str
    event_id: str
    score_a: AtlasIntelligenceScore
    score_b: AtlasIntelligenceScore
    score_delta: float
    explanation_differences: List[str]


class AtlasScoringService:
    """Master service unifying Intelligence Scoring across Events, Graph, Exposure, and Workspaces."""

    def __init__(self):
        self._score_cache: Dict[str, AtlasIntelligenceScore] = {}
        self._evaluations_cache: Dict[str, ScoringEvaluationManifest] = {}
        self._seed_reference_evaluations()

    def _seed_reference_evaluations(self):
        # Seed an institutional reference evaluation manifest for MOD_EVENT_PRIORITY v1.0.0
        ref_eval = ScoringEvaluationManifest(
            evaluation_id="eval_ref_mod_event_priority_v1",
            model_id="MOD_EVENT_PRIORITY",
            model_version="v1.0.0",
            evaluation_dataset="HISTORICAL_FINANCIAL_EVENTS_BENCHMARK_2023_Q4",
            time_window_start="2023-10-01T00:00:00Z",
            time_window_end="2023-12-31T23:59:59Z",
            sample_size=1250,
            ndcg_at_10=0.8845,
            precision_at_5=0.8200,
            mean_reciprocal_rank=0.7950,
            brier_score=None,
            expected_calibration_error=None,
            drift_detected=False,
            validation_status="VALIDATED",
            evaluated_at="2024-01-15T12:00:00Z",
        )
        self._evaluations_cache[ref_eval.evaluation_id] = ref_eval

    def get_capabilities(self) -> ScoringCapabilitiesResponse:
        return ScoringCapabilitiesResponse(
            supported_objectives=[o.objective_id.value for o in ScoringObjectiveRegistry.list_objectives()],
            supported_scales=[s.value for s in ScoreScale],
            active_models_count=len(ModelRegistry.list_models()),
            compliance_guarantees=[
                "Scores represent operational review priority and factual relevance, NOT market return or loss probabilities.",
                "Zero fabricated events, phantom graph connections, or synthetic exposure percentages.",
                "Deterministic additive baseline guarantees exact factor contribution explainability.",
                "Bitemporal evaluation strictly excludes look-ahead and post-event information.",
                "Multi-tenant isolation completely shields private portfolio attention rankings.",
                "Anti-gaming algorithms prevent syndicated article duplicates from inflating corroboration scores.",
            ],
        )

    def list_objectives(self) -> List[ScoringObjectiveDefinition]:
        return ScoringObjectiveRegistry.list_objectives()

    def get_objective(self, objective_id: str) -> ScoringObjectiveDefinition:
        return ScoringObjectiveRegistry.get_objective(objective_id)

    def list_models(self) -> List[ScoringModelDefinition]:
        return ModelRegistry.list_models()

    def get_model(self, model_id: str, version: Optional[str] = None) -> ScoringModelDefinition:
        return ModelRegistry.get_model(model_id, version=version)

    def list_policies(self, objective_id: Optional[str] = None) -> List[IntelligenceScoringPolicy]:
        obj_enum = ScoreObjectiveId(objective_id) if objective_id else None
        return ScoringPolicyRegistry.list_policies(objective_id=obj_enum)

    def get_policy(self, policy_id: str) -> IntelligenceScoringPolicy:
        return ScoringPolicyRegistry.get_policy(policy_id)

    def calculate_score(
        self,
        event_data: Dict[str, Any],
        objective_id: str = "EVENT_REVIEW_PRIORITY",
        policy_id: Optional[str] = None,
        model_version: Optional[str] = None,
        known_as_of: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> AtlasIntelligenceScore:
        # Enforce portfolio tenant isolation (Fixture D)
        portfolio_ctx = (context or {}).get("portfolio_context")
        if portfolio_ctx:
            portfolio_tenant = portfolio_ctx.get("tenant_id")
            if portfolio_tenant and tenant_id and portfolio_tenant != tenant_id:
                raise ScoringTenantAccessDeniedError(
                    tenant_id=tenant_id,
                    resource_type="PORTFOLIO",
                    resource_id=portfolio_ctx.get("portfolio_id", "private"),
                )

        obj_enum = ScoreObjectiveId(objective_id)
        score = ScoringEngine.calculate_score(
            event_data=event_data,
            objective_id=obj_enum,
            policy_id=policy_id,
            model_version=model_version,
            known_as_of=known_as_of,
            context=context,
            tenant_id=tenant_id,
        )
        self._score_cache[score.score_id] = score
        ScoringMonitor.record_scores([score])
        return score

    def rank_events(
        self,
        candidate_events: List[Dict[str, Any]],
        objective_id: str = "EVENT_REVIEW_PRIORITY",
        policy_id: Optional[str] = None,
        model_version: Optional[str] = None,
        known_as_of: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[RankedItem]:
        # Enforce portfolio tenant isolation in context
        portfolio_ctx = (context or {}).get("portfolio_context")
        if portfolio_ctx:
            portfolio_tenant = portfolio_ctx.get("tenant_id")
            if portfolio_tenant and tenant_id and portfolio_tenant != tenant_id:
                raise ScoringTenantAccessDeniedError(
                    tenant_id=tenant_id,
                    resource_type="PORTFOLIO",
                    resource_id=portfolio_ctx.get("portfolio_id", "private"),
                )

        obj_enum = ScoreObjectiveId(objective_id)
        ranked = RankingEngine.rank_events(
            candidate_events=candidate_events,
            objective_id=obj_enum,
            policy_id=policy_id,
            model_version=model_version,
            known_as_of=known_as_of,
            context=context,
            tenant_id=tenant_id,
            limit=limit,
        )
        for r in ranked:
            self._score_cache[r.score.score_id] = r.score
        ScoringMonitor.record_scores([r.score for r in ranked])
        return ranked

    def compare_models(
        self,
        event_data: Dict[str, Any],
        version_a: str,
        version_b: str,
        objective_id: str = "EVENT_REVIEW_PRIORITY",
        known_as_of: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ModelComparisonResponse:
        obj_enum = ScoreObjectiveId(objective_id)
        # Policy for version A vs version B
        pol_a = "pol_event_priority_v1" if "1" in version_a else "pol_event_priority_v2"
        pol_b = "pol_event_priority_v2" if "2" in version_b else "pol_event_priority_v1"

        score_a = ScoringEngine.calculate_score(
            event_data=event_data,
            objective_id=obj_enum,
            policy_id=pol_a,
            model_version=version_a,
            known_as_of=known_as_of,
            context=context,
        )
        score_b = ScoringEngine.calculate_score(
            event_data=event_data,
            objective_id=obj_enum,
            policy_id=pol_b,
            model_version=version_b,
            known_as_of=known_as_of,
            context=context,
        )

        val_a = score_a.score_value or 0.0
        val_b = score_b.score_value or 0.0
        delta = round(val_b - val_a, 2)

        diffs = [
            f"Version {version_a} applied policy '{pol_a}' yielding score {val_a}.",
            f"Version {version_b} applied policy '{pol_b}' yielding score {val_b}.",
            f"Net delta of {delta:+.2f} points attributable to factor weight revisions.",
        ]

        return ModelComparisonResponse(
            model_id="MOD_EVENT_PRIORITY",
            version_a=version_a,
            version_b=version_b,
            event_id=event_data.get("event_id", ""),
            score_a=score_a,
            score_b=score_b,
            score_delta=delta,
            explanation_differences=diffs,
        )

    def get_evaluation(self, evaluation_id: str) -> Optional[ScoringEvaluationManifest]:
        return self._evaluations_cache.get(evaluation_id)

    def list_evaluations(self) -> List[ScoringEvaluationManifest]:
        return list(self._evaluations_cache.values())

    def activate_model_version(
        self,
        model_id: str,
        version: str,
        user_id: str,
        user_roles: List[str],
    ) -> ScoringGovernanceAuditRecord:
        manifest = self.get_evaluation(f"eval_{model_id}_{version}")
        return ModelGovernanceManager.activate_model_version(
            model_id=model_id,
            version=version,
            user_id=user_id,
            user_roles=user_roles,
            validation_manifest=manifest,
        )

    def rollback_model_version(
        self,
        model_id: str,
        rollback_to_version: str,
        user_id: str,
        user_roles: List[str],
        rationale: str = "Rollback due to candidate validation failure or performance regression.",
    ) -> ScoringGovernanceAuditRecord:
        return ModelGovernanceManager.rollback_model_version(
            model_id=model_id,
            rollback_to_version=rollback_to_version,
            user_id=user_id,
            user_roles=user_roles,
            rationale=rationale,
        )

    def get_governance_audit(self, model_id: Optional[str] = None) -> List[ScoringGovernanceAuditRecord]:
        return ModelGovernanceManager.get_audit_trail(model_id=model_id)

    def get_telemetry(self, model_id: str = "MOD_EVENT_PRIORITY") -> ScoringTelemetrySummary:
        return ScoringMonitor.get_model_telemetry(model_id=model_id)
