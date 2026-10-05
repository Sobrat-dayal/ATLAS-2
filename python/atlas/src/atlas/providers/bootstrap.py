from atlas.providers.registry import ProviderRegistry


def build_provider_registry() -> ProviderRegistry:
    """
    Builds the production provider registry.
    At Stage 28, this correctly returns an empty registry until real providers
    are implemented in subsequent stages.
    """
    registry = ProviderRegistry()
    
    # Register the OpenBB provider framework
    from atlas.providers.openbb import register_openbb_provider
    register_openbb_provider(registry)
    
    registry.freeze()
    return registry
