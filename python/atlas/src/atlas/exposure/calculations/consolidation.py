"""Corporate Group Consolidation & Double-Counting Elimination (Stage 137).

Enforces institutional accounting invariants:
- A consolidated parent revenue ($100M) already encompasses its consolidated subsidiaries ($30M).
  Summing parent consolidated revenue with subsidiary revenue is strictly prohibited (DoubleCountingError).
- Minority ownership (e.g. 40% affiliate) follows Equity Method or Non-Consolidated basis:
  never automatically adds 40% of affiliate revenue to parent group revenue.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from atlas.exposure.domain import ConsolidationBasis
from atlas.exposure.errors import DoubleCountingError


class EntityFinancialRecord:
    def __init__(
        self,
        entity_id: str,
        name: str,
        revenue: Decimal,
        currency: str,
        period: str,
        consolidation_basis: ConsolidationBasis,
        parent_entity_id: Optional[str] = None,
        ownership_percentage: Optional[Decimal] = None
    ):
        self.entity_id = entity_id
        self.name = name
        self.revenue = revenue
        self.currency = currency
        self.period = period
        self.consolidation_basis = consolidation_basis
        self.parent_entity_id = parent_entity_id
        self.ownership_percentage = ownership_percentage


def calculate_group_consolidated_revenue(
    records: List[EntityFinancialRecord],
    parent_id: str
) -> Dict[str, any]:
    """Calculate verified corporate group consolidated revenue without double-counting."""
    parent_record = next((r for r in records if r.entity_id == parent_id), None)
    if not parent_record:
        raise ValueError(f"Parent entity {parent_id} not found in records.")

    if parent_record.consolidation_basis == ConsolidationBasis.CONSOLIDATED:
        # Parent reported consolidated revenue is already the unified total!
        # Do NOT add subsidiary revenues.
        subsidiaries = [r for r in records if r.parent_entity_id == parent_id]
        
        return {
            "group_revenue": parent_record.revenue,
            "currency": parent_record.currency,
            "period": parent_record.period,
            "consolidation_basis": ConsolidationBasis.CONSOLIDATED.value,
            "consolidated_parent_id": parent_id,
            "included_subsidiary_count": len(subsidiaries),
            "eliminated_double_count_amount": sum((s.revenue for s in subsidiaries if s.consolidation_basis == ConsolidationBasis.CONSOLIDATED), Decimal("0.0")),
            "note": "Reported parent consolidated revenue already includes consolidated subsidiaries. Subsidiary amounts were eliminated to prevent double-counting."
        }

    # If parent is standalone unconsolidated, check whether explicit consolidation is required
    raise DoubleCountingError(
        f"Parent {parent_id} is marked {parent_record.consolidation_basis.value}; cannot combine without verified intercompany elimination ledger."
    )
