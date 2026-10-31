"""Strategy Domain Models for Quant Strategy Engine (Stage 142)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from atlas.options.domain import PayoffCoordinate
from atlas.options.quant.domain import (
    PreExpirationValuationPoint,
    QuantModelGreeks,
    QuantStrategyLeg,
)


@dataclass
class QuantStrategyDefinition:
    """Canonical multi-leg options strategy definition."""

    strategy_id: str
    owner_id: str
    title: str
    underlying_symbol: str
    legs: List[QuantStrategyLeg]
    pricing_model_id: str = "BLACK_SCHOLES_MERTON"
    evaluation_date: str = ""
    total_fees: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    tenant_id: str = "default_tenant"
    is_private: bool = True


@dataclass
class StrategyValuationResult:
    """Comprehensive analytical valuation output for a multi-leg strategy."""

    strategy_name: str
    underlying_symbol: str
    evaluation_date: str
    legs: List[QuantStrategyLeg]
    net_opening_cash_flow: float
    is_net_debit: bool
    total_estimated_fees: float
    breakevens: List[float]
    max_profit: Optional[float]
    max_loss: Optional[float]
    is_unbounded_profit: bool
    is_unbounded_loss: bool
    expiration_payoff_curve: List[PayoffCoordinate]
    pre_expiration_curve: List[PreExpirationValuationPoint]
    aggregate_greeks: QuantModelGreeks
    risk_warnings: List[str]
    disclaimers: Dict[str, str]
    is_multi_expiration: bool = False
    calculation_version: str = "142.1.0"

