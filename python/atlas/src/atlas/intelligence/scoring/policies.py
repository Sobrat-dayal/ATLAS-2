"""Scoring Policies and Weight Definitions for ATLAS Intelligence Scoring (Stage 139)."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .domain import GovernanceStatus, MissingValuePolicy, ScoreObjectiveId
from .errors import ScoringPolicyNotFoundError


class ScoringFactorWeightConfig(BaseModel):
    """Weight and transformation configuration for a single factor."""
    factor_id: str
    weight: float = Field(ge=0.0, le=1.0)
    half_life_hours: Optional[float] = None
    max_bound: Optional[float] = None


class IntelligenceScoringPolicy(BaseModel):
    """Versioned scoring policy defining factor weights, missing data rules, and thresholds."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    policy_id: str
    policy_version: str
    score_objective: ScoreObjectiveId
    description: str
    factor_configs: List[ScoringFactorWeightConfig]
    missing_data_policy: MissingValuePolicy = MissingValuePolicy.OMIT_FACTOR
    min_coverage_threshold: float = 0.50
    governance_status: GovernanceStatus = GovernanceStatus.ACTIVE
    is_default: bool = False
    tenant_id: Optional[str] = None  # None = Global system policy


CANONICAL_POLICIES: Dict[str, IntelligenceScoringPolicy] = {
    "pol_event_priority_v1": IntelligenceScoringPolicy(
        policy_id="pol_event_priority_v1",
        policy_version="v1.0.0",
        score_objective=ScoreObjectiveId.EVENT_REVIEW_PRIORITY,
        description="Standard institutional operational event triage baseline.",
        factor_configs=[
            ScoringFactorWeightConfig(factor_id="FEAT_DIRECT_ISSUER_MATCH", weight=0.35),
            ScoringFactorWeightConfig(factor_id="FEAT_INDEPENDENT_SOURCE_COUNT", weight=0.25, max_bound=5.0),
            ScoringFactorWeightConfig(factor_id="FEAT_PRIMARY_OFFICIAL_FILING", weight=0.20),
            ScoringFactorWeightConfig(factor_id="FEAT_RECENCY_ELAPSED_HOURS", weight=0.20, half_life_hours=72.0),
        ],
        missing_data_policy=MissingValuePolicy.OMIT_FACTOR,
        min_coverage_threshold=0.50,
        governance_status=GovernanceStatus.ACTIVE,
        is_default=True,
    ),
    "pol_event_priority_v2": IntelligenceScoringPolicy(
        policy_id="pol_event_priority_v2",
        policy_version="v2.0.0",
        score_objective=ScoreObjectiveId.EVENT_REVIEW_PRIORITY,
        description="Alternative candidate policy weighting primary filings higher.",
        factor_configs=[
            ScoringFactorWeightConfig(factor_id="FEAT_DIRECT_ISSUER_MATCH", weight=0.40),
            ScoringFactorWeightConfig(factor_id="FEAT_INDEPENDENT_SOURCE_COUNT", weight=0.15, max_bound=5.0),
            ScoringFactorWeightConfig(factor_id="FEAT_PRIMARY_OFFICIAL_FILING", weight=0.35),
            ScoringFactorWeightConfig(factor_id="FEAT_RECENCY_ELAPSED_HOURS", weight=0.10, half_life_hours=48.0),
        ],
        missing_data_policy=MissingValuePolicy.OMIT_FACTOR,
        min_coverage_threshold=0.50,
        governance_status=GovernanceStatus.VALIDATED,
        is_default=False,
    ),
    "pol_entity_relevance_v1": IntelligenceScoringPolicy(
        policy_id="pol_entity_relevance_v1",
        policy_version="v1.0.0",
        score_objective=ScoreObjectiveId.EVENT_ENTITY_RELEVANCE,
        description="Event-to-entity direct vs indirect predicate weighting policy.",
        factor_configs=[
            ScoringFactorWeightConfig(factor_id="FEAT_DIRECT_ISSUER_MATCH", weight=0.60),
            ScoringFactorWeightConfig(factor_id="FEAT_PRIMARY_OFFICIAL_FILING", weight=0.40),
        ],
        missing_data_policy=MissingValuePolicy.OMIT_FACTOR,
        min_coverage_threshold=0.50,
        governance_status=GovernanceStatus.ACTIVE,
        is_default=True,
    ),
    "pol_portfolio_attention_v1": IntelligenceScoringPolicy(
        policy_id="pol_portfolio_attention_v1",
        policy_version="v1.0.0",
        score_objective=ScoreObjectiveId.PORTFOLIO_EVENT_ATTENTION,
        description="Portfolio holdings attention scoring based on NAV weight and direct issuer link.",
        factor_configs=[
            ScoringFactorWeightConfig(factor_id="FEAT_PORTFOLIO_WEIGHT", weight=0.50, max_bound=25.0),
            ScoringFactorWeightConfig(factor_id="FEAT_DIRECT_ISSUER_MATCH", weight=0.30),
            ScoringFactorWeightConfig(factor_id="FEAT_PRIMARY_OFFICIAL_FILING", weight=0.20),
        ],
        missing_data_policy=MissingValuePolicy.OMIT_FACTOR,
        min_coverage_threshold=0.50,
        governance_status=GovernanceStatus.ACTIVE,
        is_default=True,
    ),
    "pol_geographic_relevance_v1": IntelligenceScoringPolicy(
        policy_id="pol_geographic_relevance_v1",
        policy_version="v1.0.0",
        score_objective=ScoreObjectiveId.GEOGRAPHIC_EVENT_RELEVANCE,
        description="Spatial co-location and facility buffer proximity policy.",
        factor_configs=[
            ScoringFactorWeightConfig(factor_id="FEAT_PROXIMITY_KM", weight=0.70),
            ScoringFactorWeightConfig(factor_id="FEAT_PRIMARY_OFFICIAL_FILING", weight=0.30),
        ],
        missing_data_policy=MissingValuePolicy.OMIT_FACTOR,
        min_coverage_threshold=0.50,
        governance_status=GovernanceStatus.ACTIVE,
        is_default=True,
    ),
    "pol_source_evidence_v1": IntelligenceScoringPolicy(
        policy_id="pol_source_evidence_v1",
        policy_version="v1.0.0",
        score_objective=ScoreObjectiveId.SOURCE_EVIDENCE_ASSESSMENT,
        description="Evidence grounding, official filing backing, and conflict penalty policy.",
        factor_configs=[
            ScoringFactorWeightConfig(factor_id="FEAT_INDEPENDENT_SOURCE_COUNT", weight=0.40, max_bound=5.0),
            ScoringFactorWeightConfig(factor_id="FEAT_PRIMARY_OFFICIAL_FILING", weight=0.40),
            ScoringFactorWeightConfig(factor_id="FEAT_SOURCE_CONFLICT_FLAG", weight=0.20),
        ],
        missing_data_policy=MissingValuePolicy.OMIT_FACTOR,
        min_coverage_threshold=0.50,
        governance_status=GovernanceStatus.ACTIVE,
        is_default=True,
    ),
}


class ScoringPolicyRegistry:
    """Registry managing available scoring policies."""

    @classmethod
    def get_policy(cls, policy_id: str) -> IntelligenceScoringPolicy:
        if policy_id not in CANONICAL_POLICIES:
            raise ScoringPolicyNotFoundError(policy_id=policy_id)
        return CANONICAL_POLICIES[policy_id]

    @classmethod
    def list_policies(cls, objective_id: Optional[ScoreObjectiveId] = None) -> List[IntelligenceScoringPolicy]:
        all_pols = list(CANONICAL_POLICIES.values())
        if objective_id:
            return [p for p in all_pols if p.score_objective == objective_id]
        return all_pols

    @classmethod
    def register_policy(cls, policy: IntelligenceScoringPolicy):
        CANONICAL_POLICIES[policy.policy_id] = policy

