from pydantic_settings import BaseSettings, SettingsConfigDict


class LiveQuoteWorkerSettings(BaseSettings):
    """
    Settings for the Live Quote Worker process.
    """
    model_config = SettingsConfigDict(env_prefix="ATLAS_LIVE_QUOTE_", env_file=".env", extra="ignore")

    # Identity
    worker_id: str = "default_live_quote_worker"

    # Concurrency
    max_concurrent_targets: int = 1000
    
    # Provider concurrency limits
    max_streams_per_provider: int = 10
    
    # Lease management
    lease_duration_seconds: int = 60
    heartbeat_interval_seconds: int = 15
    
    # Reconnect/Backoff
    reconnect_base_backoff_seconds: int = 2
    reconnect_max_backoff_seconds: int = 60
    
    # Grouping
    targets_per_stream_chunk: int = 100
