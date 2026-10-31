"""Domain Models for ATLAS Intelligence Scoring (Stage 139)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ScoreStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    STALE = "STALE"
    MODEL_UNVALIDATED = "MODEL_UNVALIDATED"
    MODEL_DISABLED = "MODEL_DISABLED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    CALCULATION_FAILED = "CALCULATION_FAILED"


class ScoreScale(str, Enum):
    BOUNDED_INDEX_0_100 = "BOUNDED_INDEX_0_100"
    ORDINAL_RANK = "ORDINAL_RANK"
    PROBABILITY_0_1 = "PROBABILITY_0_1"


class ScoreObjectiveId(str, Enum):
    EVENT_REVIEW_PRIORITY = "EVENT_REVIEW_PRIORITY"
    EVENT_ENTITY_RELEVANCE = "EVENT_ENTITY_RELEVANCE"
    PORTFOLIO_EVENT_ATTENTION = "PORTFOLIO_EVENT_ATTENTION"
    ECONOMIC_EVENT_RELEVANCE = "ECONOMIC_EVENT_RELEVANCE"
    GEOGRAPHIC_EVENT_RELEVANCE = "GEOGRAPHIC_EVENT_RELEVANCE"
    SOURCE_EVIDENCE_ASSESSMENT = "SOURCE_EVIDENCE_ASSESSMENT"


class GovernanceStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    SHADOW = "SHADOW"
    DISABLED = "DISABLED"
    ROLLED_BACK = "ROLLED_BACK"
    RETIRED = "RETIRED"


class FactorTransformationMethod(str, Enum):
    BINARY_ELIGIBILITY = "BINARY_ELIGIBILITY"
    BOUNDED_PROPORTION = "BOUNDED_PROPORTION"
    EXPONENTIAL_DECAY = "EXPONENTIAL_DECAY"
    DISTANCE_STEP_FUNCTION = "DISTANCE_STEP_FUNCTION"
    ORDINAL_MAPPING = "ORDINAL_MAPPING"
    DIRECT_SCALE = "DIRECT_SCALE"


class MissingValuePolicy(str, Enum):
    OMIT_FACTOR = "OMIT_FACTOR"
    NEUTRAL_VALUE_WITH_DISCLOSURE = "NEUTRAL_VALUE_WITH_DISCLOSURE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class FactorContribution(BaseModel):
    """Calculated contribution of a single factor to the final score."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    factor_id: str
    factor_name: str
    raw_value: Optional[Any] = None
    transformed_value: float = Field(ge=0.0, le=1.0)
    transformation_method: FactorTransformationMethod
    weight: float = Field(ge=0.0, le=1.0)
    contribution_points: float
    is_missing: bool = False
    source_reference: Optional[str] = None
    explanation: str


class ScoreUncertaintyMetadata(BaseModel):
    """Explicit disclosure of coverage, missingness, and analytical limits."""
    coverage_ratio: float = Field(ge=0.0, le=1.0)
    available_feature_count: int
    required_feature_count: int
    missing_features: List[str] = Field(default_factory=list)
    has_source_conflicts: bool = False
    conflict_notes: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    is_calibration_applicable: bool = False
    calibration_target: Optional[str] = None


class ScoreLineageRecord(BaseModel):
    """Auditable trace linking the score back to source documents and graph edges."""
    feature_snapshot_id: str
    model_id: str
    model_version: str
    policy_id: str
    event_revision: Optional[int] = None
    graph_revision: Optional[int] = None
    exposure_run_id: Optional[str] = None
    source_ids: List[str] = Field(default_factory=list)
    computation_host: str = "atlas-scoring-engine-v1"


class AtlasIntelligenceScore(BaseModel):
    """Canonical typed intelligence score product."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    score_id: str
    score_type: str
    scoring_objective: ScoreObjectiveId
    subject_reference: Dict[str, Any]
    context_reference: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    entity_id: Optional[str] = None
    portfolio_id: Optional[str] = None

    model_id: str
    model_version: str
    score_value: Optional[float] = None  # None if INSUFFICIENT_DATA or NOT_APPLICABLE
    score_scale: ScoreScale
    score_interpretation: str
    score_status: ScoreStatus

    factor_contributions: List[FactorContribution] = Field(default_factory=list)
    uncertainty: ScoreUncertaintyMetadata
    lineage: ScoreLineageRecord

    valid_at: str
    known_as_of: str
    computed_at: str
    tenant_scope: Optional[str] = None


class RankedItem(BaseModel):
    """Ranked item entry within an intelligence ranking request."""
    rank: int
    score: AtlasIntelligenceScore
    tie_breaker_key: str


class ScoringEvaluationManifest(BaseModel):
    """Performance evaluation record for a versioned scoring model."""
    evaluation_id: str
    model_id: str
    model_version: str
    evaluation_dataset: str
    time_window_start: str
    time_window_end: str
    sample_size: int
    ndcg_at_10: Optional[float] = None
    precision_at_5: Optional[float] = None
    mean_reciprocal_rank: Optional[float] = None
    brier_score: Optional[float] = None
    expected_calibration_error: Optional[float] = None
    drift_detected: bool = False
    validation_status: str
    evaluated_at: str

