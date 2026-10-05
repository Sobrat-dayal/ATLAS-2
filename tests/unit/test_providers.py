import pytest
from atlas.providers.types import ProviderDomain
from atlas.providers.descriptor import ProviderDescriptor
from atlas.providers.errors import (
    ProviderNotRegisteredError,
    ProviderDomainUnsupportedError,
    ProviderFactoryInvalidError,
    ProviderAdapterInvalidError
)
from atlas.providers.base import BaseProvider
from atlas.providers.registration import ProviderRegistration
from atlas.providers.registry import ProviderRegistry
from atlas.providers.resolver import ProviderResolver


class FakeProvider(BaseProvider):
    def __init__(self, descriptor: ProviderDescriptor):
        self._descriptor = descriptor

    @property
    def descriptor(self) -> ProviderDescriptor:
        return self._descriptor

    async def close(self) -> None:
        pass


def test_provider_key_validation():
    # Valid keys
    ProviderDescriptor(
        key="openbb",
        display_name="OpenBB",
        description="Test",
        adapter_version=1,
        domains=frozenset({ProviderDomain.MARKET_DATA})
    )
    
    # Invalid keys
    with pytest.raises(ValueError):
        ProviderDescriptor(
            key="OpenBB",
            display_name="OpenBB",
            description="Test",
            adapter_version=1,
            domains=frozenset({ProviderDomain.MARKET_DATA})
        )

    with pytest.raises(ValueError):
        ProviderDescriptor(
            key="",
            display_name="OpenBB",
            description="Test",
            adapter_version=1,
            domains=frozenset({ProviderDomain.MARKET_DATA})
        )


def test_descriptor_validation():
    # Invalid adapter_version
    with pytest.raises(ValueError):
        ProviderDescriptor(
            key="openbb",
            display_name="OpenBB",
            description="Test",
            adapter_version=0,
            domains=frozenset({ProviderDomain.MARKET_DATA})
        )
    
    # Empty domains
    with pytest.raises(ValueError):
        ProviderDescriptor(
            key="openbb",
            display_name="OpenBB",
            description="Test",
            adapter_version=1,
            domains=frozenset()
        )


def test_multi_domain_descriptor():
    desc = ProviderDescriptor(
        key="multi_test",
        display_name="Multi",
        description="Multi Domain",
        adapter_version=1,
        domains=frozenset({ProviderDomain.MARKET_DATA, ProviderDomain.FUNDAMENTALS})
    )
    assert ProviderDomain.MARKET_DATA in desc.domains
    assert ProviderDomain.FUNDAMENTALS in desc.domains


def test_registry_registration_and_duplicate():
    registry = ProviderRegistry()
    desc = ProviderDescriptor(
        key="test_prov",
        display_name="Test",
        description="Desc",
        adapter_version=1,
        domains=frozenset({ProviderDomain.MARKET_DATA})
    )
    reg = ProviderRegistration(descriptor=desc, factory=lambda: FakeProvider(desc))
    
    registry.register(reg)
    assert registry.get("test_prov") == reg
    
    with pytest.raises(ValueError):
        registry.register(reg)


def test_registry_freeze():
    registry = ProviderRegistry()
    registry.freeze()
    
    desc = ProviderDescriptor(
        key="test_prov",
        display_name="Test",
        description="Desc",
        adapter_version=1,
        domains=frozenset({ProviderDomain.MARKET_DATA})
    )
    reg = ProviderRegistration(descriptor=desc, factory=lambda: FakeProvider(desc))
    
    with pytest.raises(RuntimeError):
        registry.register(reg)


