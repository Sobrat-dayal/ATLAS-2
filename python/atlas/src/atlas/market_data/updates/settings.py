from pydantic_settings import BaseSettings, SettingsConfigDict

class MarketDataUpdateSettings(BaseSettings):
    worker_id: str = "default_worker"
    poll_interval_seconds: int = 10
    lease_duration_seconds: int = 180
    heartbeat_interval_seconds: int = 60
    max_concurrent_jobs: int = 5
    max_attempts: int = 3
    retry_backoff_base_seconds: int = 60

    model_config = SettingsConfigDict(env_prefix="ATLAS_UPDATES_")
