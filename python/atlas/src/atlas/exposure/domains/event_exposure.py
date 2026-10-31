"""Event-Driven Exposure Domain Handler (Stage 137).

Links Stage 135 Universal Events and Stage 136 Knowledge Graph relationships
to verified financial exposures (Company revenue, Portfolio holdings, Corporate Facilities).

Enforces institutional invariant:
- "Exposure Is Not Impact": Identifies which financial assets or revenue streams are topologically
  linked to the event's locus or entities, while strictly refusing to predict price changes,
  losses, or speculative impacts.
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


def analyze_event_driven_exposure(
    run_id: str,
    event_ref: CanonicalGraphNodeRef,
    subject_entity_ref: CanonicalGraphNodeRef,
    exposure_type: ExposureType,
    exposure_domain: ExposureDomain,
    measure_id: str,
    amount: Optional[Decimal],
    currency: Optional[str],
    percentage: Optional[Decimal],
    graph_path_ids: List[str],
    explanation: str
) -> AtlasExposureResult:
    """Construct verified event-to-entity exposure result."""
    return AtlasExposureResult(
        exposure_id=f"exp-evt-{run_id}-{subject_entity_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=subject_entity_ref,
        target_entity_ref=subject_entity_ref,
        related_event_id=event_ref.entity_id,
        exposure_domain=exposure_domain,
        exposure_type=exposure_type,
        exposure_measure_id=measure_id,
        evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED if amount is not None else ExposureEvidenceClass.SOURCE_REPORTED_QUALITATIVE,
        relationship_strength=ExposureRelationshipStrength.DERIVED_FROM_VERIFIED_DATA,
        amount=amount,
        currency=currency,
        unit="CURRENCY" if currency else "PERCENT",
        percentage=percentage,
        calculation_method_id="EVENT_GRAPH_TRAVERSAL",
        graph_path_ids=graph_path_ids,
        coverage_status=CoverageStatus.COMPLETE if amount is not None else CoverageStatus.PARTIAL,
        uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC if amount is not None else UncertaintyClass.SOURCE_INCOMPLETE,
        explanation=explanation,
        limitations_disclaimer="Event-driven exposure measures structural connectedness only. It does not predict market price changes or damage."
    )

