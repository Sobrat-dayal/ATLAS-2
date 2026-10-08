from typing import Optional

from atlas.market_data.freshness.enums import (
    MarketDataFreshnessAgeBasis,
    MarketDataSourceTimestampFallback,
)
from atlas.market_data.freshness.models import MarketDataFreshnessPolicy
from atlas.market_data.freshness.settings import MarketDataFreshnessSettings
from atlas.market_data.live.models import MarketDataLiveQuoteTarget
from atlas.providers.config import ProviderConfigService # Assumption based on Stage 30 Provider Config


class MarketDataFreshnessPolicyResolver:
    """
    Resolves effective Freshness Policy using Precedence:
    Global -> Provider -> Target
    """

    def __init__(self, global_settings: MarketDataFreshnessSettings, provider_config_service: Optional[Any] = None):
        self.global_settings = global_settings
        self.provider_config_service = provider_config_service

    async def resolve(
        self, provider_key: str, target: Optional[MarketDataLiveQuoteTarget] = None
    ) -> MarketDataFreshnessPolicy:
        
        # 1. Start with global defaults
        fresh_until = self.global_settings.default_fresh_until_seconds
        stale_after = self.global_settings.default_stale_after_seconds
        age_basis = self.global_settings.default_age_basis
        fallback = self.global_settings.default_source_timestamp_fallback

        # 2. Provider overrides
        if self.provider_config_service:
            # Fallback to provider config if Stage 30 exists
            # We use hypothetical keys like market_data.freshness.fresh_until_seconds
            p_fresh = await self.provider_config_service.get_int(provider_key, "market_data.freshness.fresh_until_seconds")
            if p_fresh is not None:
                fresh_until = p_fresh
                
            p_stale = await self.provider_config_service.get_int(provider_key, "market_data.freshness.stale_after_seconds")
            if p_stale is not None:
                stale_after = p_stale
                
            p_basis_str = await self.provider_config_service.get_string(provider_key, "market_data.freshness.age_basis")
            if p_basis_str:
                try:
                    age_basis = MarketDataFreshnessAgeBasis(p_basis_str)
                except ValueError:
                    pass
                    
            p_fallback_str = await self.provider_config_service.get_string(provider_key, "market_data.freshness.source_timestamp_fallback")
            if p_fallback_str:
                try:
                    fallback = MarketDataSourceTimestampFallback(p_fallback_str)
                except ValueError:
                    pass

        # 3. Target overrides (highest precedence)
        if target:
            if target.freshness_fresh_until_seconds is not None:
                fresh_until = target.freshness_fresh_until_seconds
            if target.freshness_stale_after_seconds is not None:
                stale_after = target.freshness_stale_after_seconds
            if target.freshness_age_basis:
                try:
                    age_basis = MarketDataFreshnessAgeBasis(target.freshness_age_basis)
                except ValueError:
                    pass
            if target.freshness_source_timestamp_fallback:
                try:
                    fallback = MarketDataSourceTimestampFallback(target.freshness_source_timestamp_fallback)
                except ValueError:
                    pass

        # Apply bounds to prevent malformed config
        if fresh_until >= stale_after:
            # Fallback to sane state if target/provider override is invalid
            stale_after = max(fresh_until + 1, self.global_settings.default_stale_after_seconds)

        return MarketDataFreshnessPolicy(
            fresh_until_seconds=fresh_until,
            stale_after_seconds=stale_after,
            age_basis=age_basis,
            source_timestamp_fallback=fallback,
        )
