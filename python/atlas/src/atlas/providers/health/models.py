from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class ProviderHealthStatus(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ProviderHealthTargetType(str, Enum):
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"

class ProviderHealthCheckTrigger(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    STARTUP = "startup"

class ProviderHealthCoverage(str, Enum):
    RUNTIME = "runtime"
    UPSTREAM = "upstream"

class ProviderHealthComponentResult(BaseModel):
    key: str = Field(..., description="Unique key for the component check (e.g. 'runtime_import')")
    label: str = Field(..., description="Human-readable label for the component")
    status: ProviderHealthStatus = Field(..., description="Health status of this component")
    scope: ProviderHealthCoverage = Field(..., description="Coverage scope of this component")
    latency_ms: Optional[int] = Field(None, description="Execution time in milliseconds")
    error_code: Optional[str] = Field(None, description="Stable ATLAS error code if failed")
    message: Optional[str] = Field(None, description="Sanitized, safe user-facing message")

class ProviderHealthCheckResult(BaseModel):
    provider_key: str = Field(..., description="The registered provider key")
    target_type: ProviderHealthTargetType = Field(..., description="Target type evaluated")
    status: ProviderHealthStatus = Field(..., description="Aggregated health status")
    coverage: List[ProviderHealthCoverage] = Field(default_factory=list, description="Coverage scopes evaluated")
    components: List[ProviderHealthComponentResult] = Field(default_factory=list, description="Individual component results")
    probe_version: int = Field(..., description="Version of the health probe executed")
    started_at: datetime = Field(..., description="When the check started")
    completed_at: datetime = Field(..., description="When the check completed")
    latency_ms: Optional[int] = Field(None, description="Total execution time in milliseconds")

class ProviderHealthDefinition(BaseModel):
    provider_key: str = Field(..., description="Must match a registered provider key")
    probe_version: int = Field(1, description="Version of the health semantics (>= 1)")
    supported_targets: List[ProviderHealthTargetType] = Field(..., description="Which targets this provider can check")
    supported_scopes: List[ProviderHealthCoverage] = Field(..., description="Which scopes this provider can check")
    timeout_seconds: int = Field(10, description="Maximum execution time for the probe")
    schedulable: bool = Field(False, description="Whether integration monitoring can be scheduled")
    recommended_interval_seconds: Optional[int] = Field(None, description="Recommended interval if schedulable")
