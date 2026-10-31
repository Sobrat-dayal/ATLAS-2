"""Infrastructure & Physical Proximity Domain Handler (Stage 137).

Enforces institutional physical-world invariants:
- Proximity between an event (e.g. earthquake, flood) and a corporate facility or infrastructure asset
  confirms spatial co-location ONLY.
- It does NOT constitute proof of operational interruption, structural damage, or financial loss.
- Damage status and financial loss must remain UNAVAILABLE / UNKNOWN unless official loss assessments
  are published and ingested.
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


def analyze_facility_event_proximity(
    run_id: str,
    company_ref: CanonicalGraphNodeRef,
    facility_ref: CanonicalGraphNodeRef,
    event_ref: CanonicalGraphNodeRef,
    distance_km: Decimal,
    threshold_km: Decimal = Decimal("50.0")
) -> AtlasExposureResult:
    """Evaluate physical event proximity without inferring damage or financial loss."""
    is_proximate = distance_km <= threshold_km

    return AtlasExposureResult(
        exposure_id=f"exp-prox-{run_id}-{facility_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=company_ref,
        target_entity_ref=facility_ref,
        related_event_id=event_ref.entity_id,
        exposure_domain=ExposureDomain.INFRASTRUCTURE,
        exposure_type=ExposureType.INFRASTRUCTURE_ASSET_ASSOCIATION,
        exposure_measure_id="EARTHQUAKE_PROXIMITY_PRESENCE_V1",
        evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
        relationship_strength=ExposureRelationshipStrength.DIRECT_MEASURED,
        amount=distance_km,
        unit="KM",
        percentage=None,
        numerator_value=distance_km,
        denominator_value=threshold_km,
        denominator_reference=f"Proximity Threshold ({threshold_km} km)",
        calculation_method_id="HAVERSINE_SPATIAL_DISTANCE",
        coverage_status=CoverageStatus.COMPLETE,
        uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
        explanation=(
            f"Facility {facility_ref.canonical_name} is located {distance_km} km from {event_ref.canonical_name} "
            f"(threshold: {threshold_km} km). Physical proximity is confirmed. Operational status, structural damage, "
            "and economic loss are UNKNOWN and cannot be inferred from spatial distance."
        ),
        limitations_disclaimer=(
            "Geographic proximity confirms co-location only. It does not measure or imply asset impairment, "
            "business disruption, or insurance recovery."
        )
    )

