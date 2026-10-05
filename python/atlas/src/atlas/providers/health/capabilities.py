from typing import Optional, List, Callable
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.capabilities.registry import CapabilityRegistry
from atlas.capabilities.definition import CapabilityDefinition
from atlas.capabilities.types import CapabilityPermissionClass, CapabilityExposure
from atlas.capabilities.context import CapabilityExecutionContext
from atlas.providers.health.models import (
    ProviderHealthCheckResult,
    ProviderHealthCheckTrigger,
    ProviderHealthTargetType,
)
from atlas.providers.health.service import ProviderHealthService
from atlas.providers.health.repository import ProviderHealthRepository
from atlas.providers.health.registry import ProviderHealthRegistry
from atlas.providers.registry import ProviderRegistry
from atlas.providers.configuration.service import ProviderConfigurationService
from atlas.providers.configuration.secrets import SupabaseVaultSecretStore

class ProviderHealthCheckInput(BaseModel):
    provider_key: str
    target_type: ProviderHealthTargetType

class ProviderHealthHistoryInput(BaseModel):
    provider_key: str
    target_type: ProviderHealthTargetType
    configuration_id: Optional[UUID] = None
    limit: int = 25

class ProviderHealthHistoryOutput(BaseModel):
    results: list[ProviderHealthCheckResult]

def register_provider_health_capabilities(
    cap_registry: CapabilityRegistry,
    provider_registry: ProviderRegistry,
    health_registry: ProviderHealthRegistry,
) -> None:

    def execute_check_factory(session: AsyncSession) -> Callable:
        # Construct dependencies
        # SecretStore requires a proper client, but we might just construct a stub if it's not used, 
        # or we should get it from a DI container if one exists.
        # Wait, how does ProviderConfigurationService get SecretStore?
        # In a real app we'd resolve it. Let's assume we can instantiate a basic one or pass None for now
        # since health checks usually don't need to WRITE secrets.
        secret_store = SupabaseVaultSecretStore(session) # In a real implementation this gets an authenticated client
        config_service = ProviderConfigurationService(session, secret_store)
        repo = ProviderHealthRepository(session)
        service = ProviderHealthService(health_registry, provider_registry, repo, config_service)

        async def execute_check_handler(inputs: ProviderHealthCheckInput, context: CapabilityExecutionContext) -> ProviderHealthCheckResult:
            return await service.execute_check(
                provider_key=inputs.provider_key,
                target_type=inputs.target_type,
                trigger=ProviderHealthCheckTrigger.MANUAL,
                user_id=context.principal_id,
                request_id=context.request_id,
                correlation_id=context.correlation_id,
            )
        return execute_check_handler

    def get_history_factory(session: AsyncSession) -> Callable:
        repo = ProviderHealthRepository(session)
        async def get_history_handler(inputs: ProviderHealthHistoryInput, context: CapabilityExecutionContext) -> ProviderHealthHistoryOutput:
            history = await repo.list_history(
                provider_key=inputs.provider_key,
                target_type=inputs.target_type,
                configuration_id=inputs.configuration_id,
                limit=inputs.limit,
            )
            
            results = []
            for h in history:
                results.append(
                    ProviderHealthCheckResult(
                        provider_key=h.provider_key,
                        target_type=ProviderHealthTargetType(h.target_type),
                        status=h.status,
                        probe_version=h.probe_version,
                        started_at=h.started_at,
                        completed_at=h.completed_at,
                        components=h.components, # type: ignore
                        coverage=h.coverage, # type: ignore
                        latency_ms=h.latency_ms,
                    )
                )
            return ProviderHealthHistoryOutput(results=results)
        return get_history_handler

    cap_registry.register(
        CapabilityDefinition(
            key="provider.health.check",
            version=1,
            title="Check Provider Health",
            description="Manually checks the health of a provider",
            category="Providers",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=ProviderHealthCheckInput,
            output_model=ProviderHealthCheckResult
        ),
        execute_check_factory
    )

    cap_registry.register(
        CapabilityDefinition(
            key="provider.health.history",
            version=1,
            title="Get Provider Health History",
            description="Gets the health history of a provider",
            category="Providers",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=ProviderHealthHistoryInput,
            output_model=ProviderHealthHistoryOutput
        ),
        get_history_factory
    )
