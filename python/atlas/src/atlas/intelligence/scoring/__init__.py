"""ATLAS Intelligence Scoring & Prioritization Engine (Stage 139)."""

from .domain import (
    AtlasIntelligenceScore,
    FactorContribution,
    FactorTransformationMethod,
    GovernanceStatus,
    MissingValuePolicy,
    RankedItem,
    ScoreLineageRecord,
    ScoreObjectiveId,
    ScoreScale,
    ScoreStatus,
    ScoreUncertaintyMetadata,
    ScoringEvaluationManifest,
)
from .errors import (
    ScoringDomainError,
    ScoringEligibilityError,
    ScoringLookAheadViolationError,
    ScoringModelNotFoundError,
    ScoringModelValidationError,
    ScoringObjectiveNotFoundError,
    ScoringPolicyNotFoundError,
    ScoringQuotaExceededError,
    ScoringSourceEntitlementError,
    ScoringTenantAccessDeniedError,
    ScoringUnauthorizedActivationError,
)
from .evaluation import CalibrationMetrics, ModelEvaluator, RankingMetrics
from .factors import FactorMath, compute_factor_contribution
from .features import CANONICAL_FEATURES, FeatureDefinition, FeatureExtractor, IntelligenceFeatureSnapshot
from .governance import ModelGovernanceManager, ScoringGovernanceAuditRecord
from .models import CANONICAL_MODELS, ModelRegistry, ScoringModelDefinition
from .monitoring import ScoringMonitor, ScoringTelemetrySummary
from .objectives import CANONICAL_OBJECTIVES, ScoringObjectiveDefinition, ScoringObjectiveRegistry
from .policies import (
    CANONICAL_POLICIES,
    IntelligenceScoringPolicy,
    ScoringFactorWeightConfig,
    ScoringPolicyRegistry,
)
from .service import (
    AtlasScoringService,
    ModelComparisonResponse,
    ScoringCapabilitiesResponse,
)

__all__ = [
    # Domain Models
    "AtlasIntelligenceScore",
    "FactorContribution",
    "FactorTransformationMethod",
    "GovernanceStatus",
    "MissingValuePolicy",
    "RankedItem",
    "ScoreLineageRecord",
    "ScoreObjectiveId",
    "ScoreScale",
    "ScoreStatus",
    "ScoreUncertaintyMetadata",
    "ScoringEvaluationManifest",
    # Errors
    "ScoringDomainError",
    "ScoringEligibilityError",
    "ScoringLookAheadViolationError",
    "ScoringModelNotFoundError",
    "ScoringModelValidationError",
    "ScoringObjectiveNotFoundError",
    "ScoringPolicyNotFoundError",
    "ScoringQuotaExceededError",
    "ScoringSourceEntitlementError",
    "ScoringTenantAccessDeniedError",
    "ScoringUnauthorizedActivationError",
    # Service & Registries
    "AtlasScoringService",
    "ModelComparisonResponse",
    "ScoringCapabilitiesResponse",
    "ModelRegistry",
    "ScoringModelDefinition",
    "ScoringObjectiveRegistry",
    "ScoringObjectiveDefinition",
    "ScoringPolicyRegistry",
    "IntelligenceScoringPolicy",
    "ScoringFactorWeightConfig",
    "FeatureDefinition",
    "FeatureExtractor",
    "IntelligenceFeatureSnapshot",
    "ModelGovernanceManager",
    "ScoringGovernanceAuditRecord",
    "ModelEvaluator",
    "RankingMetrics",
    "CalibrationMetrics",
    "ScoringMonitor",
    "ScoringTelemetrySummary",
    "compute_factor_contribution",
    "FactorMath",
    "CANONICAL_FEATURES",
    "CANONICAL_OBJECTIVES",
    "CANONICAL_MODELS",
    "CANONICAL_POLICIES",
]

