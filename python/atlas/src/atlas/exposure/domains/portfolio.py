"""Portfolio Exposure Domain Handler (Stage 137).

Enforces institutional portfolio invariants:
- Long/short signed calculations (Net vs Gross exposure).
- Fund look-through with cycle detection.
- Discloses uncovered/unclassified holdings without fabrication.
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
from atlas.exposure.calculations.portfolio import calculate_portfolio_exposures, PortfolioPosition
from atlas.exposure.quality.coverage import calculate_coverage_summary


def analyze_portfolio_holdings(
    run_id: str,
    portfolio_ref: CanonicalGraphNodeRef,
    positions: List[PortfolioPosition],
    nav: Optional[Decimal] = None,
    currency: str = "USD",
    as_of: Optional[datetime] = None,
    tenant_id: Optional[str] = None
) -> Dict[str, any]:
    """Analyze portfolio holdings returning position weights, gross/net exposures, and sector breakdowns."""
    summary = calculate_portfolio_exposures(positions, stated_nav=nav)
    results: List[AtlasExposureResult] = []

    # Position results
    for pos in positions:
        weight_pct = (pos.market_value / summary.nav * Decimal("100.0")).quantize(Decimal("0.01"))
        
        target_ref = CanonicalGraphNodeRef(
            node_type=GraphNodeType.FINANCIAL_INSTRUMENT,
            entity_id=pos.instrument_id,
            canonical_name=pos.symbol,
            sector=pos.sector,
            country_code=pos.country_of_risk
        )

        results.append(
            AtlasExposureResult(
                exposure_id=f"exp-pos-{run_id}-{pos.position_id}",
                analysis_run_id=run_id,
                subject_entity_ref=portfolio_ref,
                target_entity_ref=target_ref,
                exposure_domain=ExposureDomain.PORTFOLIO,
                exposure_type=ExposureType.PORTFOLIO_WEIGHT_EXPOSURE,
                exposure_measure_id="PORTFOLIO_NAV_WEIGHT_V1",
                evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
                relationship_strength=ExposureRelationshipStrength.DIRECT_MEASURED,
                amount=pos.market_value,
                currency=currency,
                unit="PERCENT",
                percentage=weight_pct,
                numerator_value=pos.market_value,
                denominator_value=summary.nav,
                denominator_reference=f"Portfolio NAV ({summary.nav} {currency})",
                calculation_method_id="DETERMINISTIC_VALUATION_RATIO",
                coverage_status=CoverageStatus.COMPLETE,
                coverage_ratio=abs(pos.market_value / summary.nav).quantize(Decimal("0.0001")),
                uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
                explanation=f"Position {pos.symbol} valued at {pos.market_value} {currency} represents {weight_pct}% of NAV.",
                tenant_id=tenant_id
            )
        )

    # Sector breakdown results
    for sec_name, sec_pct in summary.sector_weights.items():
        sec_ref = CanonicalGraphNodeRef(
            node_type=GraphNodeType.SECTOR,
            entity_id=sec_name.upper().replace(" ", "_"),
            canonical_name=sec_name
        )
        sec_val = summary.nav * (sec_pct / Decimal("100.0"))
        results.append(
            AtlasExposureResult(
                exposure_id=f"exp-sec-{run_id}-{sec_name.replace(' ', '_')}",
                analysis_run_id=run_id,
                subject_entity_ref=portfolio_ref,
                target_entity_ref=sec_ref,
                exposure_domain=ExposureDomain.SECTOR,
                exposure_type=ExposureType.SECTOR_ALLOCATION_EXPOSURE,
                exposure_measure_id="PORTFOLIO_NAV_WEIGHT_V1",
                evidence_class=ExposureEvidenceClass.DETERMINISTICALLY_CALCULATED,
                relationship_strength=ExposureRelationshipStrength.DERIVED_FROM_VERIFIED_DATA,
                amount=sec_val,
                currency=currency,
                unit="PERCENT",
                percentage=sec_pct,
                numerator_value=sec_val,
                denominator_value=summary.nav,
                denominator_reference=f"Portfolio NAV ({summary.nav} {currency})",
                calculation_method_id="SECTOR_SUMMATION",
                coverage_status=CoverageStatus.COMPLETE if summary.uncovered_sector_value == Decimal("0.0") else CoverageStatus.PARTIAL,
                coverage_ratio=summary.sector_coverage_ratio,
                uncertainty_class=UncertaintyClass.VERIFIED_DETERMINISTIC,
                explanation=f"Sector {sec_name} represents {sec_pct}% of portfolio NAV.",
                tenant_id=tenant_id
            )
        )

    cov_summary = calculate_coverage_summary(
        total_relevant_denominator=summary.nav,
        covered_items_sum=summary.covered_sector_value,
        covered_dimension_names=list(summary.sector_weights.keys()),
        uncovered_dimension_names=["UNCLASSIFIED_HOLDINGS"] if summary.uncovered_sector_value > Decimal("0.0") else []
    )

    return {
        "results": results,
        "summary": summary,
        "coverage_summary": cov_summary
    }

