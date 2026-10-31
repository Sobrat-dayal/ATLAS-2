"""Corporate Group Exposure Domain Handler (Stage 137).

Enforces corporate consolidation invariants:
- Parent consolidated financials are authoritative.
- Never sums parent consolidated totals with subsidiary standalone filings.
- Explicitly handles minority ownership (Equity Method vs Consolidated).
"""

from decimal import Decimal
from typing import Dict, List, Optional
from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.exposure.domain import (
    AtlasExposureResult,
    ConsolidationBasis,
    CoverageStatus,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureRelationshipStrength,
    ExposureType,
    UncertaintyClass,
)
from atlas.exposure.calculations.consolidation import EntityFinancialRecord, calculate_group_consolidated_revenue


def analyze_corporate_group(
    run_id: str,
    parent_ref: CanonicalGraphNodeRef,
    records: List[EntityFinancialRecord],
    currency: str = "USD"
) -> Dict[str, any]:
    """Analyze corporate group structure eliminating double-counting."""
    group_data = calculate_group_consolidated_revenue(records, parent_ref.entity_id)

    result = AtlasExposureResult(
        exposure_id=f"exp-corp-{run_id}-{parent_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=parent_ref,
        target_entity_ref=parent_ref,
        exposure_domain=ExposureDomain.CORPORATE_GROUP,
        exposure_type=ExposureType.CORPORATE_GROUP_EXPOSURE,
        exposure_measure_id="CORP_GROUP_CONSOLIDATED_REV_V1",
        evidence_class=ExposureEvidenceClass.REPORTED,
        relationship_strength=ExposureRelationshipStrength.DIRECT_REPORTED,
        amount=group_data["group_revenue"],
        currency=currency,
        unit="CURRENCY",
        percentage=Decimal("100.0"),
        numerator_value=group_data["group_revenue"],
        denominator_value=group_data["group_revenue"],
        calculation_method_id="CONSOLIDATED_EXTRACTION",
        coverage_status=CoverageStatus.COMPLETE,
        uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
        explanation=group_data["note"],
        warnings=[f"Eliminated {group_data['eliminated_double_count_amount']} {currency} in subsidiary revenues to prevent double-counting."]
    )

    return {
        "results": [result],
        "group_data": group_data
    }
