"""Geographic Exposure Domain Handler (Stage 137).

Analyzes territorial concentration across revenue, assets, and operational presence:
- Differentiates revenue territory from issuer domicile
- Preserves unallocated international residuals
- Explicitly distinguishes facility count presence from financial exposure
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
from atlas.exposure.errors import ProhibitedInferenceError
from atlas.exposure.quality.coverage import calculate_coverage_summary


def analyze_geographic_presence_vs_revenue(
    run_id: str,
    company_ref: CanonicalGraphNodeRef,
    region_ref: CanonicalGraphNodeRef,
    facility_count: int,
    total_facilities: int,
    reported_revenue: Optional[Decimal] = None,
    total_company_revenue: Optional[Decimal] = None,
    currency: str = "USD"
) -> Dict[str, any]:
    """Demonstrate invariant: facility counts represent physical operational presence, NEVER revenue."""
    results: List[AtlasExposureResult] = []

    # 1. Operational Presence Result
    facility_pct = (Decimal(facility_count) / Decimal(total_facilities) * Decimal("100.0")).quantize(Decimal("0.01")) if total_facilities > 0 else Decimal("0.0")
    results.append(
        AtlasExposureResult(
            exposure_id=f"exp-fac-{run_id}-{region_ref.entity_id}",
            analysis_run_id=run_id,
            subject_entity_ref=company_ref,
            target_entity_ref=region_ref,
            exposure_domain=ExposureDomain.INFRASTRUCTURE,
            exposure_type=ExposureType.FACILITY_GEOGRAPHIC_PRESENCE,
            exposure_measure_id="FACILITY_COUNT_V1",
            evidence_class=ExposureEvidenceClass.REPORTED,
            relationship_strength=ExposureRelationshipStrength.DIRECT_MEASURED,
            amount=Decimal(facility_count),
            unit="COUNT",
            percentage=facility_pct,
            numerator_value=Decimal(facility_count),
            denominator_value=Decimal(total_facilities),
            denominator_reference=f"Total Facilities Globally ({total_facilities})",
            calculation_method_id="SPATIAL_COUNT",
            coverage_status=CoverageStatus.COMPLETE,
            uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
            explanation=f"{company_ref.canonical_name} operates {facility_count} facilities in {region_ref.canonical_name} ({facility_pct}% of total {total_facilities} facilities)."
        )
    )

    # 2. Revenue Result: If reported revenue is absent, revenue exposure is UNAVAILABLE
    if reported_revenue is not None and total_company_revenue is not None and total_company_revenue > Decimal("0.0"):
        rev_pct = (reported_revenue / total_company_revenue * Decimal("100.0")).quantize(Decimal("0.01"))
        results.append(
            AtlasExposureResult(
                exposure_id=f"exp-rev-{run_id}-{region_ref.entity_id}",
                analysis_run_id=run_id,
                subject_entity_ref=company_ref,
                target_entity_ref=region_ref,
                exposure_domain=ExposureDomain.GEOGRAPHIC,
                exposure_type=ExposureType.REVENUE_GEOGRAPHIC_EXPOSURE,
                exposure_measure_id="REV_GEO_SHARE_V1",
                evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
                relationship_strength=ExposureRelationshipStrength.DIRECT_REPORTED,
                amount=reported_revenue,
                currency=currency,
                unit="PERCENT",
                percentage=rev_pct,
                numerator_value=reported_revenue,
                denominator_value=total_company_revenue,
                calculation_method_id="RATIO_CALCULATION",
                coverage_status=CoverageStatus.PARTIAL,
                uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
                explanation=f"Reported revenue of {reported_revenue} {currency} ({rev_pct}% of total)."
            )
        )
    else:
        # Invariant: Never infer revenue from facility counts!
        results.append(
            AtlasExposureResult(
                exposure_id=f"exp-rev-unavail-{run_id}-{region_ref.entity_id}",
                analysis_run_id=run_id,
                subject_entity_ref=company_ref,
                target_entity_ref=region_ref,
                exposure_domain=ExposureDomain.GEOGRAPHIC,
                exposure_type=ExposureType.REVENUE_GEOGRAPHIC_EXPOSURE,
                exposure_measure_id="REV_GEO_SHARE_V1",
                evidence_class=ExposureEvidenceClass.UNAVAILABLE,
                relationship_strength=ExposureRelationshipStrength.UNRESOLVED,
                amount=None,
                currency=currency,
                unit="PERCENT",
                percentage=None,
                calculation_method_id="UNAVAILABLE_DATA_POLICY",
                coverage_status=CoverageStatus.UNCOVERED,
                uncertainty_class=UncertaintyClass.SOURCE_INCOMPLETE,
                explanation="Geographic revenue for this region is not disclosed in official filings. Revenue cannot be inferred from facility counts."
            )
        )

    return {"results": results}
