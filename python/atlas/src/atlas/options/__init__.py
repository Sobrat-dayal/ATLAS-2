"""ATLAS Options Analytics Subsystem (Stage 141).

Institutional derivatives analytics terminal providing:
- Canonical Options Contract Registry & OCC OSI Symbology
- Nonstandard Deliverables & Corporate Adjustments
- Real-Time & Delayed Chains with Bid-Ask Analytics
- Source-Provided Implied Volatility & Greeks
- Volatility Smile, Skew & Term Structure
- Multi-Leg Strategy Builder & Exact Piecewise Payoff Engine
- Analytical Breakeven Root Finding & Unbounded Risk Detection
- Read-Only Options Portfolio Integration & Tenant Isolation
"""

from .domain import (
    OPTIONS_DISCLAIMERS,
    AtlasOptionContract,
    ContractAdjustmentStatus,
    DeliverableType,
    ExerciseStyle,
    LegSide,
    MoneynessState,
    OptionChainResponse,
    OptionChainRow,
    OptionDeliverable,
    OptionGreeks,
    OptionQuote,
    OptionStrategyAnalysisResult,
    OptionStrategyLeg,
    OptionType,
    PayoffCoordinate,
    QuoteQualityFlag,
    SettlementMethod,
)
from .errors import (
    OptionsAdjustedDeliverableUnsupportedError,
    OptionsContractNotFoundError,
    OptionsDataQualityError,
    OptionsDomainError,
    OptionsEntitlementRequiredError,
    OptionsInvalidStrategyLegError,
    OptionsMultiExpirationPayoffUnsupportedError,
    OptionsSourceUnavailableError,
    OptionsTenantAccessDeniedError,
    OptionsUnderlyingNotFoundError,
)
from .service import AtlasOptionsService

__all__ = [
    "AtlasOptionsService",
    "AtlasOptionContract",
    "OptionQuote",
    "OptionGreeks",
    "OptionDeliverable",
    "OptionChainResponse",
    "OptionChainRow",
    "OptionStrategyLeg",
    "OptionStrategyAnalysisResult",
    "PayoffCoordinate",
    "OptionType",
    "ExerciseStyle",
    "SettlementMethod",
    "MoneynessState",
    "LegSide",
    "DeliverableType",
    "ContractAdjustmentStatus",
    "QuoteQualityFlag",
    "OPTIONS_DISCLAIMERS",
    "OptionsDomainError",
    "OptionsContractNotFoundError",
    "OptionsUnderlyingNotFoundError",
    "OptionsTenantAccessDeniedError",
    "OptionsEntitlementRequiredError",
    "OptionsSourceUnavailableError",
    "OptionsAdjustedDeliverableUnsupportedError",
    "OptionsMultiExpirationPayoffUnsupportedError",
    "OptionsInvalidStrategyLegError",
    "OptionsDataQualityError",
]
