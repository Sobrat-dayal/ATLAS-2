from pydantic_settings import BaseSettings, SettingsConfigDict


class LiveEventPipelineSettings(BaseSettings):
    """
    Settings for the Live Event Pipeline backend transport.
    """
    model_config = SettingsConfigDict(env_prefix="ATLAS_LIVE_EVENT_", env_file=".env", extra="ignore")

    enabled: bool = False
    
    # Prefix for redis keys
    stream_key_prefix: str = "atlas:events:live:market"

    # Stream retention (event-count limit, approximate trim)
    stream_max_length: int = 100000

    # Max acceptable size of a single event envelope in bytes
    event_max_bytes: int = 131072  # 128 KiB

    # Read limits
    default_read_count: int = 256
    max_read_count: int = 2048

    default_block_milliseconds: int = 1000
    max_block_milliseconds: int = 30000
