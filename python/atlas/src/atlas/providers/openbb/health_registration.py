from atlas.providers.health.models import (
    ProviderHealthCoverage,
    ProviderHealthDefinition,
    ProviderHealthTargetType,
)
from atlas.providers.health.registry import ProviderHealthRegistry
from atlas.providers.openbb.health import OpenBBHealthProbe


def register_openbb_health(registry: ProviderHealthRegistry) -> None:
    definition = ProviderHealthDefinition(
        provider_key="openbb",
        probe_version=1,
        supported_targets=[ProviderHealthTargetType.INTEGRATION],
        supported_scopes=[ProviderHealthCoverage.RUNTIME],
        timeout_seconds=5,
        schedulable=True,
        recommended_interval_seconds=300,
    )

    def probe_factory() -> OpenBBHealthProbe:
        return OpenBBHealthProbe()

    registry.register(definition, probe_factory)
