"""Supply Chain Dependency Domain Handler (Stage 137).

Enforces institutional supply chain invariants:
- Documented customer/supplier commercial ties are verified qualitative relationships.
- When filings disclose a commercial relationship (e.g., Company A is customer of Company B)
  WITHOUT a numerical contract value, the relationship is recorded as verified, but the monetary
  amount is strictly UNAVAILABLE (None). Fabricating contract percentages is prohibited.
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


def analyze_supply_chain_relationship(
    run_id: str,
    subject_ref: CanonicalGraphNodeRef,
    partner_ref: CanonicalGraphNodeRef,
    role: str,  # "SUPPLIER" or "CUSTOMER"
    disclosed_contract_amount: Optional[Decimal] = None,
    disclosed_revenue_share_pct: Optional[Decimal] = None,
    currency: str = "USD",
    source_filing: str = "10-K Item 1 Business"
) -> AtlasExposureResult:
    """Record supply chain exposure adhering strictly to disclosure boundaries."""
    if disclosed_contract_amount is not None:
        evidence = ExposureEvidenceClass.REPORTED
        amount = disclosed_contract_amount
        percentage = disclosed_revenue_share_pct
        strength = ExposureRelationshipStrength.DIRECT_REPORTED
        explanation = f"Disclosed {role.lower()} relationship with {partner_ref.canonical_name}: {amount} {currency} ({percentage}%)."
    else:
        # Qualitative relationship only - no numerical fabrication allowed!
        evidence = ExposureEvidenceClass.SOURCE_REPORTED_QUALITATIVE
        amount = None
        percentage = None
        strength = ExposureRelationshipStrength.INDIRECT_DOCUMENTED
        explanation = (
            f"Documented {role.lower()} relationship between {subject_ref.canonical_name} and {partner_ref.canonical_name} "
            f"in {source_filing}. Specific commercial contract value or percentage is not publicly disclosed (UNAVAILABLE)."
        )

    return AtlasExposureResult(
        exposure_id=f"exp-sc-{run_id}-{partner_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=subject_ref,
        target_entity_ref=partner_ref,
        exposure_domain=ExposureDomain.SUPPLY_CHAIN,
        exposure_type=ExposureType.SUPPLY_CHAIN_DEPENDENCY,
        exposure_measure_id="SUPPLY_CHAIN_QUALITATIVE_V1",
        evidence_class=evidence,
        relationship_strength=strength,
        amount=amount,
        currency=currency if amount is not None else None,
        unit="CURRENCY" if amount is not None else "QUALITATIVE",
        percentage=percentage,
        calculation_method_id="QUALITATIVE_DOCUMENTATION",
        coverage_status=CoverageStatus.COMPLETE if amount is not None else CoverageStatus.PARTIAL,
        uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC if amount is not None else UncertaintyClass.SOURCE_INCOMPLETE,
        explanation=explanation
    )
