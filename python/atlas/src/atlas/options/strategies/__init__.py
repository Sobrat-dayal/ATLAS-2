"""Options strategy package (Stage 141)."""

from .breakevens import calculate_strategy_breakevens_and_bounds
from .opening_cashflow import calculate_opening_cash_flow
from .payoff import (
    calculate_leg_expiration_payoff,
    calculate_strategy_expiration_payoff,
    generate_payoff_curve,
)
from .templates import CANONICAL_TEMPLATES, StrategyTemplateDefinition
from .validation import validate_strategy_legs

__all__ = [
    "calculate_strategy_breakevens_and_bounds",
    "calculate_opening_cash_flow",
    "calculate_leg_expiration_payoff",
    "calculate_strategy_expiration_payoff",
    "generate_payoff_curve",
    "CANONICAL_TEMPLATES",
    "StrategyTemplateDefinition",
    "validate_strategy_legs",
]
