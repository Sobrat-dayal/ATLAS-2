"""Company Exposure Domain Handler (Stage 137).

Analyzes verified company exposures:
- Geographic revenue breakdown (reported segment revenue vs total consolidated revenue)
- Segment/Business line concentrations
- Major customer disclosure exposure (e.g. 10%+ customer concentration)
"""

from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime, timezone

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
from atlas.exposure.errors import InvalidDenominatorError
from atlas.exposure.quality.coverage import calculate_coverage_summary


def analyze_company_geographic_revenue(
    run_id: str,
    company_ref: CanonicalGraphNodeRef,
    segments: List[Dict[str, any]],
    total_consolidated_revenue: Decimal,
    currency: str = "USD",
    period: str = "FY2024",
    as_of: Optional[datetime] = None,
    tenant_id: Optional[str] = None
) -> Dict[str, any]:
    """Compute geographic revenue exposure shares for a company."""
    if total_consolidated_revenue <= Decimal("0.0"):
        raise InvalidDenominatorError("Total consolidated revenue must be a verified positive value.")

    results: List[AtlasExposureResult] = []
    covered_sum = Decimal("0.0")
    covered_names: List[str] = []

    for seg in segments:
        region_code = seg.get("region_code", "UNKNOWN")
        region_name = seg.get("region_name", region_code)
        rev_amt = Decimal(str(seg.get("revenue_amount", "0.0")))
        covered_sum += rev_amt
        covered_names.append(region_name)

        share_pct = (rev_amt / total_consolidated_revenue * Decimal("100.0")).quantize(Decimal("0.01"))

        target_ref = CanonicalGraphNodeRef(
            node_type=GraphNodeType.COUNTRY if len(region_code) == 2 else GraphNodeType.ADMINISTRATIVE_REGION,
            entity_id=region_code,
            canonical_name=region_name,
            country_code=region_code if len(region_code) == 2 else None
        )

        results.append(
            AtlasExposureResult(
                exposure_id=f"exp-geo-{run_id}-{region_code}",
                analysis_run_id=run_id,
                subject_entity_ref=company_ref,
                target_entity_ref=target_ref,
                exposure_domain=ExposureDomain.GEOGRAPHIC,
                exposure_type=ExposureType.REVENUE_GEOGRAPHIC_EXPOSURE,
                exposure_measure_id="REV_GEO_SHARE_V1",
                evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
                relationship_strength=ExposureRelationshipStrength.DIRECT_REPORTED,
                amount=rev_amt,
                currency=currency,
                unit="PERCENT",
                percentage=share_pct,
                numerator_value=rev_amt,
                denominator_value=total_consolidated_revenue,
                denominator_reference=f"Total Reported Consolidated Revenue ({period})",
                reporting_period=period,
                valid_at=as_of,
                known_as_of=as_of or datetime.now(timezone.utc),
                calculation_method_id="RATIO_CALCULATION",
                coverage_status=CoverageStatus.COMPLETE if rev_amt == total_consolidated_revenue else CoverageStatus.PARTIAL,
                coverage_ratio=(rev_amt / total_consolidated_revenue).quantize(Decimal("0.0001")),
                uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
                explanation=f"{company_ref.canonical_name} reported {rev_amt} {currency} ({share_pct}%) revenue from {region_name} in {period}.",
                tenant_id=tenant_id
            )
        )

    cov_summary = calculate_coverage_summary(
        total_relevant_denominator=total_consolidated_revenue,
        covered_items_sum=covered_sum,
        covered_dimension_names=covered_names
    )

    return {
        "results": results,
        "coverage_summary": cov_summary
    }
