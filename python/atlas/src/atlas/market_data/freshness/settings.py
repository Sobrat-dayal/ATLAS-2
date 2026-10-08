from pydantic_settings import BaseSettings, SettingsConfigDict

from atlas.market_data.freshness.enums import (
    MarketDataFreshnessAgeBasis,
    MarketDataSourceTimestampFallback,
)


class MarketDataFreshnessSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ATLAS_FRESHNESS_", env_file=".env", extra="ignore")

    enabled: bool = True

    default_fresh_until_seconds: int = 15
    default_stale_after_seconds: int = 60
    default_age_basis: MarketDataFreshnessAgeBasis = MarketDataFreshnessAgeBasis.SOURCE_TIME_PREFERRED
    default_source_timestamp_fallback: MarketDataSourceTimestampFallback = MarketDataSourceTimestampFallback.USE_RECEIVED_AT

    evaluation_grace_milliseconds: int = 100
    state_ttl_seconds: int = 3600  # 1 hour by default, must be > stale_after
    max_scheduled_series_per_worker: int = 10000

    transition_event_enabled: bool = True