def test_registry_deterministic_order():
    registry = ProviderRegistry()
    desc_b = ProviderDescriptor(key="provider_b", display_name="B", description="B", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    desc_a = ProviderDescriptor(key="provider_a", display_name="A", description="A", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    
    registry.register(ProviderRegistration(descriptor=desc_b, factory=lambda: FakeProvider(desc_b)))
    registry.register(ProviderRegistration(descriptor=desc_a, factory=lambda: FakeProvider(desc_a)))
    
    listed = registry.list_providers()
    assert len(listed) == 2
    assert listed[0].key == "provider_a"
    assert listed[1].key == "provider_b"


def test_registry_domain_filter():
    registry = ProviderRegistry()
    desc_m = ProviderDescriptor(key="m_prov", display_name="M", description="M", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    desc_f = ProviderDescriptor(key="f_prov", display_name="F", description="F", adapter_version=1, domains=frozenset({ProviderDomain.FUNDAMENTALS}))
    
    registry.register(ProviderRegistration(descriptor=desc_m, factory=lambda: FakeProvider(desc_m)))
    registry.register(ProviderRegistration(descriptor=desc_f, factory=lambda: FakeProvider(desc_f)))
    
    listed = registry.list_providers(domain=ProviderDomain.MARKET_DATA)
    assert len(listed) == 1
    assert listed[0].key == "m_prov"


def test_empty_registry():
    registry = ProviderRegistry()
    registry.freeze()
    assert len(registry.list_providers()) == 0


def test_lazy_construction():
    registry = ProviderRegistry()
    desc = ProviderDescriptor(key="test", display_name="Test", description="T", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    
    call_count = 0
    def factory():
        nonlocal call_count
        call_count += 1
        return FakeProvider(desc)
        
    registry.register(ProviderRegistration(descriptor=desc, factory=factory))
    registry.list_providers()
    assert call_count == 0


@pytest.mark.asyncio
async def test_explicit_resolution():
    registry = ProviderRegistry()
    desc = ProviderDescriptor(key="test", display_name="Test", description="T", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    
    call_count = 0
    def factory():
        nonlocal call_count
        call_count += 1
        return FakeProvider(desc)
        
    registry.register(ProviderRegistration(descriptor=desc, factory=factory))
    
    resolver = ProviderResolver(registry)
    adapter = await resolver.resolve("test")
    
    assert call_count == 1
    assert adapter.descriptor.key == "test"


@pytest.mark.asyncio
async def test_unknown_provider():
    registry = ProviderRegistry()
    resolver = ProviderResolver(registry)
    with pytest.raises(ProviderNotRegisteredError):
        await resolver.resolve("unknown")


@pytest.mark.asyncio
async def test_unsupported_domain():
    registry = ProviderRegistry()
    desc = ProviderDescriptor(key="test", display_name="Test", description="T", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    registry.register(ProviderRegistration(descriptor=desc, factory=lambda: FakeProvider(desc)))
    
    resolver = ProviderResolver(registry)
    with pytest.raises(ProviderDomainUnsupportedError):
        await resolver.resolve("test", required_domain=ProviderDomain.FUNDAMENTALS)


@pytest.mark.asyncio
async def test_no_fallback():
    registry = ProviderRegistry()
    desc_a = ProviderDescriptor(key="a", display_name="A", description="A", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    desc_b = ProviderDescriptor(key="b", display_name="B", description="B", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    
    call_count_b = 0
    def factory_b():
        nonlocal call_count_b
        call_count_b += 1
        return FakeProvider(desc_b)
        
    registry.register(ProviderRegistration(descriptor=desc_a, factory=lambda: FakeProvider(desc_a)))
    registry.register(ProviderRegistration(descriptor=desc_b, factory=factory_b))
    
    resolver = ProviderResolver(registry)
    with pytest.raises(ProviderDomainUnsupportedError):
        await resolver.resolve("a", required_domain=ProviderDomain.FUNDAMENTALS)
        
    # Verify B was not attempted
    assert call_count_b == 0


@pytest.mark.asyncio
async def test_factory_descriptor_mismatch():
    registry = ProviderRegistry()
    desc_reg = ProviderDescriptor(key="reg", display_name="R", description="R", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    desc_fac = ProviderDescriptor(key="fac", display_name="F", description="F", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    
    registry.register(ProviderRegistration(descriptor=desc_reg, factory=lambda: FakeProvider(desc_fac)))
    
    resolver = ProviderResolver(registry)
    with pytest.raises(ProviderAdapterInvalidError):
        await resolver.resolve("reg")


@pytest.mark.asyncio
async def test_factory_failure():
    registry = ProviderRegistry()
    desc = ProviderDescriptor(key="test", display_name="Test", description="T", adapter_version=1, domains=frozenset({ProviderDomain.MARKET_DATA}))
    
    def failing_factory():
        raise Exception("Secret leaked!")
        
    registry.register(ProviderRegistration(descriptor=desc, factory=failing_factory))
    
    resolver = ProviderResolver(registry)
    with pytest.raises(ProviderFactoryInvalidError) as exc:
        await resolver.resolve("test")
    
    # ensure it wraps it safely, actually wait, the sanitize might hide it or wrap it
    assert "Failed to construct provider" in str(exc.value)
