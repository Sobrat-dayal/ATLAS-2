from typing import Dict, List, Any
import importlib.metadata
from atlas.providers.openbb.types import OpenBBCoverageSnapshot
from atlas.providers.openbb.errors import OpenBBCoverageUnavailableError

class OpenBBCoverageInspector:
    """Inspects OpenBB runtime capabilities and installed provider extensions."""

    def __init__(self, obb: Any):
        """
        Initialize with the OpenBB runtime client.
        :param obb: The imported OpenBB client instance.
        """
        self._obb = obb

    def inspect(self) -> OpenBBCoverageSnapshot:
        """
        Inspect local OpenBB runtime capabilities without making network requests.
        """
        try:
            runtime_version = importlib.metadata.version("openbb-core")
        except importlib.metadata.PackageNotFoundError:
            runtime_version = "unknown"

        try:
            # obb.coverage.providers returns a dict of provider names to their models/coverage
            providers_dict = getattr(self._obb.coverage, "providers", {})
            provider_names = list(providers_dict.keys())
            
            # obb.coverage.commands returns a dict of commands (e.g., '/equity/price/historical') to providers
            commands_dict = getattr(self._obb.coverage, "commands", {})
            
            commands_by_provider: Dict[str, int] = {}
            for provider in provider_names:
                commands_by_provider[provider] = 0
            
            for cmd_path, info in commands_dict.items():
                # info is typically a dict or an object containing the providers that support this command
                # We'll just safely try to count them
                cmd_providers = []
                if isinstance(info, dict):
                    cmd_providers = list(info.keys())
                elif hasattr(info, "providers"):
                    # OpenBB model might have a providers attribute or it might just be the list
                    pass # We do a simplistic count if we can, else just leave it empty
                
                for p in cmd_providers:
                    if p in commands_by_provider:
                        commands_by_provider[p] += 1
                        
        except Exception as e:
            raise OpenBBCoverageUnavailableError(f"Failed to inspect OpenBB coverage: {e}") from e

        return OpenBBCoverageSnapshot(
            runtime_version=runtime_version,
            provider_names=provider_names,
            commands_by_provider=commands_by_provider
        )
