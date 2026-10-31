"""Macroeconomic & Interest Rate Domain Handler (Stage 137).

Enforces institutional macro invariants:
- First-order local sensitivity using DV01 (-DV01 * delta_bps)
- Strictly labeled as scenario linear approximation, not realized outcome.
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
from atlas.exposure.calculations.scenarios import calculate_dv01_sensitivity


def analyze_dv01_interest_rate_sensitivity(
    run_id: str,
    subject_ref: CanonicalGraphNodeRef,
    rate_benchmark_ref: CanonicalGraphNodeRef,
    dv01_amount: Decimal,
    rate_shift_bps: Decimal,
    currency: str = "USD"
) -> AtlasExposureResult:
    """Calculate first-order interest rate sensitivity labeled as scenario approximation."""
    cond_pnl = calculate_dv01_sensitivity(dv01_amount, rate_shift_bps, currency)

    return AtlasExposureResult(
        exposure_id=f"exp-dv01-{run_id}-{rate_benchmark_ref.entity_id}",
        analysis_run_id=run_id,
        subject_entity_ref=subject_ref,
        target_entity_ref=rate_benchmark_ref,
        exposure_domain=ExposureDomain.MACRO_ECONOMIC,
        exposure_type=ExposureType.INTEREST_RATE_EXPOSURE,
        exposure_measure_id="DV01_RATE_SENSITIVITY_V1",
        evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
        relationship_strength=ExposureRelationshipStrength.ASSUMPTION_DEPENDENT,
        amount=cond_pnl,
        currency=currency,
        unit="CURRENCY",
        percentage=None,
        numerator_value=cond_pnl,
        denominator_value=dv01_amount,
        denominator_reference=f"DV01 ({dv01_amount} {currency}/bp)",
        calculation_method_id="LOCAL_LINEAR_APPROXIMATION",
        coverage_status=CoverageStatus.COMPLETE,
        uncertainty_class=UncertaintyClass.SCENARIO_ASSUMPTION,
        explanation=(
            f"Under a hypothetical interest rate shift of {rate_shift_bps} bps, DV01 of {dv01_amount} {currency}/bp "
            f"yields a first-order local P&L estimate of {cond_pnl} {currency}."
        ),
        limitations_disclaimer="Local linear DV01 approximation only. Ignores convexity, curve twists, and second-order gamma/vega shifts."
    )
