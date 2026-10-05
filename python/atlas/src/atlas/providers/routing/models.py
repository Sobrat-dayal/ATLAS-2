import enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from atlas.providers.types import ProviderDomain

class ProviderRoutingScope(str, enum.Enum):
    USER = "user"
    SYSTEM = "system"

class ProviderSelectionMode(str, enum.Enum):
    EXPLICIT = "explicit"
    POLICY = "policy"

class ProviderEligibilityReason(str, enum.Enum):
    ELIGIBLE = "eligible"
    PROVIDER_NOT_REGISTERED = "provider_not_registered"
    DOMAIN_UNSUPPORTED = "domain_unsupported"
    PROVIDER_DISABLED = "provider_disabled"
    CONFIGURATION_INCOMPLETE = "configuration_incomplete"
    REQUIRED_CREDENTIALS_MISSING = "required_credentials_missing"
    HEALTH_UNHEALTHY = "health_unhealthy"

class ProviderFailureDisposition(str, enum.Enum):
    FALLBACK_ALLOWED = "fallback_allowed"
    FALLBACK_DENIED = "fallback_denied"

class ProviderRoutingCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)
    provider_key: str = Field(...)
    position: int = Field(...)

class ProviderRoutingPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)
    policy_id: str
    scope: ProviderRoutingScope
    owner_principal_id: Optional[str] = None
    domain: ProviderDomain
    enabled: bool = False
    fallback_enabled: bool = True
    schema_version: int = 1
    candidates: list[ProviderRoutingCandidate] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class ProviderSelectionCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)
    provider_key: str
    configured_position: int
    eligible: bool
    eligibility_reason: ProviderEligibilityReason
    integration_health: str
    configuration_health: str
    health_stale: bool

class ProviderSelectionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    domain: ProviderDomain
    mode: ProviderSelectionMode
    policy_id: Optional[str] = None
    routing_enabled: bool = False
    fallback_enabled: bool = False
    selected_provider_key: Optional[str] = None
    candidates: list[ProviderSelectionCandidate] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProviderFallbackDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    allowed: bool
    reason: str
    failed_provider_key: str
    next_provider_key: Optional[str] = None
    remaining_candidates: int
