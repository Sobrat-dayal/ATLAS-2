"""Exposure Coverage and Unallocated Residual Quality Assessment (Stage 137).

Enforces institutional coverage invariants:
- When reported segments or holdings explain less than 100% of the total denominator,
  the unallocated residual is explicitly measured and preserved.
- Rescaling or normalizing incomplete disclosures to sum to 100% is strictly prohibited.
"""

from decimal import Decimal
from typing import List, Optional
from atlas.exposure.domain import CoverageStatus, ExposureCoverageSummary


def calculate_coverage_summary(
    total_relevant_denominator: Decimal,
    covered_items_sum: Decimal,
    covered_dimension_names: List[str],
    uncovered_dimension_names: Optional[List[str]] = None,
    tolerance: Decimal = Decimal("0.001")
) -> ExposureCoverageSummary:
    """Calculate explicit coverage ratio and unallocated residual."""
    if total_relevant_denominator <= Decimal("0.0"):
        return ExposureCoverageSummary(
            total_relevant_denominator=Decimal("0.0"),
            eligible_covered_denominator=Decimal("0.0"),
            coverage_ratio=Decimal("0.0"),
            coverage_status=CoverageStatus.UNKNOWN,
            notes=["Denominator is zero or negative; coverage cannot be computed."]
        )

    coverage_ratio = (covered_items_sum / total_relevant_denominator).quantize(Decimal("0.0001"))
    unallocated_amount = total_relevant_denominator - covered_items_sum
    unallocated_pct = (unallocated_amount / total_relevant_denominator * Decimal("100.0")).quantize(Decimal("0.01"))

    notes = []
    if abs(unallocated_amount) <= tolerance:
        status = CoverageStatus.COMPLETE
        unallocated_amount = Decimal("0.0")
        unallocated_pct = Decimal("0.0")
    elif unallocated_amount > Decimal("0.0"):
        status = CoverageStatus.PARTIAL
        notes.append(
            f"Reported components account for {(coverage_ratio * 100).quantize(Decimal('0.1'))}% of the verified denominator. "
            f"An unallocated residual of {unallocated_amount} ({unallocated_pct}%) remains undisclosed or unassigned."
        )
    else:
        # Covered exceeds denominator (e.g. gross items or overlapping segments)
        status = CoverageStatus.PARTIAL
        notes.append(
            f"Covered items sum ({covered_items_sum}) exceeds denominator ({total_relevant_denominator}). "
            "Segments may reflect intercompany transfers, gross volumes, or non-reconciled categories."
        )

    return ExposureCoverageSummary(
        total_relevant_denominator=total_relevant_denominator,
        eligible_covered_denominator=covered_items_sum,
        coverage_ratio=coverage_ratio,
        covered_dimensions=covered_dimension_names,
        uncovered_dimensions=uncovered_dimension_names or [],
        unallocated_residual_amount=unallocated_amount,
        unallocated_residual_percentage=unallocated_pct,
        coverage_status=status,
        notes=notes
    )

