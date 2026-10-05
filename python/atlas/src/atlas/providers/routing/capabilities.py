from pydantic import BaseModel
from atlas.providers.types import ProviderDomain
from atlas.capabilities import (
    CapabilityRegistry, CapabilityRef, CapabilityPermissionClass, CapabilityExposure
)
from atlas.providers.registry import ProviderRegistry
from atlas.providers.health.registry import ProviderHealthRegistry
from atlas.providers.routing.models import ProviderRoutingPolicy, ProviderSelectionPlan

class ProviderRoutingListOutput(BaseModel):
    policies: list[ProviderRoutingPolicy]

class ProviderRoutingGetInput(BaseModel):
    domain: ProviderDomain

class ProviderRoutingGetOutput(BaseModel):
    policy: ProviderRoutingPolicy

class ProviderRoutingUpdateInput(BaseModel):
    domain: ProviderDomain
    enabled: bool
    fallback_enabled: bool
    provider_keys: list[str]

class ProviderRoutingUpdateOutput(BaseModel):
    policy: ProviderRoutingPolicy

class ProviderRoutingResetInput(BaseModel):
    domain: ProviderDomain

class ProviderRoutingPlanInput(BaseModel):
    domain: ProviderDomain

class ProviderRoutingPlanOutput(BaseModel):
    plan: ProviderSelectionPlan

def register_provider_routing_capabilities(
    registry: CapabilityRegistry,
    provider_registry: ProviderRegistry,
    health_registry: ProviderHealthRegistry
):
    
    def _get_routing_service(context):
        from atlas.providers.routing.repository import ProviderRoutingRepository
        from atlas.providers.routing.service import ProviderRoutingService
        repo = ProviderRoutingRepository(context.session)
        return ProviderRoutingService(repo, provider_registry)
        
    def _get_selection_service(context):
        routing_service = _get_routing_service(context)
        from atlas.providers.configuration.secrets import SupabaseVaultSecretStore
        from atlas.providers.configuration.service import ProviderConfigurationService
        config_service = ProviderConfigurationService(context.session, SupabaseVaultSecretStore(context.session))
        
        from atlas.providers.health.repository import ProviderHealthRepository
        from atlas.providers.health.service import ProviderHealthService
        health_repo = ProviderHealthRepository(context.session)
        health_service = ProviderHealthService(health_registry, provider_registry, health_repo, config_service)
        
        from atlas.providers.routing.selection import ProviderSelectionService
        return ProviderSelectionService(routing_service, provider_registry, config_service, health_service)

    @registry.register(
        CapabilityRef(
            key="provider.routing.list",
            version="1.0.0",
            name="List Provider Routing Policies",
            permission_class=CapabilityPermissionClass.READ,
            exposure=CapabilityExposure.PUBLIC,
            required_permissions=["atlas.access"]
        )
    )
    async def list_policies(inputs, context):
        principal_id = context.principal.principal_id
        routing_service = _get_routing_service(context)
        policies = await routing_service.list_user_policies(principal_id)
        return ProviderRoutingListOutput(policies=policies)

    @registry.register(
        CapabilityRef(
            key="provider.routing.get",
            version="1.0.0",
            name="Get Provider Routing Policy",
            permission_class=CapabilityPermissionClass.READ,
            exposure=CapabilityExposure.PUBLIC,
            required_permissions=["atlas.access"]
        )
    )
    async def get_policy(inputs: ProviderRoutingGetInput, context):
        principal_id = context.principal.principal_id
        routing_service = _get_routing_service(context)
        policy = await routing_service.get_user_policy(principal_id, inputs.domain)
        if not policy:
            # Derived default disabled state
            policy = ProviderRoutingPolicy(
                policy_id="default",
                scope="user",
                owner_principal_id=principal_id,
                domain=inputs.domain,
                enabled=False,
                fallback_enabled=False,
                candidates=[],
                created_at=None,
                updated_at=None
            )
        return ProviderRoutingGetOutput(policy=policy)

    @registry.register(
        CapabilityRef(
            key="provider.routing.update",
            version="1.0.0",
            name="Update Provider Routing Policy",
            permission_class=CapabilityPermissionClass.WRITE,
            exposure=CapabilityExposure.PUBLIC,
            required_permissions=["atlas.access"]
        )
    )
    async def update_policy(inputs: ProviderRoutingUpdateInput, context):
        principal_id = context.principal.principal_id
        routing_service = _get_routing_service(context)
        policy = await routing_service.update_user_policy(
            principal_id,
            inputs.domain,
            inputs.enabled,
            inputs.fallback_enabled,
            inputs.provider_keys
        )
        return ProviderRoutingUpdateOutput(policy=policy)

    @registry.register(
        CapabilityRef(
            key="provider.routing.reset",
            version="1.0.0",
            name="Reset Provider Routing Policy",
            permission_class=CapabilityPermissionClass.WRITE,
            exposure=CapabilityExposure.PUBLIC,
            required_permissions=["atlas.access"]
        )
    )
    async def reset_policy(inputs: ProviderRoutingResetInput, context):
        principal_id = context.principal.principal_id
        routing_service = _get_routing_service(context)
        await routing_service.reset_user_policy(principal_id, inputs.domain)
        return {}

    @registry.register(
        CapabilityRef(
            key="provider.routing.plan",
            version="1.0.0",
            name="Preview Provider Routing Plan",
            permission_class=CapabilityPermissionClass.READ,
            exposure=CapabilityExposure.PUBLIC,
            required_permissions=["atlas.access"]
        )
    )
    async def get_plan(inputs: ProviderRoutingPlanInput, context):
        principal_id = context.principal.principal_id
        selection_service = _get_selection_service(context)
        try:
            plan = await selection_service.plan_policy(principal_id, inputs.domain)
        except Exception as e:
            # If no policy exists
            plan = ProviderSelectionPlan(
                domain=inputs.domain,
                mode="policy",
                routing_enabled=False,
                fallback_enabled=False,
                selected_provider_key=None,
                candidates=[]
            )
        return ProviderRoutingPlanOutput(plan=plan)
