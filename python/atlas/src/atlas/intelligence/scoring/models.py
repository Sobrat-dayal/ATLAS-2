"""Model Registry and Version Management for ATLAS Intelligence Scoring (Stage 139)."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .domain import GovernanceStatus, ScoreObjectiveId, ScoreScale
from .errors import ScoringModelNotFoundError


class ScoringModelDefinition(BaseModel):
    """Institutional model metadata record."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_id: str
    model_name: str
    model_family: str = "DETERMINISTIC_RULES"
    objective_id: ScoreObjectiveId
    active_version: str
    supported_versions: List[str] = Field(default_factory=list)
    score_scale: ScoreScale
    default_policy_id: str
    governance_status: GovernanceStatus = GovernanceStatus.ACTIVE
    is_production: bool = True
    approved_by: Optional[str] = "atlas_risk_governance_board"
    approved_at: Optional[str] = "2024-01-01T00:00:00Z"


CANONICAL_MODELS: Dict[str, ScoringModelDefinition] = {
    "MOD_EVENT_PRIORITY": ScoringModelDefinition(
        model_id="MOD_EVENT_PRIORITY",
        model_name="Canonical Event Review Priority Model",
        model_family="DETERMINISTIC_RULES",
        objective_id=ScoreObjectiveId.EVENT_REVIEW_PRIORITY,
        active_version="v1.0.0",
        supported_versions=["v1.0.0", "v2.0.0", "v2.0.0-candidate"],
        score_scale=ScoreScale.BOUNDED_INDEX_0_100,
        default_policy_id="pol_event_priority_v1",
        governance_status=GovernanceStatus.ACTIVE,
        is_production=True,
    ),
    "MOD_ENTITY_RELEVANCE": ScoringModelDefinition(
        model_id="MOD_ENTITY_RELEVANCE",
        model_name="Canonical Entity Relevance Model",
        model_family="DETERMINISTIC_RULES",
        objective_id=ScoreObjectiveId.EVENT_ENTITY_RELEVANCE,
        active_version="v1.0.0",
        supported_versions=["v1.0.0"],
        score_scale=ScoreScale.BOUNDED_INDEX_0_100,
        default_policy_id="pol_entity_relevance_v1",
        governance_status=GovernanceStatus.ACTIVE,
        is_production=True,
    ),
    "MOD_PORTFOLIO_ATTENTION": ScoringModelDefinition(
        model_id="MOD_PORTFOLIO_ATTENTION",
        model_name="Portfolio Holdings Event Attention Model",
        model_family="DETERMINISTIC_RULES",
        objective_id=ScoreObjectiveId.PORTFOLIO_EVENT_ATTENTION,
        active_version="v1.0.0",
        supported_versions=["v1.0.0"],
        score_scale=ScoreScale.BOUNDED_INDEX_0_100,
        default_policy_id="pol_portfolio_attention_v1",
        governance_status=GovernanceStatus.ACTIVE,
        is_production=True,
    ),
    "MOD_GEOGRAPHIC_RELEVANCE": ScoringModelDefinition(
        model_id="MOD_GEOGRAPHIC_RELEVANCE",
        model_name="Facility Proximity & Geospatial Relevance Model",
        model_family="DETERMINISTIC_RULES",
        objective_id=ScoreObjectiveId.GEOGRAPHIC_EVENT_RELEVANCE,
        active_version="v1.0.0",
        supported_versions=["v1.0.0"],
        score_scale=ScoreScale.BOUNDED_INDEX_0_100,
        default_policy_id="pol_geographic_relevance_v1",
        governance_status=GovernanceStatus.ACTIVE,
        is_production=True,
    ),
    "MOD_SOURCE_EVIDENCE": ScoringModelDefinition(
        model_id="MOD_SOURCE_EVIDENCE",
        model_name="Source Grounding & Evidence Assessment Model",
        model_family="DETERMINISTIC_RULES",
        objective_id=ScoreObjectiveId.SOURCE_EVIDENCE_ASSESSMENT,
        active_version="v1.0.0",
        supported_versions=["v1.0.0"],
        score_scale=ScoreScale.BOUNDED_INDEX_0_100,
        default_policy_id="pol_source_evidence_v1",
        governance_status=GovernanceStatus.ACTIVE,
        is_production=True,
    ),
}


class ModelRegistry:
    """Registry maintaining active and historical model versions."""

    @classmethod
    def get_model(cls, model_id: str, version: Optional[str] = None) -> ScoringModelDefinition:
        if model_id not in CANONICAL_MODELS:
            raise ScoringModelNotFoundError(model_id=model_id, version=version)
        model = CANONICAL_MODELS[model_id]
        if version and version not in model.supported_versions:
            raise ScoringModelNotFoundError(model_id=model_id, version=version)
        return model

    @classmethod
    def list_models(cls) -> List[ScoringModelDefinition]:
        return list(CANONICAL_MODELS.values())

    @classmethod
    def update_active_version(cls, model_id: str, version: str):
        if model_id not in CANONICAL_MODELS:
            raise ScoringModelNotFoundError(model_id=model_id, version=version)
        model = CANONICAL_MODELS[model_id]
        if version not in model.supported_versions:
            model.supported_versions.append(version)
        model.active_version = version
