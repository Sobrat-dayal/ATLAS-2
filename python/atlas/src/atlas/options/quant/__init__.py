"""ATLAS QuantLib Derivative Pricing & Options Strategy Engine (Stage 142)."""

from .domain import (
    GreekUnitConvention,
    MarketInputSnapshot,
    OptionPricingResult,
    PreExpirationValuationPoint,
    PricingModelFamily,
    QuantModelGreeks,
    QuantPricingDiagnostics,
    QuantPricingModelDefinition,
    QuantStrategyLeg,
    STAGE_142_DISCLAIMERS,
    StrategyComparisonItem,
)
from .errors import (
    QuantContractNotFoundError,
    QuantDomainError,
    QuantEntitlementRequiredError,
    QuantEvaluationDateError,
    QuantInvalidVolatilitySurfaceError,
    QuantLibError,
    QuantModelIncompatibleError,
    QuantMultiTenantAccessDeniedError,
    QuantNumericalConvergenceError,
    QuantResourceQuotaExceededError,
    QuantStaleQuoteError,
)
from .quantlib.adapter import QuantLibAdapter
from .quantlib.context import isolated_quantlib_context
from .quantlib.dates import from_ql_date, to_ql_date
from .service import AtlasQuantOptionsService
from .strategies.models import QuantStrategyDefinition, StrategyValuationResult
from .strategies.templates import CANONICAL_25_TEMPLATES

__all__ = [
    "AtlasQuantOptionsService",
    "QuantLibAdapter",
    "isolated_quantlib_context",
    "to_ql_date",
    "from_ql_date",
    "PricingModelFamily",
    "GreekUnitConvention",
    "QuantPricingModelDefinition",
    "MarketInputSnapshot",
    "QuantModelGreeks",
    "QuantPricingDiagnostics",
    "OptionPricingResult",
    "QuantStrategyLeg",
    "QuantStrategyDefinition",
    "StrategyValuationResult",
    "StrategyComparisonItem",
    "PreExpirationValuationPoint",
    "CANONICAL_25_TEMPLATES",
    "STAGE_142_DISCLAIMERS",
    "QuantDomainError",
    "QuantLibError",
    "QuantModelIncompatibleError",
    "QuantContractNotFoundError",
    "QuantEvaluationDateError",
    "QuantNumericalConvergenceError",
    "QuantStaleQuoteError",
    "QuantInvalidVolatilitySurfaceError",
    "QuantMultiTenantAccessDeniedError",
    "QuantEntitlementRequiredError",
    "QuantResourceQuotaExceededError",
]
