"""Scoring Objective Registry for ATLAS Intelligence Scoring (Stage 139)."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from .domain import ScoreObjectiveId, ScoreScale
from .errors import ScoringObjectiveNotFoundError


class ScoringObjectiveDefinition(BaseModel):
    """Institutional definition of a scoring objective, target construct, and boundaries."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    objective_id: ScoreObjectiveId
    name: str
    target_construct: str
    intended_use: str
    prohibited_interpretations: List[str]
    eligible_subject_types: List[str]
    default_scale: ScoreScale
    required_features: List[str]
    optional_features: List[str]


CANONICAL_OBJECTIVES: Dict[ScoreObjectiveId, ScoringObjectiveDefinition] = {
    ScoreObjectiveId.EVENT_REVIEW_PRIORITY: ScoringObjectiveDefinition(
        objective_id=ScoreObjectiveId.EVENT_REVIEW_PRIORITY,
        name="Event Review Priority",
        target_construct="Operational urgency index recommending order of human investigation within a candidate set.",
        intended_use="Triage high-relevance, highly verified events requiring prompt analyst review.",
        prohibited_interpretations=[
            "Probability of equity price movement",
            "Probability of corporate financial impairment or default",
            "Expected market return or alpha forecast",
            "Automated buy/sell trade recommendation",
        ],
        eligible_subject_types=["EVENT"],
        default_scale=ScoreScale.BOUNDED_INDEX_0_100,
        required_features=["event_id", "event_category", "verification_status", "published_at"],
        optional_features=["direct_entity_id", "portfolio_holding_weight", "independent_sources_count", "recency_half_life"],
    ),
    ScoreObjectiveId.EVENT_ENTITY_RELEVANCE: ScoringObjectiveDefinition(
        objective_id=ScoreObjectiveId.EVENT_ENTITY_RELEVANCE,
        name="Event-to-Entity Relevance",
        target_construct="Strength, directness, and specificity of verified graph connection between an event and an entity.",
        intended_use="Identify whether an event directly concerns an issuer, subsidiary, or mere text mention.",
        prohibited_interpretations=[
            "Financial contagion coefficient",
            "Earnings surprise forecast",
            "Stock correlation metric",
        ],
        eligible_subject_types=["EVENT", "ENTITY"],
        default_scale=ScoreScale.BOUNDED_INDEX_0_100,
        required_features=["event_id", "target_entity_id", "predicate"],
        optional_features=["hop_distance", "facility_match"],
    ),
    ScoreObjectiveId.PORTFOLIO_EVENT_ATTENTION: ScoringObjectiveDefinition(
        objective_id=ScoreObjectiveId.PORTFOLIO_EVENT_ATTENTION,
        name="Portfolio Event Attention",
        target_construct="Prioritization of events based on documented relationship to authorized portfolio holdings.",
        intended_use="Alert risk managers to events involving issuers in their specific active portfolios.",
        prohibited_interpretations=[
            "Portfolio Value-at-Risk (VaR)",
            "Expected portfolio dollar drawdown",
            "Loss probability",
        ],
        eligible_subject_types=["PORTFOLIO", "EVENT"],
        default_scale=ScoreScale.BOUNDED_INDEX_0_100,
        required_features=["portfolio_id", "event_id", "holding_weight_pct"],
        optional_features=["gross_exposure_usd", "is_look_through"],
    ),
    ScoreObjectiveId.ECONOMIC_EVENT_RELEVANCE: ScoringObjectiveDefinition(
        objective_id=ScoreObjectiveId.ECONOMIC_EVENT_RELEVANCE,
        name="Economic & Macro Relevance",
        target_construct="Documented relevance of an event to monetary policy, central banks, and macroeconomic indicators.",
        intended_use="Highlight significant rate decisions, inflation releases, and sovereign regulatory changes.",
        prohibited_interpretations=[
            "Universal equity beta",
            "GDP growth forecast",
            "Bond yield curve curve-shift forecast",
        ],
        eligible_subject_types=["EVENT", "ECONOMIC_INDICATOR"],
        default_scale=ScoreScale.BOUNDED_INDEX_0_100,
        required_features=["event_id", "indicator_or_cb_id"],
        optional_features=["magnitude_basis_points", "consensus_delta"],
    ),
    ScoreObjectiveId.GEOGRAPHIC_EVENT_RELEVANCE: ScoringObjectiveDefinition(
        objective_id=ScoreObjectiveId.GEOGRAPHIC_EVENT_RELEVANCE,
        name="Geographic & Facility Proximity Relevance",
        target_construct="Spatial co-location index between physical events and corporate/infrastructure assets.",
        intended_use="Filter events occurring within proximity buffers of critical corporate facilities.",
        prohibited_interpretations=[
            "Confirmed physical structural damage",
            "Facility operational outage probability",
            "Business interruption dollar loss",
        ],
        eligible_subject_types=["EVENT", "FACILITY", "INFRASTRUCTURE_ASSET"],
        default_scale=ScoreScale.BOUNDED_INDEX_0_100,
        required_features=["event_id", "asset_id", "distance_km"],
        optional_features=["administrative_region_match", "event_magnitude"],
    ),
    ScoreObjectiveId.SOURCE_EVIDENCE_ASSESSMENT: ScoringObjectiveDefinition(
        objective_id=ScoreObjectiveId.SOURCE_EVIDENCE_ASSESSMENT,
        name="Source Evidence Assessment",
        target_construct="Completeness, official backing, and consistency of supporting evidence documentation.",
        intended_use="Assess whether reported events are grounded in primary filings or unverified rumours.",
        prohibited_interpretations=[
            "Philosophical truth probability",
            "Editorial credibility ranking of news agencies",
        ],
        eligible_subject_types=["EVENT", "SOURCE"],
        default_scale=ScoreScale.BOUNDED_INDEX_0_100,
        required_features=["event_id", "source_count"],
        optional_features=["primary_source_present", "has_conflicts", "is_retracted"],
    ),
}


class ScoringObjectiveRegistry:
    """Registry managing valid scoring objectives and verification."""

    @classmethod
    def get_objective(cls, objective_id: str) -> ScoringObjectiveDefinition:
        try:
            enum_val = ScoreObjectiveId(objective_id)
            return CANONICAL_OBJECTIVES[enum_val]
        except (ValueError, KeyError):
            raise ScoringObjectiveNotFoundError(objective_id=objective_id)

    @classmethod
    def list_objectives(cls) -> List[ScoringObjectiveDefinition]:
        return list(CANONICAL_OBJECTIVES.values())
