import pytest
from unittest.mock import MagicMock, patch

from atlas.providers.registry import ProviderRegistry
from atlas.providers.resolver import ProviderResolver
from atlas.providers.types import ProviderDomain
from atlas.providers.bootstrap import build_provider_registry
from atlas.providers.openbb.runtime import OpenBBRuntime
from atlas.providers.openbb.errors import (
    OpenBBRuntimeUnavailableError,
    OpenBBVersionUnsupportedError,
)

def test_registry_includes_openbb():
    registry = build_provider_registry()
    listed = registry.list_providers()
    assert any(p.key == "openbb" for p in listed)

def test_openbb_descriptor():
    registry = build_provider_registry()
    desc = registry.get("openbb").descriptor
    assert desc.display_name == "OpenBB"
    assert desc.adapter_version == 1
    assert ProviderDomain.MARKET_DATA in desc.domains
    assert ProviderDomain.FUNDAMENTALS in desc.domains

@pytest.mark.asyncio
async def test_lazy_construction_and_resolution():
    registry = build_provider_registry()
    resolver = ProviderResolver(registry)
    
    adapter = await resolver.resolve("openbb")
    assert adapter.descriptor.key == "openbb"
    
    # Check that runtime is available but not initialized yet (lazy)
    assert hasattr(adapter, "runtime")

def test_runtime_version_unsupported():
    runtime = OpenBBRuntime()
    with patch("importlib.metadata.version", return_value="1.0.0"):
        with pytest.raises(OpenBBVersionUnsupportedError):
            runtime.initialize()

def test_runtime_package_not_found():
    runtime = OpenBBRuntime()
    import importlib.metadata
    with patch("importlib.metadata.version", side_effect=importlib.metadata.PackageNotFoundError):
        with pytest.raises(OpenBBRuntimeUnavailableError):
            runtime.initialize()

def test_runtime_import_failure():
    runtime = OpenBBRuntime()
    with patch("importlib.metadata.version", return_value="2.0.0"):
        with patch.dict("sys.modules", {"openbb": None}):
            with pytest.raises(OpenBBRuntimeUnavailableError):
                runtime.initialize()

def test_openbb_coverage_snapshot_mocked():
    runtime = OpenBBRuntime()
    with patch("importlib.metadata.version", return_value="2.0.0"):
        # Mock the obb import and its internals
        mock_obb = MagicMock()
        mock_obb.coverage.providers = {"test_provider": {}}
        mock_obb.coverage.commands = {"/test/cmd": {"test_provider": {}}}
        
        with patch.dict("sys.modules", {"openbb": MagicMock(obb=mock_obb)}):
            runtime.initialize()
            coverage = runtime.get_coverage()
            assert coverage.runtime_version == "2.0.0"
            assert "test_provider" in coverage.provider_names
            assert coverage.commands_by_provider.get("test_provider") == 1
