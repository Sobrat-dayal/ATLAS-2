"""Options Strategy Leg Validation and Institutional Invariants (Stage 141).

Guarantees:
- Rejects multi-expiration strategies from single-expiration payoff calculations (Stage 142 boundary)
- Rejects nonstandard adjusted deliverable contracts from vanilla payoff formulas
- Enforces underlying consistency and valid quantities
"""

from __future__ import annotations

from typing import List
from atlas.options.contracts.registry import OptionContractRegistry
from atlas.options.domain import (
    ContractAdjustmentStatus,
    OptionStrategyLeg,
)
from atlas.options.errors import (
    OptionsAdjustedDeliverableUnsupportedError,
    OptionsContractNotFoundError,
    OptionsInvalidStrategyLegError,
    OptionsMultiExpirationPayoffUnsupportedError,
)


def validate_strategy_legs(
    legs: List[OptionStrategyLeg],
    contract_registry: OptionContractRegistry,
) -> None:
    """Validate strategy legs for analytical compatibility."""
    if not legs:
        raise OptionsInvalidStrategyLegError(0, "Strategy must contain at least one option leg.")

    underlyings = set()
    expirations = set()

    for idx, leg in enumerate(legs, start=1):
        if leg.quantity <= 0:
            raise OptionsInvalidStrategyLegError(idx, "Contract quantity must be a positive integer greater than zero.")

        if leg.entry_premium < 0.0:
            raise OptionsInvalidStrategyLegError(idx, "Entry premium cannot be negative.")

        contract = contract_registry.get_contract(leg.contract_id)
        if not contract:
            raise OptionsContractNotFoundError(leg.contract_id)

        # 1. Nonstandard adjusted contract check (Fixture G)
        if contract.adjustment_status == ContractAdjustmentStatus.ADJUSTED_CORPORATE_ACTION:
            raise OptionsAdjustedDeliverableUnsupportedError(
                contract_id=leg.contract_id,
                deliverable_summary=contract.deliverable.summary,
                message=(
                    f"Option contract '{leg.contract_id}' has nonstandard corporate-action adjusted deliverables "
                    f"({contract.deliverable.summary}). Standard vanilla expiration payoff is unsupported."
                ),
            )

        underlyings.add(contract.underlying_symbol.upper())
        expirations.add(contract.expiration_date)

    # 2. Underlying consistency check
    if len(underlyings) > 1:
        raise OptionsInvalidStrategyLegError(0, f"All strategy legs must share the same underlying asset. Found: {list(underlyings)}")

    # 3. Multi-expiration calendar check (Fixture M)
    if len(expirations) > 1:
        raise OptionsMultiExpirationPayoffUnsupportedError(
            expirations=sorted(list(expirations)),
            message=(
                "Strategy contains legs with different expiration dates. Single-expiration payoff curves "
                "cannot accurately represent calendar or diagonal spreads without time-dependent mark-to-market pricing (reserved for Stage 142)."
            ),
        )
