from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

from atlas.providers.health.models import (
    ProviderHealthCheckResult,
    ProviderHealthTargetType,
)

class ProviderHealthProbeContext:
    def __init__(
        self,
        provider_key: str,
        target_type: ProviderHealthTargetType,
        provider: Any,  # The instantiated provider adapter
        credential_accessor: Optional[Any] = None,
        configuration_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        self.provider_key = provider_key
        self.target_type = target_type
        self.provider = provider
        self.credential_accessor = credential_accessor
        self.configuration_id = configuration_id
        self.request_id = request_id
        self.correlation_id = correlation_id

class ProviderHealthProbe(Protocol):
    async def check(self, context: ProviderHealthProbeContext) -> ProviderHealthCheckResult:
        """
        Execute the health check and return a fully populated check result.
        Must not raise exceptions for expected check failures.
        """
        ...
