"""Derivative Exposure Domain Handler (Stage 137).

Enforces institutional derivative exposure invariants:
- Option exposures measured via delta-equivalent dollar exposure:
  Contracts * Multiplier * Underlying_Price * Delta.
- Strictly avoids fabricating higher-order Greeks without explicit model parameters.
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
from atlas.exposure.calculations.scenarios import calculate_option_delta_equivalent


def analyze_option_delta_exposure(
    run_id: str,
    portfolio_ref: CanonicalGraphNodeRef,
    option_ref: CanonicalGraphNodeRef,
    underlying_ref: CanonicalGraphNodeRef,
    contracts: Decimal,
    multiplier: Decimal,
    underlying_price: Decimal,
    delta: Decimal,
    currency: str = "USD"
) -> AtlasExposureResult:
    """Compute verified delta-equivalent exposure for an option position."""
    delta_equiv = calculate_option_delta_equivalent(contracts, multiplier, underlying_price, delta, currency)

    return AtlasExposureResult(
        exposure_id=f"exp-deriv-{run_id}-{option_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=portfolio_ref,
        target_entity_ref=underlying_ref,
        exposure_domain=ExposureDomain.DERIVATIVES,
        exposure_type=ExposureType.DERIVATIVE_DELTA_EQUIVALENT_EXPOSURE,
        exposure_measure_id="DERIVATIVE_DELTA_EQUIVALENT_V1",
        evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
        relationship_strength=ExposureRelationshipStrength.DERIVED_FROM_VERIFIED_DATA,
        amount=delta_equiv,
        currency=currency,
        unit="CURRENCY",
        percentage=None,
        numerator_value=delta_equiv,
        denominator_value=contracts * multiplier * underlying_price,
        denominator_reference="Gross Notional Exposure",
        calculation_method_id="BLACK_SCHOLES_DELTA_MAPPING",
        coverage_status=CoverageStatus.COMPLETE,
        uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
        explanation=(
            f"Option position {option_ref.canonical_name} ({contracts} contracts, multiplier {multiplier}, "
            f"delta {delta}) on underlying {underlying_ref.canonical_name} at {underlying_price} {currency} "
            f"yields a delta-equivalent exposure of {delta_equiv} {currency}."
        )
    )
