import asyncio
import time
import datetime
from typing import Any, Optional
from uuid import UUID

from atlas.providers.registry import ProviderRegistry
from atlas.providers.configuration.service import ProviderConfigurationService
from atlas.providers.health.registry import ProviderHealthRegistry
from atlas.providers.health.repository import ProviderHealthRepository
from atlas.providers.health.db_models import ProviderHealthState, ProviderHealthCheck
from atlas.providers.health.models import (
    ProviderHealthStatus,
    ProviderHealthTargetType,
    ProviderHealthCheckTrigger,
    ProviderHealthCheckResult,
    ProviderHealthComponentResult,
)
from atlas.providers.health.probe import ProviderHealthProbeContext
from atlas.providers.errors import ProviderNotRegisteredError

class ProviderHealthError(Exception):
    pass

class ProviderHealthCheckCooldownError(ProviderHealthError):
    pass

class ProviderHealthService:
    def __init__(
        self,
        health_registry: ProviderHealthRegistry,
        provider_registry: ProviderRegistry,
        health_repository: ProviderHealthRepository,
        config_service: ProviderConfigurationService,
    ):
        self.health_registry = health_registry
        self.provider_registry = provider_registry
        self.health_repository = health_repository
        self.config_service = config_service

    async def execute_check(
        self,
        provider_key: str,
        target_type: ProviderHealthTargetType,
        trigger: ProviderHealthCheckTrigger,
        user_id: Optional[UUID] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> ProviderHealthCheckResult:
        
        definition = self.health_registry.get_definition(provider_key)
        if target_type not in definition.supported_targets:
            raise ProviderHealthError(f"Target type {target_type} not supported by {provider_key}")

        configuration_id = None
        if target_type == ProviderHealthTargetType.CONFIGURATION:
            if not user_id:
                raise ValueError("user_id required for configuration check")
            config = await self.config_service.get_configuration(user_id, provider_key)
            if config:
                configuration_id = config.id
            else:
                # If they have no config, we might still allow a check, but we need an ID. 
                # According to the rules, a missing config means unknown.
                pass
            
            # Check cooldown
            if trigger == ProviderHealthCheckTrigger.MANUAL and configuration_id:
                state = await self.health_repository.get_configuration_state(configuration_id)
                if state and state.checked_at:
                    elapsed = (datetime.datetime.now(datetime.timezone.utc) - state.checked_at).total_seconds()
                    if elapsed < 30: # 30 seconds cooldown
                        raise ProviderHealthCheckCooldownError("Please wait before checking health again")

        factory = self.health_registry.get_probe_factory(provider_key)
        probe = factory()

        context = ProviderHealthProbeContext(
            provider_key=provider_key,
            target_type=target_type,
            provider=None, # In a real implementation this might be the instantiated provider
            credential_accessor=None, # Will use config_service in the probe if needed
            configuration_id=configuration_id,
            request_id=request_id,
            correlation_id=correlation_id,
        )

        start_time = time.monotonic()
        started_at = datetime.datetime.now(datetime.timezone.utc)
        
        try:
            # We enforce timeout here
            result = await asyncio.wait_for(probe.check(context), timeout=definition.timeout_seconds)
        except asyncio.TimeoutError:
            result = ProviderHealthCheckResult(
                provider_key=provider_key,
                target_type=target_type,
                status=ProviderHealthStatus.UNHEALTHY,
                probe_version=definition.probe_version,
                started_at=started_at,
                completed_at=datetime.datetime.now(datetime.timezone.utc),
                components=[
                    ProviderHealthComponentResult(
                        key="timeout",
                        label="Timeout",
                        status=ProviderHealthStatus.UNHEALTHY,
                        scope=definition.supported_scopes[0] if definition.supported_scopes else "runtime", # type: ignore
                        message="Health check timed out"
                    )
                ]
            )
        except Exception as e:
            # Sanitize unexpected execution failures
            result = ProviderHealthCheckResult(
                provider_key=provider_key,
                target_type=target_type,
                status=ProviderHealthStatus.UNHEALTHY,
                probe_version=definition.probe_version,
                started_at=started_at,
                completed_at=datetime.datetime.now(datetime.timezone.utc),
                components=[
                    ProviderHealthComponentResult(
                        key="execution_failure",
                        label="Execution Failure",
                        status=ProviderHealthStatus.UNHEALTHY,
                        scope=definition.supported_scopes[0] if definition.supported_scopes else "runtime", # type: ignore
                        message="The health check encountered an internal execution error."
                    )
                ]
            )

        latency_ms = int((time.monotonic() - start_time) * 1000)
        result.latency_ms = latency_ms

        # Determine aggregate status if not already set by exception handling
        if len(result.components) == 0 and result.status == ProviderHealthStatus.UNKNOWN: # Or not set
            result.status = ProviderHealthStatus.UNKNOWN
        elif not any(c.status == ProviderHealthStatus.UNHEALTHY for c in result.components):
            if any(c.status == ProviderHealthStatus.DEGRADED for c in result.components):
                result.status = ProviderHealthStatus.DEGRADED
            elif any(c.status == ProviderHealthStatus.UNKNOWN for c in result.components):
                # According to rules, healthy + unknown -> degraded or unknown. We choose unknown.
                result.status = ProviderHealthStatus.UNKNOWN
            else:
                result.status = ProviderHealthStatus.HEALTHY
        else:
            result.status = ProviderHealthStatus.UNHEALTHY
            
        result.coverage = list({c.scope for c in result.components})

        # Save history
        check = ProviderHealthCheck(
            provider_key=provider_key,
            target_type=target_type.value,
            configuration_id=configuration_id,
            owner_principal_id=user_id,
            trigger=trigger.value,
            status=result.status.value,
            coverage=[c.value for c in result.coverage],
            components=[c.model_dump() for c in result.components],
            probe_version=result.probe_version,
            started_at=result.started_at,
            completed_at=result.completed_at,
            latency_ms=result.latency_ms,
            request_id=request_id,
            correlation_id=correlation_id,
        )
        await self.health_repository.append_check(check)

        # Update state
        state = ProviderHealthState(
            provider_key=provider_key,
            target_type=target_type.value,
            configuration_id=configuration_id,
            owner_principal_id=user_id,
            status=result.status.value,
            coverage=[c.value for c in result.coverage],
            components=[c.model_dump() for c in result.components],
            checked_at=result.completed_at,
            latency_ms=result.latency_ms,
            probe_version=result.probe_version,
        )
        
        # We need to fetch existing to update counters properly.
        if target_type == ProviderHealthTargetType.INTEGRATION:
            existing = await self.health_repository.get_integration_state(provider_key)
        else:
            existing = await self.health_repository.get_configuration_state(configuration_id) # type: ignore
            
        if existing:
            state.consecutive_successes = existing.consecutive_successes
            state.consecutive_failures = existing.consecutive_failures
            state.last_success_at = existing.last_success_at
            state.last_failure_at = existing.last_failure_at
            
        if result.status == ProviderHealthStatus.HEALTHY:
            state.consecutive_successes += 1
            state.consecutive_failures = 0
            state.last_success_at = result.completed_at
        elif result.status == ProviderHealthStatus.UNHEALTHY:
            state.consecutive_failures += 1
            state.consecutive_successes = 0
            state.last_failure_at = result.completed_at
        elif result.status == ProviderHealthStatus.DEGRADED:
            state.consecutive_failures += 1
            state.consecutive_successes = 0

        await self.health_repository.upsert_state(state)
        
        return result
