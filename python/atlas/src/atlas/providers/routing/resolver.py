from atlas.providers.base import BaseProvider
from atlas.providers.resolver import ProviderResolver
from atlas.providers.routing.models import ProviderSelectionPlan


class RoutedProviderResolver:
    def __init__(self, resolver: ProviderResolver):
        self.resolver = resolver

    async def resolve_plan(
        self, plan: ProviderSelectionPlan
    ) -> BaseProvider:
        if not plan.selected_provider_key:
            raise Exception("PROVIDER_ROUTING_NO_ELIGIBLE_PROVIDER")

        return await self.resolver.resolve(
            plan.selected_provider_key, plan.domain
        )
