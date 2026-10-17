"""Abstract base class and protocol for Technical Indicator Calculators (Stage 69).

All calculators must:
- Reference an immutable IndicatorDefinition.
- Validate input parameters authoritatively.
- Define explicit lookback requirements.
- Calculate deterministic time-aligned output points.
- Never look ahead into future bars.
- Never output NaN, Infinity, or fake zeros during warmup.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...models import ChartBarDTO
from ..models import (
    IndicatorCalculationResult,
    IndicatorDefinition,
    IndicatorParameterType,
)


class IndicatorCalculator(ABC):
    """Abstract base class for all registered technical indicator calculators."""

    @property
    @abstractmethod
    def definition(self) -> IndicatorDefinition:
        """Return the registered metadata definition for this calculator."""
        pass

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize user-provided parameters against the definition schema.

        Returns a complete parameter dictionary with validated values or authoritative defaults.
        Raises ValueError if any parameter is missing, invalid type, out of bounds, or not allowed.
        """
        normalized: Dict[str, Any] = {}

        for param_def in self.definition.parameters:
            name = param_def.name
            raw_value = params.get(name)

            if raw_value is None:
                if param_def.required:
                    if param_def.default is not None:
                        raw_value = param_def.default
                    else:
                        raise ValueError(
                            f"Missing required parameter '{name}' for indicator "
                            f"'{self.definition.indicator_id}'"
                        )
                else:
                    normalized[name] = param_def.default
                    continue

            # Type checking and conversion
            if param_def.type == IndicatorParameterType.INTEGER:
                if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                    raise ValueError(
                        f"Parameter '{name}' must be an integer, got {type(raw_value).__name__}"
                    )
                int_val = int(raw_value)
                if float(raw_value) != int_val:
                    raise ValueError(f"Parameter '{name}' must be a whole integer, got {raw_value}")
                val = int_val
            elif param_def.type == IndicatorParameterType.DECIMAL:
                if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                    raise ValueError(
                        f"Parameter '{name}' must be numeric, got {type(raw_value).__name__}"
                    )
                val = float(raw_value)
            elif param_def.type == IndicatorParameterType.BOOLEAN:
                if not isinstance(raw_value, bool):
                    raise ValueError(
                        f"Parameter '{name}' must be a boolean, got {type(raw_value).__name__}"
                    )
                val = raw_value
            elif param_def.type == IndicatorParameterType.STRING:
                if not isinstance(raw_value, str):
                    raise ValueError(
                        f"Parameter '{name}' must be a string, got {type(raw_value).__name__}"
                    )
                val = str(raw_value).strip().lower()
            else:
                val = raw_value

            # Min / Max bounds checking
            if param_def.min_value is not None:
                if val < param_def.min_value:
                    raise ValueError(
                        f"Parameter '{name}' value {val} is below minimum allowed "
                        f"{param_def.min_value}"
                    )
            if param_def.max_value is not None:
                if val > param_def.max_value:
                    raise ValueError(
                        f"Parameter '{name}' value {val} exceeds maximum allowed "
                        f"{param_def.max_value}"
                    )

            # Allowed values enumeration checking
            if param_def.allowed_values is not None:
                # normalize strings for comparison if applicable
                allowed_norm = [
                    v.lower() if isinstance(v, str) else v for v in param_def.allowed_values
                ]
                check_val = val.lower() if isinstance(val, str) else val
                if check_val not in allowed_norm:
                    raise ValueError(
                        f"Parameter '{name}' value '{val}' is not in allowed choices: "
                        f"{param_def.allowed_values}"
                    )

            normalized[name] = val

        return normalized

    @abstractmethod
    def get_required_lookback(self, params: Dict[str, Any]) -> int:
        """Return the number of previous constituent bars required for warmup."""
        pass

    @abstractmethod
    def calculate(
        self,
        instance_id: str,
        bars: List[ChartBarDTO],
        params: Dict[str, Any],
        requested_start: Optional[datetime] = None,
        requested_end: Optional[datetime] = None,
    ) -> IndicatorCalculationResult:
        """Compute the indicator series deterministically over chronological bars.

        Args:
            instance_id: Client instance identifier.
            bars: Chronologically sorted historical bars including required warmup.
            params: Validated parameters dictionary.
            requested_start: Optional start of visible chart window.
            requested_end: Optional end of visible chart window.

        Returns:
            IndicatorCalculationResult with time-aligned points and status.
        """
        pass
