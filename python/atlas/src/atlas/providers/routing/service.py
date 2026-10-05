import uuid
from datetime import datetime
from typing import Optional

from atlas.providers.types import ProviderDomain
from atlas.providers.registry import ProviderRegistry
from atlas.providers.errors import ProviderError
from atlas.providers.routing.models import (
    ProviderRoutingScope, ProviderRoutingPolicy, ProviderRoutingCandidate
)
from atlas.providers.routing.repository import ProviderRoutingRepository

class ProviderRoutingError(ProviderError):
    pass

class ProviderRoutingValidationError(ProviderRoutingError):
    pass

class ProviderRoutingService:
    MAX_CANDIDATES = 16

    def __init__(self, repository: ProviderRoutingRepository, provider_registry: ProviderRegistry):
        self.repository = repository
        self.provider_registry = provider_registry

    async def get_user_policy(self, owner_principal_id: str, domain: ProviderDomain) -> Optional[ProviderRoutingPolicy]:
        return await self.repository.get_user_policy(owner_principal_id, domain)

    async def list_user_policies(self, owner_principal_id: str) -> list[ProviderRoutingPolicy]:
        return await self.repository.list_user_policies(owner_principal_id)

    async def update_user_policy(
        self,
        owner_principal_id: str,
        domain: ProviderDomain,
        enabled: bool,
        fallback_enabled: bool,
        provider_keys: list[str]
    ) -> ProviderRoutingPolicy:
        # Validate
        if enabled and not provider_keys:
            raise ProviderRoutingValidationError("An enabled routing policy must have at least one candidate provider.")
        
        if len(provider_keys) > self.MAX_CANDIDATES:
            raise ProviderRoutingValidationError(f"Maximum of {self.MAX_CANDIDATES} candidates allowed.")
            
        unique_keys = set()
        candidates = []
        for i, key in enumerate(provider_keys):
            if key in unique_keys:
                raise ProviderRoutingValidationError(f"Duplicate provider key: {key}")
            unique_keys.add(key)
            
            # Check registry and domain
            provider_desc = self.provider_registry.get_provider(key)
            if not provider_desc:
                raise ProviderRoutingValidationError(f"Provider not registered: {key}")
            
            if domain not in provider_desc.domains:
                raise ProviderRoutingValidationError(f"Provider {key} does not support domain {domain.value}")
                
            candidates.append(ProviderRoutingCandidate(provider_key=key, position=i))

        # Get existing or create new
        existing = await self.repository.get_user_policy(owner_principal_id, domain)
        policy_id = existing.policy_id if existing else str(uuid.uuid4())
        
        policy = ProviderRoutingPolicy(
            policy_id=policy_id,
            scope=ProviderRoutingScope.USER,
            owner_principal_id=owner_principal_id,
            domain=domain,
            enabled=enabled,
            fallback_enabled=fallback_enabled,
            candidates=candidates,
            created_at=existing.created_at if existing else datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return await self.repository.save_policy(policy)

    async def reset_user_policy(self, owner_principal_id: str, domain: ProviderDomain) -> None:
        await self.repository.delete_user_policy(owner_principal_id, domain)
