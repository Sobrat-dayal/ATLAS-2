"""Server-controlled allowlisted Technical Indicator Registry (Stage 69).

Manages registered indicator definitions and their deterministic calculator instances.
Rejects duplicate registrations, unknown indicators, and unsupported versions.
Never executes arbitrary user-supplied scripts or unvalidated code.
"""

import logging
from typing import Dict, List, Tuple

from .calculators.base import IndicatorCalculator
from .calculators.sma import SmaCalculator
from .models import IndicatorDefinition

logger = logging.getLogger(__name__)


class IndicatorRegistry:
    """Central registry of approved and verified technical indicator implementations."""

    def __init__(self) -> None:
        # Key: (indicator_id, version) -> (definition, calculator)
        self._entries: Dict[Tuple[str, int], Tuple[IndicatorDefinition, IndicatorCalculator]] = {}

    def register(self, calculator: IndicatorCalculator) -> None:
        """Register a validated indicator calculator instance.

        Raises:
            ValueError: If an entry with identical indicator_id and version already exists.
        """
        defn = calculator.definition
        key = (defn.indicator_id, defn.version)
        if key in self._entries:
            raise ValueError(
                f"Duplicate registration: indicator '{defn.indicator_id}' "
                f"version {defn.version} is already registered."
            )
        self._entries[key] = (defn, calculator)
        logger.info(
            f"Registered technical indicator: {defn.indicator_id} v{defn.version} "
            f"({defn.display_name})"
        )

    def get(
        self, indicator_id: str, version: int = 1
    ) -> Tuple[IndicatorDefinition, IndicatorCalculator]:
        """Retrieve definition and calculator for a given ID and version.

        Raises:
            KeyError: If the indicator ID and version are not found.
        """
        key = (indicator_id, version)
        if key not in self._entries:
            # Check if indicator exists under different versions to provide specific error
            existing_versions = [v for (iid, v) in self._entries.keys() if iid == indicator_id]
            if existing_versions:
                raise KeyError(
                    f"Unsupported version {version} for indicator '{indicator_id}'. "
                    f"Available versions: {existing_versions}"
                )
            raise KeyError(
                f"Unknown indicator '{indicator_id}'. Not found in allowlisted registry."
            )
        return self._entries[key]

    def list_definitions(self) -> List[IndicatorDefinition]:
        """Return all registered indicator definitions sorted by indicator_id."""
        return [
            entry[0] for entry in sorted(self._entries.values(), key=lambda e: e[0].indicator_id)
        ]

    def is_registered(self, indicator_id: str, version: int = 1) -> bool:
        """Check if an indicator ID and version are registered."""
        return (indicator_id, version) in self._entries


# Initialize standard registry with reference SMA
default_indicator_registry = IndicatorRegistry()
default_indicator_registry.register(SmaCalculator())
