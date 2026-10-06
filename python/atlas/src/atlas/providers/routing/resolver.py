from atlas.providers.models import BaseProvider
from atlas.providers.resolver import ConfiguredProviderResolver
from atlas.providers.routing.models import ProviderSelectionPlan


class RoutedProviderResolver:
    def __init__(self, configured_resolver: ConfiguredProviderResolver):
        self.configured_resolver = configured_resolver

    async def resolve_plan(
        self, plan: ProviderSelectionPlan, owner_principal_id: str
    ) -> BaseProvider:
        if not plan.selected_provider_key:
            raise Exception("PROVIDER_ROUTING_NO_ELIGIBLE_PROVIDER")

        return await self.configured_resolver.resolve(
            plan.selected_provider_key, owner_principal_id
        )
