from atlas.providers.openbb.adapter import OpenBBProviderAdapter
from atlas.providers.openbb.runtime import OpenBBRuntime
from atlas.providers.registration import ProviderRegistration
from atlas.providers.registry import ProviderRegistry


def register_openbb_provider(registry: ProviderRegistry) -> None:
    """
    Registers the OpenBB framework provider into the ATLAS Provider Registry.
    Uses lazy construction to avoid OpenBB import during listing.
    """
    # Create a dummy descriptor to pass to ProviderRegistration, or just
    # we can construct it, but wait... ProviderRegistration needs the descriptor!
    # So let's instantiate the descriptor without loading OpenBB.
    # Actually, we can just instantiate OpenBBProviderAdapter without calling initialize(),
    # because OpenBBProviderAdapter only initializes OpenBBRuntime, which does not load OpenBB until initialize() is called.
    # But wait, ProviderRegistration requires `descriptor` as a property.

    from atlas.providers.openbb.adapter import OPENBB_DESCRIPTOR

    def factory() -> OpenBBProviderAdapter:
        runtime = OpenBBRuntime()
        return OpenBBProviderAdapter(runtime)

    reg = ProviderRegistration(descriptor=OPENBB_DESCRIPTOR, factory=factory)
    registry.register(reg)
