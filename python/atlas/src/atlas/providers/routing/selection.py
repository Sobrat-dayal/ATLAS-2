import logging
from typing import Optional

from atlas.providers.types import ProviderDomain
from atlas.providers.registry import ProviderRegistry
from atlas.providers.configuration.service import ProviderConfigurationService
from atlas.providers.health.service import ProviderHealthService
from atlas.providers.health.models import ProviderHealthStatus, ProviderHealthTargetType
from atlas.providers.routing.models import (
    ProviderSelectionPlan, ProviderSelectionCandidate,
    ProviderSelectionMode, ProviderEligibilityReason,
    ProviderRoutingPolicy
)
from atlas.providers.routing.service import ProviderRoutingService
from atlas.providers.errors import ProviderError

logger = logging.getLogger(__name__)

class ProviderSelectionRequiredError(ProviderError):
    pass

class ProviderRoutingNoEligibleProviderError(ProviderError):
    pass

class ProviderSelectionService:
    def __init__(
        self,
        routing_service: ProviderRoutingService,
        provider_registry: ProviderRegistry,
        config_service: ProviderConfigurationService,
        health_service: ProviderHealthService
    ):
        self.routing_service = routing_service
        self.provider_registry = provider_registry
        self.config_service = config_service
        self.health_service = health_service

    async def plan_explicit(self, owner_principal_id: str, domain: ProviderDomain, provider_key: str) -> ProviderSelectionPlan:
        # Check provider domain support
        provider_desc = self.provider_registry.get_provider(provider_key)
        if not provider_desc or domain not in provider_desc.domains:
            return ProviderSelectionPlan(
                domain=domain,
                mode=ProviderSelectionMode.EXPLICIT,
                routing_enabled=False,
                fallback_enabled=False,
                selected_provider_key=None,
                candidates=[
                    ProviderSelectionCandidate(
                        provider_key=provider_key,
                        configured_position=0,
                        eligible=False,
                        eligibility_reason=ProviderEligibilityReason.PROVIDER_NOT_REGISTERED if not provider_desc else ProviderEligibilityReason.DOMAIN_UNSUPPORTED,
                        integration_health="unknown",
                        configuration_health="unknown",
                        health_stale=False
                    )
                ]
            )

        candidate = await self._evaluate_candidate(owner_principal_id, provider_key, 0)
        
        return ProviderSelectionPlan(
            domain=domain,
            mode=ProviderSelectionMode.EXPLICIT,
            routing_enabled=False,
            fallback_enabled=False,
            selected_provider_key=provider_key if candidate.eligible else None,
            candidates=[candidate]
        )

    async def plan_policy(self, owner_principal_id: str, domain: ProviderDomain) -> ProviderSelectionPlan:
        policy = await self.routing_service.get_user_policy(owner_principal_id, domain)
        if not policy or not policy.enabled:
            raise ProviderSelectionRequiredError(f"No enabled routing policy for domain {domain.value}")
        
        candidates = []
        selected_key = None
        
        for cand in sorted(policy.candidates, key=lambda x: x.position):
            eval_cand = await self._evaluate_candidate(owner_principal_id, cand.provider_key, cand.position)
            candidates.append(eval_cand)
            if eval_cand.eligible and selected_key is None:
                selected_key = eval_cand.provider_key

        return ProviderSelectionPlan(
            domain=domain,
            mode=ProviderSelectionMode.POLICY,
            policy_id=policy.policy_id,
            routing_enabled=policy.enabled,
            fallback_enabled=policy.fallback_enabled,
            selected_provider_key=selected_key,
            candidates=candidates
        )

    async def _evaluate_candidate(self, owner_principal_id: str, provider_key: str, position: int) -> ProviderSelectionCandidate:
        # 1. Registered and supports domain? Assumed checked via policy creation, but could change
        provider_desc = self.provider_registry.get_provider(provider_key)
        if not provider_desc:
            return ProviderSelectionCandidate(
                provider_key=provider_key,
                configured_position=position,
                eligible=False,
                eligibility_reason=ProviderEligibilityReason.PROVIDER_NOT_REGISTERED,
                integration_health="unknown",
                configuration_health="unknown",
                health_stale=False
            )

        # 2. Configured and Enabled?
        config = await self.config_service.get_provider_configuration(provider_key, owner_principal_id)
        if not config or not config.enabled:
            return ProviderSelectionCandidate(
                provider_key=provider_key,
                configured_position=position,
                eligible=False,
                eligibility_reason=ProviderEligibilityReason.PROVIDER_DISABLED,
                integration_health="unknown",
                configuration_health="unknown",
                health_stale=False
            )

        # 3. Credentials Complete?
        status = await self.config_service.get_provider_credential_status(provider_key, owner_principal_id)
        for req in status.required_credentials:
            if not req.is_set:
                return ProviderSelectionCandidate(
                    provider_key=provider_key,
                    configured_position=position,
                    eligible=False,
                    eligibility_reason=ProviderEligibilityReason.REQUIRED_CREDENTIALS_MISSING,
                    integration_health="unknown",
                    configuration_health="unknown",
                    health_stale=False
                )

        # 4. Health
        health = await self.health_service.get_current_state(provider_key, ProviderHealthTargetType.INTEGRATION)
        integration_status = health.status.value if health else "unknown"
        is_stale = health.is_stale() if health else False
        
        if health and not is_stale and health.status == ProviderHealthStatus.UNHEALTHY:
            return ProviderSelectionCandidate(
                provider_key=provider_key,
                configured_position=position,
                eligible=False,
                eligibility_reason=ProviderEligibilityReason.HEALTH_UNHEALTHY,
                integration_health=integration_status,
                configuration_health="unknown",
                health_stale=is_stale
            )
            
        return ProviderSelectionCandidate(
            provider_key=provider_key,
            configured_position=position,
            eligible=True,
            eligibility_reason=ProviderEligibilityReason.ELIGIBLE,
            integration_health=integration_status,
            configuration_health="unknown",
            health_stale=is_stale
        )
