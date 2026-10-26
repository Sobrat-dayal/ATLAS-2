"""Company Earnings Intelligence Package (Stage 84).

Exports domain models, enums, errors, schemas, calculations, repository, and service.
"""

from atlas.companies.earnings.calculator import (
    calculate_eps_surprise,
    calculate_revenue_surprise,
    format_eps,
    format_percentage,
    format_revenue,
)
from atlas.companies.earnings.enums import (
    AccountingBasis,
    EarningsEventStatus,
    EarningsEventType,
    EarningsPeriodType,
    EPSBasis,
    GuidanceMetricType,
    GuidanceStatus,
    MarketSession,
    SurpriseClassification,
    TranscriptStatus,
)
from atlas.companies.earnings.errors import (
    EarningsError,
    EarningsEventNotFoundError,
    EarningsPeriodUnavailableError,
    EstimateVintageUnavailableError,
    IncompatibleEarningsBasisError,
    TranscriptNotEntitledError,
)
from atlas.companies.earnings.models import (
    ConsensusSnapshot,
    EarningsActual,
    EarningsCall,
    EarningsEvent,
    EarningsSurprise,
    ManagementGuidance,
)
from atlas.companies.earnings.repository import (
    CompanyEarningsRepository,
    clear_earnings_store,
)
from atlas.companies.earnings.schemas import (
    CompanyEarningsOverviewDTO,
    ConsensusSnapshotDTO,
    EarningsActualDTO,
    EarningsCallDTO,
    EarningsCallsResponseDTO,
    EarningsEventDTO,
    EarningsEventsResponseDTO,
    EarningsHistoryResponseDTO,
    EarningsSurpriseDTO,
    GuidanceResponseDTO,
    ManagementGuidanceDTO,
    QuarterlyEarningsItemDTO,
)
from atlas.companies.earnings.service import CompanyEarningsService

__all__ = [
    # Enums
    "AccountingBasis",
    "EarningsEventStatus",
    "EarningsEventType",
    "EarningsPeriodType",
    "EPSBasis",
    "GuidanceMetricType",
    "GuidanceStatus",
    "MarketSession",
    "SurpriseClassification",
    "TranscriptStatus",
    # Errors
    "EarningsError",
    "EarningsEventNotFoundError",
    "EarningsPeriodUnavailableError",
    "EstimateVintageUnavailableError",
    "IncompatibleEarningsBasisError",
    "TranscriptNotEntitledError",
    # Calculator
    "calculate_eps_surprise",
    "calculate_revenue_surprise",
    "format_eps",
    "format_percentage",
    "format_revenue",
    # Models
    "ConsensusSnapshot",
    "EarningsActual",
    "EarningsCall",
    "EarningsEvent",
    "EarningsSurprise",
    "ManagementGuidance",
    # Repository & Service
    "CompanyEarningsRepository",
    "CompanyEarningsService",
    "clear_earnings_store",
    # Schemas
    "CompanyEarningsOverviewDTO",
    "ConsensusSnapshotDTO",
    "EarningsActualDTO",
    "EarningsCallDTO",
    "EarningsCallsResponseDTO",
    "EarningsEventDTO",
    "EarningsEventsResponseDTO",
    "EarningsHistoryResponseDTO",
    "EarningsSurpriseDTO",
    "GuidanceResponseDTO",
    "ManagementGuidanceDTO",
    "QuarterlyEarningsItemDTO",
]
