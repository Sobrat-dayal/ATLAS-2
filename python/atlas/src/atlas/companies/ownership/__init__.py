"""Company Ownership Intelligence domain package (Stage 85).

Exposes models, calculation tools, services, and schemas for corporate ownership analysis.
"""

from .calculator import (
    calculate_concentration_metrics,
    calculate_ownership_percentage,
    calculate_percentage_points_change,
    calculate_position_percentage_change,
    calculate_shares_change,
    format_indicative_value,
    format_percentage,
    format_shares_count,
)
from .enums import (
    DisclosureType,
    HolderCategory,
    Jurisdiction,
    OwnershipForm,
    PositionChangeStatus,
    PositionType,
)
from .errors import (
    DoubleCountingConflictError,
    IncompatibleDenominatorError,
    OwnershipDataUnavailableError,
    OwnershipEntitlementDeniedError,
    OwnershipError,
    OwnershipHolderNotFoundError,
    OwnershipPeriodUnavailableError,
    OwnershipSecurityNotFoundError,
)
from .models import (
    OwnershipChange,
    OwnershipHolder,
    OwnershipPosition,
    OwnershipSnapshot,
    ShareholdingPatternCategory,
)
from .repository import CompanyOwnershipRepository
from .schemas import (
    BeneficialOwnerDTO,
    BeneficialOwnersResponseDTO,
    CompanyOwnershipOverviewDTO,
    HistoricalOwnershipSnapshotDTO,
    HolderSummaryDTO,
    InsiderHoldingDTO,
    InsiderHoldingsResponseDTO,
    InstitutionalHoldingDTO,
    InstitutionalHoldingsResponseDTO,
    OwnershipChangeDTO,
    OwnershipChangesResponseDTO,
    OwnershipConcentrationDTO,
    OwnershipHistoryResponseDTO,
    OwnershipHoldersResponseDTO,
    OwnershipPositionDTO,
    OwnershipSecuritiesResponseDTO,
    PatternCategoryDTO,
    SecuritySummaryDTO,
    ShareholdingPatternDTO,
)
from .service import CompanyOwnershipService

__all__ = [
    # Enums
    "HolderCategory",
    "OwnershipForm",
    "PositionType",
    "DisclosureType",
    "PositionChangeStatus",
    "Jurisdiction",
    # Errors
    "OwnershipError",
    "OwnershipDataUnavailableError",
    "OwnershipSecurityNotFoundError",
    "OwnershipHolderNotFoundError",
    "IncompatibleDenominatorError",
    "DoubleCountingConflictError",
    "OwnershipPeriodUnavailableError",
    "OwnershipEntitlementDeniedError",
    # Calculator
    "calculate_ownership_percentage",
    "calculate_shares_change",
    "calculate_position_percentage_change",
    "calculate_percentage_points_change",
    "calculate_concentration_metrics",
    "format_shares_count",
    "format_percentage",
    "format_indicative_value",
    # Models
    "OwnershipHolder",
    "OwnershipPosition",
    "ShareholdingPatternCategory",
    "OwnershipSnapshot",
    "OwnershipChange",
    # Repository & Service
    "CompanyOwnershipRepository",
    "CompanyOwnershipService",
    # Schemas
    "HolderSummaryDTO",
    "SecuritySummaryDTO",
    "OwnershipPositionDTO",
    "InstitutionalHoldingDTO",
    "InsiderHoldingDTO",
    "BeneficialOwnerDTO",
    "PatternCategoryDTO",
    "ShareholdingPatternDTO",
    "OwnershipConcentrationDTO",
    "OwnershipChangeDTO",
    "HistoricalOwnershipSnapshotDTO",
    "CompanyOwnershipOverviewDTO",
    "OwnershipHoldersResponseDTO",
    "InstitutionalHoldingsResponseDTO",
    "InsiderHoldingsResponseDTO",
    "BeneficialOwnersResponseDTO",
    "OwnershipHistoryResponseDTO",
    "OwnershipChangesResponseDTO",
    "OwnershipSecuritiesResponseDTO",
]
