"""Commodity Exposure Domain Handler (Stage 137).

Enforces institutional commodity invariants:
- Contextual mention of a commodity in association with an entity is qualitative ONLY.
- Numerical financial exposure (price beta, physical consumption, hedge ratio) is strictly
  marked UNAVAILABLE unless substantiated by regulatory commodity disclosures.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.exposure.domain import (
    AtlasExposureResult,
    CoverageStatus,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureRelationshipStrength,
    ExposureType,
    UncertaintyClass,
)


def analyze_commodity_mention(
    run_id: str,
    subject_ref: CanonicalGraphNodeRef,
    commodity_ref: CanonicalGraphNodeRef,
    source_context: str
) -> AtlasExposureResult:
    """Record verified qualitative commodity mention without fabricating numerical exposure."""
    return AtlasExposureResult(
        exposure_id=f"exp-com-{run_id}-{commodity_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=subject_ref,
        target_entity_ref=commodity_ref,
        exposure_domain=ExposureDomain.COMMODITY,
        exposure_type=ExposureType.COMMODITY_PRICE_EXPOSURE,
        exposure_measure_id="COMMODITY_MENTION_QUALITATIVE_V1",
        evidence_class=ExposureEvidenceClass.UNAVAILABLE,
        relationship_strength=ExposureRelationshipStrength.QUALITATIVE_REPORTED,
        amount=None,
        currency="USD",
        unit="QUALITATIVE",
        percentage=None,
        calculation_method_id="TEXTUAL_EXTRACTION",
        coverage_status=CoverageStatus.UNCOVERED,
        uncertainty_class=UncertaintyClass.SOURCE_INCOMPLETE,
        explanation=(
            f"Qualitative association between {subject_ref.canonical_name} and {commodity_ref.canonical_name} "
            f"identified in '{source_context}'. Quantitative financial or volumetric price exposure is UNAVAILABLE "
            "because numerical hedging/consumption disclosures were not reported."
        )
    )
