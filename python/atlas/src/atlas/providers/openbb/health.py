import datetime
import importlib

from atlas.providers.health.models import (
    ProviderHealthCheckResult,
    ProviderHealthComponentResult,
    ProviderHealthCoverage,
    ProviderHealthStatus,
)
from atlas.providers.health.probe import ProviderHealthProbeContext


class OpenBBHealthProbe:
    async def check(self, context: ProviderHealthProbeContext) -> ProviderHealthCheckResult:
        components = []
        started_at = datetime.datetime.now(datetime.timezone.utc)

        # Check runtime import
        try:
            openbb = importlib.import_module("openbb")
            components.append(
                ProviderHealthComponentResult(
                    key="runtime_import",
                    label="Runtime Import",
                    status=ProviderHealthStatus.HEALTHY,
                    scope=ProviderHealthCoverage.RUNTIME,
                    message="OpenBB module imported successfully.",
                )
            )
        except ImportError:
            components.append(
                ProviderHealthComponentResult(
                    key="runtime_import",
                    label="Runtime Import",
                    status=ProviderHealthStatus.UNHEALTHY,
                    scope=ProviderHealthCoverage.RUNTIME,
                    message="Failed to import openbb module.",
                )
            )
            return self._aggregate(context, components, started_at)

        # Check runtime version
        try:
            version = getattr(openbb, "__version__", "unknown")
            # Assume any version is okay for now, or check specific range
            components.append(
                ProviderHealthComponentResult(
                    key="runtime_version",
                    label="Runtime Version",
                    status=ProviderHealthStatus.HEALTHY,
                    scope=ProviderHealthCoverage.RUNTIME,
                    message=f"OpenBB version {version} detected.",
                )
            )
        except Exception:
            components.append(
                ProviderHealthComponentResult(
                    key="runtime_version",
                    label="Runtime Version",
                    status=ProviderHealthStatus.DEGRADED,
                    scope=ProviderHealthCoverage.RUNTIME,
                    message="Could not determine OpenBB version.",
                )
            )

        # Check interface/coverage
        try:
            from openbb import obb

            providers = getattr(obb.coverage, "providers", {})
            if isinstance(providers, dict):
                provider_count = len(providers)
            elif callable(providers):
                provider_count = len(providers())  # Some versions this is a property/method
            else:
                provider_count = 0

            # Zero extensions is allowed, but we report it
            components.append(
                ProviderHealthComponentResult(
                    key="coverage_metadata",
                    label="Coverage Metadata",
                    status=ProviderHealthStatus.HEALTHY,
                    scope=ProviderHealthCoverage.RUNTIME,
                    message=f"Runtime operational. {provider_count} upstream extensions found."
                    if provider_count > 0
                    else "Runtime operational. No upstream extensions checked.",
                )
            )
        except Exception:
            components.append(
                ProviderHealthComponentResult(
                    key="coverage_metadata",
                    label="Coverage Metadata",
                    status=ProviderHealthStatus.UNHEALTHY,
                    scope=ProviderHealthCoverage.RUNTIME,
                    message="Failed to inspect OpenBB coverage metadata.",
                )
            )

        return self._aggregate(context, components, started_at)

    def _aggregate(
        self,
        context: ProviderHealthProbeContext,
        components: list[ProviderHealthComponentResult],
        started_at: datetime.datetime,
    ) -> ProviderHealthCheckResult:
        if not components:
            status = ProviderHealthStatus.UNKNOWN
        elif any(c.status == ProviderHealthStatus.UNHEALTHY for c in components):
            status = ProviderHealthStatus.UNHEALTHY
        elif any(c.status == ProviderHealthStatus.DEGRADED for c in components):
            status = ProviderHealthStatus.DEGRADED
        else:
            status = ProviderHealthStatus.HEALTHY

        return ProviderHealthCheckResult(
            provider_key=context.provider_key,
            target_type=context.target_type,
            status=status,
            probe_version=1,
            started_at=started_at,
            completed_at=datetime.datetime.now(datetime.timezone.utc),
            components=components,
            coverage=[ProviderHealthCoverage.RUNTIME],
        )
