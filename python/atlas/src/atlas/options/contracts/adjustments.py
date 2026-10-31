"""Corporate action adjustment tracking for options contracts (Stage 141).

Maintains adjustment history, OCC adjustment notices, and deliverable reconciliation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from atlas.options.domain import OptionDeliverable


class CorporateOptionAdjustmentRecord(BaseModel):
    """Historical audit record of an option contract corporate adjustment."""
    adjustment_id: str
    effective_date: str  # YYYY-MM-DD
    underlying_symbol: str
    corporate_action_type: str  # "STOCK_SPLIT", "REVERSE_SPLIT", "SPECIAL_DIVIDEND", "SPIN_OFF", "MERGER"
    original_contract_id: str
    adjusted_contract_id: str
    original_multiplier: float
    adjusted_multiplier: float
    original_deliverable: OptionDeliverable
    adjusted_deliverable: OptionDeliverable
    source_memo: str
    details: Dict[str, Any] = Field(default_factory=dict)


class OptionAdjustmentRegistry:
    """In-memory registry of corporate action adjustments on options."""

    def __init__(self):
        self._adjustments: Dict[str, CorporateOptionAdjustmentRecord] = {}

    def register_adjustment(self, record: CorporateOptionAdjustmentRecord) -> None:
        self._adjustments[record.adjustment_id] = record

    def get_adjustment(self, adjustment_id: str) -> Optional[CorporateOptionAdjustmentRecord]:
        return self._adjustments.get(adjustment_id)

    def list_adjustments_for_underlying(self, underlying_symbol: str) -> List[CorporateOptionAdjustmentRecord]:
        clean = underlying_symbol.strip().upper()
        return [
            adj for adj in self._adjustments.values()
            if adj.underlying_symbol.upper() == clean
        ]

