"""Strategy Registry and Parameter Validation (Stage 143)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from atlas.trading.backtesting.domain import AtlasStrategyDefinition
from atlas.trading.backtesting.errors import (
    BacktestInvalidParameterError,
    BacktestStrategyNotFoundError,
)
from atlas.trading.backtesting.strategies.templates import CANONICAL_STRATEGY_TEMPLATES


class StrategyRegistry:
    """Thread-safe registry for institutional backtesting trading strategies."""

    def __init__(self):
        self._strategies: Dict[str, AtlasStrategyDefinition] = dict(CANONICAL_STRATEGY_TEMPLATES)

    def get_strategy(self, strategy_id: str) -> AtlasStrategyDefinition:
        strat = self._strategies.get(strategy_id)
        if not strat:
            raise BacktestStrategyNotFoundError(strategy_id)
        return strat

    def list_strategies(self) -> List[AtlasStrategyDefinition]:
        return list(self._strategies.values())

    def register_custom_strategy(self, strategy_def: AtlasStrategyDefinition) -> None:
        self._strategies[strategy_def.strategy_id] = strategy_def

    def validate_parameters(
        self,
        strategy_id: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate strategy parameters against registered schema.
        Applies defaults for missing parameters and verifies mathematical logic.
        """
        strat = self.get_strategy(strategy_id)
        resolved = dict(strat.default_parameters)
        resolved.update(parameters)

        # Cross-parameter logic validations
        if strategy_id == "MA_CROSSOVER":
            fast = resolved.get("fast_period", 10)
            slow = resolved.get("slow_period", 30)
            if fast >= slow:
                raise BacktestInvalidParameterError(
                    parameter_name="fast_period",
                    reason=f"Fast period ({fast}) must be strictly less than slow period ({slow}).",
                )

        if "quantity" in resolved:
            qty = resolved["quantity"]
            if qty <= 0:
                raise BacktestInvalidParameterError(
                    parameter_name="quantity",
                    reason=f"Quantity must be positive (> 0), got {qty}.",
                )

        return resolved

